from flask import Blueprint, request, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/faculty-by-branch', methods=['GET'])
def get_faculty_by_branch():
    db = request.db
    # Get branch from query param if provided, else return all grouped?
    # Requirement: See branchwise faculty.
    
    branch = request.args.get('branch')
    query = {"role": "teacher"}
    
    if branch:
        query["branch_code"] = branch
        
    faculty = list(db.users.find(query, {"password": 0}))
    for f in faculty:
        f['_id'] = str(f['_id'])
    return jsonify(faculty), 200

@admin_bp.route('/admin/students-by-year', methods=['GET'])
def get_students_by_year():
    db = request.db
    import math
    
    branch = request.args.get('branch')
    year = request.args.get('year')
    semester = request.args.get('semester')
    
    query = {"role": "student"}
    
    if branch:
        query["branch_code"] = branch
        
    if semester:
        try:
            sem_val = int(semester)
            # Map Semester to Admission Year
            # Sem 1/2 -> Year 1 (2025)
            # Sem 3/4 -> Year 2 (2024)
            # Formula: 2026 - ceil(sem/2)
            calc_year = 2026 - math.ceil(sem_val / 2)
            query["admission_year"] = calc_year
        except ValueError:
            pass # Invalid semester format
            
    elif year: # Fallback to direct year if provided
        try:
            query["admission_year"] = int(year)
        except:
            query["admission_year"] = year
        
    students = list(db.users.find(query, {"password": 0}))
    
    # Calculate current semester for display in frontend
    # Logic: (2026 - admission_year) * 2? 
    # Actually, let's just use the same logic we have in courses.py
    for s in students:
        s['_id'] = str(s['_id'])
        adm = int(s.get('admission_year', 2025))
        diff = 2026 - adm
        if diff < 0: diff = 0
        s['current_semester'] = diff * 2
        # Clamp? No, let's just be raw or clamp 1-8
        if s['current_semester'] == 0: s['current_semester'] = 1 # New entrants
        if s['current_semester'] > 8: s['current_semester'] = 8

    return jsonify(students), 200

@admin_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    db = request.db
    # Helper to get available branches and years for dropdowns
    branches = list(db.branches.find({}, {"_id": 0, "code": 1, "name": 1}))
    
    # Get distinct years from students
    years = db.users.distinct("admission_year", {"role": "student"})
    years.sort(reverse=True) # Recent years first
    
    return jsonify({
        "branches": branches,
        "years": years
    }), 200
