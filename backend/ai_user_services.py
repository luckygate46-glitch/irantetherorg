"""
AI-Powered User Services for Iranian Crypto Exchange
Includes: Personal AI Assistant, Trading Intelligence, Portfolio Management, Predictive Analytics
"""

import os
import json
import random
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class PersonalTradingAssistant:
    """AI-powered personal trading assistant for users"""
    
    def __init__(self):
        self.trading_strategies = {
            'conservative': {'risk_tolerance': 0.3, 'profit_target': 0.1},
            'moderate': {'risk_tolerance': 0.5, 'profit_target': 0.2},
            'aggressive': {'risk_tolerance': 0.8, 'profit_target': 0.4}
        }
        
    async def get_personalized_recommendations(self, user_id: str, portfolio: Dict, market_data: Dict) -> Dict:
        """Generate personalized trading recommendations"""
        try:
            # Analyze user's trading history and preferences
            user_profile = await self._analyze_user_profile(user_id, portfolio)
            
            # Generate recommendations based on market conditions and user profile
            recommendations = []
            
            # Analyze current holdings
            holdings = portfolio.get('holdings', {})
            for crypto, amount in holdings.items():
                if amount > 0:
                    recommendation = await self._generate_crypto_recommendation(
                        crypto, amount, market_data.get(crypto, {}), user_profile
                    )
                    if recommendation:
                        recommendations.append(recommendation)
            
            # Suggest new investment opportunities
            new_opportunities = await self._find_investment_opportunities(
                market_data, user_profile, holdings
            )
            recommendations.extend(new_opportunities)
            
            return {
                'user_profile': user_profile,
                'recommendations': recommendations[:5],  # Top 5 recommendations
                'market_sentiment': self._get_market_sentiment(market_data),
                'risk_assessment': await self._assess_portfolio_risk(portfolio, market_data),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating personal recommendations: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_user_profile(self, user_id: str, portfolio: Dict) -> Dict:
        """Analyze user trading profile and preferences"""
        # Mock user profile analysis - replace with real ML analysis
        total_value = sum(portfolio.get('holdings', {}).values())
        
        # Determine risk profile based on portfolio diversity and size
        holdings_count = len([h for h in portfolio.get('holdings', {}).values() if h > 0])
        
        if holdings_count <= 2 and total_value < 10000000:  # Less diverse, smaller portfolio
            risk_profile = 'conservative'
        elif holdings_count <= 4 and total_value < 50000000:
            risk_profile = 'moderate'
        else:
            risk_profile = 'aggressive'
        
        return {
            'risk_profile': risk_profile,
            'portfolio_value': total_value,
            'diversification_score': min(100, holdings_count * 20),
            'trading_experience': random.choice(['beginner', 'intermediate', 'advanced']),
            'preferred_timeframe': random.choice(['short_term', 'medium_term', 'long_term']),
            'investment_goals': random.choice(['growth', 'income', 'preservation'])
        }
    
    async def _generate_crypto_recommendation(self, crypto: str, amount: float, crypto_data: Dict, user_profile: Dict) -> Dict:
        """Generate recommendation for a specific crypto holding"""
        current_change = crypto_data.get('usd_24h_change', 0)
        
        # Determine action based on price movement and user risk profile
        risk_tolerance = self.trading_strategies[user_profile['risk_profile']]['risk_tolerance']
        
        if current_change < -5 and abs(current_change) > risk_tolerance * 20:
            action = 'hold_or_buy'
            confidence = random.uniform(70, 85)
            reason = f"قیمت {crypto} کاهش یافته - فرصت خرید مناسب"
        elif current_change > 10 and current_change > risk_tolerance * 15:
            action = 'consider_selling'
            confidence = random.uniform(65, 80)
            reason = f"قیمت {crypto} رشد قابل توجهی داشته - در نظر گیری فروش"
        else:
            action = 'hold'
            confidence = random.uniform(60, 75)
            reason = f"نگهداری {crypto} در شرایط فعلی بازار"
        
        return {
            'crypto': crypto,
            'action': action,
            'confidence': round(confidence, 1),
            'reason': reason,
            'current_amount': amount,
            'suggested_amount': amount * random.uniform(0.8, 1.2),
            'timeframe': user_profile.get('preferred_timeframe', 'medium_term'),
            'risk_level': user_profile['risk_profile']
        }
    
    async def _find_investment_opportunities(self, market_data: Dict, user_profile: Dict, current_holdings: Dict) -> List[Dict]:
        """Find new investment opportunities"""
        opportunities = []
        
        # Filter out cryptos already held
        available_cryptos = [crypto for crypto in market_data.keys() if crypto not in current_holdings]
        
        # Select top opportunities based on market conditions
        for crypto in available_cryptos[:3]:  # Top 3 opportunities
            crypto_data = market_data[crypto]
            change_24h = crypto_data.get('usd_24h_change', 0)
            
            # Look for undervalued opportunities
            if -10 < change_24h < -2:  # Slight dip - potential buying opportunity
                opportunity = {
                    'crypto': crypto,
                    'action': 'new_investment',
                    'confidence': random.uniform(60, 80),
                    'reason': f"ارز {crypto} در تصحیح قیمت - فرصت ورود مناسب",
                    'suggested_allocation': random.uniform(5, 15),  # Percentage of portfolio
                    'timeframe': 'medium_term',
                    'risk_level': user_profile['risk_profile']
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    def _get_market_sentiment(self, market_data: Dict) -> str:
        """Determine overall market sentiment"""
        changes = [data.get('usd_24h_change', 0) for data in market_data.values()]
        if not changes:
            return 'neutral'
        
        avg_change = sum(changes) / len(changes)
        if avg_change > 3:
            return 'bullish'
        elif avg_change < -3:
            return 'bearish'
        else:
            return 'neutral'
    
    async def _assess_portfolio_risk(self, portfolio: Dict, market_data: Dict) -> Dict:
        """Assess portfolio risk levels"""
        holdings = portfolio.get('holdings', {})
        
        if not holdings:
            return {'level': 'low', 'score': 0, 'factors': []}
        
        # Calculate concentration risk
        total_value = sum(holdings.values())
        concentrations = [value / total_value for value in holdings.values() if value > 0]
        max_concentration = max(concentrations) if concentrations else 0
        
        # Calculate volatility risk
        volatilities = []
        for crypto, amount in holdings.items():
            if amount > 0 and crypto in market_data:
                change = abs(market_data[crypto].get('usd_24h_change', 0))
                volatilities.append(change)
        
        avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0
        
        # Determine overall risk
        risk_factors = []
        risk_score = 0
        
        if max_concentration > 0.6:
            risk_factors.append("تمرکز بالا روی یک دارایی")
            risk_score += 30
        
        if avg_volatility > 10:
            risk_factors.append("نوسانات بالای پرتفوی")
            risk_score += 25
        
        if len(holdings) < 3:
            risk_factors.append("تنوع کم در پرتفوی")
            risk_score += 20
        
        if risk_score > 50:
            level = 'high'
        elif risk_score > 25:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': risk_score,
            'factors': risk_factors,
            'concentration_risk': max_concentration * 100,
            'volatility_risk': avg_volatility
        }


class IntelligentPortfolioManager:
    """AI-powered portfolio management and optimization"""
    
    def __init__(self):
        self.rebalancing_threshold = 0.1  # 10% deviation triggers rebalancing
        
    async def analyze_portfolio_performance(self, user_id: str, portfolio: Dict, historical_data: List[Dict]) -> Dict:
        """Comprehensive portfolio performance analysis"""
        try:
            # Calculate portfolio metrics
            current_value = sum(portfolio.get('holdings', {}).values())
            
            # Calculate historical performance
            performance_metrics = await self._calculate_performance_metrics(historical_data, current_value)
            
            # Asset allocation analysis
            allocation_analysis = await self._analyze_asset_allocation(portfolio)
            
            # Portfolio optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                portfolio, performance_metrics, allocation_analysis
            )
            
            # Risk-adjusted returns
            risk_metrics = await self._calculate_risk_metrics(historical_data)
            
            return {
                'current_value': current_value,
                'performance_metrics': performance_metrics,
                'allocation_analysis': allocation_analysis,
                'optimization_suggestions': optimization_suggestions,
                'risk_metrics': risk_metrics,
                'rebalancing_needed': self._check_rebalancing_need(allocation_analysis),
                'analysis_date': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio performance: {str(e)}")
            return {'error': str(e)}
    
    async def _calculate_performance_metrics(self, historical_data: List[Dict], current_value: float) -> Dict:
        """Calculate portfolio performance metrics"""
        # Mock performance calculation - replace with real historical analysis
        return {
            'total_return': random.uniform(-20, 40),  # Percentage
            'daily_return': random.uniform(-5, 8),
            'weekly_return': random.uniform(-15, 25),
            'monthly_return': random.uniform(-30, 60),
            'max_drawdown': random.uniform(5, 25),
            'win_rate': random.uniform(40, 80),
            'profit_loss_ratio': random.uniform(1.2, 3.5),
            'volatility': random.uniform(15, 45)
        }
    
    async def _analyze_asset_allocation(self, portfolio: Dict) -> Dict:
        """Analyze current asset allocation"""
        holdings = portfolio.get('holdings', {})
        total_value = sum(holdings.values())
        
        if total_value == 0:
            return {'allocations': {}, 'diversification_score': 0}
        
        allocations = {}
        for crypto, value in holdings.items():
            if value > 0:
                allocations[crypto] = (value / total_value) * 100
        
        # Calculate diversification score
        if len(allocations) == 1:
            diversification_score = 20
        elif len(allocations) == 2:
            diversification_score = 40
        elif len(allocations) <= 4:
            diversification_score = 70
        else:
            diversification_score = 90
        
        return {
            'allocations': allocations,
            'diversification_score': diversification_score,
            'largest_position': max(allocations.values()) if allocations else 0,
            'number_of_positions': len(allocations)
        }
    
    async def _generate_optimization_suggestions(self, portfolio: Dict, performance: Dict, allocation: Dict) -> List[Dict]:
        """Generate portfolio optimization suggestions"""
        suggestions = []
        
        # Check for over-concentration
        if allocation.get('largest_position', 0) > 60:
            suggestions.append({
                'type': 'diversification',
                'priority': 'high',
                'title': 'کاهش تمرکز پرتفوی',
                'description': 'بیش از 60% پرتفوی در یک دارایی متمرکز شده است',
                'action': 'تنوع‌بخشی و کاهش وزن دارایی اصلی',
                'expected_benefit': 'کاهش ریسک کلی پرتفوی'
            })
        
        # Check diversification
        if allocation.get('diversification_score', 0) < 50:
            suggestions.append({
                'type': 'diversification',
                'priority': 'medium',
                'title': 'افزایش تنوع پرتفوی',
                'description': 'پرتفوی کمتر از حد مطلوب متنوع است',
                'action': 'اضافه کردن 2-3 دارایی جدید',
                'expected_benefit': 'بهبود عملکرد تعدیل شده ریسک'
            })
        
        # Check performance
        if performance.get('total_return', 0) < -10:
            suggestions.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'بهبود عملکرد پرتفوی',
                'description': 'عملکرد پرتفوی نسبت به بازار ضعیف است',
                'action': 'بازنگری در انتخاب داراییها',
                'expected_benefit': 'بهبود بازدهی کلی'
            })
        
        # Risk management suggestions
        if performance.get('max_drawdown', 0) > 20:
            suggestions.append({
                'type': 'risk_management',
                'priority': 'high',
                'title': 'کاهش ریسک پرتفوی',
                'description': 'حداکثر افت پرتفوی بالا است',
                'action': 'اضافه کردن داراییهای کم ریسک',
                'expected_benefit': 'کاهش نوسانات پرتفوی'
            })
        
        return suggestions
    
    async def _calculate_risk_metrics(self, historical_data: List[Dict]) -> Dict:
        """Calculate portfolio risk metrics"""
        # Mock risk calculation - replace with real statistical analysis
        return {
            'value_at_risk': random.uniform(5, 15),  # VaR at 95% confidence
            'sharpe_ratio': random.uniform(0.5, 2.5),
            'sortino_ratio': random.uniform(0.6, 3.0),
            'beta': random.uniform(0.8, 1.5),
            'correlation_with_market': random.uniform(0.4, 0.9),
            'downside_deviation': random.uniform(8, 25)
        }
    
    def _check_rebalancing_need(self, allocation: Dict) -> bool:
        """Check if portfolio needs rebalancing"""
        # Simple rebalancing logic - can be enhanced
        allocations = allocation.get('allocations', {})
        if not allocations:
            return False
        
        # Check if any position is too large or too small
        ideal_weight = 100 / len(allocations)  # Equal weighting
        
        for weight in allocations.values():
            if abs(weight - ideal_weight) > (self.rebalancing_threshold * 100):
                return True
        
        return False


class SmartNotificationSystem:
    """Intelligent notification system for users"""
    
    def __init__(self):
        self.notification_types = {
            'price_alert': 'هشدار قیمت',
            'market_news': 'اخبار بازار',
            'portfolio_alert': 'هشدار پرتفوی',
            'trading_opportunity': 'فرصت معاملاتی',
            'risk_warning': 'هشدار ریسک'
        }
    
    async def generate_smart_notifications(self, user_id: str, portfolio: Dict, market_data: Dict, user_preferences: Dict) -> List[Dict]:
        """Generate intelligent notifications for user"""
        try:
            notifications = []
            
            # Price alerts based on portfolio
            price_notifications = await self._generate_price_alerts(portfolio, market_data)
            notifications.extend(price_notifications)
            
            # Market opportunity notifications
            opportunity_notifications = await self._generate_opportunity_alerts(market_data, portfolio)
            notifications.extend(opportunity_notifications)
            
            # Risk warnings
            risk_notifications = await self._generate_risk_warnings(portfolio, market_data)
            notifications.extend(risk_notifications)
            
            # Portfolio rebalancing alerts
            rebalancing_notifications = await self._generate_rebalancing_alerts(portfolio)
            notifications.extend(rebalancing_notifications)
            
            # Sort by priority and limit to top 10
            notifications.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
            
            return notifications[:10]
            
        except Exception as e:
            logger.error(f"Error generating smart notifications: {str(e)}")
            return []
    
    async def _generate_price_alerts(self, portfolio: Dict, market_data: Dict) -> List[Dict]:
        """Generate price movement alerts for portfolio holdings"""
        alerts = []
        holdings = portfolio.get('holdings', {})
        
        for crypto, amount in holdings.items():
            if amount > 0 and crypto in market_data:
                change_24h = market_data[crypto].get('usd_24h_change', 0)
                
                if abs(change_24h) > 10:  # Significant price movement
                    direction = 'صعودی' if change_24h > 0 else 'نزولی'
                    alerts.append({
                        'id': f'price_alert_{crypto}',
                        'type': 'price_alert',
                        'priority': 'high' if abs(change_24h) > 20 else 'medium',
                        'title': f'تحرک قیمتی {crypto}',
                        'message': f'قیمت {crypto} در 24 ساعت گذشته {abs(change_24h):.1f}% حرکت {direction} داشته',
                        'crypto': crypto,
                        'change_percentage': change_24h,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
        
        return alerts
    
    async def _generate_opportunity_alerts(self, market_data: Dict, portfolio: Dict) -> List[Dict]:
        """Generate trading opportunity alerts"""
        alerts = []
        
        # Look for cryptos with significant dips (potential buying opportunities)
        for crypto, data in market_data.items():
            change_24h = data.get('usd_24h_change', 0)
            
            # Significant dip might be a buying opportunity
            if -15 < change_24h < -8:
                alerts.append({
                    'id': f'opportunity_{crypto}',
                    'type': 'trading_opportunity',
                    'priority': 'medium',
                    'title': f'فرصت خرید {crypto}',
                    'message': f'{crypto} در تصحیح قیمت ({abs(change_24h):.1f}%-) - احتمال فرصت خرید',
                    'crypto': crypto,
                    'change_percentage': change_24h,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        
        return alerts[:3]  # Limit to 3 opportunities
    
    async def _generate_risk_warnings(self, portfolio: Dict, market_data: Dict) -> List[Dict]:
        """Generate risk warning notifications"""
        warnings = []
        holdings = portfolio.get('holdings', {})
        total_value = sum(holdings.values())
        
        if total_value == 0:
            return warnings
        
        # Check for over-concentration
        for crypto, value in holdings.items():
            concentration = (value / total_value) * 100
            if concentration > 70:
                warnings.append({
                    'id': f'risk_concentration_{crypto}',
                    'type': 'risk_warning',
                    'priority': 'high',
                    'title': 'ریسک تمرکز پرتفوی',
                    'message': f'بیش از {concentration:.0f}% پرتفوی در {crypto} متمرکز شده - ریسک بالا',
                    'crypto': crypto,
                    'concentration_percentage': concentration,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        
        return warnings
    
    async def _generate_rebalancing_alerts(self, portfolio: Dict) -> List[Dict]:
        """Generate portfolio rebalancing alerts"""
        alerts = []
        holdings = portfolio.get('holdings', {})
        
        if len(holdings) > 1:
            # Simple rebalancing alert
            alerts.append({
                'id': 'rebalancing_suggestion',
                'type': 'portfolio_alert',
                'priority': 'low',
                'title': 'پیشنهاد تعادل‌بخشی پرتفوی',
                'message': 'زمان مناسبی برای بررسی و تعادل‌بخشی پرتفوی شما فرا رسیده',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        return alerts


# Initialize user AI services
personal_assistant = PersonalTradingAssistant()
portfolio_manager = IntelligentPortfolioManager()
notification_system = SmartNotificationSystem()