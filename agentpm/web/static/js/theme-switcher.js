/**
 * APM (Agent Project Manager) Theme Switcher
 * Handles theme switching with persistence and system preference detection
 * 
 * Features:
 * - Multiple theme support (light, dark, royal, modern)
 * - Local storage persistence
 * - System preference detection
 * - Smooth transitions
 * - Theme preview mode
 * 
 * @version 1.0.0
 * @author APM (Agent Project Manager)
 */

class ThemeSwitcher {
  constructor() {
    this.themes = ['light', 'dark', 'royal', 'modern'];
    this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
    this.isPreviewMode = false;
    this.previewTheme = null;
    
    this.init();
  }

  /**
   * Initialize the theme switcher
   */
  init() {
    this.applyTheme(this.currentTheme);
    this.setupEventListeners();
    this.setupSystemThemeListener();
    this.updateThemeSelectors();
  }

  /**
   * Get stored theme from localStorage
   */
  getStoredTheme() {
    try {
      return localStorage.getItem('aipm-theme');
    } catch (error) {
      console.warn('Could not access localStorage:', error);
      return null;
    }
  }

  /**
   * Get system theme preference
   */
  getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Store theme in localStorage
   */
  storeTheme(theme) {
    try {
      localStorage.setItem('aipm-theme', theme);
    } catch (error) {
      console.warn('Could not store theme in localStorage:', error);
    }
  }

  /**
   * Apply theme to document
   */
  applyTheme(theme) {
    if (!this.themes.includes(theme)) {
      console.warn(`Invalid theme: ${theme}`);
      return;
    }

    // Remove existing theme classes
    this.themes.forEach(t => {
      document.documentElement.classList.remove(`theme-${t}`);
    });

    // Add new theme class
    document.documentElement.classList.add(`theme-${theme}`);

    // Update meta theme-color for mobile browsers
    this.updateMetaThemeColor(theme);

    // Update theme selectors if not in preview mode
    if (!this.isPreviewMode) {
      this.currentTheme = theme;
      this.storeTheme(theme);
      this.updateThemeSelectors();
    }
  }

  /**
   * Update meta theme-color for mobile browsers
   */
  updateMetaThemeColor(theme) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }

    const themeColors = {
      light: '#ffffff',
      dark: '#111827',
      royal: '#7c3aed',
      modern: '#3b82f6'
    };

    metaThemeColor.content = themeColors[theme] || themeColors.light;
  }

  /**
   * Switch to a specific theme
   */
  switchTheme(theme) {
    if (this.isPreviewMode) {
      this.previewTheme = theme;
    }
    this.applyTheme(theme);
  }

  /**
   * Preview a theme without applying it
   */
  previewTheme(theme) {
    if (!this.themes.includes(theme)) {
      console.warn(`Invalid theme: ${theme}`);
      return;
    }

    this.isPreviewMode = true;
    this.previewTheme = theme;
    this.applyTheme(theme);
  }

  /**
   * Cancel theme preview and revert to current theme
   */
  cancelPreview() {
    if (this.isPreviewMode) {
      this.isPreviewMode = false;
      this.previewTheme = null;
      this.applyTheme(this.currentTheme);
    }
  }

  /**
   * Confirm theme preview and make it permanent
   */
  confirmPreview() {
    if (this.isPreviewMode && this.previewTheme) {
      this.currentTheme = this.previewTheme;
      this.storeTheme(this.previewTheme);
      this.isPreviewMode = false;
      this.previewTheme = null;
      this.updateThemeSelectors();
    }
  }

  /**
   * Toggle between light and dark themes
   */
  toggleDarkMode() {
    const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.switchTheme(newTheme);
  }

  /**
   * Cycle through all themes
   */
  cycleThemes() {
    const currentIndex = this.themes.indexOf(this.currentTheme);
    const nextIndex = (currentIndex + 1) % this.themes.length;
    this.switchTheme(this.themes[nextIndex]);
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * Get available themes
   */
  getAvailableThemes() {
    return [...this.themes];
  }

  /**
   * Check if theme is currently being previewed
   */
  isPreviewing() {
    return this.isPreviewMode;
  }

  /**
   * Setup event listeners for theme switching
   */
  setupEventListeners() {
    // Listen for theme selector changes
    document.addEventListener('change', (event) => {
      if (event.target.matches('[data-theme-selector]')) {
        const theme = event.target.value;
        if (event.target.dataset.preview === 'true') {
          this.previewTheme(theme);
        } else {
          this.switchTheme(theme);
        }
      }
    });

    // Listen for theme toggle buttons
    document.addEventListener('click', (event) => {
      if (event.target.matches('[data-theme-toggle]')) {
        const theme = event.target.dataset.theme;
        if (theme) {
          this.switchTheme(theme);
        } else if (event.target.dataset.toggle === 'dark') {
          this.toggleDarkMode();
        } else if (event.target.dataset.toggle === 'cycle') {
          this.cycleThemes();
        }
      }
    });

    // Listen for preview controls
    document.addEventListener('click', (event) => {
      if (event.target.matches('[data-theme-preview]')) {
        const theme = event.target.dataset.theme;
        this.previewTheme(theme);
      } else if (event.target.matches('[data-theme-cancel]')) {
        this.cancelPreview();
      } else if (event.target.matches('[data-theme-confirm]')) {
        this.confirmPreview();
      }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
      // Ctrl/Cmd + Shift + T to cycle themes
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
        event.preventDefault();
        this.cycleThemes();
      }
      
      // Ctrl/Cmd + Shift + D to toggle dark mode
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'D') {
        event.preventDefault();
        this.toggleDarkMode();
      }
    });
  }

  /**
   * Setup system theme change listener
   */
  setupSystemThemeListener() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleSystemThemeChange = (e) => {
        // Only auto-switch if user hasn't manually set a theme
        const storedTheme = this.getStoredTheme();
        if (!storedTheme) {
          const systemTheme = e.matches ? 'dark' : 'light';
          this.switchTheme(systemTheme);
        }
      };

      // Modern browsers
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemThemeChange);
      } else {
        // Legacy browsers
        mediaQuery.addListener(handleSystemThemeChange);
      }
    }
  }

  /**
   * Update theme selector elements
   */
  updateThemeSelectors() {
    const selectors = document.querySelectorAll('[data-theme-selector]');
    selectors.forEach(selector => {
      selector.value = this.currentTheme;
    });

    // Update theme toggle buttons
    const toggles = document.querySelectorAll('[data-theme-toggle]');
    toggles.forEach(toggle => {
      const theme = toggle.dataset.theme;
      if (theme === this.currentTheme) {
        toggle.classList.add('active');
        toggle.setAttribute('aria-pressed', 'true');
      } else {
        toggle.classList.remove('active');
        toggle.setAttribute('aria-pressed', 'false');
      }
    });

    // Update theme indicator
    const indicators = document.querySelectorAll('[data-theme-indicator]');
    indicators.forEach(indicator => {
      indicator.textContent = this.currentTheme;
      indicator.className = `theme-indicator theme-${this.currentTheme}`;
    });
  }

  /**
   * Create theme selector HTML
   */
  createThemeSelector(options = {}) {
    const {
      includePreview = false,
      showLabels = true,
      className = 'theme-selector'
    } = options;

    const themeLabels = {
      light: 'Light',
      dark: 'Dark',
      royal: 'Royal',
      modern: 'Modern'
    };

    let html = `<select class="${className}" data-theme-selector>`;
    
    this.themes.forEach(theme => {
      const label = showLabels ? themeLabels[theme] || theme : theme;
      html += `<option value="${theme}">${label}</option>`;
    });
    
    html += '</select>';

    if (includePreview) {
      html += `
        <div class="theme-preview-controls">
          <button type="button" data-theme-cancel class="btn btn-sm btn-outline-secondary">
            Cancel
          </button>
          <button type="button" data-theme-confirm class="btn btn-sm btn-primary">
            Apply
          </button>
        </div>
      `;
    }

    return html;
  }

  /**
   * Create theme toggle buttons HTML
   */
  createThemeToggles(options = {}) {
    const {
      showLabels = true,
      className = 'theme-toggles'
    } = options;

    const themeLabels = {
      light: 'Light',
      dark: 'Dark',
      royal: 'Royal',
      modern: 'Modern'
    };

    let html = `<div class="${className}">`;
    
    this.themes.forEach(theme => {
      const label = showLabels ? themeLabels[theme] || theme : theme;
      const isActive = theme === this.currentTheme ? 'active' : '';
      html += `
        <button 
          type="button" 
          class="btn btn-sm btn-outline-primary theme-toggle ${isActive}"
          data-theme-toggle 
          data-theme="${theme}"
          aria-pressed="${theme === this.currentTheme}"
        >
          ${label}
        </button>
      `;
    });
    
    html += '</div>';
    return html;
  }
}

// Initialize theme switcher when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.themeSwitcher = new ThemeSwitcher();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeSwitcher;
}
