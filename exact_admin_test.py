#!/usr/bin/env python3
"""
Exact Admin User Verification Test
Tests the exact specifications requested:
- Email/Username: "admin" 
- Password: "istari118"
- Admin privileges: is_admin = true
- KYC level 2
- Admin panel access
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://tehcrypto.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class ExactAdminTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
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
        
    async def test_exact_admin_login(self):
        """Test login with EXACT credentials: admin / istari118"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "admin",
                "password": "istari118"
            })
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify exact email
                if user_info.get("email") == "admin":
                    await self.log_test("Email Exactly 'admin'", True, f"✓ Email is exactly 'admin' (not admin@something.com)")
                else:
                    await self.log_test("Email Exactly 'admin'", False, f"Email is '{user_info.get('email')}', expected 'admin'")
                
                # Verify admin privileges
                if user_info.get("is_admin") == True:
                    await self.log_test("Admin Privileges", True, "✓ is_admin = true")
                else:
                    await self.log_test("Admin Privileges", False, f"is_admin = {user_info.get('is_admin')}, expected true")
                
                # Verify KYC level
                kyc_level = user_info.get("kyc_level", 0)
                if kyc_level >= 2:
                    await self.log_test("KYC Level 2+", True, f"✓ KYC level = {kyc_level} (Level 2+)")
                else:
                    await self.log_test("KYC Level 2+", False, f"KYC level = {kyc_level}, expected 2+")
                
                # Verify user is active
                if user_info.get("is_active") == True:
                    await self.log_test("User Active", True, "✓ User is active")
                else:
                    await self.log_test("User Active", False, f"is_active = {user_info.get('is_active')}, expected true")
                
                await self.log_test("Login with admin/istari118", True, "✓ Successfully logged in with exact credentials")
                
                return {
                    "success": True,
                    "token": data.get("access_token"),
                    "user_data": user_info
                }
            else:
                await self.log_test("Login with admin/istari118", False, f"Login failed: {response.text}")
                return {"success": False}
                
        except Exception as e:
            await self.log_test("Login with admin/istari118", False, f"Exception: {str(e)}")
            return {"success": False}
    
    async def test_admin_panel_access(self, token: str):
        """Test admin panel access at /admin"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test all admin endpoints
            admin_endpoints = [
                ("/admin/stats", "Admin Statistics"),
                ("/admin/users", "Admin Users Management"),
                ("/admin/orders", "Admin Orders Management"),
                ("/admin/kyc/pending", "Admin KYC Management")
            ]
            
            all_accessible = True
            
            for endpoint, name in admin_endpoints:
                response = await self.client.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    await self.log_test(f"Access {name}", True, f"✓ {endpoint} accessible")
                else:
                    await self.log_test(f"Access {name}", False, f"{endpoint} failed: {response.status_code}")
                    all_accessible = False
            
            if all_accessible:
                await self.log_test("Admin Panel Full Access", True, "✓ All admin panel endpoints accessible")
            else:
                await self.log_test("Admin Panel Full Access", False, "Some admin panel endpoints not accessible")
                
            return all_accessible
            
        except Exception as e:
            await self.log_test("Admin Panel Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_functionality(self, token: str):
        """Test core admin functionality"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test admin can view system stats
            response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                await self.log_test("Admin View System Stats", True, f"✓ Stats: {stats['total_users']} users, {stats['active_users']} active")
            else:
                await self.log_test("Admin View System Stats", False, f"Failed: {response.text}")
                return False
            
            # Test admin can manage users
            response = await self.client.get(f"{BACKEND_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                await self.log_test("Admin Manage Users", True, f"✓ Can view {len(users)} users")
            else:
                await self.log_test("Admin Manage Users", False, f"Failed: {response.text}")
                return False
            
            # Test admin can view orders
            response = await self.client.get(f"{BACKEND_URL}/admin/orders", headers=headers)
            if response.status_code == 200:
                orders = response.json()
                await self.log_test("Admin View Orders", True, f"✓ Can view {len(orders)} orders")
            else:
                await self.log_test("Admin View Orders", False, f"Failed: {response.text}")
                return False
            
            # Test admin can manage KYC
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            if response.status_code == 200:
                kyc_pending = response.json()
                await self.log_test("Admin Manage KYC", True, f"✓ Can view {len(kyc_pending)} pending KYC requests")
            else:
                await self.log_test("Admin Manage KYC", False, f"Failed: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            await self.log_test("Admin Functionality", False, f"Exception: {str(e)}")
            return False
    
    async def run_exact_verification(self):
        """Run exact admin user verification"""
        print("🎯 EXACT ADMIN USER VERIFICATION TEST")
        print("=" * 60)
        print("Testing EXACT specifications:")
        print("• Email/Username: admin")
        print("• Password: istari118") 
        print("• Admin privileges: is_admin = true")
        print("• KYC level: 2+")
        print("• Admin panel access: /admin")
        print("=" * 60)
        
        # Test 1: Login with exact credentials
        print("\n🔐 Testing Login with Exact Credentials...")
        login_result = await self.test_exact_admin_login()
        
        if not login_result.get("success"):
            print("❌ CRITICAL FAILURE: Cannot login with admin/istari118")
            await self.print_final_verdict()
            return
        
        token = login_result.get("token")
        user_data = login_result.get("user_data", {})
        
        # Test 2: Admin panel access
        print("\n🏛️ Testing Admin Panel Access...")
        panel_access = await self.test_admin_panel_access(token)
        
        # Test 3: Admin functionality
        print("\n⚙️ Testing Admin Functionality...")
        functionality = await self.test_admin_functionality(token)
        
        print("\n" + "=" * 60)
        await self.print_final_verdict()
    
    async def print_final_verdict(self):
        """Print final verdict"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST RESULTS SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED REQUIREMENTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n🎯 FINAL VERDICT:")
        if failed_tests == 0:
            print("✅ SUCCESS: Admin user with EXACT credentials is fully functional!")
            print("✅ User can login with: admin / istari118")
            print("✅ User has admin privileges (is_admin = true)")
            print("✅ User has KYC level 2+ access")
            print("✅ User can access admin panel at /admin")
            print("✅ All requirements met perfectly!")
        else:
            print("❌ FAILURE: Admin user requirements not fully met")
            print("❌ Check failed tests above for details")
        
        print("=" * 60)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = ExactAdminTester()
    try:
        await tester.run_exact_verification()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())