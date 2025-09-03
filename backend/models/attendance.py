def mark_attendance(db, student_id, date, status):
    record = {
        "student_id": student_id,
        "date": date,
        "status": status  # 'present' or 'absent'
    }
    return db.attendance.insert_one(record)

def get_attendance_by_student(db, student_id):
    return list(db.attendance.find({"student_id": student_id}))