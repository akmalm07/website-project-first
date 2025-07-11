from flask import request, jsonify, g, Blueprint
import utils
import validate
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token



user_bp = Blueprint("user", __name__, url_prefix=f"/{utils.COLLECTION_NAME}")

@user_bp.route(f"/register", methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        is_valid, error_message = validate.is_valid_registration_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        name = data.get("name")
        email = data.get("email").lower()
        passcode = data.get("passcode")
        auth_provider = "local"

        if validate.find_user_by_email(email)[1]:
            return jsonify({"error": "Email already registered"}), 409

        user_data = {
            "name": name,
            "email": email,
            "passcode": passcode,
            "authProvider": auth_provider,
            "subscribed": False
        }

        _, doc_ref = utils.database.collection(utils.COLLECTION_NAME).add(user_data)

        doc_ref.update({"userId": doc_ref.id})

        return jsonify({
            "userId": doc_ref.id,
            "message": "User registered successfully",
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to register user: {e}"}), 500



@user_bp.route(f"/login", methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        is_valid, error_message = validate.is_valid_login_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        email = data.get("email").lower()
        passcode = data.get("passcode")

        user_id, user_data = validate.find_user_by_email(email)
        if not user_data:
            return jsonify({"error": "Invalid email"}), 401
        if user_data.get("authProvider") != "local":
            return jsonify({"error": "User did not authorize locally"}), 401

        stored_passcode = user_data.get("passcode")
        is_subscribed = user_data.get("subscribed")

        if stored_passcode == passcode:

            return jsonify({
                "message": "Login successful",
                "userId": user_id,
                "subscribed": is_subscribed
            }), 200
        else:
            return jsonify({"error": "Invalid passcode"}), 401

    except Exception as e:
        return jsonify({"error": f"Failed to login: {e}"}), 500



@user_bp.route('/auth/google', methods=['POST'])
def google_auth():
    """Registers a new user with Google OAuth ID token."""
    data = request.get_json()
    if not data or 'idToken' not in data:
        return jsonify({'error': 'Missing ID token'}), 400

    id_token_from_client = data['idToken']

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_from_client,
            google_requests.Request(),
            utils.GOOGLE_CLIENT_ID
        )

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        user_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture')

        if not email or not name:
            return jsonify({"error": "Email or name missing from token."}), 400

        user_id, _ = validate.find_user_by_email(email)
        if user_id:
            return jsonify({"error": "Email already registered"}), 409

        user_data = {
            "name": name,
            "email": email,
            "passcode": "",
            "authProvider": "google",
            "subscribed": False,
            "picture": picture
        }

        is_valid, error_message = validate.is_valid_registration_data(user_data, skip_passcode=True)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        _, doc_ref = utils.database.collection(utils.COLLECTION_NAME).add(user_data)

        doc_ref.update({
            "userId": doc_ref.id,
        })

        return jsonify({
            "userId": doc_ref.id,
            "message": "User registered successfully",
            "email": email,
            "name": name,
            "picture": picture,
        }), 201

    except ValueError as e:
        return jsonify({'error': f'Invalid Google ID token: {e}'}), 401
    except Exception as e:
        return jsonify({'error': f'Authentication error: {e}'}), 500


@user_bp.route('/auth/google_login', methods=['POST'])
def google_login():
    """Logs in a user via Google OAuth token."""

    data = request.get_json()
    if not data or 'idToken' not in data:
        return jsonify({'error': 'Missing ID token'}), 400

    id_token_from_client = data['idToken']

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_from_client,
            google_requests.Request(),
            utils.GOOGLE_CLIENT_ID
        )

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return jsonify({'error': 'Wrong issuer.'}), 401

        email = idinfo.get('email')
        name = idinfo.get('name')
        if not email or not name:
            return jsonify({"error": "Email or name missing from token."}), 400

        user_id, user_data = validate.find_user_by_email(email)
        if not user_id:
            return jsonify({"error": "User not registered. Please sign up first."}), 401

        if user_data.get("authProvider") != "google":
            return jsonify({"error": "This email is registered with a different login method."}), 401


        return jsonify({
            "message": "Login successful",
            "email": email,
            "name": name,
            "userId": user_data.get("userId", None),
            "subscribed": user_data.get("subscribed", None),
            "picture": idinfo.get("picture", None),
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid Google ID token: {e}'}), 401
    except Exception as e:
        return jsonify({'error': f'Authentication error: {e}'}), 500


@user_bp.route(f"/<user_id>", methods=['GET'])
@utils.auth_required
def get_user(user_id):
    """Retrieve user info. JWT must match user_id."""
    if g.user.get("userId") != user_id:
        return jsonify({"error": "Unauthorized access to this user"}), 403

    try:
        doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify({doc.id: doc.to_dict()}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve user: {e}"}), 500


@user_bp.route(f"/<user_id>", methods=['PUT'])
@utils.auth_required
def update_user(user_id):
    """Update user info. JWT must match user_id."""
    if g.user.get("userId") != user_id:
        return jsonify({"error": "Unauthorized access to this user"}), 403

    try:
        data = request.get_json()
        if not validate.is_valid_data(data):
            return jsonify({"error": "Invalid or empty data provided for update"}), 400

        doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
        if not doc_ref.get().exists:
            return jsonify({"error": "User not found, cannot update"}), 404

        protected_fields = ["passcode", "authProvider", "email", "userId", "subscribed"]
        for field in protected_fields:
            if field in data:
                return jsonify({"error": f"Cannot directly update {field} through this endpoint"}), 403

        doc_ref.update(data)
        return jsonify({"userId": user_id, "message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update user: {e}"}), 500


@user_bp.route(f"/<user_id>", methods=['DELETE'])
@utils.auth_required
def delete_user(user_id):
    """Delete user. JWT must match user_id."""
    if g.user.get("userId") != user_id:
        return jsonify({"error": "Unauthorized access to this user"}), 403

    try:
        doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
        if not doc_ref.get().exists:
            return jsonify({"error": "User not found"}), 404

        doc_ref.delete()
        return jsonify({"userId": user_id, "message": "User deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete user: {e}"}), 500




@user_bp.route(f"/<user_id>/change_passcode", methods=['POST'])
@utils.auth_required
def change_passcode(user_id):
    """Change user's passcode. Requires old passcode and new passcode."""
    if g.user.get("userId") != user_id:
        return jsonify({"error": "Unauthorized access to this user"}), 403

    try:
        data = request.get_json()
        old_passcode = data.get("oldPasscode")
        new_passcode = data.get("newPasscode")

        if not old_passcode or not new_passcode:
            return jsonify({"error": "Both oldPasscode and newPasscode are required"}), 400

        # Fetch user data
        doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = doc.to_dict()
        if user_data.get("authProvider") != "local":
            return jsonify({"error": "Password change only allowed for local accounts"}), 403

        if not validate.is_valid_password(new_passcode):
            return jsonify({"error": "Password must be at least 8 characters long, include one uppercase, one lowercase, one number, and one special character."}), 401

        if new_passcode == old_passcode:
            return jsonify({"error": "Passwords must not be the same."}), 401


        doc_ref.update({
            "passcode": new_passcode,
        })

        return jsonify({"message": "Passcode changed successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to change passcode: {e}"}), 500
