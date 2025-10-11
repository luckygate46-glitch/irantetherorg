#!/usr/bin/env python3
"""
Simplified Registration System Test
Tests the updated registration flow that removes SMS verification requirement
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://cryptotoman.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class SimplifiedRegistrationTester:
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
        
    async def test_simplified_registration(self, first_name: str, last_name: str, email: str, phone: str, password: str = "testpass123") -> Dict[str, Any]:
        """Test simplified registration without OTP requirement"""
        try:
            print(f"\n🔍 Testing Simplified Registration for {email}")
            
            # Test registration with new fields
            register_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "password": password
            }
            
            print(f"📤 Sending registration request: {json.dumps(register_data, ensure_ascii=False)}")
            register_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            print(f"📥 Registration response status: {register_response.status_code}")
            print(f"📥 Registration response: {register_response.text}")
            
            if register_response.status_code in [200, 201]:
                user_data = register_response.json()
                user_info = user_data.get("user", {})
                access_token = user_data.get("access_token")
                
                # Verify registration was successful without OTP
                success_checks = []
                
                # Check 1: User created with correct fields
                if user_info.get("first_name") == first_name:
                    success_checks.append("✅ first_name stored correctly")
                else:
                    success_checks.append(f"❌ first_name mismatch: expected {first_name}, got {user_info.get('first_name')}")
                
                if user_info.get("last_name") == last_name:
                    success_checks.append("✅ last_name stored correctly")
                else:
                    success_checks.append(f"❌ last_name mismatch: expected {last_name}, got {user_info.get('last_name')}")
                
                if user_info.get("email") == email:
                    success_checks.append("✅ email stored correctly")
                else:
                    success_checks.append(f"❌ email mismatch: expected {email}, got {user_info.get('email')}")
                
                if user_info.get("phone") == phone:
                    success_checks.append("✅ phone stored correctly")
                else:
                    success_checks.append(f"❌ phone mismatch: expected {phone}, got {user_info.get('phone')}")
                
                # Check 2: is_phone_verified should be False (no OTP required)
                if user_info.get("is_phone_verified") == False:
                    success_checks.append("✅ is_phone_verified=False (no OTP required)")
                else:
                    success_checks.append(f"❌ is_phone_verified should be False, got {user_info.get('is_phone_verified')}")
                
                # Check 3: JWT token generated
                if access_token:
                    success_checks.append("✅ JWT token generated")
                else:
                    success_checks.append("❌ No JWT token generated")
                
                # Check 4: full_name computed correctly
                expected_full_name = f"{first_name} {last_name}"
                if user_info.get("full_name") == expected_full_name:
                    success_checks.append(f"✅ full_name computed correctly: '{expected_full_name}'")
                else:
                    success_checks.append(f"❌ full_name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
                
                # Check 5: User fields saved correctly
                required_fields = ["id", "first_name", "last_name", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                missing_fields = [field for field in required_fields if field not in user_info]
                
                if not missing_fields:
                    success_checks.append("✅ All required user fields present")
                else:
                    success_checks.append(f"❌ Missing user fields: {missing_fields}")
                
                all_success = all("✅" in check for check in success_checks)
                
                await self.log_test(f"Simplified Registration {email}", all_success, "; ".join(success_checks))
                
                return {
                    "email": email,
                    "phone": phone,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "token": access_token,
                    "user_id": user_info.get("id"),
                    "user_data": user_info,
                    "success": all_success,
                    "checks": success_checks
                }
                
            elif register_response.status_code == 400:
                error_data = register_response.json()
                error_detail = error_data.get("detail", "")
                
                # Check if it's a duplicate user error (expected for existing users)
                if "قبلاً ثبت شده" in error_detail or "already" in error_detail.lower():
                    await self.log_test(f"Registration Duplicate Check {email}", True, f"Correctly rejected duplicate registration: {error_detail}")
                    return {"success": True, "duplicate": True, "error": error_detail}
                else:
                    await self.log_test(f"Simplified Registration {email}", False, f"Registration failed with 400: {error_detail}")
                    return {"success": False, "error": error_detail}
                    
            else:
                error_detail = register_response.text
                await self.log_test(f"Simplified Registration {email}", False, f"Registration failed with {register_response.status_code}: {error_detail}")
                return {"success": False, "error": error_detail, "status_code": register_response.status_code}
                
        except Exception as e:
            await self.log_test(f"Simplified Registration {email}", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_login_after_registration(self, email: str, password: str) -> Dict[str, Any]:
        """Test login after successful registration"""
        try:
            print(f"\n🔐 Testing Login After Registration for {email}")
            
            login_data = {
                "email": email,
                "password": password
            }
            
            print(f"📤 Sending login request: {json.dumps(login_data, ensure_ascii=False)}")
            login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            print(f"📥 Login response status: {login_response.status_code}")
            print(f"📥 Login response: {login_response.text}")
            
            if login_response.status_code == 200:
                data = login_response.json()
                user_info = data.get("user", {})
                access_token = data.get("access_token")
                
                # Verify login response
                success_checks = []
                
                if access_token:
                    success_checks.append("✅ JWT token received")
                else:
                    success_checks.append("❌ No JWT token received")
                
                if user_info.get("email") == email:
                    success_checks.append("✅ User email matches")
                else:
                    success_checks.append(f"❌ User email mismatch: expected {email}, got {user_info.get('email')}")
                
                # Check user can access dashboard (test token validity)
                if access_token:
                    headers = {"Authorization": f"Bearer {access_token}"}
                    me_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                    
                    if me_response.status_code == 200:
                        success_checks.append("✅ Can access user profile (/auth/me)")
                        me_data = me_response.json()
                        
                        # Verify profile data
                        if me_data.get("email") == email:
                            success_checks.append("✅ Profile data matches login")
                        else:
                            success_checks.append("❌ Profile data mismatch")
                    else:
                        success_checks.append(f"❌ Cannot access user profile: {me_response.status_code}")
                
                all_success = all("✅" in check for check in success_checks)
                
                await self.log_test(f"Login After Registration {email}", all_success, "; ".join(success_checks))
                
                return {
                    "success": all_success,
                    "token": access_token,
                    "user_data": user_info,
                    "checks": success_checks
                }
                
            elif login_response.status_code == 401:
                await self.log_test(f"Login After Registration {email}", False, "Login failed: Invalid credentials")
                return {"success": False, "error": "Invalid credentials"}
            else:
                error_detail = login_response.text
                await self.log_test(f"Login After Registration {email}", False, f"Login failed with {login_response.status_code}: {error_detail}")
                return {"success": False, "error": error_detail}
                
        except Exception as e:
            await self.log_test(f"Login After Registration {email}", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_backend_accessibility(self):
        """Test if backend registration endpoint is accessible"""
        try:
            print(f"\n🌐 Testing Backend Accessibility")
            
            # Test basic connectivity
            response = await self.client.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                await self.log_test("Backend Connectivity", True, f"Backend accessible at {BACKEND_URL}")
            else:
                await self.log_test("Backend Connectivity", False, f"Backend not accessible: {response.status_code}")
                return False
            
            # Test registration endpoint accessibility (should return 422 for missing data)
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json={})
            
            if response.status_code == 422:  # Validation error expected
                await self.log_test("Registration Endpoint Accessibility", True, "Registration endpoint accessible and validates input")
                return True
            else:
                await self.log_test("Registration Endpoint Accessibility", False, f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_test("Backend Accessibility", False, f"Exception: {str(e)}")
            return False
    
    async def check_backend_logs(self):
        """Check backend logs for any errors"""
        try:
            print(f"\n📋 Checking Backend Service Status")
            
            # This is a placeholder - in a real environment, we'd check supervisor logs
            # For now, we'll just test if the service is responding
            response = await self.client.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                await self.log_test("Backend Service Status", True, "Backend service is running")
            else:
                await self.log_test("Backend Service Status", False, f"Backend service issue: {response.status_code}")
                
        except Exception as e:
            await self.log_test("Backend Service Status", False, f"Exception: {str(e)}")
    
    async def run_simplified_registration_tests(self):
        """Run the simplified registration tests as requested"""
        print("🚀 Starting Simplified Registration System Tests")
        print("=" * 70)
        
        # Test 1: Backend accessibility
        backend_accessible = await self.test_backend_accessibility()
        if not backend_accessible:
            print("❌ Backend not accessible. Cannot continue tests.")
            return
        
        # Test 2: Check backend service status
        await self.check_backend_logs()
        
        # Test 3: Critical Test - Simple Registration Test
        print(f"\n🎯 CRITICAL TEST: Simple Registration Test")
        
        test_user = {
            "first_name": "احمد",
            "last_name": "محمدی", 
            "email": "ahmad.simple.test@example.com",
            "phone": "09123456789",
            "password": "testpass123"
        }
        
        registration_result = await self.test_simplified_registration(
            test_user["first_name"],
            test_user["last_name"],
            test_user["email"],
            test_user["phone"],
            test_user["password"]
        )
        
        # Test 4: User Login Test (if registration was successful)
        if registration_result.get("success") and not registration_result.get("duplicate"):
            print(f"\n🔐 USER LOGIN TEST")
            login_result = await self.test_login_after_registration(
                test_user["email"],
                test_user["password"]
            )
            
            if login_result.get("success"):
                print("✅ Complete flow working: Registration → Login → Dashboard access")
            else:
                print("❌ Login failed after registration")
        
        elif registration_result.get("duplicate"):
            print(f"\n🔐 USER LOGIN TEST (Existing User)")
            # Try to login with existing user
            login_result = await self.test_login_after_registration(
                test_user["email"],
                test_user["password"]
            )
        
        # Test 5: Additional test users to verify consistency
        print(f"\n🔄 CONSISTENCY TESTS")
        
        additional_users = [
            {
                "first_name": "سارا",
                "last_name": "کریمی",
                "email": "sara.simple.test@example.com", 
                "phone": "09123456790",
                "password": "testpass456"
            },
            {
                "first_name": "محمد",
                "last_name": "رضایی",
                "email": "mohammad.simple.test@example.com",
                "phone": "09123456791", 
                "password": "testpass789"
            }
        ]
        
        for user in additional_users:
            result = await self.test_simplified_registration(
                user["first_name"],
                user["last_name"],
                user["email"],
                user["phone"],
                user["password"]
            )
            
            # Test login for successful registrations
            if result.get("success") and not result.get("duplicate"):
                await self.test_login_after_registration(user["email"], user["password"])
        
        print("\n" + "=" * 70)
        print("🏁 Simplified Registration Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Specific analysis for the review request
        print(f"\n🎯 REVIEW REQUEST ANALYSIS:")
        
        registration_tests = [r for r in self.test_results if "Simplified Registration" in r["test"]]
        login_tests = [r for r in self.test_results if "Login After Registration" in r["test"]]
        
        if registration_tests:
            successful_registrations = [r for r in registration_tests if r["success"]]
            print(f"📝 Registration Tests: {len(successful_registrations)}/{len(registration_tests)} successful")
            
            if successful_registrations:
                print("✅ SIMPLIFIED REGISTRATION WORKING: Users can register without OTP verification")
            else:
                print("❌ SIMPLIFIED REGISTRATION FAILING: Backend issues preventing registration")
        
        if login_tests:
            successful_logins = [r for r in login_tests if r["success"]]
            print(f"🔐 Login Tests: {len(successful_logins)}/{len(login_tests)} successful")
            
            if successful_logins:
                print("✅ LOGIN AFTER REGISTRATION WORKING: Users can login and access dashboard")
            else:
                print("❌ LOGIN AFTER REGISTRATION FAILING: Authentication issues")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = SimplifiedRegistrationTester()
    try:
        await tester.run_simplified_registration_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())