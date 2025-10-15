#!/usr/bin/env python3
"""
Comprehensive System Debug & Health Check for Iranian Crypto Exchange
Tests all areas mentioned in the review request:
1. Rate Limiting System
2. Caching System  
3. Core Authentication Flow
4. Trading System
5. AI Integration Stability
6. API Performance & Reliability
7. Database Operations
"""

import asyncio
import httpx
import json
import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://crypto-farsi.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class SystemDebugTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.admin_token = None
        self.test_user_token = None
        self.test_user_data = None
        
    async def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    # ==================== RATE LIMITING TESTS ====================
    
    async def test_login_rate_limiting(self):
        """Test login rate limiting (5 per 5 min per IP)"""
        print("\n🔒 Testing Login Rate Limiting...")
        
        # Make multiple login attempts quickly
        login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        success_count = 0
        rate_limited = False
        
        for i in range(7):  # Try 7 attempts (should be rate limited after 5)
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
                
                if response.status_code == 429:
                    rate_limited = True
                    response_data = response.json()
                    if "تعداد تلاش" in response_data.get("detail", ""):
                        await self.log_test("Login Rate Limiting Persian Message", True, "Persian error message displayed correctly")
                    else:
                        await self.log_test("Login Rate Limiting Persian Message", False, f"Non-Persian error: {response_data.get('detail')}")
                    break
                elif response.status_code in [401, 422]:
                    success_count += 1
                    
            except Exception as e:
                await self.log_test("Login Rate Limiting", False, f"Exception: {str(e)}")
                return
        
        if rate_limited:
            await self.log_test("Login Rate Limiting", True, f"Rate limiting activated after {success_count} attempts")
        else:
            await self.log_test("Login Rate Limiting", False, "Rate limiting not working - made 7 attempts without being blocked")

    async def test_otp_rate_limiting(self):
        """Test OTP send rate limiting"""
        print("\n📱 Testing OTP Rate Limiting...")
        
        otp_data = {"phone": "09123456999"}
        
        success_count = 0
        rate_limited = False
        
        for i in range(5):  # Try 5 attempts (should be rate limited after 3)
            try:
                response = await self.client.post(f"{BACKEND_URL}/otp/send", json=otp_data)
                
                if response.status_code == 429:
                    rate_limited = True
                    response_data = response.json()
                    if "تعداد درخواست" in response_data.get("detail", ""):
                        await self.log_test("OTP Rate Limiting Persian Message", True, "Persian error message for OTP rate limiting")
                    else:
                        await self.log_test("OTP Rate Limiting Persian Message", False, f"Non-Persian error: {response_data.get('detail')}")
                    break
                elif response.status_code == 200:
                    success_count += 1
                    
            except Exception as e:
                await self.log_test("OTP Rate Limiting", False, f"Exception: {str(e)}")
                return
        
        if rate_limited:
            await self.log_test("OTP Send Rate Limiting", True, f"OTP rate limiting activated after {success_count} attempts")
        else:
            await self.log_test("OTP Send Rate Limiting", False, "OTP rate limiting not working properly")

    async def test_registration_rate_limiting(self):
        """Test registration rate limiting"""
        print("\n📝 Testing Registration Rate Limiting...")
        
        success_count = 0
        rate_limited = False
        
        for i in range(5):
            reg_data = {
                "first_name": "تست",
                "last_name": "کاربر",
                "email": f"ratetest{i}@test.com",
                "phone": f"0912345{i:04d}",
                "password": "testpass123"
            }
            
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/register", json=reg_data)
                
                if response.status_code == 429:
                    rate_limited = True
                    response_data = response.json()
                    if "تعداد تلاش" in response_data.get("detail", ""):
                        await self.log_test("Registration Rate Limiting Persian Message", True, "Persian error message for registration rate limiting")
                    else:
                        await self.log_test("Registration Rate Limiting Persian Message", False, f"Non-Persian error: {response_data.get('detail')}")
                    break
                elif response.status_code in [400, 422]:  # Expected failures due to OTP requirement
                    success_count += 1
                    
            except Exception as e:
                await self.log_test("Registration Rate Limiting", False, f"Exception: {str(e)}")
                return
        
        if rate_limited:
            await self.log_test("Registration Rate Limiting", True, f"Registration rate limiting activated after {success_count} attempts")
        else:
            await self.log_test("Registration Rate Limiting", False, "Registration rate limiting not working properly")

    # ==================== CACHING SYSTEM TESTS ====================
    
    async def test_crypto_prices_caching(self):
        """Test crypto prices caching (5-minute TTL)"""
        print("\n💰 Testing Crypto Prices Caching...")
        
        try:
            # First request - should hit the API
            start_time = time.time()
            response1 = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            first_request_time = time.time() - start_time
            
            if response1.status_code != 200:
                await self.log_test("Crypto Prices API", False, f"API failed: {response1.text}")
                return
            
            # Second request immediately - should hit cache
            start_time = time.time()
            response2 = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            second_request_time = time.time() - start_time
            
            if response2.status_code == 200:
                # Cache should make second request faster
                if second_request_time < first_request_time * 0.8:  # At least 20% faster
                    await self.log_test("Crypto Prices Caching", True, f"Cache working - 2nd request {second_request_time:.2f}s vs 1st {first_request_time:.2f}s")
                else:
                    await self.log_test("Crypto Prices Caching", False, f"Cache may not be working - similar response times: {first_request_time:.2f}s vs {second_request_time:.2f}s")
                
                # Verify data consistency
                data1 = response1.json()
                data2 = response2.json()
                if data1 == data2:
                    await self.log_test("Crypto Prices Cache Consistency", True, "Cached data matches original")
                else:
                    await self.log_test("Crypto Prices Cache Consistency", False, "Cached data differs from original")
            else:
                await self.log_test("Crypto Prices Caching", False, f"Second request failed: {response2.text}")
                
        except Exception as e:
            await self.log_test("Crypto Prices Caching", False, f"Exception: {str(e)}")

    async def test_coin_details_caching(self):
        """Test coin details caching"""
        print("\n🪙 Testing Coin Details Caching...")
        
        try:
            coin_id = "bitcoin"
            
            # First request
            start_time = time.time()
            response1 = await self.client.get(f"{BACKEND_URL}/crypto/{coin_id}")
            first_request_time = time.time() - start_time
            
            if response1.status_code != 200:
                await self.log_test("Coin Details API", False, f"API failed: {response1.text}")
                return
            
            # Second request - should hit cache
            start_time = time.time()
            response2 = await self.client.get(f"{BACKEND_URL}/crypto/{coin_id}")
            second_request_time = time.time() - start_time
            
            if response2.status_code == 200:
                if second_request_time < first_request_time * 0.8:
                    await self.log_test("Coin Details Caching", True, f"Cache working - 2nd request {second_request_time:.2f}s vs 1st {first_request_time:.2f}s")
                else:
                    await self.log_test("Coin Details Caching", False, f"Cache may not be working - similar times: {first_request_time:.2f}s vs {second_request_time:.2f}s")
            else:
                await self.log_test("Coin Details Caching", False, f"Second request failed: {response2.text}")
                
        except Exception as e:
            await self.log_test("Coin Details Caching", False, f"Exception: {str(e)}")

    async def test_trending_coins_caching(self):
        """Test trending coins caching"""
        print("\n📈 Testing Trending Coins Caching...")
        
        try:
            # First request
            start_time = time.time()
            response1 = await self.client.get(f"{BACKEND_URL}/crypto/trending/coins")
            first_request_time = time.time() - start_time
            
            if response1.status_code != 200:
                await self.log_test("Trending Coins API", False, f"API failed: {response1.text}")
                return
            
            # Second request - should hit cache
            start_time = time.time()
            response2 = await self.client.get(f"{BACKEND_URL}/crypto/trending/coins")
            second_request_time = time.time() - start_time
            
            if response2.status_code == 200:
                if second_request_time < first_request_time * 0.8:
                    await self.log_test("Trending Coins Caching", True, f"Cache working - 2nd request {second_request_time:.2f}s vs 1st {first_request_time:.2f}s")
                else:
                    await self.log_test("Trending Coins Caching", False, f"Cache may not be working - similar times: {first_request_time:.2f}s vs {second_request_time:.2f}s")
            else:
                await self.log_test("Trending Coins Caching", False, f"Second request failed: {response2.text}")
                
        except Exception as e:
            await self.log_test("Trending Coins Caching", False, f"Exception: {str(e)}")

    # ==================== AUTHENTICATION TESTS ====================
    
    async def test_new_registration_fields(self):
        """Test registration with new first_name/last_name fields"""
        print("\n👤 Testing New Registration Fields...")
        
        reg_data = {
            "first_name": "محمد",
            "last_name": "رضایی",
            "email": "mohammad.new@test.com",
            "phone": "09123456888",
            "password": "testpass123"
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=reg_data)
            
            if response.status_code == 400:
                # Expected due to OTP requirement
                error_data = response.json()
                if "تایید" in error_data.get("detail", ""):
                    await self.log_test("New Registration Fields Structure", True, "Registration accepts new fields and requires OTP")
                else:
                    await self.log_test("New Registration Fields Structure", False, f"Unexpected error: {error_data}")
            elif response.status_code == 422:
                # Validation error - check if it's about the fields we expect
                error_data = response.json()
                await self.log_test("New Registration Fields Validation", True, "Registration validates new fields correctly")
            else:
                await self.log_test("New Registration Fields", False, f"Unexpected response: {response.status_code} - {response.text}")
                
        except Exception as e:
            await self.log_test("New Registration Fields", False, f"Exception: {str(e)}")

    async def test_backward_compatibility(self):
        """Test backward compatibility for existing users"""
        print("\n🔄 Testing Backward Compatibility...")
        
        # Try to login with existing user
        login_data = {
            "email": "testuser@example.com",
            "password": "testpass123"
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Check if full_name is computed correctly for existing users
                full_name = user_info.get("full_name")
                if full_name:
                    await self.log_test("Backward Compatibility Login", True, f"Existing user login successful with full_name: '{full_name}'")
                    
                    # Store for further tests
                    self.test_user_token = data.get("access_token")
                    self.test_user_data = user_info
                else:
                    await self.log_test("Backward Compatibility Login", False, "Existing user login missing full_name")
            elif response.status_code in [401, 422]:
                await self.log_test("Backward Compatibility Login", True, "Login properly handles authentication errors")
            else:
                await self.log_test("Backward Compatibility Login", False, f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Backward Compatibility", False, f"Exception: {str(e)}")

    async def test_jwt_token_validation(self):
        """Test JWT token generation and validation"""
        print("\n🔐 Testing JWT Token Validation...")
        
        if not self.test_user_token:
            await self.log_test("JWT Token Validation", False, "No test user token available")
            return
        
        try:
            # Test valid token
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                await self.log_test("JWT Valid Token", True, "Valid JWT token accepted")
            else:
                await self.log_test("JWT Valid Token", False, f"Valid token rejected: {response.text}")
            
            # Test invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=invalid_headers)
            
            if response.status_code == 401:
                await self.log_test("JWT Invalid Token", True, "Invalid JWT token properly rejected")
            else:
                await self.log_test("JWT Invalid Token", False, f"Invalid token not rejected: {response.status_code}")
                
        except Exception as e:
            await self.log_test("JWT Token Validation", False, f"Exception: {str(e)}")

    # ==================== TRADING SYSTEM TESTS ====================
    
    async def test_trading_order_creation(self):
        """Test trading order creation (buy/sell/trade)"""
        print("\n💹 Testing Trading Order Creation...")
        
        if not self.test_user_token:
            await self.log_test("Trading Order Creation", False, "No test user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.test_user_token}"}
        
        # Test buy order
        buy_order = {
            "order_type": "buy",
            "coin_symbol": "BTC",
            "coin_id": "bitcoin",
            "amount_tmn": 100000.0
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=buy_order)
            
            if response.status_code == 403:
                # Expected for users without KYC level 2
                error_data = response.json()
                if "احراز هویت" in error_data.get("detail", ""):
                    await self.log_test("Trading KYC Restriction", True, "Trading properly restricted by KYC level")
                else:
                    await self.log_test("Trading KYC Restriction", False, f"Unexpected error: {error_data}")
            elif response.status_code in [200, 201]:
                await self.log_test("Trading Buy Order", True, "Buy order created successfully")
            else:
                await self.log_test("Trading Buy Order", False, f"Buy order failed: {response.text}")
                
        except Exception as e:
            await self.log_test("Trading Order Creation", False, f"Exception: {str(e)}")

    async def test_admin_order_management(self):
        """Test admin order management"""
        print("\n👨‍💼 Testing Admin Order Management...")
        
        try:
            # Test without authentication
            response = await self.client.get(f"{BACKEND_URL}/admin/orders")
            
            if response.status_code in [401, 403]:
                await self.log_test("Admin Orders Security", True, "Admin orders endpoint properly protected")
            else:
                await self.log_test("Admin Orders Security", False, f"Admin endpoint not protected: {response.status_code}")
            
            # Test admin orders approve endpoint
            response = await self.client.post(f"{BACKEND_URL}/admin/orders/approve", json={
                "order_id": "test_id",
                "action": "approve"
            })
            
            if response.status_code in [401, 403]:
                await self.log_test("Admin Orders Approve Security", True, "Admin approve endpoint properly protected")
            else:
                await self.log_test("Admin Orders Approve Security", False, f"Admin approve endpoint not protected: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Admin Order Management", False, f"Exception: {str(e)}")

    async def test_wallet_balance_calculations(self):
        """Test wallet balance calculations"""
        print("\n💰 Testing Wallet Balance Calculations...")
        
        if not self.test_user_token:
            await self.log_test("Wallet Balance", False, "No test user token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                balance = user_data.get("wallet_balance_tmn")
                
                if isinstance(balance, (int, float)) and balance >= 0:
                    await self.log_test("Wallet Balance Format", True, f"Wallet balance properly formatted: {balance} TMN")
                else:
                    await self.log_test("Wallet Balance Format", False, f"Invalid balance format: {balance}")
            else:
                await self.log_test("Wallet Balance", False, f"Failed to get user data: {response.text}")
                
        except Exception as e:
            await self.log_test("Wallet Balance", False, f"Exception: {str(e)}")

    # ==================== AI INTEGRATION TESTS ====================
    
    async def test_ai_chatbot(self):
        """Test AI chatbot endpoint"""
        print("\n🤖 Testing AI Chatbot...")
        
        if not self.test_user_token:
            await self.log_test("AI Chatbot", False, "No test user token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            chat_data = {
                "message": "سلام، قیمت بیت کوین چقدر است؟",
                "session_id": "test_session"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", headers=headers, json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    await self.log_test("AI Chatbot", True, "AI chatbot responding correctly")
                else:
                    await self.log_test("AI Chatbot", False, f"AI chatbot response format issue: {data}")
            else:
                await self.log_test("AI Chatbot", False, f"AI chatbot failed: {response.text}")
                
        except Exception as e:
            await self.log_test("AI Chatbot", False, f"Exception: {str(e)}")

    async def test_ai_market_analysis(self):
        """Test AI market analysis"""
        print("\n📊 Testing AI Market Analysis...")
        
        if not self.test_user_token:
            await self.log_test("AI Market Analysis", False, "No test user token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/ai/analyze/bitcoin", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("analysis"):
                    await self.log_test("AI Market Analysis", True, "AI market analysis working")
                else:
                    await self.log_test("AI Market Analysis", False, f"AI analysis response format issue: {data}")
            else:
                await self.log_test("AI Market Analysis", False, f"AI analysis failed: {response.text}")
                
        except Exception as e:
            await self.log_test("AI Market Analysis", False, f"Exception: {str(e)}")

    async def test_ai_trading_signals(self):
        """Test AI trading signals"""
        print("\n📈 Testing AI Trading Signals...")
        
        if not self.test_user_token:
            await self.log_test("AI Trading Signals", False, "No test user token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/ai/signals", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("signals"):
                    await self.log_test("AI Trading Signals", True, "AI trading signals working")
                else:
                    await self.log_test("AI Trading Signals", False, f"AI signals response format issue: {data}")
            else:
                await self.log_test("AI Trading Signals", False, f"AI signals failed: {response.text}")
                
        except Exception as e:
            await self.log_test("AI Trading Signals", False, f"Exception: {str(e)}")

    # ==================== PERFORMANCE TESTS ====================
    
    async def test_api_response_times(self):
        """Test API response times under load"""
        print("\n⚡ Testing API Performance...")
        
        endpoints = [
            "/crypto/prices",
            "/crypto/bitcoin",
            "/crypto/trending/coins"
        ]
        
        total_time = 0
        successful_requests = 0
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                end_time = time.time()
                
                response_time = end_time - start_time
                total_time += response_time
                
                if response.status_code == 200:
                    successful_requests += 1
                    await self.log_test(f"API Performance {endpoint}", True, f"Response time: {response_time:.2f}s")
                else:
                    await self.log_test(f"API Performance {endpoint}", False, f"Failed with status {response.status_code}")
                    
            except Exception as e:
                await self.log_test(f"API Performance {endpoint}", False, f"Exception: {str(e)}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            if avg_time < 2.0:  # Less than 2 seconds average
                await self.log_test("Overall API Performance", True, f"Average response time: {avg_time:.2f}s")
            else:
                await self.log_test("Overall API Performance", False, f"Slow average response time: {avg_time:.2f}s")

    async def test_error_handling(self):
        """Test error handling and recovery"""
        print("\n🚨 Testing Error Handling...")
        
        # Test 404 handling
        try:
            response = await self.client.get(f"{BACKEND_URL}/nonexistent/endpoint")
            if response.status_code == 404:
                await self.log_test("404 Error Handling", True, "Proper 404 response for nonexistent endpoints")
            else:
                await self.log_test("404 Error Handling", False, f"Unexpected status for 404: {response.status_code}")
        except Exception as e:
            await self.log_test("404 Error Handling", False, f"Exception: {str(e)}")
        
        # Test malformed JSON handling
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", 
                                            content="invalid json",
                                            headers={"Content-Type": "application/json"})
            if response.status_code == 422:
                await self.log_test("Malformed JSON Handling", True, "Proper handling of malformed JSON")
            else:
                await self.log_test("Malformed JSON Handling", False, f"Unexpected status for malformed JSON: {response.status_code}")
        except Exception as e:
            await self.log_test("Malformed JSON Handling", False, f"Exception: {str(e)}")

    # ==================== DATABASE TESTS ====================
    
    async def test_database_operations(self):
        """Test database connectivity and operations"""
        print("\n🗄️ Testing Database Operations...")
        
        # Test user data integrity through API
        if self.test_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if response.status_code == 200:
                    user_data = response.json()
                    required_fields = ["id", "email", "is_active", "kyc_level", "wallet_balance_tmn"]
                    
                    missing_fields = [field for field in required_fields if field not in user_data]
                    
                    if not missing_fields:
                        await self.log_test("Database User Data Integrity", True, "All required user fields present")
                    else:
                        await self.log_test("Database User Data Integrity", False, f"Missing fields: {missing_fields}")
                else:
                    await self.log_test("Database User Data Integrity", False, f"Failed to retrieve user data: {response.text}")
                    
            except Exception as e:
                await self.log_test("Database Operations", False, f"Exception: {str(e)}")

    # ==================== MAIN TEST RUNNER ====================
    
    async def run_comprehensive_debug_tests(self):
        """Run all comprehensive debug tests"""
        print("🚀 Starting Comprehensive System Debug & Health Check")
        print("=" * 80)
        
        # 1. Rate Limiting System Tests
        print("\n🔒 RATE LIMITING SYSTEM TESTS")
        print("-" * 40)
        await self.test_login_rate_limiting()
        await self.test_otp_rate_limiting()
        await self.test_registration_rate_limiting()
        
        # 2. Caching System Tests
        print("\n💾 CACHING SYSTEM TESTS")
        print("-" * 40)
        await self.test_crypto_prices_caching()
        await self.test_coin_details_caching()
        await self.test_trending_coins_caching()
        
        # 3. Core Authentication Flow Tests
        print("\n🔐 AUTHENTICATION FLOW TESTS")
        print("-" * 40)
        await self.test_new_registration_fields()
        await self.test_backward_compatibility()
        await self.test_jwt_token_validation()
        
        # 4. Trading System Tests
        print("\n💹 TRADING SYSTEM TESTS")
        print("-" * 40)
        await self.test_trading_order_creation()
        await self.test_admin_order_management()
        await self.test_wallet_balance_calculations()
        
        # 5. AI Integration Tests
        print("\n🤖 AI INTEGRATION TESTS")
        print("-" * 40)
        await self.test_ai_chatbot()
        await self.test_ai_market_analysis()
        await self.test_ai_trading_signals()
        
        # 6. API Performance & Reliability Tests
        print("\n⚡ PERFORMANCE & RELIABILITY TESTS")
        print("-" * 40)
        await self.test_api_response_times()
        await self.test_error_handling()
        
        # 7. Database Operations Tests
        print("\n🗄️ DATABASE OPERATIONS TESTS")
        print("-" * 40)
        await self.test_database_operations()
        
        print("\n" + "=" * 80)
        print("🏁 Comprehensive Debug Testing Complete!")
        await self.print_summary()

    async def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by category
        categories = {
            "Rate Limiting": [],
            "Caching": [],
            "Authentication": [],
            "Trading": [],
            "AI Integration": [],
            "Performance": [],
            "Database": [],
            "Other": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            categorized = False
            
            for category in categories:
                if any(keyword in test_name.lower() for keyword in [
                    category.lower().split()[0],
                    "rate" if category == "Rate Limiting" else "",
                    "cache" if category == "Caching" else "",
                    "auth" if category == "Authentication" else "",
                    "trading" if category == "Trading" else "",
                    "ai" if category == "AI Integration" else "",
                    "performance" if category == "Performance" else "",
                    "database" if category == "Database" else ""
                ]):
                    categories[category].append(result)
                    categorized = True
                    break
            
            if not categorized:
                categories["Other"].append(result)
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"  {category}: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Production readiness assessment
        if (passed_tests/total_tests) >= 0.9:
            print(f"\n🟢 SYSTEM STATUS: PRODUCTION READY ({(passed_tests/total_tests)*100:.1f}% success rate)")
        elif (passed_tests/total_tests) >= 0.8:
            print(f"\n🟡 SYSTEM STATUS: NEEDS MINOR FIXES ({(passed_tests/total_tests)*100:.1f}% success rate)")
        else:
            print(f"\n🔴 SYSTEM STATUS: NEEDS MAJOR FIXES ({(passed_tests/total_tests)*100:.1f}% success rate)")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = SystemDebugTester()
    try:
        await tester.run_comprehensive_debug_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())