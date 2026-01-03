from bson import ObjectId
import datetime

def create_user(db, name, email, password, role, additional_info=None):
    if additional_info is None:
        additional_info = {}

    user = {
        "name": name,
        "email": email,
        "password": password, 
        "role": role,
        "is_approved": False,
        **additional_info
    }

    # --- NEW: Admission Number Logic (Only for Students) ---
    if role == 'student' and 'branch_code' in additional_info:
        branch_code = additional_info['branch_code']
        current_year = str(datetime.datetime.now().year)
        
        # Count existing students in this branch for this year to find the sequence
        # We need to store admission_year to count correctly next time
        user['admission_year'] = current_year
        
        count = db.users.count_documents({
            "role": "student", 
            "branch_code": branch_code, 
            "admission_year": current_year
        })
        
        # Sequence is count + 1 (e.g., if 0 exist, this is #1)
        sequence = count + 1
        
        # Format: {Year}{Abbr}{No} -> 2025CS001
        # :03d pads the number with zeros (1 -> 001, 15 -> 015)
        admission_number = f"{current_year}{branch_code}{sequence:03d}"
        
        user['admission_number'] = admission_number

    return db.users.insert_one(user)

def find_user_by_email(db, email):
    return db.users.find_one({"email": email})

def get_user_by_id(db, user_id):
    try:
        return db.users.find_one({"_id": user_id})
    except:
        return None

def get_pending_users_by_role(db, role):
    return list(db.users.find({"role": role, "is_approved": False}))

def approve_user_by_id(db, user_id):
    return db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_approved": True}}
    )