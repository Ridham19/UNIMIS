from flask import Blueprint, request, jsonify

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/subjects', methods=['GET'])
def get_subjects():
    db = request.db
    branch = request.args.get('branch')
    year = request.args.get('year')
    
    query = {}
    if branch: query['branch_code'] = branch
    if year: query['year'] = int(year)
    
    subjects = list(db.subjects.find(query, {"_id": 0}))
    return jsonify(subjects), 200

@subjects_bp.route('/subjects', methods=['POST'])
def add_subject():
    db = request.db
    data = request.json
    
    # Validation
    if not all(k in data for k in ['name', 'code', 'branch_code', 'year']):
        return jsonify({"error": "Missing fields"}), 400
        
    # Check duplicate
    if db.subjects.find_one({"code": data['code']}):
         return jsonify({"error": "Subject code exists"}), 400
         
    # Ensure year is int
    data['year'] = int(data['year'])
    
    db.subjects.insert_one(data)
    return jsonify({"message": "Subject Added"}), 201
