// HTMX Integration with Alpine.js
// Professional patterns for HTMX + Alpine.js integration

document.addEventListener('DOMContentLoaded', function() {
    // HTMX event listeners for Alpine.js integration
    
    // Before request - show loading states
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        const element = evt.target;
        
        // Add loading class to the element
        element.classList.add('htmx-loading');
        
        // Show loading state in Alpine components
        if (element._x_dataStack) {
            const alpineData = element._x_dataStack[0];
            if (alpineData && typeof alpineData.setLoading === 'function') {
                alpineData.setLoading(true);
            }
        }
        
        // Global loading state
        if (window.Alpine && window.Alpine.store) {
            window.Alpine.store('loading').start('htmx-request');
        }
    });
    
    // After request - hide loading states
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const element = evt.target;
        
        // Remove loading class
        element.classList.remove('htmx-loading');
        
        // Hide loading state in Alpine components
        if (element._x_dataStack) {
            const alpineData = element._x_dataStack[0];
            if (alpineData && typeof alpineData.setLoading === 'function') {
                alpineData.setLoading(false);
            }
        }
        
        // Global loading state
        if (window.Alpine && window.Alpine.store) {
            window.Alpine.store('loading').stop('htmx-request');
        }
    });
    
    // Handle HTMX errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        console.error('HTMX Error:', evt.detail);
        
        // Show error notification
        if (window.showToast) {
            window.showToast('Request failed. Please try again.', 'error');
        }
    });
    
    // Handle successful responses
    document.body.addEventListener('htmx:afterSettle', function(evt) {
        // Re-initialize Alpine.js for new content
        if (window.Alpine) {
            window.Alpine.initTree(evt.target);
        }
    });
    
    // Handle validation errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        if (evt.detail.xhr.status === 422) {
            // Validation error
            try {
                const response = JSON.parse(evt.detail.xhr.responseText);
                if (response.errors) {
                    // Handle form validation errors
                    Object.keys(response.errors).forEach(field => {
                        const errorElement = document.querySelector(`[name="${field}"]`);
                        if (errorElement && errorElement._x_dataStack) {
                            const alpineData = errorElement._x_dataStack[0];
                            if (alpineData && typeof alpineData.setError === 'function') {
                                alpineData.setError(field, response.errors[field]);
                            }
                        }
                    });
                }
            } catch (e) {
                console.error('Error parsing validation response:', e);
            }
        }
    });
});

// HTMX indicators CSS
const htmxStyles = `
.htmx-loading {
    opacity: 0.6;
    pointer-events: none;
}

.htmx-loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #3498db;
    border-radius: 50%;
    animation: htmx-spin 1s linear infinite;
}

@keyframes htmx-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.htmx-indicator {
    display: none;
}

.htmx-request .htmx-indicator {
    display: inline;
}

.htmx-request.htmx-indicator {
    display: inline;
}
`;

// Inject HTMX styles
const styleSheet = document.createElement('style');
styleSheet.textContent = htmxStyles;
document.head.appendChild(styleSheet);
