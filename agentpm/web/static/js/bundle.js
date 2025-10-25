// APM (Agent Project Manager) JavaScript Bundle
// This file replaces CDN dependencies with local functionality

// Phase content toggle functionality - make it globally accessible
window.togglePhaseContent = function(phaseValue) {
    const content = document.getElementById(`content-${phaseValue}`);
    const chevron = document.getElementById(`chevron-${phaseValue}`);
    
    if (content && chevron) {
        if (content.classList.contains('hidden')) {
            content.classList.remove('hidden');
            chevron.classList.remove('bi-chevron-down');
            chevron.classList.add('bi-chevron-up');
        } else {
            content.classList.add('hidden');
            chevron.classList.remove('bi-chevron-up');
            chevron.classList.add('bi-chevron-down');
        }
    }
};

// Toast notification system (simplified)
window.showToast = function(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    }`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
};

// Alpine.js component registration helper
window.registerAlpineComponent = function(name, component) {
    if (window.Alpine) {
        window.Alpine.data(name, component);
    } else {
        document.addEventListener('alpine:init', () => {
            window.Alpine.data(name, component);
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('APM (Agent Project Manager) JavaScript bundle loaded');
    
    // Initialize any global components here
    if (typeof initializeComponents === 'function') {
        initializeComponents();
    }
});
