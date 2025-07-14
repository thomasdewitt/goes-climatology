#!/usr/bin/env python3
"""
Comparison Image Creator

Creates side-by-side comparison images:
1. Random seasonal: single image vs climatology (2 columns)
2. Progressive frames: various combinations with climatology reference
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
from PIL import Image


def load_image(image_path):
    """Load image as numpy array."""
    return np.array(Image.open(image_path))


def create_side_by_side(images, output_path, layout='horizontal'):
    """
    Create comparison image by concatenating arrays.
    
    Args:
        images: List of image arrays
        output_path: Path to save comparison image
        layout: 'horizontal' for 1 row, '2x2' for 2x2 grid
    """
    if layout == '2x2' and len(images) == 4:
        # Ensure all images have same dimensions
        min_height = min(img.shape[0] for img in images)
        min_width = min(img.shape[1] for img in images)
        
        resized_images = []
        for img in images:
            if img.shape[0] != min_height or img.shape[1] != min_width:
                from PIL import Image as PILImage
                pil_img = PILImage.fromarray(img)
                pil_img = pil_img.resize((min_width, min_height), PILImage.Resampling.LANCZOS)
                resized_images.append(np.array(pil_img))
            else:
                resized_images.append(img)
        
        # Create 2x2 grid: top row = [0, 1], bottom row = [2, 3]
        top_row = np.concatenate([resized_images[0], resized_images[1]], axis=1)
        bottom_row = np.concatenate([resized_images[2], resized_images[3]], axis=1)
        concatenated = np.concatenate([top_row, bottom_row], axis=0)
        
    else:
        # Horizontal layout (default)
        # Ensure all images have same height
        min_height = min(img.shape[0] for img in images)
        resized_images = []
        
        for img in images:
            if img.shape[0] != min_height:
                # Resize to match minimum height while preserving aspect ratio
                from PIL import Image as PILImage
                pil_img = PILImage.fromarray(img)
                aspect_ratio = img.shape[1] / img.shape[0]
                new_width = int(min_height * aspect_ratio)
                pil_img = pil_img.resize((new_width, min_height), PILImage.Resampling.LANCZOS)
                resized_images.append(np.array(pil_img))
            else:
                resized_images.append(img)
        
        # Concatenate horizontally
        concatenated = np.concatenate(resized_images, axis=1)
    
    # Save using PIL with lossless compression
    pil_result = Image.fromarray(concatenated)
    pil_result.save(output_path, format='PNG', compress_level=1, dpi=(300, 300))
    
    print(f"✓ Created: {output_path}")


def process_random_seasonal():
    """Create 2-column comparisons for random seasonal images."""
    print("=" * 60)
    print("Processing Random Seasonal Comparisons")
    print("=" * 60)
    
    seasonal_dir = Path("random_seasonal_output")
    climatology_dir = Path("decadal_climatology_2015_2024")
    
    if not seasonal_dir.exists():
        print(f"❌ Directory not found: {seasonal_dir}")
        return
    
    if not climatology_dir.exists():
        print(f"❌ Directory not found: {climatology_dir}")
        return
    
    # Find climatology image
    climatology_files = list(climatology_dir.glob("*.png"))
    if not climatology_files:
        print(f"❌ No PNG files found in {climatology_dir}")
        return
    
    climatology_path = climatology_files[0]  # Use first climatology image
    climatology_img = load_image(climatology_path)
    
    # Process each seasonal image
    seasonal_files = list(seasonal_dir.glob("*.png"))
    
    if not seasonal_files:
        print(f"❌ No PNG files found in {seasonal_dir}")
        return
    
    print(f"Found {len(seasonal_files)} seasonal images")
    print(f"Using climatology: {climatology_path.name}")
    
    for seasonal_file in seasonal_files:
        print(f"Processing: {seasonal_file.name}")
        
        # Load seasonal image
        seasonal_img = load_image(seasonal_file)
        
        # Create comparison
        images = [seasonal_img, climatology_img]
        
        # Output filename
        output_name = f"comparison_{seasonal_file.stem}_vs_climatology.png"
        output_path = seasonal_dir / output_name
        
        create_side_by_side(images, output_path)
    
    print()


def process_progressive_frames():
    """Create 3-col and 4-col comparisons for progressive frames."""
    print("=" * 60)
    print("Processing Progressive Frame Comparisons")
    print("=" * 60)
    
    frames_dir = Path("progressive_video_output/Frames")
    climatology_dir = Path("decadal_climatology_2015_2024")
    
    if not frames_dir.exists():
        print(f"❌ Directory not found: {frames_dir}")
        return
    
    if not climatology_dir.exists():
        print(f"❌ Directory not found: {climatology_dir}")
        return
    
    # Find climatology image
    climatology_files = list(climatology_dir.glob("*.png"))
    if not climatology_files:
        print(f"❌ No PNG files found in {climatology_dir}")
        return
    
    climatology_path = climatology_files[0]
    climatology_img = load_image(climatology_path)
    
    # Find progressive frame files
    frame_files = sorted(frames_dir.glob("progressive_frame_*.png"))
    
    if not frame_files:
        print(f"❌ No progressive frame files found in {frames_dir}")
        return
    
    print(f"Found {len(frame_files)} progressive frames")
    print(f"Using climatology: {climatology_path.name}")
    
    # Create mapping of frame number to file
    frames_by_number = {}
    for frame_file in frame_files:
        # Extract frame number from filename like "progressive_frame_01_n_images=1.png"
        parts = frame_file.stem.split('_')
        if len(parts) >= 3:
            try:
                frame_num = int(parts[2])  # "01" -> 1
                frames_by_number[frame_num] = frame_file
            except ValueError:
                continue
    
    # Required frames for comparisons
    required_frames = [1, 2, 4]  # Single image, 2 average, 8 average (frame numbers)
    
    # Find frame 4 (which should be 8 images averaged: 1, 2, 4, 8)
    frame_8_num = None
    for num in sorted(frames_by_number.keys()):
        if num >= 4:  # Frame 4 should be 8 images
            frame_8_num = num
            break
    
    # Check if we have required frames
    missing_frames = []
    for frame_num in required_frames:
        if frame_num not in frames_by_number:
            missing_frames.append(frame_num)
    
    if missing_frames:
        print(f"❌ Missing required frames: {missing_frames}")
        available = sorted(frames_by_number.keys())
        print(f"Available frames: {available}")
        return
    
    # Load required frame images
    single_img = load_image(frames_by_number[1])    # 1 image
    avg2_img = load_image(frames_by_number[2])      # 2 images average
    
    print(f"Loaded frames: {[1, 2]}")
    
    # Create 3-column comparison (single, 2-avg, climatology)
    print("Creating 3-column comparison...")
    images_3col = [single_img, avg2_img, climatology_img]
    output_3col = frames_dir.parent / "comparison_3col_single_2avg_climatology.png"
    
    create_side_by_side(images_3col, output_3col)
    
    # Create 4-column comparison if we have frame for 8-image average
    if frame_8_num:
        avg8_img = load_image(frames_by_number[frame_8_num])
        print(f"Creating 4-column comparison (using frame {frame_8_num} for 8-image average)...")
        
        images_4col = [single_img, avg2_img, avg8_img, climatology_img]
        output_4col = frames_dir.parent / "comparison_2x2_single_2avg_8avg_climatology.png"
        
        create_side_by_side(images_4col, output_4col, layout='2x2')
    else:
        print("❌ Could not find frame for 8-image average")
    
    print()


def main(random_seasonal=True, progressive_frames=True):
    """Create comparison images."""
    
    print("=" * 60)
    print("GOES Comparison Image Creator")
    print("=" * 60)
    print("Creating side-by-side comparison images...")
    print()
    
    if random_seasonal:
        process_random_seasonal()
    
    if progressive_frames:
        process_progressive_frames()
    
    print("=" * 60)
    print("✓ Comparison image creation completed!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create side-by-side comparison images')
    parser.add_argument('--skip-seasonal', action='store_true', 
                       help='Skip random seasonal comparisons')
    parser.add_argument('--skip-progressive', action='store_true', 
                       help='Skip progressive frame comparisons')
    
    args = parser.parse_args()
    
    main(
        random_seasonal=not args.skip_seasonal,
        progressive_frames=not args.skip_progressive
    )