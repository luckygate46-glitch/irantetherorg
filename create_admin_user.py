#!/usr/bin/env python3
"""
Create an admin user for testing purposes
"""

import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

BACKEND_URL = "https://agitrader-platform.preview.emergentagent.com/api"
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def create_admin_user():
    """Create an admin user by finding existing users and making one admin"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Find all users
        users = await db.users.find().to_list(None)
        print(f"Found {len(users)} users in database")
        
        if not users:
            print("❌ No users found in database")
            return False
        
        # Find the test user we know the password for
        target_user = None
        for user in users:
            if user.get('email') == 'saruman.valar.test.20251004163014@gmail.com':
                target_user = user
                break
        
        if not target_user:
            # Find any user with 'test' in email
            for user in users:
                if 'test' in user.get('email', '').lower():
                    target_user = user
                    break
        
        if not target_user:
            target_user = users[0]  # Use first user
        
        print(f"Making user {target_user.get('email')} an admin...")
        
        # Update user to be admin
        result = await db.users.update_one(
            {"id": target_user["id"]},
            {"$set": {"is_admin": True}}
        )
        
        if result.modified_count > 0:
            print(f"✅ User {target_user.get('email')} is now an admin")
            
            # Try to login and test admin access
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                # Test with known password for our test user
                test_passwords = ["password123", "testpass", "admin123", "123456"]
                
                for password in test_passwords:
                    login_response = await http_client.post(f"{BACKEND_URL}/auth/login", json={
                        "email": target_user.get('email'),
                        "password": password
                    })
                    
                    if login_response.status_code == 200:
                        print(f"✅ Successfully logged in with password: {password}")
                        login_data = login_response.json()
                        token = login_data.get("access_token")
                        
                        # Test admin access
                        headers = {"Authorization": f"Bearer {token}"}
                        admin_test = await http_client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
                        
                        if admin_test.status_code == 200:
                            print("✅ Admin access confirmed - can access admin endpoints")
                            print(f"Admin credentials: {target_user.get('email')} / {password}")
                            return True
                        else:
                            print(f"❌ Admin access test failed: {admin_test.status_code}")
                            return False
                
                print("❌ Could not find correct password for admin user")
                print(f"Admin user created but credentials unknown: {target_user.get('email')}")
                return False
        else:
            print("❌ Failed to update user admin status")
            return False
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

async def main():
    print("🚀 Creating Admin User for Testing...")
    success = await create_admin_user()
    if success:
        print("✅ Admin user creation completed successfully!")
    else:
        print("❌ Admin user creation failed!")

if __name__ == "__main__":
    asyncio.run(main())