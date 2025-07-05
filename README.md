# GOES Climate Visualization System

A comprehensive Python toolkit for creating climate visualizations and videos from GOES-16/17 satellite data. This system generates climatological averages, temporal progression videos, and seasonal comparisons using 7 years of satellite imagery (2018-2024).

## Overview

This project provides tools to:
- **Download and process** GOES satellite imagery with automatic caching
- **Create temporal videos** showing daily and yearly climate patterns  
- **Generate climatological averages** for any month or season
- **Compare random seasonal images** from different years
- **Support multiple temporal resolutions** (hourly, 30-minute intervals)

## Scripts Overview

### Core Module
- **`goes_climate_viz.py`** - Main processing module for downloading, averaging, and caching GOES data

### Video Generators
- **`average_day_video.py`** - Creates 24-hour progression videos showing average daily cycles
- **`average_year_video.py`** - Creates seasonal progression videos using enhanced odd-day sampling
- **`progressive_averaging_video.py`** - Shows progressive temporal averaging effects

### Image Generators  
- **`monthly_noon_climatology.py`** - Generates monthly climatology images
- **`random_seasonal_images.py`** - Creates random seasonal comparison images

## Installation

### Prerequisites
```bash
conda create -n main python=3.10
conda activate main
```

### Required Packages
```bash
pip install goes2go xarray matplotlib opencv-python numpy pathlib
```

### System Requirements
- **Storage**: ~10-50GB for image cache (configurable)
- **Memory**: 8GB+ RAM recommended for video generation
- **Network**: Stable internet connection for GOES data downloads

## Quick Start

### 1. Generate Monthly Climatology
```bash
conda activate main
python monthly_noon_climatology.py
```
**Output**: `decadal_climatology_2015_2024/goes_east_noon_climatology.png`

### 2. Create Daily Progression Video (Hourly)
```bash
python average_day_video.py --month 3 --days 1 10 20
```
**Output**: `average_day_output/goes_east_average_day_march_days1_10_20.mp4`

### 3. Create Daily Progression Video (30-minute intervals)
```bash
python average_day_video.py --month 6 --days 15 --temporal-resolution 30min
```
**Output**: `average_day_output/goes_east_average_day_june_days15_30min.mp4`

### 4. Create Seasonal Progression Video
```bash
python average_year_video.py --n-days 6
```
**Output**: `average_year_output/goes_east_average_year_n6_odddays.mp4`

## Detailed Usage

### Average Day Videos

**Purpose**: Shows how weather patterns evolve through a typical day using multi-year averages.

```bash
python average_day_video.py [OPTIONS]
```

**Options**:
- `--month INT`: Month number (1-12, default: 3 for March)
- `--days INT [INT ...]`: Days to include (default: 1 10 20)  
- `--temporal-resolution {hourly,30min}`: Time intervals (default: hourly)

**Examples**:
```bash
# March daily cycle with 3 days, hourly (24 frames)
python average_day_video.py --month 3 --days 1 10 20

# June daily cycle, 30-minute intervals (48 frames)  
python average_day_video.py --month 6 --days 15 --temporal-resolution 30min

# December holiday period progression
python average_day_video.py --month 12 --days 20 21 22 23 24 25
```

### Average Year Videos

**Purpose**: Shows seasonal progression through the year using enhanced temporal sampling.

```bash
python average_year_video.py [OPTIONS]
```

**Options**:
- `--n-days INT`: Moving average window size (default: 6)

**Features**:
- **Enhanced sampling**: Uses all odd days (1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31)
- **~192 temporal positions** vs original 72 (2.7x more data)
- **Smart stride**: Automatically calculated for ~40 frames
- **6-second duration**: Optimized for smooth viewing

**Examples**:
```bash
# Standard seasonal progression (6-day averaging)
python average_year_video.py --n-days 6

# Smoother progression (8-day averaging)  
python average_year_video.py --n-days 8

# More detailed progression (4-day averaging)
python average_year_video.py --n-days 4
```

### Other Scripts

**Monthly Climatology**:
```bash
python monthly_noon_climatology.py
```
- Generates 12-month climatology grid
- Uses 17:00 UTC as "local noon" for GOES-East

**Random Seasonal Images**:
```bash
python random_seasonal_images.py  
```
- Creates 2 random images each for March and June
- Uses same temporal sampling as climatology scripts

**Progressive Averaging Video**:
```bash
python progressive_averaging_video.py
```
- Shows effect of increasing temporal averaging
- Demonstrates noise reduction with more data

## Output Directory Structure

```
├── average_day_output/           # Daily progression videos
│   ├── goes_east_average_day_march_days1_10_20.mp4
│   └── goes_east_average_day_june_days15_30min.mp4
├── average_year_output/          # Seasonal progression videos  
│   ├── goes_east_average_year_n6_odddays.mp4
│   └── goes_east_average_year_n8_odddays.mp4
├── progressive_video_output/     # Progressive averaging videos
│   └── goes_east_progressive_averaging.mp4
├── random_seasonal_output/       # Random seasonal comparisons
│   ├── march_20190305.png
│   └── june_20200625.png
└── decadal_climatology_2015_2024/ # Monthly climatology
    └── goes_east_noon_climatology.png
```

## Configuration

### Cache Directory
**Default**: `/Users/thomas/Documents/GOES-IMAGES`

**Modify in scripts**:
```python
cache_dir = "/your/preferred/cache/path"
```

### Satellite Configuration
**Default**: GOES-16 East, Full Disk (F), 2x coarsening

**Available options**:
- **Satellite**: "east" (GOES-16) or "west" (GOES-17)
- **Domain**: "F" (Full Disk), "C" (CONUS), "M1/M2" (Mesoscale)
- **Coarsening**: 1, 2, 4, 8 (higher = smaller files, lower resolution)

### Time Configuration
**Default settings**:
- **Years**: 2018-2024 (GOES-16 operational period)
- **Local noon**: 17:00 UTC (for GOES-East at 75.2°W)
- **Temporal sampling**: Hourly or 30-minute intervals

## Technical Details

### Data Processing Pipeline
1. **Download**: Uses `goes2go` library for GOES data access
2. **Caching**: Automatic .npy file caching for processed images  
3. **Averaging**: Multi-year temporal averaging with NaN handling
4. **Coarsening**: Optional spatial downsampling for performance
5. **Video encoding**: OpenCV-based MP4 generation

### Memory Management
- **Subprocess isolation**: Downloads in separate processes to prevent memory leaks
- **Automatic cleanup**: Temporary files and corrupted downloads removed
- **Efficient caching**: Processed data cached to avoid re-downloading

### Performance Optimization
- **Parallel processing**: Multi-core support for large datasets
- **Smart caching**: Skip processing if cached data exists
- **Adaptive stride**: Frame count automatically optimized for video length

## Troubleshooting

### Common Issues

**1. Memory errors with 30-minute videos**:
```bash
# Use fewer days or reduce coarsening factor
python average_day_video.py --days 1 --temporal-resolution 30min
```

**2. Missing GOES data**:
- Some dates/times may not be available in archive
- Check verbose output for download failures
- Consider adjusting date ranges

**3. Video encoding issues**:
```bash
# Check OpenCV installation
python -c "import cv2; print(cv2.__version__)"

# Try different codec if needed (edit create_video_from_frames function)
```

**4. Slow downloads**:
- Check internet connection
- Use cache directory on fast storage (SSD)
- Consider running overnight for large datasets

### Cache Management
```bash
# Check cache size
du -sh /Users/thomas/Documents/GOES-IMAGES

# Clear cache if needed
rm -rf /Users/thomas/Documents/GOES-IMAGES/*.npy
```

## Data Sources

- **Satellite**: GOES-16 (East) and GOES-17 (West)
- **Instrument**: Advanced Baseline Imager (ABI)
- **Data provider**: NOAA/NESDIS via AWS Open Data
- **Access method**: `goes2go` Python library
- **Temporal coverage**: 2018-present (GOES-16 operational)

## Citation

If you use this code for research, please acknowledge:
- **GOES-16/17 data**: NOAA/NESDIS
- **Data access**: `goes2go` library by Brian Blaylock
- **Processing**: Custom climate visualization pipeline

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure adequate disk space and memory
4. Check GOES data availability for your requested dates

---

**Generated with Claude Code** - A comprehensive toolkit for GOES satellite climate visualization and analysis.