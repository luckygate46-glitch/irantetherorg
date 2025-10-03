from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import httpx
import random
from ai_services import chatbot, market_analyst, portfolio_advisor, price_predictor, risk_analyzer, news_summarizer
from crypto_prices import price_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'persian-crypto-exchange-secret-key-2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# API.IR Configuration
APIR_BASE_URL = "https://s.api.ir/api"
APIR_API_KEY = "Bearer hEDOyeYLEalDw/zGbLnyZ3V4XrsFA8+57LaeB2dJYovHDMybuxE3bTMBvC0FPaPAZRG34SOttlW19ItO6fuNql/6xJ4ajwIRuFfthX1hG88="

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str  # Mandatory for OTP
    password: str
    
    @validator('first_name')
    def validate_first_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('نام باید حداقل 2 کاراکتر باشد')
        return v.strip()
    
    @validator('last_name')
    def validate_last_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('نام خانوادگی باید حداقل 2 کاراکتر باشد')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('رمز عبور باید حداقل 6 کاراکتر باشد')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('09') or len(v) != 11:
            raise ValueError('شماره موبایل باید با 09 شروع شود و 11 رقم باشد')
        return v

class UserLogin(BaseModel):
    email: str  # Can be email or username
    password: str

class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    full_name: Optional[str] = None  # Computed from first_name + last_name
    national_code: Optional[str] = None
    is_active: bool
    is_phone_verified: bool
    kyc_level: int
    kyc_status: str
    is_admin: bool
    wallet_balance_tmn: float
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    email: str
    password_hash: str
    phone: str
    full_name: Optional[str] = None  # Added in KYC Level 1 (can override computed name)
    national_code: Optional[str] = None  # Added in KYC Level 1
    birth_date: Optional[str] = None  # Added in KYC Level 1
    bank_card_number: Optional[str] = None  # Added in KYC Level 1
    is_active: bool = True
    is_phone_verified: bool = False  # Phone OTP verified
    kyc_level: int = 0  # 0=registered, 1=basic KYC, 2=advanced KYC
    kyc_status: str = "pending"  # pending, approved, rejected
    kyc_documents: Optional[dict] = None  # ID photo, selfie/video
    is_admin: bool = False
    wallet_balance_tmn: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CardNumber(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_number: str
    cardholder_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CardNumberCreate(BaseModel):
    card_number: str
    cardholder_name: str

class CardNumberResponse(BaseModel):
    id: str
    card_number: str
    cardholder_name: str
    is_active: bool
    created_at: datetime

class DepositRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    card_number: str
    transaction_id: Optional[str] = None
    receipt_image: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected
    admin_note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DepositRequestCreate(BaseModel):
    amount: float
    card_number: str
    transaction_id: Optional[str] = None
    receipt_image: Optional[str] = None

class DepositRequestResponse(BaseModel):
    id: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    amount: float
    card_number: str
    transaction_id: Optional[str] = None
    receipt_image: Optional[str] = None
    status: str
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DepositApproval(BaseModel):
    deposit_id: str
    action: str  # approve or reject
    admin_note: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    wallet_balance_tmn: Optional[float] = None

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_deposits: float
    pending_deposits: int
    total_cards: int

class SendOTPRequest(BaseModel):
    phone: str
    
class VerifyOTPRequest(BaseModel):
    phone: str
    code: str

class OTPVerification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone: str
    code: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
    verified: bool = False

class KYCLevel1Request(BaseModel):
    full_name: str
    national_code: str
    birth_date: str  # Format: 1370/05/15
    bank_card_number: str
    
    @validator('national_code')
    def validate_national_code(cls, v):
        if len(v) != 10:
            raise ValueError('کد ملی باید 10 رقم باشد')
        return v
    
    @validator('bank_card_number')
    def validate_card(cls, v):
        # Remove spaces and dashes
        v = v.replace(' ', '').replace('-', '')
        if len(v) != 16:
            raise ValueError('شماره کارت باید 16 رقم باشد')
        return v

class KYCLevel2Request(BaseModel):
    id_card_photo: str  # Base64 or URL
    selfie_type: str  # "photo" or "video"
    selfie_data: str  # Base64 or URL

class KYCApprovalRequest(BaseModel):
    user_id: str
    kyc_level: int  # 1 or 2
    action: str  # "approve" or "reject"
    admin_note: Optional[str] = None

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="توکن نامعتبر است")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="توکن منقضی شده است")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="توکن نامعتبر است")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="کاربر یافت نشد")
    return User(**user)

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="دسترسی مجاز نیست - فقط ادمین")
    return current_user

def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        national_code=user.national_code,
        is_active=user.is_active,
        is_phone_verified=user.is_phone_verified,
        kyc_level=user.kyc_level,
        kyc_status=user.kyc_status,
        is_admin=user.is_admin,
        wallet_balance_tmn=user.wallet_balance_tmn,
        created_at=user.created_at
    )

# ==================== API.IR INTEGRATION ====================

async def send_sms_otp_apir(phone: str, code: str) -> bool:
    """Send OTP via API.IR SMS service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{APIR_BASE_URL}/sw1/SmsOTP",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/plain",
                    "Authorization": APIR_API_KEY
                },
                json={"code": code, "mobile": phone},
                timeout=10.0
            )
            data = response.json()
            return data.get("success", False)
    except Exception as e:
        logger.error(f"API.IR SMS OTP Error: {str(e)}")
        return False

async def verify_shahkar(national_code: str, mobile: str, is_company: bool = False) -> dict:
    """Verify national code with mobile number using Shahkar"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{APIR_BASE_URL}/sw1/Shahkar",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/plain",
                    "Authorization": APIR_API_KEY
                },
                json={
                    "nationalCode": national_code,
                    "mobile": mobile,
                    "isCompany": is_company
                },
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"API.IR Shahkar Error: {str(e)}")
        return {"success": False, "error": str(e)}

async def verify_card_match(national_code: str, birth_date: str, card_number: str) -> dict:
    """Verify card belongs to user"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{APIR_BASE_URL}/sw1/CardMatch",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/plain",
                    "Authorization": APIR_API_KEY
                },
                json={
                    "nationalCode": national_code,
                    "birthDate": birth_date,
                    "cardNumber": card_number
                },
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"API.IR CardMatch Error: {str(e)}")
        return {"success": False, "error": str(e)}

async def get_card_info(card_number: str) -> dict:
    """Get card owner name"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{APIR_BASE_URL}/sw1/CardInfo",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/plain",
                    "Authorization": APIR_API_KEY
                },
                json={"cardNumber": card_number},
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"API.IR CardInfo Error: {str(e)}")
        return {"success": False, "error": str(e)}

# ==================== OTP ROUTES ====================

@api_router.post("/otp/send")
async def send_otp(request: SendOTPRequest):
    """Send OTP code via SMS using API.IR"""
    # Generate 5-digit code
    code = str(random.randint(10000, 99999))
    
    # Send via API.IR
    success = await send_sms_otp_apir(request.phone, code)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="خطا در ارسال پیامک. لطفا دوباره تلاش کنید"
        )
    
    # Store OTP in database
    otp = OTPVerification(phone=request.phone, code=code)
    await db.otp_verifications.insert_one(otp.dict())
    
    return {"success": True, "message": "کد تایید با موفقیت ارسال شد"}

@api_router.post("/otp/verify")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP code"""
    # Find latest OTP for this phone
    otp_data = await db.otp_verifications.find_one(
        {"phone": request.phone, "verified": False},
        sort=[("created_at", -1)]
    )
    
    if not otp_data:
        raise HTTPException(
            status_code=404,
            detail="کد تایید یافت نشد"
        )
    
    otp = OTPVerification(**otp_data)
    
    # Check expiration
    if datetime.now(timezone.utc) > otp.expires_at:
        raise HTTPException(
            status_code=400,
            detail="کد تایید منقضی شده است. کد جدید درخواست کنید"
        )
    
    # Verify code
    if otp.code != request.code:
        raise HTTPException(
            status_code=400,
            detail="کد تایید اشتباه است"
        )
    
    # Mark as verified
    await db.otp_verifications.update_one(
        {"id": otp.id},
        {"$set": {"verified": True}}
    )
    
    return {"success": True, "message": "شماره موبایل تایید شد"}

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است"
        )
    
    # Check if phone already exists
    existing_phone = await db.users.find_one({"phone": user_data.phone})
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این شماره موبایل قبلاً ثبت شده است"
        )
    
    # Check if phone OTP is verified
    otp_verified = await db.otp_verifications.find_one(
        {"phone": user_data.phone, "verified": True}
    )
    
    if not otp_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لطفا ابتدا شماره موبایل خود را تایید کنید"
        )
    
    # Create new user with Level 0 (only phone verified)
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
        is_phone_verified=True,
        kyc_level=0,  # Can only view market
        kyc_status="pending"
    )
    
    await db.users.insert_one(user.dict())
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_to_response(user)
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    # Find user
    user_data = await db.users.find_one({"email": credentials.email})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا رمز عبور اشتباه است"
        )
    
    user = User(**user_data)
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا رمز عبور اشتباه است"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما غیرفعال است"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_to_response(user)
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return user_to_response(current_user)

# ==================== KYC ROUTES ====================

@api_router.post("/kyc/level1")
async def submit_kyc_level1(kyc_data: KYCLevel1Request, current_user: User = Depends(get_current_user)):
    """Submit Level 1 KYC - Basic information and bank card"""
    
    if current_user.kyc_level >= 1:
        raise HTTPException(
            status_code=400,
            detail="شما قبلاً احراز هویت سطح ۱ را تکمیل کرده‌اید"
        )
    
    # Verify with API.IR Shahkar
    shahkar_result = await verify_shahkar(kyc_data.national_code, current_user.phone)
    
    if not shahkar_result.get("success"):
        raise HTTPException(
            status_code=400,
            detail="کد ملی با شماره موبایل مطابقت ندارد (شاهکار)"
        )
    
    # Verify card ownership with API.IR CardMatch
    card_match_result = await verify_card_match(
        kyc_data.national_code,
        kyc_data.birth_date,
        kyc_data.bank_card_number
    )
    
    if not card_match_result.get("success"):
        raise HTTPException(
            status_code=400,
            detail="کارت بانکی متعلق به شما نیست"
        )
    
    # Get card owner name
    card_info = await get_card_info(kyc_data.bank_card_number)
    card_owner_name = card_info.get("data", {}).get("name", "")
    
    # Update user with KYC Level 1 data
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "full_name": kyc_data.full_name,
            "national_code": kyc_data.national_code,
            "birth_date": kyc_data.birth_date,
            "bank_card_number": kyc_data.bank_card_number,
            "kyc_level": 1,
            "kyc_status": "approved",  # Auto-approved since Shahkar & CardMatch passed
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {
        "success": True,
        "message": "احراز هویت سطح ۱ با موفقیت انجام شد",
        "kyc_level": 1,
        "card_owner_name": card_owner_name
    }

@api_router.post("/kyc/level2")
async def submit_kyc_level2(kyc_data: KYCLevel2Request, current_user: User = Depends(get_current_user)):
    """Submit Level 2 KYC - Document upload"""
    
    if current_user.kyc_level < 1:
        raise HTTPException(
            status_code=400,
            detail="ابتدا باید احراز هویت سطح ۱ را تکمیل کنید"
        )
    
    if current_user.kyc_level >= 2:
        raise HTTPException(
            status_code=400,
            detail="شما قبلاً احراز هویت سطح ۲ را تکمیل کرده‌اید"
        )
    
    # Store documents
    kyc_documents = {
        "id_card_photo": kyc_data.id_card_photo,
        "selfie_type": kyc_data.selfie_type,
        "selfie_data": kyc_data.selfie_data,
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update user - pending admin approval
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "kyc_documents": kyc_documents,
            "kyc_status": "pending",  # Waiting for admin review
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {
        "success": True,
        "message": "مدارک شما ارسال شد و در انتظار تایید ادمین است (حداکثر ۱ ساعت)",
        "status": "pending"
    }

@api_router.get("/kyc/status")
async def get_kyc_status(current_user: User = Depends(get_current_user)):
    """Get current KYC status"""
    return {
        "kyc_level": current_user.kyc_level,
        "kyc_status": current_user.kyc_status,
        "has_documents": current_user.kyc_documents is not None,
        "full_name": current_user.full_name,
        "national_code": current_user.national_code,
        "bank_card_number": current_user.bank_card_number
    }

# ==================== ADMIN ROUTES ====================

@api_router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(admin: User = Depends(get_current_admin)):
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    
    # Calculate total deposits
    deposits = await db.deposit_requests.find({"status": "approved"}).to_list(None)
    total_deposits = sum([d.get("amount", 0) for d in deposits])
    
    pending_deposits = await db.deposit_requests.count_documents({"status": "pending"})
    total_cards = await db.card_numbers.count_documents({"is_active": True})
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_deposits=total_deposits,
        pending_deposits=pending_deposits,
        total_cards=total_cards
    )

@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(admin: User = Depends(get_current_admin)):
    users = await db.users.find().to_list(None)
    return [user_to_response(User(**user)) for user in users]

@api_router.put("/admin/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate, admin: User = Depends(get_current_admin)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user_id})
    return user_to_response(User(**updated_user))

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, admin: User = Depends(get_current_admin)):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    return {"message": "کاربر با موفقیت حذف شد"}

# ==================== CARD NUMBER ROUTES ====================

@api_router.get("/cards", response_model=List[CardNumberResponse])
async def get_active_cards():
    cards = await db.card_numbers.find({"is_active": True}).to_list(None)
    return [CardNumberResponse(**card) for card in cards]

@api_router.get("/admin/cards", response_model=List[CardNumberResponse])
async def get_all_cards(admin: User = Depends(get_current_admin)):
    cards = await db.card_numbers.find().to_list(None)
    return [CardNumberResponse(**card) for card in cards]

@api_router.post("/admin/cards", response_model=CardNumberResponse)
async def create_card(card_data: CardNumberCreate, admin: User = Depends(get_current_admin)):
    card = CardNumber(
        card_number=card_data.card_number,
        cardholder_name=card_data.cardholder_name
    )
    await db.card_numbers.insert_one(card.dict())
    return CardNumberResponse(**card.dict())

@api_router.put("/admin/cards/{card_id}")
async def update_card(card_id: str, is_active: bool, admin: User = Depends(get_current_admin)):
    result = await db.card_numbers.update_one(
        {"id": card_id},
        {"$set": {"is_active": is_active}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="کارت یافت نشد")
    
    card = await db.card_numbers.find_one({"id": card_id})
    return CardNumberResponse(**card)

@api_router.delete("/admin/cards/{card_id}")
async def delete_card(card_id: str, admin: User = Depends(get_current_admin)):
    result = await db.card_numbers.delete_one({"id": card_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="کارت یافت نشد")
    return {"message": "کارت با موفقیت حذف شد"}

# ==================== DEPOSIT ROUTES ====================

@api_router.post("/deposits", response_model=DepositRequestResponse)
async def create_deposit_request(deposit_data: DepositRequestCreate, current_user: User = Depends(get_current_user)):
    deposit = DepositRequest(
        user_id=current_user.id,
        amount=deposit_data.amount,
        card_number=deposit_data.card_number,
        transaction_id=deposit_data.transaction_id,
        receipt_image=deposit_data.receipt_image
    )
    await db.deposit_requests.insert_one(deposit.dict())
    
    response_data = deposit.dict()
    response_data["user_email"] = current_user.email
    response_data["user_name"] = current_user.full_name
    
    return DepositRequestResponse(**response_data)

@api_router.get("/deposits/my", response_model=List[DepositRequestResponse])
async def get_my_deposits(current_user: User = Depends(get_current_user)):
    deposits = await db.deposit_requests.find({"user_id": current_user.id}).to_list(None)
    
    result = []
    for deposit in deposits:
        response_data = deposit.copy()
        response_data["user_email"] = current_user.email
        response_data["user_name"] = current_user.full_name
        result.append(DepositRequestResponse(**response_data))
    
    return result

@api_router.get("/admin/deposits", response_model=List[DepositRequestResponse])
async def get_all_deposits(admin: User = Depends(get_current_admin)):
    deposits = await db.deposit_requests.find().to_list(None)
    
    result = []
    for deposit in deposits:
        user = await db.users.find_one({"id": deposit["user_id"]})
        response_data = deposit.copy()
        if user:
            response_data["user_email"] = user.get("email")
            response_data["user_name"] = user.get("full_name")
        result.append(DepositRequestResponse(**response_data))
    
    return result

@api_router.post("/admin/deposits/approve")
async def approve_deposit(approval: DepositApproval, admin: User = Depends(get_current_admin)):
    deposit = await db.deposit_requests.find_one({"id": approval.deposit_id})
    if not deposit:
        raise HTTPException(status_code=404, detail="درخواست واریز یافت نشد")
    
    if deposit["status"] != "pending":
        raise HTTPException(status_code=400, detail="این درخواست قبلاً پردازش شده است")
    
    # Update deposit status
    new_status = "approved" if approval.action == "approve" else "rejected"
    await db.deposit_requests.update_one(
        {"id": approval.deposit_id},
        {"$set": {
            "status": new_status,
            "admin_note": approval.admin_note,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    # If approved, add balance to user wallet
    if approval.action == "approve":
        await db.users.update_one(
            {"id": deposit["user_id"]},
            {"$inc": {"wallet_balance_tmn": deposit["amount"]}}
        )
    
    return {"message": f"درخواست با موفقیت {new_status} شد"}

# ==================== ADMIN KYC ROUTES ====================

@api_router.get("/admin/kyc/pending")
async def get_pending_kyc(admin: User = Depends(get_current_admin)):
    """Get all users with pending Level 2 KYC"""
    users = await db.users.find({
        "kyc_level": 1,
        "kyc_status": "pending",
        "kyc_documents": {"$ne": None}
    }).to_list(None)
    
    return [{
        "id": u["id"],
        "full_name": u.get("full_name"),
        "email": u.get("email"),
        "phone": u.get("phone"),
        "national_code": u.get("national_code"),
        "kyc_documents": u.get("kyc_documents"),
        "submitted_at": u.get("updated_at")
    } for u in users]

@api_router.post("/admin/kyc/approve")
async def approve_kyc(approval: KYCApprovalRequest, admin: User = Depends(get_current_admin)):
    """Approve or reject KYC Level 2"""
    user = await db.users.find_one({"id": approval.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    if approval.action == "approve":
        await db.users.update_one(
            {"id": approval.user_id},
            {"$set": {
                "kyc_level": approval.kyc_level,
                "kyc_status": "approved",
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        message = f"احراز هویت سطح {approval.kyc_level} تایید شد"
    else:
        await db.users.update_one(
            {"id": approval.user_id},
            {"$set": {
                "kyc_status": "rejected",
                "kyc_documents": None,  # Clear documents so user can resubmit
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        message = "احراز هویت رد شد"
    
    return {
        "success": True,
        "message": message,
        "admin_note": approval.admin_note
    }

# ==================== CRYPTO PRICE ROUTES ====================

@api_router.get("/crypto/prices")
async def get_crypto_prices():
    """Get current prices for top cryptocurrencies"""
    result = await price_service.get_prices()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

@api_router.get("/crypto/{coin_id}")
async def get_coin_details(coin_id: str):
    """Get detailed information about a specific coin"""
    result = await price_service.get_coin_details(coin_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result

@api_router.get("/crypto/{coin_id}/chart")
async def get_coin_chart(coin_id: str, days: int = 7):
    """Get historical chart data"""
    result = await price_service.get_market_chart(coin_id, days)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

@api_router.get("/crypto/trending/coins")
async def get_trending():
    """Get trending cryptocurrencies"""
    result = await price_service.get_trending_coins()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

@api_router.get("/crypto/search/{query}")
async def search_crypto(query: str):
    """Search for cryptocurrencies"""
    result = await price_service.search_coins(query)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

# ==================== TRADING ORDER MODELS ====================

class TradingOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_type: str  # "buy", "sell", "trade"
    coin_symbol: str  # BTC, ETH, etc.
    coin_id: str  # bitcoin, ethereum, etc. (CoinGecko ID)
    amount_crypto: Optional[float] = None  # Amount of crypto (for sell/trade)
    amount_tmn: Optional[float] = None  # Amount of TMN (for buy)
    target_coin_symbol: Optional[str] = None  # For trade orders
    target_coin_id: Optional[str] = None  # For trade orders
    price_at_order: float  # Price when order was placed
    total_value_tmn: float  # Total transaction value in TMN
    status: str = "pending"  # pending, approved, rejected, completed
    admin_note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TradingOrderCreate(BaseModel):
    order_type: str  # "buy", "sell", "trade"
    coin_symbol: str
    coin_id: str
    amount_crypto: Optional[float] = None
    amount_tmn: Optional[float] = None
    target_coin_symbol: Optional[str] = None  # For trade
    target_coin_id: Optional[str] = None  # For trade

class TradingOrderResponse(BaseModel):
    id: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    order_type: str
    coin_symbol: str
    coin_id: str
    amount_crypto: Optional[float] = None
    amount_tmn: Optional[float] = None
    target_coin_symbol: Optional[str] = None
    target_coin_id: Optional[str] = None
    price_at_order: float
    total_value_tmn: float
    status: str
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TradingOrderApproval(BaseModel):
    order_id: str
    action: str  # "approve" or "reject"
    admin_note: Optional[str] = None

class UserHolding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    coin_symbol: str
    coin_id: str
    amount: float
    average_buy_price_tmn: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserHoldingResponse(BaseModel):
    id: str
    coin_symbol: str
    coin_id: str
    amount: float
    average_buy_price_tmn: float
    current_price_tmn: Optional[float] = None
    total_value_tmn: Optional[float] = None
    pnl_percent: Optional[float] = None

# ==================== TRADING ORDER ROUTES ====================

@api_router.post("/trading/order", response_model=TradingOrderResponse)
async def create_trading_order(order_data: TradingOrderCreate, current_user: User = Depends(get_current_user)):
    """Create a new trading order (buy/sell/trade)"""
    
    # Check KYC level
    if current_user.kyc_level < 2:
        raise HTTPException(
            status_code=403,
            detail="برای معامله باید احراز هویت سطح ۲ را تکمیل کنید"
        )
    
    # Get current price
    coin_data = await price_service.get_coin_details(order_data.coin_id)
    if not coin_data["success"]:
        raise HTTPException(status_code=404, detail="ارز مورد نظر یافت نشد")
    
    current_price_usd = coin_data["data"]["market_data"]["current_price"]["usd"]
    # Approximate USD to IRR conversion (1 USD = 50,000 IRR)
    current_price_tmn = current_price_usd * 50000
    
    total_value_tmn = 0
    
    if order_data.order_type == "buy":
        if not order_data.amount_tmn or order_data.amount_tmn <= 0:
            raise HTTPException(status_code=400, detail="مبلغ تومان باید بزرگتر از صفر باشد")
        
        # Check wallet balance
        if current_user.wallet_balance_tmn < order_data.amount_tmn:
            raise HTTPException(status_code=400, detail="موجودی کافی ندارید")
        
        total_value_tmn = order_data.amount_tmn
        
    elif order_data.order_type == "sell":
        if not order_data.amount_crypto or order_data.amount_crypto <= 0:
            raise HTTPException(status_code=400, detail="مقدار ارز باید بزرگتر از صفر باشد")
        
        # Check user holdings
        holding = await db.user_holdings.find_one({
            "user_id": current_user.id,
            "coin_symbol": order_data.coin_symbol
        })
        
        if not holding or holding["amount"] < order_data.amount_crypto:
            raise HTTPException(status_code=400, detail="موجودی ارز کافی ندارید")
        
        total_value_tmn = order_data.amount_crypto * current_price_tmn
        
    elif order_data.order_type == "trade":
        if not order_data.amount_crypto or not order_data.target_coin_id:
            raise HTTPException(
                status_code=400,
                detail="برای معامله باید مقدار ارز و ارز مقصد را مشخص کنید"
            )
        
        # Check user holdings for source coin
        holding = await db.user_holdings.find_one({
            "user_id": current_user.id,
            "coin_symbol": order_data.coin_symbol
        })
        
        if not holding or holding["amount"] < order_data.amount_crypto:
            raise HTTPException(status_code=400, detail="موجودی ارز کافی ندارید")
        
        total_value_tmn = order_data.amount_crypto * current_price_tmn
    
    # Create trading order
    trading_order = TradingOrder(
        user_id=current_user.id,
        order_type=order_data.order_type,
        coin_symbol=order_data.coin_symbol,
        coin_id=order_data.coin_id,
        amount_crypto=order_data.amount_crypto,
        amount_tmn=order_data.amount_tmn,
        target_coin_symbol=order_data.target_coin_symbol,
        target_coin_id=order_data.target_coin_id,
        price_at_order=current_price_tmn,
        total_value_tmn=total_value_tmn
    )
    
    await db.trading_orders.insert_one(trading_order.dict())
    
    response_data = trading_order.dict()
    response_data["user_email"] = current_user.email
    response_data["user_name"] = current_user.full_name
    
    return TradingOrderResponse(**response_data)

@api_router.get("/trading/orders/my", response_model=List[TradingOrderResponse])
async def get_my_orders(current_user: User = Depends(get_current_user)):
    """Get user's trading orders"""
    orders = await db.trading_orders.find({"user_id": current_user.id}).to_list(None)
    
    result = []
    for order in orders:
        response_data = order.copy()
        response_data["user_email"] = current_user.email
        response_data["user_name"] = current_user.full_name
        result.append(TradingOrderResponse(**response_data))
    
    return result

@api_router.get("/trading/holdings/my", response_model=List[UserHoldingResponse])
async def get_my_holdings(current_user: User = Depends(get_current_user)):
    """Get user's crypto holdings"""
    holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
    
    result = []
    for holding in holdings:
        # Get current price
        coin_data = await price_service.get_coin_details(holding["coin_id"])
        current_price_usd = 0
        current_price_tmn = 0
        
        if coin_data["success"]:
            current_price_usd = coin_data["data"]["market_data"]["current_price"]["usd"]
            current_price_tmn = current_price_usd * 50000
        
        total_value_tmn = holding["amount"] * current_price_tmn
        pnl_percent = ((current_price_tmn - holding["average_buy_price_tmn"]) / holding["average_buy_price_tmn"]) * 100 if holding["average_buy_price_tmn"] > 0 else 0
        
        response_data = UserHoldingResponse(
            id=holding["id"],
            coin_symbol=holding["coin_symbol"],
            coin_id=holding["coin_id"],
            amount=holding["amount"],
            average_buy_price_tmn=holding["average_buy_price_tmn"],
            current_price_tmn=current_price_tmn,
            total_value_tmn=total_value_tmn,
            pnl_percent=pnl_percent
        )
        result.append(response_data)
    
    return result

# ==================== ADMIN TRADING ROUTES ====================

@api_router.get("/admin/trading/orders", response_model=List[TradingOrderResponse])
async def get_all_trading_orders(admin: User = Depends(get_current_admin)):
    """Get all trading orders for admin"""
    orders = await db.trading_orders.find().to_list(None)
    
    result = []
    for order in orders:
        user = await db.users.find_one({"id": order["user_id"]})
        response_data = order.copy()
        if user:
            response_data["user_email"] = user.get("email")
            response_data["user_name"] = user.get("full_name")
        result.append(TradingOrderResponse(**response_data))
    
    return result

@api_router.post("/admin/trading/orders/approve")
async def approve_trading_order(approval: TradingOrderApproval, admin: User = Depends(get_current_admin)):
    """Approve or reject a trading order"""
    order = await db.trading_orders.find_one({"id": approval.order_id})
    if not order:
        raise HTTPException(status_code=404, detail="سفارش یافت نشد")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail="این سفارش قبلاً پردازش شده است")
    
    new_status = "approved" if approval.action == "approve" else "rejected"
    
    # Update order status
    await db.trading_orders.update_one(
        {"id": approval.order_id},
        {"$set": {
            "status": new_status,
            "admin_note": approval.admin_note,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if approval.action == "approve":
        user = await db.users.find_one({"id": order["user_id"]})
        if not user:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")
        
        if order["order_type"] == "buy":
            # Deduct TMN balance and add crypto holding
            await db.users.update_one(
                {"id": order["user_id"]},
                {"$inc": {"wallet_balance_tmn": -order["amount_tmn"]}}
            )
            
            # Add or update crypto holding
            crypto_amount = order["amount_tmn"] / order["price_at_order"]
            existing_holding = await db.user_holdings.find_one({
                "user_id": order["user_id"],
                "coin_symbol": order["coin_symbol"]
            })
            
            if existing_holding:
                # Update existing holding (weighted average price)
                total_amount = existing_holding["amount"] + crypto_amount
                new_avg_price = ((existing_holding["amount"] * existing_holding["average_buy_price_tmn"]) + 
                               (crypto_amount * order["price_at_order"])) / total_amount
                
                await db.user_holdings.update_one(
                    {"id": existing_holding["id"]},
                    {"$set": {
                        "amount": total_amount,
                        "average_buy_price_tmn": new_avg_price,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
            else:
                # Create new holding
                new_holding = UserHolding(
                    user_id=order["user_id"],
                    coin_symbol=order["coin_symbol"],
                    coin_id=order["coin_id"],
                    amount=crypto_amount,
                    average_buy_price_tmn=order["price_at_order"]
                )
                await db.user_holdings.insert_one(new_holding.dict())
                
        elif order["order_type"] == "sell":
            # Add TMN balance and deduct crypto holding
            tmn_amount = order["amount_crypto"] * order["price_at_order"]
            await db.users.update_one(
                {"id": order["user_id"]},
                {"$inc": {"wallet_balance_tmn": tmn_amount}}
            )
            
            # Deduct from crypto holding
            await db.user_holdings.update_one(
                {"user_id": order["user_id"], "coin_symbol": order["coin_symbol"]},
                {"$inc": {"amount": -order["amount_crypto"]}}
            )
            
        elif order["order_type"] == "trade":
            # Get target coin current price
            target_coin_data = await price_service.get_coin_details(order["target_coin_id"])
            if target_coin_data["success"]:
                target_price_usd = target_coin_data["data"]["market_data"]["current_price"]["usd"]
                target_price_tmn = target_price_usd * 50000
                
                # Calculate how much target coin to give
                source_value_tmn = order["amount_crypto"] * order["price_at_order"]
                target_crypto_amount = source_value_tmn / target_price_tmn
                
                # Deduct source coin
                await db.user_holdings.update_one(
                    {"user_id": order["user_id"], "coin_symbol": order["coin_symbol"]},
                    {"$inc": {"amount": -order["amount_crypto"]}}
                )
                
                # Add target coin
                existing_target_holding = await db.user_holdings.find_one({
                    "user_id": order["user_id"],
                    "coin_symbol": order["target_coin_symbol"]
                })
                
                if existing_target_holding:
                    total_amount = existing_target_holding["amount"] + target_crypto_amount
                    new_avg_price = ((existing_target_holding["amount"] * existing_target_holding["average_buy_price_tmn"]) + 
                                   (target_crypto_amount * target_price_tmn)) / total_amount
                    
                    await db.user_holdings.update_one(
                        {"id": existing_target_holding["id"]},
                        {"$set": {
                            "amount": total_amount,
                            "average_buy_price_tmn": new_avg_price,
                            "updated_at": datetime.now(timezone.utc)
                        }}
                    )
                else:
                    new_holding = UserHolding(
                        user_id=order["user_id"],
                        coin_symbol=order["target_coin_symbol"],
                        coin_id=order["target_coin_id"],
                        amount=target_crypto_amount,
                        average_buy_price_tmn=target_price_tmn
                    )
                    await db.user_holdings.insert_one(new_holding.dict())
        
        # Mark order as completed
        await db.trading_orders.update_one(
            {"id": approval.order_id},
            {"$set": {"status": "completed"}}
        )
    
    return {"message": f"سفارش با موفقیت {new_status} شد"}

# ==================== AI CHATBOT ROUTES ====================

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

@api_router.post("/ai/chat")
async def ai_chat(chat_msg: ChatMessage, current_user: User = Depends(get_current_user)):
    """Chat with AI assistant"""
    session_id = chat_msg.session_id or f"user_{current_user.id}"
    result = await chatbot.chat(chat_msg.message, session_id)
    return result

# ==================== AI MARKET ANALYSIS ROUTES ====================

@api_router.get("/ai/analyze/{coin_id}")
async def analyze_coin(coin_id: str, current_user: User = Depends(get_current_user)):
    """Get AI analysis for a specific coin"""
    # Get coin data first
    coin_data = await price_service.get_coin_details(coin_id)
    if not coin_data["success"]:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    # Analyze with AI
    analysis = await market_analyst.analyze_market(coin_data["data"])
    return analysis

@api_router.get("/ai/signals")
async def get_trading_signals(current_user: User = Depends(get_current_user)):
    """Get AI-generated trading signals"""
    # Get market data
    prices = await price_service.get_prices()
    if not prices["success"]:
        raise HTTPException(status_code=500, detail="Failed to fetch market data")
    
    # Convert to list format for analysis
    market_data = []
    for coin_id, data in list(prices["data"].items())[:10]:
        market_data.append({
            "symbol": coin_id.upper(),
            "current_price": data.get("usd", 0),
            "price_change_24h": data.get("usd_24h_change", 0),
            "volume": data.get("usd_24h_vol", 0)
        })
    
    signals = await market_analyst.generate_trading_signals(market_data)
    return signals

@api_router.post("/ai/portfolio/analyze")
async def analyze_portfolio(current_user: User = Depends(get_current_user)):
    """Analyze user's portfolio with AI"""
    # Mock portfolio for now - in real app, fetch from database
    portfolio = {
        "total_value": current_user.wallet_balance_tmn * 0.000027,  # Convert TMN to USD roughly
        "total_pnl_percent": 5.2,
        "holdings": [
            {"symbol": "BTC", "amount": 0.5, "value": 15000},
            {"symbol": "ETH", "amount": 2, "value": 3000}
        ]
    }
    
    advice = await portfolio_advisor.analyze_portfolio(portfolio)
    return advice

@api_router.get("/ai/predict/{coin_id}")
async def predict_price(coin_id: str, timeframe: str = "24h", current_user: User = Depends(get_current_user)):
    """Get AI price prediction"""
    # Get coin data
    coin_data = await price_service.get_coin_details(coin_id)
    if not coin_data["success"]:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    prediction = await price_predictor.predict_price(coin_data["data"], timeframe)
    return prediction

@api_router.get("/")
async def root():
    return {"message": "Persian Crypto Exchange API with AI", "version": "2.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()