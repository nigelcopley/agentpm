/**
 * Bulk Operations JavaScript for Tasks and Work Items
 * Handles bulk selection, update, and delete operations
 */

// Global variables
let selectedTasks = new Set();
let selectedWorkItems = new Set();

// Task bulk operations
function toggleAllTasks(checkbox) {
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    taskCheckboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedTasks.add(parseInt(cb.value));
        } else {
            selectedTasks.delete(parseInt(cb.value));
        }
    });
    updateBulkActions();
}

function updateBulkActions() {
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    const selectedCount = Array.from(taskCheckboxes).filter(cb => cb.checked).length;
    
    const bulkContainer = document.getElementById('bulkActionsContainer');
    const bulkText = document.getElementById('bulkActionsText');
    const selectAllCheckbox = document.getElementById('selectAllTasks');
    
    if (selectedCount > 0) {
        bulkContainer.style.display = 'block';
        bulkText.textContent = `${selectedCount} Selected`;
        
        // Update select all checkbox state
        if (selectedCount === taskCheckboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedCount > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    } else {
        bulkContainer.style.display = 'none';
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    }
    
    // Update selected tasks set
    selectedTasks.clear();
    taskCheckboxes.forEach(cb => {
        if (cb.checked) {
            selectedTasks.add(parseInt(cb.value));
        }
    });
}

// Work Item bulk operations
function toggleAllWorkItems(checkbox) {
    const workItemCheckboxes = document.querySelectorAll('.work-item-checkbox');
    workItemCheckboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedWorkItems.add(parseInt(cb.value));
        } else {
            selectedWorkItems.delete(parseInt(cb.value));
        }
    });
    updateWorkItemBulkActions();
}

function updateWorkItemBulkActions() {
    const workItemCheckboxes = document.querySelectorAll('.work-item-checkbox');
    const selectedCount = Array.from(workItemCheckboxes).filter(cb => cb.checked).length;
    
    const bulkContainer = document.getElementById('bulkActionsContainer');
    const bulkText = document.getElementById('bulkActionsText');
    const selectAllCheckbox = document.getElementById('selectAllWorkItems');
    
    if (selectedCount > 0) {
        bulkContainer.style.display = 'block';
        bulkText.textContent = `${selectedCount} Selected`;
        
        // Update select all checkbox state
        if (selectedCount === workItemCheckboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedCount > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    } else {
        bulkContainer.style.display = 'none';
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    }
    
    // Update selected work items set
    selectedWorkItems.clear();
    workItemCheckboxes.forEach(cb => {
        if (cb.checked) {
            selectedWorkItems.add(parseInt(cb.value));
        }
    });
}

// Bulk update modal
function showBulkUpdateModal() {
    const selectedIds = Array.from(selectedTasks);
    if (selectedIds.length === 0) {
        showToast('Please select tasks to update', 'warning');
        return;
    }
    
    // Create modal HTML
    const modalHtml = `
        <div id="bulkUpdateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Bulk Update Tasks</h3>
                    <p class="text-sm text-gray-500 mb-4">Update ${selectedIds.length} selected tasks</p>
                    
                    <form id="bulkUpdateForm">
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Status</label>
                                <select name="status" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500">
                                    <option value="">No change</option>
                                    <option value="draft">Draft</option>
                                    <option value="ready">Ready</option>
                                    <option value="active">Active</option>
                                    <option value="in_progress">In Progress</option>
                                    <option value="review">Review</option>
                                    <option value="blocked">Blocked</option>
                                    <option value="done">Done</option>
                                    <option value="cancelled">Cancelled</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Priority</label>
                                <select name="priority" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500">
                                    <option value="">No change</option>
                                    <option value="1">Priority 1 (Highest)</option>
                                    <option value="2">Priority 2</option>
                                    <option value="3">Priority 3</option>
                                    <option value="4">Priority 4</option>
                                    <option value="5">Priority 5 (Lowest)</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Assigned To</label>
                                <input type="text" name="assigned_to" placeholder="Agent name or leave empty" 
                                       class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500">
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Description</label>
                                <textarea name="description" rows="3" placeholder="New description or leave empty" 
                                          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"></textarea>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3 mt-6">
                            <button type="button" onclick="closeBulkUpdateModal()" 
                                    class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500">
                                Cancel
                            </button>
                            <button type="submit" 
                                    class="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500">
                                Update Tasks
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Handle form submission
    document.getElementById('bulkUpdateForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performBulkUpdate();
    });
}

function closeBulkUpdateModal() {
    const modal = document.getElementById('bulkUpdateModal');
    if (modal) {
        modal.remove();
    }
}

function performBulkUpdate() {
    const selectedIds = Array.from(selectedTasks);
    const formData = new FormData(document.getElementById('bulkUpdateForm'));
    
    const updateData = {
        task_ids: selectedIds,
        status: formData.get('status') || null,
        priority: formData.get('priority') ? parseInt(formData.get('priority')) : null,
        assigned_to: formData.get('assigned_to') || null,
        description: formData.get('description') || null
    };
    
    // Remove null values
    Object.keys(updateData).forEach(key => {
        if (updateData[key] === null || updateData[key] === '') {
            delete updateData[key];
        }
    });
    
    if (Object.keys(updateData).length <= 1) { // Only task_ids
        showToast('Please select at least one field to update', 'warning');
        return;
    }
    
    // Show loading state
    const submitBtn = document.querySelector('#bulkUpdateForm button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Updating...';
    submitBtn.disabled = true;
    
    fetch('/tasks/bulk-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            closeBulkUpdateModal();
            // Refresh the page to show updated data
            window.location.reload();
        } else {
            showToast(data.error || 'Update failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred during bulk update', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Bulk delete modal
function showBulkDeleteModal() {
    const selectedIds = Array.from(selectedTasks);
    if (selectedIds.length === 0) {
        showToast('Please select tasks to delete', 'warning');
        return;
    }
    
    // Create modal HTML
    const modalHtml = `
        <div id="bulkDeleteModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                        <i class="bi bi-exclamation-triangle text-red-600 text-xl"></i>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Delete Tasks</h3>
                    <p class="text-sm text-gray-500 mb-4">
                        Are you sure you want to delete <strong>${selectedIds.length}</strong> selected tasks? 
                        This action cannot be undone.
                    </p>
                    
                    <div class="flex justify-end space-x-3">
                        <button type="button" onclick="closeBulkDeleteModal()" 
                                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500">
                            Cancel
                        </button>
                        <button type="button" onclick="performBulkDelete()" 
                                class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500">
                            Delete Tasks
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function closeBulkDeleteModal() {
    const modal = document.getElementById('bulkDeleteModal');
    if (modal) {
        modal.remove();
    }
}

function performBulkDelete() {
    const selectedIds = Array.from(selectedTasks);
    
    // Show loading state
    const deleteBtn = document.querySelector('#bulkDeleteModal button[onclick="performBulkDelete()"]');
    const originalText = deleteBtn.textContent;
    deleteBtn.textContent = 'Deleting...';
    deleteBtn.disabled = true;
    
    fetch('/tasks/bulk-delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task_ids: selectedIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            closeBulkDeleteModal();
            // Refresh the page to show updated data
            window.location.reload();
        } else {
            showToast(data.error || 'Delete failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred during bulk delete', 'error');
    })
    .finally(() => {
        deleteBtn.textContent = originalText;
        deleteBtn.disabled = false;
    });
}

// Work Item bulk operations (similar to tasks)
function showWorkItemBulkUpdateModal() {
    const selectedIds = Array.from(selectedWorkItems);
    if (selectedIds.length === 0) {
        showToast('Please select work items to update', 'warning');
        return;
    }
    
    // Create modal HTML for work items
    const modalHtml = `
        <div id="bulkUpdateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Bulk Update Work Items</h3>
                    <p class="text-sm text-gray-500 mb-4">Update ${selectedIds.length} selected work items</p>
                    
                    <form id="bulkUpdateForm">
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Status</label>
                                <select name="status" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500">
                                    <option value="">No change</option>
                                    <option value="draft">Draft</option>
                                    <option value="ready">Ready</option>
                                    <option value="active">Active</option>
                                    <option value="review">Review</option>
                                    <option value="blocked">Blocked</option>
                                    <option value="done">Done</option>
                                    <option value="archived">Archived</option>
                                    <option value="cancelled">Cancelled</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Priority</label>
                                <select name="priority" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500">
                                    <option value="">No change</option>
                                    <option value="1">Priority 1 (Highest)</option>
                                    <option value="2">Priority 2</option>
                                    <option value="3">Priority 3</option>
                                    <option value="4">Priority 4</option>
                                    <option value="5">Priority 5 (Lowest)</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Phase</label>
                                <select name="phase" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500">
                                    <option value="">No change</option>
                                    <option value="D1_discovery">D1 - Discovery</option>
                                    <option value="P1_plan">P1 - Plan</option>
                                    <option value="I1_implementation">I1 - Implementation</option>
                                    <option value="R1_review">R1 - Review</option>
                                    <option value="O1_operations">O1 - Operations</option>
                                    <option value="E1_evolution">E1 - Evolution</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Description</label>
                                <textarea name="description" rows="3" placeholder="New description or leave empty" 
                                          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"></textarea>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3 mt-6">
                            <button type="button" onclick="closeBulkUpdateModal()" 
                                    class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500">
                                Cancel
                            </button>
                            <button type="submit" 
                                    class="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500">
                                Update Work Items
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Handle form submission
    document.getElementById('bulkUpdateForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performWorkItemBulkUpdate();
    });
}

function performWorkItemBulkUpdate() {
    const selectedIds = Array.from(selectedWorkItems);
    const formData = new FormData(document.getElementById('bulkUpdateForm'));
    
    const updateData = {
        work_item_ids: selectedIds,
        status: formData.get('status') || null,
        priority: formData.get('priority') ? parseInt(formData.get('priority')) : null,
        phase: formData.get('phase') || null,
        description: formData.get('description') || null
    };
    
    // Remove null values
    Object.keys(updateData).forEach(key => {
        if (updateData[key] === null || updateData[key] === '') {
            delete updateData[key];
        }
    });
    
    if (Object.keys(updateData).length <= 1) { // Only work_item_ids
        showToast('Please select at least one field to update', 'warning');
        return;
    }
    
    // Show loading state
    const submitBtn = document.querySelector('#bulkUpdateForm button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Updating...';
    submitBtn.disabled = true;
    
    fetch('/work-items/bulk-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            closeBulkUpdateModal();
            // Refresh the page to show updated data
            window.location.reload();
        } else {
            showToast(data.error || 'Update failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred during bulk update', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

function showWorkItemBulkDeleteModal() {
    const selectedIds = Array.from(selectedWorkItems);
    if (selectedIds.length === 0) {
        showToast('Please select work items to delete', 'warning');
        return;
    }
    
    // Create modal HTML
    const modalHtml = `
        <div id="bulkDeleteModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                        <i class="bi bi-exclamation-triangle text-red-600 text-xl"></i>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Delete Work Items</h3>
                    <p class="text-sm text-gray-500 mb-4">
                        Are you sure you want to delete <strong>${selectedIds.length}</strong> selected work items and their associated tasks? 
                        This action cannot be undone.
                    </p>
                    
                    <div class="flex justify-end space-x-3">
                        <button type="button" onclick="closeBulkDeleteModal()" 
                                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500">
                            Cancel
                        </button>
                        <button type="button" onclick="performWorkItemBulkDelete()" 
                                class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500">
                            Delete Work Items
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function performWorkItemBulkDelete() {
    const selectedIds = Array.from(selectedWorkItems);
    
    // Show loading state
    const deleteBtn = document.querySelector('#bulkDeleteModal button[onclick="performWorkItemBulkDelete()"]');
    const originalText = deleteBtn.textContent;
    deleteBtn.textContent = 'Deleting...';
    deleteBtn.disabled = true;
    
    fetch('/work-items/bulk-delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ work_item_ids: selectedIds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            closeBulkDeleteModal();
            // Refresh the page to show updated data
            window.location.reload();
        } else {
            showToast(data.error || 'Delete failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred during bulk delete', 'error');
    })
    .finally(() => {
        deleteBtn.textContent = originalText;
        deleteBtn.disabled = false;
    });
}

// Dropdown menu handlers
document.addEventListener('DOMContentLoaded', function() {
    // Export dropdown
    const exportBtn = document.getElementById('exportBtn');
    const exportMenu = document.getElementById('exportMenu');
    
    if (exportBtn && exportMenu) {
        exportBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            exportMenu.style.display = exportMenu.style.display === 'none' ? 'block' : 'none';
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            exportMenu.style.display = 'none';
        });
    }
    
    // Bulk actions dropdown
    const bulkActionsBtn = document.getElementById('bulkActionsBtn');
    const bulkActionsMenu = document.getElementById('bulkActionsMenu');
    
    if (bulkActionsBtn && bulkActionsMenu) {
        bulkActionsBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            bulkActionsMenu.style.display = bulkActionsMenu.style.display === 'none' ? 'block' : 'none';
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            bulkActionsMenu.style.display = 'none';
        });
    }
});

// Toast notification function (if not already defined)
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white max-w-sm transform transition-all duration-300 translate-x-full`;
    
    // Set color based on type
    switch (type) {
        case 'success':
            toast.classList.add('bg-green-500');
            break;
        case 'error':
            toast.classList.add('bg-red-500');
            break;
        case 'warning':
            toast.classList.add('bg-yellow-500');
            break;
        default:
            toast.classList.add('bg-blue-500');
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 5000);
}
