#!/usr/bin/env python3
"""
Complete KYC Approval Flow Test
Testing the complete KYC approval process to verify it works correctly
"""

import asyncio
import httpx
import json
import random
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://agitrader-platform.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class KYCFlowTester:
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
        
    async def login_admin(self) -> bool:
        """Login as admin"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "admin",
                "password": "istari118"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                await self.log_test("Admin Login", True, "Successfully logged in as admin")
                return True
            else:
                await self.log_test("Admin Login", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    async def create_test_user(self) -> Optional[Dict[str, Any]]:
        """Create a test user for KYC flow testing"""
        try:
            # Generate unique phone number
            phone_suffix = random.randint(1000, 9999)
            test_user_data = {
                "first_name": "محمد",
                "last_name": "نبودی",
                "email": f"test.kyc.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "phone": f"0912345{phone_suffix}",
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                user_token = data.get("access_token")
                user_info = data.get("user", {})
                
                await self.log_test("Test User Creation", True, 
                    f"Created test user: {test_user_data['email']}")
                
                return {
                    "email": test_user_data["email"],
                    "password": test_user_data["password"],
                    "phone": test_user_data["phone"],
                    "user_id": user_info.get("id"),
                    "token": user_token,
                    "first_name": test_user_data["first_name"],
                    "last_name": test_user_data["last_name"]
                }
            else:
                await self.log_test("Test User Creation", False, f"Failed: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test("Test User Creation", False, f"Exception: {str(e)}")
            return None
    
    async def complete_kyc_level1(self, user_token: str, user_email: str) -> bool:
        """Complete KYC Level 1"""
        try:
            headers = {"Authorization": f"Bearer {user_token}"}
            kyc1_data = {
                "full_name": "محمد نبودی",
                "national_code": "1234567890",
                "birth_date": "1370/05/15",
                "bank_card_number": "1234567890123456"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers, json=kyc1_data)
            
            if response.status_code == 200:
                await self.log_test("KYC Level 1 Completion", True, 
                    f"KYC Level 1 completed for {user_email}")
                return True
            else:
                await self.log_test("KYC Level 1 Completion", False, 
                    f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("KYC Level 1 Completion", False, f"Exception: {str(e)}")
            return False
    
    async def submit_kyc_level2(self, user_token: str, user_email: str) -> bool:
        """Submit KYC Level 2 documents"""
        try:
            headers = {"Authorization": f"Bearer {user_token}"}
            kyc2_data = {
                "id_card_photo": "base64_test_id_photo_data",
                "selfie_type": "photo",
                "selfie_data": "base64_test_selfie_data"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/kyc/level2", 
                headers=headers, json=kyc2_data)
            
            if response.status_code == 200:
                await self.log_test("KYC Level 2 Submission", True, 
                    f"KYC Level 2 documents submitted for {user_email}")
                return True
            else:
                await self.log_test("KYC Level 2 Submission", False, 
                    f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("KYC Level 2 Submission", False, f"Exception: {str(e)}")
            return False
    
    async def check_user_kyc_status(self, user_token: str, user_email: str, expected_level: int, expected_status: str) -> bool:
        """Check user KYC status via /auth/me and /kyc/status"""
        try:
            headers = {"Authorization": f"Bearer {user_token}"}
            
            # Check via /auth/me
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                actual_level = user_data.get("kyc_level")
                actual_status = user_data.get("kyc_status")
                
                if actual_level == expected_level and actual_status == expected_status:
                    await self.log_test("User Profile KYC Status", True, 
                        f"/auth/me shows correct KYC - Level: {actual_level}, Status: {actual_status}")
                else:
                    await self.log_test("User Profile KYC Status", False, 
                        f"/auth/me shows incorrect KYC - Expected: Level {expected_level}, Status {expected_status}; "
                        f"Got: Level {actual_level}, Status {actual_status}")
                    return False
            else:
                await self.log_test("User Profile KYC Status", False, f"Failed: {response.text}")
                return False
            
            # Check via /kyc/status
            kyc_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if kyc_response.status_code == 200:
                kyc_data = kyc_response.json()
                actual_level = kyc_data.get("kyc_level")
                actual_status = kyc_data.get("kyc_status")
                
                if actual_level == expected_level and actual_status == expected_status:
                    await self.log_test("KYC Status Endpoint", True, 
                        f"/kyc/status shows correct KYC - Level: {actual_level}, Status: {actual_status}")
                    return True
                else:
                    await self.log_test("KYC Status Endpoint", False, 
                        f"/kyc/status shows incorrect KYC - Expected: Level {expected_level}, Status {expected_status}; "
                        f"Got: Level {actual_level}, Status {actual_status}")
                    return False
            else:
                await self.log_test("KYC Status Endpoint", False, f"Failed: {kyc_response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Check User KYC Status", False, f"Exception: {str(e)}")
            return False
    
    async def admin_approve_kyc(self, user_id: str, user_email: str) -> bool:
        """Admin approves user KYC Level 2"""
        try:
            if not self.admin_token:
                await self.log_test("Admin KYC Approval", False, "No admin token")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            approval_data = {
                "user_id": user_id,
                "kyc_level": 2,
                "action": "approve",
                "admin_note": "Test approval for KYC debugging"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                headers=headers, json=approval_data)
            
            if response.status_code == 200:
                result = response.json()
                await self.log_test("Admin KYC Approval", True, 
                    f"Admin approved KYC Level 2 for {user_email}: {result.get('message')}")
                return True
            else:
                await self.log_test("Admin KYC Approval", False, 
                    f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin KYC Approval", False, f"Exception: {str(e)}")
            return False
    
    async def test_trading_access(self, user_token: str, user_email: str, should_work: bool = True) -> bool:
        """Test if user can access trading features"""
        try:
            headers = {"Authorization": f"Bearer {user_token}"}
            
            # Try to create a buy order
            order_data = {
                "order_type": "buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn": 100000.0
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                headers=headers, json=order_data)
            
            if should_work:
                if response.status_code in [200, 201]:
                    await self.log_test("Trading Access (Should Work)", True, 
                        f"User can create trading orders as expected")
                    return True
                elif response.status_code == 400:
                    # Check if it's a balance issue (which means KYC check passed)
                    error_msg = response.text
                    if "موجودی" in error_msg or "balance" in error_msg.lower():
                        await self.log_test("Trading Access (Should Work)", True, 
                            f"KYC check passed (failed due to insufficient balance)")
                        return True
                    else:
                        await self.log_test("Trading Access (Should Work)", False, 
                            f"Trading failed for unexpected reason: {error_msg}")
                        return False
                else:
                    await self.log_test("Trading Access (Should Work)", False, 
                        f"Trading access denied unexpectedly: {response.text}")
                    return False
            else:
                if response.status_code == 403:
                    await self.log_test("Trading Access (Should Fail)", True, 
                        f"Trading correctly blocked due to insufficient KYC")
                    return True
                else:
                    await self.log_test("Trading Access (Should Fail)", False, 
                        f"Trading should have been blocked but wasn't: {response.text}")
                    return False
                
        except Exception as e:
            await self.log_test("Test Trading Access", False, f"Exception: {str(e)}")
            return False
    
    async def run_complete_kyc_flow_test(self):
        """Run complete KYC approval flow test"""
        print("🧪 Starting Complete KYC Approval Flow Test")
        print("=" * 70)
        print("🎯 Goal: Verify KYC approval process works end-to-end")
        print("=" * 70)
        
        # Step 1: Login as admin
        print("\n👨‍💼 Step 1: Admin Login")
        admin_success = await self.login_admin()
        if not admin_success:
            print("❌ Cannot proceed without admin access")
            return
        
        # Step 2: Create test user
        print("\n👤 Step 2: Create Test User")
        test_user = await self.create_test_user()
        if not test_user:
            print("❌ Cannot proceed without test user")
            return
        
        # Step 3: Check initial KYC status (should be Level 0, pending)
        print("\n📋 Step 3: Check Initial KYC Status")
        await self.check_user_kyc_status(test_user["token"], test_user["email"], 0, "pending")
        
        # Step 4: Test trading access (should fail)
        print("\n🚫 Step 4: Test Trading Access (Should Fail)")
        await self.test_trading_access(test_user["token"], test_user["email"], should_work=False)
        
        # Step 5: Complete KYC Level 1
        print("\n📝 Step 5: Complete KYC Level 1")
        kyc1_success = await self.complete_kyc_level1(test_user["token"], test_user["email"])
        if kyc1_success:
            await self.check_user_kyc_status(test_user["token"], test_user["email"], 1, "approved")
        
        # Step 6: Submit KYC Level 2 documents
        print("\n📄 Step 6: Submit KYC Level 2 Documents")
        kyc2_success = await self.submit_kyc_level2(test_user["token"], test_user["email"])
        if kyc2_success:
            # After submission, should be Level 1, pending (waiting for admin approval)
            await self.check_user_kyc_status(test_user["token"], test_user["email"], 1, "pending")
        
        # Step 7: Admin approves KYC Level 2
        print("\n✅ Step 7: Admin Approves KYC Level 2")
        approval_success = await self.admin_approve_kyc(test_user["user_id"], test_user["email"])
        
        # Step 8: Check KYC status after admin approval (should be Level 2, approved)
        print("\n🔍 Step 8: Check KYC Status After Admin Approval")
        final_status_check = await self.check_user_kyc_status(test_user["token"], test_user["email"], 2, "approved")
        
        # Step 9: Test trading access (should work now)
        print("\n✅ Step 9: Test Trading Access (Should Work Now)")
        await self.test_trading_access(test_user["token"], test_user["email"], should_work=True)
        
        # Step 10: Re-login user to verify persistent status
        print("\n🔄 Step 10: Re-login User to Verify Persistent Status")
        login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        if login_response.status_code == 200:
            new_token = login_response.json().get("access_token")
            await self.log_test("User Re-login", True, "User successfully re-logged in")
            await self.check_user_kyc_status(new_token, test_user["email"], 2, "approved")
        else:
            await self.log_test("User Re-login", False, f"Failed: {login_response.text}")
        
        print("\n" + "=" * 70)
        print("🏁 Complete KYC Flow Test Finished!")
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
        
        print(f"\n🔍 KYC APPROVAL PROCESS ANALYSIS:")
        
        # Check key test results
        user_created = any(r["success"] and r["test"] == "Test User Creation" for r in self.test_results)
        kyc1_completed = any(r["success"] and r["test"] == "KYC Level 1 Completion" for r in self.test_results)
        kyc2_submitted = any(r["success"] and r["test"] == "KYC Level 2 Submission" for r in self.test_results)
        admin_approved = any(r["success"] and r["test"] == "Admin KYC Approval" for r in self.test_results)
        final_status_correct = any(r["success"] and r["test"] == "User Profile KYC Status" and 
                                 "Level: 2, Status: approved" in r["details"] for r in self.test_results)
        
        if user_created and kyc1_completed and kyc2_submitted and admin_approved and final_status_correct:
            print("✅ CONCLUSION: KYC approval process is working correctly")
            print("   - Users can complete KYC Level 1 and 2")
            print("   - Admin can approve KYC Level 2")
            print("   - User dashboard correctly shows approved KYC status")
            print("   - The issue with mamad.naboodi@gmail.com may be:")
            print("     1. User password is unknown (cannot verify dashboard)")
            print("     2. Frontend caching issue")
            print("     3. User needs to refresh/re-login")
        else:
            print("❌ CONCLUSION: KYC approval process has issues")
        
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
        await tester.run_complete_kyc_flow_test()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())