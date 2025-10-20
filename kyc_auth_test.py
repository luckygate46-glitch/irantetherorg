#!/usr/bin/env python3
"""
KYC and Authentication Test for Trading Routes
Testing KYC-based route access and authentication guards
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://exchange-farsi.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class KYCAuthTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up KYC and Authentication Testing...")
        
        # Login as admin
        await self.login_admin()
        
    async def login_admin(self):
        """Login as admin user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_info = data["user"]
                print(f"✅ Admin login successful: {admin_info.get('full_name', 'Admin')}")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False

    async def test_kyc_status_endpoint(self):
        """Test KYC status endpoint"""
        print("\n🔍 Testing KYC Status Endpoint...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ KYC status endpoint accessible")
                print(f"📊 KYC Level: {data.get('kyc_level', 'N/A')}")
                print(f"📊 KYC Status: {data.get('kyc_status', 'N/A')}")
                print(f"📊 Full Name: {data.get('full_name', 'N/A')}")
                print(f"📊 Has Documents: {data.get('has_documents', 'N/A')}")
                
                self.test_results.append({
                    "test": "kyc_status_endpoint", 
                    "status": "✅ PASS", 
                    "details": f"KYC Level: {data.get('kyc_level')}, Status: {data.get('kyc_status')}"
                })
                
            else:
                print(f"❌ KYC status endpoint failed: {response.status_code} - {response.text}")
                self.test_results.append({
                    "test": "kyc_status_endpoint", 
                    "status": "❌ FAIL", 
                    "details": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ KYC status test error: {str(e)}")
            self.test_results.append({
                "test": "kyc_status_endpoint", 
                "status": "❌ ERROR", 
                "details": str(e)
            })

    async def test_unauthenticated_access(self):
        """Test that trading routes require authentication"""
        print("\n🚫 Testing Unauthenticated Access to Trading Routes...")
        
        trading_endpoints = [
            ("/trading/order", "POST"),
            ("/trading/orders/my", "GET"),
            ("/trading/holdings/my", "GET"),
            ("/kyc/status", "GET"),
            ("/auth/me", "GET")
        ]
        
        blocked_count = 0
        
        for endpoint, method in trading_endpoints:
            try:
                if method == "GET":
                    response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = await self.client.post(f"{BACKEND_URL}{endpoint}", json={})
                
                if response.status_code in [401, 403]:
                    print(f"✅ {endpoint} properly blocked without authentication")
                    blocked_count += 1
                else:
                    print(f"⚠️  {endpoint} accessible without authentication: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing {endpoint}: {str(e)}")
        
        if blocked_count == len(trading_endpoints):
            self.test_results.append({
                "test": "unauthenticated_access", 
                "status": "✅ PASS", 
                "details": "All trading routes properly require authentication"
            })
        else:
            self.test_results.append({
                "test": "unauthenticated_access", 
                "status": "⚠️  PARTIAL", 
                "details": f"{blocked_count}/{len(trading_endpoints)} routes require authentication"
            })

    async def test_admin_endpoints_access(self):
        """Test admin endpoints access"""
        print("\n👨‍💼 Testing Admin Endpoints Access...")
        
        admin_endpoints = [
            "/admin/stats",
            "/admin/users", 
            "/admin/orders",
            "/admin/kyc/pending"
        ]
        
        accessible_count = 0
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for endpoint in admin_endpoints:
            try:
                response = await self.client.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint} accessible to admin")
                    accessible_count += 1
                else:
                    print(f"❌ {endpoint} not accessible: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing {endpoint}: {str(e)}")
        
        if accessible_count == len(admin_endpoints):
            self.test_results.append({
                "test": "admin_endpoints_access", 
                "status": "✅ PASS", 
                "details": "All admin endpoints accessible"
            })
        else:
            self.test_results.append({
                "test": "admin_endpoints_access", 
                "status": "❌ PARTIAL", 
                "details": f"Only {accessible_count}/{len(admin_endpoints)} admin endpoints accessible"
            })

    async def run_all_tests(self):
        """Run all KYC and authentication tests"""
        print("🚀 Starting KYC and Authentication Testing...")
        print("=" * 60)
        
        await self.setup()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run all tests
        await self.test_kyc_status_endpoint()
        await self.test_unauthenticated_access()
        await self.test_admin_endpoints_access()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 KYC AND AUTHENTICATION TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        warning_tests = [r for r in self.test_results if "⚠️" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⚠️  WARNINGS: {len(warning_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if warning_tests:
            print("\n⚠️  WARNING TESTS:")
            for test in warning_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = KYCAuthTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())