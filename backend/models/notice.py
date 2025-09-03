def create_notice(db, title, content, visible_to):
    notice = {
        "title": title,
        "content": content,
        "visible_to": visible_to  # List of roles: ['student', 'teacher']
    }
    return db.notices.insert_one(notice)

def get_notices_for_role(db, role):
    return list(db.notices.find({"visible_to": role}))