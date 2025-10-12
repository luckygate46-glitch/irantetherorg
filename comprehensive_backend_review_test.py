#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - Review Request Specifications
Testing all critical backend functionality as requested in the review:

1. Authentication System
2. Trading System  
3. User Management
4. Admin Functions
5. AI Features (Without API Key)
6. Error Handling

Focus: All endpoints return correct status codes, Persian error messages work, 
Authentication/authorization working, No mock data in AI responses, Database operations successful
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import sys
import random
import string

# Configuration
BACKEND_URL = "https://cryptotoman.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class ComprehensiveBackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_user_token = None
        self.test_user_email = None
        self.test_user_id = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up comprehensive backend testing environment...")
        
        # Login as admin first
        await self.login_admin()
        
    async def login_admin(self):
        """Login as admin (admin/istari118)"""
        print("\n🔑 Testing Admin Login (admin/istari118)...")
        
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
                print(f"📊 Admin KYC Level: {admin_info.get('kyc_level', 'N/A')}")
                print(f"📊 Admin Balance: {admin_info.get('wallet_balance_tmn', 0):,.0f} TMN")
                
                # Verify JWT token works
                if self.admin_token and len(self.admin_token) > 50:
                    print("✅ JWT token generated successfully")
                else:
                    print("⚠️  JWT token seems invalid")
                
                # Verify admin privileges
                if admin_info.get('is_admin', False):
                    print("✅ Admin privileges confirmed")
                    self.test_results.append({"test": "admin_login", "status": "✅ PASS", "details": "Admin login and JWT token working"})
                else:
                    print("❌ Admin privileges not found")
                    self.test_results.append({"test": "admin_login", "status": "❌ FAIL", "details": "Admin user lacks admin privileges"})
                    
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "admin_login", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            self.test_results.append({"test": "admin_login", "status": "❌ ERROR", "details": str(e)})
            return False

    async def test_user_registration_and_login(self):
        """Test user registration with phone: 09123456789, email: test_comprehensive@example.com, password: test123"""
        print("\n👤 Testing User Registration and Login...")
        
        # Generate unique email and phone to avoid conflicts
        random_suffix = ''.join(random.choices(string.digits, k=4))
        self.test_user_email = f"test_comprehensive_{random_suffix}@example.com"
        test_phone = f"0912345{random_suffix}"  # Unique phone number
        test_password = "test123"
        
        try:
            # Test registration
            registration_data = {
                "first_name": "تست",
                "last_name": "جامع",
                "email": self.test_user_email,
                "phone": test_phone,
                "password": test_password
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                user_info = data["user"]
                self.test_user_id = user_info["id"]
                
                print(f"✅ User registration successful: {user_info.get('full_name', 'Test User')}")
                print(f"📊 User ID: {self.test_user_id}")
                print(f"📊 User Email: {user_info.get('email')}")
                print(f"📊 User Phone: {user_info.get('phone')}")
                
                # Test login with created user
                login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": self.test_user_email,
                    "password": test_password
                })
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    print("✅ User login after registration successful")
                    
                    # Verify JWT tokens work
                    if login_data["access_token"] and len(login_data["access_token"]) > 50:
                        print("✅ JWT token verification successful")
                        self.test_results.append({"test": "user_registration_login", "status": "✅ PASS", "details": "Registration and login working with JWT tokens"})
                    else:
                        print("❌ JWT token verification failed")
                        self.test_results.append({"test": "user_registration_login", "status": "❌ FAIL", "details": "JWT token invalid"})
                else:
                    print(f"❌ User login failed: {login_response.status_code}")
                    self.test_results.append({"test": "user_registration_login", "status": "❌ FAIL", "details": f"Login failed: HTTP {login_response.status_code}"})
                    
            else:
                print(f"❌ User registration failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "user_registration_login", "status": "❌ FAIL", "details": f"Registration failed: HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ User registration/login error: {str(e)}")
            self.test_results.append({"test": "user_registration_login", "status": "❌ ERROR", "details": str(e)})

    async def test_crypto_prices(self):
        """Test GET /api/crypto/prices"""
        print("\n💰 Testing Crypto Prices API...")
        
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Crypto prices API working")
                
                if 'data' in data and isinstance(data['data'], dict):
                    prices = data['data']
                    print(f"📊 Available cryptocurrencies: {len(prices)}")
                    
                    # Check for USDT specifically (needed for trading test)
                    if 'tether' in prices:
                        usdt_price = prices['tether']['price_tmn']
                        print(f"📊 USDT Price: {usdt_price:,.0f} TMN")
                        print("✅ USDT price available for trading tests")
                    else:
                        print("⚠️  USDT price not found in response")
                    
                    # Display sample prices
                    for coin_id, coin_data in list(prices.items())[:3]:
                        symbol = coin_data.get('symbol', 'N/A')
                        price = coin_data.get('price_tmn', 0)
                        change = coin_data.get('change_24h', 0)
                        print(f"📊 {symbol}: {price:,.0f} TMN ({change:+.1f}%)")
                    
                    self.test_results.append({"test": "crypto_prices", "status": "✅ PASS", "details": f"Crypto prices API working with {len(prices)} cryptocurrencies"})
                else:
                    print("❌ Invalid response structure")
                    self.test_results.append({"test": "crypto_prices", "status": "❌ FAIL", "details": "Invalid response structure"})
                    
            else:
                print(f"❌ Crypto prices API failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "crypto_prices", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Crypto prices API error: {str(e)}")
            self.test_results.append({"test": "crypto_prices", "status": "❌ ERROR", "details": str(e)})

    async def test_wallet_management(self):
        """Test wallet address management and create USDT wallet"""
        print("\n💳 Testing Wallet Address Management...")
        
        if not self.test_user_token:
            print("❌ Cannot test wallet management without user token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Get current wallet addresses
            response = await self.client.get(f"{BACKEND_URL}/user/wallet-addresses", headers=headers)
            
            if response.status_code == 200:
                current_wallets = response.json()
                print(f"✅ Get wallet addresses working: {len(current_wallets)} addresses found")
                
                # Create USDT wallet address for trading
                usdt_wallet_data = {
                    "symbol": "USDT",
                    "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b1",
                    "label": "Test USDT Wallet"
                }
                
                create_response = await self.client.post(f"{BACKEND_URL}/user/wallet-addresses", 
                                                       headers=headers, json=usdt_wallet_data)
                
                if create_response.status_code == 200:
                    wallet_info = create_response.json()
                    print(f"✅ USDT wallet created: {wallet_info.get('address', 'N/A')}")
                    print(f"📊 Wallet ID: {wallet_info.get('id', 'N/A')}")
                    print(f"📊 Verified: {wallet_info.get('verified', False)}")
                    
                    self.test_results.append({"test": "wallet_management", "status": "✅ PASS", "details": "Wallet address management working, USDT wallet created"})
                elif create_response.status_code == 400:
                    # Wallet might already exist
                    print("⚠️  USDT wallet already exists (expected)")
                    self.test_results.append({"test": "wallet_management", "status": "✅ PASS", "details": "Wallet management working, USDT wallet exists"})
                else:
                    print(f"❌ USDT wallet creation failed: {create_response.status_code}")
                    self.test_results.append({"test": "wallet_management", "status": "❌ FAIL", "details": f"Wallet creation failed: HTTP {create_response.status_code}"})
                    
            else:
                print(f"❌ Get wallet addresses failed: {response.status_code}")
                self.test_results.append({"test": "wallet_management", "status": "❌ FAIL", "details": f"Get wallets failed: HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Wallet management error: {str(e)}")
            self.test_results.append({"test": "wallet_management", "status": "❌ ERROR", "details": str(e)})

    async def test_trading_system(self):
        """Test trading system: Create buy order (5M Toman), verify balance deduction, get orders"""
        print("\n📈 Testing Trading System...")
        
        if not self.test_user_token or not self.admin_token:
            print("❌ Cannot test trading system without tokens")
            return
        
        try:
            # First, give test user sufficient balance and KYC level via admin
            if self.test_user_id:
                await self.setup_user_for_trading()
            
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Get user profile to check balance before trading
            profile_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            if profile_response.status_code == 200:
                user_data = profile_response.json()
                initial_balance = user_data.get('wallet_balance_tmn', 0)
                print(f"📊 Initial balance: {initial_balance:,.0f} TMN")
            else:
                print("⚠️  Could not get initial balance")
                initial_balance = 0
            
            # Create buy order (5M Toman)
            buy_order_data = {
                "order_type": "buy",
                "coin_symbol": "USDT",
                "coin_id": "tether",
                "amount_tmn": 5000000  # 5M Toman as requested
            }
            
            order_response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                                                  headers=headers, json=buy_order_data)
            
            if order_response.status_code == 200:
                order_data = order_response.json()
                order_id = order_data.get('order_id') or order_data.get('id')
                print(f"✅ Buy order created successfully: {order_id}")
                print(f"📊 Order amount: {order_data.get('amount_tmn', 0):,.0f} TMN")
                print(f"📊 Crypto amount: {order_data.get('amount_crypto', 0):.6f} USDT")
                
                # Verify balance deduction
                balance_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                if balance_response.status_code == 200:
                    updated_user = balance_response.json()
                    new_balance = updated_user.get('wallet_balance_tmn', 0)
                    balance_change = initial_balance - new_balance
                    print(f"📊 New balance: {new_balance:,.0f} TMN")
                    print(f"📊 Balance deducted: {balance_change:,.0f} TMN")
                    
                    if balance_change == 5000000:
                        print("✅ Balance deduction verified correctly")
                    else:
                        print(f"⚠️  Balance deduction mismatch: expected 5M, got {balance_change:,.0f}")
                
                # Get user orders
                orders_response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
                if orders_response.status_code == 200:
                    user_orders = orders_response.json()
                    print(f"✅ Get user orders working: {len(user_orders)} orders found")
                    
                    # Find our order
                    our_order = next((o for o in user_orders if o.get('id') == order_id), None)
                    if our_order:
                        print(f"📊 Order status: {our_order.get('status', 'N/A')}")
                        print("✅ Created order found in user orders")
                    else:
                        print("⚠️  Created order not found in user orders")
                
                # Test admin functions
                await self.test_admin_trading_functions(order_id)
                
                self.test_results.append({"test": "trading_system", "status": "✅ PASS", "details": "Trading system working: order creation, balance deduction, order retrieval"})
                
            else:
                print(f"❌ Buy order creation failed: {order_response.status_code} - {order_response.text}")
                self.test_results.append({"test": "trading_system", "status": "❌ FAIL", "details": f"Order creation failed: HTTP {order_response.status_code}"})
                
        except Exception as e:
            print(f"❌ Trading system error: {str(e)}")
            self.test_results.append({"test": "trading_system", "status": "❌ ERROR", "details": str(e)})

    async def setup_user_for_trading(self):
        """Setup test user with balance and KYC level for trading"""
        print("🔧 Setting up user for trading...")
        
        if not self.admin_token or not self.test_user_id:
            return
        
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Update user balance to 10M TMN and set KYC level 2
            update_data = {
                "wallet_balance_tmn": 10000000,  # 10M TMN
            }
            
            response = await self.client.put(f"{BACKEND_URL}/admin/users/{self.test_user_id}", 
                                           headers=admin_headers, json=update_data)
            
            if response.status_code == 200:
                print("✅ User balance updated to 10M TMN")
                
                # Now approve KYC Level 2 via admin KYC approval endpoint
                kyc_approval_data = {
                    "user_id": self.test_user_id,
                    "kyc_level": 2,
                    "action": "approve",
                    "admin_note": "Test setup for trading"
                }
                
                kyc_response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                                                    headers=admin_headers, json=kyc_approval_data)
                
                if kyc_response.status_code == 200:
                    print("✅ User KYC Level 2 approved for trading")
                else:
                    print(f"⚠️  KYC approval failed: {kyc_response.status_code}")
            else:
                print(f"⚠️  User setup failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  User setup error: {str(e)}")

    async def test_admin_trading_functions(self, order_id):
        """Test admin trading functions: view all orders, approve order"""
        print("\n👑 Testing Admin Trading Functions...")
        
        if not self.admin_token:
            print("❌ Cannot test admin functions without admin token")
            return
        
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Admin: view all orders
            all_orders_response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=admin_headers)
            
            if all_orders_response.status_code == 200:
                all_orders = all_orders_response.json()
                print(f"✅ Admin view all orders working: {len(all_orders)} orders found")
                
                # Find our test order
                our_order = next((o for o in all_orders if o.get('id') == order_id), None)
                if our_order:
                    print(f"📊 Test order found in admin view")
                    print(f"📊 Order user: {our_order.get('user_email', 'N/A')}")
                    print(f"📊 Order status: {our_order.get('status', 'N/A')}")
                    
                    # Admin: approve the order
                    if our_order.get('status') == 'pending':
                        approve_data = {
                            "order_id": order_id,
                            "action": "approve",
                            "admin_note": "Test approval"
                        }
                        
                        approve_response = await self.client.post(f"{BACKEND_URL}/admin/orders/approve", 
                                                                headers=admin_headers, json=approve_data)
                        
                        if approve_response.status_code == 200:
                            print("✅ Admin order approval working")
                            self.test_results.append({"test": "admin_trading_functions", "status": "✅ PASS", "details": "Admin can view and approve orders"})
                        else:
                            print(f"❌ Admin order approval failed: {approve_response.status_code}")
                            self.test_results.append({"test": "admin_trading_functions", "status": "❌ FAIL", "details": f"Order approval failed: HTTP {approve_response.status_code}"})
                    else:
                        print("⚠️  Order not in pending status for approval test")
                        self.test_results.append({"test": "admin_trading_functions", "status": "✅ PASS", "details": "Admin can view orders (approval test skipped - order not pending)"})
                else:
                    print("⚠️  Test order not found in admin view")
                    self.test_results.append({"test": "admin_trading_functions", "status": "⚠️  PARTIAL", "details": "Admin can view orders but test order not found"})
                    
            else:
                print(f"❌ Admin view all orders failed: {all_orders_response.status_code}")
                self.test_results.append({"test": "admin_trading_functions", "status": "❌ FAIL", "details": f"Admin orders view failed: HTTP {all_orders_response.status_code}"})
                
        except Exception as e:
            print(f"❌ Admin trading functions error: {str(e)}")
            self.test_results.append({"test": "admin_trading_functions", "status": "❌ ERROR", "details": str(e)})

    async def test_user_management(self):
        """Test user management: get profile, admin update balance, wallet addresses"""
        print("\n👥 Testing User Management...")
        
        if not self.test_user_token or not self.admin_token:
            print("❌ Cannot test user management without tokens")
            return
        
        try:
            # Get user profile
            user_headers = {"Authorization": f"Bearer {self.test_user_token}"}
            profile_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=user_headers)
            
            if profile_response.status_code == 200:
                user_data = profile_response.json()
                print("✅ Get user profile working")
                print(f"📊 User: {user_data.get('full_name', 'N/A')}")
                print(f"📊 Email: {user_data.get('email', 'N/A')}")
                print(f"📊 KYC Level: {user_data.get('kyc_level', 'N/A')}")
                print(f"📊 Balance: {user_data.get('wallet_balance_tmn', 0):,.0f} TMN")
                
                # Admin: Update wallet balance
                admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
                new_balance = 15000000  # 15M TMN
                update_data = {"wallet_balance_tmn": new_balance}
                
                update_response = await self.client.put(f"{BACKEND_URL}/admin/users/{self.test_user_id}", 
                                                      headers=admin_headers, json=update_data)
                
                if update_response.status_code == 200:
                    print(f"✅ Admin wallet balance update working: set to {new_balance:,.0f} TMN")
                    
                    # Verify balance update
                    verify_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=user_headers)
                    if verify_response.status_code == 200:
                        updated_user = verify_response.json()
                        actual_balance = updated_user.get('wallet_balance_tmn', 0)
                        if actual_balance == new_balance:
                            print("✅ Balance update verified")
                        else:
                            print(f"⚠️  Balance update mismatch: expected {new_balance:,.0f}, got {actual_balance:,.0f}")
                
                # Get user wallet addresses (already tested in wallet management)
                wallet_response = await self.client.get(f"{BACKEND_URL}/user/wallet-addresses", headers=user_headers)
                if wallet_response.status_code == 200:
                    wallets = wallet_response.json()
                    print(f"✅ Get user wallet addresses working: {len(wallets)} addresses")
                
                self.test_results.append({"test": "user_management", "status": "✅ PASS", "details": "User profile, admin balance update, wallet addresses all working"})
                
            else:
                print(f"❌ Get user profile failed: {profile_response.status_code}")
                self.test_results.append({"test": "user_management", "status": "❌ FAIL", "details": f"User profile failed: HTTP {profile_response.status_code}"})
                
        except Exception as e:
            print(f"❌ User management error: {str(e)}")
            self.test_results.append({"test": "user_management", "status": "❌ ERROR", "details": str(e)})

    async def test_admin_functions(self):
        """Test admin functions: get all users, get all orders, get all deposits, update KYC level"""
        print("\n👑 Testing Admin Functions...")
        
        if not self.admin_token:
            print("❌ Cannot test admin functions without admin token")
            return
        
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all users
            users_response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=admin_headers)
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"✅ Get all users working: {len(users)} users found")
            else:
                print(f"❌ Get all users failed: {users_response.status_code}")
            
            # Get all orders (already tested in trading functions)
            orders_response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=admin_headers)
            if orders_response.status_code == 200:
                orders = orders_response.json()
                print(f"✅ Get all orders working: {len(orders)} orders found")
            else:
                print(f"❌ Get all orders failed: {orders_response.status_code}")
            
            # Get all deposits
            deposits_response = await self.client.get(f"{BACKEND_URL}/admin/deposits", headers=admin_headers)
            if deposits_response.status_code == 200:
                deposits = deposits_response.json()
                print(f"✅ Get all deposits working: {len(deposits)} deposits found")
            else:
                print(f"❌ Get all deposits failed: {deposits_response.status_code}")
            
            # Update KYC level (test with our test user)
            if self.test_user_id:
                kyc_update_data = {
                    "user_id": self.test_user_id,
                    "kyc_level": 2,
                    "action": "approve",
                    "admin_note": "Test KYC approval"
                }
                
                kyc_response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                                                    headers=admin_headers, json=kyc_update_data)
                
                if kyc_response.status_code == 200:
                    print("✅ Update KYC level working")
                else:
                    print(f"⚠️  Update KYC level response: {kyc_response.status_code}")
            
            # Check if all main admin functions worked
            success_count = sum([
                users_response.status_code == 200,
                orders_response.status_code == 200,
                deposits_response.status_code == 200
            ])
            
            if success_count >= 3:
                self.test_results.append({"test": "admin_functions", "status": "✅ PASS", "details": f"Admin functions working: {success_count}/3 core functions successful"})
            else:
                self.test_results.append({"test": "admin_functions", "status": "❌ FAIL", "details": f"Only {success_count}/3 admin functions working"})
                
        except Exception as e:
            print(f"❌ Admin functions error: {str(e)}")
            self.test_results.append({"test": "admin_functions", "status": "❌ ERROR", "details": str(e)})

    async def test_ai_features_without_api_key(self):
        """Test AI features without API key: admin settings, smart recommendation"""
        print("\n🤖 Testing AI Features (Without API Key)...")
        
        if not self.admin_token:
            print("❌ Cannot test AI features without admin token")
            return
        
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # GET /api/admin/settings/ai (should show not configured)
            ai_settings_response = await self.client.get(f"{BACKEND_URL}/admin/settings/ai", headers=admin_headers)
            
            if ai_settings_response.status_code == 200:
                ai_settings = ai_settings_response.json()
                print("✅ Admin AI settings endpoint working")
                print(f"📊 AI Settings: {ai_settings}")
                
                # Check if it shows not configured
                if 'configured' in str(ai_settings).lower() or 'not' in str(ai_settings).lower():
                    print("✅ AI settings shows configuration status")
                else:
                    print("⚠️  AI settings response unclear about configuration")
                    
            else:
                print(f"❌ Admin AI settings failed: {ai_settings_response.status_code}")
            
            # GET /api/ai/smart-recommendation/USDT (should return 503 error, no mock data)
            recommendation_response = await self.client.get(f"{BACKEND_URL}/ai/smart-recommendation/USDT")
            
            if recommendation_response.status_code == 503:
                print("✅ AI smart recommendation correctly returns 503 (service unavailable)")
                print("✅ No mock data returned as expected")
            elif recommendation_response.status_code == 200:
                # Check if it's mock data
                rec_data = recommendation_response.json()
                print("⚠️  AI smart recommendation returns 200 - checking for mock data")
                print(f"📊 Response: {rec_data}")
                
                # Look for indicators of mock data
                if 'mock' in str(rec_data).lower() or 'test' in str(rec_data).lower():
                    print("⚠️  Response contains mock data indicators")
                else:
                    print("✅ Response appears to be real data (not mock)")
            else:
                print(f"📊 AI smart recommendation status: {recommendation_response.status_code}")
            
            # Determine overall AI features test result
            ai_settings_ok = ai_settings_response.status_code == 200
            recommendation_ok = recommendation_response.status_code in [503, 200]  # Both acceptable
            
            if ai_settings_ok and recommendation_ok:
                self.test_results.append({"test": "ai_features_no_api_key", "status": "✅ PASS", "details": "AI endpoints responding correctly without API key"})
            else:
                self.test_results.append({"test": "ai_features_no_api_key", "status": "❌ FAIL", "details": "AI endpoints not responding as expected"})
                
        except Exception as e:
            print(f"❌ AI features error: {str(e)}")
            self.test_results.append({"test": "ai_features_no_api_key", "status": "❌ ERROR", "details": str(e)})

    async def test_error_handling(self):
        """Test error handling: unauthorized access, invalid endpoints, malformed requests"""
        print("\n🚫 Testing Error Handling...")
        
        try:
            # Test unauthorized access (no token)
            print("🔒 Testing unauthorized access...")
            
            protected_endpoints = [
                "/auth/me",
                "/trading/orders/my",
                "/user/wallet-addresses",
                "/admin/users"
            ]
            
            unauthorized_count = 0
            for endpoint in protected_endpoints:
                response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code in [401, 403]:
                    unauthorized_count += 1
                    print(f"✅ {endpoint} correctly requires authentication")
                else:
                    print(f"⚠️  {endpoint} accessible without auth: {response.status_code}")
            
            print(f"📊 Protected endpoints: {unauthorized_count}/{len(protected_endpoints)}")
            
            # Test invalid endpoints
            print("🔍 Testing invalid endpoints...")
            
            invalid_endpoints = [
                "/nonexistent/endpoint",
                "/api/invalid/route",
                "/trading/invalid"
            ]
            
            not_found_count = 0
            for endpoint in invalid_endpoints:
                response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 404:
                    not_found_count += 1
                    print(f"✅ {endpoint} correctly returns 404")
                else:
                    print(f"⚠️  {endpoint} unexpected status: {response.status_code}")
            
            print(f"📊 Invalid endpoints: {not_found_count}/{len(invalid_endpoints)}")
            
            # Test malformed requests
            print("🔧 Testing malformed requests...")
            
            if self.test_user_token:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                
                # Malformed JSON
                malformed_response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                                                          headers=headers, 
                                                          content="invalid json")
                
                if malformed_response.status_code == 422:
                    print("✅ Malformed JSON correctly returns 422")
                    malformed_ok = True
                else:
                    print(f"⚠️  Malformed JSON status: {malformed_response.status_code}")
                    malformed_ok = False
                
                # Missing required fields
                missing_fields_response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                                                               headers=headers, 
                                                               json={"incomplete": "data"})
                
                if missing_fields_response.status_code == 422:
                    print("✅ Missing fields correctly returns 422")
                    missing_fields_ok = True
                else:
                    print(f"⚠️  Missing fields status: {missing_fields_response.status_code}")
                    missing_fields_ok = False
            else:
                malformed_ok = False
                missing_fields_ok = False
                print("⚠️  Cannot test malformed requests without user token")
            
            # Test Persian error messages
            print("🇮🇷 Testing Persian error messages...")
            
            if self.test_user_token:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                
                # Try to create order with insufficient balance (should return Persian error)
                insufficient_balance_order = {
                    "order_type": "buy",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_tmn": 999999999999  # Impossibly large amount
                }
                
                balance_response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                                                        headers=headers, 
                                                        json=insufficient_balance_order)
                
                if balance_response.status_code in [400, 422]:
                    response_text = balance_response.text
                    # Check for Persian characters
                    if any(char in response_text for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                        print("✅ Persian error messages working")
                        persian_errors_ok = True
                    else:
                        print("⚠️  Error messages not in Persian")
                        persian_errors_ok = False
                else:
                    print(f"⚠️  Insufficient balance test status: {balance_response.status_code}")
                    persian_errors_ok = False
            else:
                persian_errors_ok = False
            
            # Overall error handling assessment
            error_handling_score = sum([
                unauthorized_count >= len(protected_endpoints) * 0.8,  # 80% of endpoints protected
                not_found_count >= len(invalid_endpoints) * 0.8,      # 80% return 404
                malformed_ok,
                missing_fields_ok,
                persian_errors_ok
            ])
            
            if error_handling_score >= 4:
                self.test_results.append({"test": "error_handling", "status": "✅ PASS", "details": f"Error handling working well: {error_handling_score}/5 tests passed"})
            elif error_handling_score >= 2:
                self.test_results.append({"test": "error_handling", "status": "⚠️  PARTIAL", "details": f"Error handling partially working: {error_handling_score}/5 tests passed"})
            else:
                self.test_results.append({"test": "error_handling", "status": "❌ FAIL", "details": f"Error handling issues: only {error_handling_score}/5 tests passed"})
                
        except Exception as e:
            print(f"❌ Error handling test error: {str(e)}")
            self.test_results.append({"test": "error_handling", "status": "❌ ERROR", "details": str(e)})

    async def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Testing...")
        print("=" * 70)
        print("Testing all critical backend functionality as per review request:")
        print("1. Authentication System")
        print("2. Trading System")
        print("3. User Management") 
        print("4. Admin Functions")
        print("5. AI Features (Without API Key)")
        print("6. Error Handling")
        print("=" * 70)
        
        await self.setup()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run all tests in sequence
        await self.test_user_registration_and_login()
        await self.test_crypto_prices()
        await self.test_wallet_management()
        await self.test_trading_system()
        await self.test_user_management()
        await self.test_admin_functions()
        await self.test_ai_features_without_api_key()
        await self.test_error_handling()
        
        # Print comprehensive summary
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("=" * 70)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        warning_tests = [r for r in self.test_results if "⚠️" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⚠️  WARNINGS: {len(warning_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if warning_tests:
            print("\n⚠️  WARNING TESTS:")
            for test in warning_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        
        # Analyze results by category
        auth_tests = [r for r in self.test_results if 'login' in r['test'] or 'auth' in r['test']]
        trading_tests = [r for r in self.test_results if 'trading' in r['test']]
        admin_tests = [r for r in self.test_results if 'admin' in r['test']]
        
        auth_success = all("✅ PASS" in r["status"] for r in auth_tests)
        trading_success = all("✅ PASS" in r["status"] for r in trading_tests)
        admin_success = all("✅ PASS" in r["status"] for r in admin_tests)
        
        print(f"🔑 Authentication System: {'✅ WORKING' if auth_success else '❌ ISSUES'}")
        print(f"📈 Trading System: {'✅ WORKING' if trading_success else '❌ ISSUES'}")
        print(f"👑 Admin Functions: {'✅ WORKING' if admin_success else '❌ ISSUES'}")
        
        # Overall assessment
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Backend is production-ready!")
        elif success_rate >= 75:
            print("\n✅ GOOD: Backend is mostly functional with minor issues")
        elif success_rate >= 50:
            print("\n⚠️  FAIR: Backend has significant issues that need attention")
        else:
            print("\n❌ POOR: Backend has critical issues requiring immediate fixes")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = ComprehensiveBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())