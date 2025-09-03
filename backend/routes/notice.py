from flask import Blueprint, request, jsonify
from models.notice import create_notice, get_notices_for_role

notice_bp = Blueprint('notice', __name__)

@notice_bp.route('/notice', methods=['POST'])
def create():
    data = request.json
    result = create_notice(request.db, data['title'], data['content'], data['visible_to'])
    return jsonify({'inserted_id': str(result.inserted_id)})

@notice_bp.route('/notice/<role>', methods=['GET'])
def get(role):
    notices = get_notices_for_role(request.db, role)
    return jsonify(notices)