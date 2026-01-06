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
        # Get subjects for their Branch + Current Semester
        branch = user.get('branch_code')
        try:
            adm_year = int(user.get('admission_year', 2025))
        except:
            adm_year = 2025
            
        # Current Date is Jan 2026 (Semesters start in July and Jan)
        # July 2025 = Sem 1, Jan 2026 = Sem 2
        # July 2024 = Sem 3, Jan 2026 = Sem 4
        # Calculate semester:
        # Years elapsed = 2026 - adm_year.
        # If we are in Jan, it's the even semester (2, 4, 6, 8).
        
        years_diff = 2026 - adm_year
        if years_diff < 0: years_diff = 0
        
        # 1st year (diff 1) -> Sem 2 (Jan 2026)
        # 2026 - 2025 = 1. 1*2 = 2.
        # 2nd year (2024) -> Sem 4. 2026-2024=2. 2*2=4.
        
        current_semester = (years_diff * 2)
        
        if current_semester == 0:
            # If admitted in 2026 and we are in Jan 2026, maybe Sem 1?
            current_semester = 1
        
        # Clamp to 8
        if current_semester > 8: current_semester = 8
        if current_semester < 1: current_semester = 1 
        
        subjects = list(db.subjects.find({"branch_code": branch, "semester": current_semester}, {"_id": 0}))
        
        # Fallback: if no subjects found for semester, maybe try 'year' for backward compat or empty
        if not subjects:
             # Try seeking by 'year' if semester migration not fully done in DB?
             # But user asked to fix courses tab for the new system. We trust 'semester' field exists.
             pass

        return jsonify({"role": "student", "courses": subjects, "current_semester": current_semester})
        
    elif role == 'teacher':
        # Teachers see subjects they are assigned (Round Robin + Even/Odd Filtering)
        branch = user.get('branch_code')
        if not branch:
             return jsonify({"role": "teacher", "courses": []})
        
        import datetime
        db = request.db
        
        # 1. Even/Odd Logic
        current_month = datetime.datetime.now().month
        is_even_cycle = 1 <= current_month <= 6
        allowed_semesters = [2, 4, 6, 8] if is_even_cycle else [1, 3, 5, 7]
        
        # 2. Fetch Relevant Subjects
        query = {
            "branch_code": branch,
            "semester": {'$in': allowed_semesters}
        }
        all_subjects = list(db.subjects.find(query, {"_id": 0}).sort([("semester", 1), ("name", 1)]))
        
        # 3. Round Robin Distribution
        teachers = list(db.users.find({"role": "teacher", "branch_code": branch}, {"_id": 1}).sort("_id", 1))
        teacher_ids = [str(t['_id']) for t in teachers]
        
        try:
            my_index = teacher_ids.index(str(user.get('_id')))
            total_teachers = len(teacher_ids)
            
            my_subjects = [s for i, s in enumerate(all_subjects) if i % total_teachers == my_index]
        except ValueError:
            my_subjects = all_subjects # Fallback

        return jsonify({"role": "teacher", "courses": my_subjects})
        
    elif role == 'admin':
        return jsonify({"role": "admin", "message": "Admins manage all courses via the Admin Panel."})
        
    return jsonify({"courses": []})
