/**
 * Markdown Enhancement JavaScript for APM (Agent Project Manager) Web Application
 * Provides interactive features for enhanced markdown rendering
 */

// Copy to clipboard functionality for code blocks
function copyToClipboard(button) {
    const codeContent = button.getAttribute('data-code');
    
    // Create a temporary textarea to copy the text
    const textarea = document.createElement('textarea');
    textarea.value = codeContent;
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        // Copy the text to clipboard
        document.execCommand('copy');
        
        // Show success feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="bi bi-check mr-1"></i>Copied!';
        button.classList.remove('hover:bg-gray-700');
        button.classList.add('bg-green-600', 'hover:bg-green-700');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-green-600', 'hover:bg-green-700');
            button.classList.add('hover:bg-gray-700');
        }, 2000);
        
    } catch (err) {
        console.error('Failed to copy text: ', err);
        
        // Show error feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="bi bi-x mr-1"></i>Failed';
        button.classList.remove('hover:bg-gray-700');
        button.classList.add('bg-red-600', 'hover:bg-red-700');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('bg-red-600', 'hover:bg-red-700');
            button.classList.add('hover:bg-gray-700');
        }, 2000);
    } finally {
        // Clean up
        document.body.removeChild(textarea);
    }
}

// Smooth scrolling for table of contents links
function initSmoothScrolling() {
    const tocLinks = document.querySelectorAll('.prose a[href^="#"]');
    
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL without triggering scroll
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });
}

// Initialize markdown enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSmoothScrolling();
    
    // Add syntax highlighting if Prism.js is available
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
});

// Export functions for global access
window.copyToClipboard = copyToClipboard;
window.initSmoothScrolling = initSmoothScrolling;
