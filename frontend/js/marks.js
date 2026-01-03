async function loadMarks(studentId) {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/marks/${studentId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();

    const container = document.getElementById('marksData');
    if (data.length === 0) {
        container.innerHTML = '<p>No marks found.</p>';
        return;
    }

    const html = `
        <div style="margin-bottom: 10px; text-align: right;">
            <button onclick="window.open('/api/marks/pdf/${studentId}', '_blank')" class="btn" style="background-color: #e17055; padding: 5px 15px; font-size: 0.9em;">
                <i class="fas fa-file-pdf"></i> Download Official Result
            </button>
        </div>
        <table class="styled-table" style="width:100%">
            <thead><tr><th>Subject</th><th>Score</th></tr></thead>
            <tbody>
            ${data.map(m => `<tr><td>${m.subject}</td><td>${m.score}</td></tr>`).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}