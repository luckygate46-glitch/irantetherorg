#!/usr/bin/env python3
"""
Backward Compatibility Testing for Iranian Crypto Exchange Authentication System
Tests the specific scenarios requested in the review:
1. Create test user with new registration system (first_name, last_name, email, phone, password)
2. Test that existing users without first_name/last_name can still login  
3. Verify that the login API no longer returns 500 errors
4. Test user profile retrieval (/auth/me) works for both new and existing users
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import bcrypt

# Configuration
BACKEND_URL = "https://irancraft.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class BackwardCompatibilityTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.db_client = None
        self.db = None
        
    async def setup_database_connection(self):
        """Setup direct database connection for creating test users"""
        try:
            # Use the same MongoDB URL from backend
            mongo_url = "mongodb://localhost:27017"
            self.db_client = AsyncIOMotorClient(mongo_url)
            self.db = self.db_client["test_database"]
            return True
        except Exception as e:
            print(f"❌ Could not connect to database: {str(e)}")
            return False
        
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
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    async def create_legacy_user_in_db(self, email: str, password: str, phone: str) -> Optional[str]:
        """Create a legacy user directly in database (without first_name/last_name)"""
        try:
            if not self.db:
                await self.log_test("Create Legacy User", False, "Database connection not available")
                return None
                
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "email": email,
                "password_hash": self.hash_password(password),
                "phone": phone,
                # Note: first_name and last_name are intentionally missing for backward compatibility test
                "is_active": True,
                "is_phone_verified": True,
                "kyc_level": 0,
                "kyc_status": "pending",
                "is_admin": False,
                "wallet_balance_tmn": 0.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Check if user already exists
            existing = await self.db.users.find_one({"email": email})
            if existing:
                await self.log_test("Create Legacy User", True, f"Legacy user {email} already exists")
                return existing["id"]
            
            await self.db.users.insert_one(user_data)
            await self.log_test("Create Legacy User", True, f"Created legacy user {email} without first_name/last_name")
            return user_id
            
        except Exception as e:
            await self.log_test("Create Legacy User", False, f"Exception: {str(e)}")
            return None
    
    async def create_new_user_via_api(self, first_name: str, last_name: str, email: str, phone: str, password: str) -> Optional[Dict[str, Any]]:
        """Create a new user via API with all new fields"""
        try:
            # First, create OTP verification record directly in database
            if self.db:
                otp_data = {
                    "id": str(uuid.uuid4()),
                    "phone": phone,
                    "code": "12345",
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow(),  # Will be extended by 5 minutes in the actual implementation
                    "verified": True
                }
                await self.db.otp_verifications.insert_one(otp_data)
            
            # Now try registration
            register_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "password": password
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify full_name computation
                expected_full_name = f"{first_name} {last_name}"
                if user_info.get("full_name") == expected_full_name:
                    await self.log_test("Create New User via API", True, f"Created user {email} with computed full_name: '{expected_full_name}'")
                else:
                    await self.log_test("Create New User via API", False, f"full_name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
                
                return {
                    "email": email,
                    "password": password,
                    "token": data.get("access_token"),
                    "user_data": user_info,
                    "success": True
                }
            else:
                await self.log_test("Create New User via API", False, f"Registration failed: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test("Create New User via API", False, f"Exception: {str(e)}")
            return None
    
    async def test_login_functionality(self, email: str, password: str, user_type: str) -> Optional[Dict[str, Any]]:
        """Test login functionality for both new and legacy users"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify no 500 errors
                await self.log_test(f"Login No 500 Error ({user_type})", True, f"Login successful for {user_type} user - no 500 error")
                
                # Verify response structure
                required_fields = ["id", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                missing_fields = [field for field in required_fields if field not in user_info]
                
                if not missing_fields:
                    await self.log_test(f"Login Response Structure ({user_type})", True, "All required fields present in login response")
                else:
                    await self.log_test(f"Login Response Structure ({user_type})", False, f"Missing fields: {missing_fields}")
                
                # Test full_name computation for legacy users
                if user_type == "legacy":
                    # For legacy users, full_name should fallback to email username
                    expected_fallback = email.split('@')[0]
                    actual_full_name = user_info.get("full_name")
                    
                    if actual_full_name == expected_fallback:
                        await self.log_test(f"Legacy User Full Name Fallback", True, f"Correctly computed fallback full_name: '{actual_full_name}'")
                    else:
                        await self.log_test(f"Legacy User Full Name Fallback", False, f"Expected fallback '{expected_fallback}', got '{actual_full_name}'")
                
                return {
                    "token": data.get("access_token"),
                    "user_data": user_info,
                    "success": True
                }
            elif response.status_code == 500:
                await self.log_test(f"Login 500 Error Check ({user_type})", False, f"LOGIN STILL RETURNS 500 ERROR: {response.text}")
                return None
            else:
                await self.log_test(f"Login ({user_type})", False, f"Login failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test(f"Login ({user_type})", False, f"Exception: {str(e)}")
            return None
    
    async def test_user_profile_retrieval(self, token: str, user_type: str, expected_data: Dict[str, Any]) -> bool:
        """Test user profile retrieval via /auth/me"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Verify all required fields are present
                required_fields = ["id", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                missing_fields = [field for field in required_fields if field not in user_data]
                
                if not missing_fields:
                    await self.log_test(f"Profile Retrieval Structure ({user_type})", True, "All required fields present in profile")
                else:
                    await self.log_test(f"Profile Retrieval Structure ({user_type})", False, f"Missing fields: {missing_fields}")
                
                # Verify email matches
                if user_data.get("email") == expected_data.get("email"):
                    await self.log_test(f"Profile Email Match ({user_type})", True, "Email matches expected value")
                else:
                    await self.log_test(f"Profile Email Match ({user_type})", False, f"Email mismatch: expected {expected_data.get('email')}, got {user_data.get('email')}")
                
                # Test full_name computation
                if user_type == "new":
                    expected_full_name = f"{expected_data.get('first_name', '')} {expected_data.get('last_name', '')}"
                    if user_data.get("full_name") == expected_full_name:
                        await self.log_test(f"Profile Full Name ({user_type})", True, f"Correctly computed full_name: '{expected_full_name}'")
                    else:
                        await self.log_test(f"Profile Full Name ({user_type})", False, f"full_name error: expected '{expected_full_name}', got '{user_data.get('full_name')}'")
                elif user_type == "legacy":
                    # For legacy users, should fallback to email username
                    expected_fallback = expected_data.get("email", "").split('@')[0]
                    if user_data.get("full_name") == expected_fallback:
                        await self.log_test(f"Profile Full Name Fallback ({user_type})", True, f"Correctly used fallback full_name: '{expected_fallback}'")
                    else:
                        await self.log_test(f"Profile Full Name Fallback ({user_type})", False, f"Expected fallback '{expected_fallback}', got '{user_data.get('full_name')}'")
                
                await self.log_test(f"Profile Retrieval ({user_type})", True, "Profile retrieval successful")
                return True
            else:
                await self.log_test(f"Profile Retrieval ({user_type})", False, f"Profile retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Profile Retrieval ({user_type})", False, f"Exception: {str(e)}")
            return False
    
    async def create_admin_user_if_needed(self) -> Optional[str]:
        """Create admin user if it doesn't exist"""
        try:
            if not self.db:
                return None
                
            # Check if admin exists
            admin = await self.db.users.find_one({"email": "admin@test.com"})
            if admin:
                await self.log_test("Admin User Exists", True, "Admin user already exists")
                return admin["id"]
            
            # Create admin user
            admin_id = str(uuid.uuid4())
            admin_data = {
                "id": admin_id,
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@test.com",
                "password_hash": self.hash_password("admin123"),
                "phone": "09100000000",
                "is_active": True,
                "is_phone_verified": True,
                "kyc_level": 2,
                "kyc_status": "approved",
                "is_admin": True,
                "wallet_balance_tmn": 0.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.db.users.insert_one(admin_data)
            await self.log_test("Create Admin User", True, "Created admin user: admin@test.com")
            return admin_id
            
        except Exception as e:
            await self.log_test("Create Admin User", False, f"Exception: {str(e)}")
            return None
    
    async def run_backward_compatibility_tests(self):
        """Run the specific backward compatibility tests requested"""
        print("🚀 Starting Backward Compatibility Tests for Authentication System")
        print("=" * 80)
        
        # Setup database connection
        db_connected = await self.setup_database_connection()
        
        # Test Scenario 1: Create new user with new registration system
        print("\n📝 Test Scenario 1: Create test user with new registration system")
        new_user_data = {
            "first_name": "Test",
            "last_name": "User", 
            "email": "testuser@example.com",
            "phone": "09123456789",
            "password": "testpass123"
        }
        
        new_user_result = await self.create_new_user_via_api(**new_user_data)
        
        # Test Scenario 2: Create admin user
        print("\n👨‍💼 Test Scenario 2: Create admin user if not exists")
        admin_user_data = {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@test.com", 
            "phone": "09100000000",
            "password": "admin123"
        }
        
        admin_id = await self.create_admin_user_if_needed()
        
        # Test Scenario 3: Create legacy user (without first_name/last_name)
        print("\n🔄 Test Scenario 3: Create legacy user without first_name/last_name")
        legacy_user_data = {
            "email": "legacy@example.com",
            "phone": "09987654321", 
            "password": "legacy123"
        }
        
        legacy_user_id = None
        if db_connected:
            legacy_user_id = await self.create_legacy_user_in_db(**legacy_user_data)
        else:
            await self.log_test("Create Legacy User", False, "Database connection not available - cannot create legacy user")
        
        # Test Scenario 4: Test login for new user
        print("\n🔐 Test Scenario 4: Test login with newly created users")
        new_user_login = None
        if new_user_result:
            new_user_login = await self.test_login_functionality(
                new_user_data["email"], 
                new_user_data["password"], 
                "new"
            )
        
        # Test login for admin user
        admin_login = await self.test_login_functionality(
            admin_user_data["email"],
            admin_user_data["password"],
            "admin"
        )
        
        # Test login for legacy user
        legacy_user_login = None
        if legacy_user_id:
            legacy_user_login = await self.test_login_functionality(
                legacy_user_data["email"],
                legacy_user_data["password"], 
                "legacy"
            )
        
        # Test Scenario 5: Test user profile retrieval (/auth/me)
        print("\n👤 Test Scenario 5: Test user profile retrieval for both user types")
        
        if new_user_login and new_user_login.get("token"):
            await self.test_user_profile_retrieval(
                new_user_login["token"], 
                "new", 
                new_user_data
            )
        
        if admin_login and admin_login.get("token"):
            await self.test_user_profile_retrieval(
                admin_login["token"],
                "admin",
                admin_user_data
            )
        
        if legacy_user_login and legacy_user_login.get("token"):
            await self.test_user_profile_retrieval(
                legacy_user_login["token"],
                "legacy", 
                legacy_user_data
            )
        
        # Test Scenario 6: Verify no 500 errors on login attempts
        print("\n🚨 Test Scenario 6: Verify no 500 errors on login attempts")
        
        # Test with invalid credentials to ensure proper error handling
        await self.test_login_functionality("nonexistent@test.com", "wrongpass", "invalid")
        
        print("\n" + "=" * 80)
        print("🏁 Backward Compatibility Testing Complete!")
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
        
        # Critical findings
        critical_issues = []
        login_500_errors = [r for r in self.test_results if "500 Error" in r["test"] and not r["success"]]
        if login_500_errors:
            critical_issues.append("🚨 CRITICAL: Login API still returns 500 errors")
        
        backward_compat_failures = [r for r in self.test_results if "legacy" in r["test"].lower() and not r["success"]]
        if backward_compat_failures:
            critical_issues.append("🚨 CRITICAL: Backward compatibility issues found")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"  {issue}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Success indicators
        success_indicators = []
        if any("Create New User via API" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ New registration system working")
        
        if any("Legacy" in r["test"] and "Login" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ Legacy user login working")
        
        if any("No 500 Error" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ No 500 errors on login")
        
        if any("Profile Retrieval" in r["test"] and r["success"] for r in self.test_results):
            success_indicators.append("✅ User profile retrieval working")
        
        if success_indicators:
            print(f"\n✅ SUCCESS INDICATORS:")
            for indicator in success_indicators:
                print(f"  {indicator}")
    
    async def close(self):
        """Close connections"""
        await self.client.aclose()
        if self.db_client:
            self.db_client.close()

async def main():
    """Main test runner"""
    tester = BackwardCompatibilityTester()
    try:
        await tester.run_backward_compatibility_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())