#!/usr/bin/env python3
"""
GOES Climate Visualization Pipeline

This script downloads GOES satellite data, processes it for climate visualization
by averaging images across time periods, and outputs results as PNG or MP4.
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Optional, Union
import os
from pathlib import Path
import warnings
import hashlib
import shutil
import multiprocessing as mp

import logging
import io
from contextlib import redirect_stdout, redirect_stderr

# Silence noisy warnings 
warnings.filterwarnings("ignore", category=FutureWarning)

def _download_worker(target_time, sat_num, domain, return_dict):
    """
    Download a single GOES image in a dedicated subprocess to avoid the
    memory leaks observed in the goes2go library. The RGB numpy array is
    returned via a shared dict so literally only the array survives.
    """
    from goes2go import GOES
    import numpy as np
    from pathlib import Path
    import shutil

    G = GOES(satellite=sat_num, domain=domain)
    # Suppress verbose console output from goes2go
    with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
        ds = G.nearesttime(target_time, download=True)

    # Clean up download directory to keep things tidy
    data_dir = Path("/Users/thomas/data")
    if data_dir.exists():
        shutil.rmtree(data_dir)

    if ds is None:
        return_dict["data"] = None
        return

    data = np.nan_to_num(ds.rgb.TrueColor(), nan=0.0)
    return_dict["data"] = data

try:
    from goes2go import GOES
except ImportError:
    print("Warning: goes2go not installed. Install with: pip install goes2go")
    GOES = None

try:
    import xarray as xr
except ImportError:
    print("Warning: xarray not installed. Install with: pip install xarray")
    xr = None

try:
    import cv2
except ImportError:
    print("Warning: opencv-python not installed. Install with: pip install opencv-python")
    cv2 = None


def download_and_average_goes_images(
    *,
    hours: List[int],
    dates: List[datetime], 
    satellite: str = "east",
    coarsening_factor: int = 2,
    domain: str = "F",
    output_path: str = "output",
    save_format: str = "png",
    use_cache: bool = True,
    cache_dir: str = "/Users/thomas/Documents/GOES-IMAGES",
    verbose: bool = True,
    minutes: List[int] = [0]
) -> np.ndarray:
    """
    Download GOES satellite images and create averaged climatology.
    
    Args:
        hours: List of hours (0-23) to download data for
        dates: List of datetime objects for specific dates
        satellite: "east" or "west" 
        coarsening_factor: Factor to coarsen images (default 2, 2x2 averaging)
        domain: Domain (C=CONUS, F=Full Disk, M1/M2=Mesoscale)
        output_path: Directory to save outputs
        save_format: "png" or "mp4"
        use_cache: Whether to use local file caching (default True)
        cache_dir: Directory for cached .npy files
        verbose: Whether to print progress messages (default False)
        minutes: List of minutes (0, 30) for sub-hourly sampling (default [0])
        
    Returns:
        numpy array of averaged image data
    """
    
    if GOES is None:
        raise ImportError("goes2go package is required. Install with: pip install goes2go")
    
    if xr is None:
        raise ImportError("xarray package is required. Install with: pip install xarray")
    
    # Create output and cache directories
    Path(output_path).mkdir(parents=True, exist_ok=True)
    if use_cache:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
    
    # Validate inputs
    if satellite.lower() not in ["east", "west"]:
        raise ValueError("satellite must be 'east' or 'west'")
    
    if not all(0 <= h <= 23 for h in hours):
        raise ValueError("hours must be between 0 and 23")
    
    if not all(m in [0, 30] for m in minutes):
        raise ValueError("minutes must be 0 or 30 for 30-minute intervals")
    
    sat_num = 16 if satellite.lower() == "east" else 17
    
    if verbose:
        total_times = len(dates) * len(hours) * len(minutes)
        print(f"Downloading GOES-{sat_num} data for {len(dates)} dates, {len(hours)} hours, {len(minutes)} minutes each")
        print(f"Total time points: {total_times}")
    
    total_image = None
    successful_downloads = 0
    
    for date in dates:
        for hour in hours:
            for minute in minutes:
                try:
                    # Create datetime for specific hour and minute
                    target_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                    # Create cache filename based on parameters
                    cache_key = f"goes{sat_num}_{domain}_{target_time.strftime('%Y%m%d_%H%M')}_c{coarsening_factor}"
                    cache_file = Path(cache_dir) / f"{cache_key}.npy"
                
                    # Check cache first
                    if use_cache and cache_file.exists():
                        if verbose:
                            print(f"Loading from cache: {target_time.strftime('%Y-%m-%d %H:%M UTC')}")
                        data = np.load(cache_file)
                    else:
                        try:
                            # Download GOES data in a separate subprocess to avoid goes2go
                            # memory bloat.  NOTE: I know this is a brutalist approach
                            manager = mp.Manager()
                            return_dict = manager.dict()
                            p = mp.Process(
                                target=_download_worker,
                                args=(target_time, sat_num, domain, return_dict),
                            )
                            p.start()
                            p.join()

                            data = return_dict.get("data", None)
                            if data is None:
                                if verbose:
                                    print(f"No data available for {target_time}")
                                continue
                        except Exception as e:
                            if "truncated file" in str(e) or "Unable to synchronously open file" in str(e):
                                if verbose:
                                    print(f"  ❌ Corrupted file detected for {target_time.strftime('%Y-%m-%d %H:%M UTC')}")
                                    print(f"  🗑️  Cleaning up corrupted downloads...")
                                # Clean up potentially corrupted downloads
                                data_dir = Path("/Users/thomas/data")
                                if data_dir.exists():
                                    import shutil
                                    shutil.rmtree(data_dir)
                                    if verbose:
                                        print(f"  ✓ Cleaned up download directory")
                            if verbose:
                                print(f"  ❌ Error downloading: {target_time.strftime('%Y-%m-%d %H:%M UTC')}: {e}")
                            continue
                    
                        # Handle NaN values - preserve RGB channels
                        # data = np.nan_to_num(data, nan=0.0)  # Already done in subprocess
                        
                        # Coarsen if requested
                        if coarsening_factor > 1:
                            data = coarsen_by_averaging(data, coarsening_factor)
                        
                        # Cache the coarsened data
                        if use_cache:
                            np.save(cache_file, data)
                            if verbose:
                                print(f"Cached coarsened data: {cache_file}")
                    
                    # Initialize total_image on first successful download
                    if total_image is None:
                        total_image = data.astype(np.float64)  # Use float64 for accumulation
                    else:
                        total_image += data.astype(np.float64)
                    
                    # Delete current image data from memory
                    del data
                    
                    successful_downloads += 1
                    
                except Exception as e:
                    print(f"Error downloading {target_time}: {str(e)}")
                    continue
    
    if total_image is None:
        raise RuntimeError("No images were successfully downloaded")
    
    if verbose:
        print(f"Successfully downloaded {successful_downloads} images")
    
    # Average all images by dividing total by count
    if verbose:
        print("Computing climatological average...")
    averaged_image = (total_image / successful_downloads).astype(np.float32)
    
    # Save output
    if save_format.lower() == "png":
        save_as_png(averaged_image, output_path, f"goes_{satellite}_climate_avg.png", verbose=verbose)
    elif save_format.lower() == "mp4":
        save_as_mp4(all_images, output_path, f"goes_{satellite}_climate_sequence.mp4", verbose=verbose)
    
    return averaged_image


def coarsen_by_averaging(data: np.ndarray, factor: int) -> np.ndarray:
    """
    Coarsen RGB array by averaging over blocks.
    
    Args:
        data: 3D numpy array (H, W, C) for RGB
        factor: Coarsening factor
        
    Returns:
        Coarsened array
    """
    if factor == 1:
        return data
    
    # Handle RGB data (H, W, C)
    h, w, c = data.shape
    new_h = (h // factor) * factor
    new_w = (w // factor) * factor
    
    trimmed = data[:new_h, :new_w, :]
    
    # Reshape and average - preserve color channels
    coarsened = trimmed.reshape(new_h // factor, factor, new_w // factor, factor, c).mean(axis=(1, 3))
    
    return coarsened


def save_as_png(data: np.ndarray, output_path: str, filename: str, *, verbose: bool = False):
    """Save RGB array as PNG image with no decorations."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(data, origin='upper')
    ax.set_axis_off()  # Remove all axes, labels, ticks
    
    filepath = Path(output_path) / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    if verbose:
        print(f"Saved PNG: {filepath}")


def save_as_mp4(images: List[np.ndarray], output_path: str, filename: str, *, verbose: bool = False, fps: int = 5):
    """Save list of images as MP4 video."""
    if cv2 is None:
        print("Warning: opencv-python not available, cannot save MP4")
        return
    
    if not images:
        return
    
    # Normalize all images to 0-255 range
    normalized_images = []
    for img in images:
        norm_img = ((img - img.min()) / (img.max() - img.min()) * 255).astype(np.uint8)
        normalized_images.append(norm_img)
    
    h, w = normalized_images[0].shape
    filepath = str(Path(output_path) / filename)
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, fps, (w, h), isColor=False)
    
    for img in normalized_images:
        out.write(img)
    
    out.release()
    if verbose:
        print(f"Saved MP4: {filepath}")


if __name__ == "__main__":
    # Example usage
    from datetime import datetime
    
    hours = [9]  # 9 UTC
    dates = [datetime(2020, 1, 1), datetime(2025, 1, 1)]
    
    try:
        result = download_and_average_goes_images(
            hours=hours,
            dates=dates,
            satellite="east",
            coarsening_factor=1,
            output_path="climate_output",
            save_format="png",
            verbose=False
        )
        print("Pipeline completed successfully!")
        print(f"Average image shape: {result.shape}")
        
    except Exception as e:
        print(f"Error: {e}")