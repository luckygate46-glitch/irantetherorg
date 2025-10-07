#!/usr/bin/env python3
"""
AI Integration Testing for Iranian Crypto Exchange
Tests all AI services: Chatbot, Market Analysis, Trading Signals, Portfolio Analysis
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://irancraft.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class AIIntegrationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.user_token = None
        
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
        
    async def setup_test_user(self) -> bool:
        """Setup a test user for AI testing"""
        try:
            # Try to login with existing test user
            login_response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "testuser@example.com",
                "password": "testpass123"
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.user_token = data.get("access_token")
                await self.log_test("User Authentication Setup", True, "Successfully authenticated test user")
                return True
            else:
                await self.log_test("User Authentication Setup", False, f"Failed to authenticate: {login_response.text}")
                return False
                
        except Exception as e:
            await self.log_test("User Authentication Setup", False, f"Exception: {str(e)}")
            return False
    
    async def test_ai_chatbot(self) -> bool:
        """Test AI Chatbot functionality"""
        try:
            if not self.user_token:
                await self.log_test("AI Chatbot", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test Persian language chat
            test_messages = [
                "سلام، چطور می‌تونم بیت کوین خریداری کنم؟",
                "احراز هویت چیست و چرا لازم است؟",
                "کدام ارزهای دیجیتال را توصیه می‌کنید؟",
                "چطور می‌تونم امنیت حساب کاربری‌ام را بالا ببرم؟"
            ]
            
            success_count = 0
            
            for i, message in enumerate(test_messages):
                chat_data = {
                    "message": message,
                    "session_id": f"test_session_{i}"
                }
                
                response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                    headers=headers, json=chat_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("message"):
                        success_count += 1
                        await self.log_test(f"AI Chat Message {i+1}", True, 
                            f"Persian response received: {data.get('message')[:100]}...")
                    else:
                        await self.log_test(f"AI Chat Message {i+1}", False, 
                            f"Invalid response format: {data}")
                else:
                    await self.log_test(f"AI Chat Message {i+1}", False, 
                        f"HTTP {response.status_code}: {response.text}")
            
            overall_success = success_count >= len(test_messages) * 0.75  # 75% success rate
            await self.log_test("AI Chatbot Overall", overall_success, 
                f"Chatbot success rate: {success_count}/{len(test_messages)}")
            
            return overall_success
            
        except Exception as e:
            await self.log_test("AI Chatbot", False, f"Exception: {str(e)}")
            return False
    
    async def test_market_analysis_ai(self) -> bool:
        """Test Market Analysis AI"""
        try:
            if not self.user_token:
                await self.log_test("Market Analysis AI", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test analysis for different coins
            test_coins = ["bitcoin", "ethereum", "cardano"]
            success_count = 0
            
            for coin_id in test_coins:
                response = await self.client.get(f"{BACKEND_URL}/ai/analyze/{coin_id}", 
                    headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("analysis"):
                        success_count += 1
                        await self.log_test(f"Market Analysis {coin_id.upper()}", True, 
                            f"Analysis received: {data.get('analysis')[:100]}...")
                    else:
                        await self.log_test(f"Market Analysis {coin_id.upper()}", False, 
                            f"Invalid response: {data}")
                else:
                    await self.log_test(f"Market Analysis {coin_id.upper()}", False, 
                        f"HTTP {response.status_code}: {response.text}")
            
            overall_success = success_count >= len(test_coins) * 0.67  # 67% success rate
            await self.log_test("Market Analysis AI Overall", overall_success, 
                f"Market analysis success rate: {success_count}/{len(test_coins)}")
            
            return overall_success
            
        except Exception as e:
            await self.log_test("Market Analysis AI", False, f"Exception: {str(e)}")
            return False
    
    async def test_trading_signals_ai(self) -> bool:
        """Test Trading Signals AI"""
        try:
            if not self.user_token:
                await self.log_test("Trading Signals AI", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = await self.client.get(f"{BACKEND_URL}/ai/signals", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("signals"):
                    await self.log_test("Trading Signals AI", True, 
                        f"Trading signals received: {data.get('signals')[:150]}...")
                    return True
                else:
                    await self.log_test("Trading Signals AI", False, 
                        f"Invalid response format: {data}")
                    return False
            else:
                await self.log_test("Trading Signals AI", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Trading Signals AI", False, f"Exception: {str(e)}")
            return False
    
    async def test_portfolio_analysis_ai(self) -> bool:
        """Test Portfolio Analysis AI"""
        try:
            if not self.user_token:
                await self.log_test("Portfolio Analysis AI", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = await self.client.post(f"{BACKEND_URL}/ai/portfolio/analyze", 
                headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("advice"):
                    await self.log_test("Portfolio Analysis AI", True, 
                        f"Portfolio advice received: {data.get('advice')[:150]}...")
                    return True
                else:
                    await self.log_test("Portfolio Analysis AI", False, 
                        f"Invalid response format: {data}")
                    return False
            else:
                await self.log_test("Portfolio Analysis AI", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Portfolio Analysis AI", False, f"Exception: {str(e)}")
            return False
    
    async def test_price_prediction_ai(self) -> bool:
        """Test Price Prediction AI"""
        try:
            if not self.user_token:
                await self.log_test("Price Prediction AI", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test prediction for different timeframes
            test_cases = [
                ("bitcoin", "24h"),
                ("ethereum", "7d"),
                ("cardano", "1h")
            ]
            
            success_count = 0
            
            for coin_id, timeframe in test_cases:
                response = await self.client.get(
                    f"{BACKEND_URL}/ai/predict/{coin_id}?timeframe={timeframe}", 
                    headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("prediction"):
                        success_count += 1
                        await self.log_test(f"Price Prediction {coin_id.upper()} {timeframe}", True, 
                            f"Prediction received: {data.get('prediction')[:100]}...")
                    else:
                        await self.log_test(f"Price Prediction {coin_id.upper()} {timeframe}", False, 
                            f"Invalid response: {data}")
                else:
                    await self.log_test(f"Price Prediction {coin_id.upper()} {timeframe}", False, 
                        f"HTTP {response.status_code}: {response.text}")
            
            overall_success = success_count >= len(test_cases) * 0.67  # 67% success rate
            await self.log_test("Price Prediction AI Overall", overall_success, 
                f"Price prediction success rate: {success_count}/{len(test_cases)}")
            
            return overall_success
            
        except Exception as e:
            await self.log_test("Price Prediction AI", False, f"Exception: {str(e)}")
            return False
    
    async def test_ai_integration_health(self) -> bool:
        """Test AI integration health and emergentintegrations library"""
        try:
            # Test if EMERGENT_LLM_KEY is configured
            if not self.user_token:
                await self.log_test("AI Integration Health", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test a simple chat to verify emergentintegrations is working
            simple_test = {
                "message": "تست",
                "session_id": "health_check"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json=simple_test)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("AI Integration Health", True, 
                        "emergentintegrations library working correctly")
                    return True
                elif "API key not configured" in data.get("error", ""):
                    await self.log_test("AI Integration Health", False, 
                        "EMERGENT_LLM_KEY not configured properly")
                    return False
                else:
                    await self.log_test("AI Integration Health", False, 
                        f"AI service error: {data.get('error')}")
                    return False
            else:
                await self.log_test("AI Integration Health", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("AI Integration Health", False, f"Exception: {str(e)}")
            return False
    
    async def test_ai_error_handling(self) -> bool:
        """Test AI error handling and graceful failures"""
        try:
            if not self.user_token:
                await self.log_test("AI Error Handling", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test with empty message
            empty_message_test = {
                "message": "",
                "session_id": "error_test"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json=empty_message_test)
            
            if response.status_code in [200, 400, 422]:
                # Should handle gracefully
                await self.log_test("AI Error Handling - Empty Message", True, 
                    "Empty message handled gracefully")
            else:
                await self.log_test("AI Error Handling - Empty Message", False, 
                    f"Unexpected response: {response.status_code}")
            
            # Test with very long message
            long_message_test = {
                "message": "تست " * 1000,  # Very long message
                "session_id": "error_test_long"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json=long_message_test)
            
            if response.status_code in [200, 400, 413, 422]:
                # Should handle gracefully
                await self.log_test("AI Error Handling - Long Message", True, 
                    "Long message handled gracefully")
                return True
            else:
                await self.log_test("AI Error Handling - Long Message", False, 
                    f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_test("AI Error Handling", False, f"Exception: {str(e)}")
            return False
    
    async def test_ai_response_times(self) -> bool:
        """Test AI response times and performance"""
        try:
            if not self.user_token:
                await self.log_test("AI Response Times", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test response time for chat
            start_time = datetime.now()
            
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json={
                    "message": "سلام",
                    "session_id": "performance_test"
                })
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                if response_time < 30:  # Should respond within 30 seconds
                    await self.log_test("AI Response Times", True, 
                        f"Response time: {response_time:.2f}s (acceptable)")
                    return True
                else:
                    await self.log_test("AI Response Times", False, 
                        f"Response time too slow: {response_time:.2f}s")
                    return False
            else:
                await self.log_test("AI Response Times", False, 
                    f"Failed to get response: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_test("AI Response Times", False, f"Exception: {str(e)}")
            return False
    
    async def test_persian_language_quality(self) -> bool:
        """Test Persian language quality in AI responses"""
        try:
            if not self.user_token:
                await self.log_test("Persian Language Quality", False, "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test Persian language questions
            persian_tests = [
                "ارز دیجیتال چیست؟",
                "چطور می‌تونم بیت کوین خریداری کنم؟",
                "بهترین استراتژی سرمایه‌گذاری چیست؟"
            ]
            
            persian_responses = 0
            
            for question in persian_tests:
                response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                    headers=headers, json={
                        "message": question,
                        "session_id": "persian_test"
                    })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("message"):
                        message = data.get("message")
                        # Check if response contains Persian characters
                        persian_chars = any('\u0600' <= char <= '\u06FF' for char in message)
                        if persian_chars:
                            persian_responses += 1
            
            success_rate = persian_responses / len(persian_tests)
            if success_rate >= 0.8:  # 80% should be in Persian
                await self.log_test("Persian Language Quality", True, 
                    f"Persian response rate: {success_rate:.1%}")
                return True
            else:
                await self.log_test("Persian Language Quality", False, 
                    f"Low Persian response rate: {success_rate:.1%}")
                return False
                
        except Exception as e:
            await self.log_test("Persian Language Quality", False, f"Exception: {str(e)}")
            return False
    
    async def run_ai_integration_tests(self):
        """Run comprehensive AI integration tests"""
        print("🤖 Starting AI Integration Tests")
        print("=" * 70)
        
        # Setup
        print("\n🔧 Setting up test environment...")
        if not await self.setup_test_user():
            print("❌ Failed to setup test user. Cannot continue AI tests.")
            return
        
        # Test 1: AI Integration Health Check
        print("\n🏥 Testing AI Integration Health...")
        await self.test_ai_integration_health()
        
        # Test 2: AI Chatbot Functionality
        print("\n💬 Testing AI Chatbot Functionality...")
        await self.test_ai_chatbot()
        
        # Test 3: Market Analysis AI
        print("\n📊 Testing Market Analysis AI...")
        await self.test_market_analysis_ai()
        
        # Test 4: Trading Signals AI
        print("\n📈 Testing Trading Signals AI...")
        await self.test_trading_signals_ai()
        
        # Test 5: Portfolio Analysis AI
        print("\n💼 Testing Portfolio Analysis AI...")
        await self.test_portfolio_analysis_ai()
        
        # Test 6: Price Prediction AI
        print("\n🔮 Testing Price Prediction AI...")
        await self.test_price_prediction_ai()
        
        # Test 7: Error Handling
        print("\n⚠️ Testing AI Error Handling...")
        await self.test_ai_error_handling()
        
        # Test 8: Response Times
        print("\n⏱️ Testing AI Response Times...")
        await self.test_ai_response_times()
        
        # Test 9: Persian Language Quality
        print("\n🇮🇷 Testing Persian Language Quality...")
        await self.test_persian_language_quality()
        
        print("\n" + "=" * 70)
        print("🏁 AI Integration Testing Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 AI INTEGRATION TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in ["health", "integration", "chatbot", "overall"]):
                    critical_failures.append(result)
                else:
                    minor_issues.append(result)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL AI INTEGRATION ISSUES:")
            for result in critical_failures:
                print(f"  - {result['test']}: {result['details']}")
        
        if minor_issues:
            print(f"\n⚠️ MINOR ISSUES:")
            for result in minor_issues:
                print(f"  - {result['test']}: {result['details']}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = AIIntegrationTester()
    try:
        await tester.run_ai_integration_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())