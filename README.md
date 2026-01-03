# Student Management System

A robust, role-based School Management System built with Python Flask and MongoDB.

## Features by Role

### 👨‍🎓 Student
- **Login**: Use Admission Number (e.g., `2024CS001`) or Email.
- **Dashboard**:
  - **Attendance**: View detailed stats per subject (Total, Present, Absent, %).
  - **Marks**: View semester marks and download **Official Result PDF**.
  - **Fees**: Check tuition, hostel, and library fee status.
  - **Schedule**: View your weekly class time table.
  - **Courses**: See the list of subjects for your current semester.

### 👩‍🏫 Teacher
- **Login**: Email & Password.
- **Dashboard**:
  - **My Classes**: View subjects you are teaching.
  - **Mark Attendance**: Record student attendance.
  - **Approve Students**: Verify and approve new student registrations.

### 👨‍💼 Admin
- **Login**: Email & Password.
- **Dashboard**:
  - **Manage Faculty**: View and filter faculty by branch.
  - **Manage Students**: View and search students by year/branch.
  - **Manage Subjects**: Add and map subjects to branches/years.
  - **Approvals**: Approve new teacher registrations.

## Technical Setup

### Prerequisites
- Python 3.x
- MongoDB (Running locally on default port 27017)

### Installation
1.  **Install Dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```
2.  **Seed Data** (Optional, for testing):
    - Run the provided seed script (e.g., `seed_v4.py`) to populate the DB with Users, Subjects, Attendance, etc.
3.  **Run Application**:
    ```bash
    python backend/app.py
    ```
4.  **Access**: Open `http://localhost:5000` in your browser.

## API Overview
- `/api/auth`: Login/Register.
- `/api/users`: specific user profile and approvals.
- `/api/attendance`: Fetch/Mark attendance.
- `/api/marks`: Fetch/Add marks, Generate PDF.
- `/api/courses`: Dynamic subject lists.
- `/api/fees`: Fee status.
- `/api/schedule`: Weekly timetables.