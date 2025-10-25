#!/usr/bin/env python3
"""
AgentPM Logo Optimisation Script

This script helps optimise and manage logo files for the AgentPM project.
It provides utilities for file size reduction, format conversion, and
generation of multiple variants.

Usage:
    python scripts/logo-optimizer.py --help
    python scripts/logo-optimizer.py optimize --input logo.png --output assets/logos/
    python scripts/logo-optimizer.py generate-favicons --input logo.png --output assets/logos/favicon/
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import subprocess
import json


class LogoOptimizer:
    """Handles logo optimisation and variant generation."""
    
    def __init__(self, project_root: Path):
        """Initialise the logo optimizer.
        
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
        required_tools = ["convert", "identify"]  # ImageMagick tools
        missing_tools = []
        
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], 
                             capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"Missing required tools: {', '.join(missing_tools)}")
            print("Please install ImageMagick: brew install imagemagick")
            return False
        
        return True
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes
        """
        return file_path.stat().st_size
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def optimize_png(self, input_path: Path, output_path: Path, 
                    quality: int = 85) -> bool:
        """Optimise PNG file using ImageMagick.
        
        Args:
            input_path: Input PNG file path
            output_path: Output PNG file path
            quality: Compression quality (1-100)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                "convert", str(input_path),
                "-strip",  # Remove metadata
                "-quality", str(quality),
                "-define", "png:compression-level=9",
                str(output_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error optimising PNG: {e}")
            return False
    
    def resize_image(self, input_path: Path, output_path: Path, 
                    width: int, height: Optional[int] = None) -> bool:
        """Resize image to specified dimensions.
        
        Args:
            input_path: Input image path
            output_path: Output image path
            width: Target width in pixels
            height: Target height in pixels (maintains aspect ratio if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if height is None:
                size_arg = f"{width}x"
            else:
                size_arg = f"{width}x{height}"
            
            cmd = [
                "convert", str(input_path),
                "-resize", size_arg,
                "-strip",
                str(output_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error resizing image: {e}")
            return False
    
    def generate_favicon(self, input_path: Path, output_dir: Path) -> bool:
        """Generate favicon files in multiple sizes.
        
        Args:
            input_path: Input logo file path
            output_dir: Output directory for favicon files
            
        Returns:
            True if successful, False otherwise
        """
        favicon_sizes = [16, 32, 48, 64]
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success = True
        for size in favicon_sizes:
            output_path = output_dir / f"favicon-{size}x{size}.png"
            if not self.resize_image(input_path, output_path, size, size):
                success = False
                continue
            
            # Also create ICO file for 32x32
            if size == 32:
                ico_path = output_dir / "favicon.ico"
                try:
                    cmd = ["convert", str(output_path), str(ico_path)]
                    subprocess.run(cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print(f"Warning: Could not create ICO file")
        
        return success
    
    def generate_logo_variants(self, input_path: Path, output_dir: Path) -> bool:
        """Generate multiple logo variants.
        
        Args:
            input_path: Input logo file path
            output_dir: Output directory for logo variants
            
        Returns:
            True if successful, False otherwise
        """
        variants = [
            ("full-200", 200, None),
            ("full-400", 400, None),
            ("full-800", 800, None),
            ("symbol-32", 32, 32),
            ("symbol-64", 64, 64),
            ("symbol-128", 128, 128),
            ("symbol-256", 256, 256),
        ]
        
        output_dir.mkdir(parents=True, exist_ok=True)
        success = True
        
        for name, width, height in variants:
            output_path = output_dir / f"{name}.png"
            if not self.resize_image(input_path, output_path, width, height):
                success = False
                continue
            
            # Optimise the resized image
            if not self.optimize_png(output_path, output_path):
                success = False
        
        return success
    
    def analyze_file(self, file_path: Path) -> dict:
        """Analyse image file properties.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary with file analysis results
        """
        try:
            cmd = ["identify", "-verbose", str(file_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse ImageMagick output
            lines = result.stdout.split('\n')
            info = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            # Get file size
            file_size = self.get_file_size(file_path)
            info['File Size'] = self.format_file_size(file_size)
            
            return info
        except subprocess.CalledProcessError as e:
            print(f"Error analysing file: {e}")
            return {}
    
    def create_optimization_report(self, input_path: Path, 
                                 output_dir: Path) -> None:
        """Create a report of optimisation results.
        
        Args:
            input_path: Original input file path
            output_dir: Directory containing optimised files
        """
        report_path = output_dir / "optimization-report.json"
        
        original_size = self.get_file_size(input_path)
        original_info = self.analyze_file(input_path)
        
        report = {
            "original_file": {
                "path": str(input_path),
                "size_bytes": original_size,
                "size_formatted": self.format_file_size(original_size),
                "properties": original_info
            },
            "optimized_files": []
        }
        
        # Analyse all generated files
        for file_path in output_dir.glob("*.png"):
            if file_path != input_path:
                file_size = self.get_file_size(file_path)
                file_info = self.analyze_file(file_path)
                
                report["optimized_files"].append({
                    "path": str(file_path),
                    "size_bytes": file_size,
                    "size_formatted": self.format_file_size(file_size),
                    "size_reduction_percent": round(
                        (1 - file_size / original_size) * 100, 2
                    ),
                    "properties": file_info
                })
        
        # Write report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Optimisation report saved to: {report_path}")


def main():
    """Main entry point for the logo optimizer script."""
    parser = argparse.ArgumentParser(
        description="AgentPM Logo Optimisation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimise a logo file
  python scripts/logo-optimizer.py optimize --input logo.png --output assets/logos/
  
  # Generate favicon files
  python scripts/logo-optimizer.py generate-favicons --input logo.png --output assets/logos/favicon/
  
  # Generate multiple logo variants
  python scripts/logo-optimizer.py generate-variants --input logo.png --output assets/logos/
  
  # Analyse a file
  python scripts/logo-optimizer.py analyze --input logo.png
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Optimise command
    optimize_parser = subparsers.add_parser('optimize', help='Optimise a logo file')
    optimize_parser.add_argument('--input', required=True, help='Input logo file path')
    optimize_parser.add_argument('--output', required=True, help='Output directory')
    optimize_parser.add_argument('--quality', type=int, default=85, 
                               help='Compression quality (1-100)')
    
    # Generate favicons command
    favicon_parser = subparsers.add_parser('generate-favicons', 
                                         help='Generate favicon files')
    favicon_parser.add_argument('--input', required=True, help='Input logo file path')
    favicon_parser.add_argument('--output', required=True, help='Output directory')
    
    # Generate variants command
    variants_parser = subparsers.add_parser('generate-variants', 
                                          help='Generate logo variants')
    variants_parser.add_argument('--input', required=True, help='Input logo file path')
    variants_parser.add_argument('--output', required=True, help='Output directory')
    
    # Analyse command
    analyze_parser = subparsers.add_parser('analyze', help='Analyse a logo file')
    analyze_parser.add_argument('--input', required=True, help='Input logo file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Initialise optimizer
    optimizer = LogoOptimizer(project_root)
    
    # Check dependencies
    if not optimizer.check_dependencies():
        sys.exit(1)
    
    # Execute command
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
    
    if args.command == 'optimize':
        output_dir = Path(args.output)
        output_path = output_dir / f"optimized_{input_path.name}"
        
        print(f"Optimising {input_path}...")
        if optimizer.optimize_png(input_path, output_path, args.quality):
            original_size = optimizer.get_file_size(input_path)
            new_size = optimizer.get_file_size(output_path)
            reduction = (1 - new_size / original_size) * 100
            
            print(f"Optimisation complete!")
            print(f"Original size: {optimizer.format_file_size(original_size)}")
            print(f"New size: {optimizer.format_file_size(new_size)}")
            print(f"Size reduction: {reduction:.1f}%")
        else:
            print("Optimisation failed!")
            sys.exit(1)
    
    elif args.command == 'generate-favicons':
        output_dir = Path(args.output)
        print(f"Generating favicon files...")
        if optimizer.generate_favicon(input_path, output_dir):
            print("Favicon generation complete!")
        else:
            print("Favicon generation failed!")
            sys.exit(1)
    
    elif args.command == 'generate-variants':
        output_dir = Path(args.output)
        print(f"Generating logo variants...")
        if optimizer.generate_logo_variants(input_path, output_dir):
            print("Logo variant generation complete!")
            optimizer.create_optimization_report(input_path, output_dir)
        else:
            print("Logo variant generation failed!")
            sys.exit(1)
    
    elif args.command == 'analyze':
        print(f"Analysing {input_path}...")
        info = optimizer.analyze_file(input_path)
        if info:
            print("\nFile Analysis:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print("Analysis failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
