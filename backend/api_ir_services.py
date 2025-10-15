"""
API.IR Integration Service for KYC Verification
Provides comprehensive KYC services using API.IR:
- CheckEmail: Email verification
- SmsOTP: Phone verification via SMS
- Call OTP: Phone verification via voice call
- Shahkar: National ID + Mobile verification (Iranian service)
- CardMatch: Bank card verification
"""
import os
import aiohttp
import logging
from typing import Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class APIRService:
    """API.IR Service for KYC verification"""
    
    def __init__(self):
        self.token = os.getenv("APIR_TOKEN", "")
        self.base_url = os.getenv("APIR_BASE_URL", "https://api.api.ir/api")
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, endpoint: str, method: str = "POST", data: Dict = None) -> Dict:
        """Make HTTP request to API.IR"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == "POST":
                    async with session.post(url, headers=self.headers, json=data, timeout=30) as response:
                        result = await response.json()
                        logger.info(f"API.IR {endpoint} response: {result}")
                        return result
                elif method == "GET":
                    async with session.get(url, headers=self.headers, timeout=30) as response:
                        result = await response.json()
                        return result
                        
        except aiohttp.ClientError as e:
            logger.error(f"API.IR request failed: {str(e)}")
            return {"success": False, "error": f"خطا در ارتباط با سرور: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in API.IR request: {str(e)}")
            return {"success": False, "error": f"خطای غیرمنتظره: {str(e)}"}
    
    # ==================== EMAIL VERIFICATION ====================
    
    async def check_email(self, email: str) -> Dict:
        """
        Verify email address validity
        
        Args:
            email: Email address to verify
            
        Returns:
            {
                "success": bool,
                "valid": bool,
                "message": str,
                "details": {
                    "exists": bool,
                    "deliverable": bool,
                    "syntax_valid": bool
                }
            }
        """
        try:
            endpoint = "/sw1/CheckEmail"
            data = {"email": email}
            
            result = await self._make_request(endpoint, "POST", data)
            
            # API.IR response format (expected)
            if result.get("success"):
                return {
                    "success": True,
                    "valid": True,
                    "message": "ایمیل معتبر است",
                    "details": result.get("data", {}),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "message": result.get("error", "ایمیل نامعتبر است"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"CheckEmail error: {str(e)}")
            return {
                "success": False,
                "valid": False,
                "message": f"خطا در بررسی ایمیل: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # ==================== SMS OTP ====================
    
    async def send_sms_otp(self, mobile: str, code: str, template: int = 1) -> Dict:
        """
        Send OTP via SMS
        
        Args:
            mobile: Mobile number (11 digits, starting with 09)
            code: OTP code (4-10 digits)
            template: Message template type (1=Code, 2=Login Code, etc.)
            
        Returns:
            {
                "success": bool,
                "message": str,
                "sent_at": str
            }
        """
        try:
            # Validate mobile format
            if not mobile.startswith("09") or len(mobile) != 11:
                return {
                    "success": False,
                    "message": "شماره موبایل باید با 09 شروع شده و 11 رقم باشد",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Validate OTP code
            if not (4 <= len(code) <= 10) or not code.isdigit():
                return {
                    "success": False,
                    "message": "کد OTP باید بین 4 تا 10 رقم باشد",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            endpoint = "/sw1/SmsOTP"
            data = {
                "code": code,
                "mobile": mobile,
                "template": template
            }
            
            result = await self._make_request(endpoint, "POST", data)
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": "کد تایید با موفقیت ارسال شد",
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "mobile": mobile
                }
            else:
                return {
                    "success": False,
                    "message": result.get("error", "خطا در ارسال پیامک"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Send SMS OTP error: {str(e)}")
            return {
                "success": False,
                "message": f"خطا در ارسال پیامک: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # ==================== CALL OTP ====================
    
    async def send_call_otp(self, phone: str, code: str) -> Dict:
        """
        Send OTP via voice call
        
        Args:
            phone: Phone number (mobile or landline)
            code: OTP code (4-10 digits)
            
        Returns:
            {
                "success": bool,
                "message": str,
                "sent_at": str
            }
        """
        try:
            # Validate OTP code
            if not (4 <= len(code) <= 10) or not code.isdigit():
                return {
                    "success": False,
                    "message": "کد OTP باید بین 4 تا 10 رقم باشد",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            endpoint = "/sw1/CallOTP"
            data = {
                "code": code,
                "phone_number": phone
            }
            
            result = await self._make_request(endpoint, "POST", data)
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": "تماس صوتی با موفقیت برقرار شد",
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "phone": phone
                }
            else:
                return {
                    "success": False,
                    "message": result.get("error", "خطا در برقراری تماس"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Send Call OTP error: {str(e)}")
            return {
                "success": False,
                "message": f"خطا در برقراری تماس: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # ==================== SHAHKAR (National ID + Mobile Verification) ====================
    
    async def verify_shahkar(self, national_id: str, mobile: str, birthdate: str) -> Dict:
        """
        Verify mobile number matches national ID (Shahkar service)
        This is a crucial KYC step for Iranian users
        
        Args:
            national_id: Iranian national ID number (10 digits)
            mobile: Mobile number (11 digits, starting with 09)
            birthdate: Birth date in format YYYY-MM-DD
            
        Returns:
            {
                "success": bool,
                "verified": bool,
                "message": str,
                "match_score": int (0-100)
            }
        """
        try:
            # Validate national ID
            if not national_id.isdigit() or len(national_id) != 10:
                return {
                    "success": False,
                    "verified": False,
                    "message": "کد ملی باید 10 رقم باشد",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Validate mobile
            if not mobile.startswith("09") or len(mobile) != 11:
                return {
                    "success": False,
                    "verified": False,
                    "message": "شماره موبایل نامعتبر است",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            endpoint = "/sw1/Shahkar2"
            data = {
                "national_id": national_id,
                "mobile": mobile,
                "birthdate": birthdate
            }
            
            result = await self._make_request(endpoint, "POST", data)
            
            if result.get("success"):
                # Shahkar verification successful
                verified = result.get("data", {}).get("verified", False)
                match_score = result.get("data", {}).get("match_score", 0)
                
                return {
                    "success": True,
                    "verified": verified,
                    "message": "شماره موبایل با کد ملی تطابق دارد" if verified else "شماره موبایل با کد ملی مطابقت ندارد",
                    "match_score": match_score,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "message": result.get("error", "خطا در بررسی شاهکار"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Shahkar verification error: {str(e)}")
            return {
                "success": False,
                "verified": False,
                "message": f"خطا در بررسی شاهکار: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # ==================== CARD MATCH (Bank Card Verification) ====================
    
    async def verify_card_match(
        self,
        card_number: str,
        national_id: str,
        birthdate: str,
        full_name: Optional[str] = None
    ) -> Dict:
        """
        Verify bank card matches user identity
        
        Args:
            card_number: Bank card number (16 digits)
            national_id: Iranian national ID (10 digits)
            birthdate: Birth date in format YYYY-MM-DD
            full_name: User's full name (optional)
            
        Returns:
            {
                "success": bool,
                "verified": bool,
                "message": str,
                "bank_name": str (optional)
            }
        """
        try:
            # Validate card number
            card_clean = card_number.replace("-", "").replace(" ", "")
            if not card_clean.isdigit() or len(card_clean) != 16:
                return {
                    "success": False,
                    "verified": False,
                    "message": "شماره کارت باید 16 رقم باشد",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Validate national ID
            if not national_id.isdigit() or len(national_id) != 10:
                return {
                    "success": False,
                    "verified": False,
                    "message": "کد ملی باید 10 رقم باشد",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            endpoint = "/sw1/CardMatch"
            data = {
                "card_number": card_clean,
                "national_id": national_id,
                "birthdate": birthdate
            }
            
            if full_name:
                data["full_name"] = full_name
            
            result = await self._make_request(endpoint, "POST", data)
            
            if result.get("success"):
                verified = result.get("data", {}).get("verified", False)
                bank_name = result.get("data", {}).get("bank_name", "")
                
                return {
                    "success": True,
                    "verified": verified,
                    "message": "کارت بانکی تایید شد" if verified else "کارت بانکی تطابق ندارد",
                    "bank_name": bank_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "message": result.get("error", "خطا در بررسی کارت بانکی"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Card match verification error: {str(e)}")
            return {
                "success": False,
                "verified": False,
                "message": f"خطا در بررسی کارت: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # ==================== HELPER METHODS ====================
    
    def is_configured(self) -> bool:
        """Check if API.IR is properly configured"""
        return bool(self.token and self.token.startswith("Bearer"))
    
    async def test_connection(self) -> Dict:
        """Test API.IR connection"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "message": "API.IR توکن پیکربندی نشده است",
                    "configured": False
                }
            
            # Try a simple email check as connection test
            result = await self.check_email("test@example.com")
            
            return {
                "success": True,
                "message": "ارتباط با API.IR برقرار است",
                "configured": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"خطا در ارتباط با API.IR: {str(e)}",
                "configured": False
            }

# Singleton instance
api_ir_service = APIRService()
