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
import json
import hashlib
from pathlib import Path

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

# Base OPeNDAP URL for IMERG
BASE_URL = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.07"

# Default NASA Earthdata credentials
DEFAULT_USERNAME = "wijaya_hydro"
DEFAULT_PASSWORD = "@huggingface4Free"
DEFAULT_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6IndpamF5YV9oeWRybyIsImV4cCI6MTc2OTY4NDQzOSwiaWF0IjoxNzY0NTAwNDM5LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.uDv6hlCaK7KRctbLZHNFMBdy2efdNmGnhRUk_er6sXgoUYLrIET84BQ36Q4MvaRcoT7ZIMWHQBPaPOTAmDrS3OVqcQiQeMT28MlX3sowkiuSkx4-G1Zvqf9BR8SC3Nvb1uXI6f5cKY3l3l2Vq1_qE16Cztko_RGg0ofvGlEcDNRfl_uHvttLNbhQjHRERQljd5vbqymhbAISy8259LbIl9m7BKKmi5mVbi6TS-h8viG4BnIgx488OmWSZ1m_WU4iJdUms711UEok0MMC1JmPUCjbB_4nwMPKMOLrMCx32gEBjCwIC3nPvvV8ZzNRjcJ2NqE2MJOI8drdUn3I8QbWEA"

# Quota System Configuration
QUOTA_DB_FILE = "quota_database.json"
DEFAULT_DAILY_QUOTA = 100  # Default daily download limit (number of files)
DEFAULT_MONTHLY_QUOTA = 1000  # Default monthly download limit (number of files)
ADMIN_PASSWORD = "wijaya13"  # Change this in production!

# Payment & Subscription Tiers (Indonesian Rupiah - IDR)
PAYMENT_TIERS = {
    "free": {
        "name": "Gratis",
        "price": 0,
        "price_idr": 0,
        "daily_quota": 10,
        "monthly_quota": 100,
        "description": "Akses dasar untuk pengguna individu"
    },
    "standard": {
        "name": "Standar",
        "price": 9.99,
        "price_idr": 150000,  # ~Rp 150,000/bulan
        "daily_quota": 100,
        "monthly_quota": 500,
        "description": "Kuota lebih tinggi untuk pengguna reguler"
    },
    "professional": {
        "name": "Profesional",
        "price": 29.99,
        "price_idr": 450000,  # ~Rp 450,000/bulan
        "daily_quota": 500,
        "monthly_quota": 1000,
        "description": "Kuota tinggi untuk profesional"
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 99.99,
        "price_idr": 1500000,  # ~Rp 1,500,000/bulan
        "daily_quota": 1000,
        "monthly_quota": 5000,
        "description": "Akses untuk perusahaan dan organisasi besar"
    }
}

# Midtrans Payment Gateway Configuration
# Configure credentials in Streamlit secrets (.streamlit/secrets.toml)
# For local: Create .streamlit/secrets.toml file
# For Streamlit Cloud: Add secrets in App settings > Secrets
PAYMENT_ENABLED = True
PAYMENT_GATEWAY = "midtrans"
MIDTRANS_MERCHANT_ID = st.secrets.get("MIDTRANS_MERCHANT_ID", "")
MIDTRANS_SERVER_KEY = st.secrets.get("MIDTRANS_SERVER_KEY", "")
MIDTRANS_CLIENT_KEY = st.secrets.get("MIDTRANS_CLIENT_KEY", "")
MIDTRANS_IS_PRODUCTION = st.secrets.get("MIDTRANS_IS_PRODUCTION", True)
MIDTRANS_SNAP_URL = "https://app.midtrans.com/snap/v1/transactions" if MIDTRANS_IS_PRODUCTION else "https://app.sandbox.midtrans.com/snap/v1/transactions"

# Quota Management Class
class QuotaManager:
    def __init__(self, db_file=QUOTA_DB_FILE):
        self.db_file = db_file
        self.data = self.load_database()
    
    def load_database(self):
        """Load user quota database from JSON file."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {"users": {}, "admin_hash": self.hash_password(ADMIN_PASSWORD)}
    
    def save_database(self):
        """Save user quota database to JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password, daily_quota=None, monthly_quota=None):
        """Create a new user with quota limits."""
        if username in self.data["users"]:
            return False, "Username already exists"
        
        self.data["users"][username] = {
            "email": email,
            "password_hash": self.hash_password(password),
            "daily_quota": daily_quota or DEFAULT_DAILY_QUOTA,
            "monthly_quota": monthly_quota or DEFAULT_MONTHLY_QUOTA,
            "subscription_tier": "free",
            "payment_history": [],
            "usage": {
                "daily": {},
                "monthly": {},
                "total": 0
            },
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        self.save_database()
        return True, "User created successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials."""
        if username not in self.data["users"]:
            return False, "User not found"
        
        user = self.data["users"][username]
        if user["password_hash"] != self.hash_password(password):
            return False, "Incorrect password"
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        self.save_database()
        return True, "Authentication successful"
    
    def check_quota(self, username, num_files):
        """Check if user has sufficient quota for download."""
        if username not in self.data["users"]:
            return False, "User not found"
        
        user = self.data["users"][username]
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        
        # Get current usage
        daily_usage = user["usage"]["daily"].get(today, 0)
        monthly_usage = user["usage"]["monthly"].get(current_month, 0)
        
        # Check limits
        if daily_usage + num_files > user["daily_quota"]:
            remaining = user["daily_quota"] - daily_usage
            return False, f"Daily quota exceeded. Remaining: {remaining} files"
        
        if monthly_usage + num_files > user["monthly_quota"]:
            remaining = user["monthly_quota"] - monthly_usage
            return False, f"Monthly quota exceeded. Remaining: {remaining} files"
        
        return True, "Quota available"
    
    def update_usage(self, username, num_files):
        """Update user's download usage."""
        if username not in self.data["users"]:
            return False
        
        user = self.data["users"][username]
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        
        # Update usage
        user["usage"]["daily"][today] = user["usage"]["daily"].get(today, 0) + num_files
        user["usage"]["monthly"][current_month] = user["usage"]["monthly"].get(current_month, 0) + num_files
        user["usage"]["total"] += num_files
        
        self.save_database()
        return True
    
    def get_user_stats(self, username):
        """Get user's quota and usage statistics."""
        if username not in self.data["users"]:
            return None
        
        user = self.data["users"][username]
        today = datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.now().strftime("%Y-%m")
        
        daily_usage = user["usage"]["daily"].get(today, 0)
        monthly_usage = user["usage"]["monthly"].get(current_month, 0)
        
        return {
            "username": username,
            "email": user["email"],
            "daily_quota": user["daily_quota"],
            "daily_usage": daily_usage,
            "daily_remaining": user["daily_quota"] - daily_usage,
            "monthly_quota": user["monthly_quota"],
            "monthly_usage": monthly_usage,
            "monthly_remaining": user["monthly_quota"] - monthly_usage,
            "total_downloads": user["usage"]["total"],
            "created_at": user["created_at"],
            "last_login": user["last_login"]
        }
    
    def update_user_quota(self, username, daily_quota=None, monthly_quota=None):
        """Update user's quota limits (admin function)."""
        if username not in self.data["users"]:
            return False, "User not found"
        
        user = self.data["users"][username]
        if daily_quota is not None:
            user["daily_quota"] = daily_quota
        if monthly_quota is not None:
            user["monthly_quota"] = monthly_quota
        
        self.save_database()
        return True, "Quota updated successfully"
    
    def list_all_users(self):
        """List all users (admin function)."""
        return list(self.data["users"].keys())
    
    def verify_admin(self, password):
        """Verify admin password."""
        return self.hash_password(password) == self.data["admin_hash"]
    
    def upgrade_subscription(self, username, tier):
        """Upgrade user's subscription tier and update quotas."""
        if username not in self.data["users"]:
            return False, "User not found"
        
        if tier not in PAYMENT_TIERS:
            return False, "Invalid subscription tier"
        
        user = self.data["users"][username]
        tier_info = PAYMENT_TIERS[tier]
        
        # Update subscription
        user["subscription_tier"] = tier
        user["daily_quota"] = tier_info["daily_quota"]
        user["monthly_quota"] = tier_info["monthly_quota"]
        
        # Record payment
        payment_record = {
            "date": datetime.now().isoformat(),
            "tier": tier,
            "amount": tier_info["price"],
            "description": f"Upgraded to {tier_info['name']}"
        }
        
        if "payment_history" not in user:
            user["payment_history"] = []
        user["payment_history"].append(payment_record)
        
        self.save_database()
        return True, f"Successfully upgraded to {tier_info['name']} tier"
    
    def get_subscription_info(self, username):
        """Get user's current subscription information."""
        if username not in self.data["users"]:
            return None
        
        user = self.data["users"][username]
        tier = user.get("subscription_tier", "free")
        tier_info = PAYMENT_TIERS.get(tier, PAYMENT_TIERS["free"])
        
        return {
            "current_tier": tier,
            "tier_name": tier_info["name"],
            "price": tier_info["price"],
            "price_idr": tier_info.get("price_idr", 0),
            "daily_quota": user["daily_quota"],
            "monthly_quota": user["monthly_quota"],
            "payment_history": user.get("payment_history", [])
        }

# Midtrans Payment Gateway Functions
def create_midtrans_transaction(username, email, tier_key):
    """Create Midtrans Snap transaction for subscription upgrade."""
    tier_info = PAYMENT_TIERS.get(tier_key)
    if not tier_info or tier_info["price_idr"] == 0:
        return None, "Invalid tier or free tier selected"
    
    # Generate unique order ID
    order_id = f"SUB-{username}-{tier_key}-{int(datetime.now().timestamp())}"
    
    # Prepare transaction data
    transaction_data = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": tier_info["price_idr"]
        },
        "customer_details": {
            "first_name": username,
            "email": email
        },
        "item_details": [
            {
                "id": tier_key,
                "price": tier_info["price_idr"],
                "quantity": 1,
                "name": f"Subscription - {tier_info['name']}"
            }
        ],
        "callbacks": {
            "finish": "https://your-domain.com/payment/finish"  # Update with your domain
        }
    }
    
    # Create Snap transaction
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {get_midtrans_auth_string()}"
        }
        
        response = requests.post(
            MIDTRANS_SNAP_URL,
            json=transaction_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            return result.get("token"), order_id
        else:
            return None, f"Error: {response.text}"
    
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_midtrans_auth_string():
    """Get base64 encoded auth string for Midtrans."""
    import base64
    auth_string = f"{MIDTRANS_SERVER_KEY}:"
    return base64.b64encode(auth_string.encode()).decode()

def verify_midtrans_payment(order_id):
    """Verify payment status from Midtrans."""
    try:
        status_url = f"https://api.{'midtrans' if MIDTRANS_IS_PRODUCTION else 'sandbox.midtrans'}.com/v2/{order_id}/status"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {get_midtrans_auth_string()}"
        }
        
        response = requests.get(status_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("transaction_status"), result
        else:
            return None, None
    
    except Exception as e:
        return None, None

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
    st.title("GPM IMERGDL V7 Downloader and Extractor v1.0")
    st.write("Download, extract, and analyze GPM IMERGDL V7 data for a specified date range and area.")
    
    # Initialize quota manager
    quota_manager = QuotaManager()
    
    # Session state initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    # Sidebar for user authentication and quota management
    with st.sidebar:
        st.header("User Authentication")
        
        if not st.session_state.logged_in:
            tab1, tab2, tab3 = st.tabs(["Login", "Register", "Admin"])
            
            # Login Tab
            with tab1:
                st.subheader("Login")
                login_username = st.text_input("Username", key="login_user")
                login_password = st.text_input("Password", type="password", key="login_pass")
                
                if st.button("Login"):
                    success, message = quota_manager.authenticate_user(login_username, login_password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Registration Tab
            with tab2:
                st.subheader("Register New User")
                reg_username = st.text_input("Username", key="reg_user")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_pass")
                reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
                
                if st.button("Register"):
                    if not all([reg_username, reg_email, reg_password]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = quota_manager.create_user(reg_username, reg_email, reg_password)
                        if success:
                            st.success(f"{message}. Default quota: {DEFAULT_DAILY_QUOTA} daily, {DEFAULT_MONTHLY_QUOTA} monthly")
                        else:
                            st.error(message)
            
            # Admin Tab
            with tab3:
                st.subheader("Admin Panel")
                admin_password = st.text_input("Admin Password", type="password", key="admin_pass")
                
                if st.button("Access Admin Panel"):
                    if quota_manager.verify_admin(admin_password):
                        st.success("Admin access granted")
                        st.session_state.admin_mode = True
                    else:
                        st.error("Invalid admin password")
                
                if st.session_state.get('admin_mode', False):
                    st.write("---")
                    st.write("**User Management**")
                    users = quota_manager.list_all_users()
                    selected_user = st.selectbox("Select User", users)
                    
                    if selected_user:
                        user_stats = quota_manager.get_user_stats(selected_user)
                        st.json(user_stats)
                        
                        new_daily = st.number_input("New Daily Quota", min_value=0, value=user_stats["daily_quota"])
                        new_monthly = st.number_input("New Monthly Quota", min_value=0, value=user_stats["monthly_quota"])
                        
                        if st.button("Update Quota"):
                            success, message = quota_manager.update_user_quota(selected_user, new_daily, new_monthly)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
        
        else:
            # User is logged in - show stats and logout
            st.success(f"Logged in as: **{st.session_state.username}**")
            
            # Get subscription info
            sub_info = quota_manager.get_subscription_info(st.session_state.username)
            if sub_info:
                current_tier = sub_info["current_tier"]
                tier_badge = f"🏷️ **{sub_info['tier_name']}**"
                if current_tier != "free":
                    tier_badge += f" (Rp {sub_info['price_idr']:,.0f}/bulan)"
                st.markdown(tier_badge)
            
            user_stats = quota_manager.get_user_stats(st.session_state.username)
            if user_stats:
                st.write("---")
                st.write("**Your Quota Status**")
                st.metric("Daily Quota", f"{user_stats['daily_usage']}/{user_stats['daily_quota']}")
                st.metric("Monthly Quota", f"{user_stats['monthly_usage']}/{user_stats['monthly_quota']}")
                st.metric("Total Downloads", user_stats['total_downloads'])
                
                # Progress bars
                daily_percent = (user_stats['daily_usage'] / user_stats['daily_quota']) * 100 if user_stats['daily_quota'] > 0 else 0
                monthly_percent = (user_stats['monthly_usage'] / user_stats['monthly_quota']) * 100 if user_stats['monthly_quota'] > 0 else 0
                
                st.progress(min(daily_percent / 100, 1.0))
                st.caption(f"Daily: {user_stats['daily_remaining']} remaining")
                
                st.progress(min(monthly_percent / 100, 1.0))
                st.caption(f"Monthly: {user_stats['monthly_remaining']} remaining")
            
            # Upgrade Subscription Section
            if PAYMENT_ENABLED:
                st.write("---")
                st.write("**💳 Upgrade Your Plan**")
                
                with st.expander("View All Plans & Upgrade", expanded=False):
                    # Display pricing tiers
                    cols = st.columns(len(PAYMENT_TIERS))
                    
                    for idx, (tier_key, tier_info) in enumerate(PAYMENT_TIERS.items()):
                        with cols[idx]:
                            is_current = sub_info and sub_info["current_tier"] == tier_key
                            
                            # Card styling
                            if is_current:
                                st.markdown(f"### ✅ {tier_info['name']}")
                            else:
                                st.markdown(f"### {tier_info['name']}")
                            
                            if tier_info['price_idr'] > 0:
                                st.markdown(f"**Rp {tier_info['price_idr']:,.0f}/bulan**")
                            else:
                                st.markdown("**Gratis**")
                            
                            st.caption(tier_info['description'])
                            st.write(f"📊 Harian: {tier_info['daily_quota']:,} file")
                            st.write(f"📊 Bulanan: {tier_info['monthly_quota']:,} file")
                            
                            # Upgrade button
                            if not is_current and tier_info['price_idr'] > 0:
                                if st.button(f"Upgrade ke {tier_info['name']}", key=f"upgrade_{tier_key}"):
                                    st.session_state.selected_tier = tier_key
                                    st.session_state.show_payment = True
                                    st.rerun()
                            elif is_current:
                                st.success("Paket Aktif")
                    
                    # Payment modal - Midtrans Integration
                    if st.session_state.get('show_payment', False):
                        selected_tier = st.session_state.get('selected_tier')
                        tier_info = PAYMENT_TIERS[selected_tier]
                        
                        st.write("---")
                        st.write(f"### 💳 Pembayaran untuk {tier_info['name']}")
                        st.info(f"💰 Total: **Rp {tier_info['price_idr']:,.0f}** per bulan")
                        
                        st.write("**Metode Pembayaran Midtrans:**")
                        st.write("✅ Transfer Bank (BCA, Mandiri, BNI, BRI, Permata)")
                        st.write("✅ E-Wallet (GoPay, OVO, DANA, ShopeePay, LinkAja)")
                        st.write("✅ Kartu Kredit/Debit (Visa, MasterCard, JCB)")
                        st.write("✅ Convenience Store (Indomaret, Alfamart)")
                        st.write("✅ QRIS")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🚀 Lanjutkan ke Pembayaran", type="primary"):
                                with st.spinner("Membuat transaksi pembayaran..."):
                                    # Get user email
                                    user_data = quota_manager.data["users"].get(st.session_state.username, {})
                                    user_email = user_data.get("email", "")
                                    
                                    # Create Midtrans transaction
                                    snap_token, order_id = create_midtrans_transaction(
                                        st.session_state.username,
                                        user_email,
                                        selected_tier
                                    )
                                    
                                    if snap_token:
                                        st.session_state.snap_token = snap_token
                                        st.session_state.order_id = order_id
                                        
                                        # Display Midtrans Snap popup
                                        st.success("✅ Transaksi berhasil dibuat!")
                                        st.write("**Klik tombol di bawah untuk membuka halaman pembayaran Midtrans:**")
                                        
                                        # Midtrans Snap popup integration
                                        midtrans_url = f"https://app.{'midtrans' if MIDTRANS_IS_PRODUCTION else 'sandbox.midtrans'}.com/snap/v2/vtweb/{snap_token}"
                                        
                                        st.markdown(f"""
                                        <a href="{midtrans_url}" target="_blank">
                                            <button style="background-color:#4CAF50;color:white;padding:15px 32px;text-align:center;font-size:16px;border:none;border-radius:4px;cursor:pointer;">
                                                🔐 Bayar Sekarang dengan Midtrans
                                            </button>
                                        </a>
                                        """, unsafe_allow_html=True)
                                        
                                        st.write("---")
                                        st.write("**Status Pembayaran:**")
                                        st.write(f"Order ID: `{order_id}`")
                                        
                                        if st.button("✅ Saya Sudah Bayar - Verifikasi Sekarang"):
                                            with st.spinner("Memverifikasi pembayaran..."):
                                                status, result = verify_midtrans_payment(order_id)
                                                
                                                if status in ["settlement", "capture"]:
                                                    # Payment successful - upgrade user
                                                    success, message = quota_manager.upgrade_subscription(
                                                        st.session_state.username,
                                                        selected_tier
                                                    )
                                                    
                                                    if success:
                                                        st.success(f"🎉 {message}")
                                                        st.balloons()
                                                        st.session_state.show_payment = False
                                                        st.session_state.selected_tier = None
                                                        st.session_state.snap_token = None
                                                        st.session_state.order_id = None
                                                        st.rerun()
                                                    else:
                                                        st.error(message)
                                                elif status == "pending":
                                                    st.warning("⏳ Pembayaran masih menunggu. Silakan selesaikan pembayaran terlebih dahulu.")
                                                elif status == "deny":
                                                    st.error("❌ Pembayaran ditolak. Silakan coba lagi.")
                                                elif status == "cancel" or status == "expire":
                                                    st.error("❌ Pembayaran dibatalkan atau kadaluarsa.")
                                                else:
                                                    st.info(f"Status: {status or 'Belum ada pembayaran'}")
                                    else:
                                        st.error(f"❌ Gagal membuat transaksi: {order_id}")
                        
                        with col2:
                            if st.button("Batal"):
                                st.session_state.show_payment = False
                                st.session_state.selected_tier = None
                                st.session_state.snap_token = None
                                st.session_state.order_id = None
                                st.rerun()
                        
                        st.caption("🔒 Pembayaran aman dengan Midtrans | Data kartu Anda tidak disimpan")
                    
                    # Payment history
                    if sub_info and sub_info.get('payment_history'):
                        st.write("---")
                        st.write("**📜 Riwayat Pembayaran**")
                        for payment in reversed(sub_info['payment_history'][-5:]):  # Show last 5
                            payment_date = datetime.fromisoformat(payment['date']).strftime("%Y-%m-%d %H:%M")
                            st.text(f"{payment_date} | {payment['description']} | Rp {payment.get('amount', 0) * 15000:,.0f}")
            
            st.write("---")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.admin_mode = False
                st.session_state.show_payment = False
                st.session_state.selected_tier = None
                st.rerun()
    
    # Main content - only accessible when logged in
    if not st.session_state.logged_in:
        st.warning("⚠️ Please login or register to use the downloader.")
        st.info("👈 Use the sidebar to login or create a new account.")
        return

    # Inputs for date range and file uploads
    start_date = st.text_input("Start Date (YYYY-MM-DD)", value="2025-01-01")
    end_date = st.text_input("End Date (YYYY-MM-DD)", value="2025-01-31")
    shapefile_zip = st.file_uploader("Upload Shapefile (ZIP) for Specific Area", type="zip")
    csv_file = st.file_uploader("Upload CSV File with Coordinates (ID,Lon,Lat)", type="csv")

    if st.button("Download and Process"):
        if not all([start_date, end_date, shapefile_zip, csv_file]):
            st.error("Please fill in all fields and upload all required files.")
            return
        
        # Calculate number of files to download
        try:
            dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(
                (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)]
            num_files = len(dates)
        except Exception as e:
            st.error(f"Invalid date format: {str(e)}")
            return
        
        # Check quota before processing
        quota_ok, quota_message = quota_manager.check_quota(st.session_state.username, num_files)
        if not quota_ok:
            st.error(f"❌ Kuota Habis: {quota_message}")
            st.warning(f"Anda mencoba download {num_files} file, tetapi kuota Anda tidak mencukupi.")
            
            # Suggest upgrade if payment is enabled
            if PAYMENT_ENABLED:
                st.info("💡 **Butuh kuota lebih?** Upgrade paket Anda untuk mendapatkan limit lebih tinggi!")
                
                # Get current tier and suggest next tier
                sub_info = quota_manager.get_subscription_info(st.session_state.username)
                current_tier = sub_info["current_tier"] if sub_info else "free"
                
                # Find suitable tier for the request
                suggested_tier = None
                for tier_key, tier_info in PAYMENT_TIERS.items():
                    if tier_info["daily_quota"] >= num_files and tier_key != current_tier:
                        suggested_tier = tier_key
                        break
                
                if suggested_tier:
                    tier_info = PAYMENT_TIERS[suggested_tier]
                    st.success(f"✨ Rekomendasi: Paket **{tier_info['name']}** - {tier_info['daily_quota']:,} file/hari seharga Rp {tier_info['price_idr']:,.0f}/bulan")
                    if st.button("🚀 Upgrade Sekarang"):
                        st.session_state.selected_tier = suggested_tier
                        st.session_state.show_payment = True
                        st.rerun()
            
            return
        
        st.info(f"✅ Quota check passed. Processing {num_files} files...")

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
            
            # Multi-threaded IMERG download
            download_all_imerg(dates, download_dir, DEFAULT_TOKEN, bbox)
            
            # Update user quota after successful download
            quota_manager.update_usage(st.session_state.username, num_files)
            st.success(f"✅ Downloaded {num_files} files. Quota updated.")

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
