# APM (Agent Project Manager) Template Structure - Component-Based Architecture

## Overview

The APM (Agent Project Manager) dashboard now uses a modern, component-based template architecture with a professional brand system. This replaces the previous Bootstrap-based approach with a custom CSS framework and reusable Jinja2 components.

## Template Directory Structure

```
agentpm/web/templates/
├── layouts/
│   └── modern_base.html          # Modern base template with brand system
├── components/
│   ├── cards/
│   │   └── work_item_card.html   # Reusable work item card component
│   ├── layout/
│   │   ├── header.html           # Modern header with search and navigation
│   │   └── sidebar.html          # Smart sidebar with filters and stats
│   ├── forms/
│   │   └── (form components)     # Reusable form components
│   ├── feedback/
│   │   └── (toast, modal, alert) # Feedback components
│   └── data/
│       └── (table, filter, search) # Data display components
├── work-items/
│   ├── list.html                 # Work items list view
│   ├── detail.html               # Work item detail view
│   └── form.html                 # Work item create/edit form
├── tasks/
│   ├── list.html                 # Tasks list view
│   ├── detail.html               # Task detail view
│   └── form.html                 # Task create/edit form
├── projects/
│   ├── list.html                 # Projects list view
│   ├── detail.html               # Project detail view
│   └── form.html                 # Project create/edit form
├── contexts/
│   └── (context templates)       # Context management templates
└── learnings/
    └── (learning templates)      # Learning management templates
```

## Brand System Implementation

### CSS Framework (`brand-system.css`)
- **Custom Properties**: CSS variables for colors, typography, spacing
- **Component Classes**: Cards, buttons, forms, badges, alerts
- **Utility Classes**: Spacing, typography, colors, layout
- **Responsive Design**: Mobile-first approach with breakpoints

### JavaScript System (`brand-system.js`)
- **AIPM Namespace**: Organized JavaScript modules
- **Smart Filters**: Advanced filtering and search functionality
- **Card Interactions**: Hover effects and action handling
- **Form Enhancements**: Validation, auto-save, error handling
- **Keyboard Shortcuts**: Global shortcuts for productivity

## Component Architecture

### Reusable Components
1. **Cards**: Work item cards, task cards, project cards
2. **Forms**: Input fields, selects, buttons with validation
3. **Layout**: Header, sidebar, navigation components
4. **Feedback**: Toast notifications, modals, alerts
5. **Data**: Tables, filters, search components

### Component Usage Pattern
```html
<!-- Example: Work Item Card -->
{% include 'components/cards/work_item_card.html' with {
    'work_item': work_item,
    'show_actions': true,
    'variant': 'default'
} %}
```

## Key Features

### Modern Design System
- **Simple, Clean, Professional**: Brand identity principles
- **Consistent Spacing**: 4px base unit system
- **Professional Color Palette**: Primary blues, semantic colors
- **Typography**: Inter font family with clear hierarchy
- **Shadows & Borders**: Subtle depth and definition

### Enhanced User Experience
- **Smart Filtering**: Real-time search and filter capabilities
- **Responsive Design**: Mobile-first, works on all devices
- **Keyboard Shortcuts**: Productivity shortcuts (Ctrl+K, Ctrl+N)
- **Auto-save**: Form data automatically saved as draft
- **Toast Notifications**: User feedback for all actions

### Component Features
- **Work Item Cards**: Progress indicators, status badges, quick actions
- **Modern Header**: Global search, navigation, user menu
- **Smart Sidebar**: Quick stats, filters, recent activity
- **Form Components**: Validation, auto-save, help text
- **Data Tables**: Sorting, filtering, pagination

## Implementation Status

### ✅ Completed
- [x] Brand system CSS framework
- [x] JavaScript interaction system
- [x] Modern base template
- [x] Header component with search
- [x] Sidebar component with filters
- [x] Work item card component
- [x] Work items list template
- [x] Work items detail template
- [x] Work items form template
- [x] Tasks list template
- [x] Projects list template
- [x] Template directory structure

### 🔄 In Progress
- [ ] Task detail and form templates
- [ ] Project detail and form templates
- [ ] Context templates
- [ ] Learning templates
- [ ] Additional form components
- [ ] Modal and toast components

### 📋 Planned
- [ ] Advanced data table components
- [ ] Chart and visualization components
- [ ] File upload components
- [ ] Date picker components
- [ ] Multi-select components
- [ ] Drag and drop functionality

## Usage Examples

### Creating a New Page
```html
{% extends "layouts/modern_base.html" %}

{% block title %}Page Title - APM (Agent Project Manager) Dashboard{% endblock %}

{% block content %}
<!-- Page content using brand system classes -->
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Section Title</h3>
    </div>
    <div class="card-body">
        <!-- Content -->
    </div>
</div>
{% endblock %}
```

### Using Components
```html
<!-- Include a work item card -->
{% include 'components/cards/work_item_card.html' with {
    'work_item': work_item,
    'show_actions': true
} %}

<!-- Include the header -->
{% include 'components/layout/header.html' %}

<!-- Include the sidebar -->
{% include 'components/layout/sidebar.html' %}
```

### JavaScript Integration
```javascript
// Use the AIPM namespace
AIPM.utils.showToast('Success message', 'success');
AIPM.filters.init();
AIPM.cards.init();
```

## Benefits

1. **Consistency**: Unified design system across all pages
2. **Maintainability**: Reusable components reduce duplication
3. **Performance**: Optimized CSS and JavaScript
4. **Accessibility**: WCAG 2.1 AA compliant components
5. **Responsiveness**: Mobile-first design approach
6. **User Experience**: Modern interactions and feedback
7. **Developer Experience**: Clear structure and documentation

## Migration from Bootstrap

The new system replaces Bootstrap with:
- Custom CSS framework with brand-specific styling
- Component-based architecture instead of utility classes
- Modern JavaScript interactions instead of jQuery dependencies
- Professional design system instead of generic Bootstrap styling
- Optimized performance with smaller bundle size

This creates a cohesive, professional identity that reflects the quality and sophistication of the APM (Agent Project Manager) system while maintaining simplicity and usability.
