"""
Admin Communication & Security Services
Handles announcements, notifications, support tickets, fraud detection

NOTE: This module is currently NOT IMPORTED in server.py and is UNUSED.
It contains communication service implementations that are not currently integrated.
Consider removing or integrating into the main application.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import uuid

class CommunicationService:
    """Handle in-app communications, announcements, support tickets"""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== ANNOUNCEMENTS ====================
    
    async def create_announcement(
        self,
        title: str,
        message: str,
        announcement_type: str,  # banner, popup, email
        target_audience: str,  # all, kyc_level_0, kyc_level_1, etc.
        expires_at: Optional[str] = None,
        admin_id: str = None,
        admin_email: str = None
    ) -> Dict:
        """Create system-wide announcement"""
        try:
            announcement = {
                "id": str(uuid.uuid4()),
                "title": title,
                "message": message,
                "type": announcement_type,
                "target_audience": target_audience,
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expires_at,
                "created_by": admin_id,
                "created_by_email": admin_email,
                "views": 0,
                "clicks": 0
            }
            
            await self.db.announcements.insert_one(announcement)
            
            return {
                "success": True,
                "announcement_id": announcement["id"],
                "message": "اعلان ایجاد شد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_active_announcements(self, user_kyc_level: int = None) -> List[Dict]:
        """Get active announcements for user"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            query = {
                "active": True,
                "$or": [
                    {"expires_at": None},
                    {"expires_at": {"$gt": now}}
                ]
            }
            
            # Filter by target audience
            if user_kyc_level is not None:
                query["$or"] = [
                    {"target_audience": "all"},
                    {"target_audience": f"kyc_level_{user_kyc_level}"}
                ]
            
            announcements = await self.db.announcements.find(query).sort("created_at", -1).to_list(length=10)
            
            return announcements
        except Exception as e:
            return []
    
    async def delete_announcement(self, announcement_id: str) -> Dict:
        """Delete or deactivate announcement"""
        try:
            await self.db.announcements.update_one(
                {"id": announcement_id},
                {"$set": {"active": False}}
            )
            
            return {"success": True, "message": "اعلان غیرفعال شد"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== SUPPORT TICKETS ====================
    
    async def create_support_ticket(
        self,
        user_id: str,
        subject: str,
        message: str,
        category: str = "general",
        priority: str = "medium"
    ) -> Dict:
        """Create support ticket"""
        try:
            ticket = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "subject": subject,
                "category": category,
                "priority": priority,
                "status": "open",
                "messages": [{
                    "id": str(uuid.uuid4()),
                    "from": "user",
                    "message": message,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }],
                "assigned_to": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.support_tickets.insert_one(ticket)
            
            return {
                "success": True,
                "ticket_id": ticket["id"],
                "message": "تیکت پشتیبانی ایجاد شد"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_support_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get support tickets with filters"""
        try:
            query = {}
            
            if status:
                query["status"] = status
            if priority:
                query["priority"] = priority
            if assigned_to:
                query["assigned_to"] = assigned_to
            
            tickets = await self.db.support_tickets.find(query).sort("created_at", -1).to_list(length=limit)
            
            return tickets
        except Exception as e:
            return []
    
    async def reply_to_ticket(
        self,
        ticket_id: str,
        message: str,
        admin_id: str,
        admin_email: str
    ) -> Dict:
        """Admin reply to support ticket"""
        try:
            reply = {
                "id": str(uuid.uuid4()),
                "from": "admin",
                "admin_id": admin_id,
                "admin_email": admin_email,
                "message": message,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.support_tickets.update_one(
                {"id": ticket_id},
                {
                    "$push": {"messages": reply},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            
            return {"success": True, "message": "پاسخ ارسال شد"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close_ticket(self, ticket_id: str, admin_id: str) -> Dict:
        """Close support ticket"""
        try:
            await self.db.support_tickets.update_one(
                {"id": ticket_id},
                {
                    "$set": {
                        "status": "closed",
                        "closed_at": datetime.now(timezone.utc).isoformat(),
                        "closed_by": admin_id
                    }
                }
            )
            
            return {"success": True, "message": "تیکت بسته شد"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== NOTIFICATIONS ====================
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info"
    ) -> Dict:
        """Send notification to user"""
        try:
            notification = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.notifications.insert_one(notification)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}


class SecurityService:
    """Handle security features - fraud detection, IP management, etc."""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== IP MANAGEMENT ====================
    
    async def add_to_blacklist(self, ip_address: str, reason: str, admin_id: str) -> Dict:
        """Add IP to blacklist"""
        try:
            entry = {
                "id": str(uuid.uuid4()),
                "ip_address": ip_address,
                "reason": reason,
                "type": "blacklist",
                "added_by": admin_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.ip_management.insert_one(entry)
            
            return {"success": True, "message": f"IP {ip_address} به لیست سیاه اضافه شد"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_to_whitelist(self, ip_address: str, reason: str, admin_id: str) -> Dict:
        """Add IP to whitelist"""
        try:
            entry = {
                "id": str(uuid.uuid4()),
                "ip_address": ip_address,
                "reason": reason,
                "type": "whitelist",
                "added_by": admin_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.ip_management.insert_one(entry)
            
            return {"success": True, "message": f"IP {ip_address} به لیست سفید اضافه شد"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_ip_status(self, ip_address: str) -> Dict:
        """Check if IP is blacklisted or whitelisted"""
        try:
            blacklist = await self.db.ip_management.find_one({
                "ip_address": ip_address,
                "type": "blacklist"
            })
            
            whitelist = await self.db.ip_management.find_one({
                "ip_address": ip_address,
                "type": "whitelist"
            })
            
            return {
                "blacklisted": bool(blacklist),
                "whitelisted": bool(whitelist),
                "status": "blacklisted" if blacklist else "whitelisted" if whitelist else "normal"
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== FRAUD DETECTION ====================
    
    async def detect_multiple_accounts(self) -> List[Dict]:
        """Detect users with multiple accounts (same IP, phone, etc.)"""
        try:
            # Group users by phone
            users = await self.db.users.find({}).to_list(length=100000)
            
            phone_groups = {}
            for user in users:
                phone = user.get("phone")
                if phone:
                    if phone not in phone_groups:
                        phone_groups[phone] = []
                    phone_groups[phone].append(user)
            
            # Find duplicates
            duplicates = []
            for phone, users_list in phone_groups.items():
                if len(users_list) > 1:
                    duplicates.append({
                        "phone": phone,
                        "users": [{"id": u.get("id"), "email": u.get("email")} for u in users_list],
                        "count": len(users_list)
                    })
            
            return duplicates
        except Exception as e:
            return []
    
    async def detect_suspicious_transactions(self, hours: int = 24) -> List[Dict]:
        """Detect suspicious transaction patterns"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            orders = await self.db.trading_orders.find({
                "created_at": {"$gte": cutoff.isoformat()}
            }).to_list(length=10000)
            
            # Group by user
            user_orders = {}
            for order in orders:
                user_id = order.get("user_id")
                if user_id not in user_orders:
                    user_orders[user_id] = []
                user_orders[user_id].append(order)
            
            suspicious = []
            for user_id, orders_list in user_orders.items():
                # Rapid fire orders
                if len(orders_list) > 20:
                    suspicious.append({
                        "user_id": user_id,
                        "reason": "rapid_orders",
                        "count": len(orders_list),
                        "description": f"{len(orders_list)} سفارش در {hours} ساعت"
                    })
                
                # Large volume
                total_volume = sum(o.get("amount_tmn", 0) for o in orders_list)
                if total_volume > 1000000000:  # 1B Toman
                    suspicious.append({
                        "user_id": user_id,
                        "reason": "high_volume",
                        "volume": total_volume,
                        "description": f"حجم معاملات بالا: {total_volume:,.0f} تومان"
                    })
            
            return suspicious
        except Exception as e:
            return []


class ReportingService:
    """Generate various reports"""
    
    def __init__(self, db):
        self.db = db
    
    async def generate_kyc_report(self) -> Dict:
        """Generate KYC status report"""
        try:
            users = await self.db.users.find({}).to_list(length=100000)
            
            kyc_stats = {
                "level_0": 0,
                "level_1": 0,
                "level_2": 0,
                "level_3": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0
            }
            
            for user in users:
                level = user.get("kyc_level", 0)
                kyc_stats[f"level_{level}"] = kyc_stats.get(f"level_{level}", 0) + 1
                
                status = user.get("kyc_status", "pending")
                kyc_stats[status] = kyc_stats.get(status, 0) + 1
            
            return kyc_stats
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_transaction_report(self, days: int = 30) -> Dict:
        """Generate transaction report"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            
            orders = await self.db.trading_orders.find({
                "created_at": {"$gte": cutoff.isoformat()}
            }).to_list(length=100000)
            
            deposits = await self.db.deposits.find({
                "created_at": {"$gte": cutoff.isoformat()}
            }).to_list(length=100000)
            
            report = {
                "period_days": days,
                "orders": {
                    "total": len(orders),
                    "pending": len([o for o in orders if o.get("status") == "pending"]),
                    "completed": len([o for o in orders if o.get("status") == "completed"]),
                    "rejected": len([o for o in orders if o.get("status") == "rejected"]),
                    "total_volume": sum(o.get("amount_tmn", 0) for o in orders)
                },
                "deposits": {
                    "total": len(deposits),
                    "pending": len([d for d in deposits if d.get("status") == "pending"]),
                    "approved": len([d for d in deposits if d.get("status") == "approved"]),
                    "rejected": len([d for d in deposits if d.get("status") == "rejected"]),
                    "total_amount": sum(d.get("amount", 0) for d in deposits)
                }
            }
            
            return report
        except Exception as e:
            return {"error": str(e)}

# Singletons
communication_service = None
security_service = None
reporting_service = None

def get_communication_service(db):
    global communication_service
    if communication_service is None:
        communication_service = CommunicationService(db)
    return communication_service

def get_security_service(db):
    global security_service
    if security_service is None:
        security_service = SecurityService(db)
    return security_service

def get_reporting_service(db):
    global reporting_service
    if reporting_service is None:
        reporting_service = ReportingService(db)
    return reporting_service
