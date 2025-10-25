# AgentPM Logo Guidelines

## Overview

The AgentPM logo combines a stylised tree/network structure with a shield, representing growth, connectivity, and protection. The design features a modern blue neon aesthetic with a professional, digital appearance.

## Logo Components

### Symbol
- **Base Structure**: Three-dimensional box-like foundation with layered horizontal lines
- **Tree/Network**: Central vertical line branching into two smaller lines with terminal circles
- **Shield**: Overlapping protective element with white checkmark
- **Colour Scheme**: Dark blue outlines with bright blue neon glow effects

### Typography
- **Font**: Sans-serif, modern typeface
- **"Agent"**: Darker blue with subtle glow
- **"PM"**: Brighter blue with pronounced neon glow effect
- **Style**: Slightly embossed with shadow effects

## File Organisation

### Directory Structure
```
assets/
├── logos/
│   ├── full/           # Complete logo with text
│   ├── symbol/         # Symbol only versions
│   ├── favicon/        # Web favicon variants
│   └── social/         # Social media optimised versions
└── icons/
    ├── app/            # Application icons
    └── ui/             # UI element icons
```

### Recommended File Formats

#### Primary Formats
- **SVG**: Vector format for scalability (preferred for web)
- **PNG**: High-quality raster for print and web
- **ICO**: Favicon format for web browsers

#### Size Variants
- **Full Logo**: 200px, 400px, 800px, 1200px widths
- **Symbol Only**: 32px, 64px, 128px, 256px, 512px
- **Favicon**: 16px, 32px, 48px, 64px

## Usage Guidelines

### Web Applications
- Use SVG format for crisp display at all resolutions
- Maintain minimum size of 32px height for readability
- Ensure adequate contrast against background colours

### Documentation
- Use PNG format for consistent rendering across platforms
- Maintain aspect ratio in all resizing operations
- Include alt text for accessibility

### Print Materials
- Use high-resolution PNG (300 DPI minimum)
- Ensure CMYK colour compatibility for professional printing
- Maintain clear space around logo (minimum 1x logo height)

## Colour Specifications

### Primary Colours
- **Dark Blue**: #1a365d (outlines and "Agent" text)
- **Bright Blue**: #3182ce (glow effects and "PM" text)
- **Shield Fill**: #2c5282 (shield background)

### Accessibility
- Ensure WCAG AA compliance (4.5:1 contrast ratio minimum)
- Provide alternative versions for colour-blind users
- Test against various background colours

## File Size Optimisation

### Current Issue
The original logo file is too large for web use and should be optimised.

### Solutions
1. **Vector Conversion**: Convert to SVG for scalability and smaller file sizes
2. **Compression**: Use tools like TinyPNG or ImageOptim for PNG files
3. **Multiple Formats**: Create purpose-specific versions
4. **Lazy Loading**: Implement progressive loading for web applications

## Implementation Recommendations

### Immediate Actions
1. Create SVG version of the logo
2. Generate multiple size variants
3. Optimise file sizes for web use
4. Create favicon versions

### Long-term Strategy
1. Establish brand asset management system
2. Create automated build processes for logo variants
3. Implement consistent usage across all touchpoints
4. Regular review and optimisation of asset sizes

## Technical Integration

### Web Interface
- Store logos in `agentpm/web/static/images/`
- Reference in HTML templates and CSS
- Implement responsive image loading

### CLI Interface
- Include logo in help text and version information
- Use ASCII art version for terminal display
- Maintain consistent branding across all interfaces

### Documentation
- Use consistent logo placement in all documentation
- Include logo in README files and project overviews
- Maintain brand consistency across all materials

## Maintenance

### Regular Tasks
- Review file sizes quarterly
- Update formats as technology evolves
- Ensure consistency across all applications
- Monitor usage compliance

### Version Control
- Track all logo variants in version control
- Maintain change log for logo updates
- Document any modifications or optimisations
