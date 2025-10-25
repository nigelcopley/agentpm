#!/usr/bin/env python3
"""
AgentPM Logo Icon Extraction Script V3

This script preserves the full icon by maintaining aspect ratio and adding
proper padding to create square icons without cutting off any content.

Usage:
    python scripts/extract-logo-icon-v3.py --input agentpm-logo-icon.png --output assets/logos/
"""

import argparse
import os
import sys
from pathlib import Path
import subprocess


class LogoIconExtractorV3:
    """Handles extraction of icon while preserving full content."""
    
    def __init__(self, project_root: Path):
        """Initialise the logo icon extractor."""
        self.project_root = project_root
        self.assets_dir = project_root / "assets"
        self.logos_dir = self.assets_dir / "logos"
        
    def check_dependencies(self) -> bool:
        """Check if required tools are available."""
        try:
            subprocess.run(["magick", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: ImageMagick not found. Please install with: brew install imagemagick")
            return False
    
    def analyze_logo_structure(self, input_path: Path) -> dict:
        """Analyze the logo to understand its structure."""
        try:
            cmd = ["magick", "identify", "-verbose", str(input_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            lines = result.stdout.split('\n')
            info = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            return info
        except subprocess.CalledProcessError as e:
            print(f"Error analysing logo: {e}")
            return {}
    
    def create_square_icon_preserve_aspect(self, input_path: Path, output_path: Path, 
                                         size: int, padding: int = 8) -> bool:
        """Create square icon while preserving the full aspect ratio of the original."""
        try:
            # First, trim any transparent borders
            # Then resize to fit within the square while maintaining aspect ratio
            # Finally, center it in a square with padding
            
            cmd = [
                "magick", str(input_path),
                "-trim",  # Remove transparent borders
                "-resize", f"{size - padding * 2}x{size - padding * 2}>",  # Resize to fit, maintain aspect ratio
                "-background", "transparent",  # Transparent background
                "-gravity", "center",  # Center the icon
                "-extent", f"{size}x{size}",  # Create square with padding
                "-strip",  # Remove metadata
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating square icon: {e}")
            return False
    
    def create_square_icon_fit_height(self, input_path: Path, output_path: Path, 
                                    size: int, padding: int = 8) -> bool:
        """Create square icon by fitting to height and centering horizontally."""
        try:
            # Fit the icon to the height of the square (minus padding)
            # This ensures the full height is preserved
            
            cmd = [
                "magick", str(input_path),
                "-trim",  # Remove transparent borders
                "-resize", f"x{size - padding * 2}",  # Resize to fit height
                "-background", "transparent",  # Transparent background
                "-gravity", "center",  # Center the icon
                "-extent", f"{size}x{size}",  # Create square with padding
                "-strip",  # Remove metadata
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating square icon (fit height): {e}")
            return False
    
    def create_square_icon_fit_width(self, input_path: Path, output_path: Path, 
                                   size: int, padding: int = 8) -> bool:
        """Create square icon by fitting to width and centering vertically."""
        try:
            # Fit the icon to the width of the square (minus padding)
            # This ensures the full width is preserved
            
            cmd = [
                "magick", str(input_path),
                "-trim",  # Remove transparent borders
                "-resize", f"{size - padding * 2}x",  # Resize to fit width
                "-background", "transparent",  # Transparent background
                "-gravity", "center",  # Center the icon
                "-extent", f"{size}x{size}",  # Create square with padding
                "-strip",  # Remove metadata
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating square icon (fit width): {e}")
            return False
    
    def generate_icon_variants(self, input_path: Path, output_dir: Path, 
                             method: str = "fit_height") -> bool:
        """Generate multiple icon variants preserving full content."""
        variants = [
            ("icon-16", 16, 2),
            ("icon-24", 24, 3),
            ("icon-32", 32, 4),
            ("icon-48", 48, 6),
            ("icon-64", 64, 8),
            ("icon-128", 128, 16),
        ]
        
        output_dir.mkdir(parents=True, exist_ok=True)
        success = True
        
        for name, size, padding in variants:
            output_path = output_dir / f"{name}.png"
            
            if method == "fit_height":
                if not self.create_square_icon_fit_height(input_path, output_path, size, padding):
                    success = False
                    continue
            elif method == "fit_width":
                if not self.create_square_icon_fit_width(input_path, output_path, size, padding):
                    success = False
                    continue
            else:  # preserve_aspect
                if not self.create_square_icon_preserve_aspect(input_path, output_path, size, padding):
                    success = False
                    continue
        
        return success
    
    def create_favicon_from_icon(self, icon_path: Path, output_dir: Path) -> bool:
        """Create favicon files from the extracted icon."""
        favicon_sizes = [16, 32, 48, 64]
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success = True
        for size in favicon_sizes:
            output_path = output_dir / f"favicon-{size}x{size}.png"
            try:
                cmd = [
                    "magick", str(icon_path),
                    "-resize", f"{size}x{size}",
                    "-strip",
                    str(output_path)
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Also create ICO file for 32x32
                if size == 32:
                    ico_path = output_dir / "favicon.ico"
                    cmd = ["magick", str(output_path), str(ico_path)]
                    subprocess.run(cmd, check=True, capture_output=True)
                    
            except subprocess.CalledProcessError:
                print(f"Warning: Could not create favicon {size}x{size}")
                success = False
        
        return success


def main():
    """Main entry point for the logo icon extractor script."""
    parser = argparse.ArgumentParser(
        description="AgentPM Logo Icon Extraction Tool V3 - Preserves Full Content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract icons preserving full height (recommended for tall icons)
  python scripts/extract-logo-icon-v3.py --input agentpm-logo-icon.png --output assets/logos/ --method fit_height
  
  # Extract icons preserving full width
  python scripts/extract-logo-icon-v3.py --input agentpm-logo-icon.png --output assets/logos/ --method fit_width
  
  # Extract icons preserving aspect ratio
  python scripts/extract-logo-icon-v3.py --input agentpm-logo-icon.png --output assets/logos/ --method preserve_aspect
        """
    )
    
    parser.add_argument('--input', required=True, help='Input logo file path')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--method', choices=['fit_height', 'fit_width', 'preserve_aspect'], 
                       default='fit_height', help='Extraction method (default: fit_height)')
    
    args = parser.parse_args()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Initialise extractor
    extractor = LogoIconExtractorV3(project_root)
    
    # Check dependencies
    if not extractor.check_dependencies():
        sys.exit(1)
    
    # Check input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting icons from {input_path}...")
    print(f"Method: {args.method}")
    print(f"Output directory: {output_dir}")
    
    # Analyze the logo first
    print("\nAnalyzing logo structure...")
    analysis = extractor.analyze_logo_structure(input_path)
    if analysis:
        print(f"Image dimensions: {analysis.get('Geometry', 'Unknown')}")
        print(f"Image format: {analysis.get('Format', 'Unknown')}")
    
    # Generate icon variants
    print(f"\nGenerating icon variants...")
    if extractor.generate_icon_variants(input_path, output_dir, args.method):
        print("Icon extraction complete!")
        
        # Create favicons from the 32px icon
        icon_32_path = output_dir / "icon-32.png"
        if icon_32_path.exists():
            print("Creating favicon files...")
            if extractor.create_favicon_from_icon(icon_32_path, output_dir / "favicon"):
                print("Favicon creation complete!")
            else:
                print("Favicon creation failed!")
    else:
        print("Icon extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
