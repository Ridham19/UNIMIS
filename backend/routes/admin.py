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
        
    faculty = list(db.users.find(query, {"_id": 0, "password": 0}))
    return jsonify(faculty), 200

@admin_bp.route('/admin/students-by-year', methods=['GET'])
def get_students_by_year():
    db = request.db
    # Requirement: Year wise students (and user requested random students to each year in each branch)
    # The user updated plan says: Select Branch -> Select Year -> Show Student Table
    
    branch = request.args.get('branch')
    year = request.args.get('year')
    
    query = {"role": "student"}
    
    if branch:
        query["branch_code"] = branch
    if year:
        query["admission_year"] = year
        
    students = list(db.users.find(query, {"_id": 0, "password": 0}))
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
