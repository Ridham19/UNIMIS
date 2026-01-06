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
    # Use seeded current_semester
    semester = student.get('current_semester', 1)
    
    # 2. Find Schedule (Collection name is 'schedule' in recent seed, not 'schedules')
    # Also we match by 'semester' now
    schedule_doc = db.schedule.find_one({
        "branch_code": branch,
        "semester": semester
    }, {"_id": 0})
    
    if not schedule_doc:
        return jsonify({"message": f"Schedule for Sem {semester} not found", "days": {}}), 200

    # Inject Teachers dynamically
    teachers = list(db.users.find({"role": "teacher", "branch_code": branch}, {"name": 1}).sort("_id", 1))
    
    # Clean emojis from names for display and assign teachers
    import re
    
    for day, classes in schedule_doc.get('days', {}).items():
        for c in classes:
            orig_subj = c.get('subject', '')
            # Clean emoji
            clean_subj = re.sub(r'[^\x00-\x7F]+', '', orig_subj).strip()
            c['subject'] = clean_subj
            
            if c.get('type') != 'break':
                if teachers:
                    # Deterministic random assignment based on subject name length or hash
                    # This ensures the same subject always gets the same teacher for this student
                    idx = sum(ord(ch) for ch in clean_subj) % len(teachers)
                    c['teacher'] = teachers[idx]['name']
                else:
                    c['teacher'] = "Faculty"
                
    return jsonify(schedule_doc), 200
