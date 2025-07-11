import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import firestore
from dotenv import load_dotenv
import os
from flask import request, jsonify, g
import stripe as STRIPE
from functools import wraps
from google.cloud import storage
from google.oauth2 import service_account
import json

load_dotenv()

COLLECTION_NAME = "users"

if not firebase_admin._apps:
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(credential=cred)
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        exit()

database = firestore.client()


PROJECT_ID = os.getenv("PROJ_ID")
AUTHORIZED_USER = os.getenv("AUTHORIZED_USER")
AUTHORIZED_PASSCODE = os.getenv("AUTHORIZED_PASSCODE")
AUTHORIZED_SECRET = os.getenv("AUTHORIZED_SECRET")

if not PROJECT_ID:
    print("Error: GCP_PROJECT_ID environment variable not set.")



GOOGLE_CLIENT_ID = 123
STRIPE.api_key = 123
STRIPE_PRICE_ID = 123

STRIPE_WEBHOOK_SECRET = 123

PAYMENT_SUCCESS_REDIRECT_URL = "https://contentvault.club/exclusive_content_page.html"

VIDEOS_COLLECTION = 'videos'
VIDEO_BUCKET_NAME = "no-licence-vids"




with open('secret/signing_key-gcloud.json') as f: # Must add manually
    signing_key_json = json.load(f)

credentials = service_account.Credentials.from_service_account_info(signing_key_json)

VIDEO_STORAGE_CLIENT = storage.Client(project=PROJECT_ID, credentials=credentials)


def auth_required(f):
    """Decorator to check if the user ID in Authorization header exists in Firestore and is subscribed."""

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.headers.get('Authorization', '').strip()

        if not user_id:
            return jsonify({"error": "Missing Authorization header"}), 401

        user_ref = database.collection(COLLECTION_NAME).document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({
                "error": "User not found",
                "debug": {
                    "user_id": user_id,
                    "collection": COLLECTION_NAME
                }
            }), 401

        user_data = user_doc.to_dict()

        g.user = {
            "userId": user_id,
            "data": user_data,
            "firestore_path": f"{COLLECTION_NAME}/{user_id}"
        }

        return f(*args, **kwargs)

    return decorated


def auth_required_subscribed(f):
    """Decorator to check if the user ID in Authorization header exists and is subscribed."""

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.headers.get('Authorization', '').strip()

        if not user_id:
            return jsonify({"error": "Missing Authorization header"}), 401

        user_ref = database.collection(COLLECTION_NAME).document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({
                "error": "User not found",
                "debug": {
                    "user_id": user_id,
                    "collection": COLLECTION_NAME
                }
            }), 401

        user_data = user_doc.to_dict()

        if not user_data.get("subscribed", False):
            return jsonify({
                "error": "User not subscribed",
                "user_location": f"{COLLECTION_NAME}/{user_id}"
            }), 403

        g.user = {
            "userId": user_id,
            "data": user_data,
            "firestore_path": f"{COLLECTION_NAME}/{user_id}"
        }

        return f(*args, **kwargs)

    return decorated