from flask import Blueprint, request, jsonify
from models.attendance import mark_attendance, get_attendance_by_student

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['POST'])
def mark():
    data = request.json
    result = mark_attendance(request.db, data['student_id'], data['date'], data['status'])
    return jsonify({'inserted_id': str(result.inserted_id)})

@attendance_bp.route('/attendance/<student_id>', methods=['GET'])
def get_attendance(student_id):
    records = get_attendance_by_student(request.db, student_id)
    return jsonify(records)