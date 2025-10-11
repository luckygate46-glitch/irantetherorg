#!/usr/bin/env python3
"""
Regular User Buy Order Testing for Iranian Crypto Exchange
Testing buy order workflow with a regular user (non-admin)
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://cryptotoman.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpass123"

class RegularUserBuyOrderTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.user_token = None
        self.user_data = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up Regular User Buy Order testing...")
        
        # Login as regular user
        await self.login_regular_user()
        
    async def login_regular_user(self):
        """Login as regular user"""
        print("\n🔐 Testing Regular User Login...")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.user_data = data["user"]
                
                print(f"✅ Regular user login successful: {self.user_data.get('full_name', 'Test User')}")
                print(f"📊 User ID: {self.user_data.get('id')}")
                print(f"📊 Email: {self.user_data.get('email')}")
                print(f"📊 KYC Level: {self.user_data.get('kyc_level')}")
                print(f"📊 Wallet Balance: {self.user_data.get('wallet_balance_tmn', 0):,.0f} TMN")
                print(f"📊 Is Admin: {self.user_data.get('is_admin')}")
                
                # Check if user is actually regular user
                if not self.user_data.get('is_admin', False):
                    print("✅ Confirmed: User is regular user (not admin)")
                else:
                    print("⚠️  Warning: User has admin privileges")
                
                # Check KYC level for trading
                kyc_level = self.user_data.get('kyc_level', 0)
                if kyc_level >= 2:
                    print("✅ Confirmed: User has KYC Level 2+ (can trade)")
                elif kyc_level == 1:
                    print("⚠️  User has KYC Level 1 (limited trading)")
                else:
                    print("⚠️  User has KYC Level 0 (cannot trade)")
                
                return True
            else:
                print(f"❌ Regular user login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Regular user login error: {str(e)}")
            return False

    async def test_buy_order_with_insufficient_balance(self):
        """Test buy order with insufficient balance"""
        print("\n💸 Testing Buy Order with Insufficient Balance...")
        
        if not self.user_token:
            print("❌ Cannot test without authentication")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Try to buy more than user's balance
        current_balance = self.user_data.get('wallet_balance_tmn', 0)
        excessive_amount = current_balance + 100000  # More than balance
        
        buy_order_data = {
            "order_type": "buy",
            "coin_symbol": "USDT",
            "coin_id": "tether",
            "amount_tmn": excessive_amount
        }
        
        print(f"📊 Attempting buy order for {excessive_amount:,.0f} TMN (balance: {current_balance:,.0f} TMN)")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=buy_order_data)
            
            if response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                error_message = error_data.get('detail', 'Unknown error')
                
                print(f"✅ Insufficient balance validation working: {error_message}")
                
                # Check if error message is in Persian
                if 'موجودی' in error_message or 'کافی' in error_message:
                    print("✅ Persian error message confirmed")
                else:
                    print("⚠️  Error message not in Persian")
                
                self.test_results.append({
                    "test": "insufficient_balance_validation", 
                    "status": "✅ PASS", 
                    "details": "Balance validation working correctly"
                })
                
            elif response.status_code == 200:
                print("❌ Order was created despite insufficient balance!")
                self.test_results.append({
                    "test": "insufficient_balance_validation", 
                    "status": "❌ FAIL", 
                    "details": "Order created with insufficient balance"
                })
                
            else:
                print(f"❓ Unexpected response: {response.status_code} - {response.text}")
                self.test_results.append({
                    "test": "insufficient_balance_validation", 
                    "status": "❓ UNEXPECTED", 
                    "details": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Insufficient balance test error: {str(e)}")
            self.test_results.append({
                "test": "insufficient_balance_validation", 
                "status": "❌ ERROR", 
                "details": str(e)
            })

    async def test_kyc_level_requirement(self):
        """Test KYC level requirement for trading"""
        print("\n🆔 Testing KYC Level Requirement...")
        
        if not self.user_token:
            print("❌ Cannot test without authentication")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        kyc_level = self.user_data.get('kyc_level', 0)
        
        buy_order_data = {
            "order_type": "buy",
            "coin_symbol": "USDT",
            "coin_id": "tether",
            "amount_tmn": 10000  # Small amount
        }
        
        print(f"📊 Testing with KYC Level {kyc_level}")
        
        try:
            response = await self.client.post(f"{BACKEND_URL}/trading/order", headers=headers, json=buy_order_data)
            
            if kyc_level < 2:
                if response.status_code == 403:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                    error_message = error_data.get('detail', 'Unknown error')
                    
                    print(f"✅ KYC Level 2 requirement enforced: {error_message}")
                    
                    # Check if error message is in Persian
                    if 'احراز هویت' in error_message or 'سطح' in error_message:
                        print("✅ Persian KYC error message confirmed")
                    else:
                        print("⚠️  KYC error message not in Persian")
                    
                    self.test_results.append({
                        "test": "kyc_level_requirement", 
                        "status": "✅ PASS", 
                        "details": f"KYC Level 2 requirement enforced for Level {kyc_level} user"
                    })
                    
                else:
                    print(f"❌ Order allowed despite insufficient KYC level: {response.status_code}")
                    self.test_results.append({
                        "test": "kyc_level_requirement", 
                        "status": "❌ FAIL", 
                        "details": f"Order allowed with KYC Level {kyc_level}"
                    })
            else:
                # User has KYC Level 2+, order should be processed
                if response.status_code in [200, 400]:  # 200 = success, 400 = validation error (balance, etc.)
                    print(f"✅ KYC Level 2+ user can access trading: {response.status_code}")
                    self.test_results.append({
                        "test": "kyc_level_requirement", 
                        "status": "✅ PASS", 
                        "details": f"KYC Level {kyc_level} user can access trading"
                    })
                else:
                    print(f"❓ Unexpected response for KYC Level 2+ user: {response.status_code}")
                    self.test_results.append({
                        "test": "kyc_level_requirement", 
                        "status": "❓ UNEXPECTED", 
                        "details": f"HTTP {response.status_code} for KYC Level {kyc_level}"
                    })
                
        except Exception as e:
            print(f"❌ KYC level test error: {str(e)}")
            self.test_results.append({
                "test": "kyc_level_requirement", 
                "status": "❌ ERROR", 
                "details": str(e)
            })

    async def test_wallet_address_requirement(self):
        """Test wallet address requirement for buy orders"""
        print("\n💳 Testing Wallet Address Requirement...")
        
        if not self.user_token:
            print("❌ Cannot test without authentication")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # First check if user has wallet addresses
        try:
            wallet_response = await self.client.get(f"{BACKEND_URL}/user/wallet-addresses", headers=headers)
            
            if wallet_response.status_code == 200:
                wallet_addresses = wallet_response.json()
                usdt_wallet = None
                
                for wallet in wallet_addresses:
                    if wallet.get('symbol', '').upper() == 'USDT':
                        usdt_wallet = wallet
                        break
                
                if usdt_wallet:
                    print(f"✅ User has USDT wallet: {usdt_wallet.get('address', '')[:20]}...")
                    print(f"📊 Wallet verified: {usdt_wallet.get('verified', False)}")
                    
                    self.test_results.append({
                        "test": "wallet_address_requirement", 
                        "status": "✅ PASS", 
                        "details": "User has USDT wallet address"
                    })
                else:
                    print("⚠️  User does not have USDT wallet address")
                    print("📊 This may prevent buy order creation")
                    
                    self.test_results.append({
                        "test": "wallet_address_requirement", 
                        "status": "⚠️  INFO", 
                        "details": "User has no USDT wallet address"
                    })
            else:
                print(f"❌ Cannot check wallet addresses: {wallet_response.status_code}")
                self.test_results.append({
                    "test": "wallet_address_requirement", 
                    "status": "❌ FAIL", 
                    "details": "Cannot access wallet addresses"
                })
                
        except Exception as e:
            print(f"❌ Wallet address check error: {str(e)}")
            self.test_results.append({
                "test": "wallet_address_requirement", 
                "status": "❌ ERROR", 
                "details": str(e)
            })

    async def run_all_tests(self):
        """Run all regular user tests"""
        print("🚀 Starting Regular User Buy Order Testing...")
        print("=" * 60)
        
        await self.setup()
        
        if not self.user_token:
            print("❌ Cannot proceed without user authentication")
            return
        
        # Run all tests
        await self.test_kyc_level_requirement()
        await self.test_wallet_address_requirement()
        await self.test_buy_order_with_insufficient_balance()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 REGULAR USER BUY ORDER TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        warning_tests = [r for r in self.test_results if "⚠️" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⚠️  WARNINGS/INFO: {len(warning_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if warning_tests:
            print("\n⚠️  WARNINGS/INFO:")
            for test in warning_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n🎯 REGULAR USER VALIDATION ANALYSIS:")
        
        # Analyze results
        kyc_validation = any("kyc_level_requirement" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)
        balance_validation = any("insufficient_balance_validation" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)
        wallet_check = any("wallet_address_requirement" in r["test"] and "✅ PASS" in r["status"] for r in self.test_results)
        
        if kyc_validation:
            print("✅ KYC Level 2 requirement properly enforced")
        if balance_validation:
            print("✅ Balance validation working correctly")
        if wallet_check:
            print("✅ Wallet address management working")
        
        # Overall assessment
        validation_tests = [kyc_validation, balance_validation]
        if all(validation_tests):
            print("\n🎉 REGULAR USER VALIDATION: FULLY FUNCTIONAL")
            print("✅ All security and validation checks working")
            print("✅ System properly protects against invalid orders")
        elif any(validation_tests):
            print("\n⚠️  REGULAR USER VALIDATION: PARTIALLY FUNCTIONAL")
            print("Some validation working, others need attention")
        else:
            print("\n❌ REGULAR USER VALIDATION: NEEDS ATTENTION")
            print("Critical validation not working properly")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = RegularUserBuyOrderTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())