"""
Admin tools for managing users and download quotas.
Usage: python admin_tools.py [command] [options]
"""

import argparse
from users_db import UserDatabase
from datetime import datetime

def list_users(db: UserDatabase):
    """List all users with their information."""
    if not db.users:
        print("No users registered.")
        return
    
    print("\n" + "="*100)
    print(f"{'Username':<20} {'Email':<30} {'Daily':<15} {'Monthly':<15} {'Active':<10}")
    print("="*100)
    
    for username in db.users:
        user_info = db.get_user_info(username)
        daily = f"{user_info['daily_downloads']}/{user_info['daily_limit']}"
        monthly = f"{user_info['monthly_downloads']}/{user_info['monthly_limit']}"
        active = "Yes" if user_info['is_active'] else "No"
        
        print(f"{username:<20} {user_info['email']:<30} {daily:<15} {monthly:<15} {active:<10}")
    
    print("="*100 + "\n")

def user_details(db: UserDatabase, username: str):
    """Show detailed information about a specific user."""
    user_info = db.get_user_info(username)
    
    if not user_info:
        print(f"User '{username}' not found.")
        return
    
    print(f"\n{'='*50}")
    print(f"User Details: {username}")
    print(f"{'='*50}")
    print(f"Email: {user_info['email']}")
    print(f"Account Status: {'Active' if user_info['is_active'] else 'Inactive'}")
    print(f"Created: {user_info['created_at']}")
    print(f"\nDownload Limits:")
    print(f"  Daily: {user_info['daily_downloads']}/{user_info['daily_limit']}")
    print(f"  Monthly: {user_info['monthly_downloads']}/{user_info['monthly_limit']}")
    
    # Show recent downloads
    if username in db.users and db.users[username].get('downloads'):
        print(f"\nRecent Downloads:")
        downloads = db.users[username]['downloads'][-10:]  # Last 10
        for download in reversed(downloads):
            date = datetime.fromisoformat(download['date']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {date} - {download['num_files']} files")
    
    print(f"{'='*50}\n")

def update_limits(db: UserDatabase, username: str, daily: int = None, monthly: int = None):
    """Update user download limits."""
    if username not in db.users:
        print(f"User '{username}' not found.")
        return
    
    if db.update_user_limits(username, daily, monthly):
        print(f"✅ Updated limits for user '{username}':")
        if daily is not None:
            print(f"   Daily limit: {daily}")
        if monthly is not None:
            print(f"   Monthly limit: {monthly}")
    else:
        print(f"❌ Failed to update limits for user '{username}'")

def toggle_user_status(db: UserDatabase, username: str, activate: bool):
    """Activate or deactivate a user account."""
    if username not in db.users:
        print(f"User '{username}' not found.")
        return
    
    if activate:
        if db.activate_user(username):
            print(f"✅ User '{username}' activated.")
        else:
            print(f"❌ Failed to activate user '{username}'")
    else:
        if db.deactivate_user(username):
            print(f"✅ User '{username}' deactivated.")
        else:
            print(f"❌ Failed to deactivate user '{username}'")

def create_admin_user(db: UserDatabase, username: str, password: str, email: str):
    """Create a user with higher limits (admin/premium user)."""
    if db.register_user(username, password, email, daily_limit=100, monthly_limit=1000):
        print(f"✅ Admin/Premium user '{username}' created successfully!")
        print(f"   Daily limit: 100")
        print(f"   Monthly limit: 1000")
    else:
        print(f"❌ Failed to create user. Username may already exist.")

def main():
    parser = argparse.ArgumentParser(description="Admin tools for GPM IMERGDL user management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List users
    subparsers.add_parser('list', help='List all users')
    
    # User details
    details_parser = subparsers.add_parser('details', help='Show detailed user information')
    details_parser.add_argument('username', help='Username to show details for')
    
    # Update limits
    limits_parser = subparsers.add_parser('update-limits', help='Update user download limits')
    limits_parser.add_argument('username', help='Username to update')
    limits_parser.add_argument('--daily', type=int, help='New daily limit')
    limits_parser.add_argument('--monthly', type=int, help='New monthly limit')
    
    # Activate user
    activate_parser = subparsers.add_parser('activate', help='Activate a user account')
    activate_parser.add_argument('username', help='Username to activate')
    
    # Deactivate user
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate a user account')
    deactivate_parser.add_argument('username', help='Username to deactivate')
    
    # Create admin user
    admin_parser = subparsers.add_parser('create-admin', help='Create admin/premium user with higher limits')
    admin_parser.add_argument('username', help='Username for new admin')
    admin_parser.add_argument('password', help='Password for new admin')
    admin_parser.add_argument('email', help='Email for new admin')
    
    args = parser.parse_args()
    
    # Initialize database
    db = UserDatabase()
    
    # Execute command
    if args.command == 'list':
        list_users(db)
    elif args.command == 'details':
        user_details(db, args.username)
    elif args.command == 'update-limits':
        update_limits(db, args.username, args.daily, args.monthly)
    elif args.command == 'activate':
        toggle_user_status(db, args.username, True)
    elif args.command == 'deactivate':
        toggle_user_status(db, args.username, False)
    elif args.command == 'create-admin':
        create_admin_user(db, args.username, args.password, args.email)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
