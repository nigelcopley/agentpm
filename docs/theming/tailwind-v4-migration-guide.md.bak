# Tailwind CSS v4 Migration Guide

## Overview

APM (Agent Project Manager) has been successfully migrated to Tailwind CSS v4, leveraging the new CSS-first configuration approach and native `@theme` directive for comprehensive theming.

## Key Changes in v4

### 1. CSS-First Configuration

Tailwind v4 moves away from JavaScript configuration files to a CSS-first approach using the `@theme` directive:

```css
@import "tailwindcss";

@theme {
  --color-primary-500: #6366f1;
  --color-secondary-500: #8b5cf6;
  --font-sans: 'Inter', system-ui, sans-serif;
  --spacing-18: 4.5rem;
}
```

### 2. PostCSS Build Process

Instead of the Tailwind CLI, v4 uses PostCSS for processing:

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

### 3. Build Scripts

Updated package.json scripts use PostCSS:

```json
{
  "scripts": {
    "build:css": "npx postcss ./agentpm/web/src/styles/theme-system.css -o ./agentpm/web/static/css/theme-system.css",
    "build:components": "npx postcss ./agentpm/web/src/styles/components.css -o ./agentpm/web/static/css/components.css",
    "watch:css": "npx postcss ./agentpm/web/src/styles/theme-system.css -o ./agentpm/web/static/css/theme-system.css --watch"
  }
}
```

## Theme System Architecture

### Core Theme File (`theme-system.css`)

The main theme system uses the `@theme` directive to define all design tokens:

```css
@import "tailwindcss";

@theme {
  /* Primary Brand Colors (Indigo) */
  --color-primary-50: #eef2ff;
  --color-primary-100: #e0e7ff;
  --color-primary-500: #6366f1; /* Base */
  --color-primary-600: #4f46e5; /* Hover */
  --color-primary-900: #312e81;

  /* AIPM-Specific: Phase Colors */
  --color-phase-d1: #6366f1; /* Discovery */
  --color-phase-p1: #8b5cf6; /* Planning */
  --color-phase-i1: #3b82f6; /* Implementation */
  --color-phase-r1: #f59e0b; /* Review */
  --color-phase-o1: #10b981; /* Operations */
  --color-phase-e1: #ec4899; /* Evolution */
}
```

### Theme Variants

Multiple theme variants are supported through CSS custom properties:

```css
/* Light Theme (Default) */
:root {
  --color-surface-primary: #ffffff;
  --color-text-primary: #111827;
}

/* Dark Theme */
.theme-dark {
  --color-surface-primary: #111827;
  --color-text-primary: #f9fafb;
}

/* Royal Theme */
.theme-royal {
  --color-primary-500: #7c3aed;
  --color-secondary-500: #f59e0b;
}
```

### Component Library (`components.css`)

Components use `@layer components` with CSS custom properties:

```css
@layer components {
  .btn-primary {
    background-color: var(--color-primary-500);
    color: white;
  }
  
  .btn-primary:hover {
    background-color: var(--color-primary-600);
  }
  
  .btn-primary:focus {
    @apply ring-2 ring-offset-2;
    --tw-ring-color: var(--color-primary-500);
  }
}
```

## Migration Benefits

### 1. Performance Improvements

- **Faster Build Times**: PostCSS processing is more efficient than the v3 CLI
- **Smaller Bundle Size**: Better tree-shaking and optimization
- **Native CSS**: No JavaScript runtime overhead

### 2. Developer Experience

- **CSS-First**: More intuitive for designers and CSS developers
- **Better IntelliSense**: Improved autocomplete for custom properties
- **Simpler Configuration**: No complex JavaScript config files

### 3. Modern CSS Features

- **CSS Custom Properties**: Native browser support for theming
- **Color Functions**: Support for `color-mix()` and other modern CSS functions
- **Layer System**: Better CSS organization with `@layer`

## Usage Examples

### Theme Switching

```javascript
// theme-switcher.js
function switchTheme(themeName) {
  document.documentElement.className = `theme-${themeName}`;
  localStorage.setItem('theme', themeName);
}
```

### Component Usage

```html
<!-- Using theme-aware components -->
<button class="btn btn-primary">Primary Button</button>
<div class="card card-elevated">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
  </div>
  <div class="card-body">
    <p class="card-description">Card content</p>
  </div>
</div>

<!-- Using AIPM-specific components -->
<span class="phase-badge phase-badge-d1">Discovery</span>
<div class="confidence-indicator confidence-high">High Confidence</div>
```

### Custom Properties

```css
/* Direct usage of theme variables */
.custom-component {
  background-color: var(--color-primary-500);
  border-color: var(--color-border-primary);
  color: var(--color-text-primary);
}
```

## Build Process

### Development

```bash
# Start development with watch mode
npm run dev

# This runs:
# - PostCSS watch for theme-system.css
# - PostCSS watch for components.css  
# - Vite watch for JavaScript
```

### Production

```bash
# Build all assets
npm run build

# This runs:
# - PostCSS build for theme-system.css (minified)
# - PostCSS build for components.css (minified)
# - Vite build for JavaScript (minified)
```

## File Structure

```
agentpm/web/src/styles/
├── theme-system.css     # Core theme definitions with @theme
└── components.css       # Component library with @layer components

agentpm/web/static/css/
├── theme-system.css     # Built theme system
└── components.css       # Built components

postcss.config.js        # PostCSS configuration
tailwind.config.js       # Minimal v4 config (mostly for plugins)
```

## Troubleshooting

### Common Issues

1. **Unknown utility class errors**: Ensure custom classes are defined before being referenced
2. **PostCSS plugin errors**: Verify `@tailwindcss/postcss` is installed and configured
3. **Theme not applying**: Check that CSS custom properties are properly defined in `@theme`

### Debug Commands

```bash
# Check Tailwind version
npm list tailwindcss

# Test PostCSS processing
npx postcss input.css -o output.css

# Verify build output
npm run build && ls -la agentpm/web/static/css/
```

## Best Practices

1. **Use CSS Custom Properties**: Leverage `var(--color-primary-500)` for theme-aware styling
2. **Layer Organization**: Use `@layer components` for custom components
3. **Theme Consistency**: Define all colors in the `@theme` block
4. **Performance**: Use `color-mix()` for dynamic color variations
5. **Accessibility**: Maintain proper contrast ratios across all themes

## Future Enhancements

- **Dynamic Theme Generation**: API-driven theme creation
- **Advanced Color Functions**: More sophisticated color manipulation
- **Component Variants**: Automated variant generation
- **Performance Monitoring**: Build time and bundle size tracking

---

**Version**: 2.0.0  
**Last Updated**: 2025-10-23  
**Tailwind Version**: 4.1.16
