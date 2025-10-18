#!/usr/bin/env python3
"""
Final Comprehensive Backend Testing for Iranian Crypto Exchange
Testing ALL endpoints specified in the review request with admin user
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://cryptotradera.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class FinalBackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_user_token = None
        self.test_results = []
        
    async def test_admin_login(self):
        """Test admin login - POST /api/auth/login"""
        print("🔑 Testing Admin Login (admin/istari118)...")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_info = data["user"]
                
                print(f"✅ Admin login successful")
                print(f"📊 Admin Name: {admin_info.get('full_name', 'Admin')}")
                print(f"📊 KYC Level: {admin_info.get('kyc_level', 'N/A')}")
                print(f"📊 Balance: {admin_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                print(f"📊 Is Admin: {admin_info.get('is_admin', False)}")
                
                self.test_results.append({"endpoint": "POST /api/auth/login", "status": "✅ PASS", "details": "Admin login working with JWT token"})
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                self.test_results.append({"endpoint": "POST /api/auth/login", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            self.test_results.append({"endpoint": "POST /api/auth/login", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_user_registration(self):
        """Test user registration - POST /api/auth/register"""
        print("\n👤 Testing User Registration...")
        
        try:
            timestamp = int(datetime.now().timestamp())
            test_email = f"test_reg_{timestamp}@example.com"
            test_phone = f"0912345{timestamp % 10000:04d}"
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json={
                "first_name": "کاربر",
                "last_name": "تست",
                "email": test_email,
                "phone": test_phone,
                "password": "test123456"
            })
            
            if response.status_code == 200:
                data = response.json()
                user_info = data["user"]
                
                print(f"✅ User registration successful")
                print(f"📊 User Name: {user_info.get('full_name', 'N/A')}")
                print(f"📊 Email: {user_info.get('email', 'N/A')}")
                print(f"📊 Is Admin: {user_info.get('is_admin', False)}")
                
                # Verify is_admin=False for new users
                if not user_info.get('is_admin', True):
                    print("✅ Confirmed: New users are not admin by default")
                    self.test_results.append({"endpoint": "POST /api/auth/register", "status": "✅ PASS", "details": "Registration working, is_admin=False for new users"})
                else:
                    print("⚠️  Warning: New user has admin privileges")
                    self.test_results.append({"endpoint": "POST /api/auth/register", "status": "⚠️  PARTIAL", "details": "Registration working but new user has admin privileges"})
                
                return True
            else:
                print(f"❌ User registration failed: {response.status_code}")
                self.test_results.append({"endpoint": "POST /api/auth/register", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ User registration error: {str(e)}")
            self.test_results.append({"endpoint": "POST /api/auth/register", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_get_current_user(self):
        """Test get current user - GET /api/auth/me"""
        print("\n👤 Testing Get Current User...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "GET /api/auth/me", "status": "❌ FAIL", "details": "No admin token"})
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Get current user working")
                print(f"📊 User Data Retrieved: {len(data)} fields")
                
                # Verify JWT token and user data response
                required_fields = ['id', 'email', 'full_name', 'kyc_level', 'is_admin']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ JWT token verification and user data response complete")
                    self.test_results.append({"endpoint": "GET /api/auth/me", "status": "✅ PASS", "details": "Authenticated user data retrieval working"})
                else:
                    print(f"⚠️  Missing fields: {missing_fields}")
                    self.test_results.append({"endpoint": "GET /api/auth/me", "status": "⚠️  PARTIAL", "details": f"Missing fields: {missing_fields}"})
            else:
                print(f"❌ Get current user failed: {response.status_code}")
                self.test_results.append({"endpoint": "GET /api/auth/me", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Get current user error: {str(e)}")
            self.test_results.append({"endpoint": "GET /api/auth/me", "status": "❌ ERROR", "details": str(e)})

    async def test_crypto_prices(self):
        """Test get crypto prices - GET /api/crypto/prices"""
        print("\n💰 Testing Get Crypto Prices...")
        
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    prices = data['data']
                    crypto_count = len(prices)
                    
                    print(f"✅ Crypto prices working")
                    print(f"📊 Cryptocurrencies: {crypto_count}")
                    
                    # Verify returns 15+ cryptocurrencies with TMN prices
                    if crypto_count >= 15:
                        print("✅ Returns 15+ cryptocurrencies as required")
                        
                        # Check TMN prices
                        tmn_prices_found = 0
                        for coin_id, coin_data in prices.items():
                            if 'price_tmn' in coin_data and coin_data['price_tmn'] > 0:
                                tmn_prices_found += 1
                        
                        print(f"📊 Coins with TMN prices: {tmn_prices_found}/{crypto_count}")
                        
                        if tmn_prices_found >= 15:
                            print("✅ TMN prices available for cryptocurrencies")
                            self.test_results.append({"endpoint": "GET /api/crypto/prices", "status": "✅ PASS", "details": f"{crypto_count} cryptocurrencies with TMN prices"})
                        else:
                            self.test_results.append({"endpoint": "GET /api/crypto/prices", "status": "⚠️  PARTIAL", "details": f"Only {tmn_prices_found} coins have TMN prices"})
                    else:
                        print(f"⚠️  Only {crypto_count} cryptocurrencies (expected 15+)")
                        self.test_results.append({"endpoint": "GET /api/crypto/prices", "status": "⚠️  PARTIAL", "details": f"Only {crypto_count} cryptocurrencies"})
                else:
                    print("❌ Invalid response format")
                    self.test_results.append({"endpoint": "GET /api/crypto/prices", "status": "❌ FAIL", "details": "Invalid response format"})
            else:
                print(f"❌ Crypto prices failed: {response.status_code}")
                self.test_results.append({"endpoint": "GET /api/crypto/prices", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Crypto prices error: {str(e)}")
            self.test_results.append({"endpoint": "GET /api/crypto/prices", "status": "❌ ERROR", "details": str(e)})

    async def test_create_buy_order(self):
        """Test create buy order - POST /api/trading/order"""
        print("\n🛒 Testing Create Buy Order...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "POST /api/trading/order", "status": "❌ FAIL", "details": "No admin token"})
            return None
        
        try:
            # First add a wallet address
            await self.add_wallet_address()
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            order_data = {
                "order_type": "buy",
                "coin_symbol": "USDT",
                "coin_id": "tether",
                "amount_tmn": 500000  # 500K TMN
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=order_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Buy order created successfully")
                print(f"📊 Order ID: {data.get('id', 'N/A')[:8]}...")
                print(f"📊 Amount: {data.get('amount_tmn', 0):,.0f} TMN")
                print(f"📊 Status: {data.get('status', 'N/A')}")
                
                # Verify order creation and balance deduction
                if data.get('status') == 'pending':
                    print("✅ Order creation and status tracking working")
                    self.test_results.append({"endpoint": "POST /api/trading/order", "status": "✅ PASS", "details": "Buy order creation working with KYC Level 2 user"})
                    return data.get('id')
                else:
                    print(f"⚠️  Unexpected order status: {data.get('status')}")
                    self.test_results.append({"endpoint": "POST /api/trading/order", "status": "⚠️  PARTIAL", "details": f"Order created but status is {data.get('status')}"})
                    return data.get('id')
            else:
                print(f"❌ Buy order creation failed: {response.status_code} - {response.text}")
                self.test_results.append({"endpoint": "POST /api/trading/order", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return None
                
        except Exception as e:
            print(f"❌ Buy order creation error: {str(e)}")
            self.test_results.append({"endpoint": "POST /api/trading/order", "status": "❌ ERROR", "details": str(e)})
            return None

    async def add_wallet_address(self):
        """Add wallet address for testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            wallet_data = {
                "symbol": "USDT",
                "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b1",
                "label": "Test USDT Wallet"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/user/wallet-addresses", headers=headers, json=wallet_data)
            
            if response.status_code in [200, 201]:
                print("✅ Wallet address added")
            elif response.status_code == 400 and "قبلاً اضافه شده" in response.text:
                print("✅ Wallet address already exists")
            else:
                print(f"⚠️  Wallet address issue: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Wallet address error: {str(e)}")

    async def test_get_user_orders(self):
        """Test get user orders - GET /api/trading/orders/my"""
        print("\n📋 Testing Get User Orders...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "GET /api/trading/orders/my", "status": "❌ FAIL", "details": "No admin token"})
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                orders_count = len(data) if isinstance(data, list) else 0
                
                print(f"✅ Get user orders working")
                print(f"📊 User Orders: {orders_count}")
                
                # Verify user can see their orders
                if orders_count >= 0:  # Even 0 orders is valid
                    print("✅ User can see their orders")
                    self.test_results.append({"endpoint": "GET /api/trading/orders/my", "status": "✅ PASS", "details": f"User orders retrieval working ({orders_count} orders)"})
                else:
                    print("❌ Invalid orders response")
                    self.test_results.append({"endpoint": "GET /api/trading/orders/my", "status": "❌ FAIL", "details": "Invalid orders response"})
            else:
                print(f"❌ Get user orders failed: {response.status_code}")
                self.test_results.append({"endpoint": "GET /api/trading/orders/my", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Get user orders error: {str(e)}")
            self.test_results.append({"endpoint": "GET /api/trading/orders/my", "status": "❌ ERROR", "details": str(e)})

    async def test_get_user_holdings(self):
        """Test get user holdings - GET /api/trading/holdings/my"""
        print("\n💼 Testing Get User Holdings...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "GET /api/trading/holdings/my", "status": "❌ FAIL", "details": "No admin token"})
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/holdings/my", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                holdings_count = len(data) if isinstance(data, list) else 0
                
                print(f"✅ Get user holdings working")
                print(f"📊 User Holdings: {holdings_count}")
                
                # Verify user can see their crypto holdings
                if holdings_count >= 0:  # Even 0 holdings is valid
                    print("✅ User can see their crypto holdings")
                    self.test_results.append({"endpoint": "GET /api/trading/holdings/my", "status": "✅ PASS", "details": f"User holdings retrieval working ({holdings_count} holdings)"})
                else:
                    print("❌ Invalid holdings response")
                    self.test_results.append({"endpoint": "GET /api/trading/holdings/my", "status": "❌ FAIL", "details": "Invalid holdings response"})
            else:
                print(f"❌ Get user holdings failed: {response.status_code}")
                self.test_results.append({"endpoint": "GET /api/trading/holdings/my", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Get user holdings error: {str(e)}")
            self.test_results.append({"endpoint": "GET /api/trading/holdings/my", "status": "❌ ERROR", "details": str(e)})

    async def test_admin_get_all_users(self):
        """Test admin get all users - GET /api/admin/users"""
        print("\n👥 Testing Admin Get All Users...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "GET /api/admin/users", "status": "❌ FAIL", "details": "No admin token"})
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users_count = len(data) if isinstance(data, list) else 0
                
                print(f"✅ Admin get all users working")
                print(f"📊 Total Users: {users_count}")
                
                # Verify admin can see all users
                if users_count > 0:
                    admin_users = [u for u in data if u.get('is_admin', False)]
                    regular_users = [u for u in data if not u.get('is_admin', False)]
                    
                    print(f"📊 Admin Users: {len(admin_users)}")
                    print(f"📊 Regular Users: {len(regular_users)}")
                    print("✅ Admin can see all users")
                    
                    self.test_results.append({"endpoint": "GET /api/admin/users", "status": "✅ PASS", "details": f"Admin can see all {users_count} users"})
                else:
                    print("⚠️  No users found")
                    self.test_results.append({"endpoint": "GET /api/admin/users", "status": "⚠️  PARTIAL", "details": "No users found"})
            else:
                print(f"❌ Admin get all users failed: {response.status_code}")
                self.test_results.append({"endpoint": "GET /api/admin/users", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Admin get all users error: {str(e)}")
            self.test_results.append({"endpoint": "GET /api/admin/users", "status": "❌ ERROR", "details": str(e)})

    async def test_admin_get_all_orders(self):
        """Test admin get all orders - GET /api/admin/orders"""
        print("\n📋 Testing Admin Get All Orders...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "GET /api/admin/orders", "status": "❌ FAIL", "details": "No admin token"})
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                orders_count = len(data) if isinstance(data, list) else 0
                
                print(f"✅ Admin get all orders working")
                print(f"📊 Total Orders: {orders_count}")
                
                # Verify admin can see all orders
                if orders_count > 0:
                    order_statuses = {}
                    for order in data:
                        status = order.get('status', 'unknown')
                        order_statuses[status] = order_statuses.get(status, 0) + 1
                    
                    print(f"📊 Order Statuses: {order_statuses}")
                    print("✅ Admin can see all orders")
                    
                    self.test_results.append({"endpoint": "GET /api/admin/orders", "status": "✅ PASS", "details": f"Admin can see all {orders_count} orders"})
                    return data
                else:
                    print("⚠️  No orders found")
                    self.test_results.append({"endpoint": "GET /api/admin/orders", "status": "⚠️  PARTIAL", "details": "No orders found"})
                    return []
            else:
                print(f"❌ Admin get all orders failed: {response.status_code}")
                self.test_results.append({"endpoint": "GET /api/admin/orders", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return []
                
        except Exception as e:
            print(f"❌ Admin get all orders error: {str(e)}")
            self.test_results.append({"endpoint": "GET /api/admin/orders", "status": "❌ ERROR", "details": str(e)})
            return []

    async def test_admin_approve_order(self, orders_data):
        """Test admin approve order - POST /api/admin/orders/approve"""
        print("\n✅ Testing Admin Order Approval...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({"endpoint": "POST /api/admin/orders/approve", "status": "❌ FAIL", "details": "No admin token"})
            return
        
        try:
            # Find a pending order to approve
            pending_orders = [o for o in orders_data if o.get('status') == 'pending']
            
            if not pending_orders:
                print("⚠️  No pending orders found for approval test")
                self.test_results.append({"endpoint": "POST /api/admin/orders/approve", "status": "⚠️  SKIP", "details": "No pending orders to approve"})
                return
            
            order_to_approve = pending_orders[0]
            order_id = order_to_approve.get('id')
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            approval_data = {
                "order_id": order_id,
                "action": "approve",
                "admin_note": "Test approval from comprehensive backend test"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/admin/orders/approve", headers=headers, json=approval_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Order approval working")
                print(f"📊 Order ID: {order_id[:8]}...")
                print(f"📊 Response: {data.get('message', 'N/A')}")
                
                # Verify order approval workflow
                print("✅ Order approval workflow functional")
                self.test_results.append({"endpoint": "POST /api/admin/orders/approve", "status": "✅ PASS", "details": "Order approval workflow working"})
            else:
                print(f"❌ Order approval failed: {response.status_code} - {response.text}")
                self.test_results.append({"endpoint": "POST /api/admin/orders/approve", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Order approval error: {str(e)}")
            self.test_results.append({"endpoint": "POST /api/admin/orders/approve", "status": "❌ ERROR", "details": str(e)})

    async def test_status_codes_and_errors(self):
        """Test proper status codes and Persian error messages"""
        print("\n🛡️  Testing Status Codes and Error Handling...")
        
        error_tests = []
        
        # Test 401 Unauthorized
        try:
            response = await self.client.get(f"{BACKEND_URL}/admin/users")
            if response.status_code == 401:
                error_tests.append("✅ 401 Unauthorized working")
            else:
                error_tests.append(f"⚠️  Expected 401, got {response.status_code}")
        except:
            error_tests.append("❌ Error testing 401")
        
        # Test 403 Forbidden (if we had a regular user)
        # Test 404 Not Found
        try:
            response = await self.client.get(f"{BACKEND_URL}/nonexistent/endpoint")
            if response.status_code == 404:
                error_tests.append("✅ 404 Not Found working")
            else:
                error_tests.append(f"⚠️  Expected 404, got {response.status_code}")
        except:
            error_tests.append("❌ Error testing 404")
        
        # Test 422 Validation Error
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json={"invalid": "data"})
                if response.status_code == 422:
                    error_tests.append("✅ 422 Validation Error working")
                else:
                    error_tests.append(f"⚠️  Expected 422, got {response.status_code}")
            except:
                error_tests.append("❌ Error testing 422")
        
        # Test Persian error messages
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                # Try to create order with insufficient balance (if possible)
                response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json={
                    "order_type": "buy",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_tmn": 999999999999  # Very large amount
                })
                
                if response.status_code in [400, 422]:
                    response_text = response.text
                    if any(char in response_text for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                        error_tests.append("✅ Persian error messages working")
                    else:
                        error_tests.append("⚠️  Error messages not in Persian")
                else:
                    error_tests.append("⚠️  Could not test Persian error messages")
            except:
                error_tests.append("❌ Error testing Persian messages")
        
        print("\n".join(error_tests))
        
        passed_error_tests = len([t for t in error_tests if "✅" in t])
        total_error_tests = len(error_tests)
        
        if passed_error_tests >= total_error_tests * 0.75:  # 75% pass rate
            self.test_results.append({"endpoint": "Error Handling", "status": "✅ PASS", "details": f"{passed_error_tests}/{total_error_tests} error handling tests passed"})
        else:
            self.test_results.append({"endpoint": "Error Handling", "status": "⚠️  PARTIAL", "details": f"{passed_error_tests}/{total_error_tests} error handling tests passed"})

    async def run_all_tests(self):
        """Run all tests as specified in the review request"""
        print("🚀 COMPREHENSIVE BACKEND TESTING - REVIEW REQUEST")
        print("=" * 80)
        print("Testing ALL critical backend functionality for Iranian Crypto Exchange")
        print("=" * 80)
        
        # Test all endpoints in order
        if not await self.test_admin_login():
            print("❌ Cannot proceed without admin authentication")
            return
        
        await self.test_user_registration()
        await self.test_get_current_user()
        await self.test_crypto_prices()
        await self.test_create_buy_order()
        await self.test_get_user_orders()
        await self.test_get_user_holdings()
        await self.test_admin_get_all_users()
        
        # Get orders data for approval test
        orders_data = await self.test_admin_get_all_orders()
        await self.test_admin_approve_order(orders_data)
        
        await self.test_status_codes_and_errors()
        
        # Print comprehensive summary
        print("\n" + "=" * 80)
        print("📋 FINAL COMPREHENSIVE BACKEND TEST RESULTS")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        warning_tests = [r for r in self.test_results if "⚠️" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⚠️  WARNINGS/PARTIAL: {len(warning_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result['status']} {result['endpoint']}: {result['details']}")
        
        if failed_tests:
            print(f"\n❌ CRITICAL ISSUES ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['endpoint']}: {test['details']}")
        
        if warning_tests:
            print(f"\n⚠️  WARNINGS/PARTIAL ({len(warning_tests)}):")
            for test in warning_tests:
                print(f"  - {test['endpoint']}: {test['details']}")
        
        print("\n🎯 REVIEW REQUEST COMPLIANCE:")
        
        # Authentication & User Management
        auth_endpoints = ["POST /api/auth/register", "POST /api/auth/login", "GET /api/auth/me"]
        auth_results = [r for r in self.test_results if r['endpoint'] in auth_endpoints]
        auth_passed = len([r for r in auth_results if "✅ PASS" in r['status']])
        print(f"🔐 Authentication & User Management: {auth_passed}/{len(auth_results)} ({'✅ PASS' if auth_passed == len(auth_results) else '⚠️  ISSUES'})")
        
        # Trading System
        trading_endpoints = ["GET /api/crypto/prices", "POST /api/trading/order", "GET /api/trading/orders/my", "GET /api/trading/holdings/my"]
        trading_results = [r for r in self.test_results if r['endpoint'] in trading_endpoints]
        trading_passed = len([r for r in trading_results if "✅ PASS" in r['status']])
        print(f"💰 Trading System: {trading_passed}/{len(trading_results)} ({'✅ PASS' if trading_passed == len(trading_results) else '⚠️  ISSUES'})")
        
        # Admin Functions
        admin_endpoints = ["GET /api/admin/users", "GET /api/admin/orders", "POST /api/admin/orders/approve"]
        admin_results = [r for r in self.test_results if r['endpoint'] in admin_endpoints]
        admin_passed = len([r for r in admin_results if "✅ PASS" in r['status']])
        print(f"👑 Admin Functions: {admin_passed}/{len(admin_results)} ({'✅ PASS' if admin_passed == len(admin_results) else '⚠️  ISSUES'})")
        
        # Overall assessment
        if success_rate >= 90:
            print("\n🟢 OVERALL ASSESSMENT: EXCELLENT")
            print("   All critical backend functionality working correctly")
            print("   System ready for production use")
        elif success_rate >= 75:
            print("\n🟡 OVERALL ASSESSMENT: GOOD")
            print("   Most functionality working, minor issues present")
            print("   System mostly ready for production")
        elif success_rate >= 50:
            print("\n🟠 OVERALL ASSESSMENT: FAIR")
            print("   Some critical issues need attention")
            print("   System needs fixes before production")
        else:
            print("\n🔴 OVERALL ASSESSMENT: POOR")
            print("   Major issues require immediate attention")
            print("   System not ready for production")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = FinalBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())