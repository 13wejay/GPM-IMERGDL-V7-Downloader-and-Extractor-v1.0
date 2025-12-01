# Quota System Workflow Diagrams

## 1. User Registration Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    USER REGISTRATION                         │
└─────────────────────────────────────────────────────────────┘

    User Opens App
         ↓
    Clicks "Register" Tab
         ↓
    Enters: Username, Email, Password
         ↓
    Clicks "Register" Button
         ↓
    ┌─────────────────────┐
    │  System Validates   │
    │  - Username unique? │
    │  - Valid email?     │
    │  - Password ≥ 6?    │
    └─────────────────────┘
         ↓
    ┌─────────────────────┐
    │  If Valid:          │
    │  - Hash password    │
    │  - Set quotas       │
    │  - Save to DB       │
    └─────────────────────┘
         ↓
    Success Message Displayed
    Default Quotas: 100/day, 1000/month
```

## 2. User Login Flow
```
┌─────────────────────────────────────────────────────────────┐
│                      USER LOGIN                              │
└─────────────────────────────────────────────────────────────┘

    User Enters Username & Password
         ↓
    Clicks "Login"
         ↓
    ┌──────────────────────┐
    │  System Checks:      │
    │  - User exists?      │
    │  - Password correct? │
    └──────────────────────┘
         ↓
    ┌──────────────────────┐         ┌──────────────────────┐
    │   If Success:        │         │   If Failure:        │
    │   - Set session      │         │   - Show error msg   │
    │   - Update login     │         │   - Stay logged out  │
    │   - Load stats       │         └──────────────────────┘
    └──────────────────────┘
         ↓
    Dashboard Displays:
    - Username
    - Quota metrics
    - Usage progress
```

## 3. Download & Quota Check Flow
```
┌─────────────────────────────────────────────────────────────┐
│              DOWNLOAD WITH QUOTA CHECK                       │
└─────────────────────────────────────────────────────────────┘

    User Logged In
         ↓
    Enters Date Range
         ↓
    Uploads Files (Shapefile, CSV)
         ↓
    Clicks "Download and Process"
         ↓
    ┌──────────────────────────────┐
    │  Calculate Required Files    │
    │  files = days in range       │
    └──────────────────────────────┘
         ↓
    ┌──────────────────────────────┐
    │  CHECK DAILY QUOTA           │
    │  current + requested         │
    │  ≤ daily_quota?              │
    └──────────────────────────────┘
         ↓ YES          ↓ NO
         ↓              └──→ ❌ Block & Show Error
         ↓
    ┌──────────────────────────────┐
    │  CHECK MONTHLY QUOTA         │
    │  current + requested         │
    │  ≤ monthly_quota?            │
    └──────────────────────────────┘
         ↓ YES          ↓ NO
         ↓              └──→ ❌ Block & Show Error
         ↓
    ✅ QUOTA OK - Proceed
         ↓
    Download Files
         ↓
    Process Data
         ↓
    ┌──────────────────────────────┐
    │  UPDATE USAGE                │
    │  - Add to daily counter      │
    │  - Add to monthly counter    │
    │  - Add to total counter      │
    │  - Save to database          │
    └──────────────────────────────┘
         ↓
    Success! Provide Download Link
```

## 4. Admin Panel Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN PANEL                               │
└─────────────────────────────────────────────────────────────┘

    User Clicks "Admin" Tab
         ↓
    Enters Admin Password
         ↓
    ┌──────────────────────────────┐
    │  Verify Admin Password       │
    │  (default: admin123)         │
    └──────────────────────────────┘
         ↓
    ✅ Access Granted
         ↓
    ┌──────────────────────────────┐
    │  Admin Panel Shows:          │
    │  - List of all users         │
    │  - User selection dropdown   │
    └──────────────────────────────┘
         ↓
    Select User
         ↓
    ┌──────────────────────────────┐
    │  Display User Stats:         │
    │  - Email                     │
    │  - Current quotas            │
    │  - Current usage             │
    │  - Total downloads           │
    │  - Creation/login dates      │
    └──────────────────────────────┘
         ↓
    Modify Quotas
         ↓
    Click "Update Quota"
         ↓
    ┌──────────────────────────────┐
    │  Save New Quotas to DB       │
    └──────────────────────────────┘
         ↓
    Success Message
```

## 5. Data Structure
```
┌─────────────────────────────────────────────────────────────┐
│                  quota_database.json                         │
└─────────────────────────────────────────────────────────────┘

{
  "users": {
    "john_doe": {
      ├─ "email": "john@example.com"
      ├─ "password_hash": "sha256..."
      ├─ "daily_quota": 100
      ├─ "monthly_quota": 1000
      ├─ "usage": {
      │    ├─ "daily": {
      │    │    ├─ "2025-12-01": 15
      │    │    └─ "2025-12-02": 20
      │    │  }
      │    ├─ "monthly": {
      │    │    ├─ "2025-11": 450
      │    │    └─ "2025-12": 35
      │    │  }
      │    └─ "total": 485
      │  }
      ├─ "created_at": "2025-11-15T10:30:00"
      └─ "last_login": "2025-12-02T09:15:00"
    }
  },
  "admin_hash": "sha256_of_admin_password"
}
```

## 6. Quota Reset Timeline
```
┌─────────────────────────────────────────────────────────────┐
│                   QUOTA RESET SCHEDULE                       │
└─────────────────────────────────────────────────────────────┘

DAILY QUOTA:
─────────────────────────────────────────────────────────────
Day 1 (Dec 1)         Day 2 (Dec 2)         Day 3 (Dec 3)
│                     │                     │
├─ Usage: 0/100       ├─ Usage: 0/100       ├─ Usage: 0/100
├─ Download: 50       ├─ Download: 75       ├─ Download: 30
├─ Usage: 50/100      ├─ Usage: 75/100      ├─ Usage: 30/100
│                     │                     │
└─► Midnight          └─► Midnight          └─► Midnight
    RESET                 RESET                 RESET


MONTHLY QUOTA:
─────────────────────────────────────────────────────────────
November                December              January
│                       │                     │
├─ Usage: 0/1000        ├─ Usage: 0/1000      ├─ Usage: 0/1000
├─累計: 450            ├─累計: 650          ├─累計: 300
│                       │                     │
└─► Nov 30 → Dec 1      └─► Dec 31 → Jan 1    └─► Jan 31 → Feb 1
    RESET                   RESET                 RESET


TOTAL DOWNLOADS:
─────────────────────────────────────────────────────────────
Nov: +450  →  Dec: +650  →  Jan: +300  →  Total: 1400
             (Never resets - cumulative counter)
```

## 7. User Journey Map
```
┌─────────────────────────────────────────────────────────────┐
│                  COMPLETE USER JOURNEY                       │
└─────────────────────────────────────────────────────────────┘

NEW USER:
  Open App → Register → Login → View Quota → Download → Logout
    │          │         │         │            │          │
    │          │         │         │            │          │
  Welcome   Create   Verify   See Stats   Check Quota  Exit
           Account  Identity  Dashboard   & Process    Session


RETURNING USER:
  Open App → Login → Check Stats → Download → Monitor → Logout
    │          │         │            │          │         │
    │          │         │            │          │         │
  Welcome   Verify   View Usage   Process    Track      Exit
           Identity   Progress     Request   Updates   Session


ADMIN:
  Open App → Admin Panel → View Users → Modify Quotas → Save
    │             │            │              │           │
    │             │            │              │           │
  Welcome    Authenticate   Review        Adjust      Update
                           Activity      Limits      Database
```

## 8. Security Model
```
┌─────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                            │
└─────────────────────────────────────────────────────────────┘

APPLICATION LEVEL:
┌──────────────────────────────────────────────────────────┐
│  1. Password Hashing (SHA-256)                           │
│     Plain Password → Hash → Store Hash Only             │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│  2. Session Management                                   │
│     Login → Session State → Access Control              │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│  3. Role-Based Access                                    │
│     User: Download only                                  │
│     Admin: Full management                               │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│  4. Quota Enforcement                                    │
│     Pre-download checks → Block if exceeded             │
└──────────────────────────────────────────────────────────┘

DATA LEVEL:
┌──────────────────────────────────────────────────────────┐
│  • No plain-text passwords stored                        │
│  • JSON file permissions (filesystem level)             │
│  • Session data in memory only                          │
└──────────────────────────────────────────────────────────┘
```

---

## Legend

```
│  = Flow connector
├─ = Branch point
└─ = End point
→  = Direction
✅ = Success
❌ = Failure/Block
```

## Quick Reference

### Key Decision Points:
1. **Registration**: Valid input? → Create user or show error
2. **Login**: Correct credentials? → Grant access or deny
3. **Quota Check**: Within limits? → Allow download or block
4. **Admin**: Correct password? → Show panel or deny

### Key Actions:
- **Hash**: Password → SHA-256 hash
- **Check**: Compare values against limits
- **Update**: Increment counters and save
- **Reset**: Clear daily/monthly at boundaries

---

*Visual representation of the quota system workflows*
