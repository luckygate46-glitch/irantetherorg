#!/usr/bin/env python3
"""
Admin User Creation and Verification Test
Creates admin user with specific credentials and verifies admin functionality
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

class AdminUserTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.admin_token = None
        self.admin_user_data = None
        
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
        
    async def create_admin_user(self) -> Dict[str, Any]:
        """Create admin user with specific credentials"""
        try:
            # Admin user data as specified
            admin_data = {
                "first_name": "ادمین",
                "last_name": "سیستم", 
                "email": "admin@system.local",
                "phone": "09000000000",
                "password": "istari118"
            }
            
            print(f"🔧 Creating admin user with email: {admin_data['email']}")
            
            # Try to register the admin user
            register_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=admin_data)
            
            if register_response.status_code in [200, 201]:
                user_data = register_response.json()
                user_info = user_data.get("user", {})
                
                await self.log_test("Admin User Registration", True, f"Admin user registered successfully with ID: {user_info.get('id')}")
                
                # Store admin data for later use
                self.admin_user_data = {
                    "email": admin_data["email"],
                    "password": admin_data["password"],
                    "user_id": user_info.get("id"),
                    "token": user_data.get("access_token"),
                    "user_info": user_info
                }
                
                return {"success": True, "data": self.admin_user_data}
                
            elif register_response.status_code == 400:
                # User might already exist, try to login
                error_data = register_response.json()
                if "قبلاً ثبت شده" in error_data.get("detail", ""):
                    await self.log_test("Admin User Already Exists", True, "Admin user already exists, will try to login")
                    return {"success": True, "already_exists": True}
                else:
                    await self.log_test("Admin User Registration", False, f"Registration failed: {error_data}")
                    return {"success": False, "error": error_data}
            else:
                error_detail = register_response.text
                await self.log_test("Admin User Registration", False, f"Registration failed: {error_detail}")
                return {"success": False, "error": error_detail}
                
        except Exception as e:
            await self.log_test("Admin User Creation", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def login_admin_user(self) -> Dict[str, Any]:
        """Login with admin credentials"""
        try:
            login_data = {
                "email": "admin",
                "password": "istari118"
            }
            
            print(f"🔐 Logging in admin user...")
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Store admin token and data
                self.admin_token = data.get("access_token")
                self.admin_user_data = {
                    "email": login_data["email"],
                    "password": login_data["password"],
                    "user_id": user_info.get("id"),
                    "token": self.admin_token,
                    "user_info": user_info
                }
                
                await self.log_test("Admin Login", True, f"Admin login successful, is_admin: {user_info.get('is_admin')}")
                return {"success": True, "data": self.admin_user_data}
            else:
                await self.log_test("Admin Login", False, f"Login failed: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            await self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def set_admin_privileges(self) -> bool:
        """Set admin privileges for the user (requires direct database access or existing admin)"""
        try:
            if not self.admin_user_data:
                await self.log_test("Set Admin Privileges", False, "No admin user data available")
                return False
            
            # Since we can't directly modify the database, we'll check if the user is already admin
            # If not, we'll need to manually set it via database or existing admin
            
            user_info = self.admin_user_data.get("user_info", {})
            if user_info.get("is_admin"):
                await self.log_test("Admin Privileges Check", True, "User already has admin privileges")
                return True
            else:
                await self.log_test("Admin Privileges Check", False, "User does not have admin privileges - needs manual database update")
                return False
                
        except Exception as e:
            await self.log_test("Set Admin Privileges", False, f"Exception: {str(e)}")
            return False
    
    async def verify_jwt_token_admin_privileges(self) -> bool:
        """Verify JWT token contains admin privileges"""
        try:
            if not self.admin_token:
                await self.log_test("JWT Admin Verification", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                is_admin = user_data.get("is_admin", False)
                
                if is_admin:
                    await self.log_test("JWT Admin Privileges", True, "JWT token correctly contains admin privileges")
                    return True
                else:
                    await self.log_test("JWT Admin Privileges", False, "JWT token does not contain admin privileges")
                    return False
            else:
                await self.log_test("JWT Admin Verification", False, f"Failed to verify token: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("JWT Admin Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_kyc_pending_access(self) -> bool:
        """Test access to /api/admin/kyc/pending endpoint"""
        try:
            if not self.admin_token:
                await self.log_test("Admin KYC Pending Access", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            
            if response.status_code == 200:
                pending_kyc = response.json()
                await self.log_test("Admin KYC Pending Access", True, f"Successfully accessed KYC pending endpoint, found {len(pending_kyc)} pending requests")
                return True
            elif response.status_code == 403:
                await self.log_test("Admin KYC Pending Access", False, "Access denied - user does not have admin privileges")
                return False
            else:
                await self.log_test("Admin KYC Pending Access", False, f"Failed to access endpoint: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin KYC Pending Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_panel_routes(self) -> bool:
        """Test various admin panel routes"""
        try:
            if not self.admin_token:
                await self.log_test("Admin Panel Routes", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            admin_routes = [
                ("/admin/stats", "Admin Stats"),
                ("/admin/users", "Admin Users List"),
                ("/admin/orders", "Admin Orders"),
                ("/admin/kyc/pending", "Admin KYC Pending")
            ]
            
            successful_routes = 0
            total_routes = len(admin_routes)
            
            for route, name in admin_routes:
                try:
                    response = await self.client.get(f"{BACKEND_URL}{route}", headers=headers)
                    
                    if response.status_code == 200:
                        await self.log_test(f"Admin Route {name}", True, f"Successfully accessed {route}")
                        successful_routes += 1
                    elif response.status_code == 403:
                        await self.log_test(f"Admin Route {name}", False, f"Access denied to {route} - insufficient privileges")
                    else:
                        await self.log_test(f"Admin Route {name}", False, f"Failed to access {route}: {response.status_code}")
                        
                except Exception as e:
                    await self.log_test(f"Admin Route {name}", False, f"Exception accessing {route}: {str(e)}")
            
            if successful_routes == total_routes:
                await self.log_test("Admin Panel Routes Overall", True, f"All {total_routes} admin routes accessible")
                return True
            else:
                await self.log_test("Admin Panel Routes Overall", False, f"Only {successful_routes}/{total_routes} admin routes accessible")
                return False
                
        except Exception as e:
            await self.log_test("Admin Panel Routes", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_dashboard_access(self) -> bool:
        """Test admin dashboard functionality"""
        try:
            if not self.admin_token:
                await self.log_test("Admin Dashboard Access", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin stats (dashboard data)
            response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats_data = response.json()
                required_stats = ["total_users", "active_users", "total_deposits", "pending_deposits", "total_cards"]
                
                missing_stats = []
                for stat in required_stats:
                    if stat not in stats_data:
                        missing_stats.append(stat)
                
                if not missing_stats:
                    await self.log_test("Admin Dashboard Stats", True, f"Dashboard stats complete: {stats_data}")
                    return True
                else:
                    await self.log_test("Admin Dashboard Stats", False, f"Missing stats: {missing_stats}")
                    return False
            elif response.status_code == 403:
                await self.log_test("Admin Dashboard Access", False, "Access denied - insufficient admin privileges")
                return False
            else:
                await self.log_test("Admin Dashboard Access", False, f"Failed to access dashboard: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin Dashboard Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_user_management(self) -> bool:
        """Test admin user management capabilities"""
        try:
            if not self.admin_token:
                await self.log_test("Admin User Management", False, "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test getting all users
            response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                await self.log_test("Admin Get All Users", True, f"Successfully retrieved {len(users)} users")
                
                # Test updating a user (if users exist)
                if users and len(users) > 0:
                    test_user = users[0]
                    user_id = test_user.get("id")
                    
                    if user_id:
                        update_response = await self.client.put(
                            f"{BACKEND_URL}/admin/users/{user_id}",
                            headers=headers,
                            json={"is_active": test_user.get("is_active", True)}  # No actual change
                        )
                        
                        if update_response.status_code == 200:
                            await self.log_test("Admin Update User", True, "Successfully updated user")
                            return True
                        else:
                            await self.log_test("Admin Update User", False, f"Failed to update user: {update_response.text}")
                            return False
                    else:
                        await self.log_test("Admin User Management", False, "No user ID found for testing update")
                        return False
                else:
                    await self.log_test("Admin User Management", True, "No users to test update with, but get users worked")
                    return True
            elif response.status_code == 403:
                await self.log_test("Admin User Management", False, "Access denied - insufficient admin privileges")
                return False
            else:
                await self.log_test("Admin User Management", False, f"Failed to get users: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin User Management", False, f"Exception: {str(e)}")
            return False
    
    async def set_kyc_level_2(self) -> bool:
        """Set KYC level to 2 for admin user"""
        try:
            if not self.admin_user_data:
                await self.log_test("Set KYC Level 2", False, "No admin user data available")
                return False
            
            user_id = self.admin_user_data.get("user_id")
            if not user_id:
                await self.log_test("Set KYC Level 2", False, "No user ID available")
                return False
            
            # First complete KYC Level 1
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            kyc1_data = {
                "full_name": "ادمین سیستم",
                "national_code": "0010316434",
                "birth_date": "1368/01/21",
                "bank_card_number": "5022291514638870"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", headers=headers, json=kyc1_data)
            
            if response.status_code == 200:
                await self.log_test("Admin KYC Level 1", True, "Admin KYC Level 1 completed")
                
                # Submit KYC Level 2 documents
                kyc2_data = {
                    "id_card_photo": "base64_encoded_admin_id_photo",
                    "selfie_type": "photo",
                    "selfie_data": "base64_encoded_admin_selfie"
                }
                
                response2 = await self.client.post(f"{BACKEND_URL}/kyc/level2", headers=headers, json=kyc2_data)
                
                if response2.status_code == 200:
                    await self.log_test("Admin KYC Level 2 Submit", True, "Admin KYC Level 2 documents submitted")
                    
                    # Since we're admin, approve our own KYC Level 2
                    approval_data = {
                        "user_id": user_id,
                        "kyc_level": 2,
                        "action": "approve",
                        "admin_note": "Admin user auto-approval"
                    }
                    
                    approval_response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", headers=headers, json=approval_data)
                    
                    if approval_response.status_code == 200:
                        await self.log_test("Admin KYC Level 2 Approval", True, "Admin KYC Level 2 approved")
                        return True
                    else:
                        await self.log_test("Admin KYC Level 2 Approval", False, f"Failed to approve KYC: {approval_response.text}")
                        return False
                else:
                    await self.log_test("Admin KYC Level 2 Submit", False, f"Failed to submit KYC Level 2: {response2.text}")
                    return False
            else:
                await self.log_test("Admin KYC Level 1", False, f"Failed to complete KYC Level 1: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Set KYC Level 2", False, f"Exception: {str(e)}")
            return False
    
    async def run_comprehensive_admin_test(self):
        """Run comprehensive admin user creation and verification test"""
        print("🚀 Starting Admin User Creation and Verification Test")
        print("=" * 70)
        
        # Step 1: Create admin user
        print("\n👤 Step 1: Creating Admin User...")
        create_result = await self.create_admin_user()
        
        # Step 2: Login admin user
        print("\n🔐 Step 2: Logging in Admin User...")
        login_result = await self.login_admin_user()
        
        if not login_result.get("success"):
            print("❌ Cannot proceed without successful admin login")
            await self.print_summary()
            return
        
        # Step 3: Check admin privileges
        print("\n🔒 Step 3: Verifying Admin Privileges...")
        await self.set_admin_privileges()
        
        # Step 4: Verify JWT token contains admin privileges
        print("\n🎫 Step 4: Verifying JWT Token Admin Privileges...")
        await self.verify_jwt_token_admin_privileges()
        
        # Step 5: Test admin KYC pending access
        print("\n📋 Step 5: Testing Admin KYC Pending Access...")
        await self.test_admin_kyc_pending_access()
        
        # Step 6: Test admin panel routes
        print("\n🌐 Step 6: Testing Admin Panel Routes...")
        await self.test_admin_panel_routes()
        
        # Step 7: Test admin dashboard access
        print("\n📊 Step 7: Testing Admin Dashboard Access...")
        await self.test_admin_dashboard_access()
        
        # Step 8: Test admin user management
        print("\n👥 Step 8: Testing Admin User Management...")
        await self.test_admin_user_management()
        
        # Step 9: Set KYC Level 2 for admin
        print("\n📝 Step 9: Setting Admin KYC Level 2...")
        await self.set_kyc_level_2()
        
        print("\n" + "=" * 70)
        print("🏁 Admin User Testing Complete!")
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
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Print admin user credentials for reference
        if self.admin_user_data:
            print(f"\n🔑 ADMIN USER CREDENTIALS:")
            print(f"Email: {self.admin_user_data.get('email')}")
            print(f"Password: {self.admin_user_data.get('password')}")
            print(f"User ID: {self.admin_user_data.get('user_id')}")
            print(f"Is Admin: {self.admin_user_data.get('user_info', {}).get('is_admin')}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = AdminUserTester()
    try:
        await tester.run_comprehensive_admin_test()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())