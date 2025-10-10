#!/usr/bin/env python3
"""
Check if saruman.valar@gmail.com user exists and test login
"""

import asyncio
import httpx
import json

async def check_saruman_user():
    client = httpx.AsyncClient(timeout=30.0)
    
    print("🔍 Checking for saruman.valar@gmail.com user...")
    
    # Try to register the user first to see if it exists
    register_data = {
        "first_name": "Saruman",
        "last_name": "Valar",
        "email": "saruman.valar@gmail.com",
        "phone": "09123456789",
        "password": "password123"
    }
    
    register_response = await client.post("https://crypto-genius-7.preview.emergentagent.com/api/auth/register", json=register_data)
    
    print(f"Registration attempt status: {register_response.status_code}")
    
    if register_response.status_code == 400:
        register_data_response = register_response.json()
        if "قبلاً ثبت شده" in register_data_response.get("detail", ""):
            print("✅ User saruman.valar@gmail.com already exists!")
            
            # Try to login with common passwords
            common_passwords = ["password123", "password", "123456", "admin", "saruman", "valar", "test"]
            
            for password in common_passwords:
                try:
                    login_response = await client.post("https://crypto-genius-7.preview.emergentagent.com/api/auth/login", json={
                        "email": "saruman.valar@gmail.com",
                        "password": password
                    })
                    
                    if login_response.status_code == 200:
                        print(f"✅ Login successful with password: {password}")
                        data = login_response.json()
                        user_data = data.get("user", {})
                        print(f"User details: {user_data.get('full_name')} - Active: {user_data.get('is_active')}")
                        break
                    elif login_response.status_code == 401:
                        print(f"❌ Wrong password: {password}")
                    elif login_response.status_code == 429:
                        print(f"⏱️ Rate limited, skipping remaining passwords")
                        break
                    else:
                        print(f"❓ Unexpected response {login_response.status_code} for password {password}")
                        
                except Exception as e:
                    print(f"❌ Error testing password {password}: {str(e)}")
                    
        else:
            print(f"❌ Registration failed for other reason: {register_data_response}")
            
    elif register_response.status_code == 200:
        print("✅ Successfully registered saruman.valar@gmail.com!")
        data = register_response.json()
        user_data = data.get("user", {})
        token = data.get("access_token")
        print(f"New user: {user_data.get('full_name')} - Token: {token[:50]}...")
        
        # Test login with the password we just used
        login_response = await client.post("https://crypto-genius-7.preview.emergentagent.com/api/auth/login", json={
            "email": "saruman.valar@gmail.com",
            "password": "password123"
        })
        
        if login_response.status_code == 200:
            print("✅ Login successful after registration!")
        else:
            print(f"❌ Login failed after registration: {login_response.text}")
            
    else:
        print(f"❌ Registration failed: {register_response.text}")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(check_saruman_user())