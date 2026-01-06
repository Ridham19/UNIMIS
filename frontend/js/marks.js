async function loadMarks(userId) {
    const token = localStorage.getItem('token');
    try {
        const res = await fetch(`/api/marks/${userId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const container = document.getElementById('marksData');
        const semSelect = document.getElementById('pastSemSelect');

        if (!res.ok) {
            container.innerHTML = '<p>Marks unavailable.</p>';
            return;
        }

        const data = await res.json();

        // Filter to show only the latest semester available in data
        // 1. Find max semester
        let maxSem = 0;
        data.forEach(m => {
            if (m.semester && m.semester > maxSem) maxSem = m.semester;
        });

        // 2. Filter data
        const currentSemMarks = data.filter(m => m.semester === maxSem);

        if (currentSemMarks.length === 0) {
            container.innerHTML = '<p>No marks uploaded yet.</p>';
        } else {
            let html = `<h4 style="margin:0 0 10px 0; font-size:0.9em; color:#666;">Semester ${maxSem} Results</h4>
                        <ul style="list-style:none; padding:0;">`;
            currentSemMarks.forEach(m => {
                html += `
                    <li style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #f1f1f1;">
                        <span>${m.subject_name}</span>
                        <strong>${m.total}/100</strong>
                    </li>
                `;
            });
            html += '</ul>';
            container.innerHTML = html;
        }

        // Load Past Semesters for Dropdown
        const histRes = await fetch(`/api/results/history/${userId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (histRes.ok) {
            const history = await histRes.json();
            // Clear valid options
            semSelect.innerHTML = '<option value="">Select Semester</option>';
            history.semesters.forEach(sem => {
                const opt = document.createElement('option');
                opt.value = sem;
                opt.innerText = `Semester ${sem}`;
                semSelect.appendChild(opt);
            });
        }

    } catch (e) {
        console.error("Marks Error", e);
    }
}

function downloadMarksheet() {
    const sem = document.getElementById('pastSemSelect').value;
    if (!sem) return alert("Select a semester first");

    // We need userId. We can get it from token since this is client side
    const token = localStorage.getItem('token');
    const payload = JSON.parse(atob(token.split('.')[1]));
    const userId = payload.user_id;

    window.open(`/api/results/download/${userId}/${sem}`, '_blank');
}