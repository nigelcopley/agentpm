/**
 * Toast Notification System for APM (Agent Project Manager) Configuration Portal
 *
 * Features:
 * - 4 toast types: success, error, warning, info
 * - Auto-dismiss after 5 seconds (configurable)
 * - Manual close button
 * - Stack multiple toasts with 20px spacing
 * - Fade in/out animations
 * - Bootstrap 5 color scheme integration
 * - HTMX integration (listens for X-Toast-* headers)
 *
 * Usage:
 *   showToast('Operation successful', 'success');
 *   showToast('Error occurred', 'error', 10000); // Custom duration
 *
 * @version 1.0.0
 * @author APM (Agent Project Manager) (WI-36 Configuration Portal)
 */

// Toast configuration
const TOAST_CONFIG = {
    defaultDuration: 5000,  // 5 seconds
    stackSpacing: 20,       // 20px vertical spacing between toasts
    animationDuration: 300, // Fade animation duration in ms
    maxToasts: 5            // Maximum simultaneous toasts
};

// Toast type configurations (Bootstrap color scheme)
const TOAST_TYPES = {
    success: {
        icon: 'bi-check-circle-fill',
        bgClass: 'bg-success',
        textClass: 'text-white',
        label: 'Success'
    },
    error: {
        icon: 'bi-x-circle-fill',
        bgClass: 'bg-danger',
        textClass: 'text-white',
        label: 'Error'
    },
    warning: {
        icon: 'bi-exclamation-triangle-fill',
        bgClass: 'bg-warning',
        textClass: 'text-dark',
        label: 'Warning'
    },
    info: {
        icon: 'bi-info-circle-fill',
        bgClass: 'bg-info',
        textClass: 'text-white',
        label: 'Info'
    }
};

/**
 * Show a toast notification
 *
 * @param {string} message - Toast message text
 * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Auto-dismiss duration in milliseconds (default: 5000)
 */
function showToast(message, type = 'info', duration = TOAST_CONFIG.defaultDuration) {
    // Validate toast type
    if (!TOAST_TYPES[type]) {
        console.error(`Invalid toast type: ${type}. Using 'info' instead.`);
        type = 'info';
    }

    const config = TOAST_TYPES[type];
    const container = document.getElementById('toast-container');

    if (!container) {
        console.error('Toast container not found. Ensure #toast-container exists in DOM.');
        return;
    }

    // Enforce max toasts limit
    const existingToasts = container.querySelectorAll('.toast');
    if (existingToasts.length >= TOAST_CONFIG.maxToasts) {
        // Remove oldest toast to make room
        const oldestToast = existingToasts[0];
        removeToast(oldestToast);
    }

    // Create toast element
    const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const toast = document.createElement('div');
    toast.className = `toast align-items-center ${config.bgClass} ${config.textClass} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.minWidth = '300px';
    toast.style.marginBottom = `${TOAST_CONFIG.stackSpacing}px`;

    // Toast HTML structure
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center">
                <i class="bi ${config.icon} me-2"></i>
                <span>${escapeHtml(message)}</span>
            </div>
            <button type="button" class="btn-close ${config.textClass === 'text-dark' ? '' : 'btn-close-white'} me-2 m-auto"
                    data-bs-dismiss="toast"
                    aria-label="Close"></button>
        </div>
    `;

    // Add to container
    container.appendChild(toast);

    // Initialize Bootstrap Toast with custom delay
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration,
        autohide: true
    });

    // Show toast
    bsToast.show();

    // Remove from DOM after hidden
    toast.addEventListener('hidden.bs.toast', () => {
        removeToast(toast);
    });

    return toastId;
}

/**
 * Remove a toast element from DOM
 *
 * @param {HTMLElement} toast - Toast element to remove
 */
function removeToast(toast) {
    if (toast && toast.parentNode) {
        // Fade out animation
        toast.style.opacity = '0';
        toast.style.transition = `opacity ${TOAST_CONFIG.animationDuration}ms ease-out`;

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, TOAST_CONFIG.animationDuration);
    }
}

/**
 * Escape HTML to prevent XSS attacks
 *
 * @param {string} text - Text to escape
 * @returns {string} Escaped text safe for HTML insertion
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show success toast (convenience method)
 *
 * @param {string} message - Success message
 * @param {number} duration - Optional duration
 */
function showSuccess(message, duration) {
    return showToast(message, 'success', duration);
}

/**
 * Show error toast (convenience method)
 *
 * @param {string} message - Error message
 * @param {number} duration - Optional duration
 */
function showError(message, duration) {
    return showToast(message, 'error', duration);
}

/**
 * Show warning toast (convenience method)
 *
 * @param {string} message - Warning message
 * @param {number} duration - Optional duration
 */
function showWarning(message, duration) {
    return showToast(message, 'warning', duration);
}

/**
 * Show info toast (convenience method)
 *
 * @param {string} message - Info message
 * @param {number} duration - Optional duration
 */
function showInfo(message, duration) {
    return showToast(message, 'info', duration);
}

// ========================================
// HTMX Integration
// ========================================

/**
 * Listen for HTMX responses and show toasts automatically
 *
 * Reads X-Toast-Message and X-Toast-Type headers from server responses
 * and triggers appropriate toast notifications.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Listen for HTMX afterSwap event (after content is swapped into DOM)
    document.body.addEventListener('htmx:afterSwap', function(event) {
        const xhr = event.detail.xhr;

        if (!xhr) return;

        // Check for toast headers
        const toastMessage = xhr.getResponseHeader('X-Toast-Message');
        const toastType = xhr.getResponseHeader('X-Toast-Type') || 'info';
        const toastDuration = xhr.getResponseHeader('X-Toast-Duration');

        if (toastMessage) {
            const duration = toastDuration ? parseInt(toastDuration) : TOAST_CONFIG.defaultDuration;
            showToast(toastMessage, toastType, duration);
        }
    });

    // Also listen for htmx:responseError for error handling
    document.body.addEventListener('htmx:responseError', function(event) {
        const xhr = event.detail.xhr;

        if (!xhr) return;

        // Check if server provided error toast headers
        const toastMessage = xhr.getResponseHeader('X-Toast-Message');
        if (toastMessage) {
            showError(toastMessage);
        } else {
            // Generic error message
            showError('An error occurred. Please try again.');
        }
    });

    // Listen for htmx:timeout
    document.body.addEventListener('htmx:timeout', function(event) {
        showError('Request timed out. Please check your connection.');
    });
});

// ========================================
// Flask Flash Message Integration
// ========================================

/**
 * Convert Flask flash messages to toasts on page load
 *
 * This function looks for flash messages in the DOM (typically rendered
 * by Flask's flash() function) and converts them to toast notifications.
 *
 * Expected HTML structure:
 *   <div class="flash-messages" data-messages='[{"message": "...", "category": "..."}]'></div>
 */
document.addEventListener('DOMContentLoaded', function() {
    const flashContainer = document.getElementById('flash-messages');

    if (!flashContainer) return;

    const flashData = flashContainer.getAttribute('data-messages');

    if (!flashData) return;

    try {
        const messages = JSON.parse(flashData);

        messages.forEach(function(flash) {
            // Map Flask categories to toast types
            const categoryMap = {
                'success': 'success',
                'error': 'error',
                'danger': 'error',
                'warning': 'warning',
                'info': 'info',
                'message': 'info'
            };

            const toastType = categoryMap[flash.category] || 'info';
            showToast(flash.message, toastType);
        });

        // Clear flash messages after displaying
        flashContainer.remove();
    } catch (e) {
        console.error('Failed to parse flash messages:', e);
    }
});

// ========================================
// Export for use in other scripts
// ========================================

// Make functions globally available
window.showToast = showToast;
window.showSuccess = showSuccess;
window.showError = showError;
window.showWarning = showWarning;
window.showInfo = showInfo;
