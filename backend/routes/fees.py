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
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
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
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- Header ---
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 50, "UNIMIS")
    
    c.setLineWidth(1.5)
    c.line(40, height - 75, width - 40, height - 75)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 105, "OFFICIAL FEE RECEIPT")
    
    # Calculate Semester (Standard Logic)
    try:
        adm_year = int(user.get('admission_year', 2025))
    except:
        adm_year = 2025
    years_diff = 2026 - adm_year
    if years_diff < 0: years_diff = 0
    current_semester = (years_diff * 2)
    if current_semester < 1: current_semester = 1
    if current_semester > 8: current_semester = 8

    # --- Student Details Table ---
    receipt_date = datetime.now().strftime('%Y-%m-%d')
    details_data = [
        ["Student Name:", user['name'], "Date:", receipt_date],
        ["Admission No:", user.get('admission_number', 'N/A'), "Receipt No:", f"REC-{int(datetime.utcnow().timestamp())}"],
        ["Branch:", user.get('branch_code', 'N/A'), "Semester:", str(current_semester)]
    ]
    
    details_table = Table(details_data, colWidths=[100, 180, 80, 140])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), # Labels bold
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'), # Labels bold
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    details_table.wrapOn(c, width, height)
    details_table.drawOn(c, 40, height - 170)
    
    # --- Fee Details Table ---
    # Prepare data rows
    data = [['Description', 'Amount (INR)']]
    
    # Add fee components
    items = [
        ('Tuition Fee', fee.get('tuition', 0)),
        ('Hostel Fee', fee.get('hostel', 0)),
        ('Library Fee', fee.get('library', 0)),
        ('Other Charges', fee.get('other', 0))
    ]
    
    total_amount = fee.get('total', 0)
    
    for label, amount in items:
        data.append([label, str(amount)])
    
    # Add Total Row
    data.append(['Total Amount', str(total_amount)])
    
    # Styling
    t = Table(data, colWidths=[350, 150])
    
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.4)), # Dark Blue Header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Description Left Aligned
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey), # Grid for items
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        
        # Total Row Style
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
    ]))
    
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, height - 230 - (len(data) * 20))
    
    table_bottom_y = height - 230 - (len(data) * 20)
    
    # --- Status Box ---
    status = fee.get('status', 'Pending')
    status_color = colors.green if status == 'Paid' else colors.red if status == 'Overdue' else colors.orange
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, table_bottom_y - 50, f"Payment Status: {status}")
    
    # --- Footer ---
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 30, "This is a computer generated document. No signature is required.")
    
    c.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Receipt_{user.get('admission_number')}.pdf", mimetype='application/pdf')
