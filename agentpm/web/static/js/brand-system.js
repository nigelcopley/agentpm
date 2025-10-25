/**
 * APM (Agent Project Manager) Brand System JavaScript
 * Modern, clean, professional interactions
 */

// Brand System Namespace
window.AIPM = window.AIPM || {};

// Utility Functions
AIPM.utils = {
    // Debounce function for performance
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },

    // Throttle function for performance
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Format date for display
    formatDate: function(date) {
        if (!date) return 'No date';
        const d = new Date(date);
        return d.toLocaleDateString('en-GB', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    // Format relative time
    formatRelativeTime: function(date) {
        if (!date) return 'No date';
        const now = new Date();
        const d = new Date(date);
        const diffMs = now - d;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
        return `${Math.floor(diffDays / 365)} years ago`;
    },

    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard', 'success');
            }).catch(() => {
                this.showToast('Failed to copy', 'error');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showToast('Copied to clipboard', 'success');
            } catch (err) {
                this.showToast('Failed to copy', 'error');
            }
            document.body.removeChild(textArea);
        }
    },

    // Show toast notification
    showToast: function(message, type = 'info', duration = 5000) {
        if (typeof showToast === 'function') {
            showToast(message, type, duration);
        } else {
            console.log(`Toast: ${message} (${type})`);
        }
    }
};

// Smart Filters System
AIPM.filters = {
    activeFilters: {
        status: null,
        type: null,
        priority: null,
        phase: null,
        search: ''
    },
    
    init: function() {
        this.setupFilterButtons();
        this.setupSearchInput();
        const hadSavedFilters = this.loadSavedFilters();
        if (!hadSavedFilters) {
            this.restoreFilterButtons();
            this.applyFilters();
            this.dispatchUpdate();
        }
    },
    
    setupFilterButtons: function() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filterValue = button.getAttribute('data-filter');
                const group = button.getAttribute('data-filter-group') ||
                    button.closest('[data-filter-group]')?.getAttribute('data-filter-group') ||
                    'misc';
                this.toggleFilter(group, filterValue, button);
            });
        });
    },
    
    setupSearchInput: function() {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            const debouncedSearch = AIPM.utils.debounce((query) => {
                this.applySearchFilter(query);
            }, 300);
            
            searchInput.addEventListener('input', (e) => {
                debouncedSearch(e.target.value);
            });
        }
    },
    
    toggleFilter: function(group, filterValue, button) {
        const filtersCopy = { ...this.activeFilters };
        const groupKey = group || 'misc';
        const previousValue = filtersCopy[groupKey] ?? null;

        if (groupKey === 'status' && previousValue !== null && previousValue === filterValue) {
            const groupContainer = button ? (button.closest('.filter-group') || document) : document;
            if (groupContainer) {
                groupContainer.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                const allBtn = groupContainer.querySelector('.filter-btn[data-filter="all"]');
                if (allBtn) {
                    allBtn.classList.add('active');
                }
            }
            filtersCopy.status = null;
            this.activeFilters = filtersCopy;
            this.applyFilters();
            this.saveFilters();
            this.dispatchUpdate();
            return;
        }

        if (groupKey !== 'status' && previousValue !== null && previousValue === filterValue) {
            filtersCopy[groupKey] = null;
            if (button) {
                const groupContainer = button.closest('.filter-group') || document;
                groupContainer.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            }
            this.activeFilters = filtersCopy;
            this.applyFilters();
            this.saveFilters();
            this.dispatchUpdate();
            return;
        }

        if (button) {
            const groupContainer = button.closest('.filter-group') || document;
            groupContainer.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        }

        if (groupKey === 'status' && filterValue === 'all') {
            filtersCopy.status = null;
        } else if (groupKey in filtersCopy) {
            filtersCopy[groupKey] = filterValue;
        } else {
            filtersCopy[groupKey] = filterValue;
        }

        this.activeFilters = filtersCopy;
        this.applyFilters();
        this.saveFilters();
        this.dispatchUpdate();
    },
    
    applyFilters: function() {
        const rows = document.querySelectorAll('.work-item-row, .task-row, .project-row');
        let visibleCount = 0;
        const statusFilter = this.activeFilters.status;
        const typeFilter = this.activeFilters.type;
        const priorityFilter = this.activeFilters.priority;
        const phaseFilter = this.activeFilters.phase;
        const searchTerm = (this.activeFilters.search || '').toLowerCase();
        
        rows.forEach(row => {
            let visible = true;

            if (statusFilter && row.getAttribute('data-status') !== statusFilter) {
                visible = false;
            }

            if (visible && typeFilter && row.getAttribute('data-type') !== typeFilter) {
                visible = false;
            }

            if (visible && priorityFilter && row.getAttribute('data-priority') !== priorityFilter) {
                visible = false;
            }

            if (visible && phaseFilter && row.getAttribute('data-phase') !== phaseFilter) {
                visible = false;
            }

            if (visible && searchTerm) {
                const text = row.textContent.toLowerCase();
                if (!text.includes(searchTerm)) {
                    visible = false;
                }
            }
            
            row.style.display = visible ? '' : 'none';
            if (visible) visibleCount++;
        });
        
        this.updateVisibleCount(visibleCount);
    },
    
    applySearchFilter: function(query) {
        this.activeFilters.search = query || '';
        this.applyFilters();
        this.saveFilters();
        this.dispatchUpdate();
    },
    
    updateVisibleCount: function(count) {
        const countElements = document.querySelectorAll('.visible-count');
        countElements.forEach(el => {
            el.textContent = count;
        });
    },
    
    saveFilters: function() {
        localStorage.setItem('aipm-filters', JSON.stringify(this.activeFilters));
    },
    
    loadSavedFilters: function() {
        const saved = localStorage.getItem('aipm-filters');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                let statusValue = parsed.status ?? null;
                let typeValue = parsed.type ?? null;
                let priorityValue = parsed.priority ?? null;
                let phaseValue = parsed.phase ?? null;

                if (!statusValue) {
                    if (parsed['in-progress']) statusValue = 'in_progress';
                    else if (parsed['proposed']) statusValue = 'proposed';
                    else if (parsed['validated']) statusValue = 'validated';
                    else if (parsed['accepted']) statusValue = 'accepted';
                    else if (parsed['review']) statusValue = 'review';
                    else if (parsed['completed']) statusValue = 'completed';
                }

                if (!typeValue) {
                    if (parsed['type-feature']) typeValue = 'feature';
                    else if (parsed['type-enhancement']) typeValue = 'enhancement';
                    else if (parsed['type-bugfix']) typeValue = 'bugfix';
                    else if (parsed['type-research']) typeValue = 'research';
                    else if (parsed['type-analysis']) typeValue = 'analysis';
                    else if (parsed['type-documentation']) typeValue = 'documentation';
                }

                if (!priorityValue) {
                    if (parsed['priority-1']) priorityValue = '1';
                    else if (parsed['priority-2']) priorityValue = '2';
                    else if (parsed['priority-3']) priorityValue = '3';
                }

                if (!phaseValue) {
                    if (parsed['phase-D1_discovery']) phaseValue = 'D1_discovery';
                    else if (parsed['phase-P1_plan']) phaseValue = 'P1_plan';
                    else if (parsed['phase-I1_implementation']) phaseValue = 'I1_implementation';
                    else if (parsed['phase-R1_review']) phaseValue = 'R1_review';
                    else if (parsed['phase-O1_operations']) phaseValue = 'O1_operations';
                    else if (parsed['phase-E1_evolution']) phaseValue = 'E1_evolution';
                }

                this.activeFilters = {
                    status: statusValue,
                    type: typeValue,
                    priority: priorityValue,
                    phase: phaseValue,
                    search: parsed.search || ''
                };
                this.restoreFilterButtons();
                this.applyFilters();
                this.dispatchUpdate();
                return true;
            } catch (err) {
                console.warn('Failed to parse saved filters', err);
            }
        }
        return false;
    },

    restoreFilterButtons: function() {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));

        Object.entries(this.activeFilters).forEach(([group, value]) => {
            if (!value && group !== 'status') {
                return;
            }
            if (group === 'status' && value === null) {
                const allBtn = document.querySelector('.filter-btn[data-filter-group="status"][data-filter="all"]');
                if (allBtn) {
                    allBtn.classList.add('active');
                }
                return;
            }
            if (!value) return;
            const selector = `.filter-btn[data-filter-group="${group}"][data-filter="${value}"]`;
            const button = document.querySelector(selector);
            if (button) {
                button.classList.add('active');
            }
        });
    },
    
    clearFilters: function() {
        this.activeFilters = {
            status: null,
            type: null,
            priority: null,
            phase: null,
            search: ''
        };
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        this.restoreFilterButtons();
        this.applyFilters();
        this.saveFilters();
        this.dispatchUpdate();
    },

    dispatchUpdate: function() {
        document.dispatchEvent(new CustomEvent('aipm:filters-update', {
            detail: {
                filters: { ...this.activeFilters }
            }
        }));
    }
};

// Card Interactions
AIPM.cards = {
    init: function() {
        this.setupCardHover();
        this.setupCardActions();
    },
    
    setupCardHover: function() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
                card.style.boxShadow = 'var(--shadow-lg)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = 'var(--shadow-md)';
            });
        });
    },
    
    setupCardActions: function() {
        // Quick action buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="start-work-item"]')) {
                e.preventDefault();
                const workItemId = e.target.closest('[data-work-item-id]').getAttribute('data-work-item-id');
                this.startWorkItem(workItemId);
            }
            
            if (e.target.closest('[data-action="pause-work-item"]')) {
                e.preventDefault();
                const workItemId = e.target.closest('[data-work-item-id]').getAttribute('data-work-item-id');
                this.pauseWorkItem(workItemId);
            }
            
            if (e.target.closest('[data-action="edit-work-item"]')) {
                e.preventDefault();
                const workItemId = e.target.closest('[data-work-item-id]').getAttribute('data-work-item-id');
                this.editWorkItem(workItemId);
            }
        });
    },
    
    startWorkItem: function(workItemId) {
        AIPM.utils.showToast('Starting work item...', 'info');
        // TODO: Implement API call
        console.log('Starting work item:', workItemId);
    },
    
    pauseWorkItem: function(workItemId) {
        AIPM.utils.showToast('Pausing work item...', 'warning');
        // TODO: Implement API call
        console.log('Pausing work item:', workItemId);
    },
    
    editWorkItem: function(workItemId) {
        window.location.href = `/work-item/${workItemId}/edit`;
    }
};

// Form Enhancements
AIPM.forms = {
    init: function() {
        this.setupFormValidation();
        this.setupAutoSave();
    },
    
    setupFormValidation: function() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    },
    
    validateForm: function(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        return isValid;
    },
    
    showFieldError: function(field, message) {
        field.classList.add('border-error');
        let errorElement = field.parentElement.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error text-sm text-error mt-1';
            field.parentElement.appendChild(errorElement);
        }
        errorElement.textContent = message;
    },
    
    clearFieldError: function(field) {
        field.classList.remove('border-error');
        const errorElement = field.parentElement.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    },
    
    setupAutoSave: function() {
        const forms = document.querySelectorAll('form[data-autosave]');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                const debouncedSave = AIPM.utils.debounce(() => {
                    this.autoSave(form);
                }, 1000);
                
                input.addEventListener('input', debouncedSave);
            });
        });
    },
    
    autoSave: function(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // TODO: Implement auto-save API call
        console.log('Auto-saving form data:', data);
        AIPM.utils.showToast('Changes saved', 'success', 2000);
    }
};

// Keyboard Shortcuts
AIPM.shortcuts = {
    shortcuts: {
        'ctrl+k': 'focus-search',
        'ctrl+n': 'new-work-item',
        'ctrl+/': 'show-help',
        'escape': 'close-modals'
    },
    
    init: function() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyString(e);
            const action = this.shortcuts[key];
            
            if (action) {
                e.preventDefault();
                this.executeAction(action);
            }
        });
    },
    
    getKeyString: function(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.metaKey) parts.push('cmd');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    },
    
    executeAction: function(action) {
        switch (action) {
            case 'focus-search':
                const searchInput = document.getElementById('global-search');
                if (searchInput) searchInput.focus();
                break;
            case 'new-work-item':
                window.location.href = '/work-item/create';
                break;
            case 'show-help':
                this.showHelp();
                break;
            case 'close-modals':
                this.closeModals();
                break;
        }
    },
    
    showHelp: function() {
        AIPM.utils.showToast('Keyboard shortcuts: Ctrl+K (search), Ctrl+N (new work item), Ctrl+/ (help)', 'info', 5000);
    },
    
    closeModals: function() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.add('hidden');
        });
    }
};

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    AIPM.filters.init();
    AIPM.cards.init();
    AIPM.forms.init();
    AIPM.shortcuts.init();
    
    // Add loading states to all buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('button[data-loading]')) {
            const button = e.target;
            const originalText = button.textContent;
            button.textContent = 'Loading...';
            button.disabled = true;
            
            // Re-enable after 3 seconds (fallback)
            setTimeout(() => {
                button.textContent = originalText;
                button.disabled = false;
            }, 3000);
        }
    });
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    console.log('APM (Agent Project Manager) Brand System initialized');
});
