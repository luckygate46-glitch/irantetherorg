#!/usr/bin/env python3
"""
Focused Backend Health Check for Iranian Crypto Exchange
Addressing the authentication issues and testing core functionality
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import sys
import time
import random

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class FocusedBackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_user_token = None
        self.test_user_email = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up focused backend testing environment...")
        
        # Login as admin
        await self.login_admin()
        
        # Try to create test user with unique credentials
        await self.create_unique_test_user()
        
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
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False
    
    async def create_unique_test_user(self):
        """Create test user with unique credentials"""
        try:
            # Generate unique credentials
            timestamp = int(time.time())
            random_num = random.randint(1000, 9999)
            
            self.test_user_email = f"healthcheck.{timestamp}.{random_num}@example.com"
            test_phone = f"0912{random.randint(1000000, 9999999)}"
            
            test_user_data = {
                "first_name": "تست",
                "last_name": "کاربر",
                "email": self.test_user_email,
                "phone": test_phone,
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["access_token"]
                user_info = data["user"]
                print(f"✅ Test user created: {user_info.get('full_name', 'Test User')} ({self.test_user_email})")
                return True
            else:
                print(f"❌ Test user creation failed: {response.status_code} - {response.text}")
                
                # Try to use existing user if registration failed
                await self.try_existing_user()
                return False
                
        except Exception as e:
            print(f"❌ Test user creation error: {str(e)}")
            await self.try_existing_user()
            return False
    
    async def try_existing_user(self):
        """Try to login with existing test user"""
        try:
            # Try some common test user credentials
            test_credentials = [
                {"email": "testuser@example.com", "password": "testpass123"},
                {"email": "buyer1@test.com", "password": "test123"},
                {"email": "useragi.test.3565@example.com", "password": "testpass123"}
            ]
            
            for creds in test_credentials:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json=creds)
                if response.status_code == 200:
                    data = response.json()
                    self.test_user_token = data["access_token"]
                    self.test_user_email = creds["email"]
                    user_info = data["user"]
                    print(f"✅ Using existing test user: {user_info.get('full_name', 'Test User')} ({creds['email']})")
                    return True
            
            print("❌ Could not login with any existing test users")
            return False
            
        except Exception as e:
            print(f"❌ Existing user login error: {str(e)}")
            return False

    async def test_core_authentication(self):
        """Test core authentication functionality"""
        print("\n🔐 Testing Core Authentication...")
        
        test_results = []
        
        # Test 1: Admin login functionality
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    user = data["user"]
                    if user.get("is_admin"):
                        print("✅ Admin authentication working correctly")
                        test_results.append("✅ Admin Login")
                    else:
                        print("❌ Admin user does not have admin privileges")
                        test_results.append("❌ Admin Login")
                else:
                    print("❌ Admin login response missing required fields")
                    test_results.append("❌ Admin Login")
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                test_results.append("❌ Admin Login")
                
        except Exception as e:
            print(f"❌ Admin login test error: {str(e)}")
            test_results.append("❌ Admin Login")
        
        # Test 2: User authentication (if available)
        if self.test_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "email" in data:
                        print("✅ User authentication working correctly")
                        test_results.append("✅ User Auth")
                    else:
                        print("❌ User auth response incomplete")
                        test_results.append("❌ User Auth")
                else:
                    print(f"❌ User authentication failed: {response.status_code}")
                    test_results.append("❌ User Auth")
                    
            except Exception as e:
                print(f"❌ User auth test error: {str(e)}")
                test_results.append("❌ User Auth")
        else:
            print("⚠️ No test user available - skipping user auth test")
            test_results.append("⚠️ User Auth")
        
        # Test 3: JWT token validation
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                print("✅ JWT token validation working")
                test_results.append("✅ JWT Validation")
            else:
                print(f"❌ JWT validation failed: {response.status_code}")
                test_results.append("❌ JWT Validation")
                
        except Exception as e:
            print(f"❌ JWT validation test error: {str(e)}")
            test_results.append("❌ JWT Validation")
        
        # Test 4: Invalid credentials handling
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            })
            
            if response.status_code == 401:
                print("✅ Invalid credentials properly rejected")
                test_results.append("✅ Invalid Creds")
            else:
                print(f"❌ Invalid credentials handling incorrect: {response.status_code}")
                test_results.append("❌ Invalid Creds")
                
        except Exception as e:
            print(f"❌ Invalid credentials test error: {str(e)}")
            test_results.append("❌ Invalid Creds")
        
        self.test_results.append({
            "category": "Core Authentication",
            "tests": test_results,
            "status": "✅ PASS" if all("✅" in t for t in test_results) else "❌ FAIL"
        })

    async def test_admin_functionality(self):
        """Test admin panel functionality"""
        print("\n👑 Testing Admin Functionality...")
        
        test_results = []
        
        if not self.admin_token:
            print("❌ No admin token available")
            self.test_results.append({
                "category": "Admin Functionality", 
                "tests": ["❌ No Admin Access"],
                "status": "❌ FAIL"
            })
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Admin stats
        try:
            response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "total_users" in data and "active_users" in data:
                    print(f"✅ Admin stats working (Total users: {data['total_users']})")
                    test_results.append("✅ Admin Stats")
                else:
                    print("❌ Admin stats response incomplete")
                    test_results.append("❌ Admin Stats")
            else:
                print(f"❌ Admin stats failed: {response.status_code}")
                test_results.append("❌ Admin Stats")
                
        except Exception as e:
            print(f"❌ Admin stats test error: {str(e)}")
            test_results.append("❌ Admin Stats")
        
        # Test 2: Get all users
        try:
            response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    admin_count = sum(1 for user in data if user.get("is_admin"))
                    regular_count = len(data) - admin_count
                    print(f"✅ Get all users working ({len(data)} total: {admin_count} admin, {regular_count} regular)")
                    test_results.append("✅ Get Users")
                else:
                    print("❌ Users list empty or incorrect format")
                    test_results.append("❌ Get Users")
            else:
                print(f"❌ Get all users failed: {response.status_code}")
                test_results.append("❌ Get Users")
                
        except Exception as e:
            print(f"❌ Get users test error: {str(e)}")
            test_results.append("❌ Get Users")
        
        # Test 3: Get all orders
        try:
            response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    status_counts = {}
                    for order in data:
                        status = order.get("status", "unknown")
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    print(f"✅ Get all orders working ({len(data)} orders: {status_counts})")
                    test_results.append("✅ Get Orders")
                else:
                    print("❌ Orders list incorrect format")
                    test_results.append("❌ Get Orders")
            else:
                print(f"❌ Get all orders failed: {response.status_code}")
                test_results.append("❌ Get Orders")
                
        except Exception as e:
            print(f"❌ Get orders test error: {str(e)}")
            test_results.append("❌ Get Orders")
        
        # Test 4: KYC management
        try:
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ KYC management working ({len(data)} pending KYC requests)")
                    test_results.append("✅ KYC Management")
                else:
                    print("❌ KYC management response incorrect format")
                    test_results.append("❌ KYC Management")
            else:
                print(f"❌ KYC management failed: {response.status_code}")
                test_results.append("❌ KYC Management")
                
        except Exception as e:
            print(f"❌ KYC management test error: {str(e)}")
            test_results.append("❌ KYC Management")
        
        self.test_results.append({
            "category": "Admin Functionality",
            "tests": test_results,
            "status": "✅ PASS" if all("✅" in t for t in test_results) else "❌ FAIL"
        })

    async def test_trading_apis(self):
        """Test trading system APIs"""
        print("\n💰 Testing Trading APIs...")
        
        test_results = []
        
        # Test 1: Crypto prices
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    prices = data["data"]
                    crypto_count = len(prices)
                    
                    # Check for key cryptocurrencies
                    key_cryptos = ["bitcoin", "ethereum", "tether"]
                    available_cryptos = [crypto for crypto in key_cryptos if crypto in prices]
                    
                    print(f"✅ Crypto prices working ({crypto_count} cryptocurrencies, {len(available_cryptos)}/{len(key_cryptos)} key cryptos)")
                    test_results.append("✅ Crypto Prices")
                else:
                    print("❌ Crypto prices response format incorrect")
                    test_results.append("❌ Crypto Prices")
            else:
                print(f"❌ Crypto prices failed: {response.status_code}")
                test_results.append("❌ Crypto Prices")
                
        except Exception as e:
            print(f"❌ Crypto prices test error: {str(e)}")
            test_results.append("❌ Crypto Prices")
        
        # Test 2: Trading orders (if user available)
        if self.test_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ User trading orders working ({len(data)} orders)")
                        test_results.append("✅ Trading Orders")
                    else:
                        print("❌ Trading orders response format incorrect")
                        test_results.append("❌ Trading Orders")
                else:
                    print(f"❌ Trading orders failed: {response.status_code}")
                    test_results.append("❌ Trading Orders")
                    
            except Exception as e:
                print(f"❌ Trading orders test error: {str(e)}")
                test_results.append("❌ Trading Orders")
        else:
            print("⚠️ No test user available - skipping trading orders test")
            test_results.append("⚠️ Trading Orders")
        
        # Test 3: User holdings (if user available)
        if self.test_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/trading/holdings/my", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ User holdings working ({len(data)} holdings)")
                        test_results.append("✅ Holdings")
                    else:
                        print("❌ Holdings response format incorrect")
                        test_results.append("❌ Holdings")
                else:
                    print(f"❌ Holdings failed: {response.status_code}")
                    test_results.append("❌ Holdings")
                    
            except Exception as e:
                print(f"❌ Holdings test error: {str(e)}")
                test_results.append("❌ Holdings")
        else:
            print("⚠️ No test user available - skipping holdings test")
            test_results.append("⚠️ Holdings")
        
        self.test_results.append({
            "category": "Trading APIs",
            "tests": test_results,
            "status": "✅ PASS" if all("✅" in t for t in test_results) else "❌ PARTIAL"
        })

    async def test_kyc_functionality(self):
        """Test KYC functionality"""
        print("\n📋 Testing KYC Functionality...")
        
        test_results = []
        
        # Test 1: KYC status (if user available)
        if self.test_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "kyc_level" in data and "kyc_status" in data:
                        print(f"✅ KYC status working (Level: {data['kyc_level']}, Status: {data['kyc_status']})")
                        test_results.append("✅ KYC Status")
                    else:
                        print("❌ KYC status response incomplete")
                        test_results.append("❌ KYC Status")
                else:
                    print(f"❌ KYC status failed: {response.status_code}")
                    test_results.append("❌ KYC Status")
                    
            except Exception as e:
                print(f"❌ KYC status test error: {str(e)}")
                test_results.append("❌ KYC Status")
        else:
            print("⚠️ No test user available - skipping KYC status test")
            test_results.append("⚠️ KYC Status")
        
        # Test 2: Admin KYC management
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✅ Admin KYC management working ({len(data)} pending requests)")
                        test_results.append("✅ Admin KYC")
                    else:
                        print("❌ Admin KYC response format incorrect")
                        test_results.append("❌ Admin KYC")
                else:
                    print(f"❌ Admin KYC management failed: {response.status_code}")
                    test_results.append("❌ Admin KYC")
                    
            except Exception as e:
                print(f"❌ Admin KYC test error: {str(e)}")
                test_results.append("❌ Admin KYC")
        else:
            print("❌ No admin token available")
            test_results.append("❌ Admin KYC")
        
        self.test_results.append({
            "category": "KYC Functionality",
            "tests": test_results,
            "status": "✅ PASS" if all("✅" in t for t in test_results) else "❌ PARTIAL"
        })

    async def test_api_health(self):
        """Test general API health"""
        print("\n⚡ Testing API Health...")
        
        test_results = []
        
        # Test 1: Response times
        endpoints_to_test = [
            ("/crypto/prices", "GET", None),
            ("/auth/login", "POST", {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        ]
        
        fast_responses = 0
        total_tests = len(endpoints_to_test)
        
        for endpoint, method, payload in endpoints_to_test:
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = await self.client.post(f"{BACKEND_URL}{endpoint}", json=payload)
                
                response_time = time.time() - start_time
                
                if response.status_code == 200 and response_time < 2.0:
                    fast_responses += 1
                
                print(f"✅ {endpoint}: {response_time:.2f}s (Status: {response.status_code})")
                
            except Exception as e:
                print(f"❌ {endpoint} test error: {str(e)}")
        
        if fast_responses >= total_tests * 0.8:
            print(f"✅ API performance good ({fast_responses}/{total_tests} endpoints under 2s)")
            test_results.append("✅ Performance")
        else:
            print(f"⚠️ API performance concerns ({fast_responses}/{total_tests} fast endpoints)")
            test_results.append("⚠️ Performance")
        
        # Test 2: Error handling
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            })
            
            if response.status_code == 401:
                print("✅ Error handling working correctly")
                test_results.append("✅ Error Handling")
            else:
                print(f"❌ Error handling incorrect: {response.status_code}")
                test_results.append("❌ Error Handling")
                
        except Exception as e:
            print(f"❌ Error handling test error: {str(e)}")
            test_results.append("❌ Error Handling")
        
        # Test 3: Persian language support
        try:
            # Test with invalid registration data to trigger Persian error
            invalid_data = {
                "first_name": "ت",  # Too short
                "last_name": "ک",   # Too short  
                "email": "invalid-email",
                "phone": "123",
                "password": "123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 422:
                response_text = response.text
                if any(char in response_text for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                    print("✅ Persian language support confirmed")
                    test_results.append("✅ Persian Support")
                else:
                    print("⚠️ Persian language not detected in errors")
                    test_results.append("⚠️ Persian Support")
            else:
                print(f"❌ Validation error test failed: {response.status_code}")
                test_results.append("❌ Persian Support")
                
        except Exception as e:
            print(f"❌ Persian language test error: {str(e)}")
            test_results.append("❌ Persian Support")
        
        self.test_results.append({
            "category": "API Health",
            "tests": test_results,
            "status": "✅ PASS" if all("✅" in t for t in test_results) else "⚠️ PARTIAL"
        })

    async def run_focused_health_check(self):
        """Run focused backend health check"""
        print("🚀 Starting Focused Backend Health Check...")
        print("=" * 60)
        
        await self.setup()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run focused tests
        await self.test_core_authentication()
        await self.test_admin_functionality()
        await self.test_trading_apis()
        await self.test_kyc_functionality()
        await self.test_api_health()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 FOCUSED BACKEND HEALTH CHECK SUMMARY")
        print("=" * 60)
        
        total_categories = len(self.test_results)
        passed_categories = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_categories = len([r for r in self.test_results if "❌ FAIL" in r["status"]])
        partial_categories = len([r for r in self.test_results if "⚠️ PARTIAL" in r["status"]])
        
        print(f"📊 CATEGORY RESULTS:")
        print(f"✅ PASSED: {passed_categories}/{total_categories}")
        print(f"❌ FAILED: {failed_categories}/{total_categories}")
        print(f"⚠️ PARTIAL: {partial_categories}/{total_categories}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if "✅ PASS" in result["status"] else "❌" if "❌ FAIL" in result["status"] else "⚠️"
            print(f"{status_icon} {result['category']}: {' '.join(result['tests'])}")
        
        print(f"\n🎯 KEY FINDINGS:")
        
        # Analyze results
        auth_working = any("✅ PASS" in r["status"] for r in self.test_results if r["category"] == "Core Authentication")
        admin_working = any("✅ PASS" in r["status"] for r in self.test_results if r["category"] == "Admin Functionality")
        trading_working = any("✅" in r["status"] for r in self.test_results if r["category"] == "Trading APIs")
        kyc_working = any("✅" in r["status"] for r in self.test_results if r["category"] == "KYC Functionality")
        api_healthy = any("✅" in r["status"] for r in self.test_results if r["category"] == "API Health")
        
        if auth_working:
            print("✅ Authentication system is functional")
        else:
            print("❌ Authentication system has issues")
            
        if admin_working:
            print("✅ Admin panel is fully operational")
        else:
            print("❌ Admin panel has issues")
            
        if trading_working:
            print("✅ Trading APIs are accessible")
        else:
            print("❌ Trading APIs have issues")
            
        if kyc_working:
            print("✅ KYC system is operational")
        else:
            print("❌ KYC system has issues")
            
        if api_healthy:
            print("✅ API performance and error handling working")
        else:
            print("❌ API health concerns detected")
        
        # Overall assessment
        if passed_categories >= total_categories * 0.8:
            print(f"\n🎉 OVERALL STATUS: HEALTHY ({passed_categories}/{total_categories} categories passing)")
        elif passed_categories >= total_categories * 0.6:
            print(f"\n⚠️ OVERALL STATUS: PARTIAL ({passed_categories}/{total_categories} categories passing)")
        else:
            print(f"\n🚨 OVERALL STATUS: CRITICAL ISSUES ({passed_categories}/{total_categories} categories passing)")
        
        # User authentication note
        if self.test_user_token:
            print(f"✅ Test user authentication successful: {self.test_user_email}")
        else:
            print("⚠️ Test user authentication unavailable - some tests skipped")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = FocusedBackendTester()
    await tester.run_focused_health_check()

if __name__ == "__main__":
    asyncio.run(main())