window.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = 'login.html';
    return;
  }

  // Decode JWT to get user ID and role
  const payload = JSON.parse(atob(token.split('.')[1]));
  const userId = payload.user_id;
  const role = payload.role;

  // Fetch user info
  const res = await fetch(`/api/user/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const user = await res.json();

  // Display user info
  const userInfoDiv = document.getElementById('userInfo');
  userInfoDiv.innerHTML = `<p>Welcome, ${user.name} (${role})</p>`;

  // Show relevant sections
  if (role === 'student') {
    document.getElementById('studentSection').style.display = 'block';
  }
  if (role === 'teacher') {
    document.getElementById('teacherSection').style.display = 'block';
  }

  // Always show notices
  document.getElementById('noticeSection').style.display = 'block';
});