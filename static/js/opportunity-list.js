/**
 * Opportunity List Filter
 * Provides real-time search filtering for opportunity cards
 */

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('opportunity-list-container');
    if (!container) return;

    // Add real-time search to existing search input
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.opportunity-card');

            cards.forEach(card => {
                const col = card.closest('.col-md-6');
                if (!col) return;

                const title = card.querySelector('.card-title')?.textContent?.toLowerCase() || '';
                const description = card.querySelector('.card-text')?.textContent?.toLowerCase() || '';
                const matches = title.includes(searchTerm) || description.includes(searchTerm);
                col.style.display = matches ? '' : 'none';
            });
        });
    }
});