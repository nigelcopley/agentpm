/**
 * Smart Filtering System
 *
 * Provides intelligent filtering and ordering with sticky preferences
 * for all dashboard views.
 *
 * Features:
 * - URL query parameters for filter state
 * - localStorage for sticky preferences
 * - Sort direction indicators (↑↓)
 * - Filter count badges
 * - Clear filters button
 * - Keyboard navigation support
 */

class SmartFilters {
    constructor(config) {
        this.viewName = config.viewName;  // e.g., 'work-items', 'tasks', 'agents'
        this.tableSelector = config.tableSelector;
        this.rowSelector = config.rowSelector;
        this.filters = config.filters || {};  // { type: ['feature', 'enhancement'], status: ['in_progress'] }
        this.sortConfig = config.sortConfig || { column: null, direction: 'asc' };

        this.init();
    }

    /**
     * Initialize filtering system
     */
    init() {
        // Load preferences from localStorage
        this.loadPreferences();

        // Parse URL parameters (takes precedence over localStorage)
        this.parseUrlParams();

        // Set up event listeners
        this.setupFilterButtons();
        this.setupSortHeaders();
        this.setupClearFilters();

        // Apply initial filters
        this.applyFilters();

        // Update UI to reflect current state
        this.updateUI();
    }

    /**
     * Load preferences from localStorage
     */
    loadPreferences() {
        const key = `aipm_filters_${this.viewName}`;
        const stored = localStorage.getItem(key);

        if (stored) {
            try {
                const prefs = JSON.parse(stored);
                this.filters = prefs.filters || this.filters;
                this.sortConfig = prefs.sortConfig || this.sortConfig;
            } catch (e) {
                console.error('Failed to load filter preferences:', e);
            }
        }
    }

    /**
     * Save preferences to localStorage
     */
    savePreferences() {
        const key = `aipm_filters_${this.viewName}`;
        const prefs = {
            filters: this.filters,
            sortConfig: this.sortConfig
        };

        try {
            localStorage.setItem(key, JSON.stringify(prefs));
        } catch (e) {
            console.error('Failed to save filter preferences:', e);
        }
    }

    /**
     * Parse URL query parameters
     */
    parseUrlParams() {
        const params = new URLSearchParams(window.location.search);

        // Parse filter parameters (e.g., ?type=feature&status=in_progress)
        for (const [key, value] of params.entries()) {
            if (key === 'sort') {
                this.sortConfig.column = value;
            } else if (key === 'dir') {
                this.sortConfig.direction = value === 'desc' ? 'desc' : 'asc';
            } else {
                // It's a filter parameter
                this.filters[key] = value.split(',');
            }
        }
    }

    /**
     * Update URL with current filter state (without page reload)
     */
    updateUrl() {
        const params = new URLSearchParams();

        // Add filter parameters
        for (const [key, values] of Object.entries(this.filters)) {
            if (values && values.length > 0 && !values.includes('all')) {
                params.set(key, values.join(','));
            }
        }

        // Add sort parameters
        if (this.sortConfig.column) {
            params.set('sort', this.sortConfig.column);
            params.set('dir', this.sortConfig.direction);
        }

        // Update URL without reload
        const newUrl = params.toString()
            ? `${window.location.pathname}?${params.toString()}`
            : window.location.pathname;

        window.history.replaceState({}, '', newUrl);
    }

    /**
     * Set up filter button event listeners
     */
    setupFilterButtons() {
        const filterButtons = document.querySelectorAll('[data-filter-type]');

        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();

                const filterType = button.getAttribute('data-filter-type');
                const filterValue = button.getAttribute('data-filter-value');

                this.toggleFilter(filterType, filterValue);
                this.applyFilters();
                this.updateUI();
                this.savePreferences();
                this.updateUrl();
            });
        });
    }

    /**
     * Toggle filter value
     */
    toggleFilter(type, value) {
        if (!this.filters[type]) {
            this.filters[type] = [];
        }

        if (value === 'all') {
            // Clear this filter type
            this.filters[type] = ['all'];
        } else {
            // Toggle specific value
            const index = this.filters[type].indexOf(value);

            if (index > -1) {
                this.filters[type].splice(index, 1);
            } else {
                this.filters[type] = this.filters[type].filter(v => v !== 'all');
                this.filters[type].push(value);
            }

            // If no values selected, default to 'all'
            if (this.filters[type].length === 0) {
                this.filters[type] = ['all'];
            }
        }
    }

    /**
     * Set up sortable column headers
     */
    setupSortHeaders() {
        const sortHeaders = document.querySelectorAll('[data-sort-column]');

        sortHeaders.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.getAttribute('data-sort-column');
                this.toggleSort(column);
                this.applySort();
                this.updateUI();
                this.savePreferences();
                this.updateUrl();
            });
        });
    }

    /**
     * Toggle sort direction
     */
    toggleSort(column) {
        if (this.sortConfig.column === column) {
            // Toggle direction
            this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            // New column, default to ascending
            this.sortConfig.column = column;
            this.sortConfig.direction = 'asc';
        }
    }

    /**
     * Set up clear filters button
     */
    setupClearFilters() {
        const clearButton = document.querySelector('[data-clear-filters]');

        if (clearButton) {
            clearButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearAllFilters();
                this.applyFilters();
                this.updateUI();
                this.savePreferences();
                this.updateUrl();
            });
        }
    }

    /**
     * Clear all filters
     */
    clearAllFilters() {
        for (const key in this.filters) {
            this.filters[key] = ['all'];
        }
        this.sortConfig = { column: null, direction: 'asc' };
    }

    /**
     * Apply filters to table rows
     */
    applyFilters() {
        const rows = document.querySelectorAll(this.rowSelector);
        let visibleCount = 0;

        rows.forEach(row => {
            let visible = true;

            // Check each filter type
            for (const [filterType, filterValues] of Object.entries(this.filters)) {
                if (!filterValues || filterValues.includes('all')) {
                    continue;
                }

                // Handle quick-view filters specially
                if (filterType === 'quick-view') {
                    const quickViewValue = filterValues[0]; // Take first selected quick view
                    const rowStatus = row.getAttribute('data-status');
                    const rowPriority = parseInt(row.getAttribute('data-priority')) || 0;
                    
                    console.log(`Quick view filter: ${quickViewValue}, Row status: ${rowStatus}, Row priority: ${rowPriority}`);
                    
                    switch (quickViewValue) {
                        case 'active':
                            // Show only active work items (not cancelled/consolidated)
                            visible = rowPriority !== 5;
                            break;
                        case 'in-progress':
                            visible = rowStatus === 'in_progress';
                            break;
                        case 'proposed':
                            visible = rowStatus === 'proposed';
                            break;
                        case 'review':
                            visible = rowStatus === 'review';
                            break;
                        case 'completed':
                            visible = rowStatus === 'completed';
                            break;
                        default:
                            visible = true;
                    }
                    
                    console.log(`Row visibility after quick-view filter: ${visible}`);
                } else {
                    // Standard filter logic
                    const rowValue = row.getAttribute(`data-${filterType}`);
                    if (rowValue && !filterValues.includes(rowValue)) {
                        visible = false;
                    }
                }

                if (!visible) break;
            }

            row.style.display = visible ? '' : 'none';
            if (visible) visibleCount++;
        });

        // Update visible count
        this.updateVisibleCount(visibleCount);
    }

    /**
     * Apply sort to visible rows
     */
    applySort() {
        if (!this.sortConfig.column) return;

        const table = document.querySelector(this.tableSelector);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll(this.rowSelector));

        rows.sort((a, b) => {
            const aValue = this.getSortValue(a, this.sortConfig.column);
            const bValue = this.getSortValue(b, this.sortConfig.column);

            let comparison = 0;

            if (aValue < bValue) {
                comparison = -1;
            } else if (aValue > bValue) {
                comparison = 1;
            }

            return this.sortConfig.direction === 'asc' ? comparison : -comparison;
        });

        // Re-append rows in sorted order
        rows.forEach(row => tbody.appendChild(row));
    }

    /**
     * Get sortable value from row
     */
    getSortValue(row, column) {
        const cell = row.querySelector(`[data-sort-value="${column}"]`);

        if (cell) {
            const value = cell.getAttribute('data-value');

            // Try to parse as number
            const numValue = parseFloat(value);
            if (!isNaN(numValue)) {
                return numValue;
            }

            // Return as string (lowercase for case-insensitive sort)
            return value.toLowerCase();
        }

        // Fallback: use data attribute on row
        const value = row.getAttribute(`data-${column}`);
        return value ? value.toLowerCase() : '';
    }

    /**
     * Update UI to reflect current filter state
     */
    updateUI() {
        // Update filter buttons
        const filterButtons = document.querySelectorAll('[data-filter-type]');

        filterButtons.forEach(button => {
            const filterType = button.getAttribute('data-filter-type');
            const filterValue = button.getAttribute('data-filter-value');

            const isActive = this.filters[filterType] &&
                            (this.filters[filterType].includes(filterValue) ||
                             (filterValue === 'all' && this.filters[filterType].includes('all')));

            button.classList.toggle('active', isActive);
            button.setAttribute('aria-pressed', isActive.toString());
        });

        // Update sort indicators
        const sortHeaders = document.querySelectorAll('[data-sort-column]');

        sortHeaders.forEach(header => {
            const column = header.getAttribute('data-sort-column');
            const indicator = header.querySelector('.sort-indicator');

            if (indicator) {
                indicator.remove();
            }

            if (this.sortConfig.column === column) {
                const arrow = this.sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
                const span = document.createElement('span');
                span.className = 'sort-indicator';
                span.textContent = arrow;
                header.appendChild(span);
            }
        });

        // Update filter count badges
        this.updateFilterBadges();
    }

    /**
     * Update filter count badges
     */
    updateFilterBadges() {
        let activeFilterCount = 0;

        for (const [key, values] of Object.entries(this.filters)) {
            if (values && values.length > 0 && !values.includes('all')) {
                activeFilterCount += values.length;
            }
        }

        const badge = document.querySelector('.filter-count-badge');

        if (badge) {
            badge.textContent = activeFilterCount;
            badge.style.display = activeFilterCount > 0 ? 'inline-block' : 'none';
        }
    }

    /**
     * Update visible row count
     */
    updateVisibleCount(count) {
        const countElement = document.querySelector('.visible-count');
        const totalCount = document.querySelectorAll(this.rowSelector).length;

        if (countElement) {
            countElement.textContent = `${count} of ${totalCount}`;
        }
    }
}

// Export for use in templates
window.SmartFilters = SmartFilters;
