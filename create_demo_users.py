"""
Demo script to create test users for the authentication system.
Run this to set up some sample users for testing.
"""

from users_db import UserDatabase

def create_demo_users():
    """Create sample users for testing."""
    db = UserDatabase()
    
    print("Creating demo users...\n")
    
    # Demo users with different quota levels
    users = [
        ("demo_user", "password123", "demo@example.com", 10, 100),
        ("premium_user", "password123", "premium@example.com", 100, 1000),
        ("test_user", "password123", "test@example.com", 5, 50),
    ]
    
    for username, password, email, daily, monthly in users:
        if db.register_user(username, password, email, daily, monthly):
            print(f"✅ Created user: {username}")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   Daily limit: {daily}")
            print(f"   Monthly limit: {monthly}")
            print()
        else:
            print(f"⚠️  User '{username}' already exists, skipping...\n")
    
    print("="*60)
    print("Demo users created successfully!")
    print("="*60)
    print("\nYou can now login with any of these accounts:")
    print("  Username: demo_user     | Password: password123")
    print("  Username: premium_user  | Password: password123")
    print("  Username: test_user     | Password: password123")
    print("\nRun: streamlit run app.py")
    print("="*60)

if __name__ == "__main__":
    create_demo_users()
