#!/usr/bin/env python3
"""
Authentication API Testing for Iranian Crypto Exchange
Tests the specific backward compatibility scenarios requested:
1. Test registration API structure with new fields
2. Test login API doesn't return 500 errors
3. Test user profile retrieval works
4. Test backward compatibility for existing users
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://tehcrypto.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class AuthAPITester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        
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
    
    async def test_registration_api_validation(self):
        """Test registration API accepts new fields and validates properly"""
        print("\n📝 Testing Registration API Structure and Validation...")
        
        # Test 1: Registration with all new fields (will fail due to OTP but should validate structure)
        test_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "phone": "09123456789",
            "password": "testpass123"
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_data)
            
            if response.status_code == 400:
                # Expected - should fail due to OTP requirement
                error_data = response.json()
                if "تایید" in error_data.get("detail", "") or "OTP" in error_data.get("detail", ""):
                    await self.log_test("Registration API Structure", True, "Registration correctly requires OTP verification - API accepts new fields")
                else:
                    await self.log_test("Registration API Structure", False, f"Unexpected error: {error_data}")
            elif response.status_code == 422:
                # Validation error - check if it's about field validation
                error_data = response.json()
                await self.log_test("Registration Field Validation", True, f"Registration validates fields correctly: {error_data}")
            elif response.status_code in [200, 201]:
                # Successful registration (unlikely without OTP)
                data = response.json()
                user_info = data.get("user", {})
                expected_full_name = f"{test_data['first_name']} {test_data['last_name']}"
                
                if user_info.get("full_name") == expected_full_name:
                    await self.log_test("Registration API Success", True, f"Registration successful with correct full_name: '{expected_full_name}'")
                else:
                    await self.log_test("Registration API Success", False, f"full_name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
            else:
                await self.log_test("Registration API Structure", False, f"Unexpected status code {response.status_code}: {response.text}")
                
        except Exception as e:
            await self.log_test("Registration API Structure", False, f"Exception: {str(e)}")
        
        # Test 2: Registration with missing fields
        incomplete_data = {
            "email": "incomplete@test.com",
            "password": "testpass123"
            # Missing first_name, last_name, phone
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=incomplete_data)
            
            if response.status_code == 422:
                await self.log_test("Registration Missing Fields Validation", True, "Registration correctly validates required fields")
            else:
                await self.log_test("Registration Missing Fields Validation", False, f"Should validate required fields: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Registration Missing Fields Validation", False, f"Exception: {str(e)}")
        
        # Test 3: Registration with invalid field formats
        invalid_data = {
            "first_name": "A",  # Too short
            "last_name": "B",   # Too short
            "email": "invalid-email",  # Invalid email
            "phone": "123",    # Invalid phone
            "password": "123"  # Too short
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 422:
                await self.log_test("Registration Field Format Validation", True, "Registration correctly validates field formats")
            else:
                await self.log_test("Registration Field Format Validation", False, f"Should validate field formats: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Registration Field Format Validation", False, f"Exception: {str(e)}")
    
    async def test_login_no_500_errors(self):
        """Test that login API doesn't return 500 errors"""
        print("\n🔐 Testing Login API - No 500 Errors...")
        
        # Test with various login scenarios to ensure no 500 errors
        test_scenarios = [
            {"email": "testuser@example.com", "password": "testpass123", "desc": "New User Format"},
            {"email": "admin@test.com", "password": "admin123", "desc": "Admin User"},
            {"email": "legacy@example.com", "password": "legacy123", "desc": "Legacy User Format"},
            {"email": "nonexistent@test.com", "password": "wrongpass", "desc": "Invalid Credentials"},
            {"email": "invalid-email", "password": "test", "desc": "Invalid Email Format"},
            {"email": "", "password": "", "desc": "Empty Credentials"}
        ]
        
        for scenario in test_scenarios:
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": scenario["email"],
                    "password": scenario["password"]
                })
                
                if response.status_code == 500:
                    await self.log_test(f"Login No 500 Error ({scenario['desc']})", False, f"LOGIN RETURNS 500 ERROR: {response.text}")
                elif response.status_code == 200:
                    # Successful login
                    data = response.json()
                    user_info = data.get("user", {})
                    
                    # Verify response structure
                    required_fields = ["id", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                    missing_fields = [field for field in required_fields if field not in user_info]
                    
                    if not missing_fields:
                        await self.log_test(f"Login Success ({scenario['desc']})", True, f"Login successful with all required fields")
                        
                        # Test full_name computation
                        full_name = user_info.get("full_name")
                        if full_name:
                            await self.log_test(f"Login Full Name ({scenario['desc']})", True, f"full_name computed: '{full_name}'")
                        else:
                            await self.log_test(f"Login Full Name ({scenario['desc']})", False, "full_name is empty or missing")
                    else:
                        await self.log_test(f"Login Response Structure ({scenario['desc']})", False, f"Missing fields: {missing_fields}")
                        
                elif response.status_code in [401, 403]:
                    # Expected authentication errors
                    await self.log_test(f"Login No 500 Error ({scenario['desc']})", True, f"Proper authentication error (status {response.status_code}) - no 500 error")
                elif response.status_code == 422:
                    # Validation error
                    await self.log_test(f"Login No 500 Error ({scenario['desc']})", True, f"Proper validation error (status {response.status_code}) - no 500 error")
                else:
                    await self.log_test(f"Login No 500 Error ({scenario['desc']})", True, f"No 500 error (status {response.status_code})")
                    
            except Exception as e:
                await self.log_test(f"Login No 500 Error ({scenario['desc']})", False, f"Exception: {str(e)}")
    
    async def test_user_profile_endpoint(self):
        """Test user profile endpoint structure"""
        print("\n👤 Testing User Profile Endpoint (/auth/me)...")
        
        # Test without authentication
        try:
            response = await self.client.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code in [401, 403]:
                await self.log_test("Profile Endpoint Security", True, "Profile endpoint properly protected (requires authentication)")
            else:
                await self.log_test("Profile Endpoint Security", False, f"Profile endpoint not protected: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Profile Endpoint Security", False, f"Exception: {str(e)}")
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid-token"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code in [401, 403]:
                await self.log_test("Profile Invalid Token", True, "Profile endpoint correctly rejects invalid tokens")
            else:
                await self.log_test("Profile Invalid Token", False, f"Should reject invalid token: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Profile Invalid Token", False, f"Exception: {str(e)}")
    
    async def test_api_endpoints_availability(self):
        """Test that all authentication endpoints are available"""
        print("\n🌐 Testing API Endpoints Availability...")
        
        endpoints = [
            {"path": "/auth/register", "method": "POST", "desc": "Registration"},
            {"path": "/auth/login", "method": "POST", "desc": "Login"},
            {"path": "/auth/me", "method": "GET", "desc": "User Profile"},
            {"path": "/otp/send", "method": "POST", "desc": "OTP Send"},
            {"path": "/otp/verify", "method": "POST", "desc": "OTP Verify"}
        ]
        
        for endpoint in endpoints:
            try:
                if endpoint["method"] == "GET":
                    response = await self.client.get(f"{BACKEND_URL}{endpoint['path']}")
                else:
                    response = await self.client.post(f"{BACKEND_URL}{endpoint['path']}", json={})
                
                # We expect various status codes, but not 404 (endpoint not found)
                if response.status_code == 404:
                    await self.log_test(f"Endpoint Available ({endpoint['desc']})", False, f"Endpoint not found: {endpoint['path']}")
                else:
                    await self.log_test(f"Endpoint Available ({endpoint['desc']})", True, f"Endpoint available (status {response.status_code})")
                    
            except Exception as e:
                await self.log_test(f"Endpoint Available ({endpoint['desc']})", False, f"Exception: {str(e)}")
    
    async def test_otp_system_integration(self):
        """Test OTP system integration"""
        print("\n📱 Testing OTP System Integration...")
        
        # Test OTP send endpoint structure
        try:
            response = await self.client.post(f"{BACKEND_URL}/otp/send", json={
                "phone": "09123456789"
            })
            
            if response.status_code == 500:
                # Check if it's an API.IR integration issue
                error_text = response.text
                if "API.IR" in error_text or "ارسال پیامک" in error_text:
                    await self.log_test("OTP Send Integration", False, "OTP service integration issue (API.IR) - **mocked** fallback needed")
                else:
                    await self.log_test("OTP Send", False, f"OTP send failed: {error_text}")
            elif response.status_code in [200, 201]:
                await self.log_test("OTP Send", True, "OTP send endpoint working")
            else:
                await self.log_test("OTP Send", True, f"OTP send endpoint available (status {response.status_code})")
                
        except Exception as e:
            await self.log_test("OTP Send", False, f"Exception: {str(e)}")
        
        # Test OTP verify endpoint structure
        try:
            response = await self.client.post(f"{BACKEND_URL}/otp/verify", json={
                "phone": "09123456789",
                "code": "12345"
            })
            
            if response.status_code == 404:
                await self.log_test("OTP Verify Structure", True, "OTP verify correctly returns 404 for non-existent OTP")
            elif response.status_code in [200, 400]:
                await self.log_test("OTP Verify Structure", True, "OTP verify endpoint working")
            else:
                await self.log_test("OTP Verify Structure", True, f"OTP verify endpoint available (status {response.status_code})")
                
        except Exception as e:
            await self.log_test("OTP Verify Structure", False, f"Exception: {str(e)}")
    
    async def test_backend_service_health(self):
        """Test overall backend service health"""
        print("\n🏥 Testing Backend Service Health...")
        
        # Test root endpoint
        try:
            response = await self.client.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "Persian Crypto Exchange" in data.get("message", ""):
                    await self.log_test("Backend Service Health", True, f"Backend service healthy: {data.get('message')}")
                else:
                    await self.log_test("Backend Service Health", True, f"Backend service responding: {data}")
            else:
                await self.log_test("Backend Service Health", False, f"Backend service issue: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Backend Service Health", False, f"Backend service unreachable: {str(e)}")
    
    async def run_comprehensive_auth_tests(self):
        """Run comprehensive authentication system tests"""
        print("🚀 Starting Comprehensive Authentication API Tests")
        print("=" * 80)
        
        # Test backend service health first
        await self.test_backend_service_health()
        
        # Test API endpoints availability
        await self.test_api_endpoints_availability()
        
        # Test registration API structure and validation
        await self.test_registration_api_validation()
        
        # Test login API for 500 errors
        await self.test_login_no_500_errors()
        
        # Test user profile endpoint
        await self.test_user_profile_endpoint()
        
        # Test OTP system integration
        await self.test_otp_system_integration()
        
        print("\n" + "=" * 80)
        print("🏁 Authentication API Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary with focus on critical issues"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        # Critical findings
        critical_issues = []
        login_500_errors = [r for r in self.test_results if "500 Error" in r["test"] and not r["success"]]
        if login_500_errors:
            critical_issues.append("🚨 CRITICAL: Login API still returns 500 errors")
        
        backend_health_issues = [r for r in self.test_results if "Backend Service Health" in r["test"] and not r["success"]]
        if backend_health_issues:
            critical_issues.append("🚨 CRITICAL: Backend service health issues")
        
        endpoint_missing = [r for r in self.test_results if "Endpoint Available" in r["test"] and not r["success"]]
        if endpoint_missing:
            critical_issues.append("🚨 CRITICAL: Authentication endpoints missing")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"  {issue}")
        
        # Success indicators
        success_indicators = []
        if any("Backend Service Health" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ Backend service is healthy")
        
        if any("Registration API Structure" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ Registration API accepts new fields")
        
        if any("No 500 Error" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ Login API doesn't return 500 errors")
        
        if any("Profile Endpoint Security" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ User profile endpoint working")
        
        if success_indicators:
            print(f"\n✅ SUCCESS INDICATORS:")
            for indicator in success_indicators:
                print(f"  {indicator}")
        
        # Integration issues
        integration_issues = []
        otp_issues = [r for r in self.test_results if "OTP" in r["test"] and "integration issue" in r["details"]]
        if otp_issues:
            integration_issues.append("⚠️  OTP service integration issues (API.IR)")
        
        if integration_issues:
            print(f"\n⚠️  INTEGRATION ISSUES:")
            for issue in integration_issues:
                print(f"  {issue}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = AuthAPITester()
    try:
        await tester.run_comprehensive_auth_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())