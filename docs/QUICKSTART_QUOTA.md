# Quick Start Guide - Quota System

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run app.py
```

### Step 3: Register Your Account
1. Look at the **sidebar** on the left
2. Click the **"Register"** tab
3. Fill in:
   - **Username**: Choose a unique username
   - **Email**: Your email address
   - **Password**: At least 6 characters
   - **Confirm Password**: Same as above
4. Click **"Register"** button

✅ You'll get default quotas:
- 100 files per day
- 1000 files per month

### Step 4: Login
1. Click the **"Login"** tab in sidebar
2. Enter your username and password
3. Click **"Login"**

### Step 5: Check Your Quota
After logging in, the sidebar shows:
- 📊 Daily usage (e.g., 0/100)
- 📊 Monthly usage (e.g., 0/1000)
- 📊 Total downloads
- Progress bars for quick visual reference

### Step 6: Download Data
1. Enter date range (YYYY-MM-DD format)
2. Upload shapefile (as ZIP)
3. Upload CSV with coordinates
4. Click **"Download and Process"**

The system will:
- ✅ Check if you have enough quota
- ⬇️ Download files if quota available
- 📈 Update your usage automatically
- ❌ Block download if quota exceeded

## 👨‍💼 Admin Access

### Login as Admin
1. Click **"Admin"** tab in sidebar
2. Enter admin password: `admin123` (⚠️ change this!)
3. Click **"Access Admin Panel"**

### Admin Features
- View all registered users
- See detailed user statistics
- Update user quotas
- Monitor system usage

### Change Admin Password
Edit `app.py` and find:
```python
ADMIN_PASSWORD = "admin123"  # Change this!
```
Replace with your secure password.

## 📊 Quota Examples

### Example 1: Daily Limit
```
Your quota: 100 files/day
Current usage: 85 files today
Request: 20 files
Result: ❌ DENIED (85 + 20 = 105 > 100)
```

### Example 2: Success
```
Your quota: 100 files/day
Current usage: 80 files today
Request: 15 files
Result: ✅ APPROVED (80 + 15 = 95 < 100)
```

## 🛠️ Common Tasks

### View My Quota
- Just login - it's displayed in the sidebar automatically

### Request Quota Increase
1. Contact your admin
2. Admin logs into Admin Panel
3. Admin selects your username
4. Admin updates your quotas
5. Changes take effect immediately

### Reset My Password
Currently not available - contact admin to:
1. Delete your account (admin deletes from quota_database.json)
2. Re-register with new password

## ⚠️ Important Notes

1. **Quota resets automatically**:
   - Daily quota: Resets at midnight
   - Monthly quota: Resets on 1st of each month

2. **Files are counted**, not file size:
   - 1 day of data = 1 file
   - 30 days of data = 30 files

3. **Quota checked before download**:
   - System won't start download if quota insufficient
   - No partial downloads charged to quota

4. **Sessions persist**:
   - Stay logged in during browser session
   - Click "Logout" to end session

## 🔒 Security Tips

### For Users
- Use strong passwords (8+ characters, mix of letters/numbers)
- Don't share your credentials
- Logout when done

### For Admins
- Change default admin password IMMEDIATELY
- Regularly backup `quota_database.json`
- Monitor user activity
- Set reasonable quotas based on server capacity

## 📁 Files Created

After running the app, you'll see:
- `quota_database.json` - User data and quotas
- `IMERG_Downloads/` - Downloaded files
- `shapefile_extract/` - Temporary shapefile data

## 🆘 Troubleshooting

### Can't register: "Username already exists"
- Choose a different username
- Usernames must be unique

### Can't download: "Daily quota exceeded"
- Wait until tomorrow (quota resets at midnight)
- OR ask admin for quota increase

### Can't download: "Monthly quota exceeded"
- Wait until next month
- OR ask admin for quota increase

### Forgot password
- Contact admin
- No self-service password reset yet

### Admin panel not showing
- Verify admin password is correct
- Default is `admin123`
- Check if it was changed

## 📞 Need Help?

1. Check the full documentation: `QUOTA_SYSTEM.md`
2. Review error messages carefully
3. Contact your system administrator
4. Check the sidebar for current quota status

---

**Happy Downloading! 🎉**
