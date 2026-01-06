from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance/<student_id>', methods=['GET'])
def get_attendance(student_id):
    db = request.db
    
    # 1. Get Efficient Attendance Record
    record = db.attendance_summary.find_one({"student_id": student_id})
    attendance_data = record.get('attendance', {}) if record else {}
    
    # 2. Get User & Current Semester Subjects
    user = db.users.find_one({"_id": ObjectId(student_id)})
    if not user:
        return jsonify({"overall_percentage": 0, "details": []})
        
    # Calculate Semester (Logic copied from courses.py for consistency)
    try:
        adm_year = int(user.get('admission_year', 2025))
    except:
        adm_year = 2025
    years_diff = 2026 - adm_year
    if years_diff < 0: years_diff = 0
    current_semester = (years_diff * 2)
    if current_semester == 0: current_semester = 1
    if current_semester > 8: current_semester = 8
    if current_semester < 1: current_semester = 1 
    
    # Fetch Subjects for this Semester
    branch = user.get('branch_code')
    current_subjects = list(db.subjects.find({"branch_code": branch, "semester": current_semester}))
    
    # 3. Format details (Show ALL current subjects, with 0 if no data)
    result = []
    total_classes_all = 0
    total_present_all = 0
    
    for sub in current_subjects:
        subj_name = sub['name']
        stats = attendance_data.get(subj_name, {'total': 0, 'present': 0})
        
        total = stats.get('total', 0)
        present = stats.get('present', 0)
        absent = total - present
        percentage = (present / total * 100) if total > 0 else 0
        
        result.append({
            "subject": subj_name,
            "total_classes": total,
            "present": present,
            "absent": absent,
            "percentage": round(percentage, 1)
        })
        
        total_classes_all += total
        total_present_all += present
        
    # 4. Calculate Overall
    overall_pct = (total_present_all / total_classes_all * 100) if total_classes_all > 0 else 0
    
    return jsonify({
        "overall_percentage": round(overall_pct, 1),
        "details": result,
        "semester": current_semester
    })

@attendance_bp.route('/attendance', methods=['POST'])
def mark_attendance():
    # Only Teachers should hit this
    data = request.json
    db = request.db
    
    # data: { student_id, date, status, subject }
    
    if not all(k in data for k in ['student_id', 'date', 'status', 'subject']):
         return jsonify({"error": "Missing fields"}), 400
         
    _process_attendance(db, data)
    return jsonify({"message": "Attendance marked"}), 201

@attendance_bp.route('/attendance/bulk', methods=['POST'])
def mark_bulk_attendance():
    data = request.json
    db = request.db
    
    items = data.get('attendance_list', [])
    if not items:
        return jsonify({"message": "No data provided"}), 400
        
    for item in items:
        # Validate minimal fields
        if all(k in item for k in ['student_id', 'date', 'status', 'subject']):
             _process_attendance(db, item)
             
    return jsonify({"message": f"Bulk attendance marked for {len(items)} students"}), 201

def _process_attendance(db, data):
    student_id = data['student_id']
    subject = data['subject']
    status = data['status']
    date = data['date'] # YYYY-MM-DD
    
    update_query = {
        "$inc": { f"attendance.{subject}.total": 1 }
    }
    
    if status == 'Present':
        update_query["$inc"][f"attendance.{subject}.present"] = 1
        
    status_code = "P" if status == 'Present' else "A"
    log_entry = f"{date}:{status_code}"
    
    full_update = update_query
    full_update["$push"] = { f"attendance.{subject}.log": log_entry }
    
    db.attendance_summary.update_one(
        {"student_id": student_id},
        full_update,
        upsert=True
    )

@attendance_bp.route('/attendance/teacher/subjects', methods=['GET'])
def get_teacher_subjects():
    # Enforce Branch Filter from Token
    import jwt
    import datetime
    SECRET_KEY = "your_secret_key" # Matching auth.py
    
    auth_header = request.headers.get('Authorization')
    branch_code = None
    user_id = None
    
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # Verify User in DB to get latest branch
            db = request.db
            from bson import ObjectId
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                branch_code = user.get('branch_code')
        except Exception as e:
            print(f"Token verification failed: {e}")
            pass

    if not branch_code or not user_id:
        return jsonify([])

    db = request.db
    
    # 1. Filter by Semester Type (Odd/Even)
    current_month = datetime.datetime.now().month
    # Even Semesters: Jan(1) to June(6) -> 2, 4, 6, 8
    # Odd Semesters: July(7) to Dec(12) -> 1, 3, 5, 7
    is_even_cycle = 1 <= current_month <= 6
    allowed_semesters = [2, 4, 6, 8] if is_even_cycle else [1, 3, 5, 7]
    
    # 2. Fetch All Relevant Subjects for Branch & Semester Cycle
    query = {
        'branch_code': branch_code,
        'semester': {'$in': allowed_semesters}
    }
    all_subjects = list(db.subjects.find(query, {"_id": 0, "name": 1, "code": 1, "semester": 1, "branch_code": 1}).sort([("semester", 1), ("name", 1)]))
    
    # 3. Distribute Subjects Among Teachers (Round Robin)
    # Get all teachers for this branch to determine order
    teachers = list(db.users.find({"role": "teacher", "branch_code": branch_code}, {"_id": 1}).sort("_id", 1))
    teacher_ids = [str(t['_id']) for t in teachers]
    
    try:
        my_index = teacher_ids.index(str(user_id))
        total_teachers = len(teacher_ids)
        
        # Filter subjects: keep only those where (index % total_teachers) == my_index
        my_subjects = [s for i, s in enumerate(all_subjects) if i % total_teachers == my_index]
        
    except ValueError:
        # Fallback if user not found in teacher list (shouldn't happen)
        my_subjects = all_subjects

    return jsonify(my_subjects)

@attendance_bp.route('/attendance/class-list/<subject_code>', methods=['GET'])
def get_class_list_for_subject(subject_code):
    db = request.db
    
    # 1. Find Subject Metadata
    subject = db.subjects.find_one({"code": subject_code})
    if not subject:
        return jsonify({"error": "Subject not found"}), 404
        
    branch = subject.get("branch_code")
    try:
        semester = int(subject.get("semester", 1)) # Force int
    except:
        semester = 1
    
    # 2. Convert Semester to Admission Year
    # formula: 2026 - ceil(sem/2)
    import math
    admission_year_est = 2026 - math.ceil(semester / 2)
    
    # Query Students (ensure admission_year is string as per DB schema)
    query = {
        "role": "student",
        "branch_code": branch,
        "admission_year": str(int(admission_year_est))
    }
    
    students = list(db.users.find(query, {"name": 1, "admission_number": 1}))
    for s in students:
        s['_id'] = str(s['_id'])
        
    return jsonify({
        "subject": subject['name'],
        "branch": branch,
        "semester": semester,
        "students": students
    })