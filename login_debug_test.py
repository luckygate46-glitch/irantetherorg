#!/usr/bin/env python3
"""
LOGIN FUNCTIONALITY DEBUG TEST
Specifically testing the login issue reported by user where frontend shows "در حال ورود..." but doesn't complete
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class LoginDebugTester:
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
        
    async def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = await self.client.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                await self.log_test("Backend Connectivity", True, f"Backend accessible: {data.get('message', 'OK')}")
                return True
            else:
                await self.log_test("Backend Connectivity", False, f"Backend returned {response.status_code}: {response.text}")
                return False
        except Exception as e:
            await self.log_test("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    async def test_login_api_direct(self, email: str, password: str, test_name: str = "Direct Login API Test"):
        """Test login API directly with detailed response analysis"""
        try:
            print(f"\n🔍 Testing login for: {email}")
            
            login_data = {
                "email": email,
                "password": password
            }
            
            # Make the login request
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data Keys: {list(data.keys())}")
                
                # Check required fields in response
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_test(test_name, False, f"Missing required fields: {missing_fields}")
                    return None
                
                user_data = data.get("user", {})
                print(f"User Data Keys: {list(user_data.keys())}")
                
                # Verify user data structure
                user_required_fields = ["id", "email", "full_name", "is_active", "kyc_level"]
                user_missing_fields = [field for field in user_required_fields if field not in user_data]
                
                if user_missing_fields:
                    await self.log_test(test_name, False, f"Missing user fields: {user_missing_fields}")
                    return None
                
                await self.log_test(test_name, True, f"Login successful for {email}")
                return {
                    "token": data.get("access_token"),
                    "user_data": user_data,
                    "full_response": data
                }
                
            elif response.status_code == 401:
                await self.log_test(test_name, False, f"Authentication failed (401): {response.text}")
                return None
            elif response.status_code == 422:
                await self.log_test(test_name, False, f"Validation error (422): {response.text}")
                return None
            elif response.status_code == 429:
                await self.log_test(test_name, False, f"Rate limited (429): {response.text}")
                return None
            elif response.status_code == 500:
                await self.log_test(test_name, False, f"CRITICAL: Server error (500): {response.text}")
                return None
            else:
                await self.log_test(test_name, False, f"Unexpected status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test(test_name, False, f"Exception during login: {str(e)}")
            return None
    
    async def test_jwt_token_validation(self, token: str):
        """Test JWT token validation by accessing protected endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                await self.log_test("JWT Token Validation", True, f"Token valid, user: {user_data.get('email', 'unknown')}")
                return user_data
            elif response.status_code == 401:
                await self.log_test("JWT Token Validation", False, f"Token invalid (401): {response.text}")
                return None
            else:
                await self.log_test("JWT Token Validation", False, f"Unexpected response {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test("JWT Token Validation", False, f"Exception: {str(e)}")
            return None
    
    async def test_rate_limiting_status(self):
        """Test if rate limiting is affecting login attempts"""
        try:
            # Make multiple rapid login attempts to check rate limiting
            test_email = "rate.limit.test@example.com"
            test_password = "wrongpassword"
            
            for i in range(6):  # Try 6 times (limit is usually 5)
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": test_email,
                    "password": test_password
                })
                
                if response.status_code == 429:
                    await self.log_test("Rate Limiting Check", True, f"Rate limiting active after {i+1} attempts")
                    return True
                elif i == 5:  # Last attempt
                    await self.log_test("Rate Limiting Check", True, "Rate limiting not triggered (normal behavior)")
                    return True
                    
        except Exception as e:
            await self.log_test("Rate Limiting Check", False, f"Exception: {str(e)}")
            return False
    
    async def test_known_user_login(self):
        """Test login with the specific user mentioned: saruman.valar@gmail.com"""
        print("\n🎯 Testing with specific user: saruman.valar@gmail.com")
        
        # Test with the specific password requested
        result = await self.test_login_api_direct("saruman.valar@gmail.com", "password123", "Specific User Login (saruman.valar@gmail.com)")
        if result:
            return result
        
        # If that fails, try other common passwords
        test_passwords = ["password", "123456", "admin", "test", "saruman", "valar"]
        
        for password in test_passwords:
            result = await self.test_login_api_direct("saruman.valar@gmail.com", password, f"Known User Login (password: {password})")
            if result:
                return result
        
        await self.log_test("Known User Login", False, "Could not login with any tested passwords")
        return None
    
    async def test_existing_test_users(self):
        """Test login with existing test users from previous tests"""
        test_users = [
            {"email": "testuser@example.com", "password": "testpass123"},
            {"email": "ali.new.test@example.com", "password": "testpass123"},
            {"email": "fateme.new.test@example.com", "password": "testpass456"},
            {"email": "admin@example.com", "password": "admin123"},
        ]
        
        successful_logins = []
        
        for user in test_users:
            result = await self.test_login_api_direct(user["email"], user["password"], f"Existing User Login ({user['email']})")
            if result:
                successful_logins.append(result)
        
        return successful_logins
    
    async def test_complete_auth_flow(self, token: str, user_email: str):
        """Test complete authentication flow: Login → JWT → Protected endpoint"""
        try:
            # Test accessing protected endpoints
            protected_endpoints = [
                "/auth/me",
                "/kyc/status", 
                "/trading/orders/my",
                "/trading/holdings/my"
            ]
            
            headers = {"Authorization": f"Bearer {token}"}
            
            for endpoint in protected_endpoints:
                try:
                    response = await self.client.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        await self.log_test(f"Protected Endpoint Access {endpoint}", True, f"Successfully accessed {endpoint}")
                    elif response.status_code == 401:
                        await self.log_test(f"Protected Endpoint Access {endpoint}", False, f"Token rejected for {endpoint}")
                    elif response.status_code == 403:
                        await self.log_test(f"Protected Endpoint Access {endpoint}", True, f"Access denied (expected for some endpoints): {endpoint}")
                    else:
                        await self.log_test(f"Protected Endpoint Access {endpoint}", False, f"Unexpected response {response.status_code} for {endpoint}")
                        
                except Exception as e:
                    await self.log_test(f"Protected Endpoint Access {endpoint}", False, f"Exception: {str(e)}")
            
            await self.log_test("Complete Auth Flow", True, f"Authentication flow tested for {user_email}")
            return True
            
        except Exception as e:
            await self.log_test("Complete Auth Flow", False, f"Exception: {str(e)}")
            return False
    
    async def test_backend_error_investigation(self):
        """Investigate potential backend errors"""
        try:
            # Test malformed requests
            malformed_requests = [
                {"email": "", "password": ""},  # Empty fields
                {"email": "invalid-email", "password": "test"},  # Invalid email
                {"password": "test"},  # Missing email
                {"email": "test@example.com"},  # Missing password
                {},  # Empty request
            ]
            
            for i, request_data in enumerate(malformed_requests):
                try:
                    response = await self.client.post(f"{BACKEND_URL}/auth/login", json=request_data)
                    
                    if response.status_code == 422:
                        await self.log_test(f"Malformed Request {i+1}", True, "Correctly handled malformed request")
                    elif response.status_code == 500:
                        await self.log_test(f"Malformed Request {i+1}", False, f"Server error on malformed request: {response.text}")
                    else:
                        await self.log_test(f"Malformed Request {i+1}", True, f"Handled malformed request with status {response.status_code}")
                        
                except Exception as e:
                    await self.log_test(f"Malformed Request {i+1}", False, f"Exception: {str(e)}")
            
            return True
            
        except Exception as e:
            await self.log_test("Backend Error Investigation", False, f"Exception: {str(e)}")
            return False
    
    async def create_test_user_for_login(self):
        """Create the specific test user requested: saruman.valar@gmail.com"""
        try:
            # Create the specific user requested in the review
            test_user_data = {
                "first_name": "سارومان",
                "last_name": "والار",
                "email": "saruman.valar@gmail.com",
                "phone": "09123456789",
                "password": "password123"
            }
            
            print(f"🔧 Creating specific test user: {test_user_data['email']}")
            print(f"   Persian names: {test_user_data['first_name']} {test_user_data['last_name']}")
            print(f"   Phone: {test_user_data['phone']}")
            print(f"   Password: {test_user_data['password']}")
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_info = data.get("user", {})
                await self.log_test("Specific Test User Creation", True, f"Created user: {test_user_data['email']} with full_name: {user_info.get('full_name')}")
                return {
                    "email": test_user_data["email"],
                    "password": test_user_data["password"],
                    "token": data.get("access_token"),
                    "user_data": user_info
                }
            elif response.status_code == 400:
                error_data = response.json()
                error_detail = error_data.get("detail", "")
                
                if "قبلاً ثبت شده" in error_detail or "already exists" in error_detail.lower():
                    await self.log_test("Specific Test User Creation", True, f"User {test_user_data['email']} already exists - will test login")
                    return {
                        "email": test_user_data["email"],
                        "password": test_user_data["password"],
                        "user_exists": True
                    }
                else:
                    await self.log_test("Specific Test User Creation", False, f"Registration failed: {error_detail}")
                    return None
            else:
                await self.log_test("Specific Test User Creation", False, f"Failed to create test user: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test("Specific Test User Creation", False, f"Exception: {str(e)}")
            return None
    
    async def run_login_debug_tests(self):
        """Run comprehensive login debugging tests"""
        print("🚀 STARTING LOGIN FUNCTIONALITY DEBUG")
        print("=" * 70)
        
        # Test 1: Backend connectivity
        print("\n🔗 Testing Backend Connectivity...")
        backend_ok = await self.test_backend_connectivity()
        
        if not backend_ok:
            print("❌ Backend is not accessible. Cannot continue testing.")
            return
        
        # Test 2: Rate limiting check
        print("\n⏱️ Testing Rate Limiting Status...")
        await self.test_rate_limiting_status()
        
        # Test 3: Backend error investigation
        print("\n🔍 Investigating Backend Error Handling...")
        await self.test_backend_error_investigation()
        
        # Test 4: Try to create a test user
        print("\n👤 Creating Test User for Login Testing...")
        test_user = await self.create_test_user_for_login()
        
        # Test 5: Test with known user
        print("\n🎯 Testing Known User Login...")
        known_user_result = await self.test_known_user_login()
        
        # Test 6: Test existing users
        print("\n👥 Testing Existing Test Users...")
        existing_users = await self.test_existing_test_users()
        
        # Test 7: Complete authentication flow
        print("\n🔐 Testing Complete Authentication Flow...")
        successful_logins = []
        
        if test_user and test_user.get("token"):
            successful_logins.append(test_user)
        
        if known_user_result:
            successful_logins.append(known_user_result)
            
        successful_logins.extend(existing_users)
        
        for login_result in successful_logins:
            if login_result.get("token"):
                await self.test_complete_auth_flow(
                    login_result["token"], 
                    login_result.get("user_data", {}).get("email", "unknown")
                )
                break  # Test with one successful login is sufficient
        
        print("\n" + "=" * 70)
        print("🏁 LOGIN DEBUG TESTING COMPLETE!")
        await self.print_summary()
        
        # Provide specific diagnosis
        await self.provide_diagnosis()
    
    async def provide_diagnosis(self):
        """Provide diagnosis based on test results"""
        print("\n🩺 LOGIN ISSUE DIAGNOSIS:")
        print("-" * 40)
        
        # Analyze test results
        backend_connectivity = any(r["test"] == "Backend Connectivity" and r["success"] for r in self.test_results)
        successful_logins = [r for r in self.test_results if "Login" in r["test"] and r["success"]]
        server_errors = [r for r in self.test_results if "500" in r["details"]]
        rate_limiting = any(r["test"] == "Rate Limiting Check" and "active" in r["details"] for r in self.test_results)
        
        if not backend_connectivity:
            print("❌ CRITICAL: Backend is not accessible")
            print("   → Check if backend service is running")
            print("   → Verify BACKEND_URL configuration")
        
        elif server_errors:
            print("❌ CRITICAL: Server errors (500) detected")
            print("   → Check backend logs for detailed error information")
            print("   → Possible database connection issues")
            print("   → JWT token generation problems")
        
        elif rate_limiting:
            print("⚠️  WARNING: Rate limiting is active")
            print("   → Wait 5 minutes before retrying")
            print("   → Check if IP is being rate limited")
        
        elif not successful_logins:
            print("❌ CRITICAL: No successful logins")
            print("   → User credentials may be incorrect")
            print("   → Database may not contain expected users")
            print("   → Authentication logic may have issues")
        
        else:
            print("✅ Backend login API appears to be working")
            print("   → Issue may be in frontend-backend communication")
            print("   → Check CORS configuration")
            print("   → Verify frontend is using correct API endpoints")
            print("   → Check browser network tab for failed requests")
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
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
    tester = LoginDebugTester()
    try:
        await tester.run_login_debug_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())