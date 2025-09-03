def add_marks(db, student_id, subject, score):
    entry = {
        "student_id": student_id,
        "subject": subject,
        "score": score
    }
    return db.marks.insert_one(entry)

def get_marks_by_student(db, student_id):
    return list(db.marks.find({"student_id": student_id}))