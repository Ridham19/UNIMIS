from flask import Blueprint, request, jsonify
from models.notice import create_notice, get_notices_for_role

notice_bp = Blueprint('notice', __name__)

@notice_bp.route('/notices', methods=['POST'])
def create():
    data = request.json
    visible_to = data.get('visible_to', [])
    if isinstance(visible_to, str):
        visible_to = [visible_to]
        
    # Default to Admin for now, or extract from token if we had it here
    posted_by = data.get('posted_by', 'Admin')
        
    result = create_notice(request.db, data['title'], data['content'], visible_to, posted_by)
    return jsonify({'inserted_id': str(result.inserted_id)})

@notice_bp.route('/notices/<role>', methods=['GET'])
def get(role):
    # If role is 'all' or 'admin', maybe return everything? 
    # For now, stick to role-based filtering.
    notices = get_notices_for_role(request.db, role)
    for notice in notices:
        notice['_id'] = str(notice['_id'])
    return jsonify(notices)