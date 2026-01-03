from flask import Blueprint, request, jsonify
from bson import ObjectId

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedule/<student_id>', methods=['GET'])
def get_schedule(student_id):
    db = request.db
    
    # 1. Get Student for Branch/Year
    student = db.users.find_one({"_id": ObjectId(student_id)})
    if not student or student['role'] != 'student':
        return jsonify({"error": "Student not found"}), 404
        
    branch = student.get('branch_code', 'CS')
    # Admission Year to Academic Year logic (Simulated)
    # If 2025 -> Year 1. 2024 -> Year 2.
    # Current context 2025.
    
    adm_year = int(student.get('admission_year', 2025))
    current_year = 2025
    academic_year = current_year - adm_year + 1
    if academic_year < 1: academic_year = 1
    if academic_year > 4: academic_year = 4
    
    # 2. Find Schedule
    schedule = db.schedules.find_one({
        "branch_code": branch,
        "year": academic_year
    }, {"_id": 0})
    
    if not schedule:
        return jsonify({"message": "Schedule not uploaded yet", "days": {}}), 200
        
    return jsonify(schedule), 200
