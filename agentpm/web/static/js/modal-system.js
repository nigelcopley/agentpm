// APM (Agent Project Manager) Modal System
// Professional Alpine.js implementation with stores

document.addEventListener('alpine:init', () => {
    // Global modal store
    Alpine.store('modal', {
        open: false,
        type: '',
        data: {},
        
        show(type, data = {}) {
            this.type = type;
            this.data = data;
            this.open = true;
            
            // Prevent body scroll when modal is open
            document.body.style.overflow = 'hidden';
        },
        
        hide() {
            this.open = false;
            this.type = '';
            this.data = {};
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    });
    
    // Global notification store
    Alpine.store('notifications', {
        items: [],
        
        add(message, type = 'info', duration = 5000) {
            const id = Date.now() + Math.random();
            const notification = {
                id,
                message,
                type,
                duration
            };
            
            this.items.push(notification);
            
            // Auto remove after duration
            setTimeout(() => {
                this.remove(id);
            }, duration);
            
            return id;
        },
        
        remove(id) {
            this.items = this.items.filter(item => item.id !== id);
        },
        
        clear() {
            this.items = [];
        }
    });
    
    // Global loading store
    Alpine.store('loading', {
        states: new Set(),
        
        start(key) {
            this.states.add(key);
        },
        
        stop(key) {
            this.states.delete(key);
        },
        
        isLoading(key) {
            return this.states.has(key);
        },
        
        isAnyLoading() {
            return this.states.size > 0;
        }
    });
});

// Global modal system for backward compatibility
window.ModalSystem = {
    show(type, data = {}) {
        if (window.Alpine && window.Alpine.store) {
            window.Alpine.store('modal').show(type, data);
        }
    },
    
    hide() {
        if (window.Alpine && window.Alpine.store) {
            window.Alpine.store('modal').hide();
        }
    },
    
    showKeyboardShortcuts() {
        this.show('keyboard-shortcuts');
    }
};

// Global notification system
window.showToast = function(message, type = 'info', duration = 5000) {
    if (window.Alpine && window.Alpine.store) {
        return window.Alpine.store('notifications').add(message, type, duration);
    }
    
    // Fallback for when Alpine isn't loaded yet
    console.log(`Toast: ${type} - ${message}`);
};

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + / for keyboard shortcuts help
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        window.ModalSystem.showKeyboardShortcuts();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        if (window.Alpine && window.Alpine.store) {
            window.Alpine.store('modal').hide();
        }
    }
});