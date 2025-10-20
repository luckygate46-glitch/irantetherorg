#!/usr/bin/env python3
"""
Reset test user password and verify login
"""

import asyncio
import httpx
import json
import bcrypt

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

async def reset_test_user_password():
    """Reset test user password"""
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Login as admin
        print("🔐 Logging in as admin...")
        response = await client.post(f"{BACKEND_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code != 200:
            print(f"❌ Admin login failed: {response.status_code}")
            return
        
        admin_data = response.json()
        admin_token = admin_data["access_token"]
        print("✅ Admin login successful")
        
        # Get all users to find test user
        print("\n📋 Finding test user...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(f"{BACKEND_URL}/admin/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            test_user = None
            
            for user in users:
                if user.get('email') == 'testuser@example.com':
                    test_user = user
                    break
            
            if test_user:
                print(f"✅ Test user found: {test_user.get('full_name')}")
                print(f"   💰 Current balance: {test_user.get('wallet_balance_tmn', 0):,.0f} TMN")
                
                # Update test user with correct password and balance
                user_id = test_user['id']
                
                # First, let's try to create a new test user with known credentials
                print("\n🔄 Creating fresh test user...")
                
                new_user_data = {
                    "first_name": "Test",
                    "last_name": "User", 
                    "email": "testuser2@example.com",
                    "phone": "09987654321",
                    "password": "password123"
                }
                
                response = await client.post(f"{BACKEND_URL}/auth/register", json=new_user_data)
                
                if response.status_code == 200:
                    new_user = response.json()
                    print("✅ New test user created successfully")
                    
                    new_user_id = new_user['user']['id']
                    
                    # Update with proper balance and settings
                    update_data = {
                        "wallet_balance_tmn": 5000000,
                        "is_admin": False
                    }
                    
                    response = await client.put(f"{BACKEND_URL}/admin/users/{new_user_id}", 
                                              headers=headers, json=update_data)
                    
                    if response.status_code == 200:
                        print("✅ New test user updated with 5M TMN balance")
                    
                    # Set KYC level to 2
                    kyc_approval = {
                        "user_id": new_user_id,
                        "kyc_level": 2,
                        "action": "approve",
                        "admin_note": "Test user setup"
                    }
                    
                    response = await client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                                               headers=headers, json=kyc_approval)
                    
                    if response.status_code == 200:
                        print("✅ New test user KYC approved to level 2")
                    
                    # Test login with new user
                    print("\n🔐 Testing login with new test user...")
                    response = await client.post(f"{BACKEND_URL}/auth/login", json={
                        "email": "testuser2@example.com",
                        "password": "password123"
                    })
                    
                    if response.status_code == 200:
                        login_data = response.json()
                        user_info = login_data['user']
                        print("✅ New test user login successful!")
                        print(f"   📧 Email: {user_info.get('email')}")
                        print(f"   👤 Full Name: {user_info.get('full_name')}")
                        print(f"   💰 Balance: {user_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                        print(f"   📋 KYC Level: {user_info.get('kyc_level')}")
                        print(f"   🔑 Is Admin: {user_info.get('is_admin')}")
                    else:
                        print(f"❌ New test user login failed: {response.status_code}")
                
                else:
                    print(f"❌ New test user creation failed: {response.status_code} - {response.text}")
                
                # Also try to test login with original testuser@example.com with different passwords
                print("\n🔐 Testing original test user with different passwords...")
                test_passwords = ["password123", "testpass123", "123456", "password", "test123"]
                
                for pwd in test_passwords:
                    response = await client.post(f"{BACKEND_URL}/auth/login", json={
                        "email": "testuser@example.com",
                        "password": pwd
                    })
                    
                    if response.status_code == 200:
                        print(f"✅ Original test user login successful with password: {pwd}")
                        break
                    else:
                        print(f"❌ Password '{pwd}' failed")
            
            else:
                print("❌ Test user not found")
        
        else:
            print(f"❌ Failed to get users: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(reset_test_user_password())