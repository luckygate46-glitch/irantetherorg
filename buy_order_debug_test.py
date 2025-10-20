#!/usr/bin/env python3
"""
Buy Order Debug Test - Testing "ثبت سفارش خرید" Button Issue
Specific test for the reported issue: User clicks buy order button but nothing happens
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

class BuyOrderDebugTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_user_token = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up Buy Order Debug testing environment...")
        
        # Login as admin first
        await self.login_admin()
        
        # Create or find test user similar to "akbar ganji"
        await self.setup_test_user()
        
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
                admin_info = data["user"]
                print(f"✅ Admin login successful: {admin_info.get('full_name', 'Admin')}")
                print(f"   Balance: {admin_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                print(f"   KYC Level: {admin_info.get('kyc_level', 0)}")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False

    async def setup_test_user(self):
        """Create or setup test user similar to akbar ganji"""
        try:
            # Try to create a test user similar to the reported user
            test_user_data = {
                "first_name": "اکبر",
                "last_name": "گنجی", 
                "email": "akbar.ganji@test.com",
                "phone": "09123456789",
                "password": "testpass123"
            }
            
            print(f"🔧 Setting up test user: {test_user_data['first_name']} {test_user_data['last_name']}")
            
            # Try to register the user (might already exist)
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                print("✅ Test user created successfully")
            elif response.status_code == 400 and "قبلاً ثبت شده" in response.text:
                print("✅ Test user already exists")
            else:
                print(f"⚠️  User creation response: {response.status_code} - {response.text}")
            
            # Login as the test user
            login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.test_user_token = login_data["access_token"]
                user_info = login_data["user"]
                print(f"✅ Test user login successful: {user_info.get('full_name', 'Test User')}")
                print(f"   User ID: {user_info.get('id')}")
                print(f"   Balance: {user_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                print(f"   KYC Level: {user_info.get('kyc_level', 0)}")
                
                # Set up user with proper balance and KYC level using admin privileges
                await self.setup_user_for_trading(user_info.get('id'))
                
                return True
            else:
                print(f"❌ Test user login failed: {login_response.status_code} - {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test user setup error: {str(e)}")
            return False

    async def setup_user_for_trading(self, user_id):
        """Setup user with proper balance and KYC level for trading"""
        try:
            # Update user balance to 10,000,000 TMN and KYC level to 2
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            update_data = {
                "wallet_balance_tmn": 10000000.0,  # 10M TMN as reported
                "kyc_level": 2,  # Level 2 for trading
                "kyc_status": "approved"
            }
            
            response = await self.client.put(f"{BACKEND_URL}/admin/users/{user_id}", 
                                           headers=headers, json=update_data)
            
            if response.status_code == 200:
                print("✅ Test user updated with 10M TMN balance and KYC Level 2")
                return True
            else:
                print(f"⚠️  User update response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ User setup error: {str(e)}")
            return False

    async def add_wallet_address(self):
        """Add USDT wallet address for the test user"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            wallet_data = {
                "symbol": "USDT",
                "address": "TE1VGdRnvga3KduECqKuuNEkm2xwLrWS4F",  # Exact address from report
                "label": "Test USDT Wallet"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/user/wallet-addresses", 
                                            headers=headers, json=wallet_data)
            
            if response.status_code == 200:
                print("✅ USDT wallet address added successfully")
                return True
            elif response.status_code == 400 and "قبلاً اضافه شده" in response.text:
                print("✅ USDT wallet address already exists")
                return True
            else:
                print(f"⚠️  Wallet address response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Wallet address error: {str(e)}")
            return False

    async def test_crypto_prices_endpoint(self):
        """Test crypto prices endpoint to get current USDT price"""
        print("\n💰 Testing Crypto Prices Endpoint...")
        
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Crypto prices endpoint working")
                
                # Find USDT price
                usdt_price = None
                for crypto in data:
                    if crypto.get('symbol') == 'USDT':
                        usdt_price = crypto.get('price_tmn', 0)
                        break
                
                if usdt_price:
                    print(f"📊 Current USDT Price: {usdt_price:,.0f} TMN")
                    
                    # Calculate expected USDT amount for 1M TMN
                    expected_usdt = 1000000 / usdt_price
                    print(f"📊 Expected USDT for 1M TMN: {expected_usdt:.8f}")
                    
                    self.test_results.append({"test": "crypto_prices", "status": "✅ PASS", "details": f"USDT price: {usdt_price:,.0f} TMN"})
                    return usdt_price
                else:
                    print("❌ USDT price not found in response")
                    self.test_results.append({"test": "crypto_prices", "status": "❌ FAIL", "details": "USDT price not found"})
                    return None
            else:
                print(f"❌ Crypto prices failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "crypto_prices", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return None
                
        except Exception as e:
            print(f"❌ Crypto prices error: {str(e)}")
            self.test_results.append({"test": "crypto_prices", "status": "❌ ERROR", "details": str(e)})
            return None

    async def test_user_profile_check(self):
        """Test user profile to verify balance and KYC status"""
        print("\n👤 Testing User Profile Check...")
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User profile endpoint working")
                
                balance = data.get('wallet_balance_tmn', 0)
                kyc_level = data.get('kyc_level', 0)
                kyc_status = data.get('kyc_status', 'unknown')
                full_name = data.get('full_name', 'Unknown')
                
                print(f"📊 User: {full_name}")
                print(f"📊 Balance: {balance:,.0f} TMN")
                print(f"📊 KYC Level: {kyc_level}")
                print(f"📊 KYC Status: {kyc_status}")
                
                # Check if user meets trading requirements
                if balance >= 1000000:
                    print("✅ User has sufficient balance for 1M TMN order")
                else:
                    print("❌ User has insufficient balance for 1M TMN order")
                
                if kyc_level >= 2:
                    print("✅ User has required KYC level for trading")
                else:
                    print("❌ User does not have required KYC level for trading")
                
                self.test_results.append({"test": "user_profile", "status": "✅ PASS", "details": f"Balance: {balance:,.0f} TMN, KYC: {kyc_level}"})
                return True
            else:
                print(f"❌ User profile failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "user_profile", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ User profile error: {str(e)}")
            self.test_results.append({"test": "user_profile", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_wallet_addresses_check(self):
        """Test wallet addresses to verify USDT wallet exists"""
        print("\n💳 Testing Wallet Addresses Check...")
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/user/wallet-addresses", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Wallet addresses endpoint working")
                
                usdt_wallet = None
                for wallet in data:
                    if wallet.get('symbol') == 'USDT':
                        usdt_wallet = wallet
                        break
                
                if usdt_wallet:
                    print(f"✅ USDT wallet found: {usdt_wallet.get('address')}")
                    print(f"📊 Wallet verified: {usdt_wallet.get('verified', False)}")
                    
                    # Check if it matches the reported address
                    if usdt_wallet.get('address') == "TE1VGdRnvga3KduECqKuuNEkm2xwLrWS4F":
                        print("✅ Wallet address matches reported address")
                    else:
                        print(f"⚠️  Wallet address differs from reported: {usdt_wallet.get('address')}")
                    
                    self.test_results.append({"test": "wallet_addresses", "status": "✅ PASS", "details": "USDT wallet found"})
                    return True
                else:
                    print("❌ USDT wallet not found")
                    self.test_results.append({"test": "wallet_addresses", "status": "❌ FAIL", "details": "USDT wallet not found"})
                    return False
            else:
                print(f"❌ Wallet addresses failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "wallet_addresses", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Wallet addresses error: {str(e)}")
            self.test_results.append({"test": "wallet_addresses", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_buy_order_creation(self):
        """Test the actual buy order creation - the core issue"""
        print("\n🛒 Testing Buy Order Creation (CORE ISSUE)...")
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Exact order data as reported in the issue
            order_data = {
                "order_type": "buy",
                "coin_symbol": "USDT",
                "coin_id": "tether",
                "amount_tmn": 1000000,  # 1M TMN as reported
                "user_wallet_address": "TE1VGdRnvga3KduECqKuuNEkm2xwLrWS4F"  # Exact address from report
            }
            
            print(f"📋 Order Details:")
            print(f"   Type: {order_data['order_type']}")
            print(f"   Coin: {order_data['coin_symbol']}")
            print(f"   Amount: {order_data['amount_tmn']:,.0f} TMN")
            print(f"   Wallet: {order_data['user_wallet_address']}")
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                                            headers=headers, json=order_data)
            
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ BUY ORDER CREATION SUCCESSFUL!")
                
                order_id = data.get('order_id')
                calculated_usdt = data.get('calculated_crypto_amount', 0)
                total_value = data.get('total_value_tmn', 0)
                status = data.get('status', 'unknown')
                
                print(f"📊 Order ID: {order_id}")
                print(f"📊 Calculated USDT: {calculated_usdt:.8f}")
                print(f"📊 Total Value: {total_value:,.0f} TMN")
                print(f"📊 Status: {status}")
                
                # Check if calculated USDT matches expected (around 8.68885220)
                expected_usdt = 8.68885220
                if abs(calculated_usdt - expected_usdt) < 0.1:
                    print(f"✅ Calculated USDT matches expected: {expected_usdt:.8f}")
                else:
                    print(f"⚠️  Calculated USDT differs from expected: {calculated_usdt:.8f} vs {expected_usdt:.8f}")
                
                self.test_results.append({"test": "buy_order_creation", "status": "✅ PASS", "details": f"Order created: {order_id}"})
                return order_id
                
            elif response.status_code == 400:
                error_text = response.text
                print(f"❌ BUY ORDER FAILED - Validation Error: {error_text}")
                
                # Check for specific error messages
                if "موجودی کافی ندارید" in error_text:
                    print("💡 Issue: Insufficient balance")
                elif "کیف پول" in error_text:
                    print("💡 Issue: Wallet address problem")
                elif "احراز هویت" in error_text or "KYC" in error_text:
                    print("💡 Issue: KYC verification problem")
                else:
                    print("💡 Issue: Other validation error")
                
                self.test_results.append({"test": "buy_order_creation", "status": "❌ FAIL", "details": f"Validation error: {error_text}"})
                return None
                
            elif response.status_code == 401:
                print("❌ BUY ORDER FAILED - Authentication Error")
                print("💡 Issue: JWT token invalid or expired")
                self.test_results.append({"test": "buy_order_creation", "status": "❌ FAIL", "details": "Authentication error"})
                return None
                
            elif response.status_code == 403:
                print("❌ BUY ORDER FAILED - Authorization Error")
                print("💡 Issue: User not authorized for trading")
                self.test_results.append({"test": "buy_order_creation", "status": "❌ FAIL", "details": "Authorization error"})
                return None
                
            else:
                print(f"❌ BUY ORDER FAILED - Unexpected Error: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append({"test": "buy_order_creation", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return None
                
        except Exception as e:
            print(f"❌ Buy order creation error: {str(e)}")
            self.test_results.append({"test": "buy_order_creation", "status": "❌ ERROR", "details": str(e)})
            return None

    async def test_order_verification(self, order_id):
        """Verify the created order appears in user's order history"""
        if not order_id:
            print("\n⚠️  Skipping order verification - no order ID")
            return False
            
        print("\n📋 Testing Order Verification...")
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Order history endpoint working")
                
                # Find the created order
                created_order = None
                for order in data:
                    if order.get('id') == order_id:
                        created_order = order
                        break
                
                if created_order:
                    print(f"✅ Order found in history: {order_id}")
                    print(f"📊 Order Status: {created_order.get('status', 'unknown')}")
                    print(f"📊 Order Amount: {created_order.get('amount_tmn', 0):,.0f} TMN")
                    
                    self.test_results.append({"test": "order_verification", "status": "✅ PASS", "details": "Order found in history"})
                    return True
                else:
                    print(f"❌ Order not found in history: {order_id}")
                    self.test_results.append({"test": "order_verification", "status": "❌ FAIL", "details": "Order not in history"})
                    return False
            else:
                print(f"❌ Order history failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "order_verification", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Order verification error: {str(e)}")
            self.test_results.append({"test": "order_verification", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_balance_deduction(self):
        """Test if balance was properly deducted after order"""
        print("\n💰 Testing Balance Deduction...")
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                current_balance = data.get('wallet_balance_tmn', 0)
                
                print(f"📊 Current Balance: {current_balance:,.0f} TMN")
                
                # Expected balance should be 9M TMN (10M - 1M)
                expected_balance = 9000000
                
                if abs(current_balance - expected_balance) < 1000:  # Allow small rounding differences
                    print(f"✅ Balance correctly deducted to ~{expected_balance:,.0f} TMN")
                    self.test_results.append({"test": "balance_deduction", "status": "✅ PASS", "details": f"Balance: {current_balance:,.0f} TMN"})
                    return True
                else:
                    print(f"⚠️  Balance not as expected. Current: {current_balance:,.0f}, Expected: ~{expected_balance:,.0f}")
                    self.test_results.append({"test": "balance_deduction", "status": "⚠️  PARTIAL", "details": f"Unexpected balance: {current_balance:,.0f}"})
                    return False
            else:
                print(f"❌ Balance check failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "balance_deduction", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Balance deduction error: {str(e)}")
            self.test_results.append({"test": "balance_deduction", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_admin_order_visibility(self, order_id):
        """Test if admin can see the created order"""
        if not order_id:
            print("\n⚠️  Skipping admin order visibility - no order ID")
            return False
            
        print("\n👨‍💼 Testing Admin Order Visibility...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Admin orders endpoint working")
                
                # Find the created order
                admin_order = None
                for order in data:
                    if order.get('id') == order_id:
                        admin_order = order
                        break
                
                if admin_order:
                    print(f"✅ Order visible to admin: {order_id}")
                    print(f"📊 User Email: {admin_order.get('user_email', 'N/A')}")
                    print(f"📊 Order Status: {admin_order.get('status', 'unknown')}")
                    
                    self.test_results.append({"test": "admin_order_visibility", "status": "✅ PASS", "details": "Order visible to admin"})
                    return True
                else:
                    print(f"❌ Order not visible to admin: {order_id}")
                    self.test_results.append({"test": "admin_order_visibility", "status": "❌ FAIL", "details": "Order not visible to admin"})
                    return False
            else:
                print(f"❌ Admin orders failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "admin_order_visibility", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Admin order visibility error: {str(e)}")
            self.test_results.append({"test": "admin_order_visibility", "status": "❌ ERROR", "details": str(e)})
            return False

    async def run_all_tests(self):
        """Run all buy order debug tests"""
        print("🚀 Starting Buy Order Debug Testing...")
        print("🎯 Testing reported issue: 'ثبت سفارش خرید' button not working")
        print("=" * 70)
        
        await self.setup()
        
        if not self.test_user_token:
            print("❌ Cannot proceed without test user authentication")
            return
        
        # Add wallet address first
        await self.add_wallet_address()
        
        # Run prerequisite tests
        usdt_price = await self.test_crypto_prices_endpoint()
        await self.test_user_profile_check()
        await self.test_wallet_addresses_check()
        
        # Run the core test - buy order creation
        order_id = await self.test_buy_order_creation()
        
        # Run verification tests
        await self.test_order_verification(order_id)
        await self.test_balance_deduction()
        await self.test_admin_order_visibility(order_id)
        
        # Print summary
        print("\n" + "=" * 70)
        print("📋 BUY ORDER DEBUG TESTING SUMMARY")
        print("=" * 70)
        
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
        
        print("\n🎯 DIAGNOSIS:")
        
        # Determine if backend is working
        core_test = next((r for r in self.test_results if r["test"] == "buy_order_creation"), None)
        if core_test and "✅ PASS" in core_test["status"]:
            print("✅ BACKEND BUY ORDER API IS WORKING CORRECTLY")
            print("💡 Issue is likely FRONTEND-related:")
            print("   - JavaScript errors preventing API call")
            print("   - Form validation blocking submission")
            print("   - Button click handler not firing")
            print("   - CORS or network issues")
            print("   - Frontend not sending proper Authorization header")
        elif core_test and "❌" in core_test["status"]:
            print("❌ BACKEND BUY ORDER API HAS ISSUES")
            print("💡 Backend problems identified:")
            print(f"   - {core_test['details']}")
        else:
            print("❓ INCONCLUSIVE - Unable to test buy order creation")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = BuyOrderDebugTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())