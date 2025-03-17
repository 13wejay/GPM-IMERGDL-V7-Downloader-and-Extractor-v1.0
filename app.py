import os
import requests
import pandas as pd
import geopandas as gpd
import zipfile
import io
import streamlit as st
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import re

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

# Base OPeNDAP URL for IMERG
BASE_URL = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.07"

# Default NASA Earthdata credentials
DEFAULT_USERNAME = "wijaya_hydro"
DEFAULT_PASSWORD = "@huggingface4Free"
DEFAULT_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6IndpamF5YV9oeWRybyIsImV4cCI6MTc0NzI4MDA5NCwiaWF0IjoxNzQyMDk2MDk0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.kSdpjDTrv5vfG0Z2XU9APcxJ7AO0QZIhyM86aHWI468bparlRnJlQ72G-KMGxEILhEj4tGbTWM9QbGd6lC7fJ-MTQgDtH0D0G9EuhQ6xIOtdoMaqTqd3vRxoV3eVXHMkkLldJjrs2ISSNRoy9zvcg-S3yVljfHW_RLnc-l-EKDnRcG8EwMudMnWWl5P84tMZ5dTMApzu0hp4kAPkXjNBuG9mAKjBGcf8cydEopvLsIsHxUysFMHYL_XozvykEiX2YTN3fSLH4hk4K1eg7CABJoqxGK0o4aVV8jjqTFJWwgfPs4FOozQh8nGJ8b5_rCd3vukuVi2exm9CHTsWgW4Swg"

# Function to handle donwloadable ZIP file
def create_download_zip(output_dir, zip_filename):
    """Creates a ZIP file containing all extracted data for user download, excluding other ZIP files."""
    zip_path = os.path.join(output_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                if not file.endswith(".zip"):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.basename(file_path))
    
    return zip_path
    
# Function to handle shapefile upload
def handle_shapefile_upload(zip_bytes):
    """Extracts ZIP file containing a shapefile and returns the path to the .shp file."""
    extract_dir = "shapefile_extract"
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Find the .shp file
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".shp"):
                return os.path.join(root, file)
    
    raise FileNotFoundError("No .shp file found in the uploaded ZIP.")

# Function to download subsetted IMERG data
def download_subset_imerg(date, download_dir, token, bbox):
    """Downloads IMERG subsetted data from OPeNDAP using correct grid ordering."""
    year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
    min_lon, min_lat, max_lon, max_lat = bbox

    # Convert lat/lon to IMERG OPeNDAP grid indices
    def lat_to_index(lat):
        return int(round((lat + 90) / 0.1)) - 1

    def lon_to_index(lon):
        return int(round((lon + 180) / 0.1))

    # Get correctly ordered lat/lon indices
    lon_min_idx = lon_to_index(min_lon)
    lon_max_idx = lon_to_index(max_lon)
    lat_min_idx = lat_to_index(min_lat)
    lat_max_idx = lat_to_index(max_lat) 

    # Construct OPeNDAP URL using correct IMERG indexing
    filename = f"3B-DAY-L.MS.MRG.3IMERG.{year}{month}{day}-S000000-E235959.V07B.nc4"
    subset_url = f"{BASE_URL}/{year}/{month}/{filename}.nc4?precipitation[0:0][{lon_min_idx}:{lon_max_idx}][{lat_min_idx}:{lat_max_idx}],time,lon[{lon_min_idx}:{lon_max_idx}],lat[{lat_min_idx}:{lat_max_idx}]"
    
    # Define save path
    save_path = os.path.join(download_dir, f"IMERG_Subset_{year}{month}{day}.nc4")

    if os.path.exists(save_path):
        return save_path

    headers = {"Authorization": f"Bearer {token}"}

    # Download subset file
    with requests.get(subset_url, headers=headers, stream=True) as response:
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            with open(save_path, 'wb') as file, tqdm(
                desc=os.path.basename(save_path),
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    bar.update(len(chunk))
            return save_path
        else:
            return None

# Function to extract precipitation data
def extract_precipitation(nc_directory, csv_file, output_excel):
    """Extracts precipitation data and saves as an Excel file."""
    df_coords = pd.read_csv(csv_file)
    df_coords["ID"] = range(1, len(df_coords) + 1)

    nc_files = sorted([f for f in os.listdir(nc_directory) if f.endswith(".nc4")])
    for nc_file in nc_files:
        date_str = re.search(r"(\d{4}\d{2}\d{2})", nc_file).group(1)
        formatted_date = pd.to_datetime(date_str, format="%Y%m%d").strftime("%d-%b-%Y")

        ds = xr.open_dataset(os.path.join(nc_directory, nc_file))
        if "time" in ds.dims:
            ds = ds.isel(time=0)

        def extract_precip(row):
            try:
                value = ds["precipitation"].sel(lat=row["Lat"], lon=row["Lon"], method="nearest").values.item()
                return value if np.isfinite(value) else -9999
            except:
                return -9999

        df_coords[formatted_date] = df_coords.apply(extract_precip, axis=1)
        ds.close()

    formatted_df = df_coords.drop(columns=["ID"]).set_index(["Lon", "Lat"]).T
    formatted_df.index.name = "Date"
    formatted_df.columns = pd.MultiIndex.from_tuples(
        [(i + 1, col[0], col[1]) for i, col in enumerate(formatted_df.columns)], 
        names=["ID", "Lon", "Lat"]
    )
    formatted_df.to_excel(output_excel)
    
# Streamlit Interface
def main():
    st.title("GPM IMERGDL V7 Downloader and Extractor v1.0")
    st.write("Download, extract, and analyze GPM IMERGDL V7 data for a specified date range and area.")

    # Inputs for date range and file uploads
    start_date = st.text_input("Start Date (YYYY-MM-DD)", value="2025-01-01")
    end_date = st.text_input("End Date (YYYY-MM-DD)", value="2025-01-31")
    shapefile_zip = st.file_uploader("Upload Shapefile (ZIP) for Specific Area", type="zip")
    csv_file = st.file_uploader("Upload CSV File with Coordinates (ID,Lon,Lat)", type="csv")

    if st.button("Download and Process"):
        if not all([start_date, end_date, shapefile_zip, csv_file]):
            st.error("Please fill in all fields and upload all required files.")
            return

        download_dir = "IMERG_Downloads"
        os.makedirs(download_dir, exist_ok=True)

        try:
            st.write("Processing shapefile and extracting bounding box...")
            # Process shapefile
            shapefile_path = handle_shapefile_upload(shapefile_zip.getvalue())
            gdf = gpd.read_file(shapefile_path).to_crs(epsg=4326)
            bbox = gdf.total_bounds  
            st.write(f"Bounding Box: {bbox}")

            # Plot shapefile boundary
            fig, ax = plt.subplots(figsize=(6, 6))
            gdf.plot(ax=ax, edgecolor='black', facecolor='none')
            ax.set_title("Shapefile Boundary")
            st.pyplot(fig)

            st.write("Downloading and extracting data...")
            
            # Download and extract data
            dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)]
            results = [download_subset_imerg(date, download_dir, DEFAULT_TOKEN, bbox) for date in dates]

            # Extract precipitation data
            output_excel = os.path.join(download_dir, "IMERG_Extracted.xlsx")
            extract_precipitation(download_dir, csv_file, output_excel)

            # Create ZIP file for download
            zip_filename = "IMERG_Extracted.zip"
            zip_path = create_download_zip(download_dir, zip_filename)

            st.success("Download and extraction complete!")

            # Provide download button
            with open(zip_path, "rb") as f:
                st.download_button("Download Extracted Data", f, file_name=zip_filename)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
