#!/usr/bin/env python3
"""
Test Staking Endpoints
"""

import asyncio
import httpx
import json

BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"email": "admin", "password": "istari118"}

async def test_staking():
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
        
        # Test staking pools
        print("\n🌾 Testing staking pools...")
        response = await client.get(f"{BACKEND_URL}/staking/pools", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('pools', []))} staking pools")
            print(f"Response preview: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"Response: {response.text}")
        
        # Test stake creation
        print("\n💰 Testing stake creation...")
        stake_data = {
            "pool_id": "eth2-staking",
            "amount": 1000000,
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
    asyncio.run(test_staking())