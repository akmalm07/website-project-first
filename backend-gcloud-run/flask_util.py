from flask import Flask
from flask_cors import CORS

def create_app():
    """Creates and configures the Flask application."""
    app = Flask(__name__)
    CORS(app, origins="*")
    #  Initialize other extensions (if any) here
    return app