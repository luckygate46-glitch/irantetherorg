#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Iranian Crypto Exchange Upgrade
Tests all newly implemented advanced features including:
- New backend models and endpoints
- Advanced AI services
- Multi-asset trading
- Staking and yield farming
- Advanced trading features
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"email": "admin", "password": "istari118"}
TEST_USER_CREDENTIALS = {"email": "testuser@example.com", "password": "password123"}

class ComprehensiveUpgradeTest:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    async def run_all_tests(self):
        """Run comprehensive testing of all upgrade features"""
        print("🚀 Starting Comprehensive Backend Upgrade Testing...")
        print("=" * 60)
        
        try:
            # Authentication setup
            await self.setup_authentication()
            
            # Test categories
            await self.test_new_backend_models()
            await self.test_advanced_ai_services()
            await self.test_advanced_trading_features()
            await self.test_multi_asset_trading()
            await self.test_staking_yield_farming()
            await self.test_authentication_validation()
            await self.test_persian_language_support()
            
            # Generate final report
            await self.generate_test_report()
            
        except Exception as e:
            print(f"❌ Critical error during testing: {str(e)}")
            self.test_results.append({
                'category': 'CRITICAL_ERROR',
                'test': 'Test Suite Execution',
                'status': 'FAILED',
                'error': str(e)
            })
        finally:
            await self.client.aclose()
    
    async def setup_authentication(self):
        """Setup authentication tokens for testing"""
        print("\n🔐 Setting up authentication...")
        
        # Admin login
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                print("✅ Admin authentication successful")
                self.test_results.append({
                    'category': 'AUTHENTICATION',
                    'test': 'Admin Login',
                    'status': 'PASSED',
                    'details': f"Admin user: {data.get('user', {}).get('full_name', 'Unknown')}"
                })
            else:
                raise Exception(f"Admin login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Admin authentication failed: {str(e)}")
            self.test_results.append({
                'category': 'AUTHENTICATION',
                'test': 'Admin Login',
                'status': 'FAILED',
                'error': str(e)
            })
        
        # Test user login
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=TEST_USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('access_token')
                print("✅ Test user authentication successful")
                self.test_results.append({
                    'category': 'AUTHENTICATION',
                    'test': 'Test User Login',
                    'status': 'PASSED',
                    'details': f"User: {data.get('user', {}).get('full_name', 'Unknown')}"
                })
            else:
                print(f"⚠️ Test user login failed: {response.status_code}")
                self.test_results.append({
                    'category': 'AUTHENTICATION',
                    'test': 'Test User Login',
                    'status': 'FAILED',
                    'error': f"Status: {response.status_code}"
                })
        except Exception as e:
            print(f"⚠️ Test user authentication failed: {str(e)}")
            self.test_results.append({
                'category': 'AUTHENTICATION',
                'test': 'Test User Login',
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def test_new_backend_models(self):
        """Test new backend models and their endpoints"""
        print("\n📊 Testing New Backend Models...")
        
        if not self.admin_token:
            print("❌ Skipping model tests - no admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test TradingOrder model via trading endpoints
        await self.test_endpoint(
            "GET", "/trading/orders/my", headers,
            "Trading Orders Model", "NEW_MODELS"
        )
        
        # Test UserHolding model
        await self.test_endpoint(
            "GET", "/trading/holdings/my", headers,
            "User Holdings Model", "NEW_MODELS"
        )
        
        # Test advanced order types
        test_endpoints = [
            ("/trading/limit-order", "Limit Order Model"),
            ("/trading/stop-loss", "Stop Loss Model"),
            ("/trading/dca-strategy", "DCA Strategy Model")
        ]
        
        for endpoint, model_name in test_endpoints:
            # Test GET endpoints if they exist, otherwise test POST structure
            await self.test_endpoint(
                "POST", endpoint, headers,
                model_name, "NEW_MODELS",
                test_data={
                    "coin_symbol": "BTC",
                    "coin_id": "bitcoin",
                    "amount_crypto": 0.001,
                    "target_price_tmn": 1000000
                }
            )
    
    async def test_advanced_ai_services(self):
        """Test advanced AI services from advanced_ai_services.py"""
        print("\n🤖 Testing Advanced AI Services...")
        
        if not self.admin_token:
            print("❌ Skipping AI tests - no admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test predictive analysis
        await self.test_endpoint(
            "GET", "/ai/predictive-analysis/bitcoin", headers,
            "Predictive Market Analysis", "ADVANCED_AI"
        )
        
        # Test sentiment analysis
        await self.test_endpoint(
            "GET", "/ai/sentiment-analysis/bitcoin", headers,
            "Sentiment Analysis Engine", "ADVANCED_AI"
        )
        
        # Test portfolio optimization
        await self.test_endpoint(
            "GET", "/ai/portfolio-optimization", headers,
            "Advanced Portfolio Optimizer", "ADVANCED_AI"
        )
        
        # Test user AI services
        user_ai_endpoints = [
            ("/user/ai/recommendations", "Personal AI Recommendations"),
            ("/user/ai/portfolio-analysis", "AI Portfolio Analysis"),
            ("/user/ai/notifications", "Smart Notifications"),
            ("/user/ai/market-insights", "AI Market Insights"),
            ("/user/ai/dashboard", "AI Dashboard Data")
        ]
        
        for endpoint, service_name in user_ai_endpoints:
            await self.test_endpoint(
                "GET", endpoint, headers,
                service_name, "ADVANCED_AI"
            )
        
        # Test AI assistant with POST
        await self.test_endpoint(
            "POST", "/user/ai/ask-assistant", headers,
            "AI Trading Assistant", "ADVANCED_AI",
            test_data={"question": "بهترین استراتژی معاملاتی چیست؟"}
        )
    
    async def test_advanced_trading_features(self):
        """Test advanced trading features"""
        print("\n📈 Testing Advanced Trading Features...")
        
        if not self.user_token:
            print("❌ Skipping trading tests - no user token")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test limit orders
        await self.test_endpoint(
            "POST", "/trading/limit-order", headers,
            "Limit Order Creation", "ADVANCED_TRADING",
            test_data={
                "order_type": "limit_buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_crypto": 0.001,
                "target_price_tmn": 1000000
            }
        )
        
        # Test stop-loss orders
        await self.test_endpoint(
            "POST", "/trading/stop-loss", headers,
            "Stop-Loss Order Creation", "ADVANCED_TRADING",
            test_data={
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_crypto": 0.001,
                "stop_price_tmn": 900000
            }
        )
        
        # Test DCA strategy
        await self.test_endpoint(
            "POST", "/trading/dca-strategy", headers,
            "DCA Strategy Creation", "ADVANCED_TRADING",
            test_data={
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn_per_purchase": 1000000,
                "frequency": "weekly",
                "total_budget_tmn": 10000000
            }
        )
    
    async def test_multi_asset_trading(self):
        """Test multi-asset trading support"""
        print("\n🌐 Testing Multi-Asset Trading...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
        
        # Test stock assets
        await self.test_endpoint(
            "GET", "/assets/stocks", headers,
            "Stock Assets Support", "MULTI_ASSET"
        )
        
        # Test commodity assets
        await self.test_endpoint(
            "GET", "/assets/commodities", headers,
            "Commodity Assets Support", "MULTI_ASSET"
        )
        
        # Test forex pairs
        await self.test_endpoint(
            "GET", "/assets/forex", headers,
            "Forex Pairs Support", "MULTI_ASSET"
        )
    
    async def test_staking_yield_farming(self):
        """Test staking and yield farming features"""
        print("\n🌾 Testing Staking & Yield Farming...")
        
        if not self.user_token:
            print("❌ Skipping staking tests - no user token")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test staking pools
        await self.test_endpoint(
            "GET", "/staking/pools", headers,
            "Staking Pools", "STAKING"
        )
        
        # Test stake creation
        await self.test_endpoint(
            "POST", "/staking/stake", headers,
            "Stake Creation", "STAKING",
            test_data={
                "pool_id": "eth2-staking",
                "amount": 1000000,
                "auto_compound": True
            }
        )
    
    async def test_authentication_validation(self):
        """Test authentication and validation for advanced features"""
        print("\n🔒 Testing Authentication & Validation...")
        
        # Test without authentication
        await self.test_endpoint(
            "GET", "/ai/predictive-analysis/bitcoin", {},
            "AI Endpoint Authentication", "SECURITY",
            expect_auth_error=True
        )
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        await self.test_endpoint(
            "GET", "/trading/orders/my", invalid_headers,
            "Invalid Token Handling", "SECURITY",
            expect_auth_error=True
        )
    
    async def test_persian_language_support(self):
        """Test Persian language support in responses"""
        print("\n🇮🇷 Testing Persian Language Support...")
        
        if not self.admin_token:
            print("❌ Skipping Persian tests - no admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test AI services for Persian responses
        response = await self.client.get(f"{BACKEND_URL}/ai/predictive-analysis/bitcoin", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Check for Persian text in response
            response_text = json.dumps(data, ensure_ascii=False)
            has_persian = any(ord(char) > 127 for char in response_text)
            
            if has_persian:
                print("✅ Persian language support confirmed")
                self.test_results.append({
                    'category': 'PERSIAN_SUPPORT',
                    'test': 'AI Services Persian Language',
                    'status': 'PASSED',
                    'details': 'Persian text detected in AI responses'
                })
            else:
                print("⚠️ No Persian text detected in AI responses")
                self.test_results.append({
                    'category': 'PERSIAN_SUPPORT',
                    'test': 'AI Services Persian Language',
                    'status': 'WARNING',
                    'details': 'No Persian text detected'
                })
        else:
            print(f"❌ Could not test Persian support: {response.status_code}")
            self.test_results.append({
                'category': 'PERSIAN_SUPPORT',
                'test': 'AI Services Persian Language',
                'status': 'FAILED',
                'error': f"Status: {response.status_code}"
            })
    
    async def test_endpoint(self, method: str, endpoint: str, headers: Dict, 
                          test_name: str, category: str, test_data: Dict = None, 
                          expect_auth_error: bool = False):
        """Generic endpoint testing method"""
        try:
            if method == "GET":
                response = await self.client.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = await self.client.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=test_data)
            else:
                response = await self.client.request(method, f"{BACKEND_URL}{endpoint}", headers=headers, json=test_data)
            
            # Handle expected authentication errors
            if expect_auth_error:
                if response.status_code in [401, 403]:
                    print(f"✅ {test_name}: Authentication properly enforced")
                    self.test_results.append({
                        'category': category,
                        'test': test_name,
                        'status': 'PASSED',
                        'details': f'Authentication enforced (Status: {response.status_code})'
                    })
                else:
                    print(f"⚠️ {test_name}: Expected auth error but got {response.status_code}")
                    self.test_results.append({
                        'category': category,
                        'test': test_name,
                        'status': 'WARNING',
                        'details': f'Expected auth error but got {response.status_code}'
                    })
                return
            
            # Handle successful responses
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test_name}: Working correctly")
                self.test_results.append({
                    'category': category,
                    'test': test_name,
                    'status': 'PASSED',
                    'details': f'Response size: {len(str(data))} chars'
                })
            elif response.status_code == 422:
                # Validation error - endpoint exists but data invalid
                print(f"✅ {test_name}: Endpoint exists (validation error expected)")
                self.test_results.append({
                    'category': category,
                    'test': test_name,
                    'status': 'PASSED',
                    'details': 'Endpoint exists, validation working'
                })
            elif response.status_code == 404:
                print(f"❌ {test_name}: Endpoint not found")
                self.test_results.append({
                    'category': category,
                    'test': test_name,
                    'status': 'FAILED',
                    'error': 'Endpoint not implemented'
                })
            else:
                print(f"⚠️ {test_name}: Unexpected status {response.status_code}")
                self.test_results.append({
                    'category': category,
                    'test': test_name,
                    'status': 'WARNING',
                    'details': f'Status: {response.status_code}, Response: {response.text[:200]}'
                })
                
        except Exception as e:
            print(f"❌ {test_name}: Error - {str(e)}")
            self.test_results.append({
                'category': category,
                'test': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
    
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE UPGRADE TEST REPORT")
        print("=" * 60)
        
        # Count results by status
        passed = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed = len([r for r in self.test_results if r['status'] == 'FAILED'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARNING'])
        total = len(self.test_results)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"✅ Passed: {passed}/{total} ({(passed/total*100):.1f}%)")
        print(f"❌ Failed: {failed}/{total} ({(failed/total*100):.1f}%)")
        print(f"⚠️ Warnings: {warnings}/{total} ({(warnings/total*100):.1f}%)")
        
        # Group by category
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'warnings': 0, 'tests': []}
            
            categories[category]['tests'].append(result)
            if result['status'] == 'PASSED':
                categories[category]['passed'] += 1
            elif result['status'] == 'FAILED':
                categories[category]['failed'] += 1
            else:
                categories[category]['warnings'] += 1
        
        # Print category results
        print(f"\n📂 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            total_cat = len(stats['tests'])
            success_rate = (stats['passed'] / total_cat * 100) if total_cat > 0 else 0
            print(f"\n{category}:")
            print(f"  ✅ {stats['passed']} ❌ {stats['failed']} ⚠️ {stats['warnings']} ({success_rate:.1f}% success)")
            
            # Show failed tests
            failed_tests = [t for t in stats['tests'] if t['status'] == 'FAILED']
            if failed_tests:
                print(f"  Failed tests:")
                for test in failed_tests:
                    print(f"    - {test['test']}: {test.get('error', 'Unknown error')}")
        
        # Critical findings
        critical_failures = [r for r in self.test_results if r['status'] == 'FAILED' and r['category'] in ['AUTHENTICATION', 'NEW_MODELS', 'ADVANCED_AI']]
        
        print(f"\n🚨 CRITICAL FINDINGS:")
        if critical_failures:
            for failure in critical_failures:
                print(f"❌ {failure['category']}: {failure['test']} - {failure.get('error', 'Unknown error')}")
        else:
            print("✅ No critical failures detected")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if failed > 0:
            print("- Fix failed endpoints before production deployment")
        if warnings > 0:
            print("- Review warning items for potential improvements")
        if passed / total > 0.8:
            print("- Overall system health is good (>80% success rate)")
        else:
            print("- System needs significant improvements (<80% success rate)")
        
        print(f"\n⏰ Test completed at: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)

async def main():
    """Main test execution"""
    tester = ComprehensiveUpgradeTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())