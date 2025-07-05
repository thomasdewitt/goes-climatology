#!/usr/bin/env python3
"""
Random Seasonal Images Generator

Creates 2 static images each for March and June, randomly selected from 
the 2018-2024 time period using the same date sampling as the climatology scripts.
"""

import numpy as np
from datetime import datetime
from pathlib import Path
import random
from goes_climate_viz import download_and_average_goes_images


def generate_random_seasonal_images():
    """Generate random images for March and June."""
    
    print("=" * 70)
    print("GOES Random Seasonal Images Generator")
    print("=" * 70)
    print("Creating 2 random images each for March and June")
    print("Time period: 2018-2024")
    print("Days per month: 1st, 5th, 10th, 15th, 20th, 25th")
    print("=" * 70)
    
    # Configuration
    local_noon_utc = 17
    satellite = "east"
    domain = "F"
    coarsening_factor = 2
    cache_dir = "/Users/thomas/Documents/GOES-IMAGES"
    output_path = "random_seasonal_output"
    
    # Create all dates for March and June (same sampling as climatology)
    march_dates = []
    june_dates = []
    
    for year in range(2018, 2025):
        # March dates
        for day in [1, 5, 10, 15, 20, 25]:
            march_dates.append(datetime(year, 3, day))
        
        # June dates
        for day in [1, 5, 10, 15, 20, 25]:
            june_dates.append(datetime(year, 6, day))
    
    print(f"Available March dates: {len(march_dates)}")
    print(f"Available June dates: {len(june_dates)}")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Randomly select 2 dates from each month
    selected_march = random.sample(march_dates, 2)
    selected_june = random.sample(june_dates, 2)
    
    print(f"\nSelected March dates:")
    for i, date in enumerate(selected_march, 1):
        print(f"  {i}: {date.strftime('%Y-%m-%d')}")
    
    print(f"\nSelected June dates:")
    for i, date in enumerate(selected_june, 1):
        print(f"  {i}: {date.strftime('%Y-%m-%d')}")
    
    # Create output directory
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Generate March images
    print(f"\n{'='*50}")
    print("Generating March images...")
    print(f"{'='*50}")
    
    for i, date in enumerate(selected_march, 1):
        print(f"\nProcessing March image {i}: {date.strftime('%Y-%m-%d')}")
        try:
            download_and_average_goes_images(
                hours=[local_noon_utc],
                dates=[date],
                satellite=satellite,
                coarsening_factor=coarsening_factor,
                domain=domain,
                output_path=output_path,
                save_format="png",
                use_cache=True,
                cache_dir=cache_dir,
                verbose=True
            )
            # The function saves as goes_east_climate_avg.png, so rename it
            old_file = Path(output_path) / "goes_east_climate_avg.png"
            new_file = Path(output_path) / f"march_{date.strftime('%Y%m%d')}.png"
            if old_file.exists():
                old_file.rename(new_file)
            print(f"✓ March image {i} saved: {new_file}")
            
        except Exception as e:
            print(f"❌ Error creating March image {i}: {e}")
    
    # Generate June images
    print(f"\n{'='*50}")
    print("Generating June images...")
    print(f"{'='*50}")
    
    for i, date in enumerate(selected_june, 1):
        print(f"\nProcessing June image {i}: {date.strftime('%Y-%m-%d')}")
        try:
            download_and_average_goes_images(
                hours=[local_noon_utc],
                dates=[date],
                satellite=satellite,
                coarsening_factor=coarsening_factor,
                domain=domain,
                output_path=output_path,
                save_format="png",
                use_cache=True,
                cache_dir=cache_dir,
                verbose=True
            )
            # The function saves as goes_east_climate_avg.png, so rename it
            old_file = Path(output_path) / "goes_east_climate_avg.png"
            new_file = Path(output_path) / f"june_{date.strftime('%Y%m%d')}.png"
            if old_file.exists():
                old_file.rename(new_file)
            print(f"✓ June image {i} saved: {new_file}")
            
        except Exception as e:
            print(f"❌ Error creating June image {i}: {e}")
    
    print(f"\n{'='*70}")
    print("✓ Random seasonal images completed!")
    print(f"✓ Output directory: {output_path}/")
    print(f"✓ Files: march_YYYYMMDD.png, june_YYYYMMDD.png")
    print(f"{'='*70}")


if __name__ == "__main__":
    import sys
    try:
        generate_random_seasonal_images()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)