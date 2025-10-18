#!/usr/bin/env python3
"""
Comprehensive Backend Test for Trading System
Tests existing functionality and identifies issues
"""

import asyncio
import httpx
import json
from datetime import datetime

BACKEND_URL = "https://cryptotradera.preview.emergentagent.com/api"

class TradingSystemTester:
    def __init__(self):
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    async def test_public_endpoints(self):
        """Test public endpoints that don't require authentication"""
        print("🌐 Testing Public Endpoints")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test crypto prices
            try:
                response = await client.get(f"{BACKEND_URL}/crypto/prices")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Crypto Prices API", True, f"Retrieved {len(data.get('data', {}))} coins")
                    else:
                        self.log_result("Crypto Prices API", False, f"API returned success=false: {data.get('error')}")
                else:
                    self.log_result("Crypto Prices API", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Crypto Prices API", False, f"Exception: {str(e)}")
            
            # Test get active cards
            try:
                response = await client.get(f"{BACKEND_URL}/cards")
                if response.status_code == 200:
                    cards = response.json()
                    self.log_result("Get Active Cards", True, f"Retrieved {len(cards)} active cards")
                else:
                    self.log_result("Get Active Cards", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get Active Cards", False, f"Exception: {str(e)}")
            
            # Test Bitcoin details
            try:
                response = await client.get(f"{BACKEND_URL}/crypto/bitcoin")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Bitcoin Details API", True, "Successfully retrieved Bitcoin details")
                    else:
                        self.log_result("Bitcoin Details API", False, f"API returned success=false: {data.get('error')}")
                else:
                    self.log_result("Bitcoin Details API", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Bitcoin Details API", False, f"Exception: {str(e)}")
    
    async def test_authentication_flow(self):
        """Test authentication and registration flow"""
        print("\n🔐 Testing Authentication Flow")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test OTP send (will likely fail due to API.IR issues)
            try:
                response = await client.post(f"{BACKEND_URL}/otp/send", json={
                    "phone": "09123456789"
                })
                if response.status_code == 200:
                    self.log_result("OTP Send", True, "OTP sent successfully")
                elif response.status_code == 500:
                    self.log_result("OTP Send", False, "OTP service error (expected - API.IR integration issue)")
                else:
                    self.log_result("OTP Send", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("OTP Send", False, f"Exception: {str(e)}")
            
            # Test login with existing user (if any)
            test_credentials = [
                {"email": "admin@example.com", "password": "admin123"},
                {"email": "testuser@example.com", "password": "testpass123"},
                {"email": "user@test.com", "password": "password123"}
            ]
            
            successful_login = None
            for creds in test_credentials:
                try:
                    response = await client.post(f"{BACKEND_URL}/auth/login", json=creds)
                    if response.status_code == 200:
                        data = response.json()
                        successful_login = {
                            "token": data.get("access_token"),
                            "user": data.get("user", {}),
                            "email": creds["email"]
                        }
                        self.log_result(f"Login {creds['email']}", True, f"Login successful - KYC Level: {data.get('user', {}).get('kyc_level', 0)}")
                        break
                    elif response.status_code == 401:
                        self.log_result(f"Login {creds['email']}", False, "Invalid credentials (expected)")
                    else:
                        self.log_result(f"Login {creds['email']}", False, f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_result(f"Login {creds['email']}", False, f"Exception: {str(e)}")
            
            return successful_login
    
    async def test_protected_endpoints(self, auth_data):
        """Test protected endpoints with authentication"""
        if not auth_data:
            print("\n🔒 Skipping Protected Endpoint Tests (No Authentication)")
            return
        
        print(f"\n🔒 Testing Protected Endpoints (User: {auth_data['email']})")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test get current user info
            try:
                response = await client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    kyc_level = user_data.get("kyc_level", 0)
                    wallet_balance = user_data.get("wallet_balance_tmn", 0)
                    self.log_result("Get Current User", True, f"KYC Level: {kyc_level}, Wallet: {wallet_balance} TMN")
                else:
                    self.log_result("Get Current User", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get Current User", False, f"Exception: {str(e)}")
            
            # Test get user's trading orders
            try:
                response = await client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
                if response.status_code == 200:
                    orders = response.json()
                    self.log_result("Get User Orders", True, f"Retrieved {len(orders)} orders")
                else:
                    self.log_result("Get User Orders", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get User Orders", False, f"Exception: {str(e)}")
            
            # Test get user's holdings
            try:
                response = await client.get(f"{BACKEND_URL}/trading/holdings/my", headers=headers)
                if response.status_code == 200:
                    holdings = response.json()
                    self.log_result("Get User Holdings", True, f"Retrieved {len(holdings)} holdings")
                else:
                    self.log_result("Get User Holdings", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get User Holdings", False, f"Exception: {str(e)}")
            
            # Test KYC status
            try:
                response = await client.get(f"{BACKEND_URL}/kyc/status", headers=headers)
                if response.status_code == 200:
                    kyc_data = response.json()
                    self.log_result("Get KYC Status", True, f"Level: {kyc_data.get('kyc_level')}, Status: {kyc_data.get('kyc_status')}")
                else:
                    self.log_result("Get KYC Status", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Get KYC Status", False, f"Exception: {str(e)}")
    
    async def test_trading_restrictions(self, auth_data):
        """Test trading order creation and restrictions"""
        if not auth_data:
            print("\n💱 Skipping Trading Tests (No Authentication)")
            return
        
        print(f"\n💱 Testing Trading Order Creation")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test creating a buy order
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=headers,
                    json={
                        "order_type": "buy",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_tmn": 100000.0
                    }
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    order_data = response.json()
                    self.log_result("Create Buy Order", True, f"Order created: {order_data.get('id')}")
                elif response.status_code == 403:
                    error_msg = response.json().get("detail", "")
                    if "احراز هویت" in error_msg or "KYC" in error_msg:
                        self.log_result("Create Buy Order", True, "Correctly blocked - KYC Level 2 required")
                    else:
                        self.log_result("Create Buy Order", False, f"Blocked for different reason: {error_msg}")
                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "")
                    if "موجودی" in error_msg or "balance" in error_msg:
                        self.log_result("Create Buy Order", True, "Correctly blocked - Insufficient balance")
                    else:
                        self.log_result("Create Buy Order", False, f"Validation error: {error_msg}")
                else:
                    self.log_result("Create Buy Order", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Create Buy Order", False, f"Exception: {str(e)}")
            
            # Test creating a sell order (should fail due to no holdings)
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=headers,
                    json={
                        "order_type": "sell",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_crypto": 0.01
                    }
                )
                
                if response.status_code == 400:
                    error_msg = response.json().get("detail", "")
                    if "موجودی" in error_msg:
                        self.log_result("Create Sell Order", True, "Correctly blocked - No crypto holdings")
                    else:
                        self.log_result("Create Sell Order", False, f"Blocked for different reason: {error_msg}")
                elif response.status_code == 403:
                    self.log_result("Create Sell Order", True, "Correctly blocked - KYC Level 2 required")
                else:
                    self.log_result("Create Sell Order", False, f"Unexpected response: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Create Sell Order", False, f"Exception: {str(e)}")
    
    async def test_admin_endpoints(self, auth_data):
        """Test admin endpoints if user is admin"""
        if not auth_data:
            print("\n👨‍💼 Skipping Admin Tests (No Authentication)")
            return
        
        print(f"\n👨‍💼 Testing Admin Endpoints")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test admin stats
            try:
                response = await client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
                if response.status_code == 200:
                    stats = response.json()
                    self.log_result("Admin Stats", True, f"Users: {stats.get('total_users')}, Deposits: {stats.get('total_deposits')}")
                elif response.status_code == 403:
                    self.log_result("Admin Stats", True, "Correctly blocked - User is not admin")
                else:
                    self.log_result("Admin Stats", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Admin Stats", False, f"Exception: {str(e)}")
            
            # Test admin get all orders
            try:
                response = await client.get(f"{BACKEND_URL}/admin/trading/orders", headers=headers)
                if response.status_code == 200:
                    orders = response.json()
                    self.log_result("Admin Get Orders", True, f"Retrieved {len(orders)} orders")
                elif response.status_code == 403:
                    self.log_result("Admin Get Orders", True, "Correctly blocked - User is not admin")
                else:
                    self.log_result("Admin Get Orders", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Admin Get Orders", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Trading System Tests")
        print("=" * 60)
        
        # Test public endpoints
        await self.test_public_endpoints()
        
        # Test authentication
        auth_data = await self.test_authentication_flow()
        
        # Test protected endpoints
        await self.test_protected_endpoints(auth_data)
        
        # Test trading functionality
        await self.test_trading_restrictions(auth_data)
        
        # Test admin functionality
        await self.test_admin_endpoints(auth_data)
        
        # Print summary
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group failures by category
        critical_failures = []
        expected_failures = []
        
        for result in self.results:
            if not result["success"]:
                if any(keyword in result["details"].lower() for keyword in ["expected", "correctly blocked", "api.ir", "otp service"]):
                    expected_failures.append(result)
                else:
                    critical_failures.append(result)
        
        if critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(critical_failures)}):")
            for result in critical_failures:
                print(f"  - {result['test']}: {result['details']}")
        
        if expected_failures:
            print(f"\n⚠️  EXPECTED FAILURES ({len(expected_failures)}):")
            for result in expected_failures:
                print(f"  - {result['test']}: {result['details']}")
        
        print("\n🏁 Testing Complete!")

async def main():
    """Main test runner"""
    tester = TradingSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())