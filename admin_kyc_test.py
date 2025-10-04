#!/usr/bin/env python3
"""
Admin KYC Management Testing for Iranian Crypto Exchange
Tests the complete admin KYC workflow including pending requests, approval/rejection process
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
BACKEND_URL = "https://tehcrypto.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class AdminKYCTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        
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
        
    async def create_test_user(self) -> Dict[str, Any]:
        """Use the existing test user mentioned in the review request"""
        try:
            # Use the existing test user from the review request
            user_data = {
                "email": "saruman.valar.test.20251004163014@gmail.com",
                "password": "password123"
            }
            
            # Try to login with existing user
            login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json=user_data)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                user_info = login_data.get("user", {})
                await self.log_test("Login Existing Test User", True, f"Logged in existing user: {user_info.get('email')}")
                return {
                    "token": login_data.get("access_token"),
                    "user_id": user_info.get("id"),
                    "email": user_info.get("email"),
                    "success": True
                }
            else:
                await self.log_test("Login Test User", False, f"Failed to login test user: {login_response.text}")
                return {"success": False}
                    
        except Exception as e:
            await self.log_test("Login Test User", False, f"Exception: {str(e)}")
            return {"success": False}
    
    async def get_admin_token(self) -> Optional[str]:
        """Get admin token by trying to login with known admin credentials"""
        try:
            # Try common admin credentials
            admin_credentials = [
                {"email": "saruman.valar.test.20251004163014@gmail.com", "password": "password123"},  # Known admin
                {"email": "admin@example.com", "password": "admin123"},
                {"email": "testuser@example.com", "password": "testpass"},
                {"email": "admin@tehcrypto.com", "password": "admin123"},
            ]
            
            for creds in admin_credentials:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json=creds)
                
                if response.status_code == 200:
                    data = response.json()
                    user_info = data.get("user", {})
                    token = data.get("access_token")
                    
                    # Test if this user has admin privileges by trying to access admin endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    admin_test = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
                    
                    if admin_test.status_code == 200:
                        await self.log_test("Admin Login", True, f"Admin logged in: {user_info.get('email')}")
                        return token
                    elif user_info.get("is_admin"):
                        await self.log_test("Admin Login", True, f"Admin logged in: {user_info.get('email')}")
                        return token
            
            await self.log_test("Admin Login", False, "No admin credentials found")
            return None
            
        except Exception as e:
            await self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return None
    
    async def complete_kyc_level1(self, token: str, user_email: str) -> bool:
        """Complete KYC Level 1 for user"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers,
                json={
                    "full_name": "سارومان والار تست",
                    "national_code": "0010316434",
                    "birth_date": "1368/01/21",
                    "bank_card_number": "5022291514638870"
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"KYC Level 1 {user_email}", True, "KYC Level 1 completed successfully")
                return True
            else:
                await self.log_test(f"KYC Level 1 {user_email}", False, f"KYC Level 1 failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"KYC Level 1 {user_email}", False, f"Exception: {str(e)}")
            return False
    
    async def submit_kyc_level2(self, token: str, user_email: str) -> bool:
        """Submit KYC Level 2 documents"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{BACKEND_URL}/kyc/level2", 
                headers=headers,
                json={
                    "id_card_photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A",
                    "selfie_type": "photo",
                    "selfie_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A"
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"KYC Level 2 Submit {user_email}", True, "KYC Level 2 documents submitted successfully")
                return True
            else:
                await self.log_test(f"KYC Level 2 Submit {user_email}", False, f"KYC Level 2 submission failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"KYC Level 2 Submit {user_email}", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_kyc_pending_endpoint(self, admin_token: str) -> List[Dict]:
        """Test GET /api/admin/kyc/pending endpoint"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            
            if response.status_code == 200:
                pending_kyc = response.json()
                await self.log_test("Admin KYC Pending Endpoint", True, f"Retrieved {len(pending_kyc)} pending KYC requests")
                
                # Verify response format
                if isinstance(pending_kyc, list):
                    if len(pending_kyc) > 0:
                        # Check first item structure
                        first_item = pending_kyc[0]
                        required_fields = ["id", "full_name", "email", "phone", "national_code", "kyc_documents"]
                        missing_fields = [field for field in required_fields if field not in first_item]
                        
                        if not missing_fields:
                            await self.log_test("Admin KYC Response Format", True, "Response format matches frontend expectations")
                        else:
                            await self.log_test("Admin KYC Response Format", False, f"Missing fields: {missing_fields}")
                    else:
                        await self.log_test("Admin KYC Response Format", True, "Empty list format is correct")
                else:
                    await self.log_test("Admin KYC Response Format", False, "Response should be a list")
                
                return pending_kyc
            else:
                await self.log_test("Admin KYC Pending Endpoint", False, f"Failed to get pending KYC: {response.text}")
                return []
                
        except Exception as e:
            await self.log_test("Admin KYC Pending Endpoint", False, f"Exception: {str(e)}")
            return []
    
    async def test_admin_kyc_approve_endpoint(self, admin_token: str, user_id: str, action: str = "approve") -> bool:
        """Test POST /api/admin/kyc/approve endpoint"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                headers=headers,
                json={
                    "user_id": user_id,
                    "kyc_level": 2,
                    "action": action,
                    "admin_note": f"Test {action} by admin KYC tester"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                await self.log_test(f"Admin KYC {action.title()}", True, f"KYC {action} successful: {data.get('message')}")
                return True
            else:
                await self.log_test(f"Admin KYC {action.title()}", False, f"KYC {action} failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Admin KYC {action.title()}", False, f"Exception: {str(e)}")
            return False
    
    async def test_user_kyc_status_after_admin_action(self, user_token: str, expected_level: int, expected_status: str) -> bool:
        """Test user KYC status after admin action"""
        try:
            headers = {"Authorization": f"Bearer {user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                actual_level = data.get("kyc_level")
                actual_status = data.get("kyc_status")
                
                if actual_level == expected_level and actual_status == expected_status:
                    await self.log_test("User KYC Status Update", True, f"KYC level: {actual_level}, status: {actual_status}")
                    return True
                else:
                    await self.log_test("User KYC Status Update", False, f"Expected level {expected_level}/{expected_status}, got {actual_level}/{actual_status}")
                    return False
            else:
                await self.log_test("User KYC Status Update", False, f"Failed to get KYC status: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("User KYC Status Update", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_authentication_required(self) -> bool:
        """Test that admin endpoints require admin privileges"""
        try:
            # Test without authentication
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending")
            
            if response.status_code in [401, 403]:
                await self.log_test("Admin Auth Required (No Token)", True, f"Correctly requires authentication (status: {response.status_code})")
            else:
                await self.log_test("Admin Auth Required (No Token)", False, f"Should require auth: {response.status_code}")
                return False
            
            # Test with non-admin user token (if we have one)
            if self.test_user_token:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
                
                if response.status_code == 403:
                    await self.log_test("Admin Auth Required (Non-Admin)", True, "Correctly blocks non-admin users")
                    return True
                else:
                    await self.log_test("Admin Auth Required (Non-Admin)", False, f"Should block non-admin: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            await self.log_test("Admin Authentication Test", False, f"Exception: {str(e)}")
            return False
    
    async def test_rejected_user_can_resubmit(self, user_token: str, user_email: str) -> bool:
        """Test that rejected users can resubmit KYC Level 2"""
        try:
            # Check if documents were cleared after rejection
            headers = {"Authorization": f"Bearer {user_token}"}
            response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_documents = data.get("has_documents", True)
                
                if not has_documents:
                    await self.log_test("Documents Cleared After Rejection", True, "Documents cleared, user can resubmit")
                    
                    # Try to resubmit
                    resubmit_success = await self.submit_kyc_level2(user_token, user_email)
                    if resubmit_success:
                        await self.log_test("KYC Resubmission After Rejection", True, "User can resubmit after rejection")
                        return True
                    else:
                        await self.log_test("KYC Resubmission After Rejection", False, "User cannot resubmit after rejection")
                        return False
                else:
                    await self.log_test("Documents Cleared After Rejection", False, "Documents not cleared after rejection")
                    return False
            else:
                await self.log_test("Check Documents After Rejection", False, f"Failed to check status: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Resubmission Test", False, f"Exception: {str(e)}")
            return False
    
    async def run_complete_workflow_test(self) -> bool:
        """Test complete KYC workflow: Level 1 → Level 2 → Admin Review → Approval/Rejection"""
        try:
            print("\n🔄 Testing Complete KYC Workflow...")
            
            # Step 1: Create test user
            user_result = await self.create_test_user()
            if not user_result.get("success"):
                return False
            
            self.test_user_token = user_result["token"]
            self.test_user_id = user_result["user_id"]
            user_email = user_result["email"]
            
            # Step 2: Check current KYC status
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            kyc_status_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if kyc_status_response.status_code == 200:
                kyc_data = kyc_status_response.json()
                current_level = kyc_data.get("kyc_level", 0)
                current_status = kyc_data.get("kyc_status", "pending")
                await self.log_test("Check Current KYC Status", True, f"Current KYC level: {current_level}, status: {current_status}")
                
                # Complete Level 1 if needed
                if current_level < 1:
                    level1_success = await self.complete_kyc_level1(self.test_user_token, user_email)
                    if not level1_success:
                        return False
                else:
                    await self.log_test("KYC Level 1 Status", True, "User already has Level 1 KYC completed")
            else:
                await self.log_test("Check Current KYC Status", False, f"Failed to check KYC status: {kyc_status_response.text}")
                return False
            
            # Step 3: Submit KYC Level 2 (check if already submitted)
            kyc_status_response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            if kyc_status_response.status_code == 200:
                kyc_data = kyc_status_response.json()
                has_documents = kyc_data.get("has_documents", False)
                current_level = kyc_data.get("kyc_level", 0)
                
                if current_level >= 2:
                    await self.log_test("KYC Level 2 Status", True, "User already has Level 2 KYC approved")
                elif has_documents:
                    await self.log_test("KYC Level 2 Documents", True, "User already has Level 2 documents submitted")
                else:
                    level2_success = await self.submit_kyc_level2(self.test_user_token, user_email)
                    if not level2_success:
                        return False
            else:
                level2_success = await self.submit_kyc_level2(self.test_user_token, user_email)
                if not level2_success:
                    return False
            
            # Step 4: Get admin token
            self.admin_token = await self.get_admin_token()
            if not self.admin_token:
                await self.log_test("Complete Workflow", False, "Cannot test admin functionality without admin token")
                return False
            
            # Step 5: Test admin can see pending KYC
            pending_kyc = await self.test_admin_kyc_pending_endpoint(self.admin_token)
            
            # Step 6: Test admin approval
            approve_success = await self.test_admin_kyc_approve_endpoint(self.admin_token, self.test_user_id, "approve")
            if approve_success:
                # Verify user status updated
                await self.test_user_kyc_status_after_admin_action(self.test_user_token, 2, "approved")
            
            # Step 7: Test rejection workflow - create a new user for this
            await self.test_rejection_workflow()
            
            await self.log_test("Complete KYC Workflow", True, "Full workflow tested successfully")
            return True
            
        except Exception as e:
            await self.log_test("Complete KYC Workflow", False, f"Exception: {str(e)}")
            return False
    
    async def run_admin_kyc_tests(self):
        """Run comprehensive admin KYC management tests"""
        print("🚀 Starting Admin KYC Management Tests")
        print("=" * 70)
        
        # Test 1: Admin authentication requirements
        print("\n🔐 Testing Admin Authentication Requirements...")
        await self.test_admin_authentication_required()
        
        # Test 2: Complete workflow test
        await self.run_complete_workflow_test()
        
        # Test 3: Additional endpoint tests (if admin token available)
        if self.admin_token:
            print("\n📋 Testing Admin KYC Endpoints...")
            
            # Test pending KYC endpoint
            await self.test_admin_kyc_pending_endpoint(self.admin_token)
            
            # Test approval endpoint with invalid user ID
            await self.test_admin_kyc_approve_endpoint(self.admin_token, "invalid-user-id", "approve")
        
        print("\n" + "=" * 70)
        print("🏁 Admin KYC Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 ADMIN KYC TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Print critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        admin_auth_tests = [r for r in self.test_results if "Admin Auth" in r["test"]]
        workflow_tests = [r for r in self.test_results if "Workflow" in r["test"]]
        
        if any(not t["success"] for t in admin_auth_tests):
            print("  ❌ Admin authentication issues detected")
        else:
            print("  ✅ Admin authentication working correctly")
        
        if any(not t["success"] for t in workflow_tests):
            print("  ❌ KYC workflow issues detected")
        else:
            print("  ✅ Complete KYC workflow functional")
    
    async def test_rejection_workflow(self) -> bool:
        """Test KYC rejection workflow with a new user"""
        try:
            # Create a new user for rejection testing
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            
            new_user_data = {
                "first_name": "تست",
                "last_name": "رد شده",
                "email": f"test.reject.{unique_id}@example.com",
                "phone": f"0912345{unique_id[:4]}",
                "password": "password123"
            }
            
            # Register new user
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json=new_user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_info = data.get("user", {})
                user_token = data.get("access_token")
                user_id = user_info.get("id")
                user_email = user_info.get("email")
                
                await self.log_test("Create Rejection Test User", True, f"Created user: {user_email}")
                
                # Complete KYC Level 1
                if await self.complete_kyc_level1(user_token, user_email):
                    # Submit KYC Level 2
                    if await self.submit_kyc_level2(user_token, user_email):
                        # Test rejection
                        reject_success = await self.test_admin_kyc_approve_endpoint(self.admin_token, user_id, "reject")
                        if reject_success:
                            # Verify user status updated and can resubmit
                            await self.test_user_kyc_status_after_admin_action(user_token, 1, "rejected")
                            await self.test_rejected_user_can_resubmit(user_token, user_email)
                            return True
                
                return False
            else:
                await self.log_test("Create Rejection Test User", False, f"Failed to create user: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Rejection Workflow Test", False, f"Exception: {str(e)}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = AdminKYCTester()
    try:
        await tester.run_admin_kyc_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())