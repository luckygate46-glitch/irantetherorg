#!/usr/bin/env python3
"""
Test staking creation specifically
"""

import asyncio
import httpx
import json

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

async def test_staking():
    client = httpx.AsyncClient(timeout=30.0)
    
    # Login
    response = await client.post(f"{BACKEND_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get pools
    pools_response = await client.get(f"{BACKEND_URL}/staking/pools", headers=headers)
    print("Pools response:", pools_response.status_code)
    
    if pools_response.status_code == 200:
        pools_data = pools_response.json()
        print("Pools data structure:")
        print(json.dumps(pools_data, indent=2, ensure_ascii=False))
        
        # Extract pools from the response
        if 'staking_pools' in pools_data:
            pools = pools_data['staking_pools']
            if pools and len(pools) > 0:
                first_pool = pools[0]
                pool_id = first_pool.get('id')
                min_stake = first_pool.get('minimum_stake', 1)
                
                print(f"\nTesting stake creation with pool_id: {pool_id}, min_stake: {min_stake}")
                
                stake_payload = {
                    "pool_id": pool_id,
                    "staked_amount": min_stake * 2,
                    "auto_compound": True
                }
                
                stake_response = await client.post(f"{BACKEND_URL}/staking/stake", headers=headers, json=stake_payload)
                print(f"Stake creation response: {stake_response.status_code}")
                
                if stake_response.status_code == 200:
                    stake_data = stake_response.json()
                    print("Stake creation successful:")
                    print(json.dumps(stake_data, indent=2, ensure_ascii=False))
                else:
                    print("Stake creation failed:", stake_response.text)
            else:
                print("No pools found in response")
        else:
            print("No 'staking_pools' key in response")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_staking())