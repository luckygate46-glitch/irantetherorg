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
    email: EmailStr
    password: str
    phone: str  # Mandatory for OTP
    
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
    email: str
    phone: str
    full_name: Optional[str] = None
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
    email: str
    password_hash: str
    phone: str
    full_name: Optional[str] = None  # Added in KYC Level 1
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

@api_router.get("/")
async def root():
    return {"message": "Persian Crypto Exchange API", "version": "1.0.0"}

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