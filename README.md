# IMERG Data Downloader & Extractor

https://gpm-imergdl-v7-de.streamlit.app/

![Python](https://img.shields.io/badge/Python-3.x-blue)  
![License](https://img.shields.io/badge/License-MIT-green)  

This repository contains a Python-based tool for downloading and extracting GPM IMERG V07 precipitation data using OPeNDAP, Streamlit, and shapefile-based area selection. It supports NASA Earthdata authentication and CSV coordinate-based data extraction.

## Features
- 📥 **Download IMERG V07 Data**: Retrieve subsetted precipitation data using OPeNDAP.
- 📌 **Shapefile-Based Area Selection**: Clip IMERG data to a specific region.
- ⚡ **Multi-Threaded Downloading**: Speeds up the process.
- 🔍 **CSV Coordinate Extraction**: Extracts precipitation values based on provided CSV points.
- 📊 **Formatted Excel Output**: Saves data in a structured multi-row format.
- 🖥 **Streamlit UI**: Provides a user-friendly interface.

## Installation
Ensure you have Python 3.10+ installed, then clone this repository:

```bash
git clone https://github.com/yourusername/IMERG-Downloader.git
cd IMERG-Downloader
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
Run the Streamlit app:

```bash
streamlit run app.py
```

### Required Inputs
- **NASA Earthdata credentials** (set up in `.env` or Streamlit UI)
- **Shapefile** defining the region of interest
- **CSV file** with coordinates for data extraction

## Output
- **Extracted Excel file** with multi-row headers (ID, Lon, Lat, Date, Precipitation)
- **Clipped IMERG precipitation plots** with shapefile overlay

## Troubleshooting
If you encounter dependency issues, ensure the following packages are installed:

```bash
pip install xarray netCDF4 h5netcdf requests pandas geopandas numpy streamlit
```

## License
This project is licensed under the MIT License.

## Contributing
Pull requests are welcome! For major changes, open an issue first to discuss your ideas.

## Acknowledgments
- **NASA GPM IMERG** dataset
- **Streamlit** for deployment support
- **xarray & geopandas** for geospatial data handling

