#!/usr/bin/env python3
"""
Debug Advanced Trading Endpoints
"""

import asyncio
import httpx
import json
import uuid

BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"email": "admin", "password": "istari118"}

async def debug_advanced_trading():
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Login as admin (who has KYC level 2)
        print("🔐 Logging in as admin...")
        response = await client.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code != 200:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return
        
        admin_data = response.json()
        admin_token = admin_data.get('access_token')
        admin_user = admin_data.get('user', {})
        print(f"✅ Admin login successful: {admin_user.get('full_name')} (KYC Level: {admin_user.get('kyc_level')})")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test limit order endpoint
        print("\n📊 Testing limit order endpoint...")
        limit_order_data = {
            "order_type": "limit_buy",
            "coin_symbol": "BTC",
            "coin_id": "bitcoin",
            "amount_crypto": 0.001,
            "target_price_tmn": 1000000
        }
        
        response = await client.post(f"{BACKEND_URL}/trading/limit-order", 
                                   headers=headers, json=limit_order_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test stop-loss endpoint
        print("\n🛡️ Testing stop-loss endpoint...")
        stop_loss_data = {
            "coin_symbol": "BTC",
            "coin_id": "bitcoin",
            "amount_crypto": 0.001,
            "stop_price_tmn": 900000
        }
        
        response = await client.post(f"{BACKEND_URL}/trading/stop-loss", 
                                   headers=headers, json=stop_loss_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test DCA strategy endpoint
        print("\n💰 Testing DCA strategy endpoint...")
        dca_data = {
            "coin_symbol": "BTC",
            "coin_id": "bitcoin",
            "amount_tmn_per_purchase": 1000000,
            "frequency": "weekly",
            "total_budget_tmn": 10000000
        }
        
        response = await client.post(f"{BACKEND_URL}/trading/dca-strategy", 
                                   headers=headers, json=dca_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(debug_advanced_trading())