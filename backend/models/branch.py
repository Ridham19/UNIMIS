def create_branch(db, name, code):
    # Avoid duplicates
    if db.branches.find_one({"code": code}):
        return None
    branch = {
        "name": name,
        "code": code.upper() # e.g., 'CS', 'ME'
    }
    return db.branches.insert_one(branch)

def get_all_branches(db):
    return list(db.branches.find({}, {"_id": 0})) # Return list without ObjectIds

def delete_branch(db, code):
    return db.branches.delete_one({"code": code})