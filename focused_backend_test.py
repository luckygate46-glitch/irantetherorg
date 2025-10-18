#!/usr/bin/env python3
"""
Focused Backend Testing - Testing key issues found in comprehensive test
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://cryptotradera.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class FocusedBackendTester:
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
    
    async def test_jwt_security_fix(self):
        """Test if JWT security issue is fixed"""
        print("\n🔒 Testing JWT Security Fix...")
        
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if response.status_code == 401:
                    await self.log_test(f"JWT Invalid Token Rejection", True, 
                                      f"Correctly rejected invalid token")
                else:
                    await self.log_test(f"JWT Invalid Token Rejection", False, 
                                      f"Should reject invalid token: {response.status_code}")
            except Exception as e:
                await self.log_test(f"JWT Invalid Token Test", False, f"Exception: {str(e)}")
    
    async def test_api_ir_integration(self):
        """Test API.IR integration status"""
        print("\n📱 Testing API.IR Integration...")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/otp/send", json={
                "phone": "09123456789"
            })
            
            if response.status_code == 200:
                await self.log_test("API.IR OTP Service", True, "API.IR OTP service working")
            elif response.status_code == 500:
                # Check error details
                try:
                    error_data = response.json()
                    await self.log_test("API.IR OTP Service", False, 
                                      f"API.IR service error: {error_data.get('detail', 'Unknown error')}")
                except:
                    await self.log_test("API.IR OTP Service", False, 
                                      "API.IR service returning 500 - likely configuration issue")
            else:
                await self.log_test("API.IR OTP Service", False, 
                                  f"Unexpected response: {response.status_code}")
        except Exception as e:
            await self.log_test("API.IR OTP Service", False, f"Exception: {str(e)}")
    
    async def test_admin_endpoints_existence(self):
        """Test which admin endpoints exist"""
        print("\n👨‍💼 Testing Admin Endpoints Existence...")
        
        admin_endpoints = [
            "/admin/users",
            "/admin/deposits", 
            "/admin/orders",  # This one doesn't exist
            "/admin/stats",
            "/admin/trading/orders",
            "/admin/kyc/pending",
            "/admin/kyc/approve"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 403:
                    await self.log_test(f"Admin Endpoint {endpoint}", True, 
                                      "Endpoint exists and is properly protected")
                elif response.status_code == 404:
                    await self.log_test(f"Admin Endpoint {endpoint}", False, 
                                      "Endpoint does not exist (404)")
                else:
                    await self.log_test(f"Admin Endpoint {endpoint}", False, 
                                      f"Unexpected response: {response.status_code}")
            except Exception as e:
                await self.log_test(f"Admin Endpoint {endpoint}", False, f"Exception: {str(e)}")
    
    async def test_trading_system_comprehensive(self):
        """Test trading system comprehensively"""
        print("\n💰 Testing Trading System...")
        
        # Test trading endpoints without auth (should be protected)
        trading_endpoints = [
            ("/trading/order", "POST", {"order_type": "buy", "coin_symbol": "BTC", "coin_id": "bitcoin", "amount_tmn": 1000000}),
            ("/trading/orders/my", "GET", None),
            ("/trading/holdings/my", "GET", None)
        ]
        
        for endpoint, method, data in trading_endpoints:
            try:
                if method == "GET":
                    response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = await self.client.post(f"{BACKEND_URL}{endpoint}", json=data)
                
                if response.status_code == 403:
                    await self.log_test(f"Trading {endpoint} Security", True, 
                                      "Trading endpoint properly protected")
                else:
                    await self.log_test(f"Trading {endpoint} Security", False, 
                                      f"Trading endpoint should be protected: {response.status_code}")
            except Exception as e:
                await self.log_test(f"Trading {endpoint} Security", False, f"Exception: {str(e)}")
    
    async def test_crypto_apis_performance(self):
        """Test crypto APIs performance and reliability"""
        print("\n📈 Testing Crypto APIs Performance...")
        
        crypto_endpoints = [
            "/crypto/prices",
            "/crypto/bitcoin", 
            "/crypto/trending/coins"
        ]
        
        for endpoint in crypto_endpoints:
            try:
                start_time = time.time()
                response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        await self.log_test(f"Crypto API {endpoint}", True, 
                                          f"Working correctly ({response_time:.0f}ms)")
                    else:
                        await self.log_test(f"Crypto API {endpoint}", False, 
                                          f"API returned success=false: {data.get('error')}")
                else:
                    await self.log_test(f"Crypto API {endpoint}", False, 
                                      f"API failed: {response.status_code}")
            except Exception as e:
                await self.log_test(f"Crypto API {endpoint}", False, f"Exception: {str(e)}")
    
    async def test_data_validation_comprehensive(self):
        """Test comprehensive data validation"""
        print("\n🛡️ Testing Data Validation...")
        
        # Test registration validation
        validation_tests = [
            {
                "name": "Empty first_name",
                "data": {"first_name": "", "last_name": "احمدی", "email": "test1@test.com", "phone": "09123456789", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Invalid email format",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "invalid-email", "phone": "09123456789", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Phone not starting with 09",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "test@test.com", "phone": "08123456789", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Phone too short",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "test@test.com", "phone": "0912345678", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Password too short",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "test@test.com", "phone": "09123456789", "password": "123"},
                "should_fail": True
            }
        ]
        
        for test_case in validation_tests:
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_case["data"])
                
                if test_case["should_fail"]:
                    if response.status_code == 422:
                        await self.log_test(f"Validation: {test_case['name']}", True, 
                                          "Correctly rejected invalid data")
                    else:
                        await self.log_test(f"Validation: {test_case['name']}", False, 
                                          f"Should have rejected invalid data: {response.status_code}")
                else:
                    if response.status_code in [200, 400]:  # 400 for OTP requirement is OK
                        await self.log_test(f"Validation: {test_case['name']}", True, 
                                          "Correctly accepted valid data")
                    else:
                        await self.log_test(f"Validation: {test_case['name']}", False, 
                                          f"Should have accepted valid data: {response.status_code}")
            except Exception as e:
                await self.log_test(f"Validation: {test_case['name']}", False, f"Exception: {str(e)}")
    
    async def test_error_responses(self):
        """Test error response quality"""
        print("\n🚨 Testing Error Response Quality...")
        
        # Test 404 handling
        try:
            response = await self.client.get(f"{BACKEND_URL}/nonexistent/endpoint")
            if response.status_code == 404:
                await self.log_test("404 Error Handling", True, "Correctly returns 404 for non-existent endpoints")
            else:
                await self.log_test("404 Error Handling", False, f"Should return 404: {response.status_code}")
        except Exception as e:
            await self.log_test("404 Error Handling", False, f"Exception: {str(e)}")
        
        # Test Persian error messages
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "nonexistent@test.com",
                "password": "wrongpass"
            })
            if response.status_code == 401:
                error_data = response.json()
                error_message = error_data.get("detail", "")
                # Check if message contains Persian characters
                has_persian = any(ord(char) > 1500 for char in error_message)
                if has_persian:
                    await self.log_test("Persian Error Messages", True, "Error messages are in Persian")
                else:
                    await self.log_test("Persian Error Messages", False, f"Error message not in Persian: {error_message}")
            else:
                await self.log_test("Persian Error Messages", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            await self.log_test("Persian Error Messages", False, f"Exception: {str(e)}")
    
    async def run_focused_tests(self):
        """Run focused backend tests"""
        print("🎯 Starting Focused Backend Testing")
        print("=" * 60)
        
        await self.test_jwt_security_fix()
        await self.test_api_ir_integration()
        await self.test_admin_endpoints_existence()
        await self.test_trading_system_comprehensive()
        await self.test_crypto_apis_performance()
        await self.test_data_validation_comprehensive()
        await self.test_error_responses()
        
        print("\n" + "=" * 60)
        print("🏁 Focused Backend Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 FOCUSED TEST SUMMARY")
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
    tester = FocusedBackendTester()
    try:
        await tester.run_focused_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())