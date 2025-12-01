# 🎯 Complete User Authentication System - Installation & Testing Guide

## 📦 What You Got

### Core Files
✅ `app.py` - Main application with authentication
✅ `users_db.py` - User database management
✅ `admin_tools.py` - Admin command-line tools
✅ `requirements.txt` - Updated with auth dependencies

### Documentation
✅ `docs/USER_AUTH_README.md` - Complete documentation
✅ `docs/QUICK_START.md` - Quick reference guide
✅ `IMPLEMENTATION_SUMMARY.md` - Implementation overview

### Utilities
✅ `create_demo_users.py` - Create test users
✅ `.gitignore` - Protects sensitive data

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Demo Users (Optional)
```bash
python create_demo_users.py
```
This creates 3 test users with password "password123"

### Step 3: Run Application
```bash
streamlit run app.py
```

## 🎮 Try It Out

### Test Scenario 1: New User Registration
1. Open http://localhost:8501
2. Click **Register** button
3. Enter:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `mypassword`
4. Click **Create Account**
5. Click **Login** and enter credentials
6. ✅ You're in! See your quota in sidebar

### Test Scenario 2: Using Demo Account
1. Click **Login**
2. Username: `demo_user`
3. Password: `password123`
4. ✅ Login successful!
5. See quota: 0/10 daily, 0/100 monthly

### Test Scenario 3: Check Quota Enforcement
1. Login as `test_user` (limit: 5/day)
2. Try to download 10 days of data (10 files)
3. ❌ System blocks: "Daily limit exceeded"
4. Try 3 days (3 files)
5. ✅ Download succeeds!
6. Quota updates: 3/5 daily

### Test Scenario 4: Admin Functions
```bash
# View all users
python admin_tools.py list

# Check a user
python admin_tools.py details demo_user

# Increase limits for test_user
python admin_tools.py update-limits test_user --daily 20 --monthly 200

# Deactivate a user
python admin_tools.py deactivate test_user

# Reactivate
python admin_tools.py activate test_user
```

## 🎨 What You'll See

### Login Screen
```
🌧️ GPM IMERGDL V7 Downloader and Extractor v1.0
Please login or register to access the downloader.

[Login]  [Register]
─────────────────────────────
🔐 Login
Username: [________]
Password: [________]
         [Login]
```

### Main App (After Login)
```
🌧️ GPM IMERGDL V7...              [🚪 Logout]
───────────────────────────────────────────────

Sidebar:
  👤 demo_user
  📧 demo@example.com
  ─────────────────
  📊 Download Quota
  Daily: 0/10
  █░░░░░░░░░ 0%
  Remaining today: 10
  
  Monthly: 0/100
  █░░░░░░░░░ 0%
  Remaining this month: 100

Main Area:
  Start Date: [2025-01-01]
  End Date: [2025-01-31]
  Upload Shapefile: [Browse...]
  Upload CSV: [Browse...]
  [Download and Process]
```

## 📊 Admin Commands Reference

```bash
# See all commands
python admin_tools.py --help

# List users
python admin_tools.py list
# Output:
# Username            Email                   Daily          Monthly        Active
# ==================================================================================
# demo_user          demo@example.com        0/10           0/100          Yes

# User details
python admin_tools.py details demo_user
# Shows: email, status, limits, recent downloads

# Update limits
python admin_tools.py update-limits USERNAME --daily NUM --monthly NUM

# Activate/Deactivate
python admin_tools.py activate USERNAME
python admin_tools.py deactivate USERNAME

# Create premium user
python admin_tools.py create-admin USERNAME PASSWORD EMAIL
# Creates user with 100/day, 1000/month limits
```

## 🧪 Testing Checklist

- [ ] Install dependencies successfully
- [ ] Create demo users
- [ ] Run application
- [ ] Register new user
- [ ] Login with new user
- [ ] See quota in sidebar
- [ ] Try downloading within quota
- [ ] Try exceeding quota (verify block)
- [ ] Logout
- [ ] Login with demo_user
- [ ] Run admin list command
- [ ] Run admin details command
- [ ] Update user limits
- [ ] Verify new limits work

## 🔑 Demo Users (Created by create_demo_users.py)

| Username | Password | Daily | Monthly | Use Case |
|----------|----------|-------|---------|----------|
| demo_user | password123 | 10 | 100 | Standard user testing |
| premium_user | password123 | 100 | 1,000 | Premium user testing |
| test_user | password123 | 5 | 50 | Quota limit testing |

## 📁 File Structure

```
GPM-IMERGDL-V7-Downloader/
├── app.py                      # Main app with auth
├── users_db.py                 # User database class
├── admin_tools.py              # Admin CLI tools
├── create_demo_users.py        # Demo user creator
├── requirements.txt            # Dependencies
├── .gitignore                  # Protects users.json
├── IMPLEMENTATION_SUMMARY.md   # Overview
├── INSTALL_TEST_GUIDE.md       # This file
└── docs/
    ├── USER_AUTH_README.md     # Full documentation
    └── QUICK_START.md          # Quick reference

Auto-generated:
├── users.json                  # User database (created after first registration)
└── IMERG_Downloads/            # Downloaded data folder
```

## 🎯 Key Features to Test

### 1. Registration
- [x] Username validation (min 3 chars)
- [x] Password validation (min 6 chars)
- [x] Email validation (contains @)
- [x] Duplicate username prevention
- [x] Password hashing

### 2. Authentication
- [x] Login with valid credentials
- [x] Reject invalid credentials
- [x] Session persistence
- [x] Logout functionality

### 3. Quota System
- [x] Display current usage
- [x] Calculate files to download
- [x] Block if exceeds daily limit
- [x] Block if exceeds monthly limit
- [x] Record downloads
- [x] Update display after download

### 4. Admin Tools
- [x] List all users
- [x] View user details
- [x] Update user limits
- [x] Activate/deactivate users
- [x] Create premium users

## ⚠️ Important Notes

1. **users.json** is auto-created on first user registration
2. **Password** is stored as bcrypt hash (secure)
3. **Quota** resets daily at midnight, monthly on 1st
4. **Downloads** are counted by number of files (days in date range)
5. **Admin** commands need users.json to exist (register user first)

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'bcrypt'"
```bash
pip install -r requirements.txt
```

### "User not found" when using admin tools
Create a user first:
```bash
python create_demo_users.py
```

### Can't login after registration
- Check username spelling
- Ensure password is correct
- Verify account is active (use admin tools)

### Download blocked unexpectedly
Check quota:
```bash
python admin_tools.py details YOUR_USERNAME
```

## 📞 Need Help?

1. **Full Documentation**: See `docs/USER_AUTH_README.md`
2. **Quick Reference**: See `docs/QUICK_START.md`
3. **Overview**: See `IMPLEMENTATION_SUMMARY.md`
4. **Admin Help**: Run `python admin_tools.py --help`

## ✅ Success Criteria

You know it's working when:
- ✅ Can register new users
- ✅ Can login and see quota
- ✅ Downloads are blocked when quota exceeded
- ✅ Downloads work when quota available
- ✅ Quota updates after download
- ✅ Admin tools show user info
- ✅ Logout works properly

## 🎊 You're All Set!

Your authentication system is:
- 🔒 Secure (bcrypt password hashing)
- 📊 Tracked (all downloads recorded)
- 🛡️ Protected (quota enforcement)
- 🎮 Easy to use (simple UI)
- 🛠️ Manageable (admin tools)

**Start testing now:**
```bash
streamlit run app.py
```

Enjoy your enhanced GPM IMERGDL V7 Downloader! 🌧️
