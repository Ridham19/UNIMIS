from flask import Blueprint, request, jsonify
from bson import ObjectId

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses/<user_id>', methods=['GET'])
def get_courses(user_id):
    db = request.db
    
    # 1. Get User
    user = db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 0, "password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    role = user.get('role')
    
    # 2. Logic by Role
    if role == 'student':
        # Get subjects for their Branch + Admission Year (mapped to Academic Year)
        branch = user.get('branch_code')
        # Simple Logic: 2025 admission = Year 1, 2024 = Year 2...
        adm_year = int(user.get('admission_year', 2025))
        current_year = 2025
        academic_year = current_year - adm_year + 1
        if academic_year < 1: academic_year = 1
        if academic_year > 4: academic_year = 4
        
        subjects = list(db.subjects.find({"branch_code": branch, "year": academic_year}, {"_id": 0}))
        return jsonify({"role": "student", "courses": subjects})
        
    elif role == 'teacher':
        # In a real app, we'd query a 'teacher_subjects' collection.
        # For now, return all subjects in their 'branch' (if they have one) or just everything.
        # Let's assume teachers have a 'branch_code' too, or we return global subjects.
        # To make it dynamic but simple:
        branch = user.get('branch_code')
        query = {"branch_code": branch} if branch else {} 
        # If no branch assigned, maybe return specific test subjects
        subjects = list(db.subjects.find(query, {"_id": 0}))
        return jsonify({"role": "teacher", "courses": subjects})
        
    elif role == 'admin':
        return jsonify({"role": "admin", "message": "Admins manage all courses via the Admin Panel."})
        
    return jsonify({"courses": []})
