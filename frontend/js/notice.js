async function loadNotices(role) {
    const container = document.getElementById('notices');
    if (!container) return;
    const token = localStorage.getItem('token');

    try {
        const targetRole = role || 'student';
        const res = await fetch(`/api/notices/${targetRole}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const notices = await res.json();

        if (notices.length === 0) {
            container.innerHTML = '<div style="color:#666; font-style:italic;">No active notices.</div>';
            return;
        }

        container.innerHTML = notices.map(n => `
            <div style="background: #fff; padding: 15px; margin-bottom: 15px; border-left: 4px solid #6c5ce7; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-radius: 0 4px 4px 0;">
                <div style="display:flex; justify-content:space-between; margin-bottom: 8px;">
                    <h4 style="margin:0; color:#2d3436; font-size: 1.1em;">${n.title}</h4>
                    <span style="font-size:0.8em; color:#999;">${new Date(n.date).toLocaleDateString()}</span>
                </div>
                <p style="margin:0 0 10px 0; color:#555; font-size:0.95em; line-height: 1.5;">${n.content}</p>
                <div style="font-size:0.8em; color:#6c5ce7; font-weight: bold;">
                    <i class="fas fa-bullhorn"></i> Posted by ${n.posted_by}
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error(e);
        container.innerHTML = '<p style="color:red;">Error loading notices.</p>';
    }
}


