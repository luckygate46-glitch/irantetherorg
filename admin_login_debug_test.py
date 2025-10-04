#!/usr/bin/env python3
"""
Admin Login Debug Test for Iranian Crypto Exchange
Specifically tests admin user existence and login functionality
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://tehcrypto.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class AdminLoginDebugger:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.admin_token = None
        
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
        
    async def test_admin_login_api(self, email: str = "admin", password: str = "istari118") -> Dict[str, Any]:
        """Test admin login API with specific credentials"""
        try:
            print(f"\n🔐 Testing Admin Login API with credentials: {email}/{password}")
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            print(f"Login Response Status: {response.status_code}")
            print(f"Login Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify admin privileges
                is_admin = user_info.get("is_admin", False)
                if is_admin:
                    await self.log_test("Admin Login Success", True, f"Successfully logged in as admin user: {user_info.get('email')}")
                    self.admin_token = data.get("access_token")
                    
                    # Verify token structure
                    if self.admin_token:
                        await self.log_test("JWT Token Generation", True, f"JWT token generated successfully (length: {len(self.admin_token)})")
                    else:
                        await self.log_test("JWT Token Generation", False, "No access token in response")
                    
                    # Verify user data structure
                    required_fields = ["id", "email", "is_admin", "kyc_level", "kyc_status"]
                    missing_fields = [field for field in required_fields if field not in user_info]
                    
                    if not missing_fields:
                        await self.log_test("Admin User Data Structure", True, "All required admin fields present")
                    else:
                        await self.log_test("Admin User Data Structure", False, f"Missing fields: {missing_fields}")
                    
                    return {
                        "success": True,
                        "token": self.admin_token,
                        "user_data": user_info,
                        "is_admin": is_admin
                    }
                else:
                    await self.log_test("Admin Login Success", False, f"User logged in but is not admin: is_admin={is_admin}")
                    return {"success": False, "error": "User is not admin"}
                    
            elif response.status_code == 401:
                await self.log_test("Admin Login Success", False, f"Authentication failed: {response.text}")
                return {"success": False, "error": "Authentication failed", "status_code": 401}
            elif response.status_code == 422:
                await self.log_test("Admin Login Success", False, f"Validation error: {response.text}")
                return {"success": False, "error": "Validation error", "status_code": 422}
            else:
                await self.log_test("Admin Login Success", False, f"Unexpected status {response.status_code}: {response.text}")
                return {"success": False, "error": f"Status {response.status_code}", "response": response.text}
                
        except Exception as e:
            await self.log_test("Admin Login API", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_admin_endpoints_access(self, token: str) -> bool:
        """Test access to admin-only endpoints"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test admin stats endpoint
            print(f"\n📊 Testing Admin Stats Endpoint...")
            stats_response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                await self.log_test("Admin Stats Access", True, f"Successfully accessed admin stats: {len(stats_data)} fields")
                print(f"Stats Data: {json.dumps(stats_data, indent=2)}")
            else:
                await self.log_test("Admin Stats Access", False, f"Failed to access admin stats: {stats_response.status_code} - {stats_response.text}")
            
            # Test admin users endpoint
            print(f"\n👥 Testing Admin Users Endpoint...")
            users_response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                await self.log_test("Admin Users Access", True, f"Successfully accessed admin users: {len(users_data)} users")
                
                # Look for admin user in the list
                admin_user = None
                for user in users_data:
                    if user.get("email") == "admin" and user.get("is_admin"):
                        admin_user = user
                        break
                
                if admin_user:
                    await self.log_test("Admin User Found in Database", True, f"Admin user found: ID={admin_user.get('id')}, Email={admin_user.get('email')}")
                    print(f"Admin User Data: {json.dumps(admin_user, indent=2, default=str)}")
                else:
                    await self.log_test("Admin User Found in Database", False, "Admin user with email 'admin' not found in users list")
                    
            else:
                await self.log_test("Admin Users Access", False, f"Failed to access admin users: {users_response.status_code} - {users_response.text}")
            
            # Test admin orders endpoint
            print(f"\n📋 Testing Admin Orders Endpoint...")
            orders_response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            
            if orders_response.status_code == 200:
                orders_data = orders_response.json()
                await self.log_test("Admin Orders Access", True, f"Successfully accessed admin orders: {len(orders_data)} orders")
            else:
                await self.log_test("Admin Orders Access", False, f"Failed to access admin orders: {orders_response.status_code} - {orders_response.text}")
            
            # Test admin KYC pending endpoint
            print(f"\n🆔 Testing Admin KYC Pending Endpoint...")
            kyc_response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            
            if kyc_response.status_code == 200:
                kyc_data = kyc_response.json()
                await self.log_test("Admin KYC Access", True, f"Successfully accessed admin KYC: {len(kyc_data)} pending requests")
            else:
                await self.log_test("Admin KYC Access", False, f"Failed to access admin KYC: {kyc_response.status_code} - {kyc_response.text}")
            
            # Test admin AI insights endpoint
            print(f"\n🤖 Testing Admin AI Insights Endpoint...")
            ai_response = await self.client.get(f"{BACKEND_URL}/admin/ai/insights", headers=headers)
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                await self.log_test("Admin AI Insights Access", True, f"Successfully accessed admin AI insights")
                print(f"AI Insights: {json.dumps(ai_data, indent=2, default=str)}")
            else:
                await self.log_test("Admin AI Insights Access", False, f"Failed to access admin AI insights: {ai_response.status_code} - {ai_response.text}")
            
            return True
            
        except Exception as e:
            await self.log_test("Admin Endpoints Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_jwt_token_validation(self, token: str) -> bool:
        """Test JWT token validation with protected endpoints"""
        try:
            print(f"\n🔑 Testing JWT Token Validation...")
            
            # Test with valid token
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                await self.log_test("JWT Token Validation (Valid)", True, f"Token validated successfully for user: {user_data.get('email')}")
                
                # Verify admin status in token
                if user_data.get("is_admin"):
                    await self.log_test("JWT Admin Status", True, "Token correctly contains admin privileges")
                else:
                    await self.log_test("JWT Admin Status", False, "Token does not contain admin privileges")
                
            else:
                await self.log_test("JWT Token Validation (Valid)", False, f"Valid token rejected: {response.status_code} - {response.text}")
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            invalid_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=invalid_headers)
            
            if invalid_response.status_code == 401:
                await self.log_test("JWT Token Validation (Invalid)", True, "Invalid token correctly rejected")
            else:
                await self.log_test("JWT Token Validation (Invalid)", False, f"Invalid token not rejected: {invalid_response.status_code}")
            
            # Test with no token
            no_token_response = await self.client.get(f"{BACKEND_URL}/auth/me")
            
            if no_token_response.status_code == 401 or no_token_response.status_code == 403:
                await self.log_test("JWT Token Validation (Missing)", True, "Missing token correctly rejected")
            else:
                await self.log_test("JWT Token Validation (Missing)", False, f"Missing token not rejected: {no_token_response.status_code}")
            
            return True
            
        except Exception as e:
            await self.log_test("JWT Token Validation", False, f"Exception: {str(e)}")
            return False
    
    async def test_database_admin_user_query(self) -> bool:
        """Test if we can verify admin user exists through API calls"""
        try:
            print(f"\n🗄️ Testing Database Admin User Query...")
            
            # Since we can't directly query the database, we'll use the admin endpoints
            # First, try to login and then check if we can access admin data
            
            login_result = await self.test_admin_login_api()
            
            if login_result.get("success") and login_result.get("token"):
                # If login successful, admin user definitely exists
                await self.log_test("Database Admin User Exists", True, "Admin user exists and can login successfully")
                
                # Get user details through /auth/me
                headers = {"Authorization": f"Bearer {login_result['token']}"}
                me_response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    await self.log_test("Admin User Data Integrity", True, f"Admin user data complete: email={user_data.get('email')}, is_admin={user_data.get('is_admin')}, kyc_level={user_data.get('kyc_level')}")
                    
                    # Check password hash verification (implicit through successful login)
                    await self.log_test("Admin Password Hash Verification", True, "Password hash correctly verified (login successful)")
                    
                    return True
                else:
                    await self.log_test("Admin User Data Retrieval", False, f"Failed to get admin user data: {me_response.status_code}")
                    return False
            else:
                await self.log_test("Database Admin User Exists", False, f"Admin user login failed: {login_result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            await self.log_test("Database Admin User Query", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_login_response_format(self) -> bool:
        """Test that admin login response matches frontend expectations"""
        try:
            print(f"\n📋 Testing Admin Login Response Format...")
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "admin",
                "password": "istari118"
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required top-level fields
                required_top_fields = ["access_token", "token_type", "user"]
                missing_top_fields = [field for field in required_top_fields if field not in data]
                
                if not missing_top_fields:
                    await self.log_test("Login Response Top-Level Fields", True, "All required top-level fields present")
                else:
                    await self.log_test("Login Response Top-Level Fields", False, f"Missing top-level fields: {missing_top_fields}")
                
                # Check token type
                if data.get("token_type") == "bearer":
                    await self.log_test("Login Response Token Type", True, "Token type is 'bearer'")
                else:
                    await self.log_test("Login Response Token Type", False, f"Token type is '{data.get('token_type')}', expected 'bearer'")
                
                # Check user object structure
                user_data = data.get("user", {})
                required_user_fields = ["id", "email", "is_admin", "kyc_level", "kyc_status", "is_active"]
                missing_user_fields = [field for field in required_user_fields if field not in user_data]
                
                if not missing_user_fields:
                    await self.log_test("Login Response User Fields", True, "All required user fields present")
                else:
                    await self.log_test("Login Response User Fields", False, f"Missing user fields: {missing_user_fields}")
                
                # Print full response for debugging
                print(f"Full Login Response: {json.dumps(data, indent=2, default=str)}")
                
                return True
            else:
                await self.log_test("Admin Login Response Format", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin Login Response Format", False, f"Exception: {str(e)}")
            return False
    
    async def run_admin_debug_tests(self):
        """Run comprehensive admin login debug tests"""
        print("🚀 Starting Admin Login Debug Tests")
        print("=" * 70)
        
        # Test 1: Verify admin user exists and can login
        print("\n🔐 CRITICAL TEST 1: Admin User Login")
        login_result = await self.test_admin_login_api()
        
        if not login_result.get("success"):
            print("❌ CRITICAL FAILURE: Admin login failed!")
            print(f"Error: {login_result.get('error')}")
            print(f"Status Code: {login_result.get('status_code')}")
            
            # Try alternative credentials or debug further
            print("\n🔍 Trying alternative debugging approaches...")
            
            # Test with different potential admin emails
            alternative_emails = ["admin@example.com", "admin@tehcrypto.com", "administrator"]
            for alt_email in alternative_emails:
                print(f"\nTrying alternative email: {alt_email}")
                alt_result = await self.test_admin_login_api(alt_email, "istari118")
                if alt_result.get("success"):
                    login_result = alt_result
                    break
        
        # Test 2: Database admin user verification
        print("\n🗄️ CRITICAL TEST 2: Database Admin User Query")
        await self.test_database_admin_user_query()
        
        # Test 3: Login response format
        print("\n📋 CRITICAL TEST 3: Login Response Format")
        await self.test_admin_login_response_format()
        
        # Test 4: JWT token validation (if login successful)
        if login_result.get("success") and login_result.get("token"):
            print("\n🔑 CRITICAL TEST 4: JWT Token Validation")
            await self.test_jwt_token_validation(login_result["token"])
            
            # Test 5: Admin endpoints access
            print("\n🔒 CRITICAL TEST 5: Admin Endpoints Access")
            await self.test_admin_endpoints_access(login_result["token"])
        else:
            print("\n❌ SKIPPING JWT and Admin Endpoint Tests - Login Failed")
        
        print("\n" + "=" * 70)
        print("🏁 Admin Login Debug Tests Complete!")
        await self.print_summary()
        
        # Provide specific recommendations
        await self.provide_recommendations()
    
    async def provide_recommendations(self):
        """Provide specific recommendations based on test results"""
        print("\n🔧 RECOMMENDATIONS:")
        
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        if not failed_tests:
            print("✅ All tests passed! Admin login is working correctly.")
            return
        
        # Analyze failures and provide specific recommendations
        login_failed = any("Admin Login Success" in test["test"] for test in failed_tests)
        token_failed = any("JWT Token" in test["test"] for test in failed_tests)
        endpoints_failed = any("Admin" in test["test"] and "Access" in test["test"] for test in failed_tests)
        
        if login_failed:
            print("❌ CRITICAL: Admin login is failing")
            print("   → Check if admin user exists in database with email 'admin'")
            print("   → Verify password hash for 'istari118' is correct")
            print("   → Ensure is_admin flag is set to true")
            print("   → Check backend logs for authentication errors")
        
        if token_failed:
            print("❌ JWT Token issues detected")
            print("   → Verify JWT_SECRET_KEY is configured correctly")
            print("   → Check token generation and validation logic")
            print("   → Ensure token contains admin privileges")
        
        if endpoints_failed:
            print("❌ Admin endpoint access issues")
            print("   → Verify admin middleware is working correctly")
            print("   → Check if admin routes are properly protected")
            print("   → Ensure admin user has correct permissions")
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 ADMIN LOGIN DEBUG SUMMARY")
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
    debugger = AdminLoginDebugger()
    try:
        await debugger.run_admin_debug_tests()
    finally:
        await debugger.close()

if __name__ == "__main__":
    asyncio.run(main())