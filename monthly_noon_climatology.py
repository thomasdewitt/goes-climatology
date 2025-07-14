#!/usr/bin/env python3
"""
Decadal Climate Climatology for GOES-East

Creates average images from days 1, 10, 20 of each month for 2015-2024
at local noon and morning times for GOES-East nadir point (75.2°W longitude).
"""

from datetime import datetime
from pathlib import Path
from goes_climate_viz import download_and_average_goes_images


def main():
    """Generate decadal climate climatology for 2015-2024."""
    
    print("=" * 70)
    print("GOES-East Decadal Climate Climatology - 2015-2024")
    print("=" * 70)
    print("Generating average images from days 1, 10, 20 of each month")
    print("Time: Local noon (17:00 UTC)")
    print("GOES-East nadir: 75.2°W longitude")
    print("=" * 70)
    
    # GOES-East is positioned at 75.2°W longitude
    # Local solar noon occurs when sun is highest at that longitude
    # 75.2°W is approximately 5 hours behind UTC (75.2/15 = ~5.0 hours)
    # So local noon (12:00 local) = 17:00 UTC
    local_noon_utc = 17
    
    # Create dates for days 1, 3,5,7,9,11,13,15,17,19,21,23,25,27 of each month for 2018-2024
    # GOES-16 operational data starts in 2018
    all_dates = []
    for year in range(2018, 2025):  # 7 years of operational data
        for month in range(1, 13):  # 12 months
            for day in [1, 3,5,7,9,11,13,15,17,19,21,23,25,27]:  # 3 days per month
            # for day in [1, 10, 20]:  # 3 days per month
                all_dates.append(datetime(year, month, day))

    all_dates = all_dates[:]

    print(f"Processing {len(all_dates)} dates across 7 years")
    print(f"Years: 2018-2024 (GOES-16 operational period)")
    print(f"Days per month: 1st, 10th, 20th")
    print()
    
    # Process noon climatology
    print("=" * 50)
    print("PROCESSING NOON CLIMATOLOGY (17:00 UTC)")
    print("=" * 50)
    
    try:
        result_noon = download_and_average_goes_images(
            hours=[local_noon_utc],  # 17:00 UTC = local noon at GOES-East nadir
            dates=all_dates,
            satellite="east",
            coarsening_factor=2, 
            domain="F",  # Full disk
            output_path="decadal_climatology_2015_2024",
            save_format="png"
        )
        
        # Rename noon output file
        noon_output = Path("decadal_climatology_2015_2024") / "goes_east_climate_avg.png"
        noon_final = Path("decadal_climatology_2015_2024") / f"goes_east_noon_climatology_{len(all_dates)}imgs.png"
        if noon_output.exists():
            noon_output.rename(noon_final)
        
    except Exception as e:
        print(f"❌ Error in noon processing: {e}")
        return False
    
    print(f"✓ Completed: {len(all_dates)} dates, noon only, 7 years (2018-2024)")
    return True
    
    return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)