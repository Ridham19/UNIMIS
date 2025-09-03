from flask import Blueprint, request, jsonify
from models.marks import add_marks, get_marks_by_student

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks', methods=['POST'])
def add():
    data = request.json
    result = add_marks(request.db, data['student_id'], data['subject'], data['score'])
    return jsonify({'inserted_id': str(result.inserted_id)})

@marks_bp.route('/marks/<student_id>', methods=['GET'])
def get(student_id):
    records = get_marks_by_student(request.db, student_id)
    return jsonify(records)