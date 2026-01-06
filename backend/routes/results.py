from flask import Blueprint, request, jsonify, send_file
from bson import ObjectId
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

results_bp = Blueprint('results', __name__)

@results_bp.route('/results/history/<student_id>', methods=['GET'])
def get_history(student_id):
    db = request.db
    # New Schema: One doc in 'student_results' with a 'results' array
    doc = db.student_results.find_one({"student_id": student_id})
    
    if not doc or 'results' not in doc:
        return jsonify({"semesters": []}), 200
        
    # Extract unique semesters
    semesters = sorted(list(set(r.get('semester', 1) for r in doc['results'])))
    
    return jsonify({"semesters": semesters}), 200

@results_bp.route('/results/download/<student_id>/<int:semester>', methods=['GET'])
def download_marksheet(student_id, semester):
    db = request.db
    
    # 1. Fetch Student
    student = db.users.find_one({"_id": ObjectId(student_id)})
    if not student:
        return jsonify({"error": "Student not found"}), 404

    # 2. Fetch Marks (Filter from single doc)
    doc = db.student_results.find_one({"student_id": student_id})
    marks = []
    if doc and 'results' in doc:
        marks = [m for m in doc['results'] if int(m.get('semester', 1)) == semester]
    
    if not marks:
        return jsonify({"error": "Data not found for this semester"}), 404
        
    # 2. Generate PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- Header ---
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 50, "UNIMIS")
    
    c.setLineWidth(1.5)
    c.line(40, height - 75, width - 40, height - 75)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 105, f"STATEMENT OF MARKS - SEMESTER {semester}")
    
    # --- Student Details Table ---
    # Using a table ensures perfect alignment
    details_data = [
        ["Student Name:", student['name'], "Admission No:", student.get('admission_number', 'N/A')],
        ["Branch:", student.get('branch_code', 'N/A'), "Session:", str(student.get('admission_year', 'N/A'))]
    ]
    
    details_table = Table(details_data, colWidths=[100, 180, 100, 140])
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
    
    # --- Marks Table ---
    data = [['Subject Code', 'Subject Name', 'Mid Term', 'End Term', 'Total', 'Grade']]
    
    total_score = 0
    max_score = 0
    
    for m in marks:
        # Calculate grade if not present or just ensure it's displayed
        # Assuming grade is in DB, if not we could calc it, but let's trust DB
        data.append([
            m['subject_code'],
            m['subject_name'],
            str(m.get('mid_term', '-')),
            str(m.get('end_term', '-')),
            str(m.get('total', '-')),
            m.get('grade', '-')
        ])
        if isinstance(m.get('total'), (int, float)):
            total_score += m.get('total')
        max_score += 100
        
    t = Table(data, colWidths=[80, 230, 60, 60, 50, 50])
    
    # Professional Styling
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.4)), # Dark Blue Header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Align Subject Names to Left
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]), # Alternating rows
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, height - 200 - (len(data) * 20) - 50) # Adjust Y based on rows
    
    table_bottom_y = height - 200 - (len(data) * 20) - 50
    
    # --- Footer / Summary ---
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Result Summary Box
    c.setLineWidth(1)
    c.rect(40, table_bottom_y - 60, width - 80, 40, stroke=1, fill=0)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, table_bottom_y - 35, f"Grand Total: {total_score} / {max_score}")
    c.drawString(250, table_bottom_y - 35, f"Percentage: {percentage:.2f}%")
    
    result_status = "PASS" if percentage >= 40 else "FAIL"
    c.drawString(450, table_bottom_y - 35, f"Result: {result_status}")
    
    # Signatures
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 30, "This is a computer generated document. No signature is required.")
    
    c.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Result_Sem{semester}_{student.get('admission_number')}.pdf", mimetype='application/pdf')
