from datetime import datetime

def create_notice(db, title, content, visible_to, posted_by="Admin"):
    notice = {
        "title": title,
        "content": content,
        "visible_to": visible_to,
        "posted_by": posted_by,
        "date": datetime.now()
    }
    return db.notices.insert_one(notice)

def get_notices_for_role(db, role):
    return list(db.notices.find({"visible_to": role}))