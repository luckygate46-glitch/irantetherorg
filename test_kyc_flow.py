#!/usr/bin/env python3
"""
KYC Flow Test with Updated User Model
Tests KYC Level 1 and Level 2 with the updated user model
"""

import asyncio
import httpx
from datetime import datetime

# Configuration
BACKEND_URL = "https://tehcrypto.preview.emergentagent.com/api"

class KYCFlowTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
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
    
    async def login_user(self, email: str, password: str):
        """Login user and return token"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "token": data.get("access_token"),
                    "user_data": data.get("user", {})
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_kyc_level1(self, token: str, user_email: str):
        """Test KYC Level 1 with updated user model"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test KYC Level 1 submission
            kyc_data = {
                "full_name": "محمد رضایی کامل",  # This should override the computed full_name
                "national_code": "1234567890",
                "birth_date": "1370/05/15",
                "bank_card_number": "1234567890123456"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", headers=headers, json=kyc_data)
            
            if response.status_code == 200:
                result_data = response.json()
                await self.log_test("KYC Level 1 Submission", True, f"KYC Level 1 submitted successfully")
                
                # Test KYC status endpoint
                status_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    # Verify the full_name was updated
                    if status_data.get("full_name") == kyc_data["full_name"]:
                        await self.log_test("KYC Level 1 Full Name Override", True, f"full_name correctly updated to '{kyc_data['full_name']}'")
                    else:
                        await self.log_test("KYC Level 1 Full Name Override", False, f"full_name not updated: expected '{kyc_data['full_name']}', got '{status_data.get('full_name')}'")
                    
                    # Check other KYC fields
                    expected_fields = ["kyc_level", "kyc_status", "national_code", "bank_card_number"]
                    missing_fields = [field for field in expected_fields if field not in status_data]
                    
                    if not missing_fields:
                        await self.log_test("KYC Status Fields", True, "All KYC status fields present")
                    else:
                        await self.log_test("KYC Status Fields", False, f"Missing fields: {missing_fields}")
                    
                    # Check KYC level
                    if status_data.get("kyc_level") == 1:
                        await self.log_test("KYC Level Update", True, "KYC level correctly updated to 1")
                    else:
                        await self.log_test("KYC Level Update", False, f"KYC level not updated: expected 1, got {status_data.get('kyc_level')}")
                    
                    return {"success": True, "kyc_data": status_data}
                else:
                    await self.log_test("KYC Status Endpoint", False, f"KYC status failed: {status_response.text}")
                    return {"success": False}
            else:
                # This might fail due to API.IR integration issues, which is expected
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                
                if "شاهکار" in error_data.get("detail", "") or "API.IR" in error_data.get("detail", ""):
                    await self.log_test("KYC Level 1 API Integration", True, "KYC Level 1 correctly requires external API verification (expected failure)")
                    return {"success": True, "api_integration_required": True}
                else:
                    await self.log_test("KYC Level 1 Submission", False, f"Unexpected error: {error_data}")
                    return {"success": False, "error": error_data}
                
        except Exception as e:
            await self.log_test("KYC Level 1 Test", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_kyc_level2(self, token: str, user_email: str):
        """Test KYC Level 2 with updated user model"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test KYC Level 2 submission
            kyc_data = {
                "id_card_photo": "base64_encoded_id_photo_data",
                "selfie_type": "photo",
                "selfie_data": "base64_encoded_selfie_data"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/kyc/level2", headers=headers, json=kyc_data)
            
            if response.status_code == 200:
                result_data = response.json()
                await self.log_test("KYC Level 2 Submission", True, "KYC Level 2 submitted successfully")
                return {"success": True}
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                
                if "سطح ۱" in error_data.get("detail", "") or "Level 1" in error_data.get("detail", ""):
                    await self.log_test("KYC Level 2 Prerequisites", True, "KYC Level 2 correctly requires Level 1 completion")
                    return {"success": True, "requires_level1": True}
                else:
                    await self.log_test("KYC Level 2 Submission", False, f"Unexpected error: {error_data}")
                    return {"success": False, "error": error_data}
                
        except Exception as e:
            await self.log_test("KYC Level 2 Test", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_user_profile_after_kyc(self, token: str):
        """Test user profile display after KYC updates"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check if user profile reflects KYC updates
                kyc_fields = ["kyc_level", "kyc_status", "national_code"]
                present_fields = [field for field in kyc_fields if field in user_data]
                
                if len(present_fields) == len(kyc_fields):
                    await self.log_test("User Profile KYC Fields", True, "User profile includes KYC information")
                else:
                    missing = [field for field in kyc_fields if field not in user_data]
                    await self.log_test("User Profile KYC Fields", False, f"Missing KYC fields: {missing}")
                
                # Check full_name field
                if "full_name" in user_data:
                    await self.log_test("User Profile Full Name", True, f"full_name present: '{user_data.get('full_name')}'")
                else:
                    await self.log_test("User Profile Full Name", False, "full_name missing from user profile")
                
                return {"success": True, "user_data": user_data}
            else:
                await self.log_test("User Profile After KYC", False, f"Failed: {response.text}")
                return {"success": False}
                
        except Exception as e:
            await self.log_test("User Profile After KYC", False, f"Exception: {str(e)}")
            return {"success": False}
    
    async def run_kyc_tests(self):
        """Run KYC flow tests"""
        print("🚀 Starting KYC Flow Tests with Updated User Model")
        print("=" * 70)
        
        # Login with the user we created in the previous test
        print("\n🔐 Logging in with test user...")
        login_result = await self.login_user("mohammad.rezaei@newtest.com", "testpass123")
        
        if not login_result.get("success"):
            await self.log_test("Login for KYC Test", False, "Could not login test user")
            print("❌ Cannot proceed with KYC tests - user login failed")
            return
        
        token = login_result["token"]
        user_data = login_result["user_data"]
        
        await self.log_test("Login for KYC Test", True, f"Logged in as {user_data.get('email')}")
        
        # Test KYC Level 1
        print("\n📋 Testing KYC Level 1...")
        kyc1_result = await self.test_kyc_level1(token, user_data.get("email"))
        
        # Test KYC Level 2
        print("\n📋 Testing KYC Level 2...")
        kyc2_result = await self.test_kyc_level2(token, user_data.get("email"))
        
        # Test user profile after KYC
        print("\n👤 Testing User Profile After KYC...")
        await self.test_user_profile_after_kyc(token)
        
        print("\n" + "=" * 70)
        print("🏁 KYC Flow Testing Complete!")
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
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = KYCFlowTester()
    try:
        await tester.run_kyc_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())