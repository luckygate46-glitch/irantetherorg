#!/usr/bin/env python3
"""
Comprehensive Backend System Health Check & Analysis for Iranian Crypto Exchange
Tests all backend APIs, security, performance, and integrations as requested
"""

import asyncio
import httpx
import json
import time
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
TEST_TIMEOUT = 30.0

class ComprehensiveBackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
        self.performance_metrics = []
        self.security_issues = []
        self.integration_status = {}
        self.admin_token = None
        self.test_user_token = None
        self.test_user_data = {}
        
    async def log_test(self, category: str, test_name: str, success: bool, details: str = "", response_data: Any = None, performance_ms: float = None):
        """Log test results with categorization"""
        result = {
            "category": category,
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "performance_ms": performance_ms
        }
        self.test_results.append(result)
        
        if performance_ms:
            self.performance_metrics.append({
                "endpoint": test_name,
                "response_time_ms": performance_ms,
                "category": category
            })
        
        status = "✅ PASS" if success else "❌ FAIL"
        perf_info = f" ({performance_ms:.0f}ms)" if performance_ms else ""
        print(f"{status} [{category}] {test_name}: {details}{perf_info}")
    
    async def log_security_issue(self, severity: str, issue: str, details: str):
        """Log security issues"""
        self.security_issues.append({
            "severity": severity,
            "issue": issue,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"🔒 SECURITY [{severity}] {issue}: {details}")
    
    async def measure_performance(self, func, *args, **kwargs):
        """Measure function execution time"""
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        return result, (end_time - start_time) * 1000
    
    # ==================== 1. API PERFORMANCE & RELIABILITY ====================
    
    async def test_authentication_endpoints(self):
        """Test all authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test registration endpoint structure
        start_time = time.time()
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/register", json={
                "first_name": "تست",
                "last_name": "کاربر",
                "email": "comprehensive.test@example.com",
                "phone": "09123456789",
                "password": "testpass123"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400 and "تایید" in response.text:
                await self.log_test("Authentication", "Registration API Structure", True, 
                                  "Registration endpoint working, requires OTP as expected", 
                                  response.json(), response_time)
            else:
                await self.log_test("Authentication", "Registration API Structure", False, 
                                  f"Unexpected response: {response.status_code} - {response.text}", 
                                  None, response_time)
        except Exception as e:
            await self.log_test("Authentication", "Registration API Structure", False, f"Exception: {str(e)}")
        
        # Test login endpoint
        start_time = time.time()
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "nonexistent@test.com",
                "password": "wrongpass"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                await self.log_test("Authentication", "Login API Error Handling", True, 
                                  "Login correctly rejects invalid credentials", 
                                  None, response_time)
            else:
                await self.log_test("Authentication", "Login API Error Handling", False, 
                                  f"Login should return 401 for invalid credentials: {response.status_code}")
        except Exception as e:
            await self.log_test("Authentication", "Login API Error Handling", False, f"Exception: {str(e)}")
        
        # Test /auth/me without token
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/auth/me")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 403:
                await self.log_test("Authentication", "Auth Me Security", True, 
                                  "Auth/me correctly requires authentication", 
                                  None, response_time)
            else:
                await self.log_test("Authentication", "Auth Me Security", False, 
                                  f"Auth/me should require authentication: {response.status_code}")
                await self.log_security_issue("HIGH", "Authentication Bypass", 
                                             "/auth/me accessible without token")
        except Exception as e:
            await self.log_test("Authentication", "Auth Me Security", False, f"Exception: {str(e)}")
    
    async def test_trading_endpoints(self):
        """Test trading endpoints"""
        print("\n💰 Testing Trading Endpoints...")
        
        # Test trading order creation without auth
        start_time = time.time()
        try:
            response = await self.client.post(f"{BACKEND_URL}/trading/order", json={
                "order_type": "buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn": 1000000
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 403:
                await self.log_test("Trading", "Trading Order Security", True, 
                                  "Trading order correctly requires authentication", 
                                  None, response_time)
            else:
                await self.log_test("Trading", "Trading Order Security", False, 
                                  f"Trading order should require authentication: {response.status_code}")
                await self.log_security_issue("HIGH", "Authorization Bypass", 
                                             "/trading/order accessible without token")
        except Exception as e:
            await self.log_test("Trading", "Trading Order Security", False, f"Exception: {str(e)}")
        
        # Test holdings endpoint without auth
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/trading/holdings/my")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 403:
                await self.log_test("Trading", "Holdings Security", True, 
                                  "Holdings endpoint correctly requires authentication", 
                                  None, response_time)
            else:
                await self.log_test("Trading", "Holdings Security", False, 
                                  f"Holdings should require authentication: {response.status_code}")
        except Exception as e:
            await self.log_test("Trading", "Holdings Security", False, f"Exception: {str(e)}")
        
        # Test orders endpoint without auth
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/trading/orders/my")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 403:
                await self.log_test("Trading", "Orders Security", True, 
                                  "Orders endpoint correctly requires authentication", 
                                  None, response_time)
            else:
                await self.log_test("Trading", "Orders Security", False, 
                                  f"Orders should require authentication: {response.status_code}")
        except Exception as e:
            await self.log_test("Trading", "Orders Security", False, f"Exception: {str(e)}")
    
    async def test_admin_endpoints(self):
        """Test admin management APIs"""
        print("\n👨‍💼 Testing Admin Management APIs...")
        
        admin_endpoints = [
            "/admin/users",
            "/admin/deposits", 
            "/admin/orders",
            "/admin/stats",
            "/admin/trading/orders"
        ]
        
        for endpoint in admin_endpoints:
            start_time = time.time()
            try:
                response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 403:
                    await self.log_test("Admin", f"Admin {endpoint} Security", True, 
                                      "Admin endpoint correctly requires admin authentication", 
                                      None, response_time)
                else:
                    await self.log_test("Admin", f"Admin {endpoint} Security", False, 
                                      f"Admin endpoint should require admin auth: {response.status_code}")
                    await self.log_security_issue("CRITICAL", "Admin Access Control", 
                                                 f"{endpoint} accessible without admin token")
            except Exception as e:
                await self.log_test("Admin", f"Admin {endpoint} Security", False, f"Exception: {str(e)}")
    
    async def test_kyc_endpoints(self):
        """Test KYC workflow endpoints"""
        print("\n📋 Testing KYC Workflow...")
        
        # Test KYC level1 without auth
        start_time = time.time()
        try:
            response = await self.client.post(f"{BACKEND_URL}/kyc/level1", json={
                "full_name": "تست کاربر",
                "national_code": "1234567890",
                "birth_date": "1370/05/15",
                "bank_card_number": "1234567890123456"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 403:
                await self.log_test("KYC", "KYC Level1 Security", True, 
                                  "KYC Level1 correctly requires authentication", 
                                  None, response_time)
            else:
                await self.log_test("KYC", "KYC Level1 Security", False, 
                                  f"KYC Level1 should require authentication: {response.status_code}")
        except Exception as e:
            await self.log_test("KYC", "KYC Level1 Security", False, f"Exception: {str(e)}")
        
        # Test KYC status without auth
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/kyc/status")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 403:
                await self.log_test("KYC", "KYC Status Security", True, 
                                  "KYC Status correctly requires authentication", 
                                  None, response_time)
            else:
                await self.log_test("KYC", "KYC Status Security", False, 
                                  f"KYC Status should require authentication: {response.status_code}")
        except Exception as e:
            await self.log_test("KYC", "KYC Status Security", False, f"Exception: {str(e)}")
    
    async def test_crypto_price_apis(self):
        """Test crypto price APIs"""
        print("\n📈 Testing Crypto Price APIs...")
        
        # Test crypto prices endpoint
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("Crypto", "Crypto Prices API", True, 
                                      f"Crypto prices API working, returned {len(data.get('data', {}))} coins", 
                                      None, response_time)
                else:
                    await self.log_test("Crypto", "Crypto Prices API", False, 
                                      f"Crypto prices API returned success=false: {data.get('error')}", 
                                      None, response_time)
            else:
                await self.log_test("Crypto", "Crypto Prices API", False, 
                                  f"Crypto prices API failed: {response.status_code} - {response.text}", 
                                  None, response_time)
        except Exception as e:
            await self.log_test("Crypto", "Crypto Prices API", False, f"Exception: {str(e)}")
        
        # Test specific coin details
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/bitcoin")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("Crypto", "Bitcoin Details API", True, 
                                      "Bitcoin details API working", 
                                      None, response_time)
                else:
                    await self.log_test("Crypto", "Bitcoin Details API", False, 
                                      f"Bitcoin details API returned success=false: {data.get('error')}")
            else:
                await self.log_test("Crypto", "Bitcoin Details API", False, 
                                  f"Bitcoin details API failed: {response.status_code}")
        except Exception as e:
            await self.log_test("Crypto", "Bitcoin Details API", False, f"Exception: {str(e)}")
        
        # Test trending coins
        start_time = time.time()
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/trending/coins")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    await self.log_test("Crypto", "Trending Coins API", True, 
                                      "Trending coins API working", 
                                      None, response_time)
                else:
                    await self.log_test("Crypto", "Trending Coins API", False, 
                                      f"Trending coins API returned success=false: {data.get('error')}")
            else:
                await self.log_test("Crypto", "Trending Coins API", False, 
                                  f"Trending coins API failed: {response.status_code}")
        except Exception as e:
            await self.log_test("Crypto", "Trending Coins API", False, f"Exception: {str(e)}")
    
    # ==================== 2. SECURITY ASSESSMENT ====================
    
    async def test_jwt_security(self):
        """Test JWT token security"""
        print("\n🔒 Testing JWT Security...")
        
        # Test with invalid token
        invalid_tokens = [
            "invalid.token.here",
            "Bearer invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            ""
        ]
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = await self.client.get(f"{BACKEND_URL}/auth/me", headers=headers)
                
                if response.status_code == 401:
                    await self.log_test("Security", f"Invalid Token Rejection", True, 
                                      f"Correctly rejected invalid token: {token[:20]}...")
                else:
                    await self.log_test("Security", f"Invalid Token Rejection", False, 
                                      f"Should reject invalid token: {response.status_code}")
                    await self.log_security_issue("HIGH", "Token Validation", 
                                                 f"Invalid token accepted: {token[:20]}...")
            except Exception as e:
                await self.log_test("Security", f"Invalid Token Test", False, f"Exception: {str(e)}")
    
    async def test_input_validation(self):
        """Test input validation and sanitization"""
        print("\n🛡️ Testing Input Validation...")
        
        # Test SQL injection attempts
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        for payload in sql_payloads:
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": payload,
                    "password": "test"
                })
                
                if response.status_code in [400, 401, 422]:
                    await self.log_test("Security", f"SQL Injection Protection", True, 
                                      f"Correctly handled SQL injection attempt")
                else:
                    await self.log_test("Security", f"SQL Injection Protection", False, 
                                      f"Potential SQL injection vulnerability: {response.status_code}")
                    await self.log_security_issue("CRITICAL", "SQL Injection", 
                                                 f"SQL payload not properly handled: {payload}")
            except Exception as e:
                await self.log_test("Security", f"SQL Injection Test", False, f"Exception: {str(e)}")
        
        # Test XSS attempts
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/register", json={
                    "first_name": payload,
                    "last_name": "test",
                    "email": "xss@test.com",
                    "phone": "09123456789",
                    "password": "testpass123"
                })
                
                if response.status_code in [400, 422]:
                    await self.log_test("Security", f"XSS Protection", True, 
                                      f"Correctly handled XSS attempt")
                else:
                    # Check if the payload is reflected in response
                    if payload in response.text:
                        await self.log_test("Security", f"XSS Protection", False, 
                                          f"XSS payload reflected in response")
                        await self.log_security_issue("HIGH", "XSS Vulnerability", 
                                                     f"XSS payload reflected: {payload}")
                    else:
                        await self.log_test("Security", f"XSS Protection", True, 
                                          f"XSS payload not reflected")
            except Exception as e:
                await self.log_test("Security", f"XSS Test", False, f"Exception: {str(e)}")
    
    async def test_rate_limiting(self):
        """Test rate limiting implementation"""
        print("\n⏱️ Testing Rate Limiting...")
        
        # Test rapid requests to login endpoint
        rapid_requests = []
        for i in range(10):
            try:
                start_time = time.time()
                response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                    "email": f"ratetest{i}@test.com",
                    "password": "testpass"
                })
                response_time = (time.time() - start_time) * 1000
                rapid_requests.append({
                    "status": response.status_code,
                    "time": response_time
                })
            except Exception as e:
                rapid_requests.append({"error": str(e)})
        
        # Check if any requests were rate limited (429 status)
        rate_limited = any(req.get("status") == 429 for req in rapid_requests)
        
        if rate_limited:
            await self.log_test("Security", "Rate Limiting", True, 
                              "Rate limiting is implemented")
        else:
            await self.log_test("Security", "Rate Limiting", False, 
                              "No rate limiting detected - potential DoS vulnerability")
            await self.log_security_issue("MEDIUM", "Rate Limiting", 
                                         "No rate limiting detected on login endpoint")
    
    # ==================== 3. DATA INTEGRITY & DATABASE ====================
    
    async def test_data_consistency(self):
        """Test data consistency"""
        print("\n🗄️ Testing Data Integrity...")
        
        # Test user data consistency by checking registration validation
        test_cases = [
            {
                "name": "Empty first_name",
                "data": {"first_name": "", "last_name": "احمدی", "email": "test1@test.com", "phone": "09123456789", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Short first_name",
                "data": {"first_name": "ا", "last_name": "احمدی", "email": "test2@test.com", "phone": "09123456789", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Invalid phone format",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "test3@test.com", "phone": "123456789", "password": "testpass123"},
                "should_fail": True
            },
            {
                "name": "Short password",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "test4@test.com", "phone": "09123456789", "password": "123"},
                "should_fail": True
            },
            {
                "name": "Valid data",
                "data": {"first_name": "علی", "last_name": "احمدی", "email": "test5@test.com", "phone": "09123456789", "password": "testpass123"},
                "should_fail": False
            }
        ]
        
        for test_case in test_cases:
            try:
                response = await self.client.post(f"{BACKEND_URL}/auth/register", json=test_case["data"])
                
                if test_case["should_fail"]:
                    if response.status_code == 422:
                        await self.log_test("Data Integrity", f"Validation: {test_case['name']}", True, 
                                          "Correctly rejected invalid data")
                    else:
                        await self.log_test("Data Integrity", f"Validation: {test_case['name']}", False, 
                                          f"Should have rejected invalid data: {response.status_code}")
                else:
                    if response.status_code in [200, 400]:  # 400 for OTP requirement is OK
                        await self.log_test("Data Integrity", f"Validation: {test_case['name']}", True, 
                                          "Correctly accepted valid data")
                    else:
                        await self.log_test("Data Integrity", f"Validation: {test_case['name']}", False, 
                                          f"Should have accepted valid data: {response.status_code}")
            except Exception as e:
                await self.log_test("Data Integrity", f"Validation: {test_case['name']}", False, f"Exception: {str(e)}")
    
    # ==================== 4. INTEGRATION HEALTH ====================
    
    async def test_external_integrations(self):
        """Test external service integrations"""
        print("\n🔗 Testing External Integrations...")
        
        # Test CoinGecko integration through crypto prices
        try:
            response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.integration_status["coingecko"] = "working"
                    await self.log_test("Integration", "CoinGecko API", True, 
                                      "CoinGecko integration working")
                else:
                    self.integration_status["coingecko"] = "degraded"
                    await self.log_test("Integration", "CoinGecko API", False, 
                                      f"CoinGecko integration degraded: {data.get('error')}")
            else:
                self.integration_status["coingecko"] = "failed"
                await self.log_test("Integration", "CoinGecko API", False, 
                                  f"CoinGecko integration failed: {response.status_code}")
        except Exception as e:
            self.integration_status["coingecko"] = "error"
            await self.log_test("Integration", "CoinGecko API", False, f"Exception: {str(e)}")
        
        # Test API.IR services (indirectly through OTP)
        try:
            response = await self.client.post(f"{BACKEND_URL}/otp/send", json={
                "phone": "09123456789"
            })
            if response.status_code == 200:
                self.integration_status["api_ir"] = "working"
                await self.log_test("Integration", "API.IR OTP Service", True, 
                                  "API.IR OTP service working")
            else:
                self.integration_status["api_ir"] = "failed"
                await self.log_test("Integration", "API.IR OTP Service", False, 
                                  f"API.IR OTP service failed: {response.status_code}")
        except Exception as e:
            self.integration_status["api_ir"] = "error"
            await self.log_test("Integration", "API.IR OTP Service", False, f"Exception: {str(e)}")
        
        # Test AI services
        try:
            # This will likely fail without proper auth, but we can test the endpoint exists
            response = await self.client.post(f"{BACKEND_URL}/ai/chat", json={
                "message": "test"
            })
            if response.status_code == 403:
                self.integration_status["ai_services"] = "protected"
                await self.log_test("Integration", "AI Services", True, 
                                  "AI services endpoint exists and is protected")
            elif response.status_code == 200:
                self.integration_status["ai_services"] = "working"
                await self.log_test("Integration", "AI Services", True, 
                                  "AI services working")
            else:
                self.integration_status["ai_services"] = "failed"
                await self.log_test("Integration", "AI Services", False, 
                                  f"AI services failed: {response.status_code}")
        except Exception as e:
            self.integration_status["ai_services"] = "error"
            await self.log_test("Integration", "AI Services", False, f"Exception: {str(e)}")
    
    # ==================== 5. PERFORMANCE ANALYSIS ====================
    
    async def test_api_performance(self):
        """Test API response times under load"""
        print("\n⚡ Testing API Performance...")
        
        endpoints_to_test = [
            ("/crypto/prices", "GET", None),
            ("/crypto/bitcoin", "GET", None),
            ("/auth/login", "POST", {"email": "test@test.com", "password": "test"}),
        ]
        
        for endpoint, method, data in endpoints_to_test:
            response_times = []
            
            # Test each endpoint 5 times
            for i in range(5):
                try:
                    start_time = time.time()
                    if method == "GET":
                        response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                    else:
                        response = await self.client.post(f"{BACKEND_URL}{endpoint}", json=data)
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                except Exception as e:
                    response_times.append(None)
            
            # Calculate performance metrics
            valid_times = [t for t in response_times if t is not None]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                max_time = max(valid_times)
                min_time = min(valid_times)
                
                # Performance thresholds
                if avg_time < 1000:  # Less than 1 second
                    performance_status = "excellent"
                elif avg_time < 3000:  # Less than 3 seconds
                    performance_status = "good"
                elif avg_time < 5000:  # Less than 5 seconds
                    performance_status = "acceptable"
                else:
                    performance_status = "poor"
                
                await self.log_test("Performance", f"{endpoint} Response Time", True, 
                                  f"Avg: {avg_time:.0f}ms, Min: {min_time:.0f}ms, Max: {max_time:.0f}ms ({performance_status})", 
                                  None, avg_time)
            else:
                await self.log_test("Performance", f"{endpoint} Response Time", False, 
                                  "All requests failed")
    
    async def test_concurrent_requests(self):
        """Test concurrent user handling"""
        print("\n🔄 Testing Concurrent Request Handling...")
        
        async def make_request():
            try:
                start_time = time.time()
                response = await self.client.get(f"{BACKEND_URL}/crypto/prices")
                response_time = (time.time() - start_time) * 1000
                return {"success": response.status_code == 200, "time": response_time}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Create 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        successful_requests = sum(1 for r in results if r.get("success"))
        avg_response_time = sum(r.get("time", 0) for r in results if r.get("time")) / len([r for r in results if r.get("time")])
        
        if successful_requests >= 8:  # At least 80% success rate
            await self.log_test("Performance", "Concurrent Request Handling", True, 
                              f"{successful_requests}/10 requests successful, avg time: {avg_response_time:.0f}ms")
        else:
            await self.log_test("Performance", "Concurrent Request Handling", False, 
                              f"Only {successful_requests}/10 requests successful")
    
    # ==================== 6. ERROR HANDLING & LOGGING ====================
    
    async def test_error_handling(self):
        """Test error handling and responses"""
        print("\n🚨 Testing Error Handling...")
        
        # Test 404 errors
        try:
            response = await self.client.get(f"{BACKEND_URL}/nonexistent/endpoint")
            if response.status_code == 404:
                await self.log_test("Error Handling", "404 Not Found", True, 
                                  "Correctly returns 404 for non-existent endpoints")
            else:
                await self.log_test("Error Handling", "404 Not Found", False, 
                                  f"Should return 404 for non-existent endpoints: {response.status_code}")
        except Exception as e:
            await self.log_test("Error Handling", "404 Not Found", False, f"Exception: {str(e)}")
        
        # Test malformed JSON
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", 
                                            content="invalid json", 
                                            headers={"Content-Type": "application/json"})
            if response.status_code == 422:
                await self.log_test("Error Handling", "Malformed JSON", True, 
                                  "Correctly handles malformed JSON")
            else:
                await self.log_test("Error Handling", "Malformed JSON", False, 
                                  f"Should handle malformed JSON properly: {response.status_code}")
        except Exception as e:
            await self.log_test("Error Handling", "Malformed JSON", False, f"Exception: {str(e)}")
        
        # Test Persian error messages
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": "invalid@test.com",
                "password": "wrongpass"
            })
            if response.status_code == 401:
                error_data = response.json()
                error_message = error_data.get("detail", "")
                if any(persian_char in error_message for persian_char in "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"):
                    await self.log_test("Error Handling", "Persian Error Messages", True, 
                                      "Error messages are in Persian")
                else:
                    await self.log_test("Error Handling", "Persian Error Messages", False, 
                                      f"Error messages should be in Persian: {error_message}")
            else:
                await self.log_test("Error Handling", "Persian Error Messages", False, 
                                  f"Unexpected status code: {response.status_code}")
        except Exception as e:
            await self.log_test("Error Handling", "Persian Error Messages", False, f"Exception: {str(e)}")
    
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend System Health Check")
        print("=" * 80)
        
        # 1. API Performance & Reliability
        await self.test_authentication_endpoints()
        await self.test_trading_endpoints()
        await self.test_admin_endpoints()
        await self.test_kyc_endpoints()
        await self.test_crypto_price_apis()
        
        # 2. Security Assessment
        await self.test_jwt_security()
        await self.test_input_validation()
        await self.test_rate_limiting()
        
        # 3. Data Integrity & Database
        await self.test_data_consistency()
        
        # 4. Integration Health
        await self.test_external_integrations()
        
        # 5. Performance Analysis
        await self.test_api_performance()
        await self.test_concurrent_requests()
        
        # 6. Error Handling & Logging
        await self.test_error_handling()
        
        print("\n" + "=" * 80)
        print("🏁 Comprehensive Backend Testing Complete!")
        await self.print_comprehensive_summary()
    
    async def print_comprehensive_summary(self):
        """Print comprehensive test summary with analysis"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Category breakdown
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        print(f"\n📈 CATEGORY BREAKDOWN:")
        for category, stats in categories.items():
            total_cat = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"] / total_cat) * 100 if total_cat > 0 else 0
            print(f"  {category}: {stats['passed']}/{total_cat} ({success_rate:.1f}%)")
        
        # Performance Analysis
        if self.performance_metrics:
            print(f"\n⚡ PERFORMANCE ANALYSIS:")
            avg_response_time = sum(m["response_time_ms"] for m in self.performance_metrics) / len(self.performance_metrics)
            max_response_time = max(m["response_time_ms"] for m in self.performance_metrics)
            min_response_time = min(m["response_time_ms"] for m in self.performance_metrics)
            
            print(f"  Average Response Time: {avg_response_time:.0f}ms")
            print(f"  Fastest Response: {min_response_time:.0f}ms")
            print(f"  Slowest Response: {max_response_time:.0f}ms")
        
        # Security Issues
        if self.security_issues:
            print(f"\n🔒 SECURITY ISSUES FOUND:")
            for issue in self.security_issues:
                print(f"  [{issue['severity']}] {issue['issue']}: {issue['details']}")
        else:
            print(f"\n🔒 SECURITY: No critical security issues detected")
        
        # Integration Status
        print(f"\n🔗 INTEGRATION STATUS:")
        for service, status in self.integration_status.items():
            status_emoji = {"working": "✅", "degraded": "⚠️", "failed": "❌", "error": "🔥", "protected": "🔒"}
            print(f"  {service}: {status_emoji.get(status, '❓')} {status}")
        
        # Failed Tests Details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  [{result['category']}] {result['test']}: {result['details']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        # Performance recommendations
        if self.performance_metrics:
            slow_endpoints = [m for m in self.performance_metrics if m["response_time_ms"] > 3000]
            if slow_endpoints:
                print(f"  - Optimize slow endpoints: {', '.join(set(m['endpoint'] for m in slow_endpoints))}")
        
        # Security recommendations
        if any(issue["severity"] in ["HIGH", "CRITICAL"] for issue in self.security_issues):
            print(f"  - Address critical security vulnerabilities immediately")
        
        if not any("Rate Limiting" in result["test"] and result["success"] for result in self.test_results):
            print(f"  - Implement rate limiting to prevent DoS attacks")
        
        # Integration recommendations
        failed_integrations = [service for service, status in self.integration_status.items() if status in ["failed", "error"]]
        if failed_integrations:
            print(f"  - Fix failed integrations: {', '.join(failed_integrations)}")
        
        # General recommendations
        if failed_tests > total_tests * 0.1:  # More than 10% failure rate
            print(f"  - High failure rate detected - review and fix failing endpoints")
        
        print(f"\n🎯 PRODUCTION READINESS SCORE: {(passed_tests/total_tests)*100:.0f}%")
        
        if (passed_tests/total_tests) >= 0.95:
            print("🟢 EXCELLENT - System is production ready")
        elif (passed_tests/total_tests) >= 0.85:
            print("🟡 GOOD - Minor issues to address before production")
        elif (passed_tests/total_tests) >= 0.70:
            print("🟠 FAIR - Several issues need attention")
        else:
            print("🔴 POOR - Major issues must be resolved before production")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = ComprehensiveBackendTester()
    try:
        await tester.run_comprehensive_tests()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())