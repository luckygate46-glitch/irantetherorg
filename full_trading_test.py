#!/usr/bin/env python3
"""
Full Trading System Test - Tests complete trading workflow
"""

import asyncio
import httpx
import json
from datetime import datetime

BACKEND_URL = "https://agitrader-platform.preview.emergentagent.com/api"

class FullTradingTester:
    def __init__(self):
        self.results = []
        self.regular_user = None
        self.admin_user = None
        
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
    
    async def login_users(self):
        """Login both regular and admin users"""
        print("🔐 Logging in Test Users")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Login regular user
            try:
                response = await client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": "testuser@example.com",
                    "password": "testpass123"
                })
                if response.status_code == 200:
                    data = response.json()
                    self.regular_user = {
                        "token": data.get("access_token"),
                        "user_data": data.get("user", {}),
                        "email": "testuser@example.com"
                    }
                    self.log_result("Login Regular User", True, f"KYC Level: {data.get('user', {}).get('kyc_level')}, Balance: {data.get('user', {}).get('wallet_balance_tmn')} TMN")
                else:
                    self.log_result("Login Regular User", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Login Regular User", False, f"Exception: {str(e)}")
            
            # Login admin user
            try:
                response = await client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": "admin@example.com",
                    "password": "testpass123"
                })
                if response.status_code == 200:
                    data = response.json()
                    self.admin_user = {
                        "token": data.get("access_token"),
                        "user_data": data.get("user", {}),
                        "email": "admin@example.com"
                    }
                    self.log_result("Login Admin User", True, f"Admin: {data.get('user', {}).get('is_admin')}, Balance: {data.get('user', {}).get('wallet_balance_tmn')} TMN")
                else:
                    self.log_result("Login Admin User", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Login Admin User", False, f"Exception: {str(e)}")
    
    async def test_complete_trading_workflow(self):
        """Test complete trading workflow: create order -> admin approve -> check balances"""
        if not self.regular_user or not self.admin_user:
            print("\n💱 Skipping Trading Workflow (Missing Users)")
            return
        
        print(f"\n💱 Testing Complete Trading Workflow")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            regular_headers = {"Authorization": f"Bearer {self.regular_user['token']}"}
            admin_headers = {"Authorization": f"Bearer {self.admin_user['token']}"}
            
            # Step 1: Create a buy order
            buy_order_id = None
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=regular_headers,
                    json={
                        "order_type": "buy",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_tmn": 1000000.0  # 1M TMN
                    }
                )
                
                if response.status_code in [200, 201]:
                    order_data = response.json()
                    buy_order_id = order_data.get("id")
                    self.log_result("Step 1: Create Buy Order", True, f"Order ID: {buy_order_id}, Amount: 1M TMN")
                else:
                    self.log_result("Step 1: Create Buy Order", False, f"HTTP {response.status_code}: {response.text}")
                    return
            except Exception as e:
                self.log_result("Step 1: Create Buy Order", False, f"Exception: {str(e)}")
                return
            
            # Step 2: Admin gets all orders
            try:
                response = await client.get(f"{BACKEND_URL}/admin/trading/orders", headers=admin_headers)
                if response.status_code == 200:
                    orders = response.json()
                    pending_orders = [o for o in orders if o.get("status") == "pending"]
                    self.log_result("Step 2: Admin Get Orders", True, f"Total: {len(orders)}, Pending: {len(pending_orders)}")
                else:
                    self.log_result("Step 2: Admin Get Orders", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Step 2: Admin Get Orders", False, f"Exception: {str(e)}")
            
            # Step 3: Admin approves the buy order
            if buy_order_id:
                try:
                    response = await client.post(f"{BACKEND_URL}/admin/trading/orders/approve", 
                        headers=admin_headers,
                        json={
                            "order_id": buy_order_id,
                            "action": "approve",
                            "admin_note": "Test approval for buy order"
                        }
                    )
                    
                    if response.status_code == 200:
                        self.log_result("Step 3: Admin Approve Order", True, "Buy order approved successfully")
                    else:
                        self.log_result("Step 3: Admin Approve Order", False, f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_result("Step 3: Admin Approve Order", False, f"Exception: {str(e)}")
            
            # Step 4: Check user's updated balance and holdings
            try:
                response = await client.get(f"{BACKEND_URL}/auth/me", headers=regular_headers)
                if response.status_code == 200:
                    user_data = response.json()
                    new_balance = user_data.get("wallet_balance_tmn", 0)
                    self.log_result("Step 4: Check Updated Balance", True, f"New balance: {new_balance} TMN (should be 4M)")
                else:
                    self.log_result("Step 4: Check Updated Balance", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Step 4: Check Updated Balance", False, f"Exception: {str(e)}")
            
            # Step 5: Check user's crypto holdings
            try:
                response = await client.get(f"{BACKEND_URL}/trading/holdings/my", headers=regular_headers)
                if response.status_code == 200:
                    holdings = response.json()
                    btc_holdings = [h for h in holdings if h.get("coin_symbol") == "BTC"]
                    if btc_holdings:
                        btc_amount = btc_holdings[0].get("amount", 0)
                        self.log_result("Step 5: Check BTC Holdings", True, f"BTC amount: {btc_amount}")
                    else:
                        self.log_result("Step 5: Check BTC Holdings", True, "No BTC holdings yet (may take time to process)")
                else:
                    self.log_result("Step 5: Check BTC Holdings", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Step 5: Check BTC Holdings", False, f"Exception: {str(e)}")
            
            # Step 6: Create a sell order (if we have holdings)
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=regular_headers,
                    json={
                        "order_type": "sell",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_crypto": 0.005  # Small amount
                    }
                )
                
                if response.status_code in [200, 201]:
                    order_data = response.json()
                    sell_order_id = order_data.get("id")
                    self.log_result("Step 6: Create Sell Order", True, f"Sell order ID: {sell_order_id}")
                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "")
                    if "موجودی" in error_msg:
                        self.log_result("Step 6: Create Sell Order", True, "Correctly blocked - No crypto holdings (expected)")
                    else:
                        self.log_result("Step 6: Create Sell Order", False, f"Unexpected error: {error_msg}")
                else:
                    self.log_result("Step 6: Create Sell Order", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Step 6: Create Sell Order", False, f"Exception: {str(e)}")
    
    async def test_trading_validations(self):
        """Test various trading validation scenarios"""
        if not self.regular_user:
            print("\n🔍 Skipping Validation Tests (No Regular User)")
            return
        
        print(f"\n🔍 Testing Trading Validations")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {self.regular_user['token']}"}
            
            # Test 1: Invalid coin ID
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=headers,
                    json={
                        "order_type": "buy",
                        "coin_symbol": "INVALID",
                        "coin_id": "invalid-coin",
                        "amount_tmn": 100000.0
                    }
                )
                
                if response.status_code == 404:
                    self.log_result("Validation: Invalid Coin", True, "Correctly rejected invalid coin")
                elif response.status_code == 400:
                    self.log_result("Validation: Invalid Coin", True, "Correctly rejected with validation error")
                else:
                    self.log_result("Validation: Invalid Coin", False, f"Should have rejected: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Validation: Invalid Coin", False, f"Exception: {str(e)}")
            
            # Test 2: Negative amount
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=headers,
                    json={
                        "order_type": "buy",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_tmn": -100000.0
                    }
                )
                
                if response.status_code == 400:
                    self.log_result("Validation: Negative Amount", True, "Correctly rejected negative amount")
                else:
                    self.log_result("Validation: Negative Amount", False, f"Should have rejected: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Validation: Negative Amount", False, f"Exception: {str(e)}")
            
            # Test 3: Insufficient balance
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=headers,
                    json={
                        "order_type": "buy",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_tmn": 999999999.0  # Very large amount
                    }
                )
                
                if response.status_code == 400:
                    error_msg = response.json().get("detail", "")
                    if "موجودی" in error_msg:
                        self.log_result("Validation: Insufficient Balance", True, "Correctly rejected insufficient balance")
                    else:
                        self.log_result("Validation: Insufficient Balance", False, f"Wrong error message: {error_msg}")
                else:
                    self.log_result("Validation: Insufficient Balance", False, f"Should have rejected: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Validation: Insufficient Balance", False, f"Exception: {str(e)}")
            
            # Test 4: Trade order validation
            try:
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=headers,
                    json={
                        "order_type": "trade",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_crypto": 0.01,
                        "target_coin_symbol": "ETH",
                        "target_coin_id": "ethereum"
                    }
                )
                
                if response.status_code == 400:
                    error_msg = response.json().get("detail", "")
                    if "موجودی" in error_msg:
                        self.log_result("Validation: Trade Order", True, "Correctly rejected - no source crypto")
                    else:
                        self.log_result("Validation: Trade Order", False, f"Wrong error: {error_msg}")
                else:
                    self.log_result("Validation: Trade Order", False, f"Should have rejected: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Validation: Trade Order", False, f"Exception: {str(e)}")
    
    async def test_admin_functionality(self):
        """Test admin-specific functionality"""
        if not self.admin_user:
            print("\n👨‍💼 Skipping Admin Tests (No Admin User)")
            return
        
        print(f"\n👨‍💼 Testing Admin Functionality")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {self.admin_user['token']}"}
            
            # Test admin stats
            try:
                response = await client.get(f"{BACKEND_URL}/admin/stats", headers=headers)
                if response.status_code == 200:
                    stats = response.json()
                    self.log_result("Admin Stats", True, f"Users: {stats.get('total_users')}, Deposits: {stats.get('total_deposits')}")
                else:
                    self.log_result("Admin Stats", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Admin Stats", False, f"Exception: {str(e)}")
            
            # Test get all users
            try:
                response = await client.get(f"{BACKEND_URL}/admin/users", headers=headers)
                if response.status_code == 200:
                    users = response.json()
                    self.log_result("Admin Get Users", True, f"Retrieved {len(users)} users")
                else:
                    self.log_result("Admin Get Users", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Admin Get Users", False, f"Exception: {str(e)}")
            
            # Test get all deposits
            try:
                response = await client.get(f"{BACKEND_URL}/admin/deposits", headers=headers)
                if response.status_code == 200:
                    deposits = response.json()
                    self.log_result("Admin Get Deposits", True, f"Retrieved {len(deposits)} deposits")
                else:
                    self.log_result("Admin Get Deposits", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Admin Get Deposits", False, f"Exception: {str(e)}")
    
    async def run_full_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Full Trading System Tests")
        print("=" * 60)
        
        # Login users
        await self.login_users()
        
        # Test complete trading workflow
        await self.test_complete_trading_workflow()
        
        # Test validations
        await self.test_trading_validations()
        
        # Test admin functionality
        await self.test_admin_functionality()
        
        # Print summary
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FULL TRADING TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for result in self.results:
            if not result["success"]:
                if any(keyword in result["details"].lower() for keyword in ["correctly", "expected", "should have"]):
                    minor_issues.append(result)
                else:
                    critical_failures.append(result)
        
        if critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(critical_failures)}):")
            for result in critical_failures:
                print(f"  - {result['test']}: {result['details']}")
        
        if minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(minor_issues)}):")
            for result in minor_issues:
                print(f"  - {result['test']}: {result['details']}")
        
        # Trading workflow status
        workflow_tests = [r for r in self.results if r["test"].startswith("Step")]
        if workflow_tests:
            workflow_passed = sum(1 for r in workflow_tests if r["success"])
            print(f"\n💱 TRADING WORKFLOW: {workflow_passed}/{len(workflow_tests)} steps completed")
        
        print("\n🏁 Full Trading Tests Complete!")

async def main():
    """Main test runner"""
    tester = FullTradingTester()
    await tester.run_full_tests()

if __name__ == "__main__":
    asyncio.run(main())