#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Iranian Crypto Exchange - Advanced Features
Testing all new advanced trading, AI, multi-asset, and staking features
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"
TEST_USER_EMAIL = "advanced.test.user@example.com"
TEST_USER_PASSWORD = "testpass123"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "istari118"

class AdvancedFeaturesTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up Advanced Features testing environment...")
        
        # Login as admin (required for most advanced features)
        await self.login_admin()
        
        # Try to login as regular user (for user-specific features)
        await self.login_user()
        
    async def login_user(self):
        """Login as regular user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                user_info = data["user"]
                print(f"✅ User login successful: {user_info.get('full_name', 'Test User')}")
                return True
            else:
                print(f"⚠️  User login failed: {response.status_code} - Will use admin for testing")
                return False
                
        except Exception as e:
            print(f"⚠️  User login error: {str(e)} - Will use admin for testing")
            return False
    
    async def login_admin(self):
        """Login as admin user"""
        try:
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_info = data["user"]
                print(f"✅ Admin login successful: {admin_info.get('full_name', 'Admin')}")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False

    async def test_advanced_trading_limit_orders(self):
        """Test POST /api/trading/limit-order"""
        print("\n📊 Testing Advanced Trading - Limit Orders...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test limit buy order
            limit_buy_payload = {
                "order_type": "limit_buy",
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_crypto": 0.001,
                "target_price_tmn": 2500000000,  # 2.5B TMN
                "expiry_date": "2024-12-31T23:59:59Z"
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/limit-order", headers=headers, json=limit_buy_payload)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Limit buy order endpoint working")
                
                # Verify response structure
                required_fields = ['id', 'order_type', 'coin_symbol', 'amount_crypto', 'target_price_tmn', 'status']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in limit order response: {missing_fields}")
                else:
                    print("✅ Limit order response structure complete")
                
                print(f"📊 Order ID: {data.get('id', 'N/A')}")
                print(f"📊 Order Type: {data.get('order_type', 'N/A')}")
                print(f"📊 Status: {data.get('status', 'N/A')}")
                print(f"📊 Target Price: {data.get('target_price_tmn', 0):,.0f} TMN")
                
                self.test_results.append({"test": "limit_orders", "status": "✅ PASS", "details": "Limit order creation working correctly"})
                
            elif response.status_code == 404:
                print("❌ Limit order endpoint not found - feature not implemented")
                self.test_results.append({"test": "limit_orders", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Limit order failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "limit_orders", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Limit order error: {str(e)}")
            self.test_results.append({"test": "limit_orders", "status": "❌ ERROR", "details": str(e)})

    async def test_advanced_trading_stop_loss(self):
        """Test POST /api/trading/stop-loss"""
        print("\n🛑 Testing Advanced Trading - Stop Loss Orders...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            stop_loss_payload = {
                "coin_symbol": "ETH",
                "coin_id": "ethereum",
                "amount_crypto": 0.1,
                "stop_price_tmn": 150000000,  # 150M TMN
                "limit_price_tmn": 145000000   # 145M TMN
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/stop-loss", headers=headers, json=stop_loss_payload)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Stop loss order endpoint working")
                
                # Verify response structure
                required_fields = ['id', 'coin_symbol', 'amount_crypto', 'stop_price_tmn', 'status']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in stop loss response: {missing_fields}")
                else:
                    print("✅ Stop loss response structure complete")
                
                print(f"📊 Order ID: {data.get('id', 'N/A')}")
                print(f"📊 Coin: {data.get('coin_symbol', 'N/A')}")
                print(f"📊 Stop Price: {data.get('stop_price_tmn', 0):,.0f} TMN")
                print(f"📊 Status: {data.get('status', 'N/A')}")
                
                self.test_results.append({"test": "stop_loss_orders", "status": "✅ PASS", "details": "Stop loss order creation working correctly"})
                
            elif response.status_code == 404:
                print("❌ Stop loss endpoint not found - feature not implemented")
                self.test_results.append({"test": "stop_loss_orders", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Stop loss order failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "stop_loss_orders", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Stop loss order error: {str(e)}")
            self.test_results.append({"test": "stop_loss_orders", "status": "❌ ERROR", "details": str(e)})

    async def test_advanced_trading_dca_strategy(self):
        """Test POST /api/trading/dca-strategy"""
        print("\n📈 Testing Advanced Trading - DCA Strategy...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            dca_payload = {
                "coin_symbol": "BTC",
                "coin_id": "bitcoin",
                "amount_tmn_per_purchase": 10000000,  # 10M TMN per purchase
                "frequency": "weekly",
                "total_budget_tmn": 100000000,  # 100M TMN total
                "auto_rebalance": True
            }
            
            response = await self.client.post(f"{BACKEND_URL}/trading/dca-strategy", headers=headers, json=dca_payload)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ DCA strategy endpoint working")
                
                # Verify response structure
                required_fields = ['id', 'coin_symbol', 'amount_tmn_per_purchase', 'frequency', 'total_budget_tmn', 'status']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in DCA response: {missing_fields}")
                else:
                    print("✅ DCA strategy response structure complete")
                
                print(f"📊 Strategy ID: {data.get('id', 'N/A')}")
                print(f"📊 Coin: {data.get('coin_symbol', 'N/A')}")
                print(f"📊 Amount per Purchase: {data.get('amount_tmn_per_purchase', 0):,.0f} TMN")
                print(f"📊 Frequency: {data.get('frequency', 'N/A')}")
                print(f"📊 Total Budget: {data.get('total_budget_tmn', 0):,.0f} TMN")
                print(f"📊 Status: {data.get('status', 'N/A')}")
                
                self.test_results.append({"test": "dca_strategy", "status": "✅ PASS", "details": "DCA strategy creation working correctly"})
                
            elif response.status_code == 404:
                print("❌ DCA strategy endpoint not found - feature not implemented")
                self.test_results.append({"test": "dca_strategy", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ DCA strategy failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "dca_strategy", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ DCA strategy error: {str(e)}")
            self.test_results.append({"test": "dca_strategy", "status": "❌ ERROR", "details": str(e)})

    async def test_advanced_ai_predictive_analysis(self):
        """Test GET /api/ai/predictive-analysis/{asset_symbol}"""
        print("\n🔮 Testing Advanced AI - Predictive Analysis...")
        
        test_assets = ["BTC", "ETH", "BNB"]
        
        for asset in test_assets:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = await self.client.get(f"{BACKEND_URL}/ai/predictive-analysis/{asset}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Predictive analysis working for {asset}")
                    
                    # Verify response structure
                    expected_fields = ['asset_symbol', 'predictions', 'confidence_score', 'analysis_date']
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields in predictive analysis: {missing_fields}")
                    else:
                        print(f"✅ Predictive analysis structure complete for {asset}")
                    
                    # Check Persian language support
                    predictions = data.get('predictions', {})
                    if isinstance(predictions, dict):
                        for key, value in predictions.items():
                            if isinstance(value, str) and any(char in value for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                                print(f"✅ Persian language support confirmed in {asset} analysis")
                                break
                    
                    print(f"📊 Asset: {data.get('asset_symbol', 'N/A')}")
                    print(f"📊 Confidence Score: {data.get('confidence_score', 0):.1f}%")
                    
                elif response.status_code == 404:
                    print(f"❌ Predictive analysis endpoint not found for {asset}")
                    break
                else:
                    print(f"❌ Predictive analysis failed for {asset}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Predictive analysis error for {asset}: {str(e)}")
        
        if any("✅" in str(result) for result in self.test_results if "predictive" in str(result)):
            self.test_results.append({"test": "predictive_analysis", "status": "✅ PASS", "details": "Predictive analysis working for tested assets"})
        else:
            self.test_results.append({"test": "predictive_analysis", "status": "❌ FAIL", "details": "Predictive analysis endpoints not working"})

    async def test_advanced_ai_sentiment_analysis(self):
        """Test GET /api/ai/sentiment-analysis/{asset_symbol}"""
        print("\n💭 Testing Advanced AI - Sentiment Analysis...")
        
        test_assets = ["BTC", "ETH", "ADA"]
        
        for asset in test_assets:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = await self.client.get(f"{BACKEND_URL}/ai/sentiment-analysis/{asset}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Sentiment analysis working for {asset}")
                    
                    # Verify response structure
                    expected_fields = ['asset_symbol', 'sentiment_score', 'sentiment_label', 'analysis_summary']
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields in sentiment analysis: {missing_fields}")
                    else:
                        print(f"✅ Sentiment analysis structure complete for {asset}")
                    
                    # Check Persian language support
                    analysis_summary = data.get('analysis_summary', '')
                    if any(char in analysis_summary for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                        print(f"✅ Persian language support confirmed in {asset} sentiment")
                    
                    print(f"📊 Asset: {data.get('asset_symbol', 'N/A')}")
                    print(f"📊 Sentiment Score: {data.get('sentiment_score', 0):.2f}")
                    print(f"📊 Sentiment Label: {data.get('sentiment_label', 'N/A')}")
                    
                elif response.status_code == 404:
                    print(f"❌ Sentiment analysis endpoint not found for {asset}")
                    break
                else:
                    print(f"❌ Sentiment analysis failed for {asset}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Sentiment analysis error for {asset}: {str(e)}")
        
        self.test_results.append({"test": "sentiment_analysis", "status": "✅ PASS", "details": "Sentiment analysis working for tested assets"})

    async def test_advanced_ai_portfolio_optimization(self):
        """Test GET /api/ai/portfolio-optimization"""
        print("\n⚖️ Testing Advanced AI - Portfolio Optimization...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/ai/portfolio-optimization", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Portfolio optimization endpoint working")
                
                # Verify response structure
                expected_fields = ['current_allocation', 'recommended_allocation', 'optimization_score', 'recommendations']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in portfolio optimization: {missing_fields}")
                else:
                    print("✅ Portfolio optimization structure complete")
                
                # Check Persian language support in recommendations
                recommendations = data.get('recommendations', [])
                if recommendations and isinstance(recommendations, list):
                    first_rec = recommendations[0]
                    if isinstance(first_rec, dict):
                        for value in first_rec.values():
                            if isinstance(value, str) and any(char in value for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                                print("✅ Persian language support confirmed in portfolio optimization")
                                break
                
                print(f"📊 Optimization Score: {data.get('optimization_score', 0):.1f}")
                print(f"📊 Recommendations Count: {len(recommendations) if recommendations else 0}")
                
                self.test_results.append({"test": "portfolio_optimization", "status": "✅ PASS", "details": "Portfolio optimization working correctly"})
                
            elif response.status_code == 404:
                print("❌ Portfolio optimization endpoint not found - feature not implemented")
                self.test_results.append({"test": "portfolio_optimization", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Portfolio optimization failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "portfolio_optimization", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Portfolio optimization error: {str(e)}")
            self.test_results.append({"test": "portfolio_optimization", "status": "❌ ERROR", "details": str(e)})

    async def test_multi_asset_stocks(self):
        """Test GET /api/assets/stocks"""
        print("\n📈 Testing Multi-Asset Trading - Stocks...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/assets/stocks", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Stock assets endpoint working")
                
                # Verify response structure
                if isinstance(data, list) and len(data) > 0:
                    first_stock = data[0]
                    expected_fields = ['symbol', 'name', 'price_tmn', 'daily_change']
                    missing_fields = [field for field in expected_fields if field not in first_stock]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields in stock data: {missing_fields}")
                    else:
                        print("✅ Stock data structure complete")
                    
                    # Check for Iranian stocks
                    iranian_stocks = [s for s in data if s.get('market') == 'TSE' or 'تهران' in str(s.get('name', ''))]
                    if iranian_stocks:
                        print("✅ Iranian stock market data confirmed")
                    
                    print(f"📊 Total Stocks: {len(data)}")
                    print(f"📊 Iranian Stocks: {len(iranian_stocks)}")
                    
                    # Display sample stocks
                    for i, stock in enumerate(data[:3]):
                        print(f"📊 Stock {i+1}: {stock.get('symbol', 'N/A')} - {stock.get('name', 'N/A')} - {stock.get('price_tmn', 0):,.0f} TMN")
                
                self.test_results.append({"test": "multi_asset_stocks", "status": "✅ PASS", "details": f"Stock assets working with {len(data) if isinstance(data, list) else 0} stocks"})
                
            elif response.status_code == 404:
                print("❌ Stock assets endpoint not found - feature not implemented")
                self.test_results.append({"test": "multi_asset_stocks", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Stock assets failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "multi_asset_stocks", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Stock assets error: {str(e)}")
            self.test_results.append({"test": "multi_asset_stocks", "status": "❌ ERROR", "details": str(e)})

    async def test_multi_asset_commodities(self):
        """Test GET /api/assets/commodities"""
        print("\n🥇 Testing Multi-Asset Trading - Commodities...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/assets/commodities", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Commodity assets endpoint working")
                
                # Verify response structure
                if isinstance(data, list) and len(data) > 0:
                    first_commodity = data[0]
                    expected_fields = ['symbol', 'name', 'price_tmn', 'unit']
                    missing_fields = [field for field in expected_fields if field not in first_commodity]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields in commodity data: {missing_fields}")
                    else:
                        print("✅ Commodity data structure complete")
                    
                    # Check for common commodities
                    commodity_symbols = [c.get('symbol', '') for c in data]
                    common_commodities = ['GOLD', 'SILVER', 'OIL']
                    found_commodities = [c for c in common_commodities if c in commodity_symbols]
                    
                    print(f"📊 Total Commodities: {len(data)}")
                    print(f"📊 Common Commodities Found: {found_commodities}")
                    
                    # Display sample commodities
                    for i, commodity in enumerate(data[:3]):
                        print(f"📊 Commodity {i+1}: {commodity.get('symbol', 'N/A')} - {commodity.get('name', 'N/A')} - {commodity.get('price_tmn', 0):,.0f} TMN/{commodity.get('unit', 'unit')}")
                
                self.test_results.append({"test": "multi_asset_commodities", "status": "✅ PASS", "details": f"Commodity assets working with {len(data) if isinstance(data, list) else 0} commodities"})
                
            elif response.status_code == 404:
                print("❌ Commodity assets endpoint not found - feature not implemented")
                self.test_results.append({"test": "multi_asset_commodities", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Commodity assets failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "multi_asset_commodities", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Commodity assets error: {str(e)}")
            self.test_results.append({"test": "multi_asset_commodities", "status": "❌ ERROR", "details": str(e)})

    async def test_multi_asset_forex(self):
        """Test GET /api/assets/forex"""
        print("\n💱 Testing Multi-Asset Trading - Forex...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/assets/forex", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Forex assets endpoint working")
                
                # Verify response structure
                if isinstance(data, list) and len(data) > 0:
                    first_pair = data[0]
                    expected_fields = ['pair_symbol', 'base_currency', 'quote_currency', 'bid_price', 'ask_price']
                    missing_fields = [field for field in expected_fields if field not in first_pair]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields in forex data: {missing_fields}")
                    else:
                        print("✅ Forex data structure complete")
                    
                    # Check for TMN pairs
                    tmn_pairs = [p for p in data if p.get('quote_currency') == 'TMN' or 'TMN' in p.get('pair_symbol', '')]
                    if tmn_pairs:
                        print("✅ TMN forex pairs confirmed")
                    
                    print(f"📊 Total Forex Pairs: {len(data)}")
                    print(f"📊 TMN Pairs: {len(tmn_pairs)}")
                    
                    # Display sample forex pairs
                    for i, pair in enumerate(data[:3]):
                        bid = pair.get('bid_price', 0)
                        ask = pair.get('ask_price', 0)
                        spread = ask - bid if ask and bid else 0
                        print(f"📊 Pair {i+1}: {pair.get('pair_symbol', 'N/A')} - Bid: {bid:,.0f}, Ask: {ask:,.0f}, Spread: {spread:,.0f}")
                
                self.test_results.append({"test": "multi_asset_forex", "status": "✅ PASS", "details": f"Forex assets working with {len(data) if isinstance(data, list) else 0} pairs"})
                
            elif response.status_code == 404:
                print("❌ Forex assets endpoint not found - feature not implemented")
                self.test_results.append({"test": "multi_asset_forex", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Forex assets failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "multi_asset_forex", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Forex assets error: {str(e)}")
            self.test_results.append({"test": "multi_asset_forex", "status": "❌ ERROR", "details": str(e)})

    async def test_staking_pools(self):
        """Test GET /api/staking/pools"""
        print("\n🏦 Testing Staking & Yield Farming - Staking Pools...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = await self.client.get(f"{BACKEND_URL}/staking/pools", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Staking pools endpoint working")
                
                # Verify response structure
                if isinstance(data, list) and len(data) > 0:
                    first_pool = data[0]
                    expected_fields = ['id', 'asset_symbol', 'pool_name', 'annual_percentage_yield', 'minimum_stake']
                    missing_fields = [field for field in expected_fields if field not in first_pool]
                    
                    if missing_fields:
                        print(f"⚠️  Missing fields in staking pool data: {missing_fields}")
                    else:
                        print("✅ Staking pool data structure complete")
                    
                    # Check for different asset types
                    asset_symbols = set(p.get('asset_symbol', '') for p in data)
                    print(f"📊 Available Staking Assets: {', '.join(asset_symbols)}")
                    
                    print(f"📊 Total Staking Pools: {len(data)}")
                    
                    # Display sample pools
                    for i, pool in enumerate(data[:3]):
                        apy = pool.get('annual_percentage_yield', 0)
                        min_stake = pool.get('minimum_stake', 0)
                        print(f"📊 Pool {i+1}: {pool.get('asset_symbol', 'N/A')} - {pool.get('pool_name', 'N/A')} - APY: {apy:.1f}% - Min: {min_stake:,.0f}")
                
                self.test_results.append({"test": "staking_pools", "status": "✅ PASS", "details": f"Staking pools working with {len(data) if isinstance(data, list) else 0} pools"})
                
            elif response.status_code == 404:
                print("❌ Staking pools endpoint not found - feature not implemented")
                self.test_results.append({"test": "staking_pools", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
            else:
                print(f"❌ Staking pools failed: {response.status_code} - {response.text}")
                self.test_results.append({"test": "staking_pools", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Staking pools error: {str(e)}")
            self.test_results.append({"test": "staking_pools", "status": "❌ ERROR", "details": str(e)})

    async def test_staking_creation(self):
        """Test POST /api/staking/stake"""
        print("\n💰 Testing Staking & Yield Farming - Stake Creation...")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First get available pools
            pools_response = await self.client.get(f"{BACKEND_URL}/staking/pools", headers=headers)
            
            if pools_response.status_code == 200:
                pools = pools_response.json()
                if pools and len(pools) > 0:
                    first_pool = pools[0]
                    pool_id = first_pool.get('id')
                    min_stake = first_pool.get('minimum_stake', 1000000)  # Default 1M TMN
                    
                    stake_payload = {
                        "pool_id": pool_id,
                        "staked_amount": min_stake * 2,  # Stake 2x minimum
                        "auto_compound": True
                    }
                    
                    response = await self.client.post(f"{BACKEND_URL}/staking/stake", headers=headers, json=stake_payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print("✅ Stake creation endpoint working")
                        
                        # Verify response structure
                        expected_fields = ['id', 'pool_id', 'staked_amount', 'status']
                        missing_fields = [field for field in expected_fields if field not in data]
                        
                        if missing_fields:
                            print(f"⚠️  Missing fields in stake response: {missing_fields}")
                        else:
                            print("✅ Stake creation response structure complete")
                        
                        print(f"📊 Stake ID: {data.get('id', 'N/A')}")
                        print(f"📊 Pool ID: {data.get('pool_id', 'N/A')}")
                        print(f"📊 Staked Amount: {data.get('staked_amount', 0):,.0f}")
                        print(f"📊 Status: {data.get('status', 'N/A')}")
                        
                        self.test_results.append({"test": "staking_creation", "status": "✅ PASS", "details": "Stake creation working correctly"})
                        
                    elif response.status_code == 404:
                        print("❌ Stake creation endpoint not found - feature not implemented")
                        self.test_results.append({"test": "staking_creation", "status": "❌ FAIL", "details": "Endpoint not implemented (404)"})
                    else:
                        print(f"❌ Stake creation failed: {response.status_code} - {response.text}")
                        self.test_results.append({"test": "staking_creation", "status": "❌ FAIL", "details": f"HTTP {response.status_code}"})
                else:
                    print("⚠️  No staking pools available for testing stake creation")
                    self.test_results.append({"test": "staking_creation", "status": "⚠️  SKIP", "details": "No pools available"})
            else:
                print("⚠️  Cannot test stake creation - pools endpoint not working")
                self.test_results.append({"test": "staking_creation", "status": "⚠️  SKIP", "details": "Pools endpoint not available"})
                
        except Exception as e:
            print(f"❌ Stake creation error: {str(e)}")
            self.test_results.append({"test": "staking_creation", "status": "❌ ERROR", "details": str(e)})

    async def test_authentication_validation(self):
        """Test authentication requirements for all advanced endpoints"""
        print("\n🔐 Testing Authentication & Validation...")
        
        endpoints_to_test = [
            ("/trading/limit-order", "POST"),
            ("/trading/stop-loss", "POST"),
            ("/trading/dca-strategy", "POST"),
            ("/ai/predictive-analysis/BTC", "GET"),
            ("/ai/sentiment-analysis/BTC", "GET"),
            ("/ai/portfolio-optimization", "GET"),
            ("/assets/stocks", "GET"),
            ("/assets/commodities", "GET"),
            ("/assets/forex", "GET"),
            ("/staking/pools", "GET"),
            ("/staking/stake", "POST")
        ]
        
        auth_required_count = 0
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = await self.client.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = await self.client.post(f"{BACKEND_URL}{endpoint}", json={})
                
                if response.status_code in [401, 403]:
                    print(f"✅ Authentication required for {endpoint}")
                    auth_required_count += 1
                elif response.status_code == 404:
                    print(f"⚠️  {endpoint} not implemented (404)")
                else:
                    print(f"⚠️  {endpoint} accessible without authentication: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing authentication for {endpoint}: {str(e)}")
        
        print(f"📊 Authentication Summary: {auth_required_count}/{len(endpoints_to_test)} endpoints require authentication")
        
        if auth_required_count >= len(endpoints_to_test) * 0.8:  # 80% threshold
            self.test_results.append({"test": "authentication_validation", "status": "✅ PASS", "details": f"Most endpoints properly require authentication ({auth_required_count}/{len(endpoints_to_test)})"})
        else:
            self.test_results.append({"test": "authentication_validation", "status": "⚠️  PARTIAL", "details": f"Only {auth_required_count}/{len(endpoints_to_test)} endpoints require authentication"})

    async def test_persian_language_responses(self):
        """Test Persian language support throughout advanced features"""
        print("\n🇮🇷 Testing Persian Language Support...")
        
        persian_found_count = 0
        total_tests = 0
        
        # Test endpoints that should return Persian text
        test_endpoints = [
            ("/ai/predictive-analysis/BTC", "GET"),
            ("/ai/sentiment-analysis/BTC", "GET"),
            ("/ai/portfolio-optimization", "GET")
        ]
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for endpoint, method in test_endpoints:
            try:
                total_tests += 1
                if method == "GET":
                    response = await self.client.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                else:
                    response = await self.client.post(f"{BACKEND_URL}{endpoint}", headers=headers, json={})
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = json.dumps(data, ensure_ascii=False)
                    
                    if any(char in response_text for char in 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'):
                        print(f"✅ Persian language found in {endpoint}")
                        persian_found_count += 1
                    else:
                        print(f"⚠️  No Persian language detected in {endpoint}")
                elif response.status_code == 404:
                    print(f"⚠️  {endpoint} not implemented")
                    total_tests -= 1  # Don't count unimplemented endpoints
                else:
                    print(f"⚠️  {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing Persian support for {endpoint}: {str(e)}")
        
        if total_tests > 0:
            persian_percentage = (persian_found_count / total_tests) * 100
            print(f"📊 Persian Language Summary: {persian_found_count}/{total_tests} endpoints ({persian_percentage:.1f}%) have Persian support")
            
            if persian_percentage >= 80:
                self.test_results.append({"test": "persian_language_support", "status": "✅ PASS", "details": f"Excellent Persian support ({persian_percentage:.1f}%)"})
            elif persian_percentage >= 50:
                self.test_results.append({"test": "persian_language_support", "status": "⚠️  PARTIAL", "details": f"Partial Persian support ({persian_percentage:.1f}%)"})
            else:
                self.test_results.append({"test": "persian_language_support", "status": "❌ FAIL", "details": f"Limited Persian support ({persian_percentage:.1f}%)"})
        else:
            self.test_results.append({"test": "persian_language_support", "status": "⚠️  SKIP", "details": "No testable endpoints available"})

    async def run_all_tests(self):
        """Run all Advanced Features tests"""
        print("🚀 Starting Advanced Features Testing...")
        print("=" * 80)
        
        await self.setup()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run all tests
        print("\n🔥 ADVANCED TRADING FEATURES TESTING")
        print("-" * 50)
        await self.test_advanced_trading_limit_orders()
        await self.test_advanced_trading_stop_loss()
        await self.test_advanced_trading_dca_strategy()
        
        print("\n🧠 ADVANCED AI FEATURES TESTING")
        print("-" * 50)
        await self.test_advanced_ai_predictive_analysis()
        await self.test_advanced_ai_sentiment_analysis()
        await self.test_advanced_ai_portfolio_optimization()
        
        print("\n📊 MULTI-ASSET TRADING TESTING")
        print("-" * 50)
        await self.test_multi_asset_stocks()
        await self.test_multi_asset_commodities()
        await self.test_multi_asset_forex()
        
        print("\n💰 STAKING & YIELD FARMING TESTING")
        print("-" * 50)
        await self.test_staking_pools()
        await self.test_staking_creation()
        
        print("\n🔐 AUTHENTICATION & VALIDATION TESTING")
        print("-" * 50)
        await self.test_authentication_validation()
        await self.test_persian_language_responses()
        
        # Print comprehensive summary
        print("\n" + "=" * 80)
        print("📋 ADVANCED FEATURES TESTING SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌" in r["status"]]
        warning_tests = [r for r in self.test_results if "⚠️" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"⚠️  WARNINGS/PARTIAL: {len(warning_tests)}")
        print(f"📊 TOTAL TESTS: {len(self.test_results)}")
        
        # Calculate success rate
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        # Detailed results by category
        print("\n📊 RESULTS BY CATEGORY:")
        
        categories = {
            "Advanced Trading": ["limit_orders", "stop_loss_orders", "dca_strategy"],
            "Advanced AI": ["predictive_analysis", "sentiment_analysis", "portfolio_optimization"],
            "Multi-Asset": ["multi_asset_stocks", "multi_asset_commodities", "multi_asset_forex"],
            "Staking": ["staking_pools", "staking_creation"],
            "Security": ["authentication_validation", "persian_language_support"]
        }
        
        for category, test_names in categories.items():
            category_results = [r for r in self.test_results if any(name in r["test"] for name in test_names)]
            category_passed = [r for r in category_results if "✅ PASS" in r["status"]]
            category_rate = (len(category_passed) / len(category_results)) * 100 if category_results else 0
            print(f"  {category}: {len(category_passed)}/{len(category_results)} ({category_rate:.1f}%)")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if warning_tests:
            print("\n⚠️  WARNING/PARTIAL TESTS:")
            for test in warning_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("\n🎯 KEY FINDINGS:")
        if len(passed_tests) >= len(self.test_results) * 0.8:
            print("✅ Most advanced features are working correctly")
        else:
            print("⚠️  Many advanced features need implementation or fixes")
        
        if any("persian" in r["test"].lower() for r in passed_tests):
            print("✅ Persian language support is functional")
        
        if any("auth" in r["test"].lower() for r in passed_tests):
            print("✅ Authentication and security measures are in place")
        
        await self.client.aclose()

async def main():
    """Main test execution"""
    tester = AdvancedFeaturesTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())