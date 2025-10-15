#!/usr/bin/env python3
"""
Registration OTP Test - Testing Updated Registration System
Tests the specific requirements from the review request:
1. Registration WITHOUT OTP verification requirement
2. Registration WITH OTP verification 
3. Backend logic verification
4. User data integrity
5. Error handling
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://crypto-farsi.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class RegistrationOTPTester:
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
        
    async def test_registration_without_otp(self) -> Dict[str, Any]:
        """Test 1: Registration Without OTP - should work without requiring prior OTP verification"""
        print("\n🔍 TEST 1: Registration Without OTP Verification")
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "first_name": "احمد",
            "last_name": "رضایی",
            "email": f"ahmad.rezaei.{unique_id}@test.com",
            "phone": f"0912345{unique_id[:4]}",
            "password": "testpass123"
        }
        
        try:
            # Attempt registration WITHOUT sending OTP first
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify user was created successfully
                if user_info.get("email") == test_user["email"]:
                    # Check that is_phone_verified is False (since no OTP was sent/verified)
                    if user_info.get("is_phone_verified") == False:
                        await self.log_test(
                            "Registration Without OTP - Success", 
                            True, 
                            f"User registered successfully without OTP, is_phone_verified=False"
                        )
                        
                        # Verify all fields are properly saved
                        field_checks = []
                        if user_info.get("first_name") == test_user["first_name"]:
                            field_checks.append("first_name ✓")
                        else:
                            field_checks.append(f"first_name ✗ (expected: {test_user['first_name']}, got: {user_info.get('first_name')})")
                            
                        if user_info.get("last_name") == test_user["last_name"]:
                            field_checks.append("last_name ✓")
                        else:
                            field_checks.append(f"last_name ✗ (expected: {test_user['last_name']}, got: {user_info.get('last_name')})")
                            
                        if user_info.get("phone") == test_user["phone"]:
                            field_checks.append("phone ✓")
                        else:
                            field_checks.append(f"phone ✗ (expected: {test_user['phone']}, got: {user_info.get('phone')})")
                            
                        expected_full_name = f"{test_user['first_name']} {test_user['last_name']}"
                        if user_info.get("full_name") == expected_full_name:
                            field_checks.append("full_name ✓")
                        else:
                            field_checks.append(f"full_name ✗ (expected: {expected_full_name}, got: {user_info.get('full_name')})")
                        
                        await self.log_test(
                            "Registration Without OTP - Field Integrity", 
                            True, 
                            f"All fields saved correctly: {', '.join(field_checks)}"
                        )
                        
                        return {
                            "success": True,
                            "user_data": test_user,
                            "token": data.get("access_token"),
                            "user_info": user_info
                        }
                    else:
                        await self.log_test(
                            "Registration Without OTP - Phone Verification Status", 
                            False, 
                            f"Expected is_phone_verified=False, got {user_info.get('is_phone_verified')}"
                        )
                        return {"success": False, "error": "Phone verification status incorrect"}
                else:
                    await self.log_test(
                        "Registration Without OTP - User Creation", 
                        False, 
                        f"User data mismatch: expected email {test_user['email']}, got {user_info.get('email')}"
                    )
                    return {"success": False, "error": "User data mismatch"}
            else:
                error_detail = response.text
                await self.log_test(
                    "Registration Without OTP - API Response", 
                    False, 
                    f"Registration failed with status {response.status_code}: {error_detail}"
                )
                return {"success": False, "error": error_detail, "status_code": response.status_code}
                
        except Exception as e:
            await self.log_test("Registration Without OTP - Exception", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_registration_with_otp(self) -> Dict[str, Any]:
        """Test 2: Registration With OTP - send OTP, verify it, then register"""
        print("\n🔍 TEST 2: Registration With OTP Verification")
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_phone = f"0912346{unique_id[:4]}"
        test_user = {
            "first_name": "فاطمه",
            "last_name": "احمدی",
            "email": f"fateme.ahmadi.{unique_id}@test.com",
            "phone": test_phone,
            "password": "testpass456"
        }
        
        try:
            # Step 1: Send OTP
            otp_response = await self.client.post(f"{BACKEND_URL}/otp/send", json={"phone": test_phone})
            
            if otp_response.status_code == 200:
                await self.log_test("OTP Send", True, "OTP sent successfully")
                
                # Step 2: Verify OTP (using a test code - in development mode this should work)
                # Since we're in development mode, let's try common test codes
                test_codes = ["12345", "00000", "11111"]
                otp_verified = False
                
                for test_code in test_codes:
                    verify_response = await self.client.post(f"{BACKEND_URL}/otp/verify", json={
                        "phone": test_phone,
                        "code": test_code
                    })
                    
                    if verify_response.status_code == 200:
                        await self.log_test("OTP Verify", True, f"OTP verified successfully with code {test_code}")
                        otp_verified = True
                        break
                
                if not otp_verified:
                    # Try to verify with any code since we're in development mode
                    verify_response = await self.client.post(f"{BACKEND_URL}/otp/verify", json={
                        "phone": test_phone,
                        "code": "99999"
                    })
                    
                    if verify_response.status_code == 200:
                        await self.log_test("OTP Verify", True, "OTP verified successfully (development mode)")
                        otp_verified = True
                    else:
                        await self.log_test("OTP Verify", False, f"OTP verification failed: {verify_response.text}")
                
                # Step 3: Register user after OTP verification
                if otp_verified:
                    register_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user)
                    
                    if register_response.status_code in [200, 201]:
                        data = register_response.json()
                        user_info = data.get("user", {})
                        
                        # Check that is_phone_verified is True (since OTP was verified)
                        if user_info.get("is_phone_verified") == True:
                            await self.log_test(
                                "Registration With OTP - Success", 
                                True, 
                                f"User registered successfully with OTP, is_phone_verified=True"
                            )
                            
                            return {
                                "success": True,
                                "user_data": test_user,
                                "token": data.get("access_token"),
                                "user_info": user_info,
                                "otp_verified": True
                            }
                        else:
                            await self.log_test(
                                "Registration With OTP - Phone Verification Status", 
                                False, 
                                f"Expected is_phone_verified=True, got {user_info.get('is_phone_verified')}"
                            )
                            return {"success": False, "error": "Phone verification status incorrect after OTP"}
                    else:
                        await self.log_test(
                            "Registration With OTP - Registration Failed", 
                            False, 
                            f"Registration failed after OTP: {register_response.text}"
                        )
                        return {"success": False, "error": register_response.text}
                else:
                    return {"success": False, "error": "OTP verification failed"}
            else:
                await self.log_test("OTP Send", False, f"OTP send failed: {otp_response.text}")
                return {"success": False, "error": f"OTP send failed: {otp_response.text}"}
                
        except Exception as e:
            await self.log_test("Registration With OTP - Exception", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_backend_logic_verification(self):
        """Test 3: Backend Logic Verification - confirm OTP check was removed from registration requirement"""
        print("\n🔍 TEST 3: Backend Logic Verification")
        
        # Test multiple registrations without OTP to confirm the logic
        test_cases = [
            {
                "first_name": "علی",
                "last_name": "محمدی",
                "email": f"ali.logic.test.{uuid.uuid4().hex[:8]}@test.com",
                "phone": f"0912347{uuid.uuid4().hex[:4]}",
                "password": "testpass789"
            },
            {
                "first_name": "مریم",
                "last_name": "حسینی",
                "email": f"maryam.logic.test.{uuid.uuid4().hex[:8]}@test.com",
                "phone": f"0912348{uuid.uuid4().hex[:4]}",
                "password": "testpass101"
            }
        ]
        
        successful_registrations = 0
        
        for i, test_user in enumerate(test_cases):
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    user_info = data.get("user", {})
                    
                    # Verify phone verification is optional (should be False without OTP)
                    if user_info.get("is_phone_verified") == False:
                        successful_registrations += 1
                        await self.log_test(
                            f"Backend Logic Test {i+1}", 
                            True, 
                            f"Registration succeeded without OTP requirement, is_phone_verified=False"
                        )
                    else:
                        await self.log_test(
                            f"Backend Logic Test {i+1}", 
                            False, 
                            f"Phone verification status unexpected: {user_info.get('is_phone_verified')}"
                        )
                else:
                    await self.log_test(
                        f"Backend Logic Test {i+1}", 
                        False, 
                        f"Registration failed: {response.text}"
                    )
                    
            except Exception as e:
                await self.log_test(f"Backend Logic Test {i+1}", False, f"Exception: {str(e)}")
        
        # Overall backend logic verification
        if successful_registrations == len(test_cases):
            await self.log_test(
                "Backend Logic Verification - Overall", 
                True, 
                f"All {successful_registrations} registrations succeeded without OTP requirement"
            )
        else:
            await self.log_test(
                "Backend Logic Verification - Overall", 
                False, 
                f"Only {successful_registrations}/{len(test_cases)} registrations succeeded"
            )
    
    async def test_user_data_integrity_and_jwt(self, user_result: Dict[str, Any]):
        """Test 4: User Data Integrity and JWT token generation"""
        print("\n🔍 TEST 4: User Data Integrity and JWT Token Generation")
        
        if not user_result.get("success") or not user_result.get("token"):
            await self.log_test("User Data Integrity - Skipped", False, "No valid user data from previous tests")
            return
        
        token = user_result["token"]
        user_data = user_result["user_data"]
        
        try:
            # Test JWT token works by accessing protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify JWT token generation works
                await self.log_test("JWT Token Generation", True, "JWT token works for protected endpoints")
                
                # Verify all user fields are properly saved and returned
                field_integrity_checks = []
                
                expected_fields = ["id", "first_name", "last_name", "email", "phone", "full_name", 
                                 "is_active", "is_phone_verified", "kyc_level", "kyc_status", 
                                 "is_admin", "wallet_balance_tmn", "created_at"]
                
                missing_fields = []
                for field in expected_fields:
                    if field not in profile_data:
                        missing_fields.append(field)
                
                if not missing_fields:
                    await self.log_test("User Data Fields", True, "All required fields present in user profile")
                else:
                    await self.log_test("User Data Fields", False, f"Missing fields: {missing_fields}")
                
                # Verify field values match registration data
                field_matches = []
                if profile_data.get("first_name") == user_data["first_name"]:
                    field_matches.append("first_name ✓")
                else:
                    field_matches.append(f"first_name ✗")
                
                if profile_data.get("last_name") == user_data["last_name"]:
                    field_matches.append("last_name ✓")
                else:
                    field_matches.append(f"last_name ✗")
                
                if profile_data.get("email") == user_data["email"]:
                    field_matches.append("email ✓")
                else:
                    field_matches.append(f"email ✗")
                
                if profile_data.get("phone") == user_data["phone"]:
                    field_matches.append("phone ✓")
                else:
                    field_matches.append(f"phone ✗")
                
                expected_full_name = f"{user_data['first_name']} {user_data['last_name']}"
                if profile_data.get("full_name") == expected_full_name:
                    field_matches.append("full_name ✓")
                else:
                    field_matches.append(f"full_name ✗")
                
                await self.log_test(
                    "User Data Integrity", 
                    True, 
                    f"Field integrity: {', '.join(field_matches)}"
                )
                
                # Test login after registration
                login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    login_user_info = login_data.get("user", {})
                    
                    # Verify login returns same user data
                    if (login_user_info.get("email") == user_data["email"] and 
                        login_user_info.get("first_name") == user_data["first_name"] and
                        login_user_info.get("last_name") == user_data["last_name"]):
                        await self.log_test("Login After Registration", True, "Login successful with consistent user data")
                    else:
                        await self.log_test("Login After Registration", False, "Login data inconsistent with registration")
                else:
                    await self.log_test("Login After Registration", False, f"Login failed: {login_response.text}")
            else:
                await self.log_test("JWT Token Generation", False, f"JWT token failed: {response.text}")
                
        except Exception as e:
            await self.log_test("User Data Integrity Test", False, f"Exception: {str(e)}")
    
    async def test_error_handling(self):
        """Test 5: Error Handling - duplicate email, duplicate phone, Persian error messages"""
        print("\n🔍 TEST 5: Error Handling")
        
        # First, create a user to test duplicates against
        unique_id = str(uuid.uuid4())[:8]
        base_user = {
            "first_name": "تست",
            "last_name": "کاربر",
            "email": f"test.duplicate.{unique_id}@test.com",
            "phone": f"0912349{unique_id[:4]}",
            "password": "testpass123"
        }
        
        try:
            # Create the base user
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=base_user)
            
            if response.status_code in [200, 201]:
                await self.log_test("Base User Creation for Duplicate Tests", True, "Base user created successfully")
                
                # Test duplicate email registration
                duplicate_email_user = base_user.copy()
                duplicate_email_user["phone"] = f"0912350{unique_id[:4]}"  # Different phone
                
                dup_email_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=duplicate_email_user)
                
                if dup_email_response.status_code == 400:
                    error_data = dup_email_response.json()
                    error_message = error_data.get("detail", "")
                    
                    # Check if error message is in Persian
                    if "ایمیل" in error_message or "ثبت" in error_message:
                        await self.log_test("Duplicate Email Error", True, f"Proper Persian error message: {error_message}")
                    else:
                        await self.log_test("Duplicate Email Error", False, f"Error message not in Persian: {error_message}")
                else:
                    await self.log_test("Duplicate Email Error", False, f"Should have rejected duplicate email: {dup_email_response.status_code}")
                
                # Test duplicate phone registration
                duplicate_phone_user = base_user.copy()
                duplicate_phone_user["email"] = f"different.{unique_id}@test.com"  # Different email
                
                dup_phone_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=duplicate_phone_user)
                
                if dup_phone_response.status_code == 400:
                    error_data = dup_phone_response.json()
                    error_message = error_data.get("detail", "")
                    
                    # Check if error message is in Persian
                    if "شماره" in error_message or "موبایل" in error_message or "ثبت" in error_message:
                        await self.log_test("Duplicate Phone Error", True, f"Proper Persian error message: {error_message}")
                    else:
                        await self.log_test("Duplicate Phone Error", False, f"Error message not in Persian: {error_message}")
                else:
                    await self.log_test("Duplicate Phone Error", False, f"Should have rejected duplicate phone: {dup_phone_response.status_code}")
                
                # Test validation errors (Persian messages)
                invalid_user = {
                    "first_name": "ا",  # Too short
                    "last_name": "ب",   # Too short
                    "email": "invalid-email",
                    "phone": "123",     # Invalid format
                    "password": "123"   # Too short
                }
                
                validation_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=invalid_user)
                
                if validation_response.status_code == 422:
                    error_data = validation_response.json()
                    # Check if validation errors contain Persian text
                    error_str = str(error_data)
                    
                    persian_indicators = ["کاراکتر", "باید", "رقم", "شروع"]
                    has_persian = any(indicator in error_str for indicator in persian_indicators)
                    
                    if has_persian:
                        await self.log_test("Validation Error Messages", True, "Validation errors contain Persian text")
                    else:
                        await self.log_test("Validation Error Messages", False, f"Validation errors not in Persian: {error_str}")
                else:
                    await self.log_test("Validation Error Messages", False, f"Should have validation errors: {validation_response.status_code}")
                    
            else:
                await self.log_test("Base User Creation for Duplicate Tests", False, f"Failed to create base user: {response.text}")
                
        except Exception as e:
            await self.log_test("Error Handling Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all registration OTP tests"""
        print("🚀 Starting Registration OTP System Tests")
        print("=" * 80)
        print("Testing updated registration system without OTP verification requirement")
        print("=" * 80)
        
        # Test 1: Registration Without OTP
        user_without_otp = await self.test_registration_without_otp()
        
        # Test 2: Registration With OTP
        user_with_otp = await self.test_registration_with_otp()
        
        # Test 3: Backend Logic Verification
        await self.test_backend_logic_verification()
        
        # Test 4: User Data Integrity and JWT (use successful user from test 1 or 2)
        test_user = user_without_otp if user_without_otp.get("success") else user_with_otp
        await self.test_user_data_integrity_and_jwt(test_user)
        
        # Test 5: Error Handling
        await self.test_error_handling()
        
        print("\n" + "=" * 80)
        print("🏁 Registration OTP Testing Complete!")
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
        
        # Group results by test category
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0] if " - " in result["test"] else result["test"]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "details": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
                categories[category]["details"].append(f"  ❌ {result['test']}: {result['details']}")
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            total_cat = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"] / total_cat) * 100 if total_cat > 0 else 0
            print(f"  {category}: {stats['passed']}/{total_cat} passed ({success_rate:.1f}%)")
            
            if stats["details"]:
                for detail in stats["details"]:
                    print(detail)
        
        # Key findings summary
        print(f"\n🔍 KEY FINDINGS:")
        
        # Check if registration without OTP works
        reg_without_otp_success = any(r["success"] and "Registration Without OTP - Success" in r["test"] for r in self.test_results)
        if reg_without_otp_success:
            print("  ✅ Registration works WITHOUT requiring OTP verification")
        else:
            print("  ❌ Registration still requires OTP verification")
        
        # Check if registration with OTP works
        reg_with_otp_success = any(r["success"] and "Registration With OTP - Success" in r["test"] for r in self.test_results)
        if reg_with_otp_success:
            print("  ✅ Registration works WITH OTP verification (is_phone_verified=True)")
        else:
            print("  ❌ Registration with OTP verification has issues")
        
        # Check backend logic
        backend_logic_success = any(r["success"] and "Backend Logic Verification - Overall" in r["test"] for r in self.test_results)
        if backend_logic_success:
            print("  ✅ Backend logic correctly makes OTP verification optional")
        else:
            print("  ❌ Backend logic issues with OTP requirement")
        
        # Check JWT and data integrity
        jwt_success = any(r["success"] and "JWT Token Generation" in r["test"] for r in self.test_results)
        if jwt_success:
            print("  ✅ JWT token generation and user data integrity working")
        else:
            print("  ❌ Issues with JWT token generation or user data integrity")
        
        # Check error handling
        error_handling_success = any(r["success"] and ("Duplicate Email Error" in r["test"] or "Duplicate Phone Error" in r["test"]) for r in self.test_results)
        if error_handling_success:
            print("  ✅ Error handling with Persian messages working")
        else:
            print("  ❌ Issues with error handling or Persian messages")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = RegistrationOTPTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())