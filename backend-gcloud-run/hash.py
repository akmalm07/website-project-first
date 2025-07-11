import bcrypt


def hash_password(password):
    """Hashes the password using bcrypt with an automatically generated salt."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def check_password(stored_hash, password):
    """Checks if the provided password matches the stored hash using bcrypt."""
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
