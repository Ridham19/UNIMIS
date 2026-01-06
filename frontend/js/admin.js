// Integrated Admin Panel Logic

document.addEventListener('DOMContentLoaded', () => {
    // We only load initial data if we are already in admin view or just to pre-load
    // But better to expose a function to init when view is switched.
    // However, for simplicity, let's just add listeners if elements exist.

    if (document.getElementById('faculty-branch-select')) {
        loadDropdowns();
        document.getElementById('faculty-branch-select').addEventListener('change', loadFaculty);
        document.getElementById('student-branch-select').addEventListener('change', loadStudents);
        document.getElementById('student-semester-select').addEventListener('change', loadStudents);

        loadFaculty();
    }
});

function showAdminSection(section) {
    // Hide all sub-views
    document.querySelectorAll('.admin-sub-view').forEach(el => el.style.display = 'none');
    // Show target
    document.getElementById(`${section}-section`).style.display = 'block';

    if (section === 'student') loadStudents();
    else if (section === 'subjects') loadSubjects();
    else if (section === 'notices') { /* Do nothing specific, just show form */ }
    else loadFaculty();
}

async function fetch_with_auth(url) {
    const token = localStorage.getItem('token');
    const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
}

async function loadDropdowns() {
    try {
        const data = await fetch_with_auth('/api/admin/stats');
        const branches = data.branches;
        // const years = data.years; // Legacy

        // Faculty Branch Select
        const fSelect = document.getElementById('faculty-branch-select');
        fSelect.innerHTML = '<option value="">All Branches</option>';
        branches.forEach(b => {
            const opt = document.createElement('option');
            opt.value = b.code;
            opt.textContent = `${b.name} (${b.code})`;
            fSelect.appendChild(opt);
        });

        // Student Branch Select
        const sSelect = document.getElementById('student-branch-select');
        sSelect.innerHTML = '<option value="">All Branches</option>';
        branches.forEach(b => {
            const opt = document.createElement('option');
            opt.value = b.code;
            opt.textContent = `${b.name} (${b.code})`;
            sSelect.appendChild(opt);
        });

        // Student Semester Select (1-8)
        const semSelect = document.getElementById('student-semester-select');
        semSelect.innerHTML = '<option value="">All Semesters</option>';
        for (let i = 1; i <= 8; i++) {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = `Semester ${i}`;
            semSelect.appendChild(opt);
        }

    } catch (err) {
        console.error("Error loading stats", err);
    }
}

async function loadFaculty() {
    const branch = document.getElementById('faculty-branch-select').value;
    let url = '/api/admin/faculty-by-branch';
    if (branch) url += `?branch=${branch}`;

    const faculty = await fetch_with_auth(url);
    renderAdminTable('faculty-results', faculty, ['name', 'email', 'branch_code', 'phone']);
}

async function loadStudents() {
    const branch = document.getElementById('student-branch-select').value;
    const semester = document.getElementById('student-semester-select').value;

    let url = '/api/admin/students-by-year?';
    if (branch) url += `branch=${branch}&`;
    if (semester) url += `semester=${semester}`; // Renamed param to match intent

    const students = await fetch_with_auth(url);
    // Add Views/Action logic
    renderAdminTable('student-results', students, ['name', 'email', 'admission_number', 'branch_code', 'current_semester'], (item) => {
        return `<button class="btn" style="padding:5px 10px; font-size:0.8em;" onclick="viewStudent('${item._id}')">View/Edit</button>`;
    });
}

/* --- Subjects Management --- */
async function loadSubjects() {
    const branch = document.getElementById('subject-filter-branch').value;
    let url = '/api/subjects';
    if (branch && branch !== 'All') url += `?branch=${branch}`;

    const subjects = await fetch_with_auth(url);
    // Changed year to semester in table display
    renderAdminTable('subjects-list', subjects, ['name', 'code', 'branch_code', 'semester']);
}

async function addSubject() {
    const name = document.getElementById('subName').value;
    const code = document.getElementById('subCode').value;
    const branch_code = document.getElementById('subBranch').value;
    const semester = document.getElementById('subSemester').value;

    if (!name || !code) return alert("Fill all fields");

    const token = localStorage.getItem('token');
    const res = await fetch('/api/subjects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ name, code, branch_code, semester })
    });

    if (res.ok) {
        alert("Subject Added");
        document.getElementById('subName').value = '';
        document.getElementById('subCode').value = '';
        loadSubjects();
    } else {
        const d = await res.json();
        alert(d.error || "Error adding subject");
    }
}

function renderAdminTable(containerId, data, columns, actionCallback = null) {
    const container = document.getElementById(containerId);
    if (!data || data.length === 0) {
        container.innerHTML = '<p>No records found.</p>';
        return;
    }

    let html = `<table class="styled-table" style="width:100%"><thead><tr>`;
    columns.forEach(col => {
        html += `<th>${col.replace('_', ' ').toUpperCase()}</th>`;
    });
    if (actionCallback) html += `<th>ACTION</th>`;
    html += `</tr></thead><tbody>`;

    data.forEach(item => {
        html += `<tr>`;
        columns.forEach(col => {
            html += `<td>${item[col] || '-'}</td>`;
        });
        if (actionCallback) {
            html += `<td>${actionCallback(item)}</td>`;
        }
        html += `</tr>`;
    });
    html += `</tbody></table>`;

    container.innerHTML = html;
}

let currentEditingStudentId = null;

async function viewStudent(studentId) {
    currentEditingStudentId = studentId;
    const token = localStorage.getItem('token');

    // Fetch user details + fees
    try {
        const [userRes, feeRes] = await Promise.all([
            fetch(`/api/user/${studentId}`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`/api/fees/${studentId}`, { headers: { 'Authorization': `Bearer ${token}` } })
        ]);

        const user = await userRes.json();
        const fee = await feeRes.json();

        // Populate Modal
        document.getElementById('modalStudentName').textContent = user.name;
        document.getElementById('modalFeeStatus').textContent = fee.error ? "No Record" : fee.status;

        // Content
        document.getElementById('modalContent').innerHTML = `
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>Admission No:</strong> ${user.admission_number}</p>
            <p><strong>Branch/Semester:</strong> ${user.branch_code} - Sem ${user.current_semester || '?'}</p>
            <hr>
            <p><strong>Fees Total:</strong> ${fee.total || 0} INR</p>
        `;

        if (!fee.error) {
            document.getElementById('newFeeStatus').value = fee.status || 'Pending';
        }

        document.getElementById('studentModal').style.display = 'block';

    } catch (e) {
        alert("Error fetching details");
        console.error(e);
    }
}

async function updateFeeStatus() {
    if (!currentEditingStudentId) return;
    const status = document.getElementById('newFeeStatus').value;
    const token = localStorage.getItem('token');

    const res = await fetch(`/api/fees/${currentEditingStudentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
    });

    if (res.ok) {
        alert("Status Updated");
        viewStudent(currentEditingStudentId); // Refresh modal
    } else {
        alert("Update Failed");
    }
}

async function postNotice() {
    const title = document.getElementById('noticeTitle').value;
    const content = document.getElementById('noticeContent').value;
    const targets = Array.from(document.querySelectorAll('.notice-target:checked')).map(el => el.value);

    if (!title || !content || targets.length === 0) {
        return alert("Please fill all fields and select at least one target group.");
    }

    const token = localStorage.getItem('token');
    const res = await fetch('/api/notices', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            title,
            content,
            visible_to: targets
        })
    });

    if (res.ok) {
        alert("Notice Posted Successfully!");
        document.getElementById('noticeTitle').value = '';
        document.getElementById('noticeContent').value = '';
        // Optionally switch view or reload notices if visible
    } else {
        alert("Failed to post notice.");
    }
}
