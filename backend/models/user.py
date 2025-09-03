def create_user(db, name, email, password, role):
    user = {
        "name": name,
        "email": email,
        "password": password,  # You should hash this before storing
        "role": role           # 'student', 'teacher', 'hod', 'dean', 'admin'
    }
    return db.users.insert_one(user)

def find_user_by_email(db, email):
    return db.users.find_one({"email": email})

def get_user_by_id(db, user_id):
    return db.users.find_one({"_id": user_id})