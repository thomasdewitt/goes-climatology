#!/usr/bin/env python3
"""
Progressive Averaging Video Generator

Creates a video showing the progressive averaging of GOES noon climatology images.
Each frame shows the average of exponentially increasing numbers of images:
- Frame 1: First image only
- Frame 2: Average of first 2 images  
- Frame 3: Average of first 4 images
- Frame 4: Average of first 8 images
- etc.

Total video duration: 6 seconds
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import cv2
import tempfile
import os
from goes_climate_viz import download_and_average_goes_images


def create_progressive_frames(all_dates, hours, satellite, domain, coarsening_factor, cache_dir, verbose=True):
    """
    Create progressive averaging frames with exponential progression.
    Reuses download_and_average_goes_images for each subset of dates.
    
    Args:
        all_dates: List of datetime objects for all dates
        hours: List of hours to process
        satellite: "east" or "west"
        domain: Domain (F=Full Disk, C=CONUS, etc.)
        coarsening_factor: Factor to coarsen images
        cache_dir: Directory for cached images
        verbose: Whether to print progress
        
    Returns:
        List of averaged image arrays for each frame
    """
    frames = []
    
    # Create exponential progression of frame counts
    frame_counts = []
    n = 1
    while n <= len(all_dates):
        frame_counts.append(n)
        n *= 2
    
    # If we don't reach the end, add a final frame with all images
    if frame_counts[-1] < len(all_dates):
        frame_counts.append(len(all_dates))
    
    print(f"Frame progression: {frame_counts}")
    
    # Generate each frame by averaging the first N dates
    for i, count in enumerate(frame_counts):
        if verbose:
            print(f"\nCreating frame {i+1}/{len(frame_counts)}: Average of first {count} images")
        
        # Use the existing function to average the first 'count' dates
        try:
            averaged_image = download_and_average_goes_images(
                hours=hours,
                dates=all_dates[:count],  # First 'count' dates
                satellite=satellite,
                coarsening_factor=coarsening_factor,
                domain=domain,
                output_path=tempfile.gettempdir(),  # Temporary output (we don't need the PNG)
                save_format="png",
                use_cache=True,
                cache_dir=cache_dir,
                verbose=False  # Suppress detailed output
            )
            frames.append(averaged_image)
            
        except Exception as e:
            print(f"Error creating frame {i+1}: {e}")
            # If we can't create this frame, skip it
            continue
    
    return frames


def create_video_from_frames(frames, output_path, filename, fps=None, verbose=True):
    """
    Create MP4 video from list of frames.
    
    Args:
        frames: List of RGB image arrays
        output_path: Directory to save video
        filename: Output filename
        fps: Frames per second (calculated for 10s duration if None)
        verbose: Whether to print progress
    """
    if not frames:
        print("No frames to create video")
        return
    
    # Calculate FPS for 6-second duration
    if fps is None:
        fps = len(frames) / 6.0
    
    # Create output directory
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Convert frames to video format
    video_frames = []
    for i, frame in enumerate(frames):
        if verbose:
            print(f"Processing frame {i+1}/{len(frames)} for video")
        
        # Convert to 8-bit RGB
        frame_8bit = (frame * 255).astype(np.uint8)
        
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame_8bit, cv2.COLOR_RGB2BGR)
        video_frames.append(frame_bgr)
    
    # Write video
    if video_frames:
        h, w = video_frames[0].shape[:2]
        filepath = str(Path(output_path) / filename)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filepath, fourcc, fps, (w, h), isColor=True)
        
        for frame in video_frames:
            out.write(frame)
        
        out.release()
        
        if verbose:
            print(f"✓ Video saved: {filepath}")
            print(f"✓ Duration: {len(frames)/fps:.1f} seconds")
            print(f"✓ FPS: {fps:.1f}")
            print(f"✓ Total frames: {len(frames)}")


def main():
    """Generate progressive averaging video."""
    
    print("=" * 70)
    print("GOES Progressive Averaging Video Generator")
    print("=" * 70)
    print("Creating video showing progressive averaging of noon climatology")
    print("Frame progression: 1, 2, 4, 8, 16, 32, ... images")
    print("Total duration: 6 seconds")
    print("=" * 70)
    
    # Use same configuration as monthly_noon_climatology.py
    local_noon_utc = 17
    
    # Create dates for days 1, 5, 10, 15, 20, 25 of each month for 2018-2024
    all_dates = []
    for year in range(2018, 2025):
        for month in range(1, 13):
            for day in [1, 5, 10, 15, 20, 25]:
                all_dates.append(datetime(year, month, day))

    # Shuffle dates
    np.random.seed(42)  # For reproducibility
    np.random.shuffle(all_dates)
    
    print(f"Processing {len(all_dates)} dates across 7 years")
    print(f"Years: 2018-2024 (GOES-16 operational period)")
    print(f"Days per month: 1st, 5th, 10th, 15th, 20th, 25th")
    print()
    
    try:
        # Create progressive frames
        frames = create_progressive_frames(
            all_dates=all_dates,
            hours=[local_noon_utc],
            satellite="east",
            domain="F",
            coarsening_factor=2,
            cache_dir="/Users/thomas/Documents/GOES-IMAGES",
            verbose=True
        )
        
        # Create video
        create_video_from_frames(
            frames=frames,
            output_path="progressive_video_output",
            filename="goes_east_progressive_averaging.mp4",
            fps=None,  # Auto-calculate for 6s duration
            verbose=True
        )
        
        print("=" * 70)
        print("✓ Progressive averaging video completed successfully!")
        print(f"✓ Output: progressive_video_output/goes_east_progressive_averaging.mp4")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)