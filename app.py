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
import concurrent.futures

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from users_db import UserDatabase

# Base OPeNDAP URL for IMERG
BASE_URL = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.07"

# Default NASA Earthdata credentials
DEFAULT_USERNAME = "wijaya_hydro"
DEFAULT_PASSWORD = "@huggingface4Free"
DEFAULT_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6IndpamF5YV9oeWRybyIsImV4cCI6MTc2OTY4NDQzOSwiaWF0IjoxNzY0NTAwNDM5LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.uDv6hlCaK7KRctbLZHNFMBdy2efdNmGnhRUk_er6sXgoUYLrIET84BQ36Q4MvaRcoT7ZIMWHQBPaPOTAmDrS3OVqcQiQeMT28MlX3sowkiuSkx4-G1Zvqf9BR8SC3Nvb1uXI6f5cKY3l3l2Vq1_qE16Cztko_RGg0ofvGlEcDNRfl_uHvttLNbhQjHRERQljd5vbqymhbAISy8259LbIl9m7BKKmi5mVbi6TS-h8viG4BnIgx488OmWSZ1m_WU4iJdUms711UEok0MMC1JmPUCjbB_4nwMPKMOLrMCx32gEBjCwIC3nPvvV8ZzNRjcJ2NqE2MJOI8drdUn3I8QbWEA"

# Initialize user database
user_db = UserDatabase()

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

def login_user(username: str, password: str) -> bool:
    """Login a user."""
    if user_db.authenticate(username, password) and user_db.is_user_active(username):
        st.session_state.logged_in = True
        st.session_state.username = username
        return True
    return False

def logout_user():
    """Logout the current user."""
    st.session_state.logged_in = False
    st.session_state.username = None

def register_user(username: str, password: str, email: str) -> tuple[bool, str]:
    """Register a new user."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if "@" not in email:
        return False, "Invalid email address"
    
    if user_db.register_user(username, password, email):
        return True, "Registration successful! Please login."
    return False, "Username already exists"

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
    """Downloads IMERG subsetted data from OPeNDAP using multi-threading."""
    year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
    min_lon, min_lat, max_lon, max_lat = bbox

    def lat_to_index(lat): return int(round((lat + 90) / 0.1)) - 1
    def lon_to_index(lon): return int(round((lon + 180) / 0.1))

    lon_min_idx, lon_max_idx = lon_to_index(min_lon), lon_to_index(max_lon)
    lat_min_idx, lat_max_idx = lat_to_index(min_lat), lat_to_index(max_lat)

    filename = f"3B-DAY-L.MS.MRG.3IMERG.{year}{month}{day}-S000000-E235959.V07B.nc4"
    subset_url = f"{BASE_URL}/{year}/{month}/{filename}.nc4?precipitation[0:0][{lon_min_idx}:{lon_max_idx}][{lat_min_idx}:{lat_max_idx}],time,lon[{lon_min_idx}:{lon_max_idx}],lat[{lat_min_idx}:{lat_max_idx}]"

    save_path = os.path.join(download_dir, f"IMERG_Subset_{year}{month}{day}.nc4")

    if os.path.exists(save_path):
        return save_path

    headers = {"Authorization": f"Bearer {token}"}

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

# Multi-threaded download manager
def download_all_imerg(dates, download_dir, token, bbox):
    """Downloads multiple IMERG files in parallel using threading."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers if needed
        results = list(executor.map(lambda date: download_subset_imerg(date, download_dir, token, bbox), dates))
    return results

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
    
# Streamlit Interface
def main():
    st.set_page_config(page_title="GPM IMERGDL V7 Downloader", layout="wide")
    init_session_state()
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """Display login and registration page."""
    st.title("🌧️ GPM IMERGDL V7 Downloader and Extractor v1.0")
    st.write("Please login or register to access the downloader.")
    
    # Toggle between login and registration
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Login", use_container_width=True, type="primary" if not st.session_state.show_register else "secondary"):
            st.session_state.show_register = False
            st.rerun()
    
    with col2:
        if st.button("Register", use_container_width=True, type="primary" if st.session_state.show_register else "secondary"):
            st.session_state.show_register = True
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.show_register:
        # Registration form
        st.subheader("📝 Register New Account")
        with st.form("register_form"):
            reg_username = st.text_input("Username", max_chars=50)
            reg_email = st.text_input("Email", max_chars=100)
            reg_password = st.text_input("Password", type="password", max_chars=100)
            reg_password_confirm = st.text_input("Confirm Password", type="password", max_chars=100)
            
            st.info("🔹 Default limits: 10 downloads/day, 100 downloads/month")
            
            submit_register = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_register:
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match!")
                elif not all([reg_username, reg_email, reg_password]):
                    st.error("Please fill in all fields!")
                else:
                    success, message = register_user(reg_username, reg_password, reg_email)
                    if success:
                        st.success(message)
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(message)
    else:
        # Login form
        st.subheader("🔐 Login")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            
            submit_login = st.form_submit_button("Login", use_container_width=True)
            
            if submit_login:
                if login_user(login_username, login_password):
                    st.success(f"Welcome back, {login_username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password, or account is inactive.")

def show_main_app():
    """Display the main application after login."""
    # Header with user info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🌧️ GPM IMERGDL V7 Downloader and Extractor v1.0")
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Display user quota information
    user_info = user_db.get_user_info(st.session_state.username)
    if user_info:
        st.sidebar.header(f"👤 {user_info['username']}")
        st.sidebar.write(f"📧 {user_info['email']}")
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Download Quota")
        
        daily_remaining = user_info['daily_limit'] - user_info['daily_downloads']
        monthly_remaining = user_info['monthly_limit'] - user_info['monthly_downloads']
        
        # Daily quota
        st.sidebar.write(f"**Daily:** {user_info['daily_downloads']}/{user_info['daily_limit']}")
        st.sidebar.progress(user_info['daily_downloads'] / user_info['daily_limit'])
        st.sidebar.write(f"Remaining today: {daily_remaining}")
        
        st.sidebar.markdown("---")
        
        # Monthly quota
        st.sidebar.write(f"**Monthly:** {user_info['monthly_downloads']}/{user_info['monthly_limit']}")
        st.sidebar.progress(user_info['monthly_downloads'] / user_info['monthly_limit'])
        st.sidebar.write(f"Remaining this month: {monthly_remaining}")
    
    st.write("Download, extract, and analyze GPM IMERGDL V7 data for a specified date range and area.")

    # Inputs for date range and file uploads
    start_date = st.text_input("Start Date (YYYY-MM-DD)", value="2025-01-01")
    end_date = st.text_input("End Date (YYYY-MM-DD)", value="2025-01-31")
    shapefile_zip = st.file_uploader("Upload Shapefile (ZIP) for Specific Area", type="zip")
    csv_file = st.file_uploader("Upload CSV File with Coordinates (ID,Lon,Lat)", type="csv")

    if st.button("Download and Process", type="primary"):
        if not all([start_date, end_date, shapefile_zip, csv_file]):
            st.error("Please fill in all fields and upload all required files.")
            return

        try:
            # Calculate number of files to download
            dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(
                (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)]
            
            num_files = len(dates)
            
            # Check download limits
            can_download, reason = user_db.can_download(st.session_state.username, num_files)
            
            if not can_download:
                st.error(f"❌ Download limit exceeded: {reason}")
                st.warning(f"You are trying to download {num_files} files.")
                return
            
            st.info(f"ℹ️ This will download {num_files} files and count against your quota.")
            
            download_dir = "IMERG_Downloads"
            os.makedirs(download_dir, exist_ok=True)

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
            
            # Multi-threaded IMERG download
            download_all_imerg(dates, download_dir, DEFAULT_TOKEN, bbox)

            # Extract precipitation data
            output_excel = os.path.join(download_dir, "IMERG_Extracted.xlsx")
            extract_precipitation(download_dir, csv_file, output_excel)

            # Create ZIP file for download
            zip_filename = "IMERG_Extracted.zip"
            zip_path = create_download_zip(download_dir, zip_filename)
            
            # Record the download
            user_db.record_download(st.session_state.username, num_files)

            st.success("✅ Download and extraction complete!")
            st.info(f"📥 {num_files} files downloaded and recorded.")

            # Provide download button
            with open(zip_path, "rb") as f:
                st.download_button("📦 Download Extracted Data", f, file_name=zip_filename, type="primary")
            
            # Update quota display
            st.rerun()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
