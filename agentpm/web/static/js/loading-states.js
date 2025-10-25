/**
 * Loading States Management
 * Handles loading indicators for forms, buttons, and AJAX requests
 */

// Alpine.js global store for loading states
document.addEventListener('alpine:init', () => {
    Alpine.store('loading', {
        global: false,
        forms: {},

        // Set global loading state
        setGlobal(state) {
            this.global = state;
        },

        // Set form-specific loading state
        setForm(formId, state) {
            this.forms[formId] = state;
        },

        // Check if form is loading
        isFormLoading(formId) {
            return this.forms[formId] || false;
        }
    });
});

/**
 * Form Submission Handler with Loading State
 * Usage:
 *   <form x-data="formHandler" @submit.prevent="submitForm">
 */
const formHandler = {
    loading: false,
    success: false,
    error: null,

    async submitForm(event) {
        const form = event.target;
        this.loading = true;
        this.error = null;
        this.success = false;

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.success = true;

            // Show success toast
            if (window.AIPM && window.AIPM.utils) {
                window.AIPM.utils.showToast(data.message || 'Success!', 'success');
            }

            // Redirect if specified
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            }

        } catch (error) {
            console.error('Form submission error:', error);
            this.error = error.message;

            // Show error toast
            if (window.AIPM && window.AIPM.utils) {
                window.AIPM.utils.showToast(this.error, 'error');
            }
        } finally {
            this.loading = false;
        }
    }
};

/**
 * Button Loading State Handler
 * Usage:
 *   <button x-data="buttonHandler" @click="handleClick">
 */
const buttonHandler = {
    loading: false,

    async handleClick(callback) {
        this.loading = true;

        try {
            await callback();
        } catch (error) {
            console.error('Button action error:', error);

            if (window.AIPM && window.AIPM.utils) {
                window.AIPM.utils.showToast(error.message, 'error');
            }
        } finally {
            this.loading = false;
        }
    }
};

/**
 * HTMX Event Listeners for Global Loading State
 */
document.addEventListener('DOMContentLoaded', () => {
    // HTMX loading indicators
    document.body.addEventListener('htmx:beforeRequest', (event) => {
        // Check if request is from a form
        const form = event.detail.elt.closest('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');

                // Add spinner if not present
                if (!submitBtn.querySelector('.spinner')) {
                    const spinner = document.createElement('span');
                    spinner.className = 'spinner inline-block animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent mr-2';
                    submitBtn.prepend(spinner);
                }
            }
        }
    });

    document.body.addEventListener('htmx:afterRequest', (event) => {
        // Re-enable form submit button
        const form = event.detail.elt.closest('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');

                // Remove spinner
                const spinner = submitBtn.querySelector('.spinner');
                if (spinner) {
                    spinner.remove();
                }
            }
        }
    });

    document.body.addEventListener('htmx:responseError', (event) => {
        console.error('HTMX request error:', event.detail);

        if (window.AIPM && window.AIPM.utils) {
            window.AIPM.utils.showToast('Request failed. Please try again.', 'error');
        }
    });
});

/**
 * Utility Functions
 */
const LoadingStates = {
    /**
     * Show loading spinner on element
     */
    showSpinner(element) {
        if (!element) return;

        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner flex items-center justify-center p-4';
        spinner.innerHTML = `
            <div class="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div>
        `;

        element.innerHTML = '';
        element.appendChild(spinner);
    },

    /**
     * Show loading skeleton on element
     */
    showSkeleton(element, type = 'card') {
        if (!element) return;

        let skeletonHTML = '';

        switch (type) {
            case 'card':
                skeletonHTML = `
                    <div class="card animate-pulse">
                        <div class="skeleton h-6 w-3/4 mb-4"></div>
                        <div class="skeleton h-4 w-full mb-2"></div>
                        <div class="skeleton h-4 w-5/6"></div>
                    </div>
                `;
                break;
            case 'list':
                skeletonHTML = `
                    <div class="space-y-4 animate-pulse">
                        ${Array(5).fill('').map(() => `
                            <div class="card">
                                <div class="skeleton h-5 w-2/3 mb-2"></div>
                                <div class="skeleton h-4 w-1/2"></div>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
            case 'table':
                skeletonHTML = `
                    <div class="animate-pulse">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th><div class="skeleton h-4 w-24"></div></th>
                                    <th><div class="skeleton h-4 w-32"></div></th>
                                    <th><div class="skeleton h-4 w-20"></div></th>
                                </tr>
                            </thead>
                            <tbody>
                                ${Array(5).fill('').map(() => `
                                    <tr>
                                        <td><div class="skeleton h-4 w-20"></div></td>
                                        <td><div class="skeleton h-4 w-40"></div></td>
                                        <td><div class="skeleton h-4 w-16"></div></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
                break;
        }

        element.innerHTML = skeletonHTML;
    },

    /**
     * Disable button with loading state
     */
    disableButton(button, loadingText = 'Loading...') {
        if (!button) return;

        button.disabled = true;
        button.dataset.originalText = button.innerHTML;

        button.innerHTML = `
            <span class="flex items-center space-x-2">
                <span class="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent"></span>
                <span>${loadingText}</span>
            </span>
        `;
    },

    /**
     * Enable button and restore original text
     */
    enableButton(button) {
        if (!button) return;

        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { formHandler, buttonHandler, LoadingStates };
}

// Global access
window.LoadingStates = LoadingStates;
window.formHandler = formHandler;
window.buttonHandler = buttonHandler;
