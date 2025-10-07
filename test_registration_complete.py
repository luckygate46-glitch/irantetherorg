#!/usr/bin/env python3
"""
Complete Registration Flow Test
Tests the full registration flow by manually creating OTP verification
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid

# Configuration
BACKEND_URL = "https://irancraft.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

class CompleteRegistrationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.mongo_client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.mongo_client[DB_NAME]
        self.test_results = []
        
    async def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    async def create_otp_verification(self, phone: str, code: str = "12345") -> bool:
        """Manually create OTP verification record in database"""
        try:
            otp_data = {
                "id": str(uuid.uuid4()),
                "phone": phone,
                "code": code,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
                "verified": True
            }
            
            await self.db.otp_verifications.insert_one(otp_data)
            await self.log_test(f"Create OTP Verification {phone}", True, f"Created verified OTP record with code {code}")
            return True
            
        except Exception as e:
            await self.log_test(f"Create OTP Verification {phone}", False, f"Exception: {str(e)}")
            return False
    
    async def test_complete_registration_flow(self, first_name: str, last_name: str, email: str, phone: str, password: str = "testpass123"):
        """Test complete registration flow with manual OTP verification"""
        try:
            # Step 1: Create OTP verification record manually
            otp_created = await self.create_otp_verification(phone)
            
            if not otp_created:
                return {"success": False, "error": "Could not create OTP verification"}
            
            # Step 2: Test registration with new fields
            register_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "password": password
            }
            
            register_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if register_response.status_code in [200, 201]:
                user_data = register_response.json()
                user_info = user_data.get("user", {})
                
                # Verify all new fields are present and correct
                success = True
                details = []
                
                required_fields = ["id", "first_name", "last_name", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                
                for field in required_fields:
                    if field not in user_info:
                        success = False
                        details.append(f"Missing field: {field}")
                
                # Check field values
                if user_info.get("first_name") != first_name:
                    success = False
                    details.append(f"first_name mismatch: expected {first_name}, got {user_info.get('first_name')}")
                
                if user_info.get("last_name") != last_name:
                    success = False
                    details.append(f"last_name mismatch: expected {last_name}, got {user_info.get('last_name')}")
                
                if user_info.get("email") != email:
                    success = False
                    details.append(f"email mismatch: expected {email}, got {user_info.get('email')}")
                
                if user_info.get("phone") != phone:
                    success = False
                    details.append(f"phone mismatch: expected {phone}, got {user_info.get('phone')}")
                
                # Check if full_name is computed correctly
                expected_full_name = f"{first_name} {last_name}"
                if user_info.get("full_name") != expected_full_name:
                    success = False
                    details.append(f"full_name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
                
                # Check phone verification status
                if not user_info.get("is_phone_verified"):
                    success = False
                    details.append("is_phone_verified should be True after OTP verification")
                
                if success:
                    await self.log_test(f"Complete Registration Flow {email}", True, "Registration successful with all new fields")
                else:
                    await self.log_test(f"Complete Registration Flow {email}", False, "; ".join(details))
                
                return {
                    "success": success,
                    "email": email,
                    "phone": phone,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "token": user_data.get("access_token"),
                    "user_id": user_info.get("id"),
                    "user_data": user_info
                }
            else:
                error_detail = register_response.text
                await self.log_test(f"Complete Registration Flow {email}", False, f"Registration failed: {error_detail}")
                return {"success": False, "error": error_detail}
                
        except Exception as e:
            await self.log_test(f"Complete Registration Flow {email}", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_login_with_new_user(self, email: str, password: str):
        """Test login with newly created user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify user response contains all expected fields
                required_fields = ["id", "first_name", "last_name", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in user_info:
                        missing_fields.append(field)
                
                if missing_fields:
                    await self.log_test(f"Login New User Fields {email}", False, f"Missing fields: {missing_fields}")
                    return {"success": False}
                else:
                    await self.log_test(f"Login New User Fields {email}", True, "All required fields present in login response")
                
                # Verify full_name computation
                expected_full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
                if user_info.get("full_name") == expected_full_name:
                    await self.log_test(f"Login Full Name Computation {email}", True, f"full_name correctly computed as '{expected_full_name}'")
                else:
                    await self.log_test(f"Login Full Name Computation {email}", False, f"full_name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
                
                return {
                    "success": True,
                    "token": data.get("access_token"),
                    "user_data": user_info
                }
            else:
                await self.log_test(f"Login New User {email}", False, f"Login failed: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            await self.log_test(f"Login New User {email}", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_user_profile_endpoint(self, token: str, expected_data: dict):
        """Test /auth/me endpoint with new user"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check all expected fields
                success = True
                details = []
                
                expected_fields = ["id", "first_name", "last_name", "email", "phone", "full_name", "is_active", "is_phone_verified", "kyc_level", "kyc_status", "is_admin", "wallet_balance_tmn", "created_at"]
                
                for field in expected_fields:
                    if field not in user_data:
                        success = False
                        details.append(f"Missing field: {field}")
                
                # Check full_name computation
                expected_full_name = f"{expected_data.get('first_name', '')} {expected_data.get('last_name', '')}"
                if user_data.get("full_name") != expected_full_name:
                    success = False
                    details.append(f"full_name error: expected '{expected_full_name}', got '{user_data.get('full_name')}'")
                
                if success:
                    await self.log_test("User Profile Endpoint", True, "Profile endpoint returns all fields correctly")
                else:
                    await self.log_test("User Profile Endpoint", False, "; ".join(details))
                
                return {"success": success, "user_data": user_data}
            else:
                await self.log_test("User Profile Endpoint", False, f"Failed: {response.text}")
                return {"success": False}
                
        except Exception as e:
            await self.log_test("User Profile Endpoint", False, f"Exception: {str(e)}")
            return {"success": False}
    
    async def run_complete_tests(self):
        """Run complete registration system tests"""
        print("🚀 Starting Complete Registration System Tests")
        print("=" * 70)
        
        # Test complete registration flow
        print("\n📝 Testing Complete Registration Flow...")
        
        test_user = {
            "first_name": "محمد",
            "last_name": "رضایی",
            "email": "mohammad.rezaei@newtest.com",
            "phone": "09123456710",
            "password": "testpass123"
        }
        
        registration_result = await self.test_complete_registration_flow(
            test_user["first_name"],
            test_user["last_name"],
            test_user["email"],
            test_user["phone"],
            test_user["password"]
        )
        
        if registration_result.get("success"):
            print("\n🔐 Testing Login with New User...")
            login_result = await self.test_login_with_new_user(
                test_user["email"],
                test_user["password"]
            )
            
            if login_result.get("success"):
                print("\n👤 Testing User Profile Endpoint...")
                await self.test_user_profile_endpoint(
                    login_result["token"],
                    test_user
                )
        
        print("\n" + "=" * 70)
        print("🏁 Complete Registration Testing Complete!")
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
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
    
    async def close(self):
        """Close connections"""
        await self.client.aclose()
        self.mongo_client.close()

async def main():
    """Main test runner"""
    tester = CompleteRegistrationTester()
    try:
        await tester.run_complete_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())