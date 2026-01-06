/* UI Effects */

document.addEventListener('DOMContentLoaded', () => {
    initSpotlightCards();
    initFloatingLabels();
});

function initSpotlightCards() {
    const cards = document.querySelectorAll('.glass-card, .section-card');

    cards.forEach(card => {
        // Ensure overlay exists
        if (!card.querySelector('.spotlight-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'spotlight-overlay';
            card.style.position = 'relative'; // Mandatory
            card.appendChild(overlay);
        }

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

function initFloatingLabels() {
    // Placeholder for future float label logic if needed, 
    // currently focusing on card effects as per request.
}
