from flask import jsonify
import validate
import utils


def handle_google_login(email):
    """Handles Google login for an existing user."""
    user_id, user_data = validate.find_user_by_email(email)
    if user_data and user_data.get("authProvider") == "google":
        return jsonify({"message": "Google login successful", "userId": user_id}), 200
    else:
        return (
            jsonify({"error": "User not registered with Google"}),
            404,
        )  # Not Found


def handle_google_registration(email, name):
    """Handles Google registration for a new user."""
    user_data = {
        "email": email,
        "name": name,  # Get name if available
        "authProvider": "google",
    }
    _, doc_ref = utils.database.collection(utils.COLLECTION_NAME).add(user_data)
    return (
        jsonify({"message": "Google user registered and logged in", "userId": doc_ref.id}),
        200,
    )