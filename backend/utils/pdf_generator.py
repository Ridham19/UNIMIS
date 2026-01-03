from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

def generate_student_result(student, marks, branch_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- Header ---
    # Dummy Logo placeholder (if file existed, would use Image('logo.png'))
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], alignment=1, fontSize=24, spaceAfter=20, textColor=colors.darkblue)
    elements.append(Paragraph("University of Technology", header_style))
    
    sub_header_style = ParagraphStyle('SubHeader', parent=styles['Normal'], alignment=1, fontSize=14, spaceAfter=30)
    elements.append(Paragraph("Official Semester Result - 2024", sub_header_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # --- Student Details ---
    # Table logic
    data = [
        ["Student Name:", student.get('name', 'N/A'), "Admission No:", student.get('admission_number', 'N/A')],
        ["Branch:", branch_name, "Year:", student.get('admission_year', 'N/A')],
        ["Email:", student.get('email', 'N/A'), "Date of Birth:", student.get('dob', 'N/A')]
    ]
    
    t = Table(data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.0*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTWEIGHT', (0,0), (0,-1), 'Bold'),
        ('FONTWEIGHT', (2,0), (2,-1), 'Bold'),
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*inch))
    
    # --- Marks Table ---
    marks_data = [["Subject", "Score", "Max Marks", "Grade", "Status"]]
    
    total_score = 0
    total_max = 0
    
    for m in marks:
        score = m.get('score', 0)
        max_m = 100 # m.get('total_marks', 100)
        total_score += score
        total_max += max_m
        
        # Grading Logic
        if score >= 90: grade = 'A+'; status = 'Pass'
        elif score >= 80: grade = 'A'; status = 'Pass'
        elif score >= 70: grade = 'B'; status = 'Pass'
        elif score >= 60: grade = 'C'; status = 'Pass'
        elif score >= 40: grade = 'D'; status = 'Pass'
        else: grade = 'F'; status = 'Fail'
        
        marks_data.append([m.get('subject', 'Unknown'), str(score), str(max_m), grade, status])
    
    # Footer Row
    marks_data.append(["TOTAL", str(total_score), str(total_max), "", ""])
    
    t2 = Table(marks_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.lightgrey]),
        ('FONTWEIGHT', (0,-1), (-1,-1), 'Bold'), # Footer bold
    ]))
    elements.append(t2)
    
    elements.append(Spacer(1, 0.5*inch))
    
    # --- Summary ---
    gpa = (total_score / total_max) * 10 if total_max > 0 else 0
    cgpa_style = ParagraphStyle('CGPA', parent=styles['Normal'], fontSize=12, textColor=colors.black)
    elements.append(Paragraph(f"<b>Scored Percentage:</b> { (total_score/total_max)*100:.2f}%", cgpa_style))
    elements.append(Paragraph(f"<b>Calculated GPA:</b> {gpa:.2f} / 10.0", cgpa_style))
    
    elements.append(Spacer(1, 1*inch))
    
    # --- Footer ---
    footer_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=2)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
