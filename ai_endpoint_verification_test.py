#!/usr/bin/env python3
"""
AI Endpoint Verification Test
Specifically tests the AI endpoints mentioned in the review request
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://irancraft.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class AIEndpointVerifier:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.user_token = None
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
        
    async def setup_authentication(self) -> bool:
        """Setup authentication"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "testuser@example.com",
                "password": "testpass123"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("access_token")
                await self.log_test("Authentication Setup", True, "Successfully authenticated")
                return True
            else:
                await self.log_test("Authentication Setup", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Authentication Setup", False, f"Exception: {str(e)}")
            return False
    
    async def test_ai_chat_endpoint(self) -> bool:
        """Test POST /api/ai/chat endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test with Persian message
            test_data = {
                "message": "سلام، چطور می‌تونم بیت کوین خریداری کنم؟",
                "session_id": "test_session_123"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["success", "message", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    await self.log_test("AI Chat Endpoint Structure", False, 
                        f"Missing fields: {missing_fields}")
                    return False
                
                if data.get("success") and data.get("message"):
                    # Check if response is in Persian
                    message = data.get("message")
                    has_persian = any('\u0600' <= char <= '\u06FF' for char in message)
                    
                    if has_persian:
                        await self.log_test("AI Chat Endpoint", True, 
                            f"Persian response received: {message[:100]}...")
                        return True
                    else:
                        await self.log_test("AI Chat Endpoint", False, 
                            "Response not in Persian language")
                        return False
                else:
                    await self.log_test("AI Chat Endpoint", False, 
                        f"Invalid response format: {data}")
                    return False
            else:
                await self.log_test("AI Chat Endpoint", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("AI Chat Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_market_analysis_endpoint(self) -> bool:
        """Test POST /api/ai/market-analysis endpoint (if exists) or GET /api/ai/analyze/{coin_id}"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # First try the expected endpoint from review request
            sample_coin_data = {
                "coin_id": "bitcoin",
                "current_price": 45000,
                "price_change_24h": 2.5,
                "volume": 1000000000
            }
            
            # Try POST /api/ai/market-analysis
            response = await self.client.post(f"{BACKEND_URL}/ai/market-analysis", 
                headers=headers, json=sample_coin_data)
            
            if response.status_code == 404:
                # Endpoint doesn't exist, try the actual implementation
                response = await self.client.get(f"{BACKEND_URL}/ai/analyze/bitcoin", 
                    headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("analysis"):
                        await self.log_test("Market Analysis Endpoint", True, 
                            f"Analysis via /ai/analyze/bitcoin: {data.get('analysis')[:100]}...")
                        return True
                    else:
                        await self.log_test("Market Analysis Endpoint", False, 
                            f"Invalid response: {data}")
                        return False
                else:
                    await self.log_test("Market Analysis Endpoint", False, 
                        f"Both endpoints failed: {response.status_code}")
                    return False
            elif response.status_code == 200:
                data = response.json()
                await self.log_test("Market Analysis Endpoint", True, 
                    f"Analysis via /ai/market-analysis: {data}")
                return True
            else:
                await self.log_test("Market Analysis Endpoint", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Market Analysis Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_trading_signals_endpoint(self) -> bool:
        """Test POST /api/ai/trading-signals endpoint (if exists) or GET /api/ai/signals"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Try POST /api/ai/trading-signals first
            market_data = {
                "coins": [
                    {"symbol": "BTC", "price": 45000, "change_24h": 2.5},
                    {"symbol": "ETH", "price": 3000, "change_24h": -1.2}
                ]
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/trading-signals", 
                headers=headers, json=market_data)
            
            if response.status_code == 404:
                # Try the actual implementation
                response = await self.client.get(f"{BACKEND_URL}/ai/signals", 
                    headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("signals"):
                        await self.log_test("Trading Signals Endpoint", True, 
                            f"Signals via /ai/signals: {data.get('signals')[:100]}...")
                        return True
                    else:
                        await self.log_test("Trading Signals Endpoint", False, 
                            f"Invalid response: {data}")
                        return False
                else:
                    await self.log_test("Trading Signals Endpoint", False, 
                        f"Both endpoints failed: {response.status_code}")
                    return False
            elif response.status_code == 200:
                data = response.json()
                await self.log_test("Trading Signals Endpoint", True, 
                    f"Signals via /ai/trading-signals: {data}")
                return True
            else:
                await self.log_test("Trading Signals Endpoint", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Trading Signals Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_portfolio_analysis_endpoint(self) -> bool:
        """Test POST /api/ai/portfolio-analysis endpoint (if exists) or POST /api/ai/portfolio/analyze"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Try POST /api/ai/portfolio-analysis first
            portfolio_data = {
                "total_value": 10000,
                "holdings": [
                    {"symbol": "BTC", "amount": 0.5, "value": 7000},
                    {"symbol": "ETH", "amount": 2, "value": 3000}
                ]
            }
            
            response = await self.client.post(f"{BACKEND_URL}/ai/portfolio-analysis", 
                headers=headers, json=portfolio_data)
            
            if response.status_code == 404:
                # Try the actual implementation
                response = await self.client.post(f"{BACKEND_URL}/ai/portfolio/analyze", 
                    headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("advice"):
                        await self.log_test("Portfolio Analysis Endpoint", True, 
                            f"Analysis via /ai/portfolio/analyze: {data.get('advice')[:100]}...")
                        return True
                    else:
                        await self.log_test("Portfolio Analysis Endpoint", False, 
                            f"Invalid response: {data}")
                        return False
                else:
                    await self.log_test("Portfolio Analysis Endpoint", False, 
                        f"Both endpoints failed: {response.status_code}")
                    return False
            elif response.status_code == 200:
                data = response.json()
                await self.log_test("Portfolio Analysis Endpoint", True, 
                    f"Analysis via /ai/portfolio-analysis: {data}")
                return True
            else:
                await self.log_test("Portfolio Analysis Endpoint", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("Portfolio Analysis Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_emergent_llm_key_functionality(self) -> bool:
        """Test EMERGENT_LLM_KEY functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test a simple chat to verify the key is working
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json={
                    "message": "تست کلید API",
                    "session_id": "key_test"
                })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("EMERGENT_LLM_KEY Functionality", True, 
                        "API key working correctly")
                    return True
                elif "API key not configured" in data.get("error", ""):
                    await self.log_test("EMERGENT_LLM_KEY Functionality", False, 
                        "API key not configured")
                    return False
                else:
                    await self.log_test("EMERGENT_LLM_KEY Functionality", False, 
                        f"API error: {data.get('error')}")
                    return False
            else:
                await self.log_test("EMERGENT_LLM_KEY Functionality", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            await self.log_test("EMERGENT_LLM_KEY Functionality", False, f"Exception: {str(e)}")
            return False
    
    async def test_api_reliability_and_response_times(self) -> bool:
        """Test API call reliability and response times"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test multiple calls to check reliability
            successful_calls = 0
            total_calls = 5
            total_time = 0
            
            for i in range(total_calls):
                start_time = datetime.now()
                
                response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                    headers=headers, json={
                        "message": f"تست شماره {i+1}",
                        "session_id": f"reliability_test_{i}"
                    })
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                total_time += response_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        successful_calls += 1
            
            reliability_rate = successful_calls / total_calls
            avg_response_time = total_time / total_calls
            
            if reliability_rate >= 0.8 and avg_response_time < 10:  # 80% success, <10s avg
                await self.log_test("API Reliability and Response Times", True, 
                    f"Reliability: {reliability_rate:.1%}, Avg time: {avg_response_time:.2f}s")
                return True
            else:
                await self.log_test("API Reliability and Response Times", False, 
                    f"Poor performance - Reliability: {reliability_rate:.1%}, Avg time: {avg_response_time:.2f}s")
                return False
                
        except Exception as e:
            await self.log_test("API Reliability and Response Times", False, f"Exception: {str(e)}")
            return False
    
    async def test_error_handling_for_api_failures(self) -> bool:
        """Test error handling for API failures"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test with malformed request
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", 
                headers=headers, json={
                    # Missing required fields
                })
            
            if response.status_code in [400, 422]:
                await self.log_test("Error Handling for API Failures", True, 
                    "Gracefully handles malformed requests")
                return True
            else:
                await self.log_test("Error Handling for API Failures", False, 
                    f"Unexpected response to malformed request: {response.status_code}")
                return False
                
        except Exception as e:
            await self.log_test("Error Handling for API Failures", False, f"Exception: {str(e)}")
            return False
    
    async def run_verification_tests(self):
        """Run all verification tests"""
        print("🔍 Starting AI Endpoint Verification Tests")
        print("=" * 70)
        
        # Setup
        if not await self.setup_authentication():
            print("❌ Cannot continue without authentication")
            return
        
        # Test each endpoint mentioned in the review request
        print("\n💬 Testing AI Chatbot Endpoint...")
        await self.test_ai_chat_endpoint()
        
        print("\n📊 Testing Market Analysis Endpoint...")
        await self.test_market_analysis_endpoint()
        
        print("\n📈 Testing Trading Signals Endpoint...")
        await self.test_trading_signals_endpoint()
        
        print("\n💼 Testing Portfolio Analysis Endpoint...")
        await self.test_portfolio_analysis_endpoint()
        
        print("\n🔑 Testing EMERGENT_LLM_KEY Functionality...")
        await self.test_emergent_llm_key_functionality()
        
        print("\n⚡ Testing API Reliability and Response Times...")
        await self.test_api_reliability_and_response_times()
        
        print("\n⚠️ Testing Error Handling...")
        await self.test_error_handling_for_api_failures()
        
        print("\n" + "=" * 70)
        print("🏁 AI Endpoint Verification Complete!")
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 VERIFICATION SUMMARY")
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
    verifier = AIEndpointVerifier()
    try:
        await verifier.run_verification_tests()
    finally:
        await verifier.close()

if __name__ == "__main__":
    asyncio.run(main())