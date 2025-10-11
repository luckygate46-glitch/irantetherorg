#!/usr/bin/env python3
"""
Final Admin User Verification Test
Verifies the admin user with exact credentials as requested
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://cryptotoman.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class FinalAdminVerification:
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
        
    async def test_admin_login_exact_credentials(self):
        """Test login with exact credentials: admin / istari118"""
        try:
            login_data = {
                "email": "admin",
                "password": "istari118"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                
                # Verify admin privileges
                is_admin = user_info.get("is_admin", False)
                kyc_level = user_info.get("kyc_level", 0)
                full_name = user_info.get("full_name", "")
                phone = user_info.get("phone", "")
                
                if is_admin and kyc_level == 2:
                    await self.log_test("Admin Login with Exact Credentials", True, 
                                      f"Login successful - Admin: {is_admin}, KYC Level: {kyc_level}, Name: {full_name}")
                    return data.get("access_token")
                else:
                    await self.log_test("Admin Login with Exact Credentials", False, 
                                      f"Login successful but missing privileges - Admin: {is_admin}, KYC Level: {kyc_level}")
                    return None
            else:
                await self.log_test("Admin Login with Exact Credentials", False, f"Login failed: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test("Admin Login with Exact Credentials", False, f"Exception: {str(e)}")
            return None
    
    async def test_jwt_admin_privileges(self, token: str):
        """Verify JWT token contains admin privileges"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                is_admin = user_data.get("is_admin", False)
                kyc_level = user_data.get("kyc_level", 0)
                
                if is_admin and kyc_level == 2:
                    await self.log_test("JWT Token Admin Privileges", True, 
                                      f"JWT contains admin privileges - Admin: {is_admin}, KYC Level: {kyc_level}")
                    return True
                else:
                    await self.log_test("JWT Token Admin Privileges", False, 
                                      f"JWT missing privileges - Admin: {is_admin}, KYC Level: {kyc_level}")
                    return False
            else:
                await self.log_test("JWT Token Admin Privileges", False, f"Token verification failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("JWT Token Admin Privileges", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_kyc_pending_access(self, token: str):
        """Test access to /api/admin/kyc/pending endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/kyc/pending", headers=headers)
            
            if response.status_code == 200:
                pending_kyc = response.json()
                await self.log_test("Admin KYC Pending Access", True, 
                                  f"Successfully accessed endpoint, found {len(pending_kyc)} pending requests")
                return True
            else:
                await self.log_test("Admin KYC Pending Access", False, f"Access failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin KYC Pending Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_panel_routes(self, token: str):
        """Test admin panel routes work correctly"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            routes = [
                ("/admin/stats", "Admin Stats"),
                ("/admin/users", "Admin Users"),
                ("/admin/orders", "Admin Orders"),
                ("/admin/kyc/pending", "Admin KYC Pending")
            ]
            
            successful_routes = 0
            for route, name in routes:
                response = await self.client.get(f"{BACKEND_URL}{route}", headers=headers)
                if response.status_code == 200:
                    successful_routes += 1
                    await self.log_test(f"Admin Route {name}", True, f"Successfully accessed {route}")
                else:
                    await self.log_test(f"Admin Route {name}", False, f"Failed to access {route}: {response.status_code}")
            
            if successful_routes == len(routes):
                await self.log_test("Admin Panel Routes Overall", True, f"All {len(routes)} admin routes working")
                return True
            else:
                await self.log_test("Admin Panel Routes Overall", False, f"Only {successful_routes}/{len(routes)} routes working")
                return False
                
        except Exception as e:
            await self.log_test("Admin Panel Routes", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_dashboard_access(self, token: str):
        """Verify admin dashboard access"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_users", "active_users", "total_deposits", "pending_deposits", "total_cards"]
                
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    await self.log_test("Admin Dashboard Access", True, 
                                      f"Dashboard accessible with complete stats: {stats}")
                    return True
                else:
                    await self.log_test("Admin Dashboard Access", False, f"Dashboard missing fields: {missing_fields}")
                    return False
            else:
                await self.log_test("Admin Dashboard Access", False, f"Dashboard access failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin Dashboard Access", False, f"Exception: {str(e)}")
            return False
    
    async def run_final_verification(self):
        """Run final comprehensive verification"""
        print("🎯 FINAL ADMIN USER VERIFICATION")
        print("=" * 50)
        print("Testing admin user with exact credentials:")
        print("- Email: admin")
        print("- Password: istari118")
        print("- Expected: is_admin = true, KYC Level 2")
        print("=" * 50)
        
        # Step 1: Test login with exact credentials
        print("\n🔐 Step 1: Testing Login with Exact Credentials...")
        token = await self.test_admin_login_exact_credentials()
        
        if not token:
            print("❌ Cannot proceed without successful admin login")
            await self.print_summary()
            return
        
        # Step 2: Verify JWT token contains admin privileges
        print("\n🎫 Step 2: Verifying JWT Token Admin Privileges...")
        await self.test_jwt_admin_privileges(token)
        
        # Step 3: Test admin KYC pending access
        print("\n📋 Step 3: Testing Admin KYC Pending Access...")
        await self.test_admin_kyc_pending_access(token)
        
        # Step 4: Test admin panel routes
        print("\n🌐 Step 4: Testing Admin Panel Routes...")
        await self.test_admin_panel_routes(token)
        
        # Step 5: Test admin dashboard access
        print("\n📊 Step 5: Testing Admin Dashboard Access...")
        await self.test_admin_dashboard_access(token)
        
        print("\n" + "=" * 50)
        print("🏁 FINAL VERIFICATION COMPLETE!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 FINAL TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL REQUIREMENTS MET!")
            print("✅ Admin user created with exact credentials")
            print("✅ Email: admin")
            print("✅ Password: istari118") 
            print("✅ Admin privileges: is_admin = true")
            print("✅ KYC Level: 2 (full access)")
            print("✅ Admin panel access working")
            print("✅ Admin dashboard functional")
        else:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    verifier = FinalAdminVerification()
    try:
        await verifier.run_final_verification()
    finally:
        await verifier.close()

if __name__ == "__main__":
    asyncio.run(main())