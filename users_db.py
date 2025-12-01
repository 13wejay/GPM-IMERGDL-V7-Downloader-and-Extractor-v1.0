import json
import bcrypt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class UserDatabase:
    """Manages user authentication and download quotas."""
    
    def __init__(self, db_file="users.json"):
        self.db_file = db_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Save users to JSON file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def register_user(self, username: str, password: str, email: str, 
                     daily_limit: int = 10, monthly_limit: int = 100) -> bool:
        """Register a new user with download limits."""
        if username in self.users:
            return False
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        self.users[username] = {
            "password": hashed_password.decode('utf-8'),
            "email": email,
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit,
            "downloads": [],
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        self._save_users()
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        if username not in self.users:
            return False
        
        stored_password = self.users[username]["password"].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    
    def is_user_active(self, username: str) -> bool:
        """Check if user account is active."""
        return self.users.get(username, {}).get("is_active", False)
    
    def record_download(self, username: str, num_files: int = 1):
        """Record a download for a user."""
        if username not in self.users:
            return
        
        download_record = {
            "date": datetime.now().isoformat(),
            "num_files": num_files
        }
        
        self.users[username]["downloads"].append(download_record)
        self._save_users()
    
    def get_daily_downloads(self, username: str) -> int:
        """Get number of downloads today."""
        if username not in self.users:
            return 0
        
        today = datetime.now().date()
        downloads = self.users[username].get("downloads", [])
        
        daily_count = sum(
            record["num_files"] 
            for record in downloads 
            if datetime.fromisoformat(record["date"]).date() == today
        )
        
        return daily_count
    
    def get_monthly_downloads(self, username: str) -> int:
        """Get number of downloads this month."""
        if username not in self.users:
            return 0
        
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        downloads = self.users[username].get("downloads", [])
        
        monthly_count = sum(
            record["num_files"] 
            for record in downloads 
            if datetime.fromisoformat(record["date"]).month == current_month 
            and datetime.fromisoformat(record["date"]).year == current_year
        )
        
        return monthly_count
    
    def can_download(self, username: str, num_files: int = 1) -> tuple[bool, str]:
        """Check if user can download, returns (can_download, reason)."""
        if username not in self.users:
            return False, "User not found"
        
        if not self.is_user_active(username):
            return False, "Account is inactive"
        
        user = self.users[username]
        daily_limit = user["daily_limit"]
        monthly_limit = user["monthly_limit"]
        
        daily_downloads = self.get_daily_downloads(username)
        monthly_downloads = self.get_monthly_downloads(username)
        
        if daily_downloads + num_files > daily_limit:
            return False, f"Daily limit exceeded ({daily_downloads}/{daily_limit})"
        
        if monthly_downloads + num_files > monthly_limit:
            return False, f"Monthly limit exceeded ({monthly_downloads}/{monthly_limit})"
        
        return True, "OK"
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information and download statistics."""
        if username not in self.users:
            return None
        
        user = self.users[username]
        return {
            "username": username,
            "email": user["email"],
            "daily_limit": user["daily_limit"],
            "monthly_limit": user["monthly_limit"],
            "daily_downloads": self.get_daily_downloads(username),
            "monthly_downloads": self.get_monthly_downloads(username),
            "is_active": user["is_active"],
            "created_at": user["created_at"]
        }
    
    def update_user_limits(self, username: str, daily_limit: int = None, 
                          monthly_limit: int = None) -> bool:
        """Update user download limits (admin function)."""
        if username not in self.users:
            return False
        
        if daily_limit is not None:
            self.users[username]["daily_limit"] = daily_limit
        
        if monthly_limit is not None:
            self.users[username]["monthly_limit"] = monthly_limit
        
        self._save_users()
        return True
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account."""
        if username not in self.users:
            return False
        
        self.users[username]["is_active"] = False
        self._save_users()
        return True
    
    def activate_user(self, username: str) -> bool:
        """Activate a user account."""
        if username not in self.users:
            return False
        
        self.users[username]["is_active"] = True
        self._save_users()
        return True
