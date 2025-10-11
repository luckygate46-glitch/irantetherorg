#!/usr/bin/env python3
"""
KYC Functionality Debug Test for Iranian Crypto Exchange
Tests KYC Level 1 submission and validation as reported by user
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

# Test user credentials as provided
TEST_USER_EMAIL = "saruman.valar.test.20251004163014@gmail.com"
TEST_USER_PASSWORD = "password123"

class KYCDebugTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.user_token = None
        
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
        
    async def test_user_login(self) -> bool:
        """Test login with provided user credentials"""
        try:
            print(f"🔐 Testing login for user: {TEST_USER_EMAIL}")
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("access_token")
                user_info = data.get("user", {})
                
                await self.log_test("User Login", True, 
                    f"Login successful. User: {user_info.get('full_name', 'N/A')}, KYC Level: {user_info.get('kyc_level', 0)}")
                return True
            else:
                await self.log_test("User Login", False, f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    async def test_kyc_status_endpoint(self) -> Dict[str, Any]:
        """Test GET /api/kyc/status endpoint"""
        try:
            if not self.user_token:
                await self.log_test("KYC Status Endpoint", False, "No user token available")
                return {}
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                await self.log_test("KYC Status Endpoint", True, 
                    f"Status retrieved: Level {data.get('kyc_level', 0)}, Status: {data.get('kyc_status', 'N/A')}")
                return data
            else:
                await self.log_test("KYC Status Endpoint", False, f"Failed: {response.text}")
                return {}
                
        except Exception as e:
            await self.log_test("KYC Status Endpoint", False, f"Exception: {str(e)}")
            return {}
    
    async def test_kyc_level1_submission(self) -> bool:
        """Test POST /api/kyc/level1 with sample Persian data"""
        try:
            if not self.user_token:
                await self.log_test("KYC Level 1 Submission", False, "No user token available")
                return False
            
            # Sample data as provided in the request
            kyc_data = {
                "full_name": "احمد محمدی",
                "national_code": "0010316434", 
                "birth_date": "1368/01/21",
                "bank_card_number": "5022291514638870"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers, json=kyc_data)
            
            if response.status_code == 200:
                data = response.json()
                await self.log_test("KYC Level 1 Submission", True, 
                    f"KYC Level 1 submitted successfully: {data.get('message', 'Success')}")
                return True
            elif response.status_code == 400:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                await self.log_test("KYC Level 1 Submission", False, 
                    f"Validation error: {error_detail}")
                return False
            else:
                await self.log_test("KYC Level 1 Submission", False, 
                    f"Submission failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("KYC Level 1 Submission", False, f"Exception: {str(e)}")
            return False
    
    async def test_kyc_validation_rules(self):
        """Test KYC Level 1 validation rules"""
        if not self.user_token:
            await self.log_test("KYC Validation Tests", False, "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test 1: Invalid national code (not 10 digits)
        invalid_national_code = {
            "full_name": "احمد محمدی",
            "national_code": "123456789",  # 9 digits instead of 10
            "birth_date": "1368/01/21",
            "bank_card_number": "5022291514638870"
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers, json=invalid_national_code)
            
            if response.status_code == 422:  # Validation error
                await self.log_test("National Code Validation (9 digits)", True, 
                    "Correctly rejected national code with 9 digits")
            else:
                await self.log_test("National Code Validation (9 digits)", False, 
                    f"Should have rejected 9-digit national code: {response.status_code}")
        except Exception as e:
            await self.log_test("National Code Validation", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid bank card number (not 16 digits)
        invalid_card_number = {
            "full_name": "احمد محمدی",
            "national_code": "0010316434",
            "birth_date": "1368/01/21",
            "bank_card_number": "502229151463887"  # 15 digits instead of 16
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers, json=invalid_card_number)
            
            if response.status_code == 422:  # Validation error
                await self.log_test("Bank Card Validation (15 digits)", True, 
                    "Correctly rejected bank card with 15 digits")
            else:
                await self.log_test("Bank Card Validation (15 digits)", False, 
                    f"Should have rejected 15-digit card number: {response.status_code}")
        except Exception as e:
            await self.log_test("Bank Card Validation", False, f"Exception: {str(e)}")
        
        # Test 3: Empty full name
        empty_full_name = {
            "full_name": "",
            "national_code": "0010316434",
            "birth_date": "1368/01/21",
            "bank_card_number": "5022291514638870"
        }
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers, json=empty_full_name)
            
            if response.status_code == 422:  # Validation error
                await self.log_test("Full Name Validation (Empty)", True, 
                    "Correctly rejected empty full name")
            else:
                await self.log_test("Full Name Validation (Empty)", False, 
                    f"Should have rejected empty full name: {response.status_code}")
        except Exception as e:
            await self.log_test("Full Name Validation", False, f"Exception: {str(e)}")
    
    async def test_kyc_authentication_requirements(self):
        """Test KYC endpoints require proper JWT authentication"""
        try:
            # Test without authentication
            response = await self.client.get(f"{BACKEND_URL}/kyc/status")
            
            if response.status_code == 401:
                await self.log_test("KYC Status Authentication", True, 
                    "KYC status endpoint correctly requires authentication")
            else:
                await self.log_test("KYC Status Authentication", False, 
                    f"KYC status should require auth: {response.status_code}")
            
            # Test KYC Level 1 without authentication
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", json={
                "full_name": "احمد محمدی",
                "national_code": "0010316434",
                "birth_date": "1368/01/21",
                "bank_card_number": "5022291514638870"
            })
            
            if response.status_code == 401:
                await self.log_test("KYC Level 1 Authentication", True, 
                    "KYC Level 1 endpoint correctly requires authentication")
            else:
                await self.log_test("KYC Level 1 Authentication", False, 
                    f"KYC Level 1 should require auth: {response.status_code}")
                
        except Exception as e:
            await self.log_test("KYC Authentication Tests", False, f"Exception: {str(e)}")
    
    async def test_kyc_database_storage(self):
        """Test if KYC data is properly stored by checking status after submission"""
        try:
            if not self.user_token:
                await self.log_test("KYC Database Storage", False, "No user token available")
                return
            
            # First get initial status
            headers = {"Authorization": f"Bearer {self.user_token}"}
            initial_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if initial_response.status_code != 200:
                await self.log_test("KYC Database Storage", False, "Cannot get initial KYC status")
                return
            
            initial_data = initial_response.json()
            initial_level = initial_data.get("kyc_level", 0)
            
            # Submit KYC Level 1 if not already done
            if initial_level < 1:
                kyc_data = {
                    "full_name": "احمد محمدی تست",
                    "national_code": "0010316434",
                    "birth_date": "1368/01/21",
                    "bank_card_number": "5022291514638870"
                }
                
                submit_response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                    headers=headers, json=kyc_data)
                
                if submit_response.status_code != 200:
                    await self.log_test("KYC Database Storage", False, 
                        f"KYC submission failed: {submit_response.text}")
                    return
            
            # Check status after submission
            final_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if final_response.status_code == 200:
                final_data = final_response.json()
                
                # Verify data was stored
                if final_data.get("kyc_level", 0) >= 1:
                    if (final_data.get("full_name") and 
                        final_data.get("national_code") and 
                        final_data.get("bank_card_number")):
                        await self.log_test("KYC Database Storage", True, 
                            f"KYC data properly stored: Level {final_data.get('kyc_level')}, Name: {final_data.get('full_name')}")
                    else:
                        await self.log_test("KYC Database Storage", False, 
                            "KYC level updated but data fields missing")
                else:
                    await self.log_test("KYC Database Storage", False, 
                        "KYC level not updated after submission")
            else:
                await self.log_test("KYC Database Storage", False, 
                    f"Cannot verify storage: {final_response.text}")
                
        except Exception as e:
            await self.log_test("KYC Database Storage", False, f"Exception: {str(e)}")
    
    async def test_kyc_error_handling(self):
        """Test KYC error handling and Persian error messages"""
        if not self.user_token:
            await self.log_test("KYC Error Handling", False, "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test malformed JSON
        try:
            malformed_headers = {**headers, "Content-Type": "application/json"}
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=malformed_headers, 
                content="invalid json")
            
            if response.status_code == 422:
                await self.log_test("KYC Malformed JSON Handling", True, 
                    "Correctly handled malformed JSON")
            else:
                await self.log_test("KYC Malformed JSON Handling", False, 
                    f"Should handle malformed JSON: {response.status_code}")
        except Exception as e:
            await self.log_test("KYC Malformed JSON Handling", False, f"Exception: {str(e)}")
        
        # Test missing required fields
        try:
            incomplete_data = {
                "full_name": "احمد محمدی"
                # Missing other required fields
            }
            
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers, json=incomplete_data)
            
            if response.status_code == 422:
                error_data = response.json()
                await self.log_test("KYC Missing Fields Handling", True, 
                    f"Correctly handled missing fields: {error_data.get('detail', 'Validation error')}")
            else:
                await self.log_test("KYC Missing Fields Handling", False, 
                    f"Should handle missing fields: {response.status_code}")
        except Exception as e:
            await self.log_test("KYC Missing Fields Handling", False, f"Exception: {str(e)}")
    
    async def test_user_profile_after_kyc(self):
        """Test user profile updates after KYC submission"""
        try:
            if not self.user_token:
                await self.log_test("User Profile After KYC", False, "No user token available")
                return
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check if KYC fields are reflected in user profile
                kyc_level = user_data.get("kyc_level", 0)
                kyc_status = user_data.get("kyc_status", "pending")
                
                await self.log_test("User Profile After KYC", True, 
                    f"User profile shows KYC Level: {kyc_level}, Status: {kyc_status}")
                
                # Check if national_code is present (if KYC Level 1 completed)
                if kyc_level >= 1 and user_data.get("national_code"):
                    await self.log_test("User Profile KYC Data", True, 
                        "User profile contains KYC data (national_code present)")
                elif kyc_level >= 1:
                    await self.log_test("User Profile KYC Data", False, 
                        "User profile missing KYC data despite Level 1 completion")
                else:
                    await self.log_test("User Profile KYC Data", True, 
                        "User profile correctly shows no KYC data for Level 0")
            else:
                await self.log_test("User Profile After KYC", False, 
                    f"Cannot get user profile: {response.text}")
                
        except Exception as e:
            await self.log_test("User Profile After KYC", False, f"Exception: {str(e)}")
    
    async def run_kyc_debug_tests(self):
        """Run comprehensive KYC debug tests"""
        print("🔍 Starting KYC Functionality Debug Tests")
        print("=" * 70)
        
        # Step 1: Login with test user
        login_success = await self.test_user_login()
        
        if not login_success:
            print("❌ Cannot proceed without successful login")
            return
        
        # Step 2: Test KYC Status Endpoint
        print("\n📊 Testing KYC Status Endpoint...")
        initial_status = await self.test_kyc_status_endpoint()
        
        # Step 3: Test Authentication Requirements
        print("\n🔐 Testing KYC Authentication Requirements...")
        await self.test_kyc_authentication_requirements()
        
        # Step 4: Test KYC Level 1 Validation Rules
        print("\n✅ Testing KYC Level 1 Validation Rules...")
        await self.test_kyc_validation_rules()
        
        # Step 5: Test KYC Level 1 Submission
        print("\n📝 Testing KYC Level 1 Submission...")
        submission_success = await self.test_kyc_level1_submission()
        
        # Step 6: Test Database Storage
        print("\n💾 Testing KYC Database Storage...")
        await self.test_kyc_database_storage()
        
        # Step 7: Test Error Handling
        print("\n⚠️ Testing KYC Error Handling...")
        await self.test_kyc_error_handling()
        
        # Step 8: Test User Profile Updates
        print("\n👤 Testing User Profile After KYC...")
        await self.test_user_profile_after_kyc()
        
        # Final status check
        print("\n🔄 Final KYC Status Check...")
        final_status = await self.test_kyc_status_endpoint()
        
        print("\n" + "=" * 70)
        print("🏁 KYC Debug Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 KYC DEBUG TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Specific KYC diagnosis
        print(f"\n🔍 KYC FUNCTIONALITY DIAGNOSIS:")
        
        login_test = next((r for r in self.test_results if r["test"] == "User Login"), None)
        if login_test and login_test["success"]:
            print("✅ User authentication working")
        else:
            print("❌ User authentication failing - check credentials")
        
        status_test = next((r for r in self.test_results if r["test"] == "KYC Status Endpoint"), None)
        if status_test and status_test["success"]:
            print("✅ KYC status endpoint accessible")
        else:
            print("❌ KYC status endpoint not working")
        
        submission_test = next((r for r in self.test_results if r["test"] == "KYC Level 1 Submission"), None)
        if submission_test and submission_test["success"]:
            print("✅ KYC Level 1 submission working")
        else:
            print("❌ KYC Level 1 submission failing - this is the main issue")
        
        storage_test = next((r for r in self.test_results if r["test"] == "KYC Database Storage"), None)
        if storage_test and storage_test["success"]:
            print("✅ KYC data storage working")
        else:
            print("❌ KYC data not being stored properly")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = KYCDebugTester()
    try:
        await tester.run_kyc_debug_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())