from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance/<student_id>', methods=['GET'])
def get_attendance(student_id):
    db = request.db
    
    # 1. Get All Attendance Records for Student
    records = list(db.attendance.find({"student_id": student_id}))
    
    # 2. Aggregate by Subject
    current_date = datetime.now()
    summary = {}
    
    # Structure: { 'SubjectName': { 'total': 0, 'present': 0, 'absent': 0 } }
    
    for r in records:
        subj = r.get('subject', 'General') # Fallback if no subject
        status = r.get('status')
        
        if subj not in summary:
            summary[subj] = {'total': 0, 'present': 0, 'absent': 0}
            
        summary[subj]['total'] += 1
        if status == 'Present':
            summary[subj]['present'] += 1
        else:
            summary[subj]['absent'] += 1
            
    # 3. Format result
    result = []
    for subj, stats in summary.items():
        total = stats['total']
        present = stats['present']
        percentage = (present / total * 100) if total > 0 else 0
        
        result.append({
            "subject": subj,
            "total_classes": total,
            "present": present,
            "absent": stats['absent'],
            "percentage": round(percentage, 1)
        })
        
    # Also calculate Overall
    total_all = sum(x['total_classes'] for x in result)
    present_all = sum(x['present'] for x in result)
    overall_pct = (present_all / total_all * 100) if total_all > 0 else 0
    
    return jsonify({
        "overall_percentage": round(overall_pct, 1),
        "details": result
    })

@attendance_bp.route('/attendance', methods=['POST'])
def mark_attendance():
    # Only Teachers should hit this
    data = request.json
    db = request.db
    
    # data: { student_id, date, status, subject }
    
    if not all(k in data for k in ['student_id', 'date', 'status', 'subject']):
         return jsonify({"error": "Missing fields"}), 400
         
    db.attendance.insert_one(data)
    return jsonify({"message": "Attendance marked"}), 201