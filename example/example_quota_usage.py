"""
Example script demonstrating QuotaManager usage
This shows how to interact with the quota system programmatically
"""

import json
from datetime import datetime

# Import from main app
import sys
sys.path.append('.')
from app import QuotaManager, DEFAULT_DAILY_QUOTA, DEFAULT_MONTHLY_QUOTA

def example_user_operations():
    """Demonstrate basic user operations"""
    print("=" * 60)
    print("QUOTA SYSTEM - EXAMPLE OPERATIONS")
    print("=" * 60)
    
    # Initialize quota manager
    quota_manager = QuotaManager()
    
    # Example 1: Create a new user
    print("\n1. Creating a new user...")
    success, message = quota_manager.create_user(
        username="demo_user",
        email="demo@example.com",
        password="demo123",
        daily_quota=50,  # Custom quota
        monthly_quota=500
    )
    print(f"   Result: {message}")
    
    # Example 2: Authenticate user
    print("\n2. Authenticating user...")
    success, message = quota_manager.authenticate_user("demo_user", "demo123")
    print(f"   Result: {message}")
    
    # Example 3: Check quota before download
    print("\n3. Checking quota for 20 files...")
    success, message = quota_manager.check_quota("demo_user", 20)
    print(f"   Result: {message}")
    
    # Example 4: Simulate download and update usage
    if success:
        print("\n4. Simulating download of 20 files...")
        quota_manager.update_usage("demo_user", 20)
        print("   Usage updated successfully")
    
    # Example 5: Get user statistics
    print("\n5. Retrieving user statistics...")
    stats = quota_manager.get_user_stats("demo_user")
    if stats:
        print(f"   Username: {stats['username']}")
        print(f"   Email: {stats['email']}")
        print(f"   Daily: {stats['daily_usage']}/{stats['daily_quota']} (Remaining: {stats['daily_remaining']})")
        print(f"   Monthly: {stats['monthly_usage']}/{stats['monthly_quota']} (Remaining: {stats['monthly_remaining']})")
        print(f"   Total Downloads: {stats['total_downloads']}")
    
    # Example 6: Try to exceed quota
    print("\n6. Attempting to exceed quota (requesting 40 more files)...")
    success, message = quota_manager.check_quota("demo_user", 40)
    print(f"   Result: {message}")
    
    # Example 7: Admin updates quota
    print("\n7. Admin updating user quota...")
    success, message = quota_manager.update_user_quota("demo_user", daily_quota=100, monthly_quota=1000)
    print(f"   Result: {message}")
    
    # Example 8: Check quota again after update
    print("\n8. Checking quota again after admin update...")
    success, message = quota_manager.check_quota("demo_user", 40)
    print(f"   Result: {message}")
    
    # Example 9: List all users (admin function)
    print("\n9. Listing all users...")
    users = quota_manager.list_all_users()
    print(f"   Total users: {len(users)}")
    for user in users:
        print(f"   - {user}")
    
    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETED")
    print("=" * 60)

def example_admin_operations():
    """Demonstrate admin operations"""
    print("\n" + "=" * 60)
    print("ADMIN OPERATIONS EXAMPLE")
    print("=" * 60)
    
    quota_manager = QuotaManager()
    
    # Verify admin password
    print("\n1. Verifying admin password...")
    is_admin = quota_manager.verify_admin("admin123")
    print(f"   Admin verified: {is_admin}")
    
    # Create multiple users
    print("\n2. Creating multiple test users...")
    users_to_create = [
        ("user1", "user1@test.com", "pass1", 75, 750),
        ("user2", "user2@test.com", "pass2", 100, 1000),
        ("user3", "user3@test.com", "pass3", 150, 1500),
    ]
    
    for username, email, password, daily, monthly in users_to_create:
        success, msg = quota_manager.create_user(username, email, password, daily, monthly)
        print(f"   {username}: {msg}")
    
    # Get statistics for all users
    print("\n3. User Statistics Summary:")
    print(f"   {'Username':<15} {'Email':<25} {'Daily Quota':<12} {'Monthly Quota':<15}")
    print("   " + "-" * 70)
    
    for username in quota_manager.list_all_users():
        stats = quota_manager.get_user_stats(username)
        if stats:
            print(f"   {username:<15} {stats['email']:<25} {stats['daily_quota']:<12} {stats['monthly_quota']:<15}")
    
    print("\n" + "=" * 60)

def example_quota_scenarios():
    """Test various quota scenarios"""
    print("\n" + "=" * 60)
    print("QUOTA SCENARIOS")
    print("=" * 60)
    
    quota_manager = QuotaManager()
    
    # Create test user
    quota_manager.create_user("test_scenarios", "test@example.com", "test123", 100, 1000)
    
    scenarios = [
        ("Small download (10 files)", 10),
        ("Medium download (50 files)", 50),
        ("Large download (90 files)", 90),
        ("Exceeding daily quota (20 more files)", 20),
    ]
    
    print("\nTesting download scenarios:")
    for description, num_files in scenarios:
        print(f"\n   Scenario: {description}")
        success, message = quota_manager.check_quota("test_scenarios", num_files)
        print(f"   Check: {message}")
        
        if success:
            quota_manager.update_usage("test_scenarios", num_files)
            stats = quota_manager.get_user_stats("test_scenarios")
            print(f"   Updated: Daily {stats['daily_usage']}/{stats['daily_quota']}, Monthly {stats['monthly_usage']}/{stats['monthly_quota']}")
        else:
            print(f"   Status: Download blocked")
    
    print("\n" + "=" * 60)

def view_database():
    """Display the current database contents"""
    print("\n" + "=" * 60)
    print("DATABASE CONTENTS")
    print("=" * 60)
    
    try:
        with open('quota_database.json', 'r') as f:
            data = json.load(f)
        
        print(f"\nTotal users: {len(data.get('users', {}))}")
        print("\nUser Details:")
        print(json.dumps(data, indent=2, default=str))
    except FileNotFoundError:
        print("\nNo database file found. Run the app or examples first.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "QUOTA SYSTEM - INTERACTIVE EXAMPLES" + " " * 13 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Run examples
    example_user_operations()
    example_admin_operations()
    example_quota_scenarios()
    view_database()
    
    print("\n✅ All examples completed successfully!")
    print("📁 Check 'quota_database.json' for the generated data")
    print("🧹 To clean up, delete 'quota_database.json'\n")
