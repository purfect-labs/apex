// APEX Tab Functionality

function initializeTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            const container = this.closest('.tab-container');
            
            // Remove active class from all buttons and contents in this container
            container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            const content = container.querySelector(`[data-tab-content="${tabName}"]`);
            if (content) content.classList.add('active');
        });
    });
}

// Export for use by other modules
window.APEX.initializeTabs = initializeTabs;