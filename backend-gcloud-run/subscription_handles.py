from flask import request, jsonify, g, Blueprint
import utils
import logging

subscription_bp = Blueprint("subscription", __name__, url_prefix=f"/{utils.COLLECTION_NAME}")


@subscription_bp.route(f"/<user_id>/subscribe_url", methods=["POST"])
@utils.auth_required
def subscribe_user(user_id):
    # Get user document
    doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()
    doc_data = doc.to_dict() if doc.exists else {}

    # Get request data
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Missing email"}), 400

    # Check if already subscribed
    if doc_data.get("subscribed") and "subscriptionId" in doc_data:
        return jsonify({"error": "User is already subscribed"}), 400

    try:

        # 2. Create a Price-based Payment Link (product & price must exist)
        payment_link = utils.STRIPE.PaymentLink.create(
            line_items=[{"price": utils.STRIPE_PRICE_ID, "quantity": 1}],
            after_completion={
                "type": "redirect",
                "redirect": {
                    "url": utils.PAYMENT_SUCCESS_REDIRECT_URL  # redirect after successful payment
                }
            },
            metadata={"userId": user_id},
        )

        # 3. Save preliminary info in Firestore
        doc_ref.update({
            "customerId": None,
            "subscriptionId": None,
            "subscribed": False  # Will be set True after webhook
        })

        # 4. Return link URL
        return jsonify({"paymentLinkUrl": payment_link.url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



logger = logging.getLogger("stripe_webhook")
@subscription_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = utils.STRIPE_WEBHOOK_SECRET

    try:
        event = utils.STRIPE.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return "Webhook error", 400

    logger.info(f"✅ Received event: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        user_id = metadata.get("userId")

        logger.info(f"🔎 Metadata: {metadata}")
        logger.info(f"🧾 Retrieved user_id: {user_id}")

        if not user_id:
            customer_email = session.get("customer_email")
            logger.warning(f"⚠️ No user_id in metadata. Falling back to email: {customer_email}")
            user_query = utils.database.collection(utils.COLLECTION_NAME).where("email", "==", customer_email).get()
            if user_query:
                user_id = user_query[0].id
                logger.info(f"✅ Found user by email: {user_id}")
            else:
                logger.warning("❌ No matching user found by email.")

        if user_id:
            doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
            doc_ref.update({
                "subscribed": True,
                "subscriptionId": session.get("subscription"),
                "customerId": session.get("customer"),
            })
            logger.info(f"✅ Subscription updated in Firestore for user_id: {user_id}")
        else:
            logger.warning("⚠️ Could not resolve user_id. No updates made.")

    return "", 200
"""
    except Exception as e:
        import traceback
        traceback.print_exc()  # full stack trace
        print("utils.STRIPE error:", str(e))
        return jsonify({"error": str(e)}), 400
"""
"""
def subscribe(user_id):
    user = g.user

    # Optional: Check user_id in URL matches g.user["userId"] for security
    if user["userId"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user_data = request.get_json()

    if user_data.get("subscribed") or "customerId" in user_data:
        return jsonify({"error": "User is already subscribed"}), 401

    if "email" not in user_data or user_data.get("email") == "":
        return jsonify({"error": "User is must provide an email"}), 401

    payment_method_id = user_data.get("payment_method_id")

    if not payment_method_id:
        return jsonify({"error": "User is must provide a payment method ID"}), 401;

    try:
        customer = utils.utils.STRIPE.Customer.create(
            email=user_data.get("email"),  # Assuming you store email
            metadata={"userId": user_id}
        )

        utils.utils.STRIPE.PaymentMethod.attach(
            payment_method_id,
            customer=customer.id
        )

        # Set it as the default payment method
        utils.utils.STRIPE.Customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method_id}
        )

        subscription = utils.utils.STRIPE.Subscription.create(
            customer=customer.id,
            items=[{"price": utils.utils.STRIPE_PRICE_ID}],
            #expand=["latest_invoice.payment_intent"]
        )

        
                invoice = subscription.get("latest_invoice")
        
                payment_intent = invoice.get("payment_intent") if invoice else None
        



        return jsonify({
            "message": "Subscribed successfully",
            "customerId": customer.id,
            "subscriptionId": subscription.id,
            #"clientSecret": payment_intent["client_secret"] if payment_intent else None
        }), 200

    except utils.utils.STRIPE.error.utils.STRIPEError as e:
        return jsonify({"error": str(e)}), 400
"""

@subscription_bp.route("/<user_id>/confirm_subscription", methods=["POST"])
@utils.auth_required
def confirm_subscription(user_id):
    doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    doc_ref.update({
        "subscribed": True,
    })

    return jsonify({"message": "Subscription confirmed"}), 200

@subscription_bp.route(f"/<user_id>/cancel_subscription", methods=['POST'])
@utils.auth_required_subscribed
def cancel_subscription(user_id):
    """Cancel user's Stripe subscription."""
    user = g.user

    if user["userId"] != user_id:
        return jsonify({"error": "Unauthorized access to this user"}), 403

    try:
        # Get subscription and customer info from Firestore (not client)
        doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
        doc = doc_ref.get()
        customer_id = doc.get("customerId")
        subscription_id = doc.get("subscriptionId")

        if not customer_id or not subscription_id:
            return jsonify({"error": "No active subscription found for this user"}), 400

        utils.STRIPE.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True,

        )
        utils.STRIPE.Customer.delete(customer_id)

        # Update Firestore
        doc_ref.update({
            "subscribed": False,
            "customerId": None,
            "subscriptionId": None
        })

        return jsonify({"message": "Subscription cancelled successfully"}), 200

    except utils.STRIPE.error.StripeError as e:
        return jsonify({"error": f"Stripe error: {e.user_message}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to cancel subscription: {str(e)}"}), 500