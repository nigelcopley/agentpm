# AgentPM Assets

This directory contains all branding assets, logos, and visual elements for the AgentPM project.

## Directory Structure

```
assets/
├── logos/              # Logo files and variants
│   ├── full/          # Complete logo with text
│   ├── symbol/        # Symbol-only versions
│   ├── favicon/       # Web favicon files
│   └── social/        # Social media optimised versions
├── icons/             # Application and UI icons
│   ├── app/           # Application icons
│   └── ui/            # UI element icons
└── README.md          # This file
```

## Logo Files

### Current Status
- **Original Logo**: Large file size, needs optimisation
- **Optimised Versions**: To be generated using the logo optimizer script
- **Formats**: PNG (current), SVG (recommended), ICO (favicon)

### Usage Guidelines
See [Logo Guidelines](../docs/branding/logo-guidelines.md) for detailed usage instructions.

## Optimisation Script

Use the logo optimizer script to create optimised versions:

```bash
# Install ImageMagick first (macOS)
brew install imagemagick

# Optimise the original logo
python scripts/logo-optimizer.py optimize --input original-logo.png --output assets/logos/

# Generate favicon files
python scripts/logo-optimizer.py generate-favicons --input original-logo.png --output assets/logos/favicon/

# Generate multiple variants
python scripts/logo-optimizer.py generate-variants --input original-logo.png --output assets/logos/

# Analyse file properties
python scripts/logo-optimizer.py analyze --input original-logo.png
```

## File Size Targets

### Web Use
- **Full Logo**: < 50KB
- **Symbol Only**: < 20KB
- **Favicon**: < 5KB

### Print Use
- **High Resolution**: 300 DPI minimum
- **Vector Format**: SVG preferred for scalability

## Integration Points

### Web Interface
- Store optimised logos in `agentpm/web/static/images/`
- Use SVG format for crisp display
- Implement lazy loading for large images

### CLI Interface
- Include ASCII art version for terminal display
- Use consistent branding in help text
- Maintain brand identity across all interfaces

### Documentation
- Use consistent logo placement
- Include in README files and project overviews
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

## Brand Standards

### Colours
- **Primary Blue**: #3182ce (bright blue glow)
- **Secondary Blue**: #1a365d (dark blue outlines)
- **Shield Blue**: #2c5282 (shield background)

### Typography
- **Font**: Sans-serif, modern typeface
- **Style**: Clean, professional, digital aesthetic

### Usage Rules
- Maintain minimum clear space around logo
- Ensure adequate contrast against backgrounds
- Use appropriate size for context
- Follow accessibility guidelines (WCAG AA)

## Getting Started

1. **Place Original Logo**: Add your large logo file to this directory
2. **Run Optimisation**: Use the logo optimizer script to create variants
3. **Review Results**: Check the optimisation report for file size improvements
4. **Integrate**: Use optimised versions in your applications
5. **Document**: Update usage guidelines as needed

## Support

For questions about logo usage or optimisation:
- Check the [Logo Guidelines](../docs/branding/logo-guidelines.md)
- Review the optimisation script documentation
- Follow the brand standards outlined in this README
