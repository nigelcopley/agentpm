// Main JavaScript entry point for APM (Agent Project Manager) - Updated for dynamic file loading
import Alpine from 'alpinejs'
import 'htmx.org'

// Import existing custom JavaScript modules
import './components/toast.js'
import './components/searchable-select.js'
import './components/smart-filters.js'
import './components/loading-states.js'
import './components/enhanced-interactions.js'

// Import HTMX integration
import '../../static/js/htmx-integration.js'

// Phase content toggle functionality - Alpine.js component
Alpine.data('phaseContent', () => ({
    openPhases: new Set(),
    
    toggle(phaseValue) {
        if (this.openPhases.has(phaseValue)) {
            this.openPhases.delete(phaseValue);
        } else {
            this.openPhases.add(phaseValue);
        }
    },
    
    isOpen(phaseValue) {
        return this.openPhases.has(phaseValue);
    }
}));

// Work item detail component
Alpine.data('workItemDetail', () => ({
    statusUpdateLoading: false,
    
    async updateStatus(newStatus) {
        this.statusUpdateLoading = true;
        try {
            const response = await fetch(`/work-items/${this.workItemId}/update-status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            });
            
            if (response.ok) {
                const result = await response.json();
                window.showToast(result.message, 'success');
                // Reload the page to show updated status
                setTimeout(() => window.location.reload(), 1000);
            } else {
                throw new Error('Failed to update status');
            }
        } catch (error) {
            window.showToast('Failed to update status', 'error');
        } finally {
            this.statusUpdateLoading = false;
        }
    }
}));

// Search component
Alpine.data('search', () => ({
    query: '',
    results: [],
    loading: false,
    
    async search() {
        if (!this.query.trim()) {
            this.results = [];
            return;
        }
        
        this.loading = true;
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(this.query)}`);
            const data = await response.json();
            this.results = data.results || [];
        } catch (error) {
            console.error('Search error:', error);
            this.results = [];
        } finally {
            this.loading = false;
        }
    },
    
    clear() {
        this.query = '';
        this.results = [];
    }
}));

// Form component with validation
Alpine.data('form', (config = {}) => ({
    data: config.initialData || {},
    errors: {},
    loading: false,
    
    setField(field, value) {
        this.data[field] = value;
        // Clear error when user starts typing
        if (this.errors[field]) {
            delete this.errors[field];
        }
    },
    
    setError(field, message) {
        this.errors[field] = message;
    },
    
    clearErrors() {
        this.errors = {};
    },
    
    async submit(url, method = 'POST') {
        this.loading = true;
        this.clearErrors();
        
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                if (result.redirect) {
                    window.location.href = result.redirect;
                } else if (result.message) {
                    window.showToast(result.message, 'success');
                }
                return result;
            } else {
                if (result.errors) {
                    this.errors = result.errors;
                } else {
                    window.showToast(result.message || 'An error occurred', 'error');
                }
                return null;
            }
        } catch (error) {
            console.error('Form submission error:', error);
            window.showToast('Network error occurred', 'error');
            return null;
        } finally {
            this.loading = false;
        }
    }
}));

// Header controller component
Alpine.data('headerController', () => ({
    searchOpen: false,
    searchQuery: '',
    mobileOpen: false,
    
    init() {
        // Focus search input when opened
        this.$watch('searchOpen', (value) => {
            if (value) {
                this.$nextTick(() => {
                    if (this.$refs.search) {
                        this.$refs.search.focus();
                    }
                });
            }
        });
    },
    
    toggleSearch() {
        this.searchOpen = !this.searchOpen;
        if (!this.searchOpen) {
            this.searchQuery = '';
        }
    },
    
    submitSearch() {
        if (this.searchQuery.trim()) {
            // Navigate to search results
            window.location.href = `/search?q=${encodeURIComponent(this.searchQuery.trim())}`;
        }
    },
    
    toggleMobile() {
        this.mobileOpen = !this.mobileOpen;
    },
    
    closeMobile() {
        this.mobileOpen = false;
    },
    
    showNotifications() {
        // Show notifications panel or navigate to notifications page
        if (window.showToast) {
            window.showToast('Notifications feature coming soon!', 'info');
        }
    },
    
    showKeyboardShortcuts() {
        if (window.ModalSystem) {
            window.ModalSystem.showKeyboardShortcuts();
        }
    }
}));

// Initialize Alpine.js
window.Alpine = Alpine
Alpine.start()

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('APM (Agent Project Manager) JavaScript bundle loaded - Version 2.0');
    
    // Initialize any global components here
    if (typeof initializeComponents === 'function') {
        initializeComponents();
    }
});

// Export for module systems
export { Alpine };
