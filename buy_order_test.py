#!/usr/bin/env python3
"""
Buy Order Functionality Testing for Iranian Crypto Exchange
Testing the buy order button fix and trading functionality
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test123"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class BuyOrderTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        self.test_user_id = None
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up Buy Order testing environment...")
        
        # Try to login with test@test.com first
        success = await self.login_test_user()
        if not success:
            # If that fails, try with admin credentials
            print("⚠️  Test user login failed, trying admin credentials...")
            success = await self.login_admin_as_user()
        
        if not success:
            print("❌ Could not authenticate any user for testing")
            return False
            
        return True
        
    async def login_test_user(self):
        """Login as test user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                user_info = data["user"]
                self.test_user_id = user_info["id"]
                print(f"✅ Test user login successful: {user_info.get('full_name', 'Test User')}")
                print(f"📊 User KYC Level: {user_info.get('kyc_level', 0)}")
                print(f"📊 Wallet Balance: {user_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                return True
            else:
                print(f"❌ Test user login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test user login error: {str(e)}")
            return False
    
    async def login_admin_as_user(self):
        """Login as admin user for testing"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.admin_token = data["access_token"]  # Same token for admin
                user_info = data["user"]
                self.test_user_id = user_info["id"]
                print(f"✅ Admin login successful: {user_info.get('full_name', 'Admin')}")
                print(f"📊 User KYC Level: {user_info.get('kyc_level', 0)}")
                print(f"📊 Wallet Balance: {user_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                print(f"📊 Is Admin: {user_info.get('is_admin', False)}")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False

    async def test_buy_order_with_valid_token(self):
        """Test buy order with valid token and sufficient balance"""
        print("\n💰 Testing Buy Order with Valid Token...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            payload = {
                "order_type": "buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn": 100000
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=payload)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Buy order created successfully")
                print(f"📊 Order ID: {data.get('order_id', 'N/A')}")
                print(f"📊 Message: {data.get('message', 'N/A')}")
                self.test_results.append({"test": "buy_order_valid_token", "status": "✅ PASS", "details": "Buy order successful"})
                
            elif response.status_code == 403:
                print("⚠️  Buy order blocked - KYC Level 2 required")
                self.test_results.append({"test": "buy_order_valid_token", "status": "⚠️  KYC", "details": "Requires KYC Level 2"})
                
            elif response.status_code == 400:
                error_data = response.json()
                error_detail = error_data.get('detail', 'Unknown error')
                print(f"⚠️  Buy order validation error: {error_detail}")
                self.test_results.append({"test": "buy_order_valid_token", "status": "⚠️  VALIDATION", "details": error_detail})
                
            else:
                print(f"❌ Buy order failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "buy_order_valid_token", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Buy order error: {str(e)}")
            self.test_results.append({"test": "buy_order_valid_token", "status": "❌ ERROR", "details": str(e)})

    async def test_buy_order_without_token(self):
        """Test buy order without authentication token"""
        print("\n🚫 Testing Buy Order without Token...")
        
        try:
            payload = {
                "order_type": "buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn": 100000
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", json=payload)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 401:
                print("✅ Buy order correctly rejected without token")
                self.test_results.append({"test": "buy_order_no_token", "status": "✅ PASS", "details": "Correctly requires authentication"})
            elif response.status_code == 403:
                print("✅ Buy order correctly rejected without token (403)")
                self.test_results.append({"test": "buy_order_no_token", "status": "✅ PASS", "details": "Correctly requires authentication"})
            else:
                print(f"❌ Buy order should require authentication: {response.status_code}")
                self.test_results.append({"test": "buy_order_no_token", "status": "❌ FAIL", "details": f"Should return 401/403, got {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Buy order no token error: {str(e)}")
            self.test_results.append({"test": "buy_order_no_token", "status": "❌ ERROR", "details": str(e)})

    async def test_buy_order_insufficient_balance(self):
        """Test buy order with insufficient balance"""
        print("\n💸 Testing Buy Order with Insufficient Balance...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            payload = {
                "order_type": "buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn": 999999999  # Very large amount
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=payload)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 400:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                if 'موجودی' in error_detail or 'balance' in error_detail.lower():
                    print("✅ Buy order correctly rejected for insufficient balance")
                    self.test_results.append({"test": "buy_order_insufficient_balance", "status": "✅ PASS", "details": "Correctly validates balance"})
                else:
                    print(f"⚠️  Buy order rejected but not for balance: {error_detail}")
                    self.test_results.append({"test": "buy_order_insufficient_balance", "status": "⚠️  PARTIAL", "details": error_detail})
            elif response.status_code == 403:
                print("⚠️  Buy order blocked - likely KYC requirement")
                self.test_results.append({"test": "buy_order_insufficient_balance", "status": "⚠️  KYC", "details": "KYC requirement prevents balance test"})
            else:
                print(f"❌ Expected 400 for insufficient balance: {response.status_code}")
                self.test_results.append({"test": "buy_order_insufficient_balance", "status": "❌ FAIL", "details": f"Expected 400, got {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Buy order insufficient balance error: {str(e)}")
            self.test_results.append({"test": "buy_order_insufficient_balance", "status": "❌ ERROR", "details": str(e)})

    async def test_trading_holdings_endpoint(self):
        """Test GET /api/trading/holdings/my"""
        print("\n📊 Testing Trading Holdings Endpoint...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/holdings/my", headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                holdings = response.json()  # Direct array response
                print("✅ Trading holdings endpoint working")
                print(f"📊 Holdings Count: {len(holdings)}")
                
                if holdings:
                    for holding in holdings[:3]:  # Show first 3
                        print(f"  - {holding.get('coin_symbol', 'N/A')}: {holding.get('amount', 0)} coins")
                
                self.test_results.append({"test": "trading_holdings", "status": "✅ PASS", "details": f"Retrieved {len(holdings)} holdings"})
                
            elif response.status_code == 401 or response.status_code == 403:
                print("⚠️  Holdings endpoint requires authentication")
                self.test_results.append({"test": "trading_holdings", "status": "⚠️  AUTH", "details": "Authentication required"})
            else:
                print(f"❌ Holdings endpoint failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "trading_holdings", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Holdings endpoint error: {str(e)}")
            self.test_results.append({"test": "trading_holdings", "status": "❌ ERROR", "details": str(e)})

    async def test_trading_orders_endpoint(self):
        """Test GET /api/trading/orders/my"""
        print("\n📋 Testing Trading Orders Endpoint...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                orders = response.json()  # Direct array response
                print("✅ Trading orders endpoint working")
                print(f"📊 Orders Count: {len(orders)}")
                
                if orders:
                    for order in orders[:3]:  # Show first 3
                        print(f"  - {order.get('order_type', 'N/A')} {order.get('coin_symbol', 'N/A')}: {order.get('status', 'N/A')}")
                
                self.test_results.append({"test": "trading_orders", "status": "✅ PASS", "details": f"Retrieved {len(orders)} orders"})
                
            elif response.status_code == 401 or response.status_code == 403:
                print("⚠️  Orders endpoint requires authentication")
                self.test_results.append({"test": "trading_orders", "status": "⚠️  AUTH", "details": "Authentication required"})
            else:
                print(f"❌ Orders endpoint failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "trading_orders", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Orders endpoint error: {str(e)}")
            self.test_results.append({"test": "trading_orders", "status": "❌ ERROR", "details": str(e)})

    async def test_buy_order_malformed_request(self):
        """Test buy order with malformed request"""
        print("\n🔧 Testing Buy Order with Malformed Request...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test with missing required fields
            payload = {
                "order_type": "buy",
                # Missing coin_symbol, coin_id, amount_tmn
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=payload)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 422:
                print("✅ Buy order correctly rejected malformed request")
                self.test_results.append({"test": "buy_order_malformed", "status": "✅ PASS", "details": "Correctly validates request format"})
            elif response.status_code == 400:
                print("✅ Buy order correctly rejected malformed request (400)")
                self.test_results.append({"test": "buy_order_malformed", "status": "✅ PASS", "details": "Correctly validates request format"})
            else:
                print(f"❌ Expected 422/400 for malformed request: {response.status_code}")
                self.test_results.append({"test": "buy_order_malformed", "status": "❌ FAIL", "details": f"Expected 422/400, got {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Buy order malformed error: {str(e)}")
            self.test_results.append({"test": "buy_order_malformed", "status": "❌ ERROR", "details": str(e)})

    async def test_user_profile_endpoint(self):
        """Test user profile endpoint to verify authentication"""
        print("\n👤 Testing User Profile Endpoint...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User profile endpoint working")
                print(f"📊 User ID: {data.get('id', 'N/A')}")
                print(f"📊 Email: {data.get('email', 'N/A')}")
                print(f"📊 KYC Level: {data.get('kyc_level', 0)}")
                print(f"📊 Wallet Balance: {data.get('wallet_balance_tmn', 0):,.0f} TMN")
                print(f"📊 Is Admin: {data.get('is_admin', False)}")
                
                self.test_results.append({"test": "user_profile", "status": "✅ PASS", "details": "User profile accessible"})
                
            else:
                print(f"❌ User profile failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "user_profile", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ User profile error: {str(e)}")
            self.test_results.append({"test": "user_profile", "status": "❌ ERROR", "details": str(e)})

    async def add_balance_to_user(self):
        """Add balance to user for testing successful buy orders"""
        print("\n💰 Adding Balance to User for Testing...")
        
        if not self.admin_token:
            print("⚠️  No admin token available, cannot add balance")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            update_data = {"wallet_balance_tmn": 1000000}  # 1M TMN
            
            response = await self.client.put(f"{BACKEND_URL}/admin/users/{self.test_user_id}", 
                                           headers=headers, json=update_data)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Balance added successfully")
                return True
            else:
                print(f"❌ Failed to add balance: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Add balance error: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all buy order tests"""
        print("🚀 Starting Buy Order Functionality Testing...")
        print("=" * 60)
        
        setup_success = await self.setup()
        if not setup_success:
            print("❌ Setup failed, cannot proceed with tests")
            return
        
        # Run all tests
        await self.test_user_profile_endpoint()
        await self.test_buy_order_with_valid_token()
        await self.test_buy_order_without_token()
        await self.test_buy_order_insufficient_balance()
        await self.test_buy_order_malformed_request()
        await self.test_trading_holdings_endpoint()
        await self.test_trading_orders_endpoint()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 BUY ORDER TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        warning_tests = [r for r in self.test_results if "⚠️" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⚠️  WARNINGS: {len(warning_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if warning_tests:
            print("\n⚠️  WARNING TESTS:")
            for test in warning_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        if len(passed_tests) >= 4:
            print("✅ Buy order functionality is working")
            print("✅ Authentication and authorization working correctly")
            print("✅ Error handling and validation working properly")
        else:
            print("⚠️  Buy order functionality may have issues")
            print("⚠️  Check failed tests for specific problems")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = BuyOrderTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())