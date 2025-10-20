#!/usr/bin/env python3
"""
Check existing users and create test user if needed
"""

import asyncio
import httpx
import json

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

async def check_and_create_test_user():
    """Check existing users and create test user if needed"""
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
        
        # Get all users
        print("\n📋 Getting all users...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(f"{BACKEND_URL}/admin/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"📊 Total users found: {len(users)}")
            
            # Look for test user
            test_user_found = False
            for user in users:
                if user.get('email') == 'testuser@example.com':
                    test_user_found = True
                    print(f"✅ Test user found:")
                    print(f"   📧 Email: {user.get('email')}")
                    print(f"   👤 Full Name: {user.get('full_name')}")
                    print(f"   💰 Balance: {user.get('wallet_balance_tmn', 0):,.0f} TMN")
                    print(f"   📋 KYC Level: {user.get('kyc_level')}")
                    print(f"   🔑 Is Admin: {user.get('is_admin')}")
                    break
            
            if not test_user_found:
                print("❌ Test user not found, creating one...")
                
                # Create test user
                user_data = {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "testuser@example.com",
                    "phone": "09123456789",
                    "password": "password123"
                }
                
                response = await client.post(f"{BACKEND_URL}/auth/register", json=user_data)
                
                if response.status_code == 200:
                    new_user = response.json()
                    print("✅ Test user created successfully")
                    print(f"   📧 Email: {new_user['user'].get('email')}")
                    print(f"   👤 Full Name: {new_user['user'].get('full_name')}")
                    
                    # Update user to have proper balance and KYC level
                    user_id = new_user['user']['id']
                    update_data = {
                        "wallet_balance_tmn": 5000000,
                        "is_admin": False
                    }
                    
                    response = await client.put(f"{BACKEND_URL}/admin/users/{user_id}", 
                                              headers=headers, json=update_data)
                    
                    if response.status_code == 200:
                        print("✅ Test user updated with balance and admin status")
                    
                    # Set KYC level to 2 via KYC approval
                    kyc_approval = {
                        "user_id": user_id,
                        "kyc_level": 2,
                        "action": "approve",
                        "admin_note": "Test user setup"
                    }
                    
                    response = await client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                                               headers=headers, json=kyc_approval)
                    
                    if response.status_code == 200:
                        print("✅ Test user KYC approved to level 2")
                    else:
                        print(f"⚠️  KYC approval failed: {response.status_code}")
                    
                else:
                    print(f"❌ Test user creation failed: {response.status_code} - {response.text}")
            
            # Show some existing users for reference
            print(f"\n📋 Sample users:")
            for i, user in enumerate(users[:5]):
                print(f"   {i+1}. {user.get('email')} - {user.get('full_name')} - KYC:{user.get('kyc_level')} - Admin:{user.get('is_admin')}")
        
        else:
            print(f"❌ Failed to get users: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(check_and_create_test_user())