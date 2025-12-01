# Quota System Configuration Template

## Quick Configuration Guide

This file provides templates and examples for common quota system configurations.

## 1. Basic Configuration (in app.py)

### Default Quotas
```python
# Located near the top of app.py

# Daily quota - number of files a user can download per day
DEFAULT_DAILY_QUOTA = 100

# Monthly quota - number of files a user can download per month
DEFAULT_MONTHLY_QUOTA = 1000

# Admin password - CHANGE THIS!
ADMIN_PASSWORD = "admin123"

# Database file location
QUOTA_DB_FILE = "quota_database.json"
```

## 2. Quota Tier Examples

### Tier 1: Free Users (Limited)
```python
DEFAULT_DAILY_QUOTA = 10
DEFAULT_MONTHLY_QUOTA = 100
```
**Use case**: Public access, limited resources

### Tier 2: Standard Users (Moderate)
```python
DEFAULT_DAILY_QUOTA = 100
DEFAULT_MONTHLY_QUOTA = 1000
```
**Use case**: Regular users, balanced access *(Current default)*

### Tier 3: Premium Users (High)
```python
DEFAULT_DAILY_QUOTA = 500
DEFAULT_MONTHLY_QUOTA = 10000
```
**Use case**: Paid users, research institutions

### Tier 4: Unlimited (Admin/Special)
```python
DEFAULT_DAILY_QUOTA = 999999
DEFAULT_MONTHLY_QUOTA = 999999
```
**Use case**: System administrators, special projects

## 3. Custom User Creation Examples

### Creating Users Programmatically
```python
from app import QuotaManager

qm = QuotaManager()

# Free tier user
qm.create_user(
    username="free_user",
    email="free@example.com",
    password="secure_pass",
    daily_quota=10,
    monthly_quota=100
)

# Premium tier user
qm.create_user(
    username="premium_user",
    email="premium@example.com",
    password="secure_pass",
    daily_quota=500,
    monthly_quota=10000
)

# Research institution (unlimited)
qm.create_user(
    username="research_lab",
    email="lab@university.edu",
    password="secure_pass",
    daily_quota=999999,
    monthly_quota=999999
)
```

## 4. Admin Password Security

### Method 1: Environment Variable (Recommended)
```python
# In app.py
import os
ADMIN_PASSWORD = os.getenv("QUOTA_ADMIN_PASSWORD", "default_admin123")
```

```bash
# In terminal or .env file
export QUOTA_ADMIN_PASSWORD="your_super_secure_password"
```

### Method 2: Configuration File
```python
# In app.py
import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
ADMIN_PASSWORD = config.get("admin_password", "admin123")
```

```json
// config.json
{
  "admin_password": "your_secure_password",
  "default_daily_quota": 100,
  "default_monthly_quota": 1000
}
```

### Method 3: Streamlit Secrets (Best for Streamlit Cloud)
```python
# In app.py
import streamlit as st
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")
```

```toml
# .streamlit/secrets.toml
admin_password = "your_secure_password"
```

## 5. Database Configuration

### Change Database Location
```python
# In app.py
QUOTA_DB_FILE = "/path/to/secure/location/quota_database.json"

# Or use environment variable
import os
QUOTA_DB_FILE = os.getenv("QUOTA_DB_PATH", "quota_database.json")
```

### Multiple Database Files (Multi-tenant)
```python
# In app.py
def get_db_file(tenant_id):
    return f"quota_database_{tenant_id}.json"

# Usage
quota_manager = QuotaManager(db_file=get_db_file("tenant1"))
```

## 6. Custom Quota Rules

### Time-based Quotas
```python
# Example: Higher quota on weekdays, lower on weekends
from datetime import datetime

def get_dynamic_quota(base_quota):
    today = datetime.now().weekday()
    if today < 5:  # Monday to Friday
        return base_quota
    else:  # Weekend
        return base_quota // 2  # Half quota on weekends

# Modify in QuotaManager.check_quota()
```

### Project-based Quotas
```python
# Add project tracking to user data structure
{
    "username": {
        "projects": {
            "project_a": {"daily_quota": 50, "usage": {...}},
            "project_b": {"daily_quota": 100, "usage": {...}}
        }
    }
}
```

### Data Size-based Quotas
```python
# Track by file size instead of file count
{
    "usage": {
        "daily_mb": {"2025-12-01": 1024},  # MB downloaded
        "monthly_mb": {"2025-12": 15360}
    }
}
```

## 7. Notification Settings

### Email Notifications (Requires email setup)
```python
EMAIL_NOTIFICATIONS = True
QUOTA_WARNING_THRESHOLD = 0.8  # Warn at 80% usage

def check_and_notify(username, usage, quota):
    if usage / quota >= QUOTA_WARNING_THRESHOLD:
        send_email(username, "Quota warning: 80% used")
```

### Slack Notifications
```python
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
NOTIFY_ADMIN_ON_QUOTA_EXCEEDED = True

def notify_slack(message):
    import requests
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})
```

## 8. Advanced Security

### Password Complexity Requirements
```python
import re

def validate_password(password):
    """Require: 8+ chars, uppercase, lowercase, number, special char"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain number"
    if not re.search(r"[!@#$%^&*]", password):
        return False, "Password must contain special character"
    return True, "Password valid"

# Use in create_user()
```

### Rate Limiting Login Attempts
```python
LOGIN_ATTEMPTS = {}  # username: [timestamp1, timestamp2, ...]
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds

def check_login_rate_limit(username):
    from datetime import datetime, timedelta
    
    now = datetime.now()
    if username in LOGIN_ATTEMPTS:
        # Remove old attempts
        LOGIN_ATTEMPTS[username] = [
            t for t in LOGIN_ATTEMPTS[username]
            if (now - t).seconds < LOCKOUT_DURATION
        ]
        
        # Check if locked out
        if len(LOGIN_ATTEMPTS[username]) >= MAX_ATTEMPTS:
            return False, "Too many login attempts. Try again later."
    
    return True, "OK"
```

## 9. Quota Monitoring Dashboard

### Usage Statistics
```python
def get_system_stats(quota_manager):
    """Get overall system statistics"""
    users = quota_manager.list_all_users()
    
    total_users = len(users)
    total_downloads = sum(
        quota_manager.get_user_stats(u)['total_downloads'] 
        for u in users
    )
    
    today = datetime.now().strftime("%Y-%m-%d")
    daily_total = sum(
        quota_manager.data["users"][u]["usage"]["daily"].get(today, 0)
        for u in users
    )
    
    return {
        "total_users": total_users,
        "total_downloads": total_downloads,
        "today_downloads": daily_total
    }
```

### Top Users
```python
def get_top_users(quota_manager, n=10):
    """Get top N users by total downloads"""
    users = quota_manager.list_all_users()
    
    user_totals = [
        (u, quota_manager.get_user_stats(u)['total_downloads'])
        for u in users
    ]
    
    return sorted(user_totals, key=lambda x: x[1], reverse=True)[:n]
```

## 10. Backup and Recovery

### Automatic Backup
```python
import shutil
from datetime import datetime

def backup_database():
    """Create timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"quota_database_backup_{timestamp}.json"
    shutil.copy(QUOTA_DB_FILE, backup_file)
    print(f"Backup created: {backup_file}")

# Schedule daily backups
import schedule
schedule.every().day.at("02:00").do(backup_database)
```

### Database Restoration
```python
def restore_database(backup_file):
    """Restore from backup"""
    shutil.copy(backup_file, QUOTA_DB_FILE)
    print(f"Database restored from: {backup_file}")
```

## 11. Migration to SQL Database

### SQLite Example
```python
import sqlite3

def migrate_to_sqlite():
    """Convert JSON to SQLite"""
    conn = sqlite3.connect('quota.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            email TEXT,
            password_hash TEXT,
            daily_quota INTEGER,
            monthly_quota INTEGER,
            created_at TEXT,
            last_login TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE usage (
            username TEXT,
            date TEXT,
            count INTEGER,
            type TEXT,  -- 'daily' or 'monthly'
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    # Import data from JSON
    qm = QuotaManager()
    for username, data in qm.data["users"].items():
        cursor.execute('''
            INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            data["email"],
            data["password_hash"],
            data["daily_quota"],
            data["monthly_quota"],
            data["created_at"],
            data["last_login"]
        ))
    
    conn.commit()
    conn.close()
```

## 12. Environment-Specific Configurations

### Development
```python
# dev_config.py
DEFAULT_DAILY_QUOTA = 999999  # Unlimited for testing
DEFAULT_MONTHLY_QUOTA = 999999
ADMIN_PASSWORD = "dev_admin"
QUOTA_DB_FILE = "quota_database_dev.json"
```

### Production
```python
# prod_config.py
DEFAULT_DAILY_QUOTA = 100
DEFAULT_MONTHLY_QUOTA = 1000
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")  # From environment
QUOTA_DB_FILE = "/var/data/quota_database.json"
```

### Usage
```python
# In app.py
import os

if os.getenv("ENV") == "production":
    from prod_config import *
else:
    from dev_config import *
```

## 13. Deployment Checklist

Before deploying to production:

- [ ] Change ADMIN_PASSWORD from default
- [ ] Set appropriate DEFAULT_DAILY_QUOTA
- [ ] Set appropriate DEFAULT_MONTHLY_QUOTA
- [ ] Configure database backup strategy
- [ ] Set up HTTPS/SSL
- [ ] Configure email notifications (if used)
- [ ] Test user registration flow
- [ ] Test quota enforcement
- [ ] Test admin panel access
- [ ] Document admin credentials securely
- [ ] Set up monitoring/logging
- [ ] Configure file permissions on database
- [ ] Test backup and restore procedures

---

## Quick Start Templates

### Minimal Setup
```python
# Minimal changes to get started
ADMIN_PASSWORD = "your_password_here"  # CHANGE THIS!
DEFAULT_DAILY_QUOTA = 100
DEFAULT_MONTHLY_QUOTA = 1000
```

### Secure Production Setup
```python
import os

# Use environment variables
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
DEFAULT_DAILY_QUOTA = int(os.getenv("DAILY_QUOTA", "100"))
DEFAULT_MONTHLY_QUOTA = int(os.getenv("MONTHLY_QUOTA", "1000"))
QUOTA_DB_FILE = os.getenv("QUOTA_DB_PATH", "quota_database.json")

# Email notifications
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
```

---

*This configuration template provides flexible options for customizing the quota system to your specific needs.*
