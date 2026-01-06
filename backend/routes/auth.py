from flask import Blueprint, request, jsonify
from models.user import find_user_by_email, create_user
import jwt
import datetime
import re # Regex for phone validation

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = "your_secret_key"

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if find_user_by_email(request.db, data['email']):
        return jsonify({'error': 'Email already exists'}), 400

    # --- 1. Phone Validation ---
    phone = data.get('phone', '')
    if not re.match(r'^\d{10}$', phone):
        return jsonify({'error': 'Mobile number must be exactly 10 digits'}), 400

    # Extract info
    additional_info = {
        "phone": phone,
        "dob": data.get('dob', ''),
        "address": data.get('address', ''),
        "branch_code": data.get('branch_code', '') # Save code (CS)
    }

    create_user(
        request.db, 
        data['name'], 
        data['email'], 
        data['password'], 
        data['role'],
        additional_info
    )
    
    return jsonify({'message': 'Registration successful. Please wait for approval.'})

# ... (Keep login route same as before) ...
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    identifier = data['email'] # Frontend sends both as 'email' field or we can change js. Let's keep field name 'email' in JS for simplicity or change it.
    
    # Check if identifier looks like Admission Number (Starts with 20 and has letters/numbers)
    # Simple heuristic: If it has '@', treat as email.
    
    user = None
    if '@' in identifier:
        user = find_user_by_email(request.db, identifier)
    else:
        # Search by admission_number
        user = request.db.users.find_one({"admission_number": identifier})

    if user and user['password'] == data['password']:
        if not user.get('is_approved', False):
            return jsonify({'error': 'Account not approved yet. Contact your Administrator/Teacher.'}), 403

        token = jwt.encode({
            'user_id': str(user['_id']),
            'role': user['role'],
            'branch_code': user.get('branch_code', ''),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm='HS256')
        
        if isinstance(token, bytes): token = token.decode('utf-8')
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401