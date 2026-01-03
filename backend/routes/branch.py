from flask import Blueprint, request, jsonify
from models.branch import create_branch, get_all_branches, delete_branch

branch_bp = Blueprint('branch', __name__)

@branch_bp.route('/branches', methods=['GET'])
def get_branches():
    branches = get_all_branches(request.db)
    return jsonify(branches)

@branch_bp.route('/branches', methods=['POST'])
def add_branch():
    data = request.json
    # In a real app, verify if requester is Admin here!
    create_branch(request.db, data['name'], data['code'])
    return jsonify({'message': 'Branch added successfully'})

@branch_bp.route('/branches/<code>', methods=['DELETE'])
def remove_branch(code):
    # In a real app, verify if requester is Admin here!
    delete_branch(request.db, code)
    return jsonify({'message': 'Branch removed'})