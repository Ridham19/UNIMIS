from flask import Blueprint, request, jsonify
from models.marks import add_marks, get_marks_by_student

marks_bp = Blueprint('marks', __name__)

@marks_bp.route('/marks', methods=['POST'])
def add():
    data = request.json
    # Expects: student_id, subject_code, score
    # Optional: subject_name, semester (default 1), max_marks
    
    result = add_marks(
        request.db, 
        data['student_id'], 
        data.get('subject_code', data.get('subject')), # Support both 'subject' (legacy) and 'subject_code'
        data.get('subject_name', data.get('subject')), 
        data.get('semester', 1), # Default to 1 if not provided? Or look up student? Default 1 for now.
        data['score']
    )
    
    # UpdateResult object from update_one
    if result.upserted_id:
        return jsonify({'message': 'Marks added (New Record)', 'id': str(result.upserted_id)})
    else:
        return jsonify({'message': 'Marks updated'})

@marks_bp.route('/marks/<student_id>', methods=['GET'])
def get(student_id):
    records = get_marks_by_student(request.db, student_id)
    # records is now a simple list of dicts, no _id to convert
    return jsonify(records)

from utils.pdf_generator import generate_student_result
from flask import send_file

@marks_bp.route('/marks/pdf/<student_id>', methods=['GET'])
def download_pdf(student_id):
    db = request.db
    # 1. Get Student Info
    from models.user import get_user_by_id
    from bson import ObjectId
    
    student = db.users.find_one({"_id": ObjectId(student_id)})
    if not student:
        return jsonify({"error": "Student not found"}), 404
        
    # 2. Get Branch Name
    branch_code = student.get('branch_code')
    branch_name = branch_code
    if branch_code:
        b = db.branches.find_one({"code": branch_code})
        if b: branch_name = b['name']
        
    # 3. Get Marks
    marks = list(get_marks_by_student(db, student_id))
    
    # 4. Generate PDF
    pdf_buffer = generate_student_result(student, marks, branch_name)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Result_{student.get('admission_number', 'student')}.pdf",
        mimetype='application/pdf'
    )