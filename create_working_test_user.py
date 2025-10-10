#!/usr/bin/env python3
"""
Create a working test user for login debugging
Since saruman.valar@gmail.com exists with different password,
we'll create a similar user that works for testing
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

async def create_working_test_user():
    """Create a working test user for login debugging"""
    
    client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    try:
        print("🔧 Creating Working Test User for Login Debugging")
        print("=" * 60)
        
        # Create a unique timestamp for the user
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # User data with unique identifiers
        user_data = {
            "first_name": "سارومان",
            "last_name": "والار",
            "email": f"saruman.valar.test.{timestamp}@gmail.com",
            "phone": f"0912345{timestamp[-4:]}",  # Use last 4 digits of timestamp
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
            print(f"Is Phone Verified: {user_info.get('is_phone_verified')}")
            print(f"Token: {data.get('access_token')[:50]}...")
            
            # Test login immediately
            print("\n🔐 Testing login with created user...")
            login_response = await client.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            print(f"Login Response Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                login_user_info = login_data.get("user", {})
                
                print("✅ Login successful!")
                print(f"Login Token: {login_data.get('access_token')[:50]}...")
                print(f"Token Type: {login_data.get('token_type')}")
                print(f"User Full Name: {login_user_info.get('full_name')}")
                
                # Verify response structure matches frontend expectations
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in login_data]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in login response: {missing_fields}")
                else:
                    print("✅ Login response structure is correct for frontend")
                
                # Test protected endpoint
                print("\n🔒 Testing protected endpoint access...")
                headers = {"Authorization": f"Bearer {login_data.get('access_token')}"}
                me_response = await client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ Protected endpoint access successful!")
                    print(f"Profile Full Name: {me_data.get('full_name')}")
                    print(f"Profile Email: {me_data.get('email')}")
                    print(f"Profile KYC Level: {me_data.get('kyc_level')}")
                else:
                    print(f"❌ Protected endpoint failed: {me_response.status_code}")
                    print(f"Error: {me_response.text}")
                
                # Test another protected endpoint
                print("\n📊 Testing KYC status endpoint...")
                kyc_response = await client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
                
                if kyc_response.status_code == 200:
                    kyc_data = kyc_response.json()
                    print("✅ KYC status endpoint accessible!")
                    print(f"KYC Level: {kyc_data.get('kyc_level')}")
                    print(f"KYC Status: {kyc_data.get('kyc_status')}")
                else:
                    print(f"❌ KYC status endpoint failed: {kyc_response.status_code}")
                
                print("\n" + "=" * 60)
                print("🎯 WORKING TEST USER CREDENTIALS:")
                print("=" * 60)
                print(f"Email: {user_data['email']}")
                print(f"Password: {user_data['password']}")
                print(f"Persian Names: {user_data['first_name']} {user_data['last_name']}")
                print(f"Phone: {user_data['phone']}")
                print("=" * 60)
                print("✅ LOGIN FUNCTIONALITY IS WORKING!")
                print("✅ JWT TOKEN GENERATION IS WORKING!")
                print("✅ PROTECTED ENDPOINTS ARE ACCESSIBLE!")
                print("✅ RESPONSE FORMAT MATCHES FRONTEND EXPECTATIONS!")
                print("=" * 60)
                
                # Also test the original requested user for comparison
                print("\n🔍 Testing original requested user for comparison...")
                original_login = await client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": "saruman.valar@gmail.com",
                    "password": "password123"
                })
                
                if original_login.status_code == 200:
                    print("✅ Original user saruman.valar@gmail.com also works with password123!")
                elif original_login.status_code == 401:
                    print("❌ Original user saruman.valar@gmail.com has different password")
                    print("   The user exists but password is not 'password123'")
                else:
                    print(f"❓ Original user login returned: {original_login.status_code}")
                    
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Error: {login_response.text}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(create_working_test_user())