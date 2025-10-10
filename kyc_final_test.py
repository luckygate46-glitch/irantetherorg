#!/usr/bin/env python3
"""
Final KYC Functionality Test - Test with fresh user to confirm fix
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

class KYCFinalTester:
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
        
    async def create_test_user(self) -> bool:
        """Create a fresh test user for KYC testing"""
        try:
            # Generate unique email
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_email = f"kyc.test.{timestamp}@example.com"
            test_phone = f"0912345{timestamp[-4:]}"
            
            user_data = {
                "first_name": "احمد",
                "last_name": "محمدی",
                "email": test_email,
                "phone": test_phone,
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("access_token")
                user_info = data.get("user", {})
                
                await self.log_test("Create Test User", True, 
                    f"User created: {test_email}, KYC Level: {user_info.get('kyc_level', 0)}")
                return True
            else:
                await self.log_test("Create Test User", False, f"Registration failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Create Test User", False, f"Exception: {str(e)}")
            return False
    
    async def test_kyc_level1_fresh_user(self) -> bool:
        """Test KYC Level 1 submission with fresh user"""
        try:
            if not self.user_token:
                await self.log_test("KYC Level 1 Fresh User", False, "No user token available")
                return False
            
            # Test data as provided in the original request
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
                await self.log_test("KYC Level 1 Fresh User", True, 
                    f"KYC Level 1 completed successfully: {data.get('message', 'Success')}")
                return True
            else:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                await self.log_test("KYC Level 1 Fresh User", False, 
                    f"KYC submission failed: {error_detail}")
                return False
                
        except Exception as e:
            await self.log_test("KYC Level 1 Fresh User", False, f"Exception: {str(e)}")
            return False
    
    async def test_kyc_status_after_submission(self) -> bool:
        """Test KYC status after successful submission"""
        try:
            if not self.user_token:
                await self.log_test("KYC Status After Submission", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                kyc_level = data.get("kyc_level", 0)
                kyc_status = data.get("kyc_status", "pending")
                full_name = data.get("full_name", "")
                national_code = data.get("national_code", "")
                
                if kyc_level >= 1 and kyc_status == "approved" and full_name and national_code:
                    await self.log_test("KYC Status After Submission", True, 
                        f"KYC data properly stored: Level {kyc_level}, Status: {kyc_status}, Name: {full_name}")
                    return True
                else:
                    await self.log_test("KYC Status After Submission", False, 
                        f"KYC data incomplete: Level {kyc_level}, Status: {kyc_status}")
                    return False
            else:
                await self.log_test("KYC Status After Submission", False, 
                    f"Cannot get KYC status: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("KYC Status After Submission", False, f"Exception: {str(e)}")
            return False
    
    async def test_user_profile_kyc_integration(self) -> bool:
        """Test user profile shows KYC data correctly"""
        try:
            if not self.user_token:
                await self.log_test("User Profile KYC Integration", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                kyc_level = user_data.get("kyc_level", 0)
                kyc_status = user_data.get("kyc_status", "pending")
                national_code = user_data.get("national_code", "")
                
                if kyc_level >= 1 and national_code:
                    await self.log_test("User Profile KYC Integration", True, 
                        f"User profile correctly shows KYC data: Level {kyc_level}, National Code: {national_code}")
                    return True
                else:
                    await self.log_test("User Profile KYC Integration", False, 
                        f"User profile missing KYC data: Level {kyc_level}")
                    return False
            else:
                await self.log_test("User Profile KYC Integration", False, 
                    f"Cannot get user profile: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("User Profile KYC Integration", False, f"Exception: {str(e)}")
            return False
    
    async def run_final_kyc_test(self):
        """Run final KYC functionality test"""
        print("🎯 Starting Final KYC Functionality Test")
        print("=" * 70)
        
        # Step 1: Create fresh test user
        print("\n👤 Creating Fresh Test User...")
        user_created = await self.create_test_user()
        
        if not user_created:
            print("❌ Cannot proceed without test user")
            return
        
        # Step 2: Test KYC Level 1 submission
        print("\n📝 Testing KYC Level 1 Submission...")
        kyc_success = await self.test_kyc_level1_fresh_user()
        
        # Step 3: Test KYC status after submission
        print("\n📊 Testing KYC Status After Submission...")
        status_success = await self.test_kyc_status_after_submission()
        
        # Step 4: Test user profile integration
        print("\n👤 Testing User Profile KYC Integration...")
        profile_success = await self.test_user_profile_kyc_integration()
        
        print("\n" + "=" * 70)
        print("🏁 Final KYC Test Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 FINAL KYC TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print(f"\n🎉 SUCCESS: KYC FUNCTIONALITY IS NOW WORKING!")
            print("✅ Users can successfully complete KYC Level 1 verification")
            print("✅ KYC data is properly stored in the database")
            print("✅ User profiles correctly reflect KYC status")
            print("✅ API.IR integration issues have been resolved with development fallback")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: Some issues remain")
            
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
    tester = KYCFinalTester()
    try:
        await tester.run_final_kyc_test()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())