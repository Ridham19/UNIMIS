from flask import Flask, request
from pymongo import MongoClient
from routes.auth import auth_bp
from routes.user import user_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp
from routes.notice import notice_bp

def create_app():
    app = Flask(__name__)

    # MongoDB setup
    client = MongoClient("mongodb://localhost:27017/")
    db = client["student_management"]

    # Middleware to inject db into request
    @app.before_request
    def inject_db():
        request.db = db

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix='/api')
    app.register_blueprint(marks_bp, url_prefix='/api')
    app.register_blueprint(notice_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)