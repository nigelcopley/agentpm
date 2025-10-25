#!/usr/bin/env python3
"""
AgentPM Logo Icon Extraction Script

This script extracts the icon/symbol from the full logo and creates clean,
padding-free versions for better web integration.

Usage:
    python scripts/extract-logo-icon.py --input agentpm-logo.png --output assets/logos/
"""

import argparse
import os
import sys
from pathlib import Path
import subprocess


class LogoIconExtractor:
    """Handles extraction of icon from full logo."""
    
    def __init__(self, project_root: Path):
        """Initialise the logo icon extractor.
        
        Args:
            project_root: Path to the AgentPM project root directory
        """
        self.project_root = project_root
        self.assets_dir = project_root / "assets"
        self.logos_dir = self.assets_dir / "logos"
        
    def check_dependencies(self) -> bool:
        """Check if required tools are available.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        try:
            subprocess.run(["magick", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: ImageMagick not found. Please install with: brew install imagemagick")
            return False
    
    def analyze_logo_structure(self, input_path: Path) -> dict:
        """Analyze the logo to understand its structure.
        
        Args:
            input_path: Path to the input logo file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Get image dimensions and properties
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
    
    def extract_icon_with_trim(self, input_path: Path, output_path: Path, 
                              size: int, padding: int = 0) -> bool:
        """Extract icon from logo with automatic trimming and padding control.
        
        Args:
            input_path: Input logo file path
            output_path: Output icon file path
            size: Target size in pixels
            padding: Additional padding to add (default: 0)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, trim the image to remove transparent/white borders
            # Then resize to target size
            # Finally add controlled padding if needed
            
            if padding > 0:
                # Add padding around the trimmed icon
                cmd = [
                    "magick", str(input_path),
                    "-trim",  # Remove transparent borders
                    "-resize", f"{size}x{size}",  # Resize to target
                    "-background", "transparent",  # Transparent background
                    "-gravity", "center",  # Center the icon
                    "-extent", f"{size + padding * 2}x{size + padding * 2}",  # Add padding
                    "-strip",  # Remove metadata
                    str(output_path)
                ]
            else:
                # No padding, just trim and resize
                cmd = [
                    "magick", str(input_path),
                    "-trim",  # Remove transparent borders
                    "-resize", f"{size}x{size}",  # Resize to target
                    "-background", "transparent",  # Transparent background
                    "-strip",  # Remove metadata
                    str(output_path)
                ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error extracting icon: {e}")
            return False
    
    def extract_icon_manual_crop(self, input_path: Path, output_path: Path, 
                                size: int, crop_x: int, crop_y: int, 
                                crop_width: int, crop_height: int) -> bool:
        """Extract icon using manual crop coordinates.
        
        Args:
            input_path: Input logo file path
            output_path: Output icon file path
            size: Target size in pixels
            crop_x: X coordinate for crop start
            crop_y: Y coordinate for crop start
            crop_width: Width of crop area
            crop_height: Height of crop area
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                "magick", str(input_path),
                "-crop", f"{crop_width}x{crop_height}+{crop_x}+{crop_y}",  # Manual crop
                "-resize", f"{size}x{size}",  # Resize to target
                "-background", "transparent",  # Transparent background
                "-strip",  # Remove metadata
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error extracting icon with manual crop: {e}")
            return False
    
    def generate_icon_variants(self, input_path: Path, output_dir: Path, 
                              method: str = "trim") -> bool:
        """Generate multiple icon variants.
        
        Args:
            input_path: Input logo file path
            output_dir: Output directory for icon variants
            method: Extraction method ("trim" or "crop")
            
        Returns:
            True if successful, False otherwise
        """
        variants = [
            ("icon-16", 16, 0),
            ("icon-24", 24, 0),
            ("icon-32", 32, 0),
            ("icon-48", 48, 0),
            ("icon-64", 64, 0),
            ("icon-128", 128, 0),
        ]
        
        output_dir.mkdir(parents=True, exist_ok=True)
        success = True
        
        for name, size, padding in variants:
            output_path = output_dir / f"{name}.png"
            
            if method == "trim":
                if not self.extract_icon_with_trim(input_path, output_path, size, padding):
                    success = False
                    continue
            elif method == "crop":
                # For 1024x1024 logo, assume the icon is in the center
                # You may need to adjust these coordinates based on your logo
                crop_size = int(size * 0.8)  # Icon takes 80% of the space
                crop_x = (1024 - crop_size) // 2
                crop_y = (1024 - crop_size) // 2
                
                if not self.extract_icon_manual_crop(input_path, output_path, size, 
                                                   crop_x, crop_y, crop_size, crop_size):
                    success = False
                    continue
        
        return success
    
    def create_favicon_from_icon(self, icon_path: Path, output_dir: Path) -> bool:
        """Create favicon files from the extracted icon.
        
        Args:
            icon_path: Path to the extracted icon
            output_dir: Output directory for favicon files
            
        Returns:
            True if successful, False otherwise
        """
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
        description="AgentPM Logo Icon Extraction Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract icon using automatic trimming
  python scripts/extract-logo-icon.py --input agentpm-logo.png --output assets/logos/ --method trim
  
  # Extract icon using manual crop (adjust coordinates as needed)
  python scripts/extract-logo-icon.py --input agentpm-logo.png --output assets/logos/ --method crop
        """
    )
    
    parser.add_argument('--input', required=True, help='Input logo file path')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--method', choices=['trim', 'crop'], default='trim',
                       help='Extraction method (default: trim)')
    parser.add_argument('--size', type=int, default=32,
                       help='Target icon size (default: 32)')
    
    args = parser.parse_args()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Initialise extractor
    extractor = LogoIconExtractor(project_root)
    
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
    
    print(f"Extracting icon from {input_path}...")
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
