import bcrypt
import utils
import re

def is_valid_data(data):
    return isinstance(data, dict) and data

def check_password(stored_hash, password, salt):
    """Checks if the provided password matches the stored hash using the salt."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
    return hashed_password.decode('utf-8') == stored_hash

def find_user_by_email(email):
    """Checks if a user with the given email exists."""
    users_ref = utils.database.collection(utils.COLLECTION_NAME)
    query = users_ref.where("email", "==", email).limit(1)
    results = query.stream()
    for doc in results:
        return doc.id, doc.to_dict()
    return None, None

def find_user_by_id(user_id):
    """Checks if a user with the given document ID exists."""
    doc_ref = utils.database.collection(utils.COLLECTION_NAME).document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.id, doc.to_dict()
    return None, None

def is_valid_registration_data(data, skip_passcode = False):
    """Validates registration data (name, email, passcode)."""
    if not all(key in data for key in ["name", "email", "passcode"]):
        return False, "Missing required fields (name, email, passcode)"
    if not is_valid_email(data["email"]):
        return False, "Please enter a valid email address."
    if not skip_passcode:
        if not is_valid_password(data["passcode"]):
            return False, "Password must be at least 8 characters long and include one uppercase, one lowercase, one number, and one special character."
    return True, None

def is_valid_login_data(data):
    """Validates login data (email, passcode)."""
    if not all(key in data for key in ["email", "passcode"]):
        return False, "Missing required fields (email, passcode)"
    if not is_valid_email(data["email"]):
        return False, "Please enter a valid email address."
    if not data["passcode"]:
        return False, "Password cannot be empty."
    return True, None

def is_valid_email(email):
    """Checks if the email format is valid."""
    email_regex = re.compile(r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return bool(email_regex.match(email))

def is_valid_password(password):
    password_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}:\"<>?;.,]).{8,}$")
    return bool(password_regex.match(password))