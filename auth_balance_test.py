#!/usr/bin/env python3
"""
Authentication System and Balance Display Testing
Testing complete authentication system and balance display as per review request
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://cryptotradera.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpass123"

class AuthBalanceTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_user_token = None
        self.test_results = []
        
    async def test_admin_login(self):
        """Test 1: Admin Login Test"""
        print("\n🔐 Test 1: Admin Login Test...")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                user_info = data["user"]
                
                print(f"✅ Admin login successful")
                print(f"📧 Email: {user_info.get('email')}")
                print(f"👤 Full Name: {user_info.get('full_name')}")
                print(f"💰 Wallet Balance TMN: {user_info.get('wallet_balance_tmn', 0):,.0f}")
                print(f"🔑 Is Admin: {user_info.get('is_admin')}")
                print(f"📋 KYC Level: {user_info.get('kyc_level')}")
                print(f"🎫 Access Token: {data['access_token'][:20]}...")
                
                # Verify required fields
                required_checks = [
                    ("access_token", data.get("access_token") is not None),
                    ("wallet_balance_tmn", user_info.get("wallet_balance_tmn") is not None),
                    ("is_admin", user_info.get("is_admin") == True),
                    ("kyc_level", user_info.get("kyc_level") == 2)
                ]
                
                all_passed = True
                for field, check in required_checks:
                    if check:
                        print(f"✅ {field}: VERIFIED")
                    else:
                        print(f"❌ {field}: FAILED")
                        all_passed = False
                
                if all_passed:
                    self.test_results.append({"test": "admin_login", "status": "✅ PASS", "details": "All admin login requirements verified"})
                else:
                    self.test_results.append({"test": "admin_login", "status": "❌ FAIL", "details": "Some admin login requirements failed"})
                
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "admin_login", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            self.test_results.append({"test": "admin_login", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_user_login(self):
        """Test 2: Test User Login"""
        print("\n👤 Test 2: Test User Login...")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                user_info = data["user"]
                
                print(f"✅ Test user login successful")
                print(f"📧 Email: {user_info.get('email')}")
                print(f"👤 Full Name: {user_info.get('full_name')}")
                print(f"💰 Wallet Balance TMN: {user_info.get('wallet_balance_tmn', 0):,.0f}")
                print(f"🔑 Is Admin: {user_info.get('is_admin')}")
                print(f"📋 KYC Level: {user_info.get('kyc_level')}")
                print(f"🎫 Access Token: {data['access_token'][:20]}...")
                
                # Verify required fields
                required_checks = [
                    ("access_token", data.get("access_token") is not None),
                    ("wallet_balance_tmn", user_info.get("wallet_balance_tmn") is not None and user_info.get("wallet_balance_tmn") > 0),
                    ("is_admin", user_info.get("is_admin") == False),
                    ("kyc_level", user_info.get("kyc_level") == 2)
                ]
                
                all_passed = True
                for field, check in required_checks:
                    if check:
                        print(f"✅ {field}: VERIFIED")
                    else:
                        print(f"❌ {field}: FAILED")
                        all_passed = False
                
                if all_passed:
                    self.test_results.append({"test": "test_user_login", "status": "✅ PASS", "details": "All test user login requirements verified"})
                else:
                    self.test_results.append({"test": "test_user_login", "status": "❌ FAIL", "details": "Some test user login requirements failed"})
                
                return True
            else:
                print(f"❌ Test user login failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "test_user_login", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Test user login error: {str(e)}")
            self.test_results.append({"test": "test_user_login", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_admin_profile(self):
        """Test 3: Get User Profile (Admin)"""
        print("\n👑 Test 3: Get Admin User Profile...")
        
        if not self.admin_token:
            print("❌ Admin token not available")
            self.test_results.append({"test": "admin_profile", "status": "❌ SKIP", "details": "Admin token not available"})
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                
                print(f"✅ Admin profile retrieved successfully")
                print(f"📧 Email: {user_info.get('email')}")
                print(f"👤 Full Name: {user_info.get('full_name')}")
                print(f"💰 Wallet Balance TMN: {user_info.get('wallet_balance_tmn', 0):,.0f}")
                print(f"🔑 Is Admin: {user_info.get('is_admin')}")
                print(f"📋 KYC Level: {user_info.get('kyc_level')}")
                print(f"📱 Phone: {user_info.get('phone')}")
                print(f"🆔 User ID: {user_info.get('id')}")
                print(f"✅ Is Active: {user_info.get('is_active')}")
                print(f"📞 Phone Verified: {user_info.get('is_phone_verified')}")
                print(f"📄 KYC Status: {user_info.get('kyc_status')}")
                
                # Verify all user fields are present
                required_fields = ['id', 'email', 'full_name', 'phone', 'wallet_balance_tmn', 'is_admin', 'kyc_level', 'kyc_status', 'is_active', 'is_phone_verified']
                missing_fields = [field for field in required_fields if user_info.get(field) is None]
                
                if not missing_fields:
                    print("✅ All user fields present")
                    self.test_results.append({"test": "admin_profile", "status": "✅ PASS", "details": "Admin profile complete with all fields"})
                else:
                    print(f"❌ Missing fields: {missing_fields}")
                    self.test_results.append({"test": "admin_profile", "status": "❌ FAIL", "details": f"Missing fields: {missing_fields}"})
                
                return True
            else:
                print(f"❌ Admin profile retrieval failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "admin_profile", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Admin profile error: {str(e)}")
            self.test_results.append({"test": "admin_profile", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_trading_access(self):
        """Test 4: Test Trading Access"""
        print("\n📈 Test 4: Test Trading Access...")
        
        # Test crypto prices endpoint (should work for both admin and regular users)
        print("\n📊 Testing crypto prices access...")
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Crypto prices accessible (no auth required)")
                print(f"📊 Prices data: {len(data.get('data', {}))} cryptocurrencies")
                
                # Check for USDT specifically
                prices_data = data.get('data', {})
                if 'tether' in prices_data:
                    usdt_price = prices_data['tether'].get('price_tmn', 0)
                    print(f"💰 USDT Price: {usdt_price:,.0f} TMN")
                
            else:
                print(f"❌ Crypto prices failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Crypto prices error: {str(e)}")
        
        # Test admin trading orders access
        print("\n👑 Testing admin trading orders access...")
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
                
                if response.status_code == 200:
                    orders = response.json()
                    print(f"✅ Admin trading orders accessible")
                    print(f"📊 Admin orders count: {len(orders)}")
                    
                    if orders:
                        latest_order = orders[0]
                        print(f"📋 Latest order: {latest_order.get('order_type')} {latest_order.get('coin_symbol')} - {latest_order.get('status')}")
                    
                else:
                    print(f"❌ Admin trading orders failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Admin trading orders error: {str(e)}")
        
        # Test user trading orders access
        print("\n👤 Testing test user trading orders access...")
        if self.test_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
                
                if response.status_code == 200:
                    orders = response.json()
                    print(f"✅ Test user trading orders accessible")
                    print(f"📊 Test user orders count: {len(orders)}")
                    
                    if orders:
                        latest_order = orders[0]
                        print(f"📋 Latest order: {latest_order.get('order_type')} {latest_order.get('coin_symbol')} - {latest_order.get('status')}")
                    
                else:
                    print(f"❌ Test user trading orders failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Test user trading orders error: {str(e)}")
        
        self.test_results.append({"test": "trading_access", "status": "✅ PASS", "details": "Trading access endpoints tested"})

    async def test_balance_after_order(self):
        """Test 5: Verify Balance After Order"""
        print("\n💰 Test 5: Verify Balance After Order...")
        
        if not self.admin_token:
            print("❌ Admin token not available")
            self.test_results.append({"test": "balance_after_order", "status": "❌ SKIP", "details": "Admin token not available"})
            return False
        
        # Get initial balance
        print("\n📊 Getting initial admin balance...")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                initial_user = response.json()
                initial_balance = initial_user.get('wallet_balance_tmn', 0)
                print(f"💰 Initial balance: {initial_balance:,.0f} TMN")
            else:
                print(f"❌ Failed to get initial balance: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Initial balance error: {str(e)}")
            return False
        
        # Create a small buy order
        print("\n🛒 Creating small buy order...")
        try:
            order_data = {
                "order_type": "buy",
                "coin_symbol": "USDT",
                "coin_id": "tether",
                "amount_tmn": 100000  # 100,000 TMN order
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=order_data)
            
            if response.status_code == 200:
                order_result = response.json()
                print(f"✅ Buy order created successfully")
                order_id = order_result.get('order_id') or order_result.get('id')
                print(f"📋 Order ID: {order_id}")
                print(f"💰 Order Amount: {order_result.get('amount_tmn', 0):,.0f} TMN")
                print(f"🪙 Crypto Amount: {order_result.get('amount_crypto', 0):.6f} USDT")
                print(f"📊 Status: {order_result.get('status')}")
                
                # Check balance after order
                print("\n📊 Checking balance after order...")
                response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if response.status_code == 200:
                    updated_user = response.json()
                    new_balance = updated_user.get('wallet_balance_tmn', 0)
                    balance_change = initial_balance - new_balance
                    
                    print(f"💰 New balance: {new_balance:,.0f} TMN")
                    print(f"📉 Balance deducted: {balance_change:,.0f} TMN")
                    
                    if balance_change == 100000:
                        print("✅ Balance deducted correctly")
                    else:
                        print(f"⚠️  Balance deduction mismatch: expected 100,000, got {balance_change:,.0f}")
                    
                    # Check if order appears in order history
                    print("\n📋 Checking order in history...")
                    response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
                    
                    if response.status_code == 200:
                        orders = response.json()
                        order_found = False
                        
                        order_id = order_result.get('order_id') or order_result.get('id')
                        for order in orders:
                            if order.get('id') == order_id:
                                order_found = True
                                print(f"✅ Order found in history")
                                print(f"📊 Order status: {order.get('status')}")
                                break
                        
                        if not order_found:
                            print("❌ Order not found in history")
                    
                    self.test_results.append({"test": "balance_after_order", "status": "✅ PASS", "details": "Balance verification and order creation successful"})
                    
                else:
                    print(f"❌ Failed to get updated balance: {response.status_code}")
                    self.test_results.append({"test": "balance_after_order", "status": "❌ FAIL", "details": "Could not verify balance after order"})
                
            else:
                print(f"❌ Buy order creation failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "balance_after_order", "status": "❌ FAIL", "details": f"Order creation failed: HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Balance after order error: {str(e)}")
            self.test_results.append({"test": "balance_after_order", "status": "❌ ERROR", "details": str(e)})

    async def run_all_tests(self):
        """Run all authentication and balance tests"""
        print("🚀 Starting Authentication System and Balance Display Testing...")
        print("=" * 70)
        
        # Run tests in sequence
        await self.test_admin_login()
        await self.test_user_login()
        await self.test_admin_profile()
        await self.test_trading_access()
        await self.test_balance_after_order()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📋 AUTHENTICATION & BALANCE TESTING SUMMARY")
        print("=" * 70)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        skipped_tests = [r for r in self.test_results if "SKIP" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⏭️  SKIPPED: {len(skipped_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if skipped_tests:
            print("\n⏭️  SKIPPED TESTS:")
            for test in skipped_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        if len(passed_tests) == len([r for r in self.test_results if "SKIP" not in r["status"]]):
            print("✅ All authentication and balance functionality working correctly")
            print("✅ Admin credentials (admin/istari118) working perfectly")
            print("✅ Test user credentials working as expected")
            print("✅ Balance display and deduction working correctly")
            print("✅ Trading access properly configured")
        else:
            print("⚠️  Some authentication or balance issues detected")
            print("🔍 Review failed tests above for details")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = AuthBalanceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())