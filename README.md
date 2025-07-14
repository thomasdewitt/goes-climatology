# GOES Climatology

Python scripts for creating climate visualizations and videos from GOES-16/17 satellite data. Videos and images can be found in the `*_output/` folders.

**Note**: The `goes_west_/` folder contains full resolution images (~5000x5000 pixels), while other outputs use GOES-East data at half resolution (configurable in scripts).

**Citation**: If you use these visualizations, please cite the associated blog post (link upcoming).

## Requirements

- **Storage**: 100s of GB to 1 TB disk space for downloading satellite imagery, depending on desired outputs
- **Python packages**: `goes2go`, `xarray`, `matplotlib`, `opencv-python`, `numpy`, `PIL`

## Main Scripts

- **`goes_climate_viz.py`** - Core module for downloading, averaging, and caching GOES data
- **`average_day_video.py`** - Creates 24-hour progression videos showing average daily cycles  
- **`average_year_video.py`** - Creates seasonal progression videos through the year
- **`progressive_averaging_video.py`** - Shows progressive temporal averaging effects
- **`monthly_noon_climatology.py`** - Generates monthly climatology images
- **`random_seasonal_images.py`** - Creates individual seasonal comparison images

## Data Sources

- **Satellite**: GOES-16 (East) and GOES-17 (West)
- **Instrument**: Advanced Baseline Imager (ABI)
- **Data provider**: NOAA/NESDIS via AWS Open Data
- **Access method**: `goes2go` Python library
- **Temporal coverage**: 2018-present (GOES-16 operational)