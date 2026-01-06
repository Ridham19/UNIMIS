from flask import Flask, request, send_from_directory
from pymongo import MongoClient
from routes.auth import auth_bp
from routes.user import user_bp
from routes.attendance import attendance_bp
from routes.marks import marks_bp
from routes.notice import notice_bp
from routes.branch import branch_bp # Import new route
import os

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client["student_management_v2"]

    @app.before_request
    def inject_db():
        request.db = db

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix='/api')
    app.register_blueprint(marks_bp, url_prefix='/api')
    app.register_blueprint(notice_bp, url_prefix='/api')
    app.register_blueprint(branch_bp, url_prefix='/api')
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    from routes.subjects import subjects_bp
    app.register_blueprint(subjects_bp, url_prefix='/api')
    
    from routes.fees import fees_bp
    app.register_blueprint(fees_bp, url_prefix='/api')
    
    from routes.schedule import schedule_bp
    app.register_blueprint(schedule_bp, url_prefix='/api')
    
    from routes.courses import courses_bp
    app.register_blueprint(courses_bp, url_prefix='/api')
    
    from routes.results import results_bp
    app.register_blueprint(results_bp, url_prefix='/api')

    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(app.static_folder, path)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)