# Logo Optimization Instructions

## Quick Start

1. **Place your logo file** in the project root directory (e.g., `agentpm-logo.png`)

2. **Run the optimization commands**:

```bash
# Generate multiple logo variants (recommended first step)
python scripts/logo-optimizer.py generate-variants --input agentpm-logo.png --output assets/logos/

# Generate favicon files
python scripts/logo-optimizer.py generate-favicons --input agentpm-logo.png --output assets/logos/favicon/

# Analyze the original file
python scripts/logo-optimizer.py analyze --input agentpm-logo.png
```

## What This Will Create

### Logo Variants (`assets/logos/`)
- `full-200.png` - 200px width logo
- `full-400.png` - 400px width logo  
- `full-800.png` - 800px width logo
- `symbol-32.png` - 32x32px symbol only
- `symbol-64.png` - 64x64px symbol only
- `symbol-128.png` - 128x128px symbol only
- `symbol-256.png` - 256x256px symbol only
- `optimization-report.json` - Detailed analysis report

### Favicon Files (`assets/logos/favicon/`)
- `favicon-16x16.png` - 16x16px favicon
- `favicon-32x32.png` - 32x32px favicon
- `favicon-48x48.png` - 48x48px favicon
- `favicon-64x64.png` - 64x64px favicon
- `favicon.ico` - Standard ICO format

## Expected Results

- **File size reduction**: Typically 60-80% smaller files
- **Multiple formats**: Optimized for different use cases
- **Quality maintained**: Professional appearance preserved
- **Web ready**: All files optimized for web use

## Next Steps After Optimization

1. **Review the optimization report** in `assets/logos/optimization-report.json`
2. **Test the files** in your web interface
3. **Update your applications** to use the optimized versions
4. **Remove the original large file** once you're satisfied with the results

## Troubleshooting

If you encounter any issues:

1. **Check ImageMagick installation**:
   ```bash
   convert --version
   identify --version
   ```

2. **Verify file permissions**:
   ```bash
   chmod +x scripts/logo-optimizer.py
   ```

3. **Check file format**: The script works best with PNG, JPG, and other common formats

## File Size Targets

- **Web logos**: < 50KB
- **Favicons**: < 5KB  
- **Symbol variants**: < 20KB

The optimization script will help you achieve these targets while maintaining visual quality.
