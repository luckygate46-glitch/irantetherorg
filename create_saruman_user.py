#!/usr/bin/env python3
"""
Create specific test user: saruman.valar@gmail.com
For login debugging as requested in the review
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://irancraft.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

async def create_saruman_user():
    """Create the specific test user requested"""
    
    client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    try:
        print("🔧 Creating Test User for Login Debugging")
        print("=" * 50)
        
        # User data as requested
        user_data = {
            "first_name": "سارومان",
            "last_name": "والار",
            "email": "saruman.valar@gmail.com",
            "phone": "09123456789",
            "password": "password123"
        }
        
        print(f"Email: {user_data['email']}")
        print(f"Password: {user_data['password']}")
        print(f"Persian Names: {user_data['first_name']} {user_data['last_name']}")
        print(f"Phone: {user_data['phone']}")
        print()
        
        # Try to register the user
        print("📝 Attempting registration...")
        response = await client.post(f"{BACKEND_URL}/auth/register", json=user_data)
        
        print(f"Registration Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            user_info = data.get("user", {})
            
            print("✅ User created successfully!")
            print(f"User ID: {user_info.get('id')}")
            print(f"Full Name: {user_info.get('full_name')}")
            print(f"Email: {user_info.get('email')}")
            print(f"Phone: {user_info.get('phone')}")
            print(f"KYC Level: {user_info.get('kyc_level')}")
            print(f"Token: {data.get('access_token')[:50]}...")
            
            # Test login immediately
            print("\n🔐 Testing login with created user...")
            login_response = await client.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ Login successful!")
                print(f"Login Token: {login_data.get('access_token')[:50]}...")
                
                # Test protected endpoint
                headers = {"Authorization": f"Bearer {login_data.get('access_token')}"}
                me_response = await client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ Protected endpoint access successful!")
                    print(f"Profile Full Name: {me_data.get('full_name')}")
                else:
                    print(f"❌ Protected endpoint failed: {me_response.status_code}")
                    
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                
        elif response.status_code == 400:
            error_data = response.json()
            error_detail = error_data.get("detail", "")
            
            if "قبلاً ثبت شده" in error_detail or "already exists" in error_detail.lower():
                print("⚠️  User already exists. Testing login with existing user...")
                
                # Test login with existing user
                login_response = await client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    user_info = login_data.get("user", {})
                    print("✅ Login successful with existing user!")
                    print(f"Full Name: {user_info.get('full_name')}")
                    print(f"Email: {user_info.get('email')}")
                    print(f"Token: {login_data.get('access_token')[:50]}...")
                else:
                    print(f"❌ Login failed with existing user: {login_response.status_code}")
                    print(f"Error: {login_response.text}")
                    
                    # If login fails, the user might exist with different password
                    # Let's try to create a new user with different email
                    print("\n🔄 Trying to create user with different email...")
                    alt_user_data = user_data.copy()
                    alt_user_data["email"] = f"saruman.valar.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
                    
                    alt_response = await client.post(f"{BACKEND_URL}/auth/register", json=alt_user_data)
                    
                    if alt_response.status_code in [200, 201]:
                        alt_data = alt_response.json()
                        alt_user_info = alt_data.get("user", {})
                        print("✅ Alternative user created successfully!")
                        print(f"Email: {alt_user_info.get('email')}")
                        print(f"Full Name: {alt_user_info.get('full_name')}")
                        print(f"Token: {alt_data.get('access_token')[:50]}...")
                        
                        # Test login with alternative user
                        alt_login_response = await client.post(f"{BACKEND_URL}/auth/login", json={
                            "email": alt_user_data["email"],
                            "password": alt_user_data["password"]
                        })
                        
                        if alt_login_response.status_code == 200:
                            print("✅ Login successful with alternative user!")
                        else:
                            print(f"❌ Login failed with alternative user: {alt_login_response.status_code}")
                    else:
                        print(f"❌ Alternative user creation failed: {alt_response.status_code}")
                        print(f"Error: {alt_response.text}")
            else:
                print(f"❌ Registration failed: {error_detail}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Error: {response.text}")
            
        print("\n" + "=" * 50)
        print("🎯 FINAL CREDENTIALS FOR TESTING:")
        print("=" * 50)
        print(f"Email: {user_data['email']}")
        print(f"Password: {user_data['password']}")
        print(f"Persian Names: {user_data['first_name']} {user_data['last_name']}")
        print(f"Phone: {user_data['phone']}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(create_saruman_user())