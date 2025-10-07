"""
AI-Powered Admin Services for Iranian Crypto Exchange
Includes: Fraud Detection, Market Analysis, Predictive Analytics, System Intelligence
"""

import os
import json
import random
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient

# Setup logging
logger = logging.getLogger(__name__)

class FraudDetectionAI:
    """AI-powered fraud detection system"""
    
    def __init__(self):
        self.risk_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }
        
    async def analyze_user_behavior(self, user_id: str, transactions: List[Dict]) -> Dict:
        """Analyze user behavior for suspicious activities"""
        try:
            # Mock AI analysis - replace with real ML models
            risk_factors = []
            risk_score = 0.0
            
            if len(transactions) > 10:
                # High frequency trading detection
                recent_txns = [t for t in transactions if 
                             datetime.fromisoformat(t.get('created_at', '')) > datetime.now(timezone.utc) - timedelta(hours=1)]
                if len(recent_txns) > 5:
                    risk_factors.append("تراکنش‌های پرتعداد در مدت کوتاه")
                    risk_score += 0.3
            
            # Unusual amount patterns
            amounts = [float(t.get('amount', 0)) for t in transactions]
            if amounts:
                avg_amount = sum(amounts) / len(amounts)
                for amount in amounts[-5:]:  # Check last 5 transactions
                    if amount > avg_amount * 10:
                        risk_factors.append("مبلغ تراکنش غیرمعمول")
                        risk_score += 0.2
                        break
            
            # Time-based anomaly detection
            times = [datetime.fromisoformat(t.get('created_at', '')) for t in transactions if t.get('created_at')]
            if len(times) >= 3:
                time_intervals = [(times[i] - times[i-1]).total_seconds() for i in range(1, len(times))]
                avg_interval = sum(time_intervals) / len(time_intervals)
                if any(interval < 10 for interval in time_intervals[-3:]):  # Very quick transactions
                    risk_factors.append("فاصله زمانی کم بین تراکنش‌ها")
                    risk_score += 0.25
            
            # Determine risk level
            if risk_score >= self.risk_thresholds['high']:
                risk_level = 'high'
            elif risk_score >= self.risk_thresholds['medium']:
                risk_level = 'medium'
            elif risk_score >= self.risk_thresholds['low']:
                risk_level = 'low'
            else:
                risk_level = 'low'
            
            return {
                'user_id': user_id,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendations': self._get_risk_recommendations(risk_level),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fraud detection analysis: {str(e)}")
            return {
                'user_id': user_id,
                'risk_score': 0.0,
                'risk_level': 'low',
                'risk_factors': [],
                'recommendations': [],
                'error': str(e)
            }
    
    def _get_risk_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations based on risk level"""
        recommendations = {
            'high': [
                "فریز فوری حساب کاربری",
                "بررسی دستی تمام تراکنش‌ها",
                "تماس تلفنی با کاربر برای احراز هویت",
                "گزارش به واحد مقابله با پولشویی"
            ],
            'medium': [
                "محدودسازی موقت حساب",
                "درخواست مدارک اضافی KYC",
                "نظارت دقیق‌تر بر تراکنش‌ها",
                "اعمال محدودیت مبلغ روزانه"
            ],
            'low': [
                "ادامه نظارت معمول",
                "ثبت در سیستم مانیتورینگ",
                "بررسی دوره‌ای عملکرد کاربر"
            ]
        }
        return recommendations.get(risk_level, [])
    
    async def get_fraud_alerts(self, limit: int = 10) -> List[Dict]:
        """Generate mock fraud alerts - replace with real data"""
        alerts = [
            {
                'id': f'alert_{i}',
                'title': 'فعالیت مشکوک کاربر',
                'description': f'کاربر شناسه {1000+i} دارای الگوی معاملاتی غیرعادی است',
                'risk_level': random.choice(['high', 'medium', 'low']),
                'user_id': f'user_{1000+i}',
                'timestamp': (datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 1440))).strftime('%Y-%m-%d %H:%M'),
                'status': 'pending'
            } for i in range(limit)
        ]
        return alerts
    
    async def detect_fraud_patterns(self) -> Dict:
        """Detect and analyze fraud patterns across the platform"""
        try:
            patterns = {
                'velocity_fraud': {
                    'name': 'تراکنش‌های پرسرعت',
                    'description': 'الگوی تراکنش‌های متعدد در زمان کوتاه',
                    'detected_count': random.randint(5, 25),
                    'risk_score': random.uniform(0.6, 0.9),
                    'affected_users': random.randint(3, 15)
                },
                'amount_anomaly': {
                    'name': 'ناهنجاری مبلغ تراکنش',
                    'description': 'مبالغ غیرمعمول نسبت به تاریخچه کاربر',
                    'detected_count': random.randint(2, 12),
                    'risk_score': random.uniform(0.5, 0.8),
                    'affected_users': random.randint(2, 8)
                },
                'geographic_anomaly': {
                    'name': 'ناهنجاری جغرافیایی',
                    'description': 'ورود از مکان‌های غیرمعمول',
                    'detected_count': random.randint(1, 8),
                    'risk_score': random.uniform(0.4, 0.7),
                    'affected_users': random.randint(1, 5)
                },
                'behavioral_shift': {
                    'name': 'تغییر رفتار کاربر',
                    'description': 'تغییر ناگهانی در الگوی معاملاتی',
                    'detected_count': random.randint(3, 18),
                    'risk_score': random.uniform(0.3, 0.6),
                    'affected_users': random.randint(2, 12)
                }
            }
            
            # Calculate overall fraud risk
            total_risk = sum(p['risk_score'] * p['detected_count'] for p in patterns.values())
            normalized_risk = min(100, (total_risk / 10) * 100)
            
            return {
                'patterns': patterns,
                'overall_risk_score': round(normalized_risk, 1),
                'total_incidents': sum(p['detected_count'] for p in patterns.values()),
                'recommendations': [
                    "تقویت سیستم‌های احراز هویت دومرحله‌ای",
                    "اعمال محدودیت‌های زمانی برای تراکنش‌های بزرگ",
                    "بهبود مانیتورینگ ورود کاربران",
                    "پیاده‌سازی سیستم هشدار فوری"
                ],
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting fraud patterns: {str(e)}")
            return {'error': str(e)}


class MarketIntelligenceAI:
    """AI-powered market analysis and predictions"""
    
    def __init__(self):
        self.prediction_models = {}
        
    async def analyze_market_trends(self, crypto_data: List[Dict]) -> Dict:
        """Analyze market trends and generate insights"""
        try:
            insights = {
                'market_sentiment': self._calculate_market_sentiment(crypto_data),
                'predictions': self._generate_price_predictions(crypto_data),
                'recommendations': [],
                'volatility_analysis': self._analyze_volatility(crypto_data),
                'volume_trends': self._analyze_volume_trends(crypto_data),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Generate recommendations based on analysis
            insights['recommendations'] = self._generate_market_recommendations(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_market_sentiment(self, crypto_data: List[Dict]) -> str:
        """Calculate overall market sentiment"""
        if not crypto_data:
            return 'neutral'
        
        positive_changes = sum(1 for crypto in crypto_data if crypto.get('change_24h', 0) > 0)
        total_cryptos = len(crypto_data)
        
        if positive_changes / total_cryptos > 0.6:
            return 'bullish'
        elif positive_changes / total_cryptos < 0.4:
            return 'bearish'
        else:
            return 'neutral'
    
    def _generate_price_predictions(self, crypto_data: List[Dict]) -> List[Dict]:
        """Generate AI price predictions"""
        predictions = []
        for crypto in crypto_data[:5]:  # Top 5 cryptos
            # Mock prediction - replace with real ML model
            current_change = crypto.get('change_24h', 0)
            
            # Simple trend-based prediction
            if current_change > 5:
                trend = 'up'
                prediction = random.uniform(2, 8)
            elif current_change < -5:
                trend = 'down' 
                prediction = random.uniform(-8, -2)
            else:
                trend = random.choice(['up', 'down'])
                prediction = random.uniform(-3, 3)
            
            predictions.append({
                'symbol': crypto.get('symbol', 'UNKNOWN'),
                'trend': trend,
                'prediction': round(prediction, 2),
                'confidence': random.randint(65, 95),
                'timeframe': '24h'
            })
        
        return predictions
    
    def _analyze_volatility(self, crypto_data: List[Dict]) -> Dict:
        """Analyze market volatility"""
        if not crypto_data:
            return {'level': 'low', 'score': 0}
        
        changes = [abs(crypto.get('change_24h', 0)) for crypto in crypto_data]
        avg_volatility = sum(changes) / len(changes)
        
        if avg_volatility > 10:
            level = 'high'
        elif avg_volatility > 5:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': round(avg_volatility, 2),
            'highest_volatile': max(crypto_data, key=lambda x: abs(x.get('change_24h', 0)))['symbol'] if crypto_data else None
        }
    
    def _analyze_volume_trends(self, crypto_data: List[Dict]) -> Dict:
        """Analyze trading volume trends"""
        # Mock volume analysis
        return {
            'trend': random.choice(['increasing', 'decreasing', 'stable']),
            'change_percentage': round(random.uniform(-15, 25), 2),
            'total_volume_24h': sum(crypto.get('volume_24h', 0) for crypto in crypto_data)
        }
    
    def _generate_market_recommendations(self, insights: Dict) -> List[str]:
        """Generate actionable market recommendations"""
        recommendations = []
        
        sentiment = insights.get('market_sentiment', 'neutral')
        volatility = insights.get('volatility_analysis', {}).get('level', 'low')
        
        if sentiment == 'bullish':
            recommendations.append("بازار در روند صعودی است - افزایش نقدینگی پیشنهاد می‌شود")
            recommendations.append("آماده‌سازی برای افزایش حجم معاملات")
        elif sentiment == 'bearish':
            recommendations.append("بازار در روند نزولی است - احتیاط در معاملات")
            recommendations.append("تقویت سیستم‌های ریسک منجمنت")
        
        if volatility == 'high':
            recommendations.append("نوسانات بالای بازار - تنظیم محدودیت‌های معاملاتی")
            recommendations.append("افزایش فرکانس به‌روزرسانی قیمت‌ها")
        
        return recommendations
    
    async def get_trading_performance(self) -> Dict:
        """Analyze trading platform performance metrics"""
        try:
            # Mock trading performance analysis
            performance_data = {
                'execution_speed': {
                    'avg_order_execution': random.uniform(0.5, 2.5),  # seconds
                    'fastest_execution': random.uniform(0.1, 0.8),
                    'slowest_execution': random.uniform(2.0, 5.0),
                    'success_rate': random.uniform(95, 99.8)
                },
                'liquidity_analysis': {
                    'market_depth': random.uniform(70, 95),
                    'bid_ask_spread': random.uniform(0.1, 0.5),
                    'volume_consistency': random.uniform(80, 98)
                },
                'user_satisfaction': {
                    'avg_slippage': random.uniform(0.05, 0.3),
                    'order_completion_rate': random.uniform(92, 99),
                    'user_retention': random.uniform(75, 90)
                },
                'market_efficiency': {
                    'price_discovery': random.uniform(85, 98),
                    'arbitrage_opportunities': random.randint(2, 15),
                    'market_stability': random.uniform(80, 95)
                }
            }
            
            # Calculate overall performance score
            scores = [
                performance_data['execution_speed']['success_rate'],
                performance_data['liquidity_analysis']['market_depth'],
                performance_data['user_satisfaction']['order_completion_rate'],
                performance_data['market_efficiency']['price_discovery']
            ]
            overall_score = sum(scores) / len(scores)
            
            return {
                'performance_metrics': performance_data,
                'overall_score': round(overall_score, 1),
                'recommendations': self._get_performance_recommendations(overall_score),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trading performance: {str(e)}")
            return {'error': str(e)}
    
    def _get_performance_recommendations(self, score: float) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        if score < 85:
            recommendations.extend([
                "بهینه‌سازی موتور معاملاتی برای کاهش زمان اجرا",
                "بهبود سیستم تطبیق سفارشات",
                "افزایش ظرفیت پردازش همزمان"
            ])
        elif score < 92:
            recommendations.extend([
                "تنظیم دقیق‌تر پارامترهای ریسک",
                "بهبود الگوریتم‌های قیمت‌گذاری",
                "ارتقای زیرساخت شبکه"
            ])
        else:
            recommendations.extend([
                "حفظ عملکرد فعلی عالی",
                "بررسی امکانات توسعه جدید",
                "مانیتورینگ مستمر کیفیت خدمات"
            ])
        
        return recommendations


class SystemIntelligenceAI:
    """AI-powered system monitoring and optimization"""
    
    def __init__(self):
        self.performance_metrics = {}
        
    async def analyze_system_health(self) -> Dict:
        """Analyze overall system health"""
        try:
            # Mock system analysis - integrate with real monitoring tools
            metrics = {
                'api_response_time': random.uniform(50, 200),  # milliseconds
                'success_rate': random.uniform(95, 99.9),  # percentage
                'requests_per_second': random.randint(100, 1000),
                'error_rate': random.uniform(0.1, 2.0),  # percentage
                'database_connections': random.randint(50, 200),
                'memory_usage': random.uniform(40, 85),  # percentage
                'cpu_usage': random.uniform(20, 70),  # percentage
                'disk_usage': random.uniform(30, 80)  # percentage
            }
            
            # Calculate overall health score
            score = self._calculate_health_score(metrics)
            
            return {
                'score': score,
                'metrics': metrics,
                'status': self._get_status_from_score(score),
                'recommendations': self._get_health_recommendations(score, metrics),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in system health analysis: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_health_score(self, metrics: Dict) -> int:
        """Calculate overall system health score (0-100)"""
        # Weighted scoring system
        weights = {
            'api_response_time': -0.2,  # Lower is better
            'success_rate': 0.3,        # Higher is better
            'error_rate': -0.3,         # Lower is better
            'memory_usage': -0.1,       # Lower is better
            'cpu_usage': -0.1           # Lower is better
        }
        
        normalized_score = 0
        
        # Normalize and weight each metric
        if metrics['api_response_time'] <= 100:
            normalized_score += 30
        elif metrics['api_response_time'] <= 200:
            normalized_score += 20
        else:
            normalized_score += 10
            
        normalized_score += metrics['success_rate'] * 0.3
        normalized_score -= metrics['error_rate'] * 10
        normalized_score -= (metrics['memory_usage'] - 50) * 0.2
        normalized_score -= (metrics['cpu_usage'] - 30) * 0.2
        
        return max(0, min(100, int(normalized_score)))
    
    def _get_status_from_score(self, score: int) -> str:
        """Get system status from health score"""
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        elif score >= 70:
            return 'warning'
        else:
            return 'critical'
    
    def _get_health_recommendations(self, score: int, metrics: Dict) -> List[str]:
        """Get system optimization recommendations"""
        recommendations = []
        
        if metrics['api_response_time'] > 150:
            recommendations.append("بهینه‌سازی عملکرد API - زمان پاسخ بالا")
        
        if metrics['success_rate'] < 98:
            recommendations.append("بررسی خطاهای API و رفع مشکلات")
        
        if metrics['memory_usage'] > 80:
            recommendations.append("بهینه‌سازی مصرف حافظه سیستم")
        
        if metrics['cpu_usage'] > 60:
            recommendations.append("بررسی فرآیندهای پرمصرف CPU")
        
        if score < 80:
            recommendations.append("نیاز به بررسی فوری سیستم")
        
        return recommendations


class PredictiveAnalyticsAI:
    """AI-powered predictive analytics for business intelligence"""
    
    def __init__(self):
        self.models = {}
        
    async def predict_user_churn(self, user_data: List[Dict]) -> Dict:
        """Predict user churn probability"""
        # Mock churn prediction - replace with real ML model
        high_risk_users = []
        medium_risk_users = []
        
        for user in user_data:
            # Simple heuristic-based prediction
            last_login = user.get('last_login')
            if last_login:
                days_inactive = (datetime.now(timezone.utc) - datetime.fromisoformat(last_login)).days
                
                if days_inactive > 30:
                    high_risk_users.append(user)
                elif days_inactive > 14:
                    medium_risk_users.append(user)
        
        return {
            'high_risk_count': len(high_risk_users),
            'medium_risk_count': len(medium_risk_users),
            'high_risk_users': high_risk_users[:10],  # Top 10
            'recommendations': [
                "ارسال ایمیل بازگشت به کاربران پرخطر",
                "ارائه تخفیف ویژه برای بازگشت کاربران",
                "بررسی دلایل عدم استفاده از پلتفرم"
            ],
            'analysis_date': datetime.now(timezone.utc).isoformat()
        }
    
    async def forecast_trading_volume(self, historical_data: List[Dict]) -> Dict:
        """Forecast future trading volume"""
        # Mock forecasting - replace with real time series model
        if not historical_data:
            return {'error': 'No historical data available'}
        
        recent_volumes = [item.get('volume', 0) for item in historical_data[-7:]]  # Last 7 days
        avg_volume = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0
        
        # Simple trend-based forecast
        trend = random.uniform(0.8, 1.2)  # -20% to +20% change
        
        forecasts = []
        for i in range(1, 8):  # Next 7 days
            forecast_volume = avg_volume * trend * (1 + random.uniform(-0.1, 0.1))
            forecasts.append({
                'date': (datetime.now(timezone.utc) + timedelta(days=i)).date().isoformat(),
                'predicted_volume': round(forecast_volume, 2),
                'confidence': random.randint(70, 90)
            })
        
        return {
            'forecasts': forecasts,
            'trend': 'increasing' if trend > 1 else 'decreasing',
            'confidence_avg': sum(f['confidence'] for f in forecasts) / len(forecasts),
            'model': 'ARIMA-based prediction',
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def analyze_revenue_trends(self, revenue_data: List[Dict]) -> Dict:
        """Analyze revenue trends and predictions"""
        if not revenue_data:
            return {'error': 'No revenue data available'}
        
        # Mock revenue analysis
        total_revenue = sum(item.get('amount', 0) for item in revenue_data)
        daily_avg = total_revenue / max(len(revenue_data), 1)
        
        # Growth rate calculation
        if len(revenue_data) >= 2:
            recent_avg = sum(item.get('amount', 0) for item in revenue_data[-3:]) / 3
            older_avg = sum(item.get('amount', 0) for item in revenue_data[-7:-3]) / 4 if len(revenue_data) >= 7 else daily_avg
            growth_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            growth_rate = 0
        
        return {
            'total_revenue': total_revenue,
            'daily_average': daily_avg,
            'growth_rate': round(growth_rate, 2),
            'trend': 'positive' if growth_rate > 0 else 'negative',
            'projections': {
                'next_month': daily_avg * 30 * (1 + growth_rate / 100),
                'next_quarter': daily_avg * 90 * (1 + growth_rate / 100)
            },
            'recommendations': self._get_revenue_recommendations(growth_rate),
            'analysis_date': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_revenue_recommendations(self, growth_rate: float) -> List[str]:
        """Get revenue optimization recommendations"""
        if growth_rate > 5:
            return [
                "روند درآمد مثبت است - تداوم استراتژی فعلی",
                "بررسی امکان افزایش کارمزد معاملات",
                "سرمایه‌گذاری در بازاریابی برای جذب کاربران بیشتر"
            ]
        elif growth_rate < -5:
            return [
                "کاهش درآمد نگران‌کننده - نیاز به بازنگری استراتژی",
                "بررسی کاهش کارمزدها برای جذب مجدد کاربران",
                "تحلیل رقبا و ارائه خدمات جدید"
            ]
        else:
            return [
                "درآمد در حال ثبات - امکان بهینه‌سازی وجود دارد",
                "راه‌اندازی کمپین‌های تشویقی",
                "بررسی نظرات کاربران برای بهبود خدمات"
            ]


# Initialize AI services
fraud_detector = FraudDetectionAI()
market_intelligence = MarketIntelligenceAI()
system_intelligence = SystemIntelligenceAI()
predictive_analytics = PredictiveAnalyticsAI()