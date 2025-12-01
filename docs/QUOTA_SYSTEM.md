# Quota System Documentation

## Overview
The GPM IMERGDL V7 Downloader now includes a comprehensive quota system to manage user access and track download usage based on username/email.

## Features

### 1. User Authentication
- **Registration**: New users can register with username, email, and password
- **Login**: Secure authentication with SHA-256 password hashing
- **Session Management**: Persistent login state during app session

### 2. Quota Management
- **Daily Quota**: Limit on number of files users can download per day
- **Monthly Quota**: Limit on number of files users can download per month
- **Total Tracking**: Cumulative download statistics for each user

### 3. Default Quotas
- Daily Quota: 100 files
- Monthly Quota: 1000 files
- These can be customized per user by administrators

## User Interface

### Sidebar Features

#### Login Tab
- Username and password fields
- Secure authentication
- Session persistence

#### Register Tab
- Username (unique identifier)
- Email address
- Password (minimum 6 characters)
- Password confirmation
- Automatic quota assignment

#### Admin Tab
- Admin password authentication
- View all users
- Modify user quotas
- View detailed user statistics

### Main Dashboard (When Logged In)
- Real-time quota usage display
- Daily and monthly progress bars
- Total downloads counter
- Remaining quota indicators

## How It Works

### 1. User Registration
```
1. User fills registration form
2. System validates input
3. Password is hashed using SHA-256
4. User profile created with default quotas
5. Data saved to quota_database.json
```

### 2. Download Process
```
1. User logs in
2. Selects date range and uploads files
3. System calculates number of files to download
4. Quota check performed before download
5. If quota sufficient:
   - Download proceeds
   - Usage updated automatically
6. If quota exceeded:
   - Download blocked
   - User informed of remaining quota
```

### 3. Quota Tracking
- **Daily Reset**: Usage resets at midnight (system timezone)
- **Monthly Reset**: Usage resets on 1st of each month
- **Persistent Storage**: All data stored in `quota_database.json`

## Database Structure

### quota_database.json Format
```json
{
  "users": {
    "username1": {
      "email": "user@example.com",
      "password_hash": "hashed_password",
      "daily_quota": 100,
      "monthly_quota": 1000,
      "usage": {
        "daily": {
          "2025-12-01": 15,
          "2025-12-02": 20
        },
        "monthly": {
          "2025-12": 35
        },
        "total": 150
      },
      "created_at": "2025-12-01T10:30:00",
      "last_login": "2025-12-01T14:20:00"
    }
  },
  "admin_hash": "admin_password_hash"
}
```

## Admin Functions

### Default Admin Password
- Default: `admin123`
- **⚠️ IMPORTANT**: Change this in production!

### Admin Capabilities
1. **View All Users**: See list of registered users
2. **View User Details**: Complete statistics for any user
3. **Update Quotas**: Modify daily/monthly limits per user
4. **Monitor Usage**: Track download patterns

### Changing Admin Password
Edit the `ADMIN_PASSWORD` variable in `app.py`:
```python
ADMIN_PASSWORD = "your_secure_password_here"
```

## Quota System Configuration

### Adjusting Default Quotas
Modify these constants in `app.py`:
```python
DEFAULT_DAILY_QUOTA = 100   # Files per day
DEFAULT_MONTHLY_QUOTA = 1000  # Files per month
```

### Per-User Custom Quotas
Admins can set custom quotas for specific users through the Admin Panel:
1. Login as admin
2. Select user from dropdown
3. Enter new quota values
4. Click "Update Quota"

## Security Features

### Password Security
- SHA-256 hashing
- No plain text storage
- Secure comparison

### Session Management
- Server-side session state
- Automatic logout option
- No exposed credentials

### Database Protection
- JSON file-based storage
- Local filesystem access only
- Admin-only quota modifications

## Usage Examples

### Example 1: New User Registration
```
1. Click "Register" tab
2. Enter:
   - Username: john_doe
   - Email: john@example.com
   - Password: secure123
3. System creates user with:
   - Daily quota: 100
   - Monthly quota: 1000
```

### Example 2: Quota Check
```
User wants to download 15 days of data:
- Files needed: 15
- Current daily usage: 90
- Daily quota: 100
- Result: ✅ Allowed (90 + 15 = 105 > 100 ❌)
Wait, recalculate: ✅ Allowed (90 + 15 = 105, but 105 > 100, so ❌ DENIED)
Actually: Daily remaining = 100 - 90 = 10
User needs 15 but only has 10 remaining = DENIED
```

### Example 3: Admin Quota Update
```
Admin increases user quota:
1. Login as admin
2. Select user "john_doe"
3. Set daily quota: 200
4. Set monthly quota: 2000
5. User can now download more files
```

## Error Messages

### Common Messages
- **"Daily quota exceeded. Remaining: X files"**: User hit daily limit
- **"Monthly quota exceeded. Remaining: X files"**: User hit monthly limit
- **"User not found"**: Invalid username
- **"Incorrect password"**: Authentication failed
- **"Username already exists"**: Registration conflict

## Best Practices

### For Users
1. Plan downloads within quota limits
2. Check quota status before large downloads
3. Use strong passwords (8+ characters recommended)
4. Contact admin for quota increases if needed

### For Administrators
1. Change default admin password immediately
2. Monitor quota_database.json file size
3. Regularly review user statistics
4. Set appropriate quotas based on server capacity
5. Back up quota_database.json regularly

### For Production Deployment
1. Change `ADMIN_PASSWORD` constant
2. Use environment variables for sensitive data
3. Implement HTTPS for secure transmission
4. Consider database migration (SQLite/PostgreSQL)
5. Add email verification for registrations
6. Implement password recovery mechanism
7. Add rate limiting for login attempts

## Troubleshooting

### Issue: Can't login after registration
**Solution**: Ensure password is at least 6 characters and username is correct

### Issue: Quota not updating
**Solution**: Check if quota_database.json has write permissions

### Issue: Lost admin password
**Solution**: Delete quota_database.json (⚠️ loses all user data) or manually edit admin_hash

### Issue: All users see same quota
**Solution**: Check if database file is corrupted; verify JSON format

## Future Enhancements

Potential improvements:
- Email notifications for quota warnings
- Webhook integrations
- API access tokens
- Multi-tier quota plans
- Usage analytics dashboard
- Export usage reports
- Password reset via email
- Two-factor authentication
- User groups/roles
- Scheduled quota resets

## Support

For issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Contact system administrator
4. Check `quota_database.json` for data integrity

---

**Version**: 1.0  
**Last Updated**: December 2025  
**Compatibility**: GPM IMERGDL V7 Downloader and Extractor v1.0
