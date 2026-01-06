def add_marks(db, student_id, subject_code, subject_name, semester, score, max_marks=100, mid_term=None, end_term=None):
    # New Schema: One document per student in 'student_results'
    # entry structure
    new_entry = {
        "subject_code": subject_code,
        "subject_name": subject_name,
        "semester": semester,
        "total": score, # Assuming score is total
        "mid_term": mid_term,
        "end_term": end_term,
        "grade": _calculate_grade(score)
    }

    # 1. Try to update existing subject entry in the array
    result = db.student_results.update_one(
        {"student_id": student_id, "results.subject_code": subject_code},
        {"$set": {"results.$": new_entry}}
    )
    
    # 2. If not found (matched_count == 0), push to array
    if result.matched_count == 0:
        db.student_results.update_one(
            {"student_id": student_id},
            {"$push": {"results": new_entry}},
            upsert=True
        )
        
    return result

def get_marks_by_student(db, student_id):
    # Retrieve the results array from the single document
    doc = db.student_results.find_one({"student_id": student_id}, {"_id": 0, "results": 1})
    if doc and "results" in doc:
        return doc["results"]
    return []

def _calculate_grade(score):
    if score >= 90: return 'A+'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    if score >= 40: return 'E'
    return 'F'