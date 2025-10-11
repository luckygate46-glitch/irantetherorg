#!/usr/bin/env python3
"""
Test Staking Endpoints - Fixed
"""

import asyncio
import httpx
import json

BACKEND_URL = "https://cryptotoman.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"email": "admin", "password": "istari118"}

async def test_staking_fixed():
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Login as admin
        print("🔐 Logging in as admin...")
        response = await client.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Admin login failed: {response.status_code}")
            return
        
        admin_data = response.json()
        admin_token = admin_data.get('access_token')
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test stake creation with correct field name
        print("\n💰 Testing stake creation (fixed)...")
        stake_data = {
            "pool_id": "eth2-staking",
            "staked_amount": 1000000,  # Fixed field name
            "auto_compound": True
        }
        
        response = await client.post(f"{BACKEND_URL}/staking/stake", 
                                   headers=headers, json=stake_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_staking_fixed())