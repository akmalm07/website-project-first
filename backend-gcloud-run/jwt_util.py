"""

import jwt
import datetime
from flask import request, jsonify, g
from functools import wraps
import validate
import os
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is not set")

JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600

def generate_jwt(payload: dict) -> str:
    payload_copy = payload.copy()
    payload_copy["exp"] = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    token = jwt.encode(payload_copy, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_jwt(token: str) -> dict:
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return decoded

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401

        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'error': 'Authorization header must be Bearer token'}), 401

        token = parts[1]

        try:
            payload = decode_jwt(token)
            user_id = payload.get('userId')
            if not user_id or not validate.find_user_by_id(user_id)[1]:
                return jsonify({'error': 'User not found'}), 401

            g.current_user = validate.find_user_by_id(user_id)[1]
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication error: {str(e)}'}), 401

    return decorated_function

"""