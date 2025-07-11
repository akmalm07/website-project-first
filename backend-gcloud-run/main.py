from flask_util import create_app
from user_account_handles import user_bp
from video_handles import video_bp
from subscription_handles import subscription_bp


app = create_app()

app.register_blueprint(user_bp)

app.register_blueprint(video_bp)

app.register_blueprint(subscription_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)