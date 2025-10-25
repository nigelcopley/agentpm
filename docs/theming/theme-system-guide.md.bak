# APM (Agent Project Manager) Theme System Guide

A comprehensive theme system built with Tailwind CSS v4 patterns, providing multiple theme variants, consistent design tokens, and seamless theme switching capabilities.

## Table of Contents

- [Overview](#overview)
- [Theme Variants](#theme-variants)
- [Getting Started](#getting-started)
- [Theme Switching](#theme-switching)
- [Component Usage](#component-usage)
- [Customization](#customization)
- [Accessibility](#accessibility)
- [Best Practices](#best-practices)

## Overview

The APM (Agent Project Manager) theme system is built using Tailwind CSS v4's `@theme` directive, providing:

- **Multiple Theme Variants**: Light, Dark, Royal, and Modern themes
- **CSS-First Configuration**: All theming done via CSS custom properties
- **Semantic Design Tokens**: Consistent color, spacing, and typography scales
- **Theme Switching**: Runtime theme switching with persistence
- **Accessibility**: WCAG 2.1 AA compliant contrast ratios
- **Responsive Design**: Mobile-first responsive utilities

## Theme Variants

### Light Theme (Default)
Clean, professional design with high contrast and excellent readability.

```css
/* Primary: Indigo (#6366f1) */
/* Secondary: Purple (#8b5cf6) */
/* Accent: Pink (#ec4899) */
```

### Dark Theme
Modern dark interface with reduced eye strain for low-light environments.

```css
/* Inverted color scales for dark backgrounds */
/* Maintains accessibility standards */
```

### Royal Theme
Premium design with royal purple and gold accents for executive interfaces.

```css
/* Primary: Royal Purple (#7c3aed) */
/* Secondary: Gold (#f59e0b) */
/* Accent: Deep Purple (#9333ea) */
```

### Modern Theme
Contemporary design with blue and teal accents for modern applications.

```css
/* Primary: Modern Blue (#3b82f6) */
/* Secondary: Teal (#14b8a6) */
/* Accent: Violet (#8b5cf6) */
```

## Getting Started

### 1. Include Theme CSS

```html
<!-- Include the theme system CSS -->
<link rel="stylesheet" href="/static/css/theme-system.css">
<link rel="stylesheet" href="/static/css/components.css">
```

### 2. Include Theme Switcher JavaScript

```html
<!-- Include the theme switcher -->
<script src="/static/js/theme-switcher.js"></script>
```

### 3. Basic HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APM (Agent Project Manager)</title>
    <link rel="stylesheet" href="/static/css/theme-system.css">
    <link rel="stylesheet" href="/static/css/components.css">
</head>
<body class="bg-surface-primary text-text-primary">
    <!-- Your content here -->
    <script src="/static/js/theme-switcher.js"></script>
</body>
</html>
```

## Theme Switching

### Automatic Theme Detection

The theme switcher automatically detects system preferences and applies the appropriate theme:

```javascript
// System preference detection
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
// Automatically applies 'dark' or 'light' theme
```

### Manual Theme Switching

```javascript
// Switch to a specific theme
window.themeSwitcher.switchTheme('royal');

// Toggle between light and dark
window.themeSwitcher.toggleDarkMode();

// Cycle through all themes
window.themeSwitcher.cycleThemes();
```

### Theme Persistence

Themes are automatically saved to localStorage and restored on page load:

```javascript
// Get current theme
const currentTheme = window.themeSwitcher.getCurrentTheme();

// Check if previewing
const isPreviewing = window.themeSwitcher.isPreviewing();
```

### HTML Theme Controls

#### Theme Selector Dropdown

```html
<select data-theme-selector class="theme-selector">
    <option value="light">Light</option>
    <option value="dark">Dark</option>
    <option value="royal">Royal</option>
    <option value="modern">Modern</option>
</select>
```

#### Theme Toggle Buttons

```html
<div class="theme-toggles">
    <button data-theme-toggle data-theme="light" class="theme-toggle">Light</button>
    <button data-theme-toggle data-theme="dark" class="theme-toggle">Dark</button>
    <button data-theme-toggle data-theme="royal" class="theme-toggle">Royal</button>
    <button data-theme-toggle data-theme="modern" class="theme-toggle">Modern</button>
</div>
```

#### Dark Mode Toggle

```html
<button data-theme-toggle data-toggle="dark" class="btn btn-outline-primary">
    Toggle Dark Mode
</button>
```

### Keyboard Shortcuts

- `Ctrl/Cmd + Shift + T`: Cycle through themes
- `Ctrl/Cmd + Shift + D`: Toggle dark mode

## Component Usage

### Buttons

```html
<!-- Primary Button -->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Secondary Action</button>

<!-- Outline Button -->
<button class="btn btn-outline-primary">Outline Button</button>

<!-- Ghost Button -->
<button class="btn btn-ghost">Ghost Button</button>

<!-- Button Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
```

### Cards

```html
<!-- Basic Card -->
<div class="card">
    <div class="card-body">
        <h3 class="card-title">Card Title</h3>
        <p class="card-description">Card description text.</p>
    </div>
</div>

<!-- Elevated Card -->
<div class="card card-elevated">
    <div class="card-header">
        <h3 class="card-title">Header</h3>
    </div>
    <div class="card-body">
        <p>Card content goes here.</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>

<!-- Interactive Card -->
<div class="card card-interactive">
    <div class="card-body">
        <h3 class="card-title">Clickable Card</h3>
        <p>This card has hover effects.</p>
    </div>
</div>
```

### Forms

```html
<!-- Form Group -->
<div class="form-group">
    <label class="form-label" for="email">Email Address</label>
    <input type="email" id="email" class="form-input" placeholder="Enter your email">
    <div class="form-help">We'll never share your email.</div>
</div>

<!-- Form with Error -->
<div class="form-group">
    <label class="form-label" for="password">Password</label>
    <input type="password" id="password" class="form-input form-input-error">
    <div class="form-error">Password is required.</div>
</div>

<!-- Form Switch -->
<div class="form-group">
    <label class="form-label">Enable notifications</label>
    <div class="form-switch">
        <input type="checkbox" class="sr-only">
        <div class="form-switch-thumb"></div>
    </div>
</div>
```

### Badges

```html
<!-- Status Badges -->
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>

<!-- AIPM Phase Badges -->
<span class="phase-badge phase-badge-d1">Discovery</span>
<span class="phase-badge phase-badge-p1">Planning</span>
<span class="phase-badge phase-badge-i1">Implementation</span>
<span class="phase-badge phase-badge-r1">Review</span>
<span class="phase-badge phase-badge-o1">Operations</span>
<span class="phase-badge phase-badge-e1">Evolution</span>

<!-- Confidence Indicators -->
<span class="confidence-indicator confidence-high">High Confidence</span>
<span class="confidence-indicator confidence-medium">Medium Confidence</span>
<span class="confidence-indicator confidence-low">Low Confidence</span>
```

### Alerts

```html
<!-- Success Alert -->
<div class="alert alert-success">
    <div class="alert-title">Success!</div>
    <div class="alert-description">Your changes have been saved.</div>
</div>

<!-- Warning Alert -->
<div class="alert alert-warning">
    <div class="alert-title">Warning</div>
    <div class="alert-description">Please review your input.</div>
</div>

<!-- Error Alert -->
<div class="alert alert-error">
    <div class="alert-title">Error</div>
    <div class="alert-description">Something went wrong.</div>
</div>
```

### Navigation

```html
<!-- Horizontal Navigation -->
<nav class="nav">
    <div class="nav-item">
        <a href="#" class="nav-link nav-link-active">Dashboard</a>
    </div>
    <div class="nav-item">
        <a href="#" class="nav-link">Projects</a>
    </div>
    <div class="nav-item">
        <a href="#" class="nav-link">Settings</a>
    </div>
</nav>

<!-- Vertical Navigation -->
<nav class="nav nav-vertical">
    <div class="nav-item">
        <a href="#" class="nav-link nav-link-active">Dashboard</a>
    </div>
    <div class="nav-item">
        <a href="#" class="nav-link">Projects</a>
    </div>
    <div class="nav-item">
        <a href="#" class="nav-link">Settings</a>
    </div>
</nav>
```

### Tables

```html
<div class="table-container">
    <table class="table">
        <thead class="table-header">
            <tr>
                <th class="table-header-cell">Name</th>
                <th class="table-header-cell">Status</th>
                <th class="table-header-cell">Date</th>
            </tr>
        </thead>
        <tbody class="table-body">
            <tr class="table-row">
                <td class="table-cell">John Doe</td>
                <td class="table-cell">
                    <span class="badge badge-success">Active</span>
                </td>
                <td class="table-cell table-cell-secondary">2024-01-15</td>
            </tr>
        </tbody>
    </table>
</div>
```

### Modals

```html
<!-- Modal Overlay -->
<div class="modal-overlay">
    <div class="modal">
        <div class="modal-header">
            <h3 class="modal-title">Modal Title</h3>
            <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
            <p>Modal content goes here.</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-outline-secondary">Cancel</button>
            <button class="btn btn-primary">Save</button>
        </div>
    </div>
</div>
```

### Progress Bars

```html
<!-- Basic Progress -->
<div class="progress">
    <div class="progress-bar progress-bar-primary" style="width: 75%"></div>
</div>

<!-- Progress with Label -->
<div class="progress progress-lg">
    <div class="progress-bar progress-bar-success" style="width: 60%">60%</div>
</div>
```

### Loading States

```html
<!-- Spinner -->
<div class="loading-spinner"></div>

<!-- Loading Dots -->
<div class="loading-dots">
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
    <div class="loading-dot"></div>
</div>
```

## Customization

### Creating Custom Themes

To create a custom theme, add a new `@theme` block:

```css
@theme custom {
  /* Primary Colors */
  --color-primary-50: 240 253 244;
  --color-primary-100: 220 252 231;
  --color-primary-200: 187 247 208;
  --color-primary-300: 134 239 172;
  --color-primary-400: 74 222 128;
  --color-primary-500: 34 197 94;
  --color-primary-600: 22 163 74;
  --color-primary-700: 21 128 61;
  --color-primary-800: 22 101 52;
  --color-primary-900: 20 83 45;
  
  /* Add other color scales... */
}
```

### Extending Component Styles

```css
/* Custom button variant */
.btn-custom {
  @apply bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600;
}

/* Custom card variant */
.card-gradient {
  @apply bg-gradient-to-br from-primary-50 to-secondary-50 border-primary-200;
}
```

### Custom Design Tokens

```css
@theme {
  /* Custom spacing */
  --spacing-custom: 2.5rem;
  
  /* Custom border radius */
  --radius-custom: 1.25rem;
  
  /* Custom shadows */
  --shadow-custom: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
```

## Accessibility

### Color Contrast

All themes meet WCAG 2.1 AA contrast requirements:

- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text**: 3:1 minimum contrast ratio
- **UI components**: 3:1 minimum contrast ratio

### Focus Management

```css
/* Focus styles are automatically applied */
.focus-visible {
  @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
}
```

### Screen Reader Support

```html
<!-- Screen reader only text -->
<span class="sr-only">Screen reader only content</span>

<!-- Proper labeling -->
<label for="input-id" class="form-label">Label Text</label>
<input id="input-id" class="form-input" aria-describedby="help-text">
<div id="help-text" class="form-help">Help text</div>
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}
```

## Best Practices

### 1. Use Semantic Classes

```html
<!-- Good: Semantic and theme-aware -->
<button class="btn btn-primary">Save Changes</button>

<!-- Avoid: Hard-coded colors -->
<button class="bg-blue-500 text-white">Save Changes</button>
```

### 2. Leverage Theme Tokens

```html
<!-- Good: Uses theme tokens -->
<div class="bg-surface-primary text-text-primary border-border-primary">

<!-- Avoid: Hard-coded values -->
<div class="bg-white text-gray-900 border-gray-200">
```

### 3. Consistent Spacing

```html
<!-- Good: Uses consistent spacing scale -->
<div class="p-4 mb-6 space-y-4">

<!-- Avoid: Arbitrary spacing -->
<div class="p-3.5 mb-7 space-y-3.5">
```

### 4. Responsive Design

```html
<!-- Good: Mobile-first responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

<!-- Avoid: Desktop-first -->
<div class="grid grid-cols-3 md:grid-cols-2 sm:grid-cols-1 gap-4">
```

### 5. Theme Testing

Always test components across all theme variants:

```javascript
// Test all themes
const themes = ['light', 'dark', 'royal', 'modern'];
themes.forEach(theme => {
  window.themeSwitcher.switchTheme(theme);
  // Test component appearance
});
```

### 6. Performance Considerations

- Use CSS custom properties for theme switching (no JavaScript required)
- Minimize theme-specific overrides
- Leverage Tailwind's utility classes for consistency

## Troubleshooting

### Common Issues

1. **Theme not applying**: Ensure the theme CSS is loaded before component CSS
2. **Colors not updating**: Check that CSS custom properties are properly defined
3. **JavaScript errors**: Verify the theme switcher script is loaded

### Debug Mode

Enable debug mode to see theme information:

```javascript
// Enable debug logging
window.themeSwitcher.debug = true;
```

### Browser Support

- **Modern browsers**: Full support
- **IE11**: Limited support (fallback to light theme)
- **Mobile browsers**: Full support with theme-color meta tag

## Migration Guide

### From Tailwind v3

1. Replace `tailwind.config.js` color definitions with `@theme` blocks
2. Update color references to use CSS custom properties
3. Replace hard-coded colors with semantic classes

### From Custom CSS

1. Map existing color variables to theme tokens
2. Replace component styles with utility classes
3. Update JavaScript theme switching logic

## Contributing

When contributing to the theme system:

1. Follow the established color scale patterns
2. Ensure accessibility compliance
3. Test across all theme variants
4. Update documentation for new features
5. Maintain backward compatibility

## Resources

- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Custom Properties Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
