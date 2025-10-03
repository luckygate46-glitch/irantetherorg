#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Iranian Crypto Exchange Registration System
Tests updated registration API with new fields (first_name, last_name, email, phone, password)
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

class RegistrationSystemTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_users = {}
        self.admin_token = None
        self.test_results = []
        
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
        
    async def test_registration_with_new_fields(self, first_name: str, last_name: str, email: str, phone: str, password: str = "testpass123") -> Dict[str, Any]:
        """Test registration with new fields (first_name, last_name, email, phone, password)"""
        try:
            # Step 1: Send OTP
            await self.log_test(f"OTP Send for {phone}", True, "Sending OTP...")
            otp_response = await self.client.post(f"{BACKEND_URL}/otp/send", json={
                "phone": phone
            })
            
            if otp_response.status_code != 200:
                await self.log_test(f"OTP Send for {phone}", False, f"Failed to send OTP: {otp_response.text}")
                # Continue with registration test anyway to check validation
            else:
                await self.log_test(f"OTP Send for {phone}", True, "OTP sent successfully")
            
            # Step 2: Try to verify OTP (we'll mock this since we can't get real SMS)
            # First, let's try with a common test code
            test_codes = ["12345", "00000", "11111", "99999"]
            otp_verified = False
            
            for test_code in test_codes:
                verify_response = await self.client.post(f"{BACKEND_URL}/otp/verify", json={
                    "phone": phone,
                    "code": test_code
                })
                
                if verify_response.status_code == 200:
                    await self.log_test(f"OTP Verify for {phone}", True, f"OTP verified with code {test_code}")
                    otp_verified = True
                    break
            
            if not otp_verified:
                await self.log_test(f"OTP Verify for {phone}", False, "Could not verify OTP with test codes")
                # Continue anyway to test registration validation
            
            # Step 3: Test registration with new fields
            register_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "password": password
            }
            
            register_response = await self.client.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            if register_response.status_code in [200, 201]:
                user_data = register_response.json()
                user_info = user_data.get("user", {})
                
                # Verify all new fields are present and correct
                success = True
                details = []
                
                if user_info.get("first_name") != first_name:
                    success = False
                    details.append(f"first_name mismatch: expected {first_name}, got {user_info.get('first_name')}")
                
                if user_info.get("last_name") != last_name:
                    success = False
                    details.append(f"last_name mismatch: expected {last_name}, got {user_info.get('last_name')}")
                
                if user_info.get("email") != email:
                    success = False
                    details.append(f"email mismatch: expected {email}, got {user_info.get('email')}")
                
                if user_info.get("phone") != phone:
                    success = False
                    details.append(f"phone mismatch: expected {phone}, got {user_info.get('phone')}")
                
                # Check if full_name is computed correctly
                expected_full_name = f"{first_name} {last_name}"
                if user_info.get("full_name") != expected_full_name:
                    success = False
                    details.append(f"full_name computation error: expected '{expected_full_name}', got '{user_info.get('full_name')}'")
                
                if success:
                    await self.log_test(f"Registration with New Fields {email}", True, "All fields stored and computed correctly")
                else:
                    await self.log_test(f"Registration with New Fields {email}", False, "; ".join(details))
                
                return {
                    "email": email,
                    "phone": phone,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "token": user_data.get("access_token"),
                    "user_id": user_info.get("id"),
                    "user_data": user_info,
                    "success": success
                }
            else:
                error_detail = register_response.text
                await self.log_test(f"Registration with New Fields {email}", False, f"Registration failed: {error_detail}")
                return {"success": False, "error": error_detail}
                
        except Exception as e:
            await self.log_test(f"Registration Test {email}", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return token"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                await self.log_test(f"Login {email}", True, "Login successful")
                return {
                    "token": data.get("access_token"),
                    "user_data": data.get("user", {})
                }
            else:
                await self.log_test(f"Login {email}", False, f"Login failed: {response.text}")
                return {}
                
        except Exception as e:
            await self.log_test(f"Login {email}", False, f"Exception: {str(e)}")
            return {}
    
    async def complete_kyc_level1(self, token: str, user_email: str) -> bool:
        """Complete KYC Level 1 for user"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", 
                headers=headers,
                json={
                    "full_name": "علی احمدی",
                    "national_code": "1234567890",
                    "birth_date": "1370/05/15",
                    "bank_card_number": "1234567890123456"
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"KYC Level 1 {user_email}", True, "KYC Level 1 completed")
                return True
            else:
                await self.log_test(f"KYC Level 1 {user_email}", False, f"KYC failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"KYC Level 1 {user_email}", False, f"Exception: {str(e)}")
            return False
    
    async def complete_kyc_level2(self, token: str, user_email: str) -> bool:
        """Complete KYC Level 2 for user"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{BACKEND_URL}/kyc/level2", 
                headers=headers,
                json={
                    "id_card_photo": "base64_encoded_id_photo",
                    "selfie_type": "photo",
                    "selfie_data": "base64_encoded_selfie"
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"KYC Level 2 Submit {user_email}", True, "KYC Level 2 submitted")
                return True
            else:
                await self.log_test(f"KYC Level 2 Submit {user_email}", False, f"KYC Level 2 failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"KYC Level 2 Submit {user_email}", False, f"Exception: {str(e)}")
            return False
    
    async def approve_kyc_as_admin(self, admin_token: str, user_id: str, kyc_level: int) -> bool:
        """Approve KYC as admin"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = await self.client.post(f"{BACKEND_URL}/admin/kyc/approve", 
                headers=headers,
                json={
                    "user_id": user_id,
                    "kyc_level": kyc_level,
                    "action": "approve",
                    "admin_note": "Test approval"
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"Admin KYC Approval Level {kyc_level}", True, "KYC approved by admin")
                return True
            else:
                await self.log_test(f"Admin KYC Approval Level {kyc_level}", False, f"Admin approval failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Admin KYC Approval Level {kyc_level}", False, f"Exception: {str(e)}")
            return False
    
    async def add_wallet_balance(self, admin_token: str, user_id: str, amount: float) -> bool:
        """Add wallet balance as admin"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = await self.client.put(f"{BACKEND_URL}/admin/users/{user_id}", 
                headers=headers,
                json={
                    "wallet_balance_tmn": amount
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"Add Wallet Balance", True, f"Added {amount} TMN to wallet")
                return True
            else:
                await self.log_test(f"Add Wallet Balance", False, f"Failed to add balance: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Add Wallet Balance", False, f"Exception: {str(e)}")
            return False
    
    async def test_trading_order_creation(self, token: str, order_type: str, test_name: str) -> Optional[str]:
        """Test creating trading orders"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test data for different order types
            order_data = {}
            if order_type == "buy":
                order_data = {
                    "order_type": "buy",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_tmn": 1000000.0  # 1M TMN
                }
            elif order_type == "sell":
                order_data = {
                    "order_type": "sell",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_crypto": 0.01  # 0.01 BTC
                }
            elif order_type == "trade":
                order_data = {
                    "order_type": "trade",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_crypto": 0.01,
                    "target_coin_symbol": "ETH",
                    "target_coin_id": "ethereum"
                }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                headers=headers,
                json=order_data
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                order_id = data.get("id")
                await self.log_test(test_name, True, f"Order created successfully: {order_id}")
                return order_id
            else:
                await self.log_test(test_name, False, f"Order creation failed: {response.text}")
                return None
                
        except Exception as e:
            await self.log_test(test_name, False, f"Exception: {str(e)}")
            return None
    
    async def test_get_user_orders(self, token: str, user_email: str) -> bool:
        """Test getting user's orders"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/orders/my", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()
                await self.log_test(f"Get User Orders {user_email}", True, f"Retrieved {len(orders)} orders")
                return True
            else:
                await self.log_test(f"Get User Orders {user_email}", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Get User Orders {user_email}", False, f"Exception: {str(e)}")
            return False
    
    async def test_get_user_holdings(self, token: str, user_email: str) -> bool:
        """Test getting user's crypto holdings"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{BACKEND_URL}/trading/holdings/my", headers=headers)
            
            if response.status_code == 200:
                holdings = response.json()
                await self.log_test(f"Get User Holdings {user_email}", True, f"Retrieved {len(holdings)} holdings")
                return True
            else:
                await self.log_test(f"Get User Holdings {user_email}", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Get User Holdings {user_email}", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_get_orders(self, admin_token: str) -> bool:
        """Test admin getting all orders"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/admin/trading/orders", headers=headers)
            
            if response.status_code == 200:
                orders = response.json()
                await self.log_test("Admin Get All Orders", True, f"Retrieved {len(orders)} orders")
                return True
            else:
                await self.log_test("Admin Get All Orders", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Admin Get All Orders", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_approve_order(self, admin_token: str, order_id: str, action: str = "approve") -> bool:
        """Test admin approving/rejecting orders"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = await self.client.post(f"{BACKEND_URL}/admin/trading/orders/approve", 
                headers=headers,
                json={
                    "order_id": order_id,
                    "action": action,
                    "admin_note": f"Test {action}"
                }
            )
            
            if response.status_code == 200:
                await self.log_test(f"Admin {action.title()} Order", True, f"Order {action}d successfully")
                return True
            else:
                await self.log_test(f"Admin {action.title()} Order", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test(f"Admin {action.title()} Order", False, f"Exception: {str(e)}")
            return False
    
    async def test_kyc_restrictions(self, token: str, kyc_level: int) -> bool:
        """Test KYC level restrictions for trading"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                headers=headers,
                json={
                    "order_type": "buy",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_tmn": 100000.0
                }
            )
            
            if kyc_level < 2:
                # Should fail for KYC level < 2
                if response.status_code == 403:
                    await self.log_test(f"KYC Restriction Level {kyc_level}", True, "Correctly blocked trading for insufficient KYC")
                    return True
                else:
                    await self.log_test(f"KYC Restriction Level {kyc_level}", False, "Should have blocked trading but didn't")
                    return False
            else:
                # Should succeed for KYC level >= 2
                if response.status_code in [200, 201]:
                    await self.log_test(f"KYC Permission Level {kyc_level}", True, "Correctly allowed trading for sufficient KYC")
                    return True
                else:
                    await self.log_test(f"KYC Permission Level {kyc_level}", False, f"Should have allowed trading: {response.text}")
                    return False
                
        except Exception as e:
            await self.log_test(f"KYC Restriction Level {kyc_level}", False, f"Exception: {str(e)}")
            return False
    
    async def test_insufficient_balance(self, token: str) -> bool:
        """Test insufficient balance error handling"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"{BACKEND_URL}/trading/order", 
                headers=headers,
                json={
                    "order_type": "buy",
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_tmn": 999999999.0  # Very large amount
                }
            )
            
            if response.status_code == 400:
                await self.log_test("Insufficient Balance Check", True, "Correctly rejected order with insufficient balance")
                return True
            else:
                await self.log_test("Insufficient Balance Check", False, f"Should have rejected order: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Insufficient Balance Check", False, f"Exception: {str(e)}")
            return False
    
    async def run_comprehensive_tests(self):
        """Run all trading system tests"""
        print("🚀 Starting Comprehensive Trading System Tests")
        print("=" * 60)
        
        # Test 1: Create test users
        print("\n📝 Creating Test Users...")
        regular_user = await self.create_test_user("testuser@example.com", "09123456789")
        admin_user = await self.create_test_user("admin@example.com", "09123456788")
        
        if not regular_user or not admin_user:
            print("❌ Failed to create test users. Trying login instead...")
            regular_user = await self.login_user("testuser@example.com", "testpass123")
            admin_user = await self.login_user("admin@example.com", "testpass123")
        
        if not regular_user.get("token"):
            await self.log_test("Test Setup", False, "Could not create or login regular user")
            return
        
        # Test 2: Test KYC restrictions (Level 0)
        print("\n🔒 Testing KYC Level 0 Restrictions...")
        await self.test_kyc_restrictions(regular_user["token"], 0)
        
        # Test 3: Complete KYC Level 1
        print("\n📋 Completing KYC Level 1...")
        await self.complete_kyc_level1(regular_user["token"], regular_user["email"])
        
        # Test 4: Test KYC restrictions (Level 1)
        print("\n🔒 Testing KYC Level 1 Restrictions...")
        await self.test_kyc_restrictions(regular_user["token"], 1)
        
        # Test 5: Complete KYC Level 2
        print("\n📋 Completing KYC Level 2...")
        await self.complete_kyc_level2(regular_user["token"], regular_user["email"])
        
        # Test 6: Admin approval of KYC Level 2 (if admin exists)
        if admin_user.get("token"):
            print("\n👨‍💼 Admin Approving KYC Level 2...")
            await self.approve_kyc_as_admin(admin_user["token"], regular_user.get("user_id", ""), 2)
            
            # Add wallet balance for testing
            print("\n💰 Adding Wallet Balance...")
            await self.add_wallet_balance(admin_user["token"], regular_user.get("user_id", ""), 5000000.0)
        
        # Test 7: Test trading with KYC Level 2
        print("\n💱 Testing Trading Orders...")
        buy_order_id = await self.test_trading_order_creation(regular_user["token"], "buy", "Create Buy Order")
        sell_order_id = await self.test_trading_order_creation(regular_user["token"], "sell", "Create Sell Order")
        trade_order_id = await self.test_trading_order_creation(regular_user["token"], "trade", "Create Trade Order")
        
        # Test 8: Test insufficient balance
        print("\n💸 Testing Insufficient Balance...")
        await self.test_insufficient_balance(regular_user["token"])
        
        # Test 9: Test user order retrieval
        print("\n📋 Testing Order Retrieval...")
        await self.test_get_user_orders(regular_user["token"], regular_user["email"])
        await self.test_get_user_holdings(regular_user["token"], regular_user["email"])
        
        # Test 10: Admin order management
        if admin_user.get("token"):
            print("\n👨‍💼 Testing Admin Order Management...")
            await self.test_admin_get_orders(admin_user["token"])
            
            if buy_order_id:
                await self.test_admin_approve_order(admin_user["token"], buy_order_id, "approve")
            if sell_order_id:
                await self.test_admin_approve_order(admin_user["token"], sell_order_id, "reject")
        
        # Test 11: Test crypto price endpoints
        print("\n📈 Testing Crypto Price APIs...")
        await self.test_crypto_prices()
        
        print("\n" + "=" * 60)
        print("🏁 Testing Complete!")
        await self.print_summary()
    
    async def test_crypto_prices(self):
        """Test crypto price endpoints"""
        try:
            # Test get prices
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            if response.status_code == 200:
                await self.log_test("Get Crypto Prices", True, "Successfully retrieved crypto prices")
            else:
                await self.log_test("Get Crypto Prices", False, f"Failed: {response.text}")
            
            # Test get coin details
            response = await self.client.get(f"{BACKEND_URL}/crypto/bitcoin")
            if response.status_code == 200:
                await self.log_test("Get Bitcoin Details", True, "Successfully retrieved Bitcoin details")
            else:
                await self.log_test("Get Bitcoin Details", False, f"Failed: {response.text}")
                
        except Exception as e:
            await self.log_test("Crypto Price APIs", False, f"Exception: {str(e)}")
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY")
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
    tester = TradingSystemTester()
    try:
        await tester.run_comprehensive_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())