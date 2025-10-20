#!/usr/bin/env python3
"""
Backend Testing Script for Admin Orders with Wallet Addresses
Testing the updated admin orders endpoint functionality
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class BackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_results = []
        
    async def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def admin_login(self):
        """Login as admin user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                user_data = data["user"]
                
                await self.log_test(
                    "Admin Login",
                    True,
                    f"Logged in as {user_data.get('email')} (Admin: {user_data.get('is_admin')})"
                )
                return True
            else:
                await self.log_test(
                    "Admin Login",
                    False,
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            await self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_orders_endpoint(self):
        """Test GET /api/admin/orders endpoint"""
        if not self.admin_token:
            await self.log_test("Admin Orders Endpoint", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()
                
                await self.log_test(
                    "Admin Orders Endpoint Access",
                    True,
                    f"Retrieved {len(orders)} orders"
                )
                
                # Verify response structure
                if orders:
                    sample_order = orders[0]
                    required_fields = [
                        'id', 'user_id', 'user_email', 'user_name', 'user_phone',
                        'order_type', 'coin_symbol', 'wallet_address', 'user_wallet_addresses'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in sample_order:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        await self.log_test(
                            "Admin Orders Response Structure",
                            True,
                            f"All required fields present: {required_fields}"
                        )
                    else:
                        await self.log_test(
                            "Admin Orders Response Structure",
                            False,
                            f"Missing fields: {missing_fields}"
                        )
                    
                    # Check wallet address formatting
                    wallet_addresses_valid = True
                    wallet_details = []
                    
                    for order in orders[:5]:  # Check first 5 orders
                        wallet_addr = order.get('wallet_address')
                        user_wallets = order.get('user_wallet_addresses', {})
                        
                        if wallet_addr:
                            # Basic wallet address validation
                            if len(wallet_addr) < 10:
                                wallet_addresses_valid = False
                                wallet_details.append(f"Order {order['id']}: Invalid wallet address length")
                            else:
                                wallet_details.append(f"Order {order['id']}: {order['coin_symbol']} wallet {wallet_addr[:10]}...")
                        
                        # Check user_wallet_addresses structure
                        if user_wallets:
                            for symbol, wallet_info in user_wallets.items():
                                if not isinstance(wallet_info, dict) or 'address' not in wallet_info:
                                    wallet_addresses_valid = False
                                    wallet_details.append(f"Order {order['id']}: Invalid wallet structure for {symbol}")
                    
                    await self.log_test(
                        "Wallet Address Formatting",
                        wallet_addresses_valid,
                        "; ".join(wallet_details[:3])  # Show first 3 details
                    )
                    
                    # Check for BTC and USDT orders specifically
                    btc_orders = [o for o in orders if o.get('coin_symbol') == 'BTC']
                    usdt_orders = [o for o in orders if o.get('coin_symbol') == 'USDT']
                    
                    await self.log_test(
                        "BTC Orders Present",
                        len(btc_orders) > 0,
                        f"Found {len(btc_orders)} BTC orders"
                    )
                    
                    await self.log_test(
                        "USDT Orders Present",
                        len(usdt_orders) > 0,
                        f"Found {len(usdt_orders)} USDT orders"
                    )
                    
                    # Detailed analysis of first few orders
                    print("\n📊 DETAILED ORDER ANALYSIS:")
                    for i, order in enumerate(orders[:3]):
                        print(f"\nOrder {i+1}:")
                        print(f"  ID: {order.get('id')}")
                        print(f"  User: {order.get('user_name')} ({order.get('user_email')})")
                        print(f"  Phone: {order.get('user_phone')}")
                        print(f"  Type: {order.get('order_type')} {order.get('coin_symbol')}")
                        print(f"  Wallet Address: {order.get('wallet_address')}")
                        print(f"  User Wallets: {list(order.get('user_wallet_addresses', {}).keys())}")
                        print(f"  Status: {order.get('status')}")
                        print(f"  Amount: {order.get('amount_tmn', 0):,.0f} TMN")
                
                else:
                    await self.log_test(
                        "Admin Orders Data",
                        False,
                        "No orders found in database"
                    )
                
                return True
                
            else:
                await self.log_test(
                    "Admin Orders Endpoint Access",
                    False,
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            await self.log_test("Admin Orders Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_trading_orders_endpoint(self):
        """Test GET /api/admin/trading/orders endpoint"""
        if not self.admin_token:
            await self.log_test("Admin Trading Orders Endpoint", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/trading/orders", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()
                
                await self.log_test(
                    "Admin Trading Orders Endpoint Access",
                    True,
                    f"Retrieved {len(orders)} trading orders"
                )
                
                # Compare with /admin/orders to ensure they return same data
                orders_response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
                if orders_response.status_code == 200:
                    orders_alias = orders_response.json()
                    
                    await self.log_test(
                        "Endpoint Consistency",
                        len(orders) == len(orders_alias),
                        f"/admin/trading/orders: {len(orders)}, /admin/orders: {len(orders_alias)}"
                    )
                
                return True
                
            else:
                await self.log_test(
                    "Admin Trading Orders Endpoint Access",
                    False,
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            await self.log_test("Admin Trading Orders Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def verify_wallet_address_integration(self):
        """Verify wallet addresses are properly integrated with orders"""
        if not self.admin_token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get orders
            orders_response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            if orders_response.status_code != 200:
                await self.log_test("Wallet Integration Check", False, "Could not fetch orders")
                return False
            
            orders = orders_response.json()
            
            # Check if orders have proper wallet integration
            orders_with_wallets = 0
            orders_with_user_wallets = 0
            
            for order in orders:
                if order.get('wallet_address'):
                    orders_with_wallets += 1
                
                if order.get('user_wallet_addresses'):
                    orders_with_user_wallets += 1
            
            await self.log_test(
                "Orders with Wallet Addresses",
                orders_with_wallets > 0,
                f"{orders_with_wallets}/{len(orders)} orders have wallet addresses"
            )
            
            await self.log_test(
                "Orders with User Wallet Data",
                orders_with_user_wallets > 0,
                f"{orders_with_user_wallets}/{len(orders)} orders have user wallet data"
            )
            
            return True
            
        except Exception as e:
            await self.log_test("Wallet Integration Check", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING ADMIN ORDERS WITH WALLET ADDRESSES TESTING")
        print("=" * 60)
        
        # Login first
        login_success = await self.admin_login()
        if not login_success:
            print("❌ Cannot proceed without admin login")
            return
        
        # Run tests
        await self.test_admin_orders_endpoint()
        await self.test_admin_trading_orders_endpoint()
        await self.verify_wallet_address_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        await self.client.aclose()

async def main():
    """Main test function"""
    tester = BackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())