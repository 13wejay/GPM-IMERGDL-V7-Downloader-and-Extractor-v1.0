# Quick Start Guide - User Authentication

## For Users

### First Time Setup
1. Run: `streamlit run app.py`
2. Click **Register**
3. Fill in: Username, Email, Password
4. Click **Create Account**
5. Click **Login** and enter credentials

### Daily Usage
1. Login to see your quota in sidebar
2. Upload files and select date range
3. System checks your quota automatically
4. Download completes if quota available
5. Quota updates in real-time

## For Administrators

### Common Commands

```bash
# View all users
python admin_tools.py list

# Check specific user
python admin_tools.py details john_doe

# Give user more quota
python admin_tools.py update-limits john_doe --daily 50 --monthly 500

# Disable a user
python admin_tools.py deactivate john_doe

# Re-enable a user
python admin_tools.py activate john_doe

# Create premium user
python admin_tools.py create-admin admin_user password123 admin@example.com
```

### Default Limits
- **Standard User**: 10/day, 100/month
- **Premium User**: 100/day, 1000/month

### Quota Reset
- **Daily**: Resets at midnight
- **Monthly**: Resets on 1st of each month

## Files Created
- `users.json` - User database (auto-generated)
- `IMERG_Downloads/` - Downloaded data directory

## Quick Troubleshooting
- **Login fails**: Check username/password, verify account is active
- **Quota exceeded**: Wait for reset or request limit increase
- **Permission error**: Ensure write access to application folder
