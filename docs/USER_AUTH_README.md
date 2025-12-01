# User Authentication & Download Limitation System

## Overview

This system adds user authentication and download quota management to the GPM IMERGDL V7 Downloader application. Users must register and login to download data, and their downloads are tracked with daily and monthly limits.

## Features

### 🔐 User Authentication
- **Registration**: New users can create accounts with email and password
- **Login/Logout**: Secure session management
- **Password Hashing**: Passwords are encrypted using bcrypt

### 📊 Download Quotas
- **Daily Limits**: Default 10 downloads per day
- **Monthly Limits**: Default 100 downloads per month
- **Real-time Tracking**: View remaining quota in sidebar
- **Automatic Enforcement**: System prevents downloads when quota exceeded

### 👤 User Management
- **User Database**: JSON-based storage (`users.json`)
- **Admin Tools**: Command-line utilities for user management
- **Account Status**: Activate/deactivate user accounts

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
streamlit run app.py
```

### First Time Users

1. Click the **Register** button
2. Enter username, email, and password
3. Click **Create Account**
4. Login with your credentials

### Using the Downloader

Once logged in:
1. Check your quota in the left sidebar
2. Enter date range (YYYY-MM-DD)
3. Upload shapefile (ZIP format)
4. Upload CSV with coordinates
5. Click **Download and Process**

The system will:
- Calculate number of files to download
- Check if you have sufficient quota
- Process the download if quota allows
- Record the download against your quota
- Update your remaining quota

### Viewing Your Quota

The sidebar displays:
- **Daily Usage**: Files downloaded today / Daily limit
- **Monthly Usage**: Files downloaded this month / Monthly limit
- **Remaining**: How many downloads you have left

## Admin Tools

### Command-Line Administration

Use `admin_tools.py` to manage users:

#### List All Users
```bash
python admin_tools.py list
```

#### View User Details
```bash
python admin_tools.py details <username>
```

#### Update User Limits
```bash
python admin_tools.py update-limits <username> --daily 50 --monthly 500
```

#### Activate/Deactivate Users
```bash
python admin_tools.py activate <username>
python admin_tools.py deactivate <username>
```

#### Create Admin/Premium User
```bash
python admin_tools.py create-admin <username> <password> <email>
```
Default limits for admin users: 100/day, 1000/month

## File Structure

```
├── app.py                  # Main Streamlit application
├── users_db.py            # User database management
├── admin_tools.py         # Admin command-line tools
├── requirements.txt       # Python dependencies
├── users.json            # User database (auto-created)
└── USER_AUTH_README.md   # This file
```

## Database Schema

The `users.json` file stores user information:

```json
{
  "username": {
    "password": "hashed_password",
    "email": "user@example.com",
    "daily_limit": 10,
    "monthly_limit": 100,
    "downloads": [
      {
        "date": "2025-12-01T10:30:00",
        "num_files": 5
      }
    ],
    "created_at": "2025-12-01T09:00:00",
    "is_active": true
  }
}
```

## Default Quota Limits

- **Regular Users**: 10 downloads/day, 100 downloads/month
- **Admin Users**: 100 downloads/day, 1000 downloads/month

## Security Features

- ✅ Password hashing with bcrypt
- ✅ Session-based authentication
- ✅ Account activation/deactivation
- ✅ Download quota enforcement
- ✅ Real-time quota tracking

## Customization

### Changing Default Limits

Edit `users_db.py` in the `register_user` method:

```python
def register_user(self, username: str, password: str, email: str, 
                 daily_limit: int = 10,     # Change this
                 monthly_limit: int = 100)  # Change this
```

### Adjusting Individual User Limits

Use admin tools:
```bash
python admin_tools.py update-limits username --daily 20 --monthly 200
```

## Troubleshooting

### "Invalid username or password"
- Check your credentials
- Ensure account is active (contact admin)

### "Daily/Monthly limit exceeded"
- Wait for quota reset (daily: midnight, monthly: 1st of month)
- Contact admin to increase limits

### Users.json not found
- File is auto-created on first user registration
- Ensure write permissions in application directory

## API Reference

### UserDatabase Class

Main methods:
- `register_user(username, password, email)` - Create new user
- `authenticate(username, password)` - Verify credentials
- `can_download(username, num_files)` - Check quota
- `record_download(username, num_files)` - Record download
- `get_user_info(username)` - Get user statistics
- `update_user_limits(username, daily, monthly)` - Modify limits

## Future Enhancements

Potential improvements:
- [ ] Password reset functionality
- [ ] Email verification
- [ ] User roles (admin, premium, standard)
- [ ] Download history export
- [ ] Quota notifications
- [ ] Database migration to SQLite/PostgreSQL

## Support

For issues or questions:
1. Check this README
2. Review admin tools help: `python admin_tools.py --help`
3. Contact system administrator
