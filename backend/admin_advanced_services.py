"""
Advanced Admin Services - Core Infrastructure
Provides comprehensive admin capabilities for the crypto exchange

NOTE: This module is currently NOT IMPORTED in server.py and is UNUSED.
It contains comprehensive admin service implementations that are not currently integrated.
Consider removing or integrating into the main application.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import statistics
import uuid

class AdvancedAdminService:
    """Comprehensive admin service with all advanced features"""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== DASHBOARD & ANALYTICS ====================
    
    async def get_realtime_metrics(self) -> Dict:
        """Get real-time dashboard metrics"""
        try:
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = today_start - timedelta(days=1)
            
            # Active users (logged in last 30 min)
            active_threshold = now - timedelta(minutes=30)
            # In a real system, track last_activity. For now, estimate
            total_users = await self.db.users.count_documents({})
            
            # Today's orders
            today_orders = await self.db.trading_orders.count_documents({
                "created_at": {"$gte": today_start.isoformat()}
            })
            
            # Yesterday's orders
            yesterday_orders = await self.db.trading_orders.count_documents({
                "created_at": {
                    "$gte": yesterday_start.isoformat(),
                    "$lt": today_start.isoformat()
                }
            })
            
            # Today's revenue (assume 0.5% fee)
            today_orders_data = await self.db.trading_orders.find({
                "created_at": {"$gte": today_start.isoformat()},
                "status": "completed"
            }).to_list(length=10000)
            
            today_volume = sum(o.get("amount_tmn", 0) for o in today_orders_data)
            today_revenue = today_volume * 0.005
            
            # Pending actions
            pending_orders = await self.db.trading_orders.count_documents({"status": "pending"})
            pending_kyc = await self.db.users.count_documents({"kyc_status": "pending"})
            pending_deposits = await self.db.deposits.count_documents({"status": "pending"})
            
            # System health
            system_health = "healthy"
            if pending_orders > 100 or pending_kyc > 50:
                system_health = "warning"
            if pending_orders > 500 or pending_kyc > 200:
                system_health = "critical"
            
            return {
                "users_online": max(1, total_users // 20),  # Estimate
                "total_users": total_users,
                "today_orders": today_orders,
                "yesterday_orders": yesterday_orders,
                "order_change": ((today_orders - yesterday_orders) / max(yesterday_orders, 1) * 100) if yesterday_orders > 0 else 0,
                "today_revenue": round(today_revenue, 2),
                "today_volume": round(today_volume, 2),
                "pending_actions": {
                    "orders": pending_orders,
                    "kyc": pending_kyc,
                    "deposits": pending_deposits,
                    "total": pending_orders + pending_kyc + pending_deposits
                },
                "system_health": system_health,
                "timestamp": now.isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_trading_charts(self, days: int = 30) -> Dict:
        """Get trading volume charts"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            orders = await self.db.trading_orders.find({
                "created_at": {"$gte": cutoff.isoformat()}
            }).to_list(length=100000)
            
            # Group by date
            daily_data = {}
            coin_volumes = {}
            
            for order in orders:
                date = order.get("created_at", "")[:10]
                amount = order.get("amount_tmn", 0)
                coin = order.get("coin_symbol", "UNKNOWN")
                
                if date not in daily_data:
                    daily_data[date] = {"volume": 0, "orders": 0}
                daily_data[date]["volume"] += amount
                daily_data[date]["orders"] += 1
                
                if coin not in coin_volumes:
                    coin_volumes[coin] = 0
                coin_volumes[coin] += amount
            
            # Sort by date
            chart_data = [
                {"date": date, "volume": data["volume"], "orders": data["orders"]}
                for date, data in sorted(daily_data.items())
            ]
            
            return {
                "daily_chart": chart_data,
                "coin_distribution": coin_volumes,
                "total_volume": sum(d["volume"] for d in chart_data),
                "total_orders": sum(d["orders"] for d in chart_data),
                "avg_order_size": sum(d["volume"] for d in chart_data) / max(sum(d["orders"] for d in chart_data), 1)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_user_registration_trends(self, days: int = 30) -> Dict:
        """Get user registration trends"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            users = await self.db.users.find({
                "created_at": {"$gte": cutoff.isoformat()}
            }).to_list(length=100000)
            
            daily_registrations = {}
            for user in users:
                date = user.get("created_at", "")[:10]
                if date not in daily_registrations:
                    daily_registrations[date] = 0
                daily_registrations[date] += 1
            
            chart_data = [
                {"date": date, "registrations": count}
                for date, count in sorted(daily_registrations.items())
            ]
            
            return {
                "chart": chart_data,
                "total_new_users": len(users),
                "avg_daily": len(users) / days
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_financial_summary(self) -> Dict:
        """Get comprehensive financial summary"""
        try:
            # Total user balances
            users = await self.db.users.find({}).to_list(length=100000)
            total_user_balance = sum(u.get("wallet_balance_tmn", 0) for u in users)
            
            # Total orders
            all_orders = await self.db.trading_orders.find({}).to_list(length=100000)
            completed_orders = [o for o in all_orders if o.get("status") == "completed"]
            
            total_volume = sum(o.get("amount_tmn", 0) for o in completed_orders)
            total_fees = total_volume * 0.005  # 0.5% fee
            
            # Deposits vs Withdrawals
            deposits = await self.db.deposits.find({"status": "approved"}).to_list(length=100000)
            total_deposits = sum(d.get("amount", 0) for d in deposits)
            
            # TODO: Add withdrawals collection
            total_withdrawals = 0
            
            return {
                "total_platform_balance_tmn": round(total_user_balance, 2),
                "total_trading_volume": round(total_volume, 2),
                "total_fees_collected": round(total_fees, 2),
                "total_deposits": round(total_deposits, 2),
                "total_withdrawals": round(total_withdrawals, 2),
                "net_flow": round(total_deposits - total_withdrawals, 2),
                "total_orders": len(all_orders),
                "completed_orders": len(completed_orders),
                "completion_rate": (len(completed_orders) / max(len(all_orders), 1) * 100)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== AUDIT LOGGING ====================
    
    async def log_admin_action(
        self,
        admin_id: str,
        admin_email: str,
        action: str,
        target_type: str,
        target_id: str,
        details: Dict,
        ip_address: Optional[str] = None
    ) -> Dict:
        """Log admin action for audit trail"""
        try:
            log_entry = {
                "id": str(uuid.uuid4()),
                "admin_id": admin_id,
                "admin_email": admin_email,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
                "details": details,
                "ip_address": ip_address,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.admin_audit_logs.insert_one(log_entry)
            
            return {"success": True, "log_id": log_entry["id"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_audit_logs(
        self,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """Get audit logs with filters"""
        try:
            query = {}
            
            if admin_id:
                query["admin_id"] = admin_id
            
            if action:
                query["action"] = action
            
            if days:
                cutoff = datetime.now(timezone.utc) - timedelta(days=days)
                query["timestamp"] = {"$gte": cutoff.isoformat()}
            
            logs = await self.db.admin_audit_logs.find(query).sort("timestamp", -1).to_list(length=limit)
            
            return logs
        except Exception as e:
            return []
    
    # ==================== BULK OPERATIONS ====================
    
    async def bulk_approve_kyc(self, user_ids: List[str], admin_id: str, admin_email: str) -> Dict:
        """Bulk approve KYC for multiple users"""
        try:
            result = await self.db.users.update_many(
                {"id": {"$in": user_ids}},
                {
                    "$set": {
                        "kyc_status": "approved",
                        "kyc_approved_at": datetime.now(timezone.utc).isoformat(),
                        "kyc_approved_by": admin_id
                    }
                }
            )
            
            # Log action
            await self.log_admin_action(
                admin_id,
                admin_email,
                "bulk_approve_kyc",
                "users",
                ",".join(user_ids),
                {"count": len(user_ids)},
                None
            )
            
            return {
                "success": True,
                "modified_count": result.modified_count,
                "message": f"{result.modified_count} کاربر تایید شدند"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def bulk_approve_orders(self, order_ids: List[str], admin_id: str, admin_email: str) -> Dict:
        """Bulk approve orders"""
        try:
            result = await self.db.trading_orders.update_many(
                {"id": {"$in": order_ids}},
                {
                    "$set": {
                        "status": "approved",
                        "approved_at": datetime.now(timezone.utc).isoformat(),
                        "approved_by": admin_id
                    }
                }
            )
            
            await self.log_admin_action(
                admin_id,
                admin_email,
                "bulk_approve_orders",
                "orders",
                ",".join(order_ids),
                {"count": len(order_ids)},
                None
            )
            
            return {
                "success": True,
                "modified_count": result.modified_count,
                "message": f"{result.modified_count} سفارش تایید شد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def bulk_send_message(
        self,
        user_ids: List[str],
        message: str,
        admin_id: str,
        admin_email: str
    ) -> Dict:
        """Send message to multiple users"""
        try:
            # Create notifications for users
            notifications = []
            for user_id in user_ids:
                notifications.append({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "message": message,
                    "type": "admin_message",
                    "read": False,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            
            if notifications:
                await self.db.notifications.insert_many(notifications)
            
            await self.log_admin_action(
                admin_id,
                admin_email,
                "bulk_send_message",
                "users",
                ",".join(user_ids),
                {"count": len(user_ids), "message": message},
                None
            )
            
            return {
                "success": True,
                "sent_count": len(notifications),
                "message": f"پیام به {len(notifications)} کاربر ارسال شد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== USER ACTIVITY TIMELINE ====================
    
    async def get_user_timeline(self, user_id: str) -> List[Dict]:
        """Get complete user activity timeline"""
        try:
            timeline = []
            
            # Get user
            user = await self.db.users.find_one({"id": user_id})
            if user:
                timeline.append({
                    "type": "registration",
                    "timestamp": user.get("created_at"),
                    "description": "ثبت‌نام در سیستم",
                    "icon": "👤"
                })
            
            # Get orders
            orders = await self.db.trading_orders.find({"user_id": user_id}).sort("created_at", -1).to_list(length=100)
            for order in orders:
                timeline.append({
                    "type": "order",
                    "timestamp": order.get("created_at"),
                    "description": f"سفارش {order.get('order_type')} {order.get('coin_symbol')} - {order.get('amount_tmn'):,.0f} تومان",
                    "status": order.get("status"),
                    "icon": "🛒"
                })
            
            # Get deposits
            deposits = await self.db.deposits.find({"user_id": user_id}).sort("created_at", -1).to_list(length=100)
            for deposit in deposits:
                timeline.append({
                    "type": "deposit",
                    "timestamp": deposit.get("created_at"),
                    "description": f"واریز {deposit.get('amount'):,.0f} تومان",
                    "status": deposit.get("status"),
                    "icon": "💰"
                })
            
            # Sort by timestamp
            timeline.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return timeline[:50]  # Last 50 activities
        except Exception as e:
            return []
    
    # ==================== ADVANCED USER FILTERS ====================
    
    async def search_users_advanced(self, filters: Dict) -> List[Dict]:
        """Advanced user search with multiple filters"""
        try:
            query = {}
            
            # Email search
            if filters.get("email"):
                query["email"] = {"$regex": filters["email"], "$options": "i"}
            
            # Phone search
            if filters.get("phone"):
                query["phone"] = {"$regex": filters["phone"]}
            
            # National ID search
            if filters.get("national_id"):
                query["national_id"] = filters["national_id"]
            
            # KYC level filter
            if filters.get("kyc_level") is not None:
                query["kyc_level"] = filters["kyc_level"]
            
            # Registration date range
            if filters.get("registered_from"):
                if "created_at" not in query:
                    query["created_at"] = {}
                query["created_at"]["$gte"] = filters["registered_from"]
            
            if filters.get("registered_to"):
                if "created_at" not in query:
                    query["created_at"] = {}
                query["created_at"]["$lte"] = filters["registered_to"]
            
            # Balance range
            if filters.get("min_balance"):
                query["wallet_balance_tmn"] = {"$gte": filters["min_balance"]}
            
            if filters.get("max_balance"):
                if "wallet_balance_tmn" not in query:
                    query["wallet_balance_tmn"] = {}
                query["wallet_balance_tmn"]["$lte"] = filters["max_balance"]
            
            # Is admin filter
            if filters.get("is_admin") is not None:
                query["is_admin"] = filters["is_admin"]
            
            users = await self.db.users.find(query).to_list(length=1000)
            
            return users
        except Exception as e:
            return []
    
    # ==================== USER TAGGING & NOTES ====================
    
    async def add_user_tag(self, user_id: str, tag: str, admin_id: str) -> Dict:
        """Add tag to user"""
        try:
            result = await self.db.users.update_one(
                {"id": user_id},
                {"$addToSet": {"tags": tag}}
            )
            
            return {
                "success": True,
                "message": f"تگ '{tag}' اضافه شد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_user_note(
        self,
        user_id: str,
        note: str,
        admin_id: str,
        admin_email: str
    ) -> Dict:
        """Add internal note to user"""
        try:
            note_entry = {
                "id": str(uuid.uuid4()),
                "note": note,
                "admin_id": admin_id,
                "admin_email": admin_email,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = await self.db.users.update_one(
                {"id": user_id},
                {"$push": {"admin_notes": note_entry}}
            )
            
            return {
                "success": True,
                "message": "یادداشت اضافه شد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== BALANCE ADJUSTMENT ====================
    
    async def adjust_user_balance(
        self,
        user_id: str,
        amount: float,
        reason: str,
        admin_id: str,
        admin_email: str
    ) -> Dict:
        """Manually adjust user balance"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                return {"success": False, "error": "کاربر یافت نشد"}
            
            old_balance = user.get("wallet_balance_tmn", 0)
            new_balance = old_balance + amount
            
            # Update balance
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"wallet_balance_tmn": new_balance}}
            )
            
            # Log transaction
            await self.db.balance_adjustments.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "amount": amount,
                "reason": reason,
                "admin_id": admin_id,
                "admin_email": admin_email,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Audit log
            await self.log_admin_action(
                admin_id,
                admin_email,
                "adjust_balance",
                "user",
                user_id,
                {"amount": amount, "reason": reason, "old": old_balance, "new": new_balance},
                None
            )
            
            return {
                "success": True,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "message": f"موجودی از {old_balance:,.0f} به {new_balance:,.0f} تغییر کرد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== FEE MANAGEMENT ====================
    
    async def get_fee_settings(self) -> Dict:
        """Get current fee settings"""
        try:
            settings = await self.db.system_settings.find_one({"type": "fee_config"})
            
            if not settings:
                return {
                    "default_fee_percent": 0.5,
                    "vip_fee_percent": 0.3,
                    "tiered_fees": {
                        "0-10000000": 0.7,
                        "10000000-100000000": 0.5,
                        "100000000+": 0.3
                    }
                }
            
            return settings
        except Exception as e:
            return {"error": str(e)}
    
    async def update_fee_settings(self, fee_config: Dict, admin_id: str, admin_email: str) -> Dict:
        """Update fee settings"""
        try:
            await self.db.system_settings.update_one(
                {"type": "fee_config"},
                {
                    "$set": {
                        **fee_config,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "updated_by": admin_id
                    }
                },
                upsert=True
            )
            
            await self.log_admin_action(
                admin_id,
                admin_email,
                "update_fee_settings",
                "system",
                "fee_config",
                fee_config,
                None
            )
            
            return {"success": True, "message": "تنظیمات کارمزد به‌روزرسانی شد"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Singleton
advanced_admin_service = None

def get_advanced_admin_service(db):
    global advanced_admin_service
    if advanced_admin_service is None:
        advanced_admin_service = AdvancedAdminService(db)
    return advanced_admin_service
