from flask import Blueprint, request, jsonify
from models.user import find_user_by_email
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = "your_secret_key"  # Replace with env variable in production

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = find_user_by_email(request.db, data['email'])

    if user and user['password'] == data['password']:  # Add hashing check
        token = jwt.encode({
            'user_id': str(user['_id']),
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401