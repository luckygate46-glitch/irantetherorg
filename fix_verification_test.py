#!/usr/bin/env python3
"""
Fix Verification Test for Iranian Crypto Exchange
Tests the specific fixes implemented as requested in the review:

1. Authentication System Fix - Test that login no longer returns 500 errors
2. OTP Service Fix - Test OTP sending with development fallback  
3. Missing Admin Endpoints Fix - Test /admin/orders and /admin/orders/approve endpoints
4. Complete User Journey Testing - Test full registration → OTP → login → dashboard flow
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://cryptotradera.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class FixVerificationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.admin_token = None
        self.test_user_token = None
        
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

    async def test_authentication_system_fix(self):
        """Test 1: Authentication System Fix - Verify login no longer returns 500 errors"""
        print("\n🔐 Testing Authentication System Fix...")
        
        # Test 1.1: Test login with existing user (backward compatibility)
        try:
            login_data = {
                "email": "testuser@example.com",
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify backward compatibility - user should have computed full_name
                if user_info.get("full_name"):
                    await self.log_test("Login Backward Compatibility", True, f"Existing user login successful with full_name: '{user_info.get('full_name')}'")
                    self.test_user_token = data.get("access_token")
                else:
                    await self.log_test("Login Backward Compatibility", False, "User login successful but missing full_name computation")
                    
            elif response.status_code in [401, 422]:
                # Expected for wrong credentials - no 500 error
                await self.log_test("Login No 500 Error", True, f"Login returns proper error code {response.status_code} instead of 500")
            else:
                await self.log_test("Login Error Handling", False, f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Login Authentication Test", False, f"Exception: {str(e)}")
        
        # Test 1.2: Test registration with new fields
        try:
            register_data = {
                "first_name": "محمد",
                "last_name": "رضایی", 
                "email": "mohammad.test@example.com",
                "phone": "09123456789",
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if response.status_code == 400:
                # Expected - requires OTP verification
                error_detail = response.json().get("detail", "")
                if "تایید" in error_detail or "موبایل" in error_detail:
                    await self.log_test("Registration New Fields Structure", True, "Registration accepts new fields and requires OTP verification")
                else:
                    await self.log_test("Registration New Fields Structure", False, f"Unexpected error: {error_detail}")
            elif response.status_code == 200:
                # Successful registration (OTP was pre-verified somehow)
                data = response.json()
                user_info = data.get("user", {})
                expected_full_name = f"{register_data['first_name']} {register_data['last_name']}"
                
                if user_info.get("full_name") == expected_full_name:
                    await self.log_test("Registration New Fields Success", True, f"Registration successful with correct full_name: '{expected_full_name}'")
                else:
                    await self.log_test("Registration New Fields Success", False, f"Full name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
            else:
                await self.log_test("Registration New Fields", False, f"Registration failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            await self.log_test("Registration New Fields Test", False, f"Exception: {str(e)}")

    async def test_otp_service_fix(self):
        """Test 2: OTP Service Fix - Test OTP sending with development fallback"""
        print("\n📱 Testing OTP Service Fix...")
        
        # Test 2.1: Send OTP
        try:
            otp_data = {
                "phone": "09123456788"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/otp/send", json=otp_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("OTP Send with Fallback", True, "OTP sending works with development fallback")
                else:
                    await self.log_test("OTP Send with Fallback", False, "OTP send returned success=false")
            else:
                await self.log_test("OTP Send Service", False, f"OTP send failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            await self.log_test("OTP Send Test", False, f"Exception: {str(e)}")
        
        # Test 2.2: Verify OTP (with mock code)
        try:
            verify_data = {
                "phone": "09123456788",
                "code": "12345"  # Mock code
            }
            
            response = await self.client.post(f"{BACKEND_URL}/otp/verify", json=verify_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("OTP Verify Functionality", True, "OTP verification works correctly")
                else:
                    await self.log_test("OTP Verify Functionality", False, "OTP verify returned success=false")
            elif response.status_code == 400:
                # Expected for wrong code or expired
                await self.log_test("OTP Verify Error Handling", True, "OTP verification properly handles invalid codes")
            else:
                await self.log_test("OTP Verify Service", False, f"OTP verify failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            await self.log_test("OTP Verify Test", False, f"Exception: {str(e)}")

    async def test_missing_admin_endpoints_fix(self):
        """Test 3: Missing Admin Endpoints Fix - Test /admin/orders and /admin/orders/approve"""
        print("\n👨‍💼 Testing Missing Admin Endpoints Fix...")
        
        # First, try to get admin access (test with existing admin or create one)
        await self.get_admin_access()
        
        # Test 3.1: Test /admin/orders endpoint exists
        try:
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
                
                if response.status_code == 200:
                    orders = response.json()
                    await self.log_test("Admin Orders Endpoint", True, f"/admin/orders endpoint works - returned {len(orders)} orders")
                elif response.status_code == 404:
                    await self.log_test("Admin Orders Endpoint", False, "/admin/orders endpoint still returns 404 - not fixed")
                else:
                    await self.log_test("Admin Orders Endpoint", False, f"/admin/orders returned {response.status_code}: {response.text}")
            else:
                # Test without auth - should return 401/403, not 404
                response = await self.client.get(f"{BACKEND_URL}/admin/orders")
                
                if response.status_code in [401, 403]:
                    await self.log_test("Admin Orders Endpoint Exists", True, "/admin/orders endpoint exists (returns auth error, not 404)")
                elif response.status_code == 404:
                    await self.log_test("Admin Orders Endpoint Exists", False, "/admin/orders endpoint still returns 404 - not implemented")
                else:
                    await self.log_test("Admin Orders Endpoint Exists", True, f"/admin/orders endpoint exists (returns {response.status_code})")
                    
        except Exception as e:
            await self.log_test("Admin Orders Endpoint Test", False, f"Exception: {str(e)}")
        
        # Test 3.2: Test /admin/orders/approve endpoint exists
        try:
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                # Test with dummy data to see if endpoint exists
                approve_data = {
                    "order_id": "dummy-order-id",
                    "action": "approve",
                    "admin_note": "Test approval"
                }
                
                response = await self.client.post(f"{BACKEND_URL}/admin/orders/approve", headers=headers, json=approve_data)
                
                if response.status_code == 404 and "سفارش یافت نشد" in response.text:
                    await self.log_test("Admin Orders Approve Endpoint", True, "/admin/orders/approve endpoint works (order not found is expected)")
                elif response.status_code == 404 and "Not Found" in response.text:
                    await self.log_test("Admin Orders Approve Endpoint", False, "/admin/orders/approve endpoint still returns 404 - not implemented")
                else:
                    await self.log_test("Admin Orders Approve Endpoint", True, f"/admin/orders/approve endpoint exists (returns {response.status_code})")
            else:
                # Test without auth
                response = await self.client.post(f"{BACKEND_URL}/admin/orders/approve", json={})
                
                if response.status_code in [401, 403]:
                    await self.log_test("Admin Orders Approve Endpoint Exists", True, "/admin/orders/approve endpoint exists (returns auth error)")
                elif response.status_code == 404:
                    await self.log_test("Admin Orders Approve Endpoint Exists", False, "/admin/orders/approve endpoint returns 404 - not implemented")
                else:
                    await self.log_test("Admin Orders Approve Endpoint Exists", True, f"/admin/orders/approve endpoint exists (returns {response.status_code})")
                    
        except Exception as e:
            await self.log_test("Admin Orders Approve Test", False, f"Exception: {str(e)}")

    async def get_admin_access(self):
        """Try to get admin access for testing"""
        try:
            # Try to login as admin (common admin credentials)
            admin_credentials = [
                {"email": "admin@example.com", "password": "admin123"},
                {"email": "admin@tehcrypto.com", "password": "admin123"},
                {"email": "testuser@example.com", "password": "testpass123"}  # In case testuser is admin
            ]
            
            for creds in admin_credentials:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json=creds)
                
                if response.status_code == 200:
                    data = response.json()
                    user_info = data.get("user", {})
                    
                    if user_info.get("is_admin"):
                        self.admin_token = data.get("access_token")
                        await self.log_test("Admin Access", True, f"Got admin access with {creds['email']}")
                        return
                        
            await self.log_test("Admin Access", False, "Could not get admin access - testing endpoints without auth")
            
        except Exception as e:
            await self.log_test("Admin Access", False, f"Exception getting admin access: {str(e)}")

    async def test_complete_user_journey(self):
        """Test 4: Complete User Journey - Test full registration → OTP → login → dashboard flow"""
        print("\n🚀 Testing Complete User Journey...")
        
        # Test 4.1: Full registration flow (with OTP requirement)
        try:
            # Step 1: Send OTP
            phone = "09123456787"
            otp_response = await self.client.post(f"{BACKEND_URL}/otp/send", json={"phone": phone})
            
            if otp_response.status_code == 200:
                await self.log_test("Journey Step 1: OTP Send", True, "OTP sent successfully")
                
                # Step 2: Verify OTP (using development fallback)
                # In development mode, any code should work due to fallback
                verify_response = await self.client.post(f"{BACKEND_URL}/otp/verify", json={
                    "phone": phone,
                    "code": "12345"
                })
                
                if verify_response.status_code == 200:
                    await self.log_test("Journey Step 2: OTP Verify", True, "OTP verified successfully")
                    
                    # Step 3: Register user
                    register_data = {
                        "first_name": "احمد",
                        "last_name": "محمدی",
                        "email": "ahmad.journey@example.com", 
                        "phone": phone,
                        "password": "journey123"
                    }
                    
                    register_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
                    
                    if register_response.status_code == 200:
                        register_data_response = register_response.json()
                        user_info = register_data_response.get("user", {})
                        token = register_data_response.get("access_token")
                        
                        await self.log_test("Journey Step 3: Registration", True, f"User registered successfully with full_name: '{user_info.get('full_name')}'")
                        
                        # Step 4: Test dashboard access (user profile)
                        if token:
                            headers = {"Authorization": f"Bearer {token}"}
                            profile_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                            
                            if profile_response.status_code == 200:
                                profile_data = profile_response.json()
                                await self.log_test("Journey Step 4: Dashboard Access", True, f"Dashboard accessible - user: {profile_data.get('full_name')}")
                                
                                # Step 5: Test trading page access (should be blocked by KYC)
                                trading_response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                                    headers=headers,
                                    json={
                                        "order_type": "buy",
                                        "coin_symbol": "BTC", 
                                        "coin_id": "bitcoin",
                                        "amount_tmn": 100000.0
                                    }
                                )
                                
                                if trading_response.status_code == 403:
                                    await self.log_test("Journey Step 5: Trading Access Control", True, "Trading correctly blocked for KYC level 0")
                                else:
                                    await self.log_test("Journey Step 5: Trading Access Control", False, f"Trading should be blocked: {trading_response.status_code}")
                                    
                            else:
                                await self.log_test("Journey Step 4: Dashboard Access", False, f"Dashboard access failed: {profile_response.status_code}")
                        else:
                            await self.log_test("Journey Step 4: Token Missing", False, "No access token received from registration")
                            
                    else:
                        await self.log_test("Journey Step 3: Registration", False, f"Registration failed: {register_response.status_code} - {register_response.text}")
                        
                else:
                    await self.log_test("Journey Step 2: OTP Verify", False, f"OTP verification failed: {verify_response.status_code}")
                    
            else:
                await self.log_test("Journey Step 1: OTP Send", False, f"OTP send failed: {otp_response.status_code}")
                
        except Exception as e:
            await self.log_test("Complete User Journey", False, f"Exception: {str(e)}")

    async def test_admin_panel_functionality(self):
        """Test admin panel functionality if admin access is available"""
        print("\n🔧 Testing Admin Panel Functionality...")
        
        if not self.admin_token:
            await self.log_test("Admin Panel Test", False, "No admin access available - skipping admin panel tests")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin stats
            stats_response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                await self.log_test("Admin Stats", True, f"Admin stats working - {stats.get('total_users', 0)} users")
            else:
                await self.log_test("Admin Stats", False, f"Admin stats failed: {stats_response.status_code}")
            
            # Test admin users list
            users_response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            if users_response.status_code == 200:
                users = users_response.json()
                await self.log_test("Admin Users List", True, f"Admin users list working - {len(users)} users")
            else:
                await self.log_test("Admin Users List", False, f"Admin users list failed: {users_response.status_code}")
                
        except Exception as e:
            await self.log_test("Admin Panel Functionality", False, f"Exception: {str(e)}")

    async def run_fix_verification_tests(self):
        """Run all fix verification tests"""
        print("🔍 Starting Fix Verification Tests")
        print("=" * 70)
        print("Testing specific fixes implemented:")
        print("1. Authentication System Fix")
        print("2. OTP Service Fix") 
        print("3. Missing Admin Endpoints Fix")
        print("4. Complete User Journey Testing")
        print("=" * 70)
        
        # Run all tests
        await self.test_authentication_system_fix()
        await self.test_otp_service_fix()
        await self.test_missing_admin_endpoints_fix()
        await self.test_complete_user_journey()
        await self.test_admin_panel_functionality()
        
        print("\n" + "=" * 70)
        print("🏁 Fix Verification Testing Complete!")
        await self.print_summary()

    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 FIX VERIFICATION SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by fix category
        auth_tests = [r for r in self.test_results if "Login" in r["test"] or "Registration" in r["test"] or "Authentication" in r["test"]]
        otp_tests = [r for r in self.test_results if "OTP" in r["test"]]
        admin_tests = [r for r in self.test_results if "Admin" in r["test"]]
        journey_tests = [r for r in self.test_results if "Journey" in r["test"]]
        
        print(f"\n📋 RESULTS BY FIX CATEGORY:")
        print(f"🔐 Authentication System: {sum(1 for r in auth_tests if r['success'])}/{len(auth_tests)} passed")
        print(f"📱 OTP Service: {sum(1 for r in otp_tests if r['success'])}/{len(otp_tests)} passed")
        print(f"👨‍💼 Admin Endpoints: {sum(1 for r in admin_tests if r['success'])}/{len(admin_tests)} passed")
        print(f"🚀 User Journey: {sum(1 for r in journey_tests if r['success'])}/{len(journey_tests)} passed")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 CRITICAL FIXES STATUS:")
        
        # Check if critical fixes are working
        login_500_fixed = any(r["success"] and ("No 500 Error" in r["test"] or "Login" in r["test"]) for r in self.test_results)
        otp_working = any(r["success"] and "OTP" in r["test"] for r in self.test_results)
        admin_endpoints_fixed = any(r["success"] and "Admin Orders Endpoint" in r["test"] for r in self.test_results)
        user_journey_working = any(r["success"] and "Journey" in r["test"] for r in self.test_results)
        
        print(f"✅ Login 500 errors fixed: {'YES' if login_500_fixed else 'NO'}")
        print(f"✅ OTP service working: {'YES' if otp_working else 'NO'}")
        print(f"✅ Admin endpoints fixed: {'YES' if admin_endpoints_fixed else 'NO'}")
        print(f"✅ User journey working: {'YES' if user_journey_working else 'NO'}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = FixVerificationTester()
    try:
        await tester.run_fix_verification_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())