/**
 * Alpine.js Tooltip Directive
 *
 * Provides accessible, keyboard-friendly tooltips via custom Alpine.js directive.
 * WCAG 2.1 AA compliant with keyboard navigation and ARIA support.
 *
 * Usage:
 * <button x-tooltip="'Tooltip text'">Hover me</button>
 * <button x-tooltip.bottom="'Bottom positioned'">Click me</button>
 * <button x-tooltip.delay.500="'500ms delay'">Long hover</button>
 * <button x-tooltip.multiline="'Line 1\nLine 2'">Multiple lines</button>
 *
 * Positions: top (default), bottom, left, right
 * Modifiers: delay.{ms}, multiline
 *
 * @requires Alpine.js 3.x
 */

document.addEventListener('alpine:init', () => {
  Alpine.directive('tooltip', (el, { expression, modifiers }, { evaluate, cleanup }) => {
    // Evaluate tooltip content
    const content = evaluate(expression);

    if (!content) {
      console.warn('Tooltip directive requires content expression', el);
      return;
    }

    // Configuration from modifiers
    const position = ['top', 'bottom', 'left', 'right'].find(p => modifiers.includes(p)) || 'top';
    const multiline = modifiers.includes('multiline');

    // Delay in milliseconds (default: 300ms)
    let delay = 300;
    if (modifiers.includes('delay')) {
      const delayIndex = modifiers.indexOf('delay');
      const delayValue = parseInt(modifiers[delayIndex + 1]);
      if (!isNaN(delayValue)) {
        delay = delayValue;
      }
    }

    // State
    let tooltipEl = null;
    let showTimeout = null;
    let hideTimeout = null;
    let isVisible = false;

    /**
     * Create tooltip element and append to trigger
     */
    function createTooltip() {
      if (tooltipEl) return; // Already created

      tooltipEl = document.createElement('div');
      tooltipEl.className = 'tooltip-content';
      if (multiline) {
        tooltipEl.classList.add('tooltip-multiline');
      }
      tooltipEl.setAttribute('data-position', position);
      tooltipEl.setAttribute('role', 'tooltip');
      tooltipEl.setAttribute('aria-hidden', 'true');

      // Handle multiline content (newlines)
      if (multiline && content.includes('\n')) {
        const lines = content.split('\n');
        lines.forEach((line, index) => {
          if (index > 0) tooltipEl.appendChild(document.createElement('br'));
          tooltipEl.appendChild(document.createTextNode(line));
        });
      } else {
        tooltipEl.textContent = content;
      }

      // Add tooltip trigger class to parent
      el.classList.add('tooltip-trigger');

      // Append to trigger element
      el.appendChild(tooltipEl);

      // Generate unique ID for ARIA relationship
      const tooltipId = `tooltip-${Math.random().toString(36).substr(2, 9)}`;
      tooltipEl.id = tooltipId;

      // Link trigger to tooltip via ARIA (accessibility)
      if (!el.hasAttribute('aria-describedby')) {
        el.setAttribute('aria-describedby', tooltipId);
      }
    }

    /**
     * Show tooltip with delay
     */
    function showTooltip() {
      clearTimeout(hideTimeout);

      showTimeout = setTimeout(() => {
        if (!tooltipEl) createTooltip();

        // Prevent showing if already visible
        if (isVisible) return;

        isVisible = true;

        // Update ARIA state
        tooltipEl.setAttribute('aria-hidden', 'false');

        // Fade in animation (handled by CSS transition)
        tooltipEl.style.display = 'block';

        // Check if tooltip overflows viewport and adjust position
        requestAnimationFrame(() => {
          adjustPositionIfNeeded();
        });
      }, delay);
    }

    /**
     * Hide tooltip with brief delay
     */
    function hideTooltip() {
      clearTimeout(showTimeout);

      if (!tooltipEl || !isVisible) return;

      hideTimeout = setTimeout(() => {
        isVisible = false;

        // Update ARIA state
        tooltipEl.setAttribute('aria-hidden', 'true');

        // Fade out (CSS handles opacity transition)
        setTimeout(() => {
          if (tooltipEl && !isVisible) {
            tooltipEl.style.display = 'none';
          }
        }, 150); // Match CSS transition duration
      }, 100); // Brief delay before hiding
    }

    /**
     * Adjust tooltip position if it overflows viewport
     * (Prevents tooltip from being cut off at screen edges)
     */
    function adjustPositionIfNeeded() {
      if (!tooltipEl) return;

      const rect = tooltipEl.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      // Check horizontal overflow
      if (rect.right > viewportWidth) {
        tooltipEl.style.left = 'auto';
        tooltipEl.style.right = '0';
      } else if (rect.left < 0) {
        tooltipEl.style.left = '0';
        tooltipEl.style.right = 'auto';
      }

      // Check vertical overflow
      if (rect.bottom > viewportHeight) {
        // Flip to top if positioned bottom
        if (position === 'bottom') {
          tooltipEl.setAttribute('data-position', 'top');
        }
      } else if (rect.top < 0) {
        // Flip to bottom if positioned top
        if (position === 'top') {
          tooltipEl.setAttribute('data-position', 'bottom');
        }
      }
    }

    /**
     * Handle keyboard Escape key to hide tooltip
     */
    function handleEscape(event) {
      if (event.key === 'Escape' && isVisible) {
        hideTooltip();
      }
    }

    // Event listeners
    el.addEventListener('mouseenter', showTooltip);
    el.addEventListener('mouseleave', hideTooltip);
    el.addEventListener('focus', showTooltip);
    el.addEventListener('blur', hideTooltip);

    // Touch device support (tap to show/hide)
    el.addEventListener('touchstart', (e) => {
      if (isVisible) {
        hideTooltip();
      } else {
        showTooltip();
      }
    }, { passive: true });

    // Keyboard accessibility (Escape to close)
    document.addEventListener('keydown', handleEscape);

    // Cleanup on directive destruction
    cleanup(() => {
      clearTimeout(showTimeout);
      clearTimeout(hideTimeout);

      // Remove event listeners
      el.removeEventListener('mouseenter', showTooltip);
      el.removeEventListener('mouseleave', hideTooltip);
      el.removeEventListener('focus', showTooltip);
      el.removeEventListener('blur', hideTooltip);
      document.removeEventListener('keydown', handleEscape);

      // Remove tooltip element
      if (tooltipEl) {
        tooltipEl.remove();
        tooltipEl = null;
      }

      // Remove trigger class
      el.classList.remove('tooltip-trigger');
    });
  });
});

/**
 * Utility: Initialize tooltips on dynamically added elements
 *
 * Usage:
 * AIPM.tooltips.refresh();
 */
if (!window.AIPM) window.AIPM = {};
window.AIPM.tooltips = {
  /**
   * Refresh tooltips (useful after dynamic content injection)
   */
  refresh() {
    // Alpine.js handles this automatically via x-tooltip directive
    console.log('Tooltips refreshed');
  },

  /**
   * Check if tooltips are supported
   */
  isSupported() {
    return typeof Alpine !== 'undefined';
  }
};

console.log('[AIPM] Tooltip directive registered');
