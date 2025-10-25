/**
 * Enhanced Interactions & Micro-Interactions for APM (Agent Project Manager)
 * 
 * Features:
 * - Smooth page transitions with HTMX
 * - Enhanced hover effects and micro-interactions
 * - Loading animations and skeleton screens
 * - Progress indicators with animations
 * - Breadcrumb animations
 * - Card hover states with depth
 * - Button feedback and ripple effects
 * - Form transitions and validation feedback
 * - Skeleton loading states
 * - Page transition effects
 * 
 * @version 1.0.0
 * @author APM (Agent Project Manager) (WI-36 Task #187)
 * @date 2025-10-09
 */

// ========================================
// Configuration
// ========================================

const INTERACTION_CONFIG = {
    // Animation timings
    fast: 150,
    standard: 300,
    slow: 500,
    
    // Hover effects
    hoverScale: 1.02,
    hoverLift: 4,
    
    // Loading states
    skeletonDuration: 1500,
    loadingPulseDuration: 1000,
    
    // Page transitions
    pageTransitionDuration: 300,
    
    // Ripple effects
    rippleDuration: 600
};

// ========================================
// Page Transitions
// ========================================

/**
 * Enhanced page transitions for HTMX navigation
 */
class PageTransitions {
    constructor() {
        this.init();
    }
    
    init() {
        // Listen for HTMX events
        document.body.addEventListener('htmx:beforeRequest', this.beforeRequest.bind(this));
        document.body.addEventListener('htmx:afterRequest', this.afterRequest.bind(this));
        document.body.addEventListener('htmx:beforeSwap', this.beforeSwap.bind(this));
        document.body.addEventListener('htmx:afterSwap', this.afterSwap.bind(this));
        
        // Initial page load animation
        this.animatePageLoad();
    }
    
    beforeRequest(event) {
        // Add loading state to the target element
        const target = document.querySelector(event.detail.target);
        if (target) {
            this.addLoadingState(target);
        }
    }
    
    afterRequest(event) {
        // Remove loading state
        const target = document.querySelector(event.detail.target);
        if (target) {
            this.removeLoadingState(target);
        }
    }
    
    beforeSwap(event) {
        // Fade out current content
        const target = document.querySelector(event.detail.target);
        if (target) {
            target.style.opacity = '0';
            target.style.transition = `opacity ${INTERACTION_CONFIG.pageTransitionDuration}ms ease-out`;
        }
    }
    
    afterSwap(event) {
        // Fade in new content
        const target = document.querySelector(event.detail.target);
        if (target) {
            target.style.opacity = '1';
            target.style.transition = `opacity ${INTERACTION_CONFIG.pageTransitionDuration}ms ease-in`;
            
            // Animate new content
            this.animateNewContent(target);
        }
    }
    
    animatePageLoad() {
        // Stagger animation for cards and elements
        const cards = document.querySelectorAll('.card-fade-in');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = `opacity 0.6s ease-out, transform 0.6s ease-out`;
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    animateNewContent(container) {
        // Animate new elements in the container
        const newElements = container.querySelectorAll('.card, .table, .alert');
        newElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(10px)';
            element.style.transition = `opacity 0.4s ease-out, transform 0.4s ease-out`;
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }
    
    addLoadingState(element) {
        element.classList.add('loading-state');
        element.style.position = 'relative';
        
        // Add loading overlay
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        element.appendChild(overlay);
    }
    
    removeLoadingState(element) {
        element.classList.remove('loading-state');
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// ========================================
// Enhanced Hover Effects
// ========================================

/**
 * Enhanced hover effects for cards, buttons, and interactive elements
 */
class HoverEffects {
    constructor() {
        this.init();
    }
    
    init() {
        this.enhanceCards();
        this.enhanceButtons();
        this.enhanceTables();
        this.enhanceBadges();
    }
    
    enhanceCards() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            // Add enhanced hover class if not already present
            if (!card.classList.contains('card-lift')) {
                card.classList.add('card-lift');
            }
            
            // Add depth on hover
            card.addEventListener('mouseenter', () => {
                card.style.transform = `translateY(-${INTERACTION_CONFIG.hoverLift}px) scale(${INTERACTION_CONFIG.hoverScale})`;
                card.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = '';
            });
        });
    }
    
    enhanceButtons() {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            // Add ripple effect
            this.addRippleEffect(button);
            
            // Add enhanced hover
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-1px)';
                button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
                button.style.boxShadow = '';
            });
        });
    }
    
    enhanceTables() {
        const tableRows = document.querySelectorAll('.table tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.backgroundColor = 'rgba(124, 58, 237, 0.05)';
                row.style.transform = 'scale(1.005)';
            });
            
            row.addEventListener('mouseleave', () => {
                row.style.backgroundColor = '';
                row.style.transform = 'scale(1)';
            });
        });
    }
    
    enhanceBadges() {
        const badges = document.querySelectorAll('.badge');
        badges.forEach(badge => {
            badge.addEventListener('mouseenter', () => {
                badge.style.transform = 'scale(1.1)';
                badge.style.transition = 'transform 0.2s ease';
            });
            
            badge.addEventListener('mouseleave', () => {
                badge.style.transform = 'scale(1)';
            });
        });
    }
    
    addRippleEffect(button) {
        button.addEventListener('click', (e) => {
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, INTERACTION_CONFIG.rippleDuration);
        });
    }
}

// ========================================
// Loading States & Skeleton Screens
// ========================================

/**
 * Loading states and skeleton screens for better UX
 */
class LoadingStates {
    constructor() {
        this.init();
    }
    
    init() {
        this.createSkeletonStyles();
        this.enhanceProgressBars();
    }
    
    createSkeletonStyles() {
        // Add skeleton styles if not already present
        if (!document.getElementById('skeleton-styles')) {
            const style = document.createElement('style');
            style.id = 'skeleton-styles';
            style.textContent = `
                .skeleton {
                    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                    background-size: 200% 100%;
                    animation: skeletonShimmer 1.5s infinite;
                    border-radius: 4px;
                }
                
                .skeleton-text {
                    height: 1rem;
                    margin-bottom: 0.5rem;
                }
                
                .skeleton-text:last-child {
                    width: 60%;
                }
                
                .skeleton-avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                }
                
                .skeleton-card {
                    padding: 1rem;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }
                
                .loading-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10;
                }
                
                .loading-spinner {
                    text-align: center;
                }
                
                @keyframes skeletonShimmer {
                    0% { background-position: 200% 0; }
                    100% { background-position: -200% 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    showSkeleton(container, type = 'card') {
        const skeleton = document.createElement('div');
        skeleton.className = `skeleton-${type}`;
        
        if (type === 'card') {
            skeleton.innerHTML = `
                <div class="skeleton skeleton-avatar mb-3"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
            `;
        } else if (type === 'table') {
            skeleton.innerHTML = `
                <div class="skeleton skeleton-text mb-2"></div>
                <div class="skeleton skeleton-text mb-2"></div>
                <div class="skeleton skeleton-text mb-2"></div>
            `;
        }
        
        container.innerHTML = '';
        container.appendChild(skeleton);
    }
    
    hideSkeleton(container) {
        const skeleton = container.querySelector('.skeleton-card, .skeleton-table');
        if (skeleton) {
            skeleton.style.opacity = '0';
            skeleton.style.transition = 'opacity 0.3s ease-out';
            setTimeout(() => {
                skeleton.remove();
            }, 300);
        }
    }
    
    enhanceProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            // Add fill animation
            const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            bar.style.transition = 'width 1s ease-out';
            
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
            
            // Add shimmer effect for active progress
            if (bar.getAttribute('aria-valuenow') < 100) {
                bar.classList.add('progress-shimmer');
            }
        });
    }
}

// ========================================
// Form Enhancements
// ========================================

/**
 * Enhanced form interactions and validation feedback
 */
class FormEnhancements {
    constructor() {
        this.init();
    }
    
    init() {
        this.enhanceInputs();
        this.enhanceSelects();
        this.enhanceCheckboxes();
    }
    
    enhanceInputs() {
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            // Focus glow effect
            input.addEventListener('focus', () => {
                input.style.boxShadow = '0 0 0 3px rgba(124, 58, 237, 0.25)';
                input.style.borderColor = '#7C3AED';
            });
            
            input.addEventListener('blur', () => {
                input.style.boxShadow = '';
                input.style.borderColor = '';
            });
            
            // Real-time validation feedback
            input.addEventListener('input', () => {
                this.validateInput(input);
            });
        });
    }
    
    enhanceSelects() {
        const selects = document.querySelectorAll('.form-select');
        selects.forEach(select => {
            select.addEventListener('change', () => {
                // Add selection animation
                select.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    select.style.transform = 'scale(1)';
                }, 150);
            });
        });
    }
    
    enhanceCheckboxes() {
        const checkboxes = document.querySelectorAll('.form-check-input');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // Add check animation
                const label = checkbox.closest('.form-check');
                if (checkbox.checked) {
                    label.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        label.style.transform = 'scale(1)';
                    }, 200);
                }
            });
        });
    }
    
    validateInput(input) {
        const value = input.value.trim();
        const isValid = value.length > 0;
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    }
}

// ========================================
// Breadcrumb Animations
// ========================================

/**
 * Enhanced breadcrumb animations
 */
class BreadcrumbAnimations {
    constructor() {
        this.init();
    }
    
    init() {
        const breadcrumbs = document.querySelectorAll('.breadcrumb-item');
        breadcrumbs.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-10px)';
            item.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
            
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }
}

// ========================================
// Micro-Interactions
// ========================================

/**
 * Micro-interactions for enhanced user feedback
 */
class MicroInteractions {
    constructor() {
        this.init();
    }
    
    init() {
        this.enhanceIcons();
        this.enhanceLinks();
        this.addClickFeedback();
    }
    
    enhanceIcons() {
        const icons = document.querySelectorAll('.bi');
        icons.forEach(icon => {
            icon.addEventListener('mouseenter', () => {
                icon.style.transform = 'scale(1.2)';
                icon.style.transition = 'transform 0.2s ease';
            });
            
            icon.addEventListener('mouseleave', () => {
                icon.style.transform = 'scale(1)';
            });
        });
    }
    
    enhanceLinks() {
        const links = document.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.style.textDecoration = 'none';
                link.style.transform = 'translateY(-1px)';
            });
            
            link.addEventListener('mouseleave', () => {
                link.style.transform = 'translateY(0)';
            });
        });
    }
    
    addClickFeedback() {
        const clickableElements = document.querySelectorAll('.btn, .card, .nav-link, .dropdown-item');
        clickableElements.forEach(element => {
            element.addEventListener('click', () => {
                element.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 100);
            });
        });
    }
}

// ========================================
// Initialize All Enhancements
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhancement classes
    new PageTransitions();
    new HoverEffects();
    new LoadingStates();
    new FormEnhancements();
    new BreadcrumbAnimations();
    new MicroInteractions();
    
    // Add ripple effect styles
    const rippleStyles = document.createElement('style');
    rippleStyles.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation ${INTERACTION_CONFIG.rippleDuration}ms ease-out;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .btn {
            position: relative;
            overflow: hidden;
        }
    `;
    document.head.appendChild(rippleStyles);
    
    console.log('🎨 Enhanced interactions initialized');
});

// ========================================
// Export for global access
// ========================================

window.AIPMInteractions = {
    PageTransitions,
    HoverEffects,
    LoadingStates,
    FormEnhancements,
    BreadcrumbAnimations,
    MicroInteractions
};

