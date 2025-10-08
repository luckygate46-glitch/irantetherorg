#!/usr/bin/env python3
"""
Targeted Testing for Advanced Features - Check actual response structures
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://irancraft.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class TargetedTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up targeted testing...")
        await self.login_admin()
        
    async def login_admin(self):
        """Login as admin user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                print(f"✅ Admin login successful")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False

    async def test_endpoint_response_structure(self, endpoint, method="GET", payload=None):
        """Test an endpoint and show its actual response structure"""
        print(f"\n🔍 Testing {method} {endpoint}")
        print("-" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if method == "GET":
                response = await self.client.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            else:
                response = await self.client.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=payload)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Response Structure:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2, ensure_ascii=False))
                    return data
                except:
                    print("Response Text:", response.text[:500])
                    return response.text
            else:
                print("Error Response:", response.text)
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    async def run_targeted_tests(self):
        """Run targeted tests on specific endpoints"""
        print("🎯 Starting Targeted Advanced Features Testing...")
        print("=" * 80)
        
        await self.setup()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Test Advanced Trading Features
        print("\n🔥 ADVANCED TRADING FEATURES")
        print("=" * 50)
        
        # Test limit order
        limit_payload = {
            "order_type": "limit_buy",
            "coin_symbol": "BTC",
            "coin_id": "bitcoin",
            "amount_crypto": 0.001,
            "target_price_tmn": 2500000000,
            "expiry_date": "2024-12-31T23:59:59Z"
        }
        await self.test_endpoint_response_structure("/trading/limit-order", "POST", limit_payload)
        
        # Test stop loss
        stop_loss_payload = {
            "coin_symbol": "ETH",
            "coin_id": "ethereum",
            "amount_crypto": 0.1,
            "stop_price_tmn": 150000000,
            "limit_price_tmn": 145000000
        }
        await self.test_endpoint_response_structure("/trading/stop-loss", "POST", stop_loss_payload)
        
        # Test DCA strategy
        dca_payload = {
            "coin_symbol": "BTC",
            "coin_id": "bitcoin",
            "amount_tmn_per_purchase": 10000000,
            "frequency": "weekly",
            "total_budget_tmn": 100000000,
            "auto_rebalance": True
        }
        await self.test_endpoint_response_structure("/trading/dca-strategy", "POST", dca_payload)
        
        # Test Advanced AI Features
        print("\n🧠 ADVANCED AI FEATURES")
        print("=" * 50)
        
        await self.test_endpoint_response_structure("/ai/predictive-analysis/BTC")
        await self.test_endpoint_response_structure("/ai/sentiment-analysis/BTC")
        await self.test_endpoint_response_structure("/ai/portfolio-optimization")
        
        # Test Multi-Asset Trading
        print("\n📊 MULTI-ASSET TRADING")
        print("=" * 50)
        
        await self.test_endpoint_response_structure("/assets/stocks")
        await self.test_endpoint_response_structure("/assets/commodities")
        await self.test_endpoint_response_structure("/assets/forex")
        
        # Test Staking
        print("\n💰 STAKING & YIELD FARMING")
        print("=" * 50)
        
        pools_data = await self.test_endpoint_response_structure("/staking/pools")
        
        # Test staking creation with actual pool data
        if pools_data and isinstance(pools_data, list) and len(pools_data) > 0:
            first_pool = pools_data[0]
            pool_id = first_pool.get('id')
            min_stake = first_pool.get('minimum_stake', 1000000)
            
            stake_payload = {
                "pool_id": pool_id,
                "staked_amount": min_stake * 2,
                "auto_compound": True
            }
            await self.test_endpoint_response_structure("/staking/stake", "POST", stake_payload)
        else:
            print("⚠️  No staking pools available for testing stake creation")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = TargetedTester()
    await tester.run_targeted_tests()

if __name__ == "__main__":
    asyncio.run(main())