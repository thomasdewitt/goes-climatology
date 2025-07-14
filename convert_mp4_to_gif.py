#!/usr/bin/env python3
"""
MP4 to GIF Converter

Converts all .mp4 files to .gif in each output folder.
Uses ffmpeg for high-quality conversion with optimized settings.
"""

import os
import subprocess
from pathlib import Path
import argparse


def convert_mp4_to_gif(mp4_path, gif_path, fps=10, scale=512, verbose=True):
    """
    Convert MP4 to GIF using ffmpeg with optimization.
    
    Args:
        mp4_path: Path to input MP4 file
        gif_path: Path to output GIF file
        fps: Frames per second for GIF (default 10)
        scale: Width to scale GIF to (height auto-calculated, default 512)
        verbose: Whether to print progress
    """
    if verbose:
        print(f"Converting {mp4_path.name} to {gif_path.name}...")
    
    # ffmpeg command for high-quality GIF conversion
    # Uses palettegen/paletteuse for better colors and compression
    cmd = [
        'ffmpeg', '-y',  # -y to overwrite existing files
        '-i', str(mp4_path),
        '-filter_complex', 
        f'[0:v] fps={fps},scale={scale}:-1:flags=lanczos,split [a][b];[a] palettegen [p];[b][p] paletteuse',
        str(gif_path)
    ]
    
    try:
        # Run ffmpeg with suppressed output unless there's an error
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if verbose:
            print(f"✓ Successfully converted: {gif_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {mp4_path}: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ ffmpeg not found. Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        return False
    
    return True


def find_output_folders(base_dir="."):
    """Find all directories ending with '_output'."""
    base_path = Path(base_dir)
    output_folders = []
    
    for item in base_path.iterdir():
        if item.is_dir() and item.name.endswith('_output'):
            output_folders.append(item)
    
    return sorted(output_folders)


def find_mp4_files(folder):
    """Find all .mp4 files in a folder."""
    return list(folder.glob("*.mp4"))


def main(fps=10, scale=512, verbose=True):
    """Convert all MP4 files to GIF in output folders."""
    
    print("=" * 60)
    print("MP4 to GIF Converter")
    print("=" * 60)
    print(f"Settings: {fps} fps, {scale}px width")
    print()
    
    # Find all output folders
    output_folders = find_output_folders()
    
    if not output_folders:
        print("No output folders found (folders ending with '_output')")
        return False
    
    print(f"Found {len(output_folders)} output folders:")
    for folder in output_folders:
        print(f"  • {folder.name}")
    print()
    
    total_converted = 0
    total_errors = 0
    
    # Process each output folder
    for folder in output_folders:
        mp4_files = find_mp4_files(folder)
        
        if not mp4_files:
            if verbose:
                print(f"📁 {folder.name}: No MP4 files found")
            continue
        
        print(f"📁 {folder.name}: Found {len(mp4_files)} MP4 file(s)")
        
        for mp4_file in mp4_files:
            # Create GIF filename with scale parameter in name
            gif_name = f"{mp4_file.stem}_{scale}px.gif"
            gif_file = mp4_file.parent / gif_name
            
            # Skip if GIF already exists and is newer than MP4
            if gif_file.exists() and gif_file.stat().st_mtime > mp4_file.stat().st_mtime:
                if verbose:
                    print(f"⏭️  Skipping {mp4_file.name} (GIF already up-to-date)")
                continue
            
            # Convert MP4 to GIF
            success = convert_mp4_to_gif(
                mp4_file, 
                gif_file, 
                fps=fps, 
                scale=scale, 
                verbose=verbose
            )
            
            if success:
                total_converted += 1
                # Show file sizes
                mp4_size = mp4_file.stat().st_size / 1024 / 1024  # MB
                gif_size = gif_file.stat().st_size / 1024 / 1024  # MB
                if verbose:
                    print(f"   📊 Size: {mp4_size:.1f}MB → {gif_size:.1f}MB")
            else:
                total_errors += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"✓ Successfully converted: {total_converted} files")
    if total_errors > 0:
        print(f"❌ Errors: {total_errors} files")
    print("=" * 60)
    
    return total_errors == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert MP4 files to GIF in output folders')
    parser.add_argument('--fps', type=int, default=10, 
                       help='Frames per second for GIF (default: 10)')
    parser.add_argument('--scale', type=int, default=512, 
                       help='Width to scale GIF to in pixels (default: 512)')
    parser.add_argument('--quiet', action='store_true', 
                       help='Suppress verbose output')
    
    args = parser.parse_args()
    
    success = main(
        fps=args.fps, 
        scale=args.scale, 
        verbose=not args.quiet
    )
    
    exit(0 if success else 1)