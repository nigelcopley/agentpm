/**
 * Searchable Select Component
 * 
 * A reusable searchable dropdown component similar to Select2.
 * Can be applied to any select element by adding the 'searchable-select' class.
 * 
 * Usage:
 * 1. Add 'searchable-select' class to any select element
 * 2. Optionally add 'data-placeholder' attribute for custom placeholder
 * 3. Optionally add 'data-search-placeholder' for search input placeholder
 * 
 * Features:
 * - Real-time filtering as you type
 * - Keyboard navigation (arrow keys, enter, escape)
 * - Click outside to close
 * - Auto-completion on form submit
 * - Custom styling with hover effects
 * - Accessible with proper focus management
 */

class SearchableSelect {
    constructor(selectElement) {
        this.originalSelect = selectElement;
        this.container = null;
        this.searchInput = null;
        this.hiddenInput = null;
        this.dropdown = null;
        this.options = [];
        this.isOpen = false;
        this.selectedOption = null;
        
        this.init();
    }
    
    init() {
        this.createContainer();
        this.createSearchInput();
        this.createHiddenInput();
        this.createDropdown();
        this.populateOptions();
        this.bindEvents();
        this.hideOriginalSelect();
    }
    
    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'searchable-select-container relative';
        this.container.setAttribute('data-name', this.originalSelect.name || '');
        
        // Insert after the original select
        this.originalSelect.parentNode.insertBefore(this.container, this.originalSelect.nextSibling);
    }
    
    createSearchInput() {
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.className = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent searchable-select-input';
        this.searchInput.placeholder = this.originalSelect.dataset.searchPlaceholder || 'Type to search...';
        this.searchInput.autocomplete = 'off';
        
        // Add chevron icon
        const chevron = document.createElement('div');
        chevron.className = 'absolute right-3 top-2.5 pointer-events-none';
        chevron.innerHTML = '<i class="bi bi-chevron-down text-gray-400"></i>';
        
        this.container.appendChild(this.searchInput);
        this.container.appendChild(chevron);
    }
    
    createHiddenInput() {
        this.hiddenInput = document.createElement('input');
        this.hiddenInput.type = 'hidden';
        this.hiddenInput.name = this.originalSelect.name;
        this.hiddenInput.id = this.originalSelect.id;
        this.hiddenInput.value = this.originalSelect.value;
        
        this.container.appendChild(this.hiddenInput);
    }
    
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'searchable-select-dropdown hidden absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto';
        
        this.container.appendChild(this.dropdown);
    }
    
    populateOptions() {
        const originalOptions = this.originalSelect.querySelectorAll('option');
        
        originalOptions.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'searchable-select-option px-4 py-2 hover:bg-gray-100 cursor-pointer';
            optionElement.setAttribute('data-value', option.value);
            optionElement.setAttribute('data-index', index);
            
            // Create option content
            const content = document.createElement('div');
            if (option.value === '') {
                // Special handling for empty option (usually placeholder)
                content.innerHTML = `
                    <div class="font-medium text-gray-900">${option.textContent}</div>
                    <div class="text-sm text-gray-500">${option.dataset.description || ''}</div>
                `;
            } else {
                content.innerHTML = `
                    <div class="font-medium text-gray-900">${option.textContent}</div>
                    <div class="text-sm text-gray-500">${option.dataset.description || option.value}</div>
                `;
            }
            
            optionElement.appendChild(content);
            this.dropdown.appendChild(optionElement);
            this.options.push(optionElement);
        });
        
        // Set initial value if selected
        if (this.originalSelect.value) {
            const selectedOption = this.options.find(opt => opt.dataset.value === this.originalSelect.value);
            if (selectedOption) {
                this.selectOption(selectedOption, false);
            }
        }
    }
    
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('click', (e) => {
            e.stopPropagation();
            if (!this.isOpen) {
                this.toggleDropdown();
            }
        });
        
        this.searchInput.addEventListener('input', () => {
            if (!this.isOpen) {
                this.toggleDropdown();
            }
            this.filterOptions();
        });
        
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (!this.isOpen) {
                    this.toggleDropdown();
                }
                this.focusFirstVisibleOption();
            } else if (e.key === 'Escape') {
                this.closeDropdown();
            }
        });
        
        // Option events
        this.options.forEach(option => {
            option.addEventListener('click', () => {
                this.selectOption(option);
            });
            
            option.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectOption(option);
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.focusNextOption(option);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.focusPreviousOption(option);
                }
            });
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Form submission handling
        const form = this.originalSelect.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                this.handleFormSubmit();
            });
        }
    }
    
    toggleDropdown() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.openDropdown();
        } else {
            this.closeDropdown();
        }
    }
    
    openDropdown() {
        this.dropdown.classList.remove('hidden');
        this.searchInput.focus();
        this.filterOptions();
    }
    
    closeDropdown() {
        this.dropdown.classList.add('hidden');
        this.isOpen = false;
    }
    
    filterOptions() {
        const searchTerm = this.searchInput.value.toLowerCase();
        
        this.options.forEach(option => {
            const text = option.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        });
    }
    
    selectOption(option, closeDropdown = true) {
        this.selectedOption = option;
        const value = option.dataset.value;
        const displayText = option.querySelector('.font-medium').textContent;
        
        // Update hidden input
        this.hiddenInput.value = value;
        
        // Update search input display
        if (value === '') {
            this.searchInput.value = '';
            this.searchInput.placeholder = this.originalSelect.dataset.searchPlaceholder || 'Type to search...';
        } else {
            this.searchInput.value = displayText;
        }
        
        // Close dropdown
        if (closeDropdown) {
            this.closeDropdown();
        }
        
        // Update visual state
        this.options.forEach(opt => {
            opt.classList.remove('bg-blue-50', 'border-blue-200');
        });
        option.classList.add('bg-blue-50', 'border-blue-200');
        
        // Trigger change event
        this.triggerChangeEvent();
    }
    
    focusFirstVisibleOption() {
        const visibleOptions = this.options.filter(opt => opt.style.display !== 'none');
        if (visibleOptions.length > 0) {
            visibleOptions[0].focus();
        }
    }
    
    focusNextOption(currentOption) {
        const currentIndex = parseInt(currentOption.dataset.index);
        const nextOption = this.options.find(opt => 
            parseInt(opt.dataset.index) === currentIndex + 1 && opt.style.display !== 'none'
        );
        if (nextOption) {
            nextOption.focus();
        }
    }
    
    focusPreviousOption(currentOption) {
        const currentIndex = parseInt(currentOption.dataset.index);
        const prevOption = this.options.find(opt => 
            parseInt(opt.dataset.index) === currentIndex - 1 && opt.style.display !== 'none'
        );
        if (prevOption) {
            prevOption.focus();
        }
    }
    
    handleFormSubmit() {
        if (this.searchInput.value && !this.hiddenInput.value) {
            // If user typed something but didn't select, try to find matching option
            const matchingOption = this.options.find(option => {
                const text = option.querySelector('.font-medium').textContent.toLowerCase();
                return text === this.searchInput.value.toLowerCase();
            });
            
            if (matchingOption) {
                this.hiddenInput.value = matchingOption.dataset.value;
            }
        }
    }
    
    triggerChangeEvent() {
        // Create and dispatch a change event
        const event = new Event('change', { bubbles: true });
        this.hiddenInput.dispatchEvent(event);
    }
    
    hideOriginalSelect() {
        this.originalSelect.style.display = 'none';
    }
    
    // Public methods for external control
    getValue() {
        return this.hiddenInput.value;
    }
    
    setValue(value) {
        const option = this.options.find(opt => opt.dataset.value === value);
        if (option) {
            this.selectOption(option, false);
        }
    }
    
    destroy() {
        // Restore original select
        this.originalSelect.style.display = '';
        
        // Remove container
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }
}

// Auto-initialize all searchable selects on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSearchableSelects();
});

// Function to initialize searchable selects
function initializeSearchableSelects() {
    const selectElements = document.querySelectorAll('select.searchable-select');
    selectElements.forEach(select => {
        if (!select.dataset.searchableInitialized) {
            new SearchableSelect(select);
            select.dataset.searchableInitialized = 'true';
        }
    });
}

// Function to manually initialize a specific select
function makeSearchable(selectElement) {
    if (selectElement && selectElement.tagName === 'SELECT') {
        if (!selectElement.dataset.searchableInitialized) {
            new SearchableSelect(selectElement);
            selectElement.dataset.searchableInitialized = 'true';
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SearchableSelect, initializeSearchableSelects, makeSearchable };
}
