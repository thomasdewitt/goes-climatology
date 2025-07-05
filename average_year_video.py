#!/usr/bin/env python3
"""
Average Year Video Generator

Creates a video showing seasonal progression through moving averages of N days
across all years 2018-2024. Each frame shows the average of N consecutive dates
(e.g., 1/1, 1/5, 1/10, 1/15, 1/20, 1/25) across all years, then moves forward
by one date position for the next frame.

Total video duration: 10 seconds
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import cv2
import tempfile
import os
from goes_climate_viz import download_and_average_goes_images


def create_seasonal_frames(n_days, hours, satellite, domain, coarsening_factor, cache_dir, verbose=True):
    """
    Create seasonal progression frames with moving averages of N days.
    
    Args:
        n_days: Number of consecutive days to average for each frame (default 6)
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
    
    # Create all dates for all years (same as monthly_noon_climatology.py)
    all_dates_by_position = []
    for year in range(2018, 2025):  # 7 years: 2018-2024
        for month in range(1, 13):  # 12 months
            for day in [1, 5, 10, 15, 20, 25]:  # 6 days per month
                all_dates_by_position.append(datetime(year, month, day))
    
    # Organize dates by position in year (72 positions: 12 months × 6 days)
    # Each position contains dates from all 7 years
    dates_by_year_position = {}
    for date in all_dates_by_position:
        # Calculate position in year (0-71)
        position = (date.month - 1) * 6 + ([1, 5, 10, 15, 20, 25].index(date.day))
        if position not in dates_by_year_position:
            dates_by_year_position[position] = []
        dates_by_year_position[position].append(date)
    
    # Sort positions and create sliding window
    positions = sorted(dates_by_year_position.keys())
    n_positions = len(positions)
    
    if verbose:
        print(f"Total positions in year: {n_positions}")
        print(f"Moving average window: {n_days} consecutive date positions")
        print(f"Each position contains dates from {len(dates_by_year_position[positions[0]])} years")
    
    # Create frames using sliding window of N consecutive positions
    for start_pos in range(0, n_positions, 2):
        # Get N consecutive positions (wrapping around at end of year)
        window_positions = []
        for i in range(n_days):
            pos_idx = (start_pos + i) % n_positions
            window_positions.append(positions[pos_idx])
        
        # Collect all dates from these positions across all years
        frame_dates = []
        for pos in window_positions:
            frame_dates.extend(dates_by_year_position[pos])
        
        if verbose:
            first_date = sorted(frame_dates)[0]
            last_date = sorted(frame_dates)[-1]
            frame_num = (start_pos // 2) + 1
            total_frames = (n_positions + 1) // 2
            print(f"\nFrame {frame_num}/{total_frames}: {len(frame_dates)} dates")
            print(f"  Date range: {first_date.strftime('%m/%d')} to {last_date.strftime('%m/%d')} (all years)")
            print(f"  Positions: {window_positions}")
        
        # Use existing function to average all dates for this frame
        try:
            averaged_image = download_and_average_goes_images(
                hours=hours,
                dates=frame_dates,
                satellite=satellite,
                coarsening_factor=coarsening_factor,
                domain=domain,
                output_path=tempfile.gettempdir(),  # Temporary output
                save_format="png",
                use_cache=True,
                cache_dir=cache_dir,
                verbose=False  # Suppress detailed output
            )
            frames.append(averaged_image)
            
        except Exception as e:
            print(f"Error creating frame {start_pos + 1}: {e}")
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


def main(n_days=6):
    """Generate average year seasonal progression video."""
    
    print("=" * 70)
    print("GOES Average Year Video Generator")
    print("=" * 70)
    print("Creating video showing seasonal progression through the year")
    print(f"Moving average window: {n_days} consecutive date positions")
    print("Years: 2018-2024 (7 years of data)")
    print("Total duration: 6 seconds")
    print("=" * 70)
    
    # Use same configuration as monthly_noon_climatology.py
    local_noon_utc = 17
    
    try:
        # Create seasonal progression frames
        frames = create_seasonal_frames(
            n_days=n_days,
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
            output_path="average_year_output",
            filename=f"goes_east_average_year_n{n_days}.mp4",
            fps=None,  # Auto-calculate for 10s duration
            verbose=True
        )
        
        print("=" * 70)
        print("✓ Average year video completed successfully!")
        print(f"✓ Output: average_year_output/goes_east_average_year_n{n_days}.mp4")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    import sys
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate GOES average year video')
    parser.add_argument('--n-days', type=int, default=6, 
                       help='Number of consecutive days to average (default: 6)')
    args = parser.parse_args()
    
    success = main(n_days=args.n_days)
    sys.exit(0 if success else 1)