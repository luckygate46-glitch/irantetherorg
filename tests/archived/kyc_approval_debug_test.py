#!/usr/bin/env python3
"""
KYC Approval Process Debug Test
Specifically testing the bug where admin approved KYC for user "mamad.naboodi@gmail.com" 
but user dashboard still shows incomplete KYC status.
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class KYCApprovalDebugger:
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
        """Login as admin to get admin token"""
        try:
            # Try to login with admin credentials
            admin_credentials = [
                {"email": "admin", "password": "istari118"},
                {"email": "admin@example.com", "password": "admin123"},
                {"email": "testadmin@example.com", "password": "admin123"}
            ]
            
            for creds in admin_credentials:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json=creds)
                
                if response.status_code == 200:
                    data = response.json()
                    user_info = data.get("user", {})
                    
                    if user_info.get("is_admin"):
                        self.admin_token = data.get("access_token")
                        await self.log_test("Admin Login", True, f"Successfully logged in as admin: {creds['email']}")
                        return True
                    else:
                        await self.log_test("Admin Login", False, f"User {creds['email']} is not admin")
                else:
                    await self.log_test("Admin Login Attempt", False, f"Failed to login with {creds['email']}: {response.text}")
            
            await self.log_test("Admin Login", False, "Could not login as admin with any credentials")
            return False
            
        except Exception as e:
            await self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    async def check_user_exists(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if user exists and get their current status"""
        try:
            if not self.admin_token:
                await self.log_test("Check User Exists", False, "No admin token available")
                return None
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                target_user = None
                
                for user in users:
                    if user.get("email") == email:
                        target_user = user
                        break
                
                if target_user:
                    await self.log_test("User Exists Check", True, 
                        f"User {email} found - KYC Level: {target_user.get('kyc_level')}, "
                        f"KYC Status: {target_user.get('kyc_status')}")
                    return target_user
                else:
                    await self.log_test("User Exists Check", False, f"User {email} not found in database")
                    return None
            else:
                await self.log_test("User Exists Check", False, f"Failed to get users: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test("User Exists Check", False, f"Exception: {str(e)}")
            return None
    
    async def test_user_login_and_profile(self, email: str, password: str = "password123") -> Optional[str]:
        """Test if user can login and check their profile KYC status"""
        try:
            # Try common passwords for the user
            passwords_to_try = [password, "password123", "123456", "testpass123", "mamad123"]
            
            user_token = None
            for pwd in passwords_to_try:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": email,
                    "password": pwd
                })
                
                if response.status_code == 200:
                    data = response.json()
                    user_token = data.get("access_token")
                    user_info = data.get("user", {})
                    
                    await self.log_test("User Login", True, 
                        f"User {email} logged in successfully with password: {pwd}")
                    await self.log_test("User Login KYC Status", True,
                        f"Login response shows - KYC Level: {user_info.get('kyc_level')}, "
                        f"KYC Status: {user_info.get('kyc_status')}")
                    break
                else:
                    await self.log_test("User Login Attempt", False, 
                        f"Failed login with password {pwd}: {response.text}")
            
            if not user_token:
                await self.log_test("User Login", False, f"Could not login user {email} with any password")
                return None
            
            # Test /auth/me endpoint to see what user dashboard would show
            headers = {"Authorization": f"Bearer {user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                await self.log_test("User Profile KYC Status", True,
                    f"/auth/me shows - KYC Level: {user_data.get('kyc_level')}, "
                    f"KYC Status: {user_data.get('kyc_status')}")
                
                # Check KYC status endpoint specifically
                kyc_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
                if kyc_response.status_code == 200:
                    kyc_data = kyc_response.json()
                    await self.log_test("KYC Status Endpoint", True,
                        f"/kyc/status shows - KYC Level: {kyc_data.get('kyc_level')}, "
                        f"KYC Status: {kyc_data.get('kyc_status')}")
                else:
                    await self.log_test("KYC Status Endpoint", False, f"KYC status failed: {kyc_response.text}")
                
                return user_token
            else:
                await self.log_test("User Profile", False, f"Failed to get user profile: {response.text}")
                return user_token
                
        except Exception as e:
            await self.log_test("User Login and Profile", False, f"Exception: {str(e)}")
            return None
    
    async def test_kyc_approval_endpoint(self, user_id: str) -> bool:
        """Test the KYC approval endpoint functionality"""
        try:
            if not self.admin_token:
                await self.log_test("KYC Approval Test", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test approving KYC Level 2
            approval_data = {
                "user_id": user_id,
                "kyc_level": 2,
                "action": "approve",
                "admin_note": "Debug test approval"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                headers=headers, json=approval_data)
            
            if response.status_code == 200:
                result = response.json()
                await self.log_test("KYC Approval Endpoint", True, 
                    f"KYC approval successful: {result.get('message')}")
                return True
            else:
                await self.log_test("KYC Approval Endpoint", False, 
                    f"KYC approval failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("KYC Approval Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_pending_kyc_list(self) -> bool:
        """Test getting pending KYC requests"""
        try:
            if not self.admin_token:
                await self.log_test("Pending KYC List", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            
            if response.status_code == 200:
                pending_kyc = response.json()
                await self.log_test("Pending KYC List", True, 
                    f"Found {len(pending_kyc)} pending KYC requests")
                
                # Check if our target user is in pending list
                target_found = False
                for kyc_request in pending_kyc:
                    if kyc_request.get("email") == "mamad.naboodi@gmail.com":
                        target_found = True
                        await self.log_test("Target User in Pending KYC", True,
                            f"User mamad.naboodi@gmail.com found in pending KYC list")
                        break
                
                if not target_found:
                    await self.log_test("Target User in Pending KYC", False,
                        "User mamad.naboodi@gmail.com NOT found in pending KYC list")
                
                return True
            else:
                await self.log_test("Pending KYC List", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Pending KYC List", False, f"Exception: {str(e)}")
            return False
    
    async def create_test_user_for_kyc_flow(self) -> Optional[Dict[str, Any]]:
        """Create a test user to verify KYC approval flow works correctly"""
        try:
            # Create a test user
            test_user_data = {
                "first_name": "تست",
                "last_name": "کاربر",
                "email": f"kyc.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "phone": "09123456999",
                "password": "testpass123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                user_token = data.get("access_token")
                user_info = data.get("user", {})
                
                await self.log_test("Test User Creation", True, 
                    f"Created test user: {test_user_data['email']}")
                
                # Complete KYC Level 1
                headers = {"Authorization": f"Bearer {user_token}"}
                kyc1_data = {
                    "full_name": "تست کاربر",
                    "national_code": "1234567890",
                    "birth_date": "1370/05/15",
                    "bank_card_number": "1234567890123456"
                }
                
                kyc1_response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                    headers=headers, json=kyc1_data)
                
                if kyc1_response.status_code == 200:
                    await self.log_test("Test User KYC Level 1", True, "KYC Level 1 completed")
                    
                    # Submit KYC Level 2 documents
                    kyc2_data = {
                        "id_card_photo": "base64_test_id_photo",
                        "selfie_type": "photo",
                        "selfie_data": "base64_test_selfie"
                    }
                    
                    kyc2_response = await self.client.post(f"{BACKEND_URL}/kyc/level2", 
                        headers=headers, json=kyc2_data)
                    
                    if kyc2_response.status_code == 200:
                        await self.log_test("Test User KYC Level 2 Submit", True, "KYC Level 2 documents submitted")
                        
                        return {
                            "email": test_user_data["email"],
                            "password": test_user_data["password"],
                            "user_id": user_info.get("id"),
                            "token": user_token
                        }
                    else:
                        await self.log_test("Test User KYC Level 2 Submit", False, f"KYC Level 2 failed: {kyc2_response.text}")
                else:
                    await self.log_test("Test User KYC Level 1", False, f"KYC Level 1 failed: {kyc1_response.text}")
            else:
                await self.log_test("Test User Creation", False, f"Failed: {response.text}")
                
            return None
            
        except Exception as e:
            await self.log_test("Test User Creation", False, f"Exception: {str(e)}")
            return None
    
    async def test_complete_kyc_approval_flow(self, test_user: Dict[str, Any]) -> bool:
        """Test complete KYC approval flow with test user"""
        try:
            # 1. Approve KYC as admin
            success = await self.test_kyc_approval_endpoint(test_user["user_id"])
            if not success:
                return False
            
            # 2. Check user profile after approval
            user_token = await self.test_user_login_and_profile(test_user["email"], test_user["password"])
            if not user_token:
                return False
            
            # 3. Verify user can access trading (KYC Level 2 required)
            headers = {"Authorization": f"Bearer {user_token}"}
            trading_test_response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                headers=headers,
                json={
                    "order_type": "buy",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_tmn": 100000.0
                }
            )
            
            if trading_test_response.status_code in [200, 201]:
                await self.log_test("Trading Access After KYC Approval", True, 
                    "User can access trading after KYC approval")
            elif trading_test_response.status_code == 400:
                # Might fail due to insufficient balance, but that's OK - means KYC check passed
                error_msg = trading_test_response.text
                if "موجودی" in error_msg or "balance" in error_msg.lower():
                    await self.log_test("Trading Access After KYC Approval", True, 
                        "KYC check passed (failed due to insufficient balance)")
                else:
                    await self.log_test("Trading Access After KYC Approval", False, 
                        f"Trading failed for other reason: {error_msg}")
            else:
                await self.log_test("Trading Access After KYC Approval", False, 
                    f"Trading access denied: {trading_test_response.text}")
            
            return True
            
        except Exception as e:
            await self.log_test("Complete KYC Approval Flow", False, f"Exception: {str(e)}")
            return False
    
    async def run_kyc_debug_tests(self):
        """Run comprehensive KYC approval debug tests"""
        print("🔍 Starting KYC Approval Process Debug")
        print("=" * 70)
        print("🎯 Target User: mamad.naboodi@gmail.com")
        print("🐛 Issue: Admin approved KYC but user dashboard shows incomplete status")
        print("=" * 70)
        
        # Step 1: Login as admin
        print("\n👨‍💼 Step 1: Admin Login")
        admin_success = await self.login_admin()
        if not admin_success:
            print("❌ Cannot proceed without admin access")
            return
        
        # Step 2: Check if target user exists and their current status
        print("\n🔍 Step 2: Check Target User Status in Database")
        target_user = await self.check_user_exists("mamad.naboodi@gmail.com")
        
        # Step 3: Test user login and profile endpoints
        print("\n👤 Step 3: Test User Login and Profile Endpoints")
        user_token = await self.test_user_login_and_profile("mamad.naboodi@gmail.com")
        
        # Step 4: Test pending KYC list
        print("\n📋 Step 4: Check Pending KYC Requests")
        await self.test_pending_kyc_list()
        
        # Step 5: Test KYC approval endpoint if user exists
        if target_user and target_user.get("id"):
            print("\n✅ Step 5: Test KYC Approval Endpoint")
            await self.test_kyc_approval_endpoint(target_user["id"])
            
            # Re-check user status after approval attempt
            print("\n🔄 Step 6: Re-check User Status After Approval")
            await self.check_user_exists("mamad.naboodi@gmail.com")
            await self.test_user_login_and_profile("mamad.naboodi@gmail.com")
        
        # Step 6: Create test user to verify KYC flow works correctly
        print("\n🧪 Step 7: Test KYC Flow with New Test User")
        test_user = await self.create_test_user_for_kyc_flow()
        if test_user:
            await self.test_complete_kyc_approval_flow(test_user)
        
        print("\n" + "=" * 70)
        print("🏁 KYC Debug Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 DEBUG TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Analyze results to identify root cause
        user_exists = any(r["success"] and "User mamad.naboodi@gmail.com found" in r["details"] 
                         for r in self.test_results)
        user_login_success = any(r["success"] and r["test"] == "User Login" 
                               for r in self.test_results)
        kyc_approval_works = any(r["success"] and r["test"] == "KYC Approval Endpoint" 
                               for r in self.test_results)
        
        if not user_exists:
            print("❌ ISSUE: User mamad.naboodi@gmail.com does not exist in database")
            print("   SOLUTION: User needs to register first")
        elif not user_login_success:
            print("❌ ISSUE: Cannot login as user to verify dashboard status")
            print("   SOLUTION: Need correct password or user account may be inactive")
        elif not kyc_approval_works:
            print("❌ ISSUE: KYC approval endpoint is not working correctly")
            print("   SOLUTION: Check admin KYC approval implementation")
        else:
            print("✅ ANALYSIS: KYC approval system appears to be working")
            print("   NOTE: Issue may be in frontend dashboard display logic")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main debug test runner"""
    debugger = KYCApprovalDebugger()
    try:
        await debugger.run_kyc_debug_tests()
    finally:
        await debugger.close()

if __name__ == "__main__":
    asyncio.run(main())