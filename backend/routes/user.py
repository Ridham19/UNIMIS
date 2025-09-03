from flask import Blueprint, request, jsonify
from models.user import create_user, get_user_by_id

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(request.db, user_id)
    if user:
        user['_id'] = str(user['_id'])
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@user_bp.route('/user', methods=['POST'])
def register_user():
    data = request.json
    result = create_user(request.db, data['name'], data['email'], data['password'], data['role'])
    return jsonify({'inserted_id': str(result.inserted_id)})