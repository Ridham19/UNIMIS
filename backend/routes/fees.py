from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('/fees/<student_id>', methods=['GET'])
def get_fees(student_id):
    db = request.db
    # In a real app, verify token matches student_id or is admin
    
    fee_record = db.fees.find_one({"student_id": student_id}, {"_id": 0})
    if not fee_record:
         return jsonify({"error": "No fee record found"}), 404
         
    return jsonify(fee_record), 200

@fees_bp.route('/fees/<student_id>', methods=['PUT'])
def update_fee_status(student_id):
    db = request.db
    data = request.json
    status = data.get('status')
    
    if status not in ['Paid', 'Pending', 'Overdue']:
        return jsonify({"error": "Invalid status"}), 400
        
    result = db.fees.update_one(
        {"student_id": student_id},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": "No fee record found"}), 404
        
    return jsonify({"message": "Fee status updated"}), 200

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from flask import send_file

@fees_bp.route('/fees/receipt/<student_id>', methods=['GET'])
def download_receipt(student_id):
    db = request.db
    fee = db.fees.find_one({"student_id": student_id})
    user = db.users.find_one({"_id": ObjectId(student_id)})
    
    if not fee or not user:
        return jsonify({"error": "Data not found"}), 404
        
    # Generate PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Fee Receipt - UNIMIS")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Student Name: {user['name']}")
    p.drawString(100, 705, f"Admission No: {user.get('admission_number', 'N/A')}")
    p.drawString(100, 690, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    y = 650
    p.drawString(100, y, f"Tuition Fee: {fee.get('tuition', 0)}")
    p.drawString(100, y-20, f"Hostel Fee: {fee.get('hostel', 0)}")
    p.drawString(100, y-40, f"Library Fee: {fee.get('library', 0)}")
    p.drawString(100, y-60, f"Other Charges: {fee.get('other', 0)}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y-90, f"Total Amount: {fee.get('total', 0)}")
    p.drawString(100, y-110, f"Status: {fee.get('status', 'Pending')}")
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"receipt_{user.get('admission_number')}.pdf", mimetype='application/pdf')

