window.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'login.html';
    return;
  }

  // 1. Decode Token
  const payload = JSON.parse(atob(token.split('.')[1]));
  const userId = payload.user_id;
  const role = payload.role;

  // 2. Fetch Full User Details
  const res = await fetch(`${CONFIG.API_BASE}/user/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Session expired");
    logout();
    return;
  }

  const user = await res.json();

  // 3. Populate Profile View
  document.getElementById('profileName').textContent = user.name;
  document.getElementById('profileRole').textContent = user.role.toUpperCase();
  document.getElementById('profileEmail').textContent = user.email;
  document.getElementById('profileId').textContent = user._id;

  document.getElementById('profilePhone').textContent = user.phone || 'N/A';
  document.getElementById('profileDob').textContent = user.dob || 'N/A';
  document.getElementById('profileAddress').textContent = user.address || 'N/A';
  document.getElementById('profileAdmNo').textContent = user.admission_number || 'Not Generated';

  // 4. Role-Based Dashboard Logic
  // 4. Role-Based Dashboard Logic
  if (role === 'student') {
    document.getElementById('studentSection').style.display = 'block';
    document.querySelectorAll('.student-only').forEach(el => el.style.setProperty('display', 'flex', 'important'));
    document.querySelectorAll('.academic-only').forEach(el => el.style.setProperty('display', 'flex', 'important'));

    if (typeof loadAttendance === 'function') loadAttendance(userId);
    if (typeof loadMarks === 'function') loadMarks(userId);
    loadFees(userId);
    loadSchedule(userId);
    loadCourses(userId);
  }

  if (role === 'teacher') {
    document.getElementById('teacherSection').style.display = 'block';
    document.querySelectorAll('.academic-only').forEach(el => el.style.setProperty('display', 'flex', 'important'));

    // Teachers approve Students
    loadPendingUsers('student');
    loadCourses(userId); // Load Teacher Courses
  }

  if (role === 'admin') {
    // Show Admin Menu Links
    document.querySelectorAll('.admin-only').forEach(el => el.style.setProperty('display', 'flex', 'important'));
    // Admins approve Teachers
    loadPendingUsers('teacher');
    // Load Branch Data - Removed
    // loadAdminBranches();
  }

  // Load Notices (Everyone sees this)
  if (typeof loadNotices === 'function') loadNotices(role);
});

/* --- Approval System --- */
async function loadPendingUsers(roleToApprove) {
  const token = localStorage.getItem('token');
  const container = document.getElementById('approvalSection');
  const list = document.getElementById('pendingList');

  const res = await fetch(`/api/users/pending/${roleToApprove}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const users = await res.json();

  if (users.length > 0) {
    container.style.display = 'block';
    list.innerHTML = `
      <table style="width:100%; border-collapse: collapse;">
        <tr style="background:#fff5f5; text-align:left;">
            <th style="padding:10px;">Name</th>
            <th>Email</th>
            <th>Action</th>
        </tr>
        ${users.map(u => `
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:10px;">${u.name}</td>
            <td>${u.email}</td>
            <td>
              <button onclick="approveUser('${u._id}')" class="btn" style="padding:5px 15px; font-size:0.8em; background:#e17055;">
                Approve
              </button>
            </td>
          </tr>
        `).join('')}
      </table>
    `;
  }
}

async function approveUser(targetId) {
  const token = localStorage.getItem('token');
  if (!confirm("Confirm approval?")) return;

  const res = await fetch(`/api/users/approve/${targetId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (res.ok) {
    alert("User Approved!");
    location.reload();
  } else {
    alert("Error approving user");
  }
}



/* --- V3: Fees & Schedule --- */
async function loadFees(userId) {
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`/api/fees/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const container = document.getElementById('feeContainer');

    if (!res.ok) {
      container.innerHTML = '<p>No fee record found.</p>';
      return;
    }

    const fee = await res.json();

    const statusColor = fee.status === 'Paid' ? 'green' : (fee.status === 'Overdue' ? 'red' : 'orange');

    container.innerHTML = `
            <table class="styled-table" style="width:100%; max-width:600px;">
                <tr><th>Category</th><th>Amount (INR)</th></tr>
                <tr><td>Tuition Fee</td><td>₹${fee.tuition}</td></tr>
                <tr><td>Hostel Fee</td><td>₹${fee.hostel}</td></tr>
                <tr><td>Library Fee</td><td>₹${fee.library}</td></tr>
                <tr><td>Other Charges</td><td>₹${fee.other}</td></tr>
                <tr style="background:#f8f9fa; font-weight:bold;">
                    <td>TOTAL</td><td>₹${fee.total}</td>
                </tr>
                <tr>
                    <td>Status</td>
                    <td style="color:${statusColor}; font-weight:bold;">${fee.status.toUpperCase()}</td>
                </tr>
                <tr>
                    <td>Due Date</td>
                    <td>${fee.due_date || 'N/A'}</td>
                </tr>
            </table>
            <div style="margin-top:15px;">
                ${fee.status === 'Paid' ? `
                    <button onclick="window.open('/api/fees/receipt/${userId}', '_blank')" class="btn" style="background:#0984e3;">
                        <i class="fas fa-file-invoice"></i> Download Receipt
                    </button>
                ` : ''}
            </div>
        `;
  } catch (e) {
    console.error(e);
  }
}

async function loadSchedule(userId) {
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`/api/schedule/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const container = document.getElementById('scheduleContainer');

    if (!res.ok) {
      container.innerHTML = '<p>Schedule not available yet.</p>';
      return;
    }

    const data = await res.json();
    if (!data.days || Object.keys(data.days).length === 0) {
      container.innerHTML = '<p>No classes scheduled.</p>';
      return;
    }

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    let html = '<div style="display:flex; gap:15px; min-width: 800px;">';

    days.forEach(day => {
      const classes = data.days[day] || [];
      html += `
                <div style="flex:1; background:#fff; border:1px solid #eee; border-radius:5px; overflow:hidden;">
                    <div style="background:#6c5ce7; color:white; padding:10px; text-align:center; font-weight:bold;">${day}</div>
                    <div style="padding:10px; display:flex; flex-direction:column; gap:10px;">
            `;

      if (classes.length === 0) {
        html += `<div style="text-align:center; color:#ccc;">No Classes</div>`;
      } else {
        classes.forEach(c => {
          const bgColor = c.type === 'break' ? '#ffeb3b40' : '#e3f2fd';
          // User requested removal of emojis
          html += `
                        <div style="background:${bgColor}; padding:8px; border-radius:4px; font-size:0.9em; border-left: 3px solid #ccc;">
                            <div style="font-weight:bold; font-size:0.85em; color:#555;">${c.time}</div>
                            <div style="margin-top:2px;">${c.subject}</div>
                             <div style="font-size:0.8em; color:#666; margin-top:3px;">
                                <i class="fas fa-user-tie"></i> ${c.teacher || 'Faculty'}
                            </div>
                        </div>
                    `;
        });
      }
      html += `</div></div>`;
    });

    html += '</div>';
    container.innerHTML = html;

  } catch (e) {
    console.error(e);
  }
}
/* --- V4: Detailed Attendance & Dynamic Courses --- */
async function loadAttendance(userId) {
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`/api/attendance/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const container = document.getElementById('attendanceData');
    // If not, we might need to update dashboard.html too. Assuming 'attendance-section' exists
    // Wait, dashboard.html structure needs checking. Let's assume there is a container. 
    // If not, I'll update dashboard.html next.

    if (!container) return; // Safety

    if (!res.ok) {
      container.innerHTML = '<p>Attendance data unavailable.</p>';
      return;
    }

    const data = await res.json();
    const details = data.details || [];

    if (details.length === 0) {
      container.innerHTML = `<p>No attendance records found.</p>`;
      return;
    }

    let html = `
            <div style="margin-bottom:15px; font-size:1.1em;">
                <strong>Overall Attendance:</strong> 
                <span style="color:${data.overall_percentage >= 75 ? 'green' : 'red'}; font-weight:bold;">
                    ${data.overall_percentage}%
                </span>
            </div>
            <table class="styled-table" style="width:100%">
                <thead>
                    <tr>
                        <th>Subject</th>
                        <th>Total Classes</th>
                        <th>Present</th>
                        <th>Absent</th>
                        <th>%</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

    details.forEach(row => {
      const color = row.percentage >= 75 ? '#2ecc71' : '#e74c3c';
      html += `
                <tr>
                    <td>${row.subject}</td>
                    <td>${row.total_classes}</td>
                    <td>${row.present}</td>
                    <td>${row.absent}</td>
                    <td style="font-weight:bold;">${row.percentage}%</td>
                    <td>
                        <div style="width:100px; height:8px; background:#eee; border-radius:4px; overflow:hidden;">
                            <div style="width:${row.percentage}%; height:100%; background:${color};"></div>
                        </div>
                    </td>
                </tr>
            `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;

  } catch (e) {
    console.error("Attendance Error", e);
  }
}

async function loadCourses(userId) {
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`/api/courses/${userId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const container = document.getElementById('coursesContainer'); // Need to ensure this ID exists

    if (!container) return;

    if (!res.ok) {
      container.innerHTML = '<p>Courses unavailable.</p>';
      return;
    }

    const data = await res.json();

    if (data.role === 'admin') {
      container.innerHTML = `<div class="alert alert-info">${data.message}</div>`;
      return;
    }

    const courses = data.courses || [];
    if (courses.length === 0) {
      container.innerHTML = '<p>No courses assigned yet.</p>';
      return;
    }

    let html = '<div class="cards-grid">';
    courses.forEach(c => {
      const labBadge = c.has_lab ? '<span style="background:#e84393; color:white; padding:2px 6px; border-radius:4px; font-size:0.7em; margin-left:5px;">LAB</span>' : '';
      html += `
                <div class="card">
                    <h3>${c.name} ${labBadge}</h3>
                    <p><strong>Code:</strong> ${c.code}</p>
                    <p><strong>Branch:</strong> ${c.branch_code} | <strong>Semester:</strong> ${c.semester}</p>
                </div>
             `;
    });
    html += '</div>';
    container.innerHTML = html;

  } catch (e) {
    console.error("Courses Error", e);
  }
}