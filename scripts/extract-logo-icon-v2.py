#!/usr/bin/env python3
"""
AgentPM Logo Icon Extraction Script V2

This script creates better icon extractions from rectangular logos by:
1. Extracting the symbol/icon portion
2. Creating square icons with proper padding
3. Handling rectangular logos better

Usage:
    python scripts/extract-logo-icon-v2.py --input agentpm-logo.png --output assets/logos/
"""

import argparse
import os
import sys
from pathlib import Path
import subprocess


class LogoIconExtractorV2:
    """Handles extraction of icon from rectangular logos."""
    
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
    
    def extract_symbol_from_rectangular_logo(self, input_path: Path, output_path: Path, 
                                           size: int) -> bool:
        """Extract symbol from rectangular logo and create square icon."""
        try:
            # For rectangular logos, we want to extract the left portion (symbol)
            # and create a square icon with proper padding
            
            # First, get the dimensions
            cmd = ["magick", "identify", "-format", "%wx%h", str(input_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            dimensions = result.stdout.strip()
            width, height = map(int, dimensions.split('x'))
            
            # Calculate crop area - take the left portion (assuming symbol is on the left)
            # For a 856x318 logo, we might want the left 318x318 portion
            crop_size = min(width, height)
            crop_x = 0
            crop_y = 0
            
            # Create square icon with the symbol portion
            cmd = [
                "magick", str(input_path),
                "-crop", f"{crop_size}x{crop_size}+{crop_x}+{crop_y}",  # Crop to square
                "-resize", f"{size}x{size}",  # Resize to target
                "-background", "transparent",  # Transparent background
                "-strip",  # Remove metadata
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error extracting symbol: {e}")
            return False
    
    def extract_text_portion(self, input_path: Path, output_path: Path, 
                           size: int) -> bool:
        """Extract text portion from rectangular logo."""
        try:
            # Get dimensions
            cmd = ["magick", "identify", "-format", "%wx%h", str(input_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            dimensions = result.stdout.strip()
            width, height = map(int, dimensions.split('x'))
            
            # For text portion, take the right side
            # Assuming text starts after the symbol
            text_start_x = min(width, height)  # Start after the square symbol area
            text_width = width - text_start_x
            text_height = height
            
            if text_width > 0:
                cmd = [
                    "magick", str(input_path),
                    "-crop", f"{text_width}x{text_height}+{text_start_x}+0",  # Crop text portion
                    "-resize", f"{size}x{size}",  # Resize to target
                    "-background", "transparent",  # Transparent background
                    "-strip",  # Remove metadata
                    str(output_path)
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                return True
            else:
                print("Warning: No text portion found")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error extracting text portion: {e}")
            return False
    
    def create_square_icon_with_padding(self, input_path: Path, output_path: Path, 
                                      size: int, padding: int = 4) -> bool:
        """Create square icon with controlled padding."""
        try:
            cmd = [
                "magick", str(input_path),
                "-trim",  # Remove transparent borders
                "-resize", f"{size - padding * 2}x{size - padding * 2}",  # Resize to fit with padding
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
    
    def generate_icon_variants(self, input_path: Path, output_dir: Path) -> bool:
        """Generate multiple icon variants from rectangular logo."""
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
            
            # Try extracting symbol first
            if not self.extract_symbol_from_rectangular_logo(input_path, output_path, size):
                # Fallback to trim method
                if not self.create_square_icon_with_padding(input_path, output_path, size, padding):
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
        description="AgentPM Logo Icon Extraction Tool V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract icons from rectangular logo
  python scripts/extract-logo-icon-v2.py --input agentpm-logo.png --output assets/logos/
        """
    )
    
    parser.add_argument('--input', required=True, help='Input logo file path')
    parser.add_argument('--output', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Initialise extractor
    extractor = LogoIconExtractorV2(project_root)
    
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
    print(f"Output directory: {output_dir}")
    
    # Analyze the logo first
    print("\nAnalyzing logo structure...")
    analysis = extractor.analyze_logo_structure(input_path)
    if analysis:
        print(f"Image dimensions: {analysis.get('Geometry', 'Unknown')}")
        print(f"Image format: {analysis.get('Format', 'Unknown')}")
    
    # Generate icon variants
    print(f"\nGenerating icon variants...")
    if extractor.generate_icon_variants(input_path, output_dir):
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
