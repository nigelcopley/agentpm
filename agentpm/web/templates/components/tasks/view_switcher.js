// Task View Switcher JavaScript Component
// This handles the view switching functionality for tasks list

function setView(viewType) {
    // Hide all view containers
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.add('hidden');
    });
    
    // Remove active class from all view toggles
    document.querySelectorAll('.view-toggle').forEach(toggle => {
        toggle.classList.remove('active', 'bg-white', 'text-emerald-600', 'shadow-sm');
        toggle.classList.add('text-gray-500');
    });
    
    // Show selected view and activate toggle
    const container = document.getElementById(viewType + 'ViewContainer');
    const toggle = document.getElementById(viewType + 'View');
    
    if (container) {
        container.classList.remove('hidden');
    }
    
    if (toggle) {
        toggle.classList.add('active', 'bg-white', 'text-emerald-600', 'shadow-sm');
        toggle.classList.remove('text-gray-500');
    }
    
    // Save preference to localStorage
    localStorage.setItem('tasksView', viewType);
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('filterForm').submit();
}

function clearFilter(filterName) {
    const form = document.getElementById('filterForm');
    const input = form.querySelector(`[name="${filterName}"]`);
    if (input) {
        input.value = '';
        form.submit();
    }
}

function updateFilterCount() {
    const form = document.getElementById('filterForm');
    if (!form) return;
    
    const searchInput = form.querySelector('[name="search"]');
    const statusSelect = form.querySelector('[name="status"]');
    const typeSelect = form.querySelector('[name="type"]');
    const workItemSelect = form.querySelector('[name="work_item"]');
    const assignedSelect = form.querySelector('[name="assigned"]');
    
    const searchValue = searchInput ? searchInput.value.trim() : '';
    const statusValue = statusSelect ? statusSelect.value : '';
    const typeValue = typeSelect ? typeSelect.value : '';
    const workItemValue = workItemSelect ? workItemSelect.value : '';
    const assignedValue = assignedSelect ? assignedSelect.value : '';
    
    let activeCount = 0;
    if (searchValue) activeCount++;
    if (statusValue) activeCount++;
    if (typeValue) activeCount++;
    if (workItemValue) activeCount++;
    if (assignedValue) activeCount++;
    
    const countElement = document.getElementById('filterCount');
    if (countElement) {
        if (activeCount > 0) {
            countElement.textContent = activeCount;
            countElement.style.display = 'inline-block';
        } else {
            countElement.style.display = 'none';
        }
    }
}

// Auto-submit form on filter change with debouncing
let submitTimeout;
function debouncedSubmit(form) {
    clearTimeout(submitTimeout);
    submitTimeout = setTimeout(() => {
        form.submit();
    }, 300);
}

document.addEventListener('DOMContentLoaded', function() {
    // Restore saved view preference
    const savedView = localStorage.getItem('tasksView') || 'list';
    setView(savedView);
    
    // Auto-submit on filter changes
    const filterSelects = document.querySelectorAll('select[name="status"], select[name="type"], select[name="work_item"], select[name="assigned"], select[name="sort"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            updateFilterCount();
            debouncedSubmit(this.form);
        });
    });
    
    // Auto-submit on search with debouncing
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            updateFilterCount();
            debouncedSubmit(this.form);
        });
    }
    
    // Update filter count on page load
    updateFilterCount();
    
    // Show loading state on form submission
    const form = document.getElementById('filterForm');
    if (form) {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="bi bi-hourglass-split mr-1"></i>Applying...';
                submitButton.disabled = true;
                
                // Re-enable after a delay (in case of errors)
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 3000);
            }
        });
    }
});
