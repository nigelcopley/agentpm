// Toast notification system
export function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white transition-all duration-300 transform translate-x-full ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
    }`;
    
    // Create toast content
    const content = document.createElement('div');
    content.className = 'flex items-center space-x-2';
    
    // Add icon
    const icon = document.createElement('i');
    icon.className = `bi ${
        type === 'success' ? 'bi-check-circle-fill' :
        type === 'error' ? 'bi-x-circle-fill' :
        type === 'warning' ? 'bi-exclamation-triangle-fill' :
        'bi-info-circle-fill'
    }`;
    
    // Add message
    const messageEl = document.createElement('span');
    messageEl.textContent = message;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'ml-2 text-white hover:text-gray-200';
    closeBtn.innerHTML = '<i class="bi bi-x"></i>';
    closeBtn.onclick = () => removeToast(toast);
    
    content.appendChild(icon);
    content.appendChild(messageEl);
    content.appendChild(closeBtn);
    toast.appendChild(content);
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
        toast.classList.add('translate-x-0');
    }, 10);
    
    // Auto remove
    setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
    toast.classList.add('translate-x-full');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Make it globally available
window.showToast = showToast;
