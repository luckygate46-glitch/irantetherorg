"""
Admin AI Analytics Service
Rule-based AI features for admin panel - NO external API dependencies
Provides 18 AI-powered features for fraud detection, analytics, and automation
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import statistics

class AdminAIAnalytics:
    """Rule-based AI analytics service for admin panel"""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== SECURITY & FRAUD DETECTION ====================
    
    async def detect_fraud(self) -> Dict:
        """AI Fraud Detection System - Detect suspicious activities"""
        try:
            # Get recent orders (last 24 hours)
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            
            recent_orders = await self.db.trading_orders.find({
                "created_at": {"$gte": yesterday.isoformat()}
            }).to_list(length=1000)
            
            # Get all users
            all_users = await self.db.users.find({}).to_list(length=10000)
            
            alerts = []
            
            # Rule 1: Multiple large orders from same user
            user_order_counts = {}
            for order in recent_orders:
                user_id = order.get("user_id")
                amount = order.get("amount_tmn", 0)
                
                if user_id not in user_order_counts:
                    user_order_counts[user_id] = {"count": 0, "total": 0}
                user_order_counts[user_id]["count"] += 1
                user_order_counts[user_id]["total"] += amount
            
            for user_id, stats in user_order_counts.items():
                if stats["count"] > 10:  # More than 10 orders in 24h
                    alerts.append({
                        "type": "suspicious_activity",
                        "severity": "high",
                        "user_id": user_id,
                        "description": f"کاربر {stats['count']} سفارش در ۲۴ ساعت ثبت کرده (مشکوک به ربات)",
                        "details": f"تعداد: {stats['count']}, مجموع: {stats['total']:,.0f} تومان"
                    })
                
                if stats["total"] > 500000000:  # More than 500M Toman
                    alerts.append({
                        "type": "large_transactions",
                        "severity": "medium",
                        "user_id": user_id,
                        "description": f"حجم معاملات بالا: {stats['total']:,.0f} تومان در ۲۴ ساعت",
                        "details": f"تعداد سفارشات: {stats['count']}"
                    })
            
            # Rule 2: Users with no KYC but high balance/orders
            for user in all_users:
                kyc_level = user.get("kyc_level", 0)
                balance = user.get("wallet_balance_tmn", 0)
                
                if kyc_level == 0 and balance > 10000000:  # 10M+ with no KYC
                    alerts.append({
                        "type": "kyc_violation",
                        "severity": "high",
                        "user_id": user.get("id"),
                        "description": f"موجودی بالا بدون تایید KYC: {balance:,.0f} تومان",
                        "details": f"سطح KYC: {kyc_level}"
                    })
            
            return {
                "total_alerts": len(alerts),
                "high_severity": len([a for a in alerts if a["severity"] == "high"]),
                "medium_severity": len([a for a in alerts if a["severity"] == "medium"]),
                "alerts": alerts[:50],  # Return top 50
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "total_alerts": 0,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def detect_anomalies(self) -> Dict:
        """Anomaly Detection Dashboard - Detect unusual patterns"""
        try:
            # Get data from last 7 days
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            recent_orders = await self.db.trading_orders.find({
                "created_at": {"$gte": week_ago.isoformat()}
            }).to_list(length=10000)
            
            # Analyze daily patterns
            daily_orders = {}
            daily_volumes = {}
            
            for order in recent_orders:
                date = order.get("created_at", "")[:10]  # YYYY-MM-DD
                amount = order.get("amount_tmn", 0)
                
                if date not in daily_orders:
                    daily_orders[date] = 0
                    daily_volumes[date] = 0
                
                daily_orders[date] += 1
                daily_volumes[date] += amount
            
            # Calculate averages
            avg_daily_orders = statistics.mean(daily_orders.values()) if daily_orders else 0
            avg_daily_volume = statistics.mean(daily_volumes.values()) if daily_volumes else 0
            
            anomalies = []
            
            # Detect anomalies (2x above average)
            for date, count in daily_orders.items():
                if count > avg_daily_orders * 2:
                    anomalies.append({
                        "type": "order_spike",
                        "date": date,
                        "description": f"افزایش غیرعادی سفارشات: {count} سفارش (میانگین: {avg_daily_orders:.0f})",
                        "severity": "medium"
                    })
            
            for date, volume in daily_volumes.items():
                if volume > avg_daily_volume * 2:
                    anomalies.append({
                        "type": "volume_spike",
                        "date": date,
                        "description": f"افزایش غیرعادی حجم معاملات: {volume:,.0f} تومان",
                        "severity": "high"
                    })
            
            return {
                "total_anomalies": len(anomalies),
                "avg_daily_orders": round(avg_daily_orders, 2),
                "avg_daily_volume": round(avg_daily_volume, 2),
                "anomalies": anomalies,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def calculate_risk_scores(self) -> Dict:
        """AI Risk Scoring - Calculate risk score for each user"""
        try:
            users = await self.db.users.find({}).to_list(length=1000)
            
            high_risk_users = []
            medium_risk_users = []
            
            for user in users:
                risk_score = 0
                risk_factors = []
                
                # Factor 1: KYC Level (0-40 points)
                kyc_level = user.get("kyc_level", 0)
                if kyc_level == 0:
                    risk_score += 40
                    risk_factors.append("بدون تایید KYC")
                elif kyc_level == 1:
                    risk_score += 20
                    risk_factors.append("KYC سطح 1")
                
                # Factor 2: Account Age (0-20 points)
                created_at = user.get("created_at", "")
                if created_at:
                    account_age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days
                    if account_age_days < 7:
                        risk_score += 20
                        risk_factors.append("حساب جدید")
                    elif account_age_days < 30:
                        risk_score += 10
                
                # Factor 3: Balance (0-20 points)
                balance = user.get("wallet_balance_tmn", 0)
                if balance > 100000000:  # > 100M
                    risk_score += 20
                    risk_factors.append("موجودی بالا")
                
                # Factor 4: Incomplete Profile (0-20 points)
                if not user.get("first_name") or not user.get("last_name"):
                    risk_score += 10
                    risk_factors.append("پروفایل ناقص")
                
                if not user.get("phone"):
                    risk_score += 10
                    risk_factors.append("بدون شماره تلفن")
                
                # Categorize
                if risk_score >= 60:
                    high_risk_users.append({
                        "user_id": user.get("id"),
                        "email": user.get("email"),
                        "risk_score": risk_score,
                        "risk_factors": risk_factors
                    })
                elif risk_score >= 30:
                    medium_risk_users.append({
                        "user_id": user.get("id"),
                        "email": user.get("email"),
                        "risk_score": risk_score,
                        "risk_factors": risk_factors
                    })
            
            return {
                "high_risk_count": len(high_risk_users),
                "medium_risk_count": len(medium_risk_users),
                "high_risk_users": high_risk_users[:20],
                "medium_risk_users": medium_risk_users[:20],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ==================== ANALYTICS & INSIGHTS ====================
    
    async def predict_user_analytics(self) -> Dict:
        """Predictive User Analytics - Predict churn, high-value users"""
        try:
            users = await self.db.users.find({}).to_list(length=10000)
            orders = await self.db.trading_orders.find({}).to_list(length=10000)
            
            # Calculate user activity
            user_activity = {}
            for order in orders:
                user_id = order.get("user_id")
                if user_id not in user_activity:
                    user_activity[user_id] = {
                        "order_count": 0,
                        "total_volume": 0,
                        "last_order": None
                    }
                
                user_activity[user_id]["order_count"] += 1
                user_activity[user_id]["total_volume"] += order.get("amount_tmn", 0)
                
                order_date = order.get("created_at", "")
                if not user_activity[user_id]["last_order"] or order_date > user_activity[user_id]["last_order"]:
                    user_activity[user_id]["last_order"] = order_date
            
            # Identify segments
            high_value_users = []
            churn_risk_users = []
            inactive_users = []
            
            now = datetime.now(timezone.utc)
            
            for user in users:
                user_id = user.get("id")
                activity = user_activity.get(user_id, {"order_count": 0, "total_volume": 0, "last_order": None})
                
                # High-value users: >10 orders OR >50M volume
                if activity["order_count"] > 10 or activity["total_volume"] > 50000000:
                    high_value_users.append({
                        "user_id": user_id,
                        "email": user.get("email"),
                        "orders": activity["order_count"],
                        "volume": activity["total_volume"]
                    })
                
                # Churn risk: Had orders but inactive >30 days
                if activity["last_order"]:
                    last_order_date = datetime.fromisoformat(activity["last_order"].replace('Z', '+00:00'))
                    days_inactive = (now - last_order_date).days
                    
                    if days_inactive > 30 and activity["order_count"] > 3:
                        churn_risk_users.append({
                            "user_id": user_id,
                            "email": user.get("email"),
                            "days_inactive": days_inactive,
                            "previous_orders": activity["order_count"]
                        })
                
                # Inactive users: Registered but never ordered
                if activity["order_count"] == 0:
                    created_at = user.get("created_at", "")
                    if created_at:
                        account_age = (now - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days
                        if account_age > 7:
                            inactive_users.append({
                                "user_id": user_id,
                                "email": user.get("email"),
                                "account_age_days": account_age
                            })
            
            return {
                "high_value_count": len(high_value_users),
                "churn_risk_count": len(churn_risk_users),
                "inactive_count": len(inactive_users),
                "high_value_users": high_value_users[:20],
                "churn_risk_users": churn_risk_users[:20],
                "inactive_users": inactive_users[:20],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def detect_market_manipulation(self) -> Dict:
        """Market Manipulation Detection - Detect coordinated trading"""
        try:
            # Get recent orders
            recent_orders = await self.db.trading_orders.find({}).sort("created_at", -1).to_list(length=1000)
            
            alerts = []
            
            # Rule 1: Same coin, same amount, multiple users (coordinated)
            order_patterns = {}
            for order in recent_orders:
                coin = order.get("coin_symbol")
                amount = order.get("amount_tmn", 0)
                pattern_key = f"{coin}_{amount}"
                
                if pattern_key not in order_patterns:
                    order_patterns[pattern_key] = []
                order_patterns[pattern_key].append(order)
            
            for pattern_key, orders in order_patterns.items():
                if len(orders) >= 5:  # 5+ identical orders
                    unique_users = set(o.get("user_id") for o in orders)
                    if len(unique_users) >= 3:  # From 3+ different users
                        alerts.append({
                            "type": "coordinated_trading",
                            "severity": "high",
                            "coin": orders[0].get("coin_symbol"),
                            "amount": orders[0].get("amount_tmn"),
                            "order_count": len(orders),
                            "unique_users": len(unique_users),
                            "description": f"معاملات هماهنگ مشکوک: {len(orders)} سفارش یکسان از {len(unique_users)} کاربر"
                        })
            
            # Rule 2: Rapid buy-sell by same user (pump and dump)
            user_orders = {}
            for order in recent_orders[:500]:  # Last 500 orders
                user_id = order.get("user_id")
                if user_id not in user_orders:
                    user_orders[user_id] = []
                user_orders[user_id].append(order)
            
            for user_id, orders in user_orders.items():
                if len(orders) >= 10:  # 10+ orders
                    buy_count = sum(1 for o in orders if o.get("order_type") == "buy")
                    sell_count = sum(1 for o in orders if o.get("order_type") == "sell")
                    
                    if buy_count >= 5 and sell_count >= 5:
                        alerts.append({
                            "type": "pump_dump_suspected",
                            "severity": "high",
                            "user_id": user_id,
                            "buy_count": buy_count,
                            "sell_count": sell_count,
                            "description": f"مشکوک به pump-dump: {buy_count} خرید و {sell_count} فروش متوالی"
                        })
            
            return {
                "total_alerts": len(alerts),
                "high_severity": len([a for a in alerts if a["severity"] == "high"]),
                "alerts": alerts,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def optimize_revenue(self) -> Dict:
        """Revenue Optimization AI - Suggest optimal strategies"""
        try:
            # Get all orders
            all_orders = await self.db.trading_orders.find({}).to_list(length=10000)
            users = await self.db.users.find({}).to_list(length=10000)
            
            # Calculate current metrics
            total_volume = sum(o.get("amount_tmn", 0) for o in all_orders)
            completed_orders = [o for o in all_orders if o.get("status") == "completed"]
            
            # Current fee (assume 0.5%)
            current_fee = 0.005
            estimated_revenue = total_volume * current_fee
            
            # Calculate user tiers
            user_volumes = {}
            for order in all_orders:
                user_id = order.get("user_id")
                if user_id not in user_volumes:
                    user_volumes[user_id] = 0
                user_volumes[user_id] += order.get("amount_tmn", 0)
            
            high_volume_users = len([v for v in user_volumes.values() if v > 100000000])  # >100M
            medium_volume_users = len([v for v in user_volumes.values() if 10000000 < v <= 100000000])  # 10M-100M
            low_volume_users = len([v for v in user_volumes.values() if v <= 10000000])  # <10M
            
            recommendations = []
            
            # Recommendation 1: Tiered fee structure
            recommendations.append({
                "category": "fee_optimization",
                "title": "ساختار کارمزد چند سطحی",
                "description": f"کاربران حجم بالا: {high_volume_users} نفر - کارمزد 0.3%، حجم متوسط: {medium_volume_users} نفر - کارمزد 0.5%، حجم پایین: {low_volume_users} نفر - کارمزد 0.7%",
                "estimated_increase": "15-20%",
                "priority": "high"
            })
            
            # Recommendation 2: Premium membership
            potential_premium_users = high_volume_users + medium_volume_users
            premium_revenue = potential_premium_users * 500000  # 500K Toman/month
            
            recommendations.append({
                "category": "premium_membership",
                "title": "عضویت ویژه ماهانه",
                "description": f"{potential_premium_users} کاربر بالقوه برای عضویت ویژه (۵۰۰,۰۰۰ تومان/ماه)",
                "estimated_revenue": f"{premium_revenue:,.0f} تومان/ماه",
                "priority": "high"
            })
            
            # Recommendation 3: Inactive user reactivation
            inactive_count = len([u for u in users if user_volumes.get(u.get("id"), 0) == 0])
            
            recommendations.append({
                "category": "user_activation",
                "title": "فعال‌سازی کاربران غیرفعال",
                "description": f"{inactive_count} کاربر غیرفعال - پیشنهاد بونوس یا کارمزد رایگان برای اولین معامله",
                "estimated_impact": "5-10% افزایش کاربران فعال",
                "priority": "medium"
            })
            
            return {
                "current_monthly_revenue": round(estimated_revenue, 2),
                "total_volume": round(total_volume, 2),
                "completed_orders": len(completed_orders),
                "recommendations": recommendations,
                "user_tiers": {
                    "high_volume": high_volume_users,
                    "medium_volume": medium_volume_users,
                    "low_volume": low_volume_users
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ==================== AUTOMATION ====================
    
    async def triage_support_tickets(self) -> Dict:
        """Automated Support Ticket Triage - Categorize and prioritize"""
        try:
            # Get recent orders with issues
            pending_orders = await self.db.trading_orders.find({"status": "pending"}).to_list(length=1000)
            
            # Simulate support tickets from order issues
            tickets = []
            
            # High priority: Large pending orders >50M
            for order in pending_orders:
                amount = order.get("amount_tmn", 0)
                if amount > 50000000:
                    tickets.append({
                        "priority": "high",
                        "category": "large_order",
                        "user_id": order.get("user_id"),
                        "order_id": order.get("id"),
                        "description": f"سفارش بزرگ در انتظار تایید: {amount:,.0f} تومان",
                        "suggested_action": "بررسی فوری و تایید یا رد"
                    })
            
            # Medium priority: Pending >24 hours
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            for order in pending_orders:
                created_at = order.get("created_at", "")
                if created_at:
                    order_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if order_date < yesterday:
                        tickets.append({
                            "priority": "medium",
                            "category": "delayed_order",
                            "user_id": order.get("user_id"),
                            "order_id": order.get("id"),
                            "description": "سفارش بیش از ۲۴ ساعت در انتظار",
                            "suggested_action": "بررسی و اقدام"
                        })
            
            return {
                "total_tickets": len(tickets),
                "high_priority": len([t for t in tickets if t["priority"] == "high"]),
                "medium_priority": len([t for t in tickets if t["priority"] == "medium"]),
                "tickets": tickets[:30],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def analyze_user_intent(self) -> Dict:
        """User Intent Analysis - Understand what users are trying to do"""
        try:
            users = await self.db.users.find({}).to_list(length=10000)
            orders = await self.db.trading_orders.find({}).to_list(length=10000)
            
            # Analyze user journey stages
            registered_but_no_kyc = 0
            kyc_but_no_wallet = 0
            wallet_but_no_order = 0
            active_traders = 0
            
            user_orders = {}
            for order in orders:
                user_id = order.get("user_id")
                if user_id not in user_orders:
                    user_orders[user_id] = []
                user_orders[user_id].append(order)
            
            for user in users:
                user_id = user.get("id")
                kyc_level = user.get("kyc_level", 0)
                
                # Check if user has wallet addresses
                # This is a simplified check - in real implementation, query wallet_addresses collection
                has_orders = user_id in user_orders
                
                if kyc_level == 0:
                    registered_but_no_kyc += 1
                elif not has_orders:
                    kyc_but_no_wallet += 1  # Simplified
                else:
                    active_traders += 1
            
            # Calculate conversion rates
            total_users = len(users)
            kyc_conversion = ((total_users - registered_but_no_kyc) / total_users * 100) if total_users > 0 else 0
            trading_conversion = (active_traders / total_users * 100) if total_users > 0 else 0
            
            insights = []
            
            if registered_but_no_kyc > total_users * 0.5:
                insights.append({
                    "issue": "drop_off_at_kyc",
                    "severity": "high",
                    "description": f"{registered_but_no_kyc} کاربر ({registered_but_no_kyc/total_users*100:.1f}%) در مرحله KYC متوقف شده‌اند",
                    "suggestion": "ساده‌سازی فرآیند KYC، راهنمای گام‌به‌گام"
                })
            
            if kyc_but_no_wallet > 0:
                insights.append({
                    "issue": "drop_off_at_wallet",
                    "severity": "medium",
                    "description": f"{kyc_but_no_wallet} کاربر KYC دارند اما معامله نکرده‌اند",
                    "suggestion": "آموزش نحوه افزودن کیف پول و ثبت اولین سفارش"
                })
            
            return {
                "total_users": total_users,
                "stages": {
                    "registered_no_kyc": registered_but_no_kyc,
                    "kyc_no_orders": kyc_but_no_wallet,
                    "active_traders": active_traders
                },
                "conversion_rates": {
                    "kyc_conversion": round(kyc_conversion, 2),
                    "trading_conversion": round(trading_conversion, 2)
                },
                "insights": insights,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def monitor_transactions(self) -> Dict:
        """Transaction Monitoring AI - Real-time monitoring"""
        try:
            # Get recent transactions (last hour)
            hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            
            recent_orders = await self.db.trading_orders.find({
                "created_at": {"$gte": hour_ago.isoformat()}
            }).to_list(length=1000)
            
            alerts = []
            
            # Monitor for suspicious patterns
            for order in recent_orders:
                amount = order.get("amount_tmn", 0)
                user_id = order.get("user_id")
                
                # Alert 1: Very large transactions
                if amount > 100000000:  # >100M
                    alerts.append({
                        "type": "large_transaction",
                        "severity": "high",
                        "order_id": order.get("id"),
                        "user_id": user_id,
                        "amount": amount,
                        "description": f"معامله بزرگ: {amount:,.0f} تومان"
                    })
                
                # Alert 2: Pending too long
                if order.get("status") == "pending":
                    created_at = order.get("created_at", "")
                    if created_at:
                        order_age = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).total_seconds() / 3600
                        if order_age > 1:  # >1 hour pending
                            alerts.append({
                                "type": "delayed_processing",
                                "severity": "medium",
                                "order_id": order.get("id"),
                                "user_id": user_id,
                                "hours_pending": round(order_age, 1),
                                "description": f"سفارش {order_age:.1f} ساعت در انتظار"
                            })
            
            return {
                "monitoring_period": "1 hour",
                "total_transactions": len(recent_orders),
                "total_volume": sum(o.get("amount_tmn", 0) for o in recent_orders),
                "alerts": alerts,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ==================== MARKET INTELLIGENCE ====================
    
    async def detect_price_anomalies(self) -> Dict:
        """Price Anomaly Detection - Detect unusual price movements"""
        try:
            # Get current prices (from static or API)
            # This is a simplified version - actual implementation would compare with historical data
            
            # Mock price history for demonstration
            anomalies = []
            
            # Example: If we had price history, we'd detect:
            # - Sudden >10% changes
            # - Prices deviating from global markets
            # - Unusual spreads
            
            # For now, return structure showing what would be detected
            anomalies.append({
                "type": "price_info",
                "description": "سیستم آماده است - نیاز به تاریخچه قیمت برای تشخیص ناهنجاری",
                "note": "برای فعال‌سازی کامل، نیاز به ذخیره تاریخچه قیمت‌ها"
            })
            
            return {
                "total_anomalies": 0,
                "anomalies": anomalies,
                "status": "ready",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def analyze_market_sentiment(self) -> Dict:
        """Market Sentiment Analysis - Analyze overall market mood"""
        try:
            # Get recent orders to gauge sentiment
            recent_orders = await self.db.trading_orders.find({}).sort("created_at", -1).to_list(length=1000)
            
            buy_orders = [o for o in recent_orders if o.get("order_type") == "buy"]
            sell_orders = [o for o in recent_orders if o.get("order_type") == "sell"]
            
            buy_volume = sum(o.get("amount_tmn", 0) for o in buy_orders)
            sell_volume = sum(o.get("amount_tmn", 0) for o in sell_orders)
            
            total_volume = buy_volume + sell_volume
            
            if total_volume > 0:
                buy_percentage = (buy_volume / total_volume) * 100
                sell_percentage = (sell_volume / total_volume) * 100
            else:
                buy_percentage = 50
                sell_percentage = 50
            
            # Determine sentiment
            if buy_percentage > 60:
                sentiment = "صعودی"
                mood = "خوشبین"
            elif sell_percentage > 60:
                sentiment = "نزولی"
                mood = "بدبین"
            else:
                sentiment = "خنثی"
                mood = "متعادل"
            
            return {
                "sentiment": sentiment,
                "mood": mood,
                "buy_percentage": round(buy_percentage, 2),
                "sell_percentage": round(sell_percentage, 2),
                "buy_volume": buy_volume,
                "sell_volume": sell_volume,
                "total_orders": len(recent_orders),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ==================== SMART AUTOMATION ====================
    
    async def auto_kyc_approval(self) -> Dict:
        """Auto-KYC Approval - Automatically approve low-risk KYC"""
        try:
            # Get users pending KYC approval
            pending_kyc_users = await self.db.users.find({
                "kyc_level": 0
            }).to_list(length=1000)
            
            auto_approve_candidates = []
            manual_review_needed = []
            
            for user in pending_kyc_users:
                risk_score = 0
                
                # Low risk factors
                has_phone = bool(user.get("phone"))
                has_email = bool(user.get("email"))
                has_full_name = bool(user.get("first_name") and user.get("last_name"))
                
                # Calculate risk
                if not has_phone:
                    risk_score += 30
                if not has_email:
                    risk_score += 20
                if not has_full_name:
                    risk_score += 20
                
                # Check account age
                created_at = user.get("created_at", "")
                if created_at:
                    account_age = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days
                    if account_age < 1:
                        risk_score += 30
                
                # Decision
                if risk_score < 30:
                    auto_approve_candidates.append({
                        "user_id": user.get("id"),
                        "email": user.get("email"),
                        "risk_score": risk_score,
                        "recommendation": "تایید خودکار - ریسک پایین"
                    })
                else:
                    manual_review_needed.append({
                        "user_id": user.get("id"),
                        "email": user.get("email"),
                        "risk_score": risk_score,
                        "recommendation": "نیاز به بررسی دستی"
                    })
            
            return {
                "auto_approve_count": len(auto_approve_candidates),
                "manual_review_count": len(manual_review_needed),
                "auto_approve_candidates": auto_approve_candidates[:50],
                "manual_review_needed": manual_review_needed[:50],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def generate_automated_notifications(self) -> Dict:
        """Automated Notifications - Smart notification system"""
        try:
            notifications = []
            
            # Check for important events
            # 1. Pending orders >24 hours
            yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
            pending_orders = await self.db.trading_orders.find({
                "status": "pending",
                "created_at": {"$lt": yesterday.isoformat()}
            }).to_list(length=100)
            
            if pending_orders:
                notifications.append({
                    "type": "admin_action_needed",
                    "priority": "high",
                    "title": "سفارشات در انتظار تایید",
                    "message": f"{len(pending_orders)} سفارش بیش از ۲۴ ساعت در انتظار تایید هستند",
                    "action_url": "/admin/orders"
                })
            
            # 2. High-value pending orders
            high_value_pending = await self.db.trading_orders.find({
                "status": "pending",
                "amount_tmn": {"$gt": 50000000}
            }).to_list(length=100)
            
            if high_value_pending:
                notifications.append({
                    "type": "high_value_order",
                    "priority": "high",
                    "title": "سفارشات با ارزش بالا",
                    "message": f"{len(high_value_pending)} سفارش با مبلغ بالای ۵۰ میلیون تومان در انتظار",
                    "action_url": "/admin/orders"
                })
            
            # 3. New registrations today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            new_users = await self.db.users.find({
                "created_at": {"$gte": today_start.isoformat()}
            }).to_list(length=1000)
            
            if new_users:
                notifications.append({
                    "type": "info",
                    "priority": "low",
                    "title": "کاربران جدید",
                    "message": f"{len(new_users)} کاربر جدید امروز ثبت‌نام کرده‌اند",
                    "action_url": "/admin/users"
                })
            
            return {
                "total_notifications": len(notifications),
                "high_priority": len([n for n in notifications if n["priority"] == "high"]),
                "notifications": notifications,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ==================== BUSINESS INTELLIGENCE ====================
    
    async def optimize_conversion(self) -> Dict:
        """Conversion Optimization - Improve registration-to-trading conversion"""
        try:
            users = await self.db.users.find({}).to_list(length=10000)
            orders = await self.db.trading_orders.find({}).to_list(length=10000)
            
            # Calculate funnel
            total_registered = len(users)
            kyc_completed = len([u for u in users if u.get("kyc_level", 0) > 0])
            users_with_orders = len(set(o.get("user_id") for o in orders))
            
            # Calculate conversion rates
            kyc_conversion = (kyc_completed / total_registered * 100) if total_registered > 0 else 0
            trading_conversion = (users_with_orders / total_registered * 100) if total_registered > 0 else 0
            
            # Identify bottlenecks
            bottlenecks = []
            
            if kyc_conversion < 50:
                bottlenecks.append({
                    "stage": "KYC",
                    "current_rate": round(kyc_conversion, 2),
                    "target_rate": 70,
                    "suggestions": [
                        "ساده‌سازی فرآیند تایید هویت",
                        "ارائه راهنمای تصویری گام‌به‌گام",
                        "ارسال یادآوری به کاربران ناتمام"
                    ]
                })
            
            if trading_conversion < 30:
                bottlenecks.append({
                    "stage": "First Trade",
                    "current_rate": round(trading_conversion, 2),
                    "target_rate": 50,
                    "suggestions": [
                        "ارائه بونوس برای اولین معامله",
                        "آموزش ویدیویی نحوه معامله",
                        "کارمزد رایگان برای اولین سفارش"
                    ]
                })
            
            return {
                "total_registered": total_registered,
                "kyc_completed": kyc_completed,
                "users_with_orders": users_with_orders,
                "conversion_rates": {
                    "kyc_conversion": round(kyc_conversion, 2),
                    "trading_conversion": round(trading_conversion, 2)
                },
                "bottlenecks": bottlenecks,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def ai_powered_search(self, query: str) -> Dict:
        """AI-Powered Search - Search users, orders with natural language"""
        try:
            query_lower = query.lower()
            results = {
                "users": [],
                "orders": [],
                "insights": []
            }
            
            # Search users
            if "کاربر" in query or "user" in query_lower:
                users = await self.db.users.find({}).to_list(length=100)
                
                # Filter by query keywords
                if "جدید" in query or "new" in query_lower:
                    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                    results["users"] = [
                        {
                            "id": u.get("id"),
                            "email": u.get("email"),
                            "created_at": u.get("created_at")
                        }
                        for u in users
                        if u.get("created_at") and datetime.fromisoformat(u.get("created_at").replace('Z', '+00:00')) > week_ago
                    ][:20]
                elif "admin" in query_lower or "ادمین" in query:
                    results["users"] = [
                        {
                            "id": u.get("id"),
                            "email": u.get("email"),
                            "is_admin": u.get("is_admin")
                        }
                        for u in users
                        if u.get("is_admin")
                    ][:20]
            
            # Search orders
            if "سفارش" in query or "order" in query_lower:
                orders = await self.db.trading_orders.find({}).to_list(length=100)
                
                if "pending" in query_lower or "انتظار" in query:
                    results["orders"] = [
                        {
                            "id": o.get("id"),
                            "user_id": o.get("user_id"),
                            "amount_tmn": o.get("amount_tmn"),
                            "status": o.get("status")
                        }
                        for o in orders
                        if o.get("status") == "pending"
                    ][:20]
            
            # Generate insights
            results["insights"].append({
                "query": query,
                "results_found": len(results["users"]) + len(results["orders"]),
                "suggestion": "نتایج بر اساس کلمات کلیدی فیلتر شده‌اند"
            })
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
    
    async def smart_recommendations(self) -> Dict:
        """Smart Recommendations - AI suggests actions for admin"""
        try:
            recommendations = []
            
            # Get data
            pending_orders = await self.db.trading_orders.find({"status": "pending"}).to_list(length=1000)
            users = await self.db.users.find({}).to_list(length=1000)
            
            # Recommendation 1: Auto-approve low-risk pending orders
            low_risk_pending = [o for o in pending_orders if o.get("amount_tmn", 0) < 5000000]
            if low_risk_pending:
                recommendations.append({
                    "type": "bulk_action",
                    "priority": "medium",
                    "title": "تایید دسته‌جمعی سفارشات کم‌ریسک",
                    "description": f"{len(low_risk_pending)} سفارش زیر ۵ میلیون تومان در انتظار",
                    "action": "auto_approve_orders",
                    "count": len(low_risk_pending)
                })
            
            # Recommendation 2: Contact inactive high-value users
            # (Users with high balance but no recent orders)
            # Simplified for demonstration
            high_balance_users = [u for u in users if u.get("wallet_balance_tmn", 0) > 50000000]
            if high_balance_users:
                recommendations.append({
                    "type": "marketing",
                    "priority": "high",
                    "title": "ارتباط با کاربران دارای موجودی بالا",
                    "description": f"{len(high_balance_users)} کاربر با موجودی بالای ۵۰ میلیون",
                    "action": "send_promotional_message",
                    "count": len(high_balance_users)
                })
            
            # Recommendation 3: Approve ready KYCs
            unverified_users = [u for u in users if u.get("kyc_level", 0) == 0]
            if unverified_users:
                recommendations.append({
                    "type": "kyc_action",
                    "priority": "low",
                    "title": "بررسی درخواست‌های KYC",
                    "description": f"{len(unverified_users)} کاربر بدون تایید KYC",
                    "action": "review_kyc_requests",
                    "count": len(unverified_users)
                })
            
            return {
                "total_recommendations": len(recommendations),
                "high_priority": len([r for r in recommendations if r["priority"] == "high"]),
                "recommendations": recommendations,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def predict_crisis(self) -> Dict:
        """Predictive Crisis Management - Predict and prepare for issues"""
        try:
            warnings = []
            
            # Get recent data
            recent_orders = await self.db.trading_orders.find({}).sort("created_at", -1).to_list(length=1000)
            users = await self.db.users.find({}).to_list(length=1000)
            
            # Warning 1: Sudden spike in orders
            hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_hour_orders = [
                o for o in recent_orders 
                if o.get("created_at") and datetime.fromisoformat(o.get("created_at").replace('Z', '+00:00')) > hour_ago
            ]
            
            if len(recent_hour_orders) > 50:
                warnings.append({
                    "type": "order_spike",
                    "severity": "medium",
                    "description": f"افزایش ناگهانی سفارشات: {len(recent_hour_orders)} سفارش در یک ساعت",
                    "recommendation": "آماده‌باش برای افزایش بار سرور"
                })
            
            # Warning 2: Many pending orders
            pending_count = len([o for o in recent_orders if o.get("status") == "pending"])
            if pending_count > 100:
                warnings.append({
                    "type": "pending_overload",
                    "severity": "high",
                    "description": f"تعداد زیاد سفارشات در انتظار: {pending_count}",
                    "recommendation": "افزایش تیم پشتیبانی برای بررسی سریع‌تر"
                })
            
            # Warning 3: Sudden increase in registrations
            today = datetime.now(timezone.utc).date()
            today_registrations = [
                u for u in users
                if u.get("created_at") and datetime.fromisoformat(u.get("created_at").replace('Z', '+00:00')).date() == today
            ]
            
            if len(today_registrations) > 50:
                warnings.append({
                    "type": "registration_spike",
                    "severity": "low",
                    "description": f"افزایش ثبت‌نام‌ها: {len(today_registrations)} کاربر جدید امروز",
                    "recommendation": "بررسی منبع ترافیک و آماده‌سازی منابع"
                })
            
            return {
                "total_warnings": len(warnings),
                "high_severity": len([w for w in warnings if w["severity"] == "high"]),
                "warnings": warnings,
                "system_health": "good" if len(warnings) < 2 else "needs_attention",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
