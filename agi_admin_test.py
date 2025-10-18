#!/usr/bin/env python3
"""
AGI Admin Features Testing for Iranian Crypto Exchange
Tests the new AI-powered admin endpoints and enhanced analytics
"""

import asyncio
import httpx
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://cryptotradera.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "email": "admin",
    "password": "istari118"
}

class AGIAdminTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.admin_token = None
        self.test_results = []
        
    async def setup(self):
        """Setup admin authentication"""
        print("🔐 Setting up admin authentication...")
        
        try:
            response = await self.client.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                user_info = data["user"]
                print(f"✅ Admin login successful: {user_info['full_name']} (Admin: {user_info['is_admin']})")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    async def test_fraud_detection_endpoint(self):
        """Test GET /api/admin/ai/fraud-detection"""
        print("\n🔍 Testing AI Fraud Detection Endpoint...")
        
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/admin/ai/fraud-detection",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["high_risk_users", "fraud_patterns", "total_analyzed", "risk_summary", "generated_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ Missing fields in fraud detection response: {missing_fields}")
                    return False
                
                # Check fraud patterns structure
                fraud_patterns = data["fraud_patterns"]
                if "patterns" in fraud_patterns and "overall_risk_score" in fraud_patterns:
                    print(f"✅ Fraud detection analysis successful")
                    print(f"   📊 Total users analyzed: {data['total_analyzed']}")
                    print(f"   ⚠️  High risk users: {data['risk_summary']['high_risk_count']}")
                    print(f"   📈 Overall risk score: {fraud_patterns['overall_risk_score']}%")
                    
                    # Check Persian language support
                    if any("تراکنش" in str(pattern) or "کاربر" in str(pattern) for pattern in fraud_patterns.get("patterns", {}).values()):
                        print(f"   🇮🇷 Persian language support: ✅")
                    else:
                        print(f"   🇮🇷 Persian language support: ❌")
                    
                    return True
                else:
                    print(f"❌ Invalid fraud patterns structure")
                    return False
                    
            else:
                print(f"❌ Fraud detection endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Fraud detection test error: {str(e)}")
            return False
    
    async def test_advanced_analytics_endpoint(self):
        """Test GET /api/admin/ai/advanced-analytics"""
        print("\n📊 Testing AI Advanced Analytics Endpoint...")
        
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/admin/ai/advanced-analytics",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["system_analytics", "user_behavior", "trading_performance", "generated_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ Missing fields in advanced analytics response: {missing_fields}")
                    return False
                
                # Check system analytics
                system_analytics = data["system_analytics"]
                if "performance_trends" in system_analytics and "api_metrics" in system_analytics:
                    print(f"✅ Advanced analytics successful")
                    print(f"   🖥️  System metrics: Available")
                    print(f"   👥 User behavior analysis: Available")
                    print(f"   💹 Trading performance: Available")
                    
                    # Check for comprehensive data structures
                    api_metrics = system_analytics.get("api_metrics", {})
                    if "endpoint_performance" in api_metrics:
                        endpoints = list(api_metrics["endpoint_performance"].keys())
                        print(f"   🔗 API endpoints monitored: {len(endpoints)}")
                    
                    # Check Persian language in user behavior
                    user_behavior = data.get("user_behavior", {})
                    if "insights" in user_behavior:
                        persian_insights = [insight for insight in user_behavior["insights"] if any(persian_char in insight for persian_char in "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")]
                        if persian_insights:
                            print(f"   🇮🇷 Persian insights: ✅ ({len(persian_insights)} insights)")
                        else:
                            print(f"   🇮🇷 Persian insights: ❌")
                    
                    return True
                else:
                    print(f"❌ Invalid system analytics structure")
                    return False
                    
            else:
                print(f"❌ Advanced analytics endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Advanced analytics test error: {str(e)}")
            return False
    
    async def test_ai_assistant_endpoint(self):
        """Test GET /api/admin/ai/assistant"""
        print("\n🤖 Testing AI Assistant Interface Endpoint...")
        
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/admin/ai/assistant",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["recommendations", "recent_alerts", "quick_actions", "assistant_status", "generated_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ Missing fields in AI assistant response: {missing_fields}")
                    return False
                
                print(f"✅ AI Assistant interface successful")
                print(f"   💡 Recommendations: {len(data['recommendations'])}")
                print(f"   🚨 Recent alerts: {len(data['recent_alerts'])}")
                print(f"   ⚡ Quick actions: {len(data['quick_actions'])}")
                print(f"   🟢 Assistant status: {data['assistant_status']}")
                
                # Check Persian language in recommendations
                recommendations = data.get("recommendations", [])
                persian_recommendations = [rec for rec in recommendations if any(persian_char in str(rec) for persian_char in "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")]
                if persian_recommendations:
                    print(f"   🇮🇷 Persian recommendations: ✅ ({len(persian_recommendations)}/{len(recommendations)})")
                else:
                    print(f"   🇮🇷 Persian recommendations: ❌")
                
                # Check quick actions structure
                quick_actions = data.get("quick_actions", [])
                if quick_actions and all("title" in action and "description" in action for action in quick_actions):
                    print(f"   ⚡ Quick actions structure: ✅")
                else:
                    print(f"   ⚡ Quick actions structure: ❌")
                
                return True
                
            else:
                print(f"❌ AI assistant endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ AI assistant test error: {str(e)}")
            return False
    
    async def test_execute_action_endpoint(self):
        """Test POST /api/admin/ai/execute-action"""
        print("\n⚡ Testing AI Execute Action Endpoint...")
        
        # Test different action types
        test_actions = [
            {
                "action_type": "clear_cache",
                "parameters": {}
            },
            {
                "action_type": "sync_prices", 
                "parameters": {}
            },
            {
                "action_type": "backup_db",
                "parameters": {}
            }
        ]
        
        successful_actions = 0
        
        for action in test_actions:
            try:
                response = await self.client.post(
                    f"{BACKEND_URL}/admin/ai/execute-action",
                    headers=self.get_auth_headers(),
                    json=action
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and "result" in data:
                        print(f"   ✅ Action '{action['action_type']}': {data['result'].get('message', 'Success')}")
                        successful_actions += 1
                    else:
                        print(f"   ❌ Action '{action['action_type']}': Invalid response structure")
                else:
                    print(f"   ❌ Action '{action['action_type']}': {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Action '{action['action_type']}' error: {str(e)}")
        
        if successful_actions == len(test_actions):
            print(f"✅ Execute action endpoint: All {successful_actions} actions successful")
            return True
        else:
            print(f"⚠️  Execute action endpoint: {successful_actions}/{len(test_actions)} actions successful")
            return successful_actions > 0
    
    async def test_predictive_analytics_endpoint(self):
        """Test GET /api/admin/analytics/predictive (enhanced)"""
        print("\n🔮 Testing Enhanced Predictive Analytics Endpoint...")
        
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/admin/analytics/predictive",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["churn_prediction", "volume_forecast", "revenue_analysis", "generated_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"❌ Missing fields in predictive analytics response: {missing_fields}")
                    return False
                
                print(f"✅ Predictive analytics successful")
                
                # Check churn prediction
                churn_data = data.get("churn_prediction", {})
                if "high_risk_count" in churn_data and "recommendations" in churn_data:
                    print(f"   📉 Churn prediction: {churn_data['high_risk_count']} high-risk users")
                
                # Check volume forecast
                volume_data = data.get("volume_forecast", {})
                if "forecasts" in volume_data and "trend" in volume_data:
                    forecasts = volume_data["forecasts"]
                    print(f"   📈 Volume forecast: {len(forecasts)} days, trend: {volume_data['trend']}")
                
                # Check revenue analysis
                revenue_data = data.get("revenue_analysis", {})
                if "growth_rate" in revenue_data and "projections" in revenue_data:
                    print(f"   💰 Revenue analysis: {revenue_data['growth_rate']}% growth rate")
                
                # Check Persian language support
                persian_found = False
                for section in [churn_data, volume_data, revenue_data]:
                    recommendations = section.get("recommendations", [])
                    if any(any(persian_char in str(rec) for persian_char in "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی") for rec in recommendations):
                        persian_found = True
                        break
                
                if persian_found:
                    print(f"   🇮🇷 Persian language support: ✅")
                else:
                    print(f"   🇮🇷 Persian language support: ❌")
                
                return True
                
            else:
                print(f"❌ Predictive analytics endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Predictive analytics test error: {str(e)}")
            return False
    
    async def test_data_quality_and_realism(self):
        """Test the quality and realism of AI-generated mock data"""
        print("\n🎯 Testing AI Data Quality and Realism...")
        
        try:
            # Test fraud detection data quality
            fraud_response = await self.client.get(
                f"{BACKEND_URL}/admin/ai/fraud-detection",
                headers=self.get_auth_headers()
            )
            
            quality_score = 0
            total_checks = 0
            
            if fraud_response.status_code == 200:
                fraud_data = fraud_response.json()
                
                # Check fraud patterns realism
                patterns = fraud_data.get("fraud_patterns", {}).get("patterns", {})
                if patterns:
                    total_checks += 1
                    # Check if patterns have realistic names and descriptions
                    realistic_patterns = ["velocity_fraud", "amount_anomaly", "geographic_anomaly", "behavioral_shift"]
                    if any(pattern in patterns for pattern in realistic_patterns):
                        quality_score += 1
                        print(f"   ✅ Fraud patterns: Realistic pattern types detected")
                    else:
                        print(f"   ❌ Fraud patterns: Unrealistic or missing pattern types")
                
                # Check risk scoring
                overall_risk = fraud_data.get("fraud_patterns", {}).get("overall_risk_score", 0)
                if 0 <= overall_risk <= 100:
                    total_checks += 1
                    quality_score += 1
                    print(f"   ✅ Risk scoring: Valid range (0-100): {overall_risk}%")
                else:
                    print(f"   ❌ Risk scoring: Invalid range: {overall_risk}%")
            
            # Test advanced analytics data quality
            analytics_response = await self.client.get(
                f"{BACKEND_URL}/admin/ai/advanced-analytics",
                headers=self.get_auth_headers()
            )
            
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                
                # Check performance trends
                system_analytics = analytics_data.get("system_analytics", {})
                performance_trends = system_analytics.get("performance_trends", {})
                
                if performance_trends:
                    total_checks += 1
                    # Check if trends have 24-hour data points
                    cpu_trend = performance_trends.get("cpu_trend", [])
                    if len(cpu_trend) == 24 and all(0 <= val <= 100 for val in cpu_trend):
                        quality_score += 1
                        print(f"   ✅ Performance trends: Realistic 24-hour CPU data")
                    else:
                        print(f"   ❌ Performance trends: Invalid CPU trend data")
                
                # Check API endpoint performance
                api_metrics = system_analytics.get("api_metrics", {})
                endpoint_performance = api_metrics.get("endpoint_performance", {})
                
                if endpoint_performance:
                    total_checks += 1
                    # Check if endpoints have realistic response times
                    realistic_endpoints = ["/api/auth/login", "/api/trading/orders", "/api/kyc/status"]
                    found_endpoints = [ep for ep in endpoint_performance.keys() if any(realistic in ep for realistic in realistic_endpoints)]
                    
                    if found_endpoints:
                        quality_score += 1
                        print(f"   ✅ API metrics: Realistic endpoint monitoring ({len(found_endpoints)} endpoints)")
                    else:
                        print(f"   ❌ API metrics: No realistic endpoints found")
            
            # Test user behavior patterns
            user_behavior = analytics_data.get("user_behavior", {})
            patterns = user_behavior.get("patterns", {})
            
            if patterns:
                total_checks += 1
                # Check trading patterns
                trading_patterns = patterns.get("trading_patterns", {})
                if "peak_trading_hours" in trading_patterns and "user_segments" in trading_patterns:
                    quality_score += 1
                    print(f"   ✅ User behavior: Realistic trading patterns and segments")
                else:
                    print(f"   ❌ User behavior: Missing or unrealistic trading patterns")
            
            # Calculate overall quality score
            if total_checks > 0:
                quality_percentage = (quality_score / total_checks) * 100
                print(f"\n📊 Data Quality Score: {quality_score}/{total_checks} ({quality_percentage:.1f}%)")
                
                if quality_percentage >= 80:
                    print(f"✅ AI data quality: Excellent")
                    return True
                elif quality_percentage >= 60:
                    print(f"⚠️  AI data quality: Good")
                    return True
                else:
                    print(f"❌ AI data quality: Needs improvement")
                    return False
            else:
                print(f"❌ Could not assess data quality - no data available")
                return False
                
        except Exception as e:
            print(f"❌ Data quality test error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all AGI admin feature tests"""
        print("🚀 Starting AGI Admin Features Testing for Iranian Crypto Exchange")
        print("=" * 70)
        
        # Setup authentication
        if not await self.setup():
            print("❌ Failed to setup admin authentication. Exiting.")
            return False
        
        # Run all tests
        tests = [
            ("Fraud Detection", self.test_fraud_detection_endpoint),
            ("Advanced Analytics", self.test_advanced_analytics_endpoint),
            ("AI Assistant", self.test_ai_assistant_endpoint),
            ("Execute Action", self.test_execute_action_endpoint),
            ("Predictive Analytics", self.test_predictive_analytics_endpoint),
            ("Data Quality", self.test_data_quality_and_realism)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
                    self.test_results.append(f"✅ {test_name}: PASSED")
                else:
                    self.test_results.append(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name} test crashed: {str(e)}")
                self.test_results.append(f"💥 {test_name}: CRASHED - {str(e)}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📋 AGI ADMIN FEATURES TEST SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            print(result)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 AGI Admin Features: EXCELLENT - Production Ready!")
            return True
        elif success_rate >= 60:
            print("⚠️  AGI Admin Features: GOOD - Minor issues to address")
            return True
        else:
            print("❌ AGI Admin Features: NEEDS WORK - Major issues found")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = AGIAdminTester()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)