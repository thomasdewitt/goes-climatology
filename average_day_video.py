#!/usr/bin/env python3
"""
Average Day Video Generator

Creates a video showing the progression of an average day through hourly averages.
Each frame shows the average of all images at a specific hour (00Z, 01Z, 02Z, etc.)
across all years for specified days in a given month.

Default: March, days 1, 10, 20 across 2018-2024
24 frames (00Z-23Z), 6 seconds duration
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import cv2
import tempfile
import os
from goes_climate_viz import download_and_average_goes_images


def create_hourly_frames(month, days, hours, satellite, domain, coarsening_factor, cache_dir, verbose=True):
    """
    Create hourly progression frames showing average day cycle.
    
    Args:
        month: Month number (1-12)
        days: List of days to include
        hours: List of hours (0-23) to create frames for
        satellite: "east" or "west"
        domain: Domain (F=Full Disk, C=CONUS, etc.)
        coarsening_factor: Factor to coarsen images
        cache_dir: Directory for cached images
        verbose: Whether to print progress
        
    Returns:
        List of averaged image arrays for each hour
    """
    frames = []
    
    # Create all dates for the specified month and days across all years
    all_dates = []
    for year in range(2018, 2025):  # 7 years: 2018-2024
        for day in days:
            all_dates.append(datetime(year, month, day))
    
    month_name = datetime(2000, month, 1).strftime('%B')
    
    if verbose:
        print(f"Processing {month_name} days {days} across {len(all_dates)} total dates")
        print(f"Years: 2018-2024")
        print(f"Creating {len(hours)} hourly frames")
    
    # Create frames for each hour
    for hour in hours:
        if verbose:
            print(f"\nCreating frame for hour {hour:02d}Z ({len(all_dates)} dates)")
        
        try:
            # Use existing function to average all dates for this hour
            averaged_image = download_and_average_goes_images(
                hours=[hour],
                dates=all_dates,
                satellite=satellite,
                coarsening_factor=coarsening_factor,
                domain=domain,
                output_path='/Users/thomas/Documents/GOES-IMAGES',  # Temporary output
                save_format="png",
                use_cache=True,
                cache_dir=cache_dir,
                verbose=True  # Suppress detailed output
            )
            frames.append(averaged_image)
            
        except Exception as e:
            print(f"Error creating frame for hour {hour:02d}Z: {e}")
            continue
    
    return frames


def create_video_from_frames(frames, output_path, filename, fps=None, verbose=True):
    """
    Create MP4 video from list of frames.
    
    Args:
        frames: List of RGB image arrays
        output_path: Directory to save video
        filename: Output filename
        fps: Frames per second (calculated for 6s duration if None)
        verbose: Whether to print progress
    """
    if not frames:
        print("No frames to create video")
        return
    
    # Calculate FPS for 6-second duration
    if fps is None:
        fps = len(frames) / 6.5     ########### EXACTLY 6 BREAKS VIDEO FOR UNKNOWN REASON ###########
    
    # Create output directory relative to current working directory
    output_path = os.path.join(os.getcwd(), output_path)
    os.makedirs(output_path, exist_ok=True)
    
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
        filepath = os.path.join(output_path, filename)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filepath, fourcc, fps, (w, h), isColor=True)
        
        for frame in video_frames:
            # print(np.count_nonzero(np.isnan(frame)), "NaNs in frame")
            # print('Max value in frame:', np.nanmax(frame))
            # print('Mean value in frame:', np.nanmean(frame))
            # print('Mean of first bit:', np.mean(frame[0:10,0:10,:]))
            out.write(frame)
        
        out.release()
        
        if verbose:
            print(f"✓ Video saved: {filepath}")
            print(f"✓ Duration: {len(frames)/fps:.1f} seconds")
            print(f"✓ FPS: {fps:.1f}")
            print(f"✓ Total frames: {len(frames)}")



def main(month=3, days=[1, 10, 20]):
    """Generate average day progression video."""
    
    month_name = datetime(2000, month, 1).strftime('%B')
    
    print("=" * 70)
    print("GOES Average Day Video Generator")
    print("=" * 70)
    print(f"Creating video showing hourly progression through average day")
    print(f"Month: {month_name}")
    print(f"Days: {days}")
    print(f"Hours: 00Z-23Z (24 frames)")
    print(f"Years: 2018-2024 (7 years of data)")
    print("Total duration: 6 seconds")
    print("=" * 70)
    
    # All hours 00Z through 23Z
    hours = list(range(24))
    # hours = [1]*24
    
    try:
        # Create hourly progression frames
        frames = create_hourly_frames(
            month=month,
            days=days,
            hours=hours,
            satellite="east",
            domain="F",
            coarsening_factor=2,
            cache_dir="/Users/thomas/Documents/GOES-IMAGES",
            verbose=True
        )
        # plt.imshow(frames[1])
        # plt.show()
        # exit()
        
        # Create video filename
        days_str = "_".join(map(str, days))
        filename = f"goes_east_average_day_{month_name.lower()}_days{days_str}.mp4"
        
        # Create video
        create_video_from_frames(
            frames=frames,
            output_path="average_day_output",
            filename=filename,
            fps=None,  # Auto-calculate for 6s duration
            verbose=True
        )
        
        print("=" * 70)
        print("✓ Average day video completed successfully!")
        print(f"✓ Output: average_day_output/{filename}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate GOES average day video')
    parser.add_argument('--month', type=int, default=3, 
                       help='Month number (1-12, default: 3 for March)')
    parser.add_argument('--days', nargs='+', type=int, default=[1, 10, 20],
                       help='Days to include (default: 1 10 20)')
    args = parser.parse_args()
    
    # Validate month
    if not 1 <= args.month <= 12:
        print("Error: Month must be between 1 and 12")
        sys.exit(1)
    
    # Validate days
    if not all(1 <= day <= 31 for day in args.days):
        print("Error: Days must be between 1 and 31")
        sys.exit(1)
    
    success = main(month=args.month, days=args.days)
    sys.exit(0 if success else 1)