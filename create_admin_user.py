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

BACKEND_URL = "https://tehcrypto.preview.emergentagent.com/api"
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def create_admin_user():
    """Create an admin user by registering and then updating database"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # First, try to register a new admin user
        admin_data = {
            "email": "testuser@example.com",
            "password": "testpass"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            # Try to login with existing user
            login_response = await http_client.post(f"{BACKEND_URL}/auth/login", json=admin_data)
            
            if login_response.status_code == 200:
                print("✅ User logged in successfully")
                login_data = login_response.json()
                user_info = login_data.get("user", {})
                user_id = user_info.get("id")
            else:
                print(f"❌ Failed to login user: {login_response.text}")
                return False
            
            # Update user to be admin in database
            if user_id:
                result = await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"is_admin": True}}
                )
                
                if result.modified_count > 0:
                    print(f"✅ User {admin_data['email']} is now an admin")
                    
                    # Test admin access
                    token = login_data.get("access_token")
                    if token:
                        headers = {"Authorization": f"Bearer {token}"}
                        admin_test = await http_client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
                        
                        if admin_test.status_code == 200:
                            print("✅ Admin access confirmed - can access admin endpoints")
                            print(f"Admin credentials: {admin_data['email']} / {admin_data['password']}")
                            return True
                        else:
                            print(f"❌ Admin access test failed: {admin_test.status_code}")
                            return False
                else:
                    print("❌ Failed to update user admin status")
                    return False
            else:
                print("❌ No user ID found")
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