#!/usr/bin/env python3
"""
Final Registration Test - Test with completely new user data
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

async def test_complete_new_user_flow():
    """Test complete flow with a brand new user"""
    client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    try:
        # Generate unique user data
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "first_name": "احمد",
            "last_name": "محمدی",
            "email": f"ahmad.test.{unique_id}@example.com",
            "phone": f"0912345{unique_id[:4]}",  # Unique phone
            "password": "testpass123"
        }
        
        print("🎯 TESTING COMPLETE NEW USER FLOW")
        print("=" * 50)
        print(f"Test User: {json.dumps(test_user, ensure_ascii=False)}")
        
        # Step 1: Registration
        print(f"\n📝 Step 1: Registration")
        register_response = await client.post(f"{BACKEND_URL}/auth/register", json=test_user)
        
        print(f"Registration Status: {register_response.status_code}")
        print(f"Registration Response: {register_response.text}")
        
        if register_response.status_code in [200, 201]:
            user_data = register_response.json()
            user_info = user_data.get("user", {})
            access_token = user_data.get("access_token")
            
            print("✅ Registration successful!")
            print(f"   - User ID: {user_info.get('id')}")
            print(f"   - Full Name: {user_info.get('full_name')}")
            print(f"   - Phone Verified: {user_info.get('is_phone_verified')}")
            print(f"   - JWT Token: {'✅ Generated' if access_token else '❌ Missing'}")
            
            # Step 2: Login
            print(f"\n🔐 Step 2: Login Test")
            login_response = await client.post(f"{BACKEND_URL}/auth/login", json={
                "email": test_user["email"],
                "password": test_user["password"]
            })
            
            print(f"Login Status: {login_response.status_code}")
            print(f"Login Response: {login_response.text}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                login_token = login_data.get("access_token")
                
                print("✅ Login successful!")
                
                # Step 3: Dashboard Access
                print(f"\n📊 Step 3: Dashboard Access Test")
                headers = {"Authorization": f"Bearer {login_token}"}
                me_response = await client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                print(f"Dashboard Access Status: {me_response.status_code}")
                print(f"Dashboard Response: {me_response.text}")
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ Dashboard access successful!")
                    print(f"   - User Profile: {me_data.get('full_name')}")
                    print(f"   - KYC Level: {me_data.get('kyc_level')}")
                    print(f"   - Phone Verified: {me_data.get('is_phone_verified')}")
                    
                    # Final verification
                    print(f"\n🎉 FINAL VERIFICATION")
                    print("=" * 50)
                    
                    success_criteria = [
                        ("Registration without OTP", register_response.status_code in [200, 201]),
                        ("User created with is_phone_verified=False", user_info.get('is_phone_verified') == False),
                        ("JWT token generated", bool(access_token)),
                        ("All user fields saved correctly", all(user_info.get(field) for field in ['first_name', 'last_name', 'email', 'phone'])),
                        ("Login after registration", login_response.status_code == 200),
                        ("Dashboard access", me_response.status_code == 200)
                    ]
                    
                    all_passed = True
                    for criteria, passed in success_criteria:
                        status = "✅ PASS" if passed else "❌ FAIL"
                        print(f"{status} {criteria}")
                        if not passed:
                            all_passed = False
                    
                    print(f"\n{'🎉 ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")
                    print(f"SIMPLIFIED REGISTRATION SYSTEM: {'✅ WORKING' if all_passed else '❌ HAS ISSUES'}")
                    
                else:
                    print("❌ Dashboard access failed!")
            else:
                print("❌ Login failed!")
        else:
            print("❌ Registration failed!")
            print(f"Error: {register_response.text}")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_complete_new_user_flow())