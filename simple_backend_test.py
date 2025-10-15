#!/usr/bin/env python3
"""
Simple Backend Test for Trading System APIs
"""

import asyncio
import httpx
import json

BACKEND_URL = "https://crypto-farsi.preview.emergentagent.com/api"

async def test_basic_endpoints():
    """Test basic endpoints without authentication"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🚀 Testing Basic Backend Endpoints")
        print("=" * 50)
        
        # Test 1: Root endpoint
        try:
            response = await client.get("https://crypto-farsi.preview.emergentagent.com/")
            print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
        
        # Test 2: Crypto prices
        try:
            response = await client.get(f"{BACKEND_URL}/crypto/prices")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Crypto prices: Retrieved {len(data.get('data', {}))} coins")
            else:
                print(f"❌ Crypto prices failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Crypto prices failed: {e}")
        
        # Test 3: Get active cards (public endpoint)
        try:
            response = await client.get(f"{BACKEND_URL}/cards")
            print(f"✅ Active cards: {response.status_code} - {len(response.json()) if response.status_code == 200 else response.text}")
        except Exception as e:
            print(f"❌ Active cards failed: {e}")
        
        # Test 4: Try to access protected endpoint without auth
        try:
            response = await client.get(f"{BACKEND_URL}/auth/me")
            if response.status_code == 401:
                print("✅ Auth protection working: Correctly rejected unauthenticated request")
            else:
                print(f"❌ Auth protection failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Auth test failed: {e}")
        
        # Test 5: Try to create trading order without auth
        try:
            response = await client.post(f"{BACKEND_URL}/trading/order", json={
                "order_type": "buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn": 100000.0
            })
            if response.status_code == 401 or response.status_code == 403:
                print("✅ Trading protection working: Correctly rejected unauthenticated request")
            else:
                print(f"❌ Trading protection failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Trading auth test failed: {e}")
        
        # Test 6: Try login with invalid credentials
        try:
            response = await client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            })
            if response.status_code == 401:
                print("✅ Login validation working: Correctly rejected invalid credentials")
            else:
                print(f"❌ Login validation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Login test failed: {e}")
        
        print("\n🏁 Basic endpoint testing complete!")

async def test_with_mock_user():
    """Test with a mock user if possible"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n🔐 Testing with Mock Authentication")
        print("=" * 50)
        
        # Try to register a user (will likely fail due to OTP requirement)
        try:
            response = await client.post(f"{BACKEND_URL}/auth/register", json={
                "email": "testuser123@example.com",
                "password": "testpass123",
                "phone": "09123456789"
            })
            
            if response.status_code == 400:
                error_msg = response.json().get("detail", "")
                if "تایید" in error_msg or "OTP" in error_msg:
                    print("✅ Registration validation working: Requires phone verification")
                else:
                    print(f"✅ Registration validation working: {error_msg}")
            else:
                print(f"❌ Registration unexpected response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Registration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_endpoints())
    asyncio.run(test_with_mock_user())