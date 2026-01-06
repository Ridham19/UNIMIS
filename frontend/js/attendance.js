// Global state to track marked status
let currentClassList = [];
let attendanceState = {}; // { studentId: 'Present' | 'Absent' }
let subjectCodeNameMap = {}; // { code: name }

document.addEventListener('DOMContentLoaded', () => {
    // We bind the event listener if the element exists, or waits for it to be visible
    // Since this script is loaded at the end, elements should be ready.
    // If we are on the dashboard and elements exist:
    if (document.getElementById('teachSubjectSelect')) {
        loadTeacherSubjects();

        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('teachDate').value = today;
    }
});

async function loadTeacherSubjects() {
    const token = localStorage.getItem('token');
    const select = document.getElementById('teachSubjectSelect');

    let branchCode = '';
    try {
        if (token) {
            const payload = JSON.parse(atob(token.split('.')[1]));
            branchCode = payload.branch_code || '';
        }
    } catch (e) {
        console.error("Error decoding token for branch", e);
    }

    try {
        const url = branchCode
            ? `/api/attendance/teacher/subjects?branch_code=${branchCode}`
            : '/api/attendance/teacher/subjects';

        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const subjects = await res.json();

        select.innerHTML = '<option value="">-- Select Subject --</option>';
        subjectCodeNameMap = {}; // Reset map

        subjects.forEach(s => {
            // Store mapping for submission
            subjectCodeNameMap[s.code] = s.name;
            select.innerHTML += `<option value="${s.code}">${s.name} (Sem ${s.semester})</option>`;
        });
    } catch (e) {
        console.error("Error loading subjects", e);
    }
}

async function loadClassList() {
    const subjectCode = document.getElementById('teachSubjectSelect').value;
    const date = document.getElementById('teachDate').value;

    if (!subjectCode || !date) return alert("Please select a subject and date");

    const token = localStorage.getItem('token');
    const container = document.getElementById('attendanceListContainer');
    const tbody = document.getElementById('attendanceTableBody');

    // Show loading state could be nice here
    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:20px;">Loading class list...</td></tr>';
    container.style.display = 'block';

    try {
        const res = await fetch(`/api/attendance/class-list/${subjectCode}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.error || "Error loading class list");
            tbody.innerHTML = '';
            return;
        }

        const data = await res.json();
        currentClassList = data.students; // { _id, name, admission_number }
        attendanceState = {}; // Reset state

        if (currentClassList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:20px;">No students found for this subject/semester.</td></tr>';
            return;
        }

        const subjectName = subjectCodeNameMap[subjectCode] || data.subject;
        document.getElementById('classHeader').innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>${subjectName} <span style="font-weight:normal; font-size:0.8em; color:#666;">(${data.branch} - Sem ${data.semester})</span></span>
                <div style="font-size:0.6em;">
                    <button onclick="markAll('Present')" class="btn" style="padding:4px 10px; height:auto; background:#00b894; font-size:12px;">All Present</button>
                    <button onclick="markAll('Absent')" class="btn" style="padding:4px 10px; height:auto; background:#ff7675; font-size:12px;">All Absent</button>
                </div>
            </div>
        `;

        tbody.innerHTML = ''; // Clear loading/old data

        currentClassList.forEach(student => {
            // Default to Present
            attendanceState[student._id] = 'Present';
            const rowId = `row-${student._id}`;

            const tr = document.createElement('tr');
            tr.id = rowId;

            // Toggle Switch UI
            // We use a simple segment control look with two buttons but styled together
            const toggleHtml = `
                <div class="attendance-toggle-group">
                    <div id="tog-p-${student._id}" 
                         onclick="toggleStatus('${student._id}', 'Present')" 
                         class="att-toggle active">P</div>
                    <div id="tog-a-${student._id}" 
                         onclick="toggleStatus('${student._id}', 'Absent')" 
                         class="att-toggle">A</div>
                </div>
            `;

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:bold; color:#6c5ce7;">${student.admission_number || 'N/A'}</td>
                <td style="font-weight:500;">${student.name}</td>
                <td style="text-align:center; vertical-align:middle;">
                    ${toggleHtml}
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Ensure styles are injected
        injectAttendanceStyles();

    } catch (e) {
        console.error("Critical Error loading class list:", e);
        alert("An error occurred while loading the class list. Please check the console for details.");
    }
}

function injectAttendanceStyles() {
    if (document.getElementById('att-styles')) return;
    const style = document.createElement('style');
    style.id = 'att-styles';
    style.innerHTML = `
        .attendance-toggle-group {
            display: inline-flex;
            background: #dfe6e9;
            border-radius: 20px;
            padding: 3px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
        }
        .att-toggle {
            padding: 5px 15px;
            border-radius: 18px;
            cursor: pointer;
            font-weight: bold;
            color: #636e72;
            transition: all 0.2s ease;
            user-select: none;
            min-width: 40px;
        }
        .att-toggle:hover {
            color: #2d3436;
        }
        .att-toggle.active {
            background: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* Specific Colors for Active State */
        #attendanceTableBody .att-toggle.active[id^="tog-p"] {
            color: #00b894; /* Green for Present */
        }
        #attendanceTableBody .att-toggle.active[id^="tog-a"] {
            color: #ff7675; /* Red for Absent */
        }
    `;
    document.head.appendChild(style);
}

function toggleStatus(studentId, status) {
    attendanceState[studentId] = status;

    // Update UI
    const pBtn = document.getElementById(`tog-p-${studentId}`);
    const aBtn = document.getElementById(`tog-a-${studentId}`);

    if (status === 'Present') {
        pBtn.classList.add('active');
        aBtn.classList.remove('active');
    } else {
        pBtn.classList.remove('active');
        aBtn.classList.add('active');
    }
}

function markAll(status) {
    currentClassList.forEach(s => {
        toggleStatus(s._id, status);
    });
}

async function submitBulkAttendance() {
    const subjectCode = document.getElementById('teachSubjectSelect').value;
    const date = document.getElementById('teachDate').value;
    // Use the robust map, fallback to text manipulation only if map fails (unlikely)
    const subjectName = subjectCodeNameMap[subjectCode] ||
        document.getElementById('teachSubjectSelect').options[document.getElementById('teachSubjectSelect').selectedIndex].text.split('(')[0].trim();

    if (!subjectCode || !date) return alert("Missing Subject or Date");

    const attendanceList = currentClassList.map(s => ({
        student_id: s._id,
        date: date,
        subject: subjectName,
        status: attendanceState[s._id]
    }));

    if (!confirm(`Submit attendance for ${attendanceList.length} students?\nSubject: ${subjectName}\nDate: ${date}`)) return;

    const token = localStorage.getItem('token');
    try {
        const res = await fetch('/api/attendance/bulk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ attendance_list: attendanceList })
        });

        if (res.ok) {
            alert("Attendance Saved Successfully!");
            // Reset or hide
            document.getElementById('attendanceListContainer').style.display = 'none';
            document.getElementById('teachSubjectSelect').value = "";
        } else {
            const d = await res.json();
            alert("Error saving: " + (d.message || d.error));
        }
    } catch (e) {
        console.error(e);
        alert("Error submitting");
    }
}