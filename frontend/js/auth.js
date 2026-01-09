document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  const res = await fetch(`${CONFIG.API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  const errorDiv = document.getElementById('loginErrorMessage');

  if (res.ok && data.token) {
    localStorage.setItem('token', data.token);
    window.location.href = 'dashboard.html';
  } else {
    // Show Error
    errorDiv.textContent = data.error || 'Invalid credentials or login failed';
    errorDiv.style.display = 'block';
  }
});