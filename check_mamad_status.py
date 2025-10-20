#!/usr/bin/env python3
"""
Check mamad.naboodi@gmail.com current status after admin approval
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

async def check_mamad_status():
    """Check mamad.naboodi@gmail.com current status"""
    client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    try:
        # Login as admin
        admin_response = await client.post(f"{BACKEND_URL}/auth/login", json={
            "email": "admin",
            "password": "istari118"
        })
        
        if admin_response.status_code != 200:
            print("❌ Failed to login as admin")
            return
        
        admin_token = admin_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get all users
        users_response = await client.get(f"{BACKEND_URL}/admin/users", headers=headers)
        
        if users_response.status_code != 200:
            print("❌ Failed to get users")
            return
        
        users = users_response.json()
        mamad_user = None
        
        for user in users:
            if user.get("email") == "mamad.naboodi@gmail.com":
                mamad_user = user
                break
        
        if mamad_user:
            print("✅ Found mamad.naboodi@gmail.com in database:")
            print(f"   - User ID: {mamad_user.get('id')}")
            print(f"   - Email: {mamad_user.get('email')}")
            print(f"   - Full Name: {mamad_user.get('full_name')}")
            print(f"   - Phone: {mamad_user.get('phone')}")
            print(f"   - KYC Level: {mamad_user.get('kyc_level')}")
            print(f"   - KYC Status: {mamad_user.get('kyc_status')}")
            print(f"   - Is Active: {mamad_user.get('is_active')}")
            print(f"   - Is Phone Verified: {mamad_user.get('is_phone_verified')}")
            print(f"   - Wallet Balance: {mamad_user.get('wallet_balance_tmn')} TMN")
            print(f"   - Created At: {mamad_user.get('created_at')}")
            
            # Check if user has KYC documents
            if mamad_user.get('kyc_level') >= 1:
                print(f"   - National Code: {mamad_user.get('national_code', 'Not set')}")
                print(f"   - Bank Card: {mamad_user.get('bank_card_number', 'Not set')}")
            
            print("\n🔍 ANALYSIS:")
            if mamad_user.get('kyc_level') == 2 and mamad_user.get('kyc_status') == 'approved':
                print("✅ KYC Status is CORRECT: Level 2, Approved")
                print("   The admin approval was successful!")
                print("   If user dashboard shows incomplete KYC, the issue is likely:")
                print("   1. Frontend caching - user needs to refresh browser")
                print("   2. User needs to logout and login again")
                print("   3. Frontend is checking wrong endpoint or field")
            else:
                print(f"❌ KYC Status is INCORRECT: Level {mamad_user.get('kyc_level')}, Status {mamad_user.get('kyc_status')}")
                print("   The admin approval did not work properly")
        else:
            print("❌ User mamad.naboodi@gmail.com not found in database")
            print("   User may need to register first")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(check_mamad_status())