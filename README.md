# GPM Precipitation Data IMERG DL V7 Data Downloader & Extractor

[https://gpm-imergdl-v7-de.streamlit.app/](https://gpm-precipiation.streamlit.app/)

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
- 🔐 **User Authentication & Quota System**: Track and limit downloads per user
- 📈 **Usage Monitoring**: Real-time quota tracking with daily and monthly limits
- 👨‍💼 **Admin Panel**: Manage users and quotas
- 💳 **Payment & Subscriptions**: Upgrade quota limits with flexible pricing tiers (NEW!)
- 🎁 **Multiple Tiers**: Free, Standard, Professional, and Enterprise plans (NEW!)

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

### Quota System (NEW!)
The application now includes a comprehensive quota management system:

#### For New Users:
1. **Register** in the sidebar with username, email, and password
2. Default quotas: 10 files/day, 100 files/month
3. **Login** to access the downloader
4. Monitor your quota usage in real-time

#### Upgrade Your Plan 💳:
Need more quota? Choose from our flexible pricing tiers:
- **Gratis**: 10 daily / 100 monthly - $0/month or Rp0/bulan
- **Standar**: 100 daily / 500 monthly - $9.99/month or Rp 150,000/bulan
- **Profesional**: 5000 daily / 1000 monthly - $29.99/month or Rp450,000/bulan
- **Enterprise**: 1,000 daily / 5,000 monthly - $99.99/month or Rp1,500,000/bulan

**Upgrade in seconds**:
1. Login to your account
2. Click "View All Plans & Upgrade" in sidebar
3. Select your tier and complete payment
4. Instant activation!

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

