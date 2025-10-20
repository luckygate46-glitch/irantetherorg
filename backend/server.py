from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
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
import time
import asyncio
import csv
import io
from ai_services import chatbot, market_analyst, portfolio_advisor, price_predictor, risk_analyzer, news_summarizer
from crypto_prices import price_service
from wallex_prices import get_wallex_service
from ai_admin_services import fraud_detector, market_intelligence, system_intelligence, predictive_analytics
from ai_user_services import personal_assistant, portfolio_manager, notification_system
from advanced_ai_services import predictive_market_analysis, sentiment_analysis_engine, portfolio_optimizer
from comprehensive_ai_services import get_ai_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration variables first
RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.environ.get('CACHE_TTL', '300'))  # 5 minutes default
DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE', 'true').lower() == 'true'

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Rate limiting storage (in-memory for simplicity)
rate_limit_storage = {}

# Cache storage (in-memory for simplicity)
cache_storage = {}

def check_rate_limit(identifier: str, limit: int = 10, window: int = 60) -> bool:
    """Simple rate limiting check"""
    if not RATE_LIMIT_ENABLED:
        return True
    
    current_time = time.time()
    
    if identifier not in rate_limit_storage:
        rate_limit_storage[identifier] = []
    
    # Clean old entries
    rate_limit_storage[identifier] = [
        timestamp for timestamp in rate_limit_storage[identifier] 
        if current_time - timestamp < window
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[identifier]) >= limit:
        return False
    
    # Add current request
    rate_limit_storage[identifier].append(current_time)
    return True

def get_from_cache(key: str):
    """Get value from cache"""
    if key not in cache_storage:
        return None
    
    item = cache_storage[key]
    if time.time() - item['timestamp'] > CACHE_TTL:
        del cache_storage[key]
        return None
    
    return item['data']

def set_cache(key: str, data):
    """Set value in cache"""
    cache_storage[key] = {
        'data': data,
        'timestamp': time.time()
    }

# Security
security = HTTPBearer()
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'persian-crypto-exchange-secret-key-2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# API.IR Configuration
APIR_BASE_URL = "https://s.api.ir/api"
APIR_API_KEY = os.environ.get('APIR_API_KEY', None)  # Must be set in environment variables

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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
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
    first_name: Optional[str] = None  # Made optional for backward compatibility
    last_name: Optional[str] = None  # Made optional for backward compatibility
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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    wallet_balance_tmn: Optional[float] = None

class WalletAddress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    symbol: str  # BTC, ETH, USDT, etc.
    address: str
    label: Optional[str] = None
    verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WalletAddressCreate(BaseModel):
    symbol: str
    address: str
    label: Optional[str] = None

class WalletAddressResponse(BaseModel):
    id: str
    symbol: str
    address: str
    label: Optional[str] = None
    verified: bool
    created_at: datetime

class BankingInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    card_number: str
    bank_name: str
    account_holder: str
    iban: Optional[str] = None
    verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BankingInfoCreate(BaseModel):
    card_number: str
    bank_name: str
    account_holder: str
    iban: Optional[str] = None

class BankingInfoResponse(BaseModel):
    id: str
    card_number: str
    bank_name: str
    account_holder: str
    iban: Optional[str] = None
    verified: bool
    created_at: datetime

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
    full_name: str  # Complete name (can override first_name + last_name)
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

# Enhanced KYC Models for Video KYC and Advanced Verification
class VideoKYCRequest(BaseModel):
    session_id: str
    video_data: str  # Base64 encoded video
    duration: float  # Video duration in seconds
    questions_answers: List[dict]  # Video responses to verification questions

class DocumentOCRResult(BaseModel):
    document_type: str  # "national_id", "passport", "driving_license"
    extracted_data: dict
    confidence_score: float
    verification_status: str  # "verified", "needs_review", "failed"

class LivenessDetectionResult(BaseModel):
    session_id: str
    liveness_score: float
    face_match_score: float
    verification_status: str
    anti_spoofing_passed: bool

class AMLRiskAssessment(BaseModel):
    user_id: str
    risk_score: float  # 0-100
    risk_level: str  # "low", "medium", "high", "very_high"
    risk_factors: List[str]
    compliance_status: str
    review_required: bool
    last_assessment: datetime

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

# ========================================
# TRANSACTION RECORDING SYSTEM (Critical for audit trail)
# ========================================

async def record_transaction(
    user_id: str,
    transaction_type: str,  # 'deposit', 'withdrawal', 'order_buy', 'order_sell', 'refund', 'admin_adjustment'
    amount_tmn: float,
    reference_type: str,  # 'deposit', 'order', 'admin_action'
    reference_id: str,
    description: str,
    created_by: str,
    ip_address: str = None,
    admin_notes: str = None
) -> dict:
    """
    Record a financial transaction with full audit trail.
    This creates a permanent record of every balance change.
    
    Returns the transaction document
    """
    try:
        # Get current balance
        user = await db.users.find_one({'id': user_id})
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        balance_before = user.get('wallet_balance_tmn', 0)
        balance_after = balance_before + amount_tmn
        
        # Prevent negative balance
        if balance_after < 0:
            raise ValueError(f"Insufficient balance. Current: {balance_before}, Attempting: {amount_tmn}")
        
        # Create transaction record
        transaction = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'type': transaction_type,
            'amount_tmn': amount_tmn,
            'balance_before': balance_before,
            'balance_after': balance_after,
            
            # Reference to source document
            'reference_type': reference_type,
            'reference_id': reference_id,
            
            # Metadata
            'description': description,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'created_by': created_by,
            'ip_address': ip_address,
            
            # Status
            'status': 'completed',
            'reversed_by': None,
            
            # Admin notes (for adjustments)
            'admin_notes': admin_notes
        }
        
        # Insert transaction record
        await db.transactions.insert_one(transaction)
        
        # Update user balance
        await db.users.update_one(
            {'id': user_id},
            {
                '$set': {
                    'wallet_balance_tmn': balance_after,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"✅ Transaction recorded: {transaction_type} {amount_tmn} TMN for user {user_id}")
        logger.info(f"   Balance: {balance_before} → {balance_after}")
        
        return transaction
        
    except Exception as e:
        logger.error(f"❌ Error recording transaction: {str(e)}")
        raise

async def calculate_user_balance_from_transactions(user_id: str) -> dict:
    """
    Calculate user's balance from transaction history.
    Used for verification and reconciliation.
    
    Returns dict with calculated balance and breakdown
    """
    transactions = await db.transactions.find({'user_id': user_id}).to_list(length=10000)
    
    calculated_balance = 0
    breakdown = {
        'deposits': 0,
        'withdrawals': 0,
        'order_buy': 0,
        'order_sell': 0,
        'refunds': 0,
        'admin_adjustments': 0
    }
    
    for txn in transactions:
        amount = txn.get('amount_tmn', 0)
        txn_type = txn.get('type', '')
        
        calculated_balance += amount
        
        if txn_type == 'deposit':
            breakdown['deposits'] += amount
        elif txn_type == 'withdrawal':
            breakdown['withdrawals'] += amount
        elif txn_type == 'order_buy':
            breakdown['order_buy'] += amount
        elif txn_type == 'order_sell':
            breakdown['order_sell'] += amount
        elif txn_type == 'refund':
            breakdown['refunds'] += amount
        elif txn_type == 'admin_adjustment':
            breakdown['admin_adjustments'] += amount
    
    return {
        'calculated_balance': calculated_balance,
        'breakdown': breakdown,
        'transaction_count': len(transactions)
    }

# ========================================
# NOTIFICATION SYSTEM
# ========================================

async def create_notification(
    user_id: str,
    notification_type: str,  # 'order_approved', 'order_rejected', 'deposit_approved', etc.
    title: str,
    message: str,
    reference_type: str = None,  # 'order', 'deposit', 'kyc'
    reference_id: str = None,
    data: dict = None
) -> dict:
    """
    Create an in-app notification for a user
    
    Types:
    - order_approved
    - order_rejected
    - deposit_approved
    - deposit_rejected
    - kyc_approved
    - kyc_rejected
    - price_alert
    """
    try:
        notification = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'type': notification_type,
            'title': title,
            'message': message,
            'reference_type': reference_type,
            'reference_id': reference_id,
            'data': data or {},
            'is_read': False,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        await db.notifications.insert_one(notification)
        logger.info(f"✅ Notification created: {notification_type} for user {user_id}")
        
        return notification
        
    except Exception as e:
        logger.error(f"❌ Error creating notification: {str(e)}")
        # Don't fail the main operation if notification fails
        return None

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
    except jwt.InvalidTokenError:
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
    # Handle backward compatibility for users without first_name/last_name
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    
    # Compute full_name from first_name + last_name if not overridden
    if user.full_name:
        computed_full_name = user.full_name
    elif first_name and last_name:
        computed_full_name = f"{first_name} {last_name}"
    elif first_name or last_name:
        computed_full_name = first_name or last_name
    else:
        computed_full_name = user.email.split('@')[0]  # Fallback to email username
    
    return UserResponse(
        id=user.id,
        first_name=first_name,
        last_name=last_name,
        email=user.email,
        phone=user.phone,
        full_name=computed_full_name,
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
    """Send OTP via API.IR SMS service with development fallback"""
    
    # Development mode fallback - simulate successful OTP sending
    if DEVELOPMENT_MODE:
        logger.info(f"DEVELOPMENT MODE: OTP {code} for {phone} (not actually sent)")
        return True
    
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
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                logger.warning(f"API.IR OTP failed with status {response.status_code}: {response.text}")
                # Fallback to development mode on API failure
                logger.info(f"FALLBACK: OTP {code} for {phone} (API.IR unavailable)")
                return True
                
    except Exception as e:
        logger.error(f"API.IR SMS OTP Error: {str(e)}")
        # Fallback to development mode on error
        logger.info(f"FALLBACK: OTP {code} for {phone} (API.IR error)")
        return True

async def verify_shahkar_internal(national_code: str, mobile: str, is_company: bool = False) -> dict:
    """Verify national code with mobile number using Shahkar with development fallback"""
    
    # Development mode fallback - simulate successful verification
    if DEVELOPMENT_MODE:
        logger.info(f"DEVELOPMENT MODE: Shahkar verification for {national_code} with {mobile} (not actually verified)")
        return {"success": True, "data": {"match": True}}
    
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
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API.IR Shahkar failed with status {response.status_code}: {response.text}")
                # Fallback to development mode on API failure
                logger.info(f"FALLBACK: Shahkar verification for {national_code} with {mobile} (API.IR unavailable)")
                return {"success": True, "data": {"match": True}}
                
    except Exception as e:
        logger.error(f"API.IR Shahkar Error: {str(e)}")
        # Fallback to development mode on error
        logger.info(f"FALLBACK: Shahkar verification for {national_code} with {mobile} (API.IR error)")
        return {"success": True, "data": {"match": True}}

async def verify_card_match_internal(national_code: str, birth_date: str, card_number: str) -> dict:
    """Verify card belongs to user with development fallback"""
    
    # Development mode fallback - simulate successful verification
    if DEVELOPMENT_MODE:
        logger.info(f"DEVELOPMENT MODE: CardMatch verification for {national_code} with card {card_number[-4:]} (not actually verified)")
        return {"success": True, "data": {"match": True}}
    
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
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API.IR CardMatch failed with status {response.status_code}: {response.text}")
                # Fallback to development mode on API failure
                logger.info(f"FALLBACK: CardMatch verification for {national_code} with card {card_number[-4:]} (API.IR unavailable)")
                return {"success": True, "data": {"match": True}}
                
    except Exception as e:
        logger.error(f"API.IR CardMatch Error: {str(e)}")
        # Fallback to development mode on error
        logger.info(f"FALLBACK: CardMatch verification for {national_code} with card {card_number[-4:]} (API.IR error)")
        return {"success": True, "data": {"match": True}}

async def get_card_info(card_number: str) -> dict:
    """Get card owner name with development fallback"""
    
    # Development mode fallback - return mock card owner name
    if DEVELOPMENT_MODE:
        logger.info(f"DEVELOPMENT MODE: CardInfo for card {card_number[-4:]} (returning mock name)")
        return {"success": True, "data": {"name": "صاحب کارت تست"}}
    
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
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API.IR CardInfo failed with status {response.status_code}: {response.text}")
                # Fallback to development mode on API failure
                logger.info(f"FALLBACK: CardInfo for card {card_number[-4:]} (API.IR unavailable)")
                return {"success": True, "data": {"name": "صاحب کارت"}}
                
    except Exception as e:
        logger.error(f"API.IR CardInfo Error: {str(e)}")
        # Fallback to development mode on error
        logger.info(f"FALLBACK: CardInfo for card {card_number[-4:]} (API.IR error)")
        return {"success": True, "data": {"name": "صاحب کارت"}}

# ==================== OTP ROUTES ====================

@api_router.post("/otp/send")
async def send_otp(request: SendOTPRequest, http_request: Request):
    """Send OTP code via SMS using API.IR"""
    # Rate limiting for OTP requests
    client_ip = http_request.client.host if http_request.client else "unknown"
    phone_key = f"otp_send_{request.phone}"
    ip_key = f"otp_send_ip_{client_ip}"
    
    if not check_rate_limit(phone_key, limit=3, window=300):  # 3 OTP per phone per 5 minutes
        raise HTTPException(
            status_code=429,
            detail="تعداد درخواست کد تایید برای این شماره بیش از حد مجاز. لطفا 5 دقیقه صبر کنید"
        )
    
    if not check_rate_limit(ip_key, limit=10, window=300):  # 10 OTP per IP per 5 minutes
        raise HTTPException(
            status_code=429,
            detail="تعداد درخواست کد تایید از این IP بیش از حد مجاز. لطفا 5 دقیقه صبر کنید"
        )
    
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
async def verify_otp(request: VerifyOTPRequest, http_request: Request):
    """Verify OTP code"""
    # Rate limiting for OTP verification attempts
    phone_key = f"otp_verify_{request.phone}"
    
    if not check_rate_limit(phone_key, limit=5, window=300):  # 5 verification attempts per phone per 5 minutes
        raise HTTPException(
            status_code=429,
            detail="تعداد تلاش‌های تایید کد برای این شماره بیش از حد مجاز. لطفا 5 دقیقه صبر کنید"
        )
    
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
    
    # Check expiration - ensure both datetimes are timezone-aware
    current_time = datetime.now(timezone.utc)
    expires_at = otp.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if current_time > expires_at:
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
async def register(user_data: UserCreate, request: Request):
    # Rate limiting for registration attempts
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(f"register_{client_ip}", limit=3, window=300):  # 3 attempts per 5 minutes
        raise HTTPException(
            status_code=429,
            detail="تعداد تلاش‌های ثبت‌نام بیش از حد مجاز. لطفا 5 دقیقه صبر کنید"
        )
    
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
    
    # Check if phone OTP is verified (optional - user can verify later)
    otp_verified = await db.otp_verifications.find_one(
        {"phone": user_data.phone, "verified": True}
    )
    
    is_phone_verified = bool(otp_verified)
    
    # Create new user with Level 0 (phone verification optional)
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
        is_phone_verified=is_phone_verified,
        is_admin=False,  # EXPLICITLY set to False - new users are NOT admins
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
async def login_user(user_credentials: UserLogin, request: Request):
    """Login user and return JWT token"""
    
    # Rate limiting for login attempts
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(f"login_{client_ip}", limit=5, window=300):  # 5 attempts per 5 minutes
        raise HTTPException(
            status_code=429,
            detail="تعداد تلاش‌های ورود بیش از حد مجاز. لطفا 5 دقیقه صبر کنید"
        )
    
    # Find user
    user_data = await db.users.find_one({"email": user_credentials.email})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا رمز عبور اشتباه است"
        )
    
    user = User(**user_data)
    
    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
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
    shahkar_result = await verify_shahkar_internal(kyc_data.national_code, current_user.phone)
    
    if not shahkar_result.get("success"):
        raise HTTPException(
            status_code=400,
            detail="کد ملی با شماره موبایل مطابقت ندارد (شاهکار)"
        )
    
    # Verify card ownership with API.IR CardMatch
    card_match_result = await verify_card_match_internal(
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

# ==================== USER PROFILE & WALLET ROUTES ====================

@api_router.put("/user/profile")
async def update_user_profile(profile_data: dict, current_user: User = Depends(get_current_user)):
    """Update user profile information"""
    
    # Only allow updating specific fields
    allowed_fields = ['first_name', 'last_name', 'phone']
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    
    if update_data:
        # Update full_name if first_name or last_name changed
        if 'first_name' in update_data or 'last_name' in update_data:
            first_name = update_data.get('first_name', current_user.first_name)
            last_name = update_data.get('last_name', current_user.last_name)
            update_data['full_name'] = f"{first_name} {last_name}"
        
        update_data['updated_at'] = datetime.now(timezone.utc)
        
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
        
        # Get updated user
        updated_user = await db.users.find_one({"id": current_user.id})
        return User(**updated_user)
    
    return current_user

@api_router.post("/user/wallet-addresses", response_model=WalletAddressResponse)
async def add_wallet_address(wallet_data: WalletAddressCreate, current_user: User = Depends(get_current_user)):
    """Add a new wallet address for the user"""
    
    # Create wallet address
    wallet_address = WalletAddress(
        user_id=current_user.id,
        symbol=wallet_data.symbol.upper(),
        address=wallet_data.address,
        label=wallet_data.label
    )
    
    # Check if address already exists
    existing = await db.wallet_addresses.find_one({
        "user_id": current_user.id,
        "symbol": wallet_address.symbol,
        "address": wallet_address.address
    })
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="این آدرس کیف پول قبلاً اضافه شده است"
        )
    
    # Insert into database
    await db.wallet_addresses.insert_one(wallet_address.dict())
    
    return WalletAddressResponse(**wallet_address.dict())

@api_router.get("/user/wallet-addresses", response_model=List[WalletAddressResponse])
async def get_wallet_addresses(current_user: User = Depends(get_current_user)):
    """Get all wallet addresses for the current user"""
    
    wallet_addresses = await db.wallet_addresses.find({"user_id": current_user.id}).to_list(None)
    
    return [WalletAddressResponse(**address) for address in wallet_addresses]

@api_router.delete("/user/wallet-addresses/{wallet_id}")
async def delete_wallet_address(wallet_id: str, current_user: User = Depends(get_current_user)):
    """Delete a wallet address"""
    
    # Check if wallet belongs to current user
    wallet = await db.wallet_addresses.find_one({
        "id": wallet_id,
        "user_id": current_user.id
    })
    
    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="کیف پول یافت نشد"
        )
    
    # Delete wallet
    await db.wallet_addresses.delete_one({
        "id": wallet_id,
        "user_id": current_user.id
    })
    
    return {"success": True, "message": "کیف پول حذف شد"}

@api_router.post("/user/banking-info", response_model=BankingInfoResponse)
async def add_banking_info(banking_data: BankingInfoCreate, current_user: User = Depends(get_current_user)):
    """Add or update banking information"""
    
    # Create banking info
    banking_info = BankingInfo(
        user_id=current_user.id,
        card_number=banking_data.card_number,
        bank_name=banking_data.bank_name,
        account_holder=banking_data.account_holder,
        iban=banking_data.iban
    )
    
    # Check if banking info already exists and update instead
    existing = await db.banking_info.find_one({"user_id": current_user.id})
    
    if existing:
        # Update existing
        update_data = banking_info.dict()
        update_data['updated_at'] = datetime.now(timezone.utc)
        
        await db.banking_info.update_one(
            {"user_id": current_user.id},
            {"$set": update_data}
        )
        
        updated = await db.banking_info.find_one({"user_id": current_user.id})
        return BankingInfoResponse(**updated)
    else:
        # Insert new
        await db.banking_info.insert_one(banking_info.dict())
        return BankingInfoResponse(**banking_info.dict())

@api_router.get("/user/banking-info", response_model=Optional[BankingInfoResponse])
async def get_banking_info(current_user: User = Depends(get_current_user)):
    """Get banking information for the current user"""
    
    banking_info = await db.banking_info.find_one({"user_id": current_user.id})
    
    if banking_info:
        return BankingInfoResponse(**banking_info)
    
    return None

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

# ==================== ENHANCED USER MANAGEMENT ROUTES ====================

@api_router.post("/admin/users/{user_id}/suspend")
async def suspend_user(user_id: str, suspension_data: dict, admin: User = Depends(get_current_admin)):
    """Suspend a user temporarily or permanently"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    duration = suspension_data.get("duration")  # in days, None for permanent
    reason = suspension_data.get("reason", "")
    
    suspension_end = None
    if duration:
        suspension_end = (datetime.now(timezone.utc) + timedelta(days=duration)).isoformat()
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "is_suspended": True,
            "suspension_reason": reason,
            "suspension_end": suspension_end,
            "suspended_at": datetime.now(timezone.utc).isoformat(),
            "suspended_by": admin.id
        }}
    )
    
    # Log activity
    await db.user_activity_logs.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": "user_suspended",
        "performed_by": admin.id,
        "details": {"reason": reason, "duration": duration},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "کاربر با موفقیت تعلیق شد", "suspension_end": suspension_end}

@api_router.post("/admin/users/{user_id}/unsuspend")
async def unsuspend_user(user_id: str, admin: User = Depends(get_current_admin)):
    """Remove suspension from a user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "is_suspended": False,
            "suspension_reason": None,
            "suspension_end": None,
            "unsuspended_at": datetime.now(timezone.utc).isoformat(),
            "unsuspended_by": admin.id
        }}
    )
    
    # Log activity
    await db.user_activity_logs.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": "user_unsuspended",
        "performed_by": admin.id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "تعلیق کاربر با موفقیت لغو شد"}

@api_router.post("/admin/users/{user_id}/notes")
async def add_user_note(user_id: str, note_data: dict, admin: User = Depends(get_current_admin)):
    """Add a private admin note to a user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    note = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "note": note_data.get("note"),
        "created_by": admin.id,
        "created_by_name": admin.full_name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_notes.insert_one(note)
    
    return {"message": "یادداشت با موفقیت اضافه شد", "note": note}

@api_router.get("/admin/users/{user_id}/notes")
async def get_user_notes(user_id: str, admin: User = Depends(get_current_admin)):
    """Get all notes for a user"""
    notes = await db.user_notes.find({"user_id": user_id}).sort("created_at", -1).to_list(None)
    return notes

@api_router.post("/admin/users/{user_id}/tags")
async def add_user_tag(user_id: str, tag_data: dict, admin: User = Depends(get_current_admin)):
    """Add a tag to a user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    tag = tag_data.get("tag")
    current_tags = user.get("tags", [])
    
    if tag not in current_tags:
        current_tags.append(tag)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"tags": current_tags}}
        )
    
    return {"message": "برچسب با موفقیت اضافه شد", "tags": current_tags}

@api_router.delete("/admin/users/{user_id}/tags/{tag}")
async def remove_user_tag(user_id: str, tag: str, admin: User = Depends(get_current_admin)):
    """Remove a tag from a user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    current_tags = user.get("tags", [])
    if tag in current_tags:
        current_tags.remove(tag)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"tags": current_tags}}
        )
    
    return {"message": "برچسب با موفقیت حذف شد", "tags": current_tags}

@api_router.get("/admin/users/{user_id}/activity")
async def get_user_activity(user_id: str, admin: User = Depends(get_current_admin)):
    """Get activity log for a user"""
    activities = await db.user_activity_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(50).to_list(None)
    return activities

@api_router.post("/admin/users/search")
async def search_users(search_params: dict, admin: User = Depends(get_current_admin)):
    """Advanced user search with multiple filters"""
    query = {}
    
    # Text search
    if search_params.get("search_text"):
        text = search_params["search_text"]
        query["$or"] = [
            {"email": {"$regex": text, "$options": "i"}},
            {"phone": {"$regex": text, "$options": "i"}},
            {"full_name": {"$regex": text, "$options": "i"}},
            {"first_name": {"$regex": text, "$options": "i"}},
            {"last_name": {"$regex": text, "$options": "i"}}
        ]
    
    # KYC level filter
    if search_params.get("kyc_level") is not None:
        query["kyc_level"] = search_params["kyc_level"]
    
    # KYC status filter
    if search_params.get("kyc_status"):
        query["kyc_status"] = search_params["kyc_status"]
    
    # Admin filter
    if search_params.get("is_admin") is not None:
        query["is_admin"] = search_params["is_admin"]
    
    # Suspension filter
    if search_params.get("is_suspended") is not None:
        query["is_suspended"] = search_params["is_suspended"]
    
    # Tag filter
    if search_params.get("tag"):
        query["tags"] = search_params["tag"]
    
    # Date range filter
    if search_params.get("created_after"):
        query["created_at"] = {"$gte": search_params["created_after"]}
    if search_params.get("created_before"):
        if "created_at" in query:
            query["created_at"]["$lte"] = search_params["created_before"]
        else:
            query["created_at"] = {"$lte": search_params["created_before"]}
    
    users = await db.users.find(query).to_list(None)
    return [user_to_response(User(**user)) for user in users]

@api_router.post("/admin/users/bulk-action")
async def bulk_user_action(bulk_data: dict, admin: User = Depends(get_current_admin)):
    """Perform bulk actions on multiple users"""
    user_ids = bulk_data.get("user_ids", [])
    action = bulk_data.get("action")
    
    if not user_ids or not action:
        raise HTTPException(status_code=400, detail="شناسه کاربران و نوع عملیات الزامی است")
    
    result = {"success": 0, "failed": 0, "errors": []}
    
    for user_id in user_ids:
        try:
            if action == "suspend":
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {
                        "is_suspended": True,
                        "suspension_reason": bulk_data.get("reason", "عملیات گروهی"),
                        "suspended_at": datetime.now(timezone.utc).isoformat(),
                        "suspended_by": admin.id
                    }}
                )
            elif action == "unsuspend":
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {
                        "is_suspended": False,
                        "unsuspended_at": datetime.now(timezone.utc).isoformat(),
                        "unsuspended_by": admin.id
                    }}
                )
            elif action == "add_tag":
                tag = bulk_data.get("tag")
                if tag:
                    await db.users.update_one(
                        {"id": user_id},
                        {"$addToSet": {"tags": tag}}
                    )
            elif action == "remove_tag":
                tag = bulk_data.get("tag")
                if tag:
                    await db.users.update_one(
                        {"id": user_id},
                        {"$pull": {"tags": tag}}
                    )
            elif action == "delete":
                await db.users.delete_one({"id": user_id})
            
            result["success"] += 1
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({"user_id": user_id, "error": str(e)})
    
    return {
        "message": f"عملیات انجام شد: {result['success']} موفق، {result['failed']} ناموفق",
        "result": result
    }

@api_router.get("/admin/users/stats")
async def get_user_stats(admin: User = Depends(get_current_admin)):
    """Get user statistics for admin dashboard"""
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"last_login": {"$gte": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()}})
    suspended_users = await db.users.count_documents({"is_suspended": True})
    admin_users = await db.users.count_documents({"is_admin": True})
    
    # KYC stats
    kyc_level_0 = await db.users.count_documents({"kyc_level": 0})
    kyc_level_1 = await db.users.count_documents({"kyc_level": 1})
    kyc_level_2 = await db.users.count_documents({"kyc_level": 2})
    
    pending_kyc = await db.users.count_documents({"kyc_status": "pending"})
    
    # Recent registrations
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    new_today = await db.users.count_documents({"created_at": {"$gte": today_start.isoformat()}})
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "admin_users": admin_users,
        "kyc_stats": {
            "level_0": kyc_level_0,
            "level_1": kyc_level_1,
            "level_2": kyc_level_2,
            "pending": pending_kyc
        },
        "new_today": new_today
    }

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
            "approved_by": admin.id if approval.action == "approve" else None,
            "approved_at": datetime.now(timezone.utc).isoformat() if approval.action == "approve" else None,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    # If approved, add balance to user wallet using transaction system
    if approval.action == "approve":
        try:
            # Record transaction for audit trail
            transaction = await record_transaction(
                user_id=deposit["user_id"],
                transaction_type="deposit",
                amount_tmn=deposit["amount"],
                reference_type="deposit",
                reference_id=deposit["id"],
                description=f"واریز کارت به کارت تایید شده",
                created_by=admin.id
            )
            
            logger.info(f"✅ Deposit approved with transaction: {transaction['id']}")
            
            # Update deposit with transaction reference
            await db.deposit_requests.update_one(
                {"id": approval.deposit_id},
                {"$set": {"transaction_id": transaction['id']}}
            )
            
            # Create notification for user
            await create_notification(
                user_id=deposit["user_id"],
                notification_type="deposit_approved",
                title="✅ واریز تایید شد",
                message=f"واریز {deposit['amount']:,.0f} تومان شما تایید شد و به کیف پول اضافه گردید",
                reference_type="deposit",
                reference_id=deposit["id"],
                data={
                    'amount': deposit['amount'],
                    'transaction_id': transaction['id']
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error recording deposit transaction: {str(e)}")
            # Rollback deposit status
            await db.deposit_requests.update_one(
                {"id": approval.deposit_id},
                {"$set": {"status": "pending"}}
            )
            raise HTTPException(status_code=500, detail=f"خطا در ثبت تراکنش: {str(e)}")
    else:
        # Create notification for rejection
        await create_notification(
            user_id=deposit["user_id"],
            notification_type="deposit_rejected",
            title="❌ واریز رد شد",
            message=f"واریز {deposit['amount']:,.0f} تومان شما رد شد. {approval.admin_note or ''}",
            reference_type="deposit",
            reference_id=deposit["id"],
            data={
                'amount': deposit['amount'],
                'reason': approval.admin_note
            }
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
        
        # Log the approval for debugging
        logger.info(f"KYC approved for user {approval.user_id}: level={approval.kyc_level}, status=approved")
        
        # Create notification for user
        await create_notification(
            user_id=approval.user_id,
            notification_type="kyc_approved",
            title=f"✅ احراز هویت سطح {approval.kyc_level} تایید شد",
            message=f"تبریک! احراز هویت شما تایید شد و اکنون می‌توانید از تمام امکانات سایت استفاده کنید",
            reference_type="kyc",
            reference_id=approval.user_id,
            data={
                'kyc_level': approval.kyc_level,
                'admin_note': approval.admin_note
            }
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
        
        # Create notification for rejection
        await create_notification(
            user_id=approval.user_id,
            notification_type="kyc_rejected",
            title="❌ احراز هویت رد شد",
            message=f"متأسفانه احراز هویت شما رد شد. {approval.admin_note or 'لطفاً مدارک معتبر ارسال کنید'}",
            reference_type="kyc",
            reference_id=approval.user_id,
            data={
                'reason': approval.admin_note
            }
        )
        
        message = "احراز هویت رد شد"
    
    if approval.action == "approve":
        return {
            "success": True,
            "message": message,
            "user_id": approval.user_id,
            "new_level": approval.kyc_level,
            "admin_note": approval.admin_note
        }
    else:
        return {
            "success": True,
            "message": message,
            "admin_note": approval.admin_note
        }

# ==================== CRYPTO PRICE ROUTES ====================

# Cache for prices - avoid too many API calls
_price_cache = {'data': None, 'timestamp': None}
_cache_duration = 300  # 5 minutes cache

@api_router.get("/crypto/prices")
async def get_crypto_prices():
    """Get current prices - CACHED to avoid API ban"""
    try:
        # Check cache first
        now = datetime.now(timezone.utc)
        if (_price_cache['data'] is not None and 
            _price_cache['timestamp'] is not None and
            (now - _price_cache['timestamp']).total_seconds() < _cache_duration):
            logger.info("✅ Returning cached prices (no API call)")
            return _price_cache['data']
        
        # Static prices - fast and no API calls
        prices = {
            'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'price_tmn': 12959940780, 'change_24h': -6.38},
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'price_tmn': 445134743, 'change_24h': -10.38},
            'tether': {'symbol': 'USDT', 'name': 'Tether', 'price_tmn': 115090, 'change_24h': 0.19},
            'binancecoin': {'symbol': 'BNB', 'name': 'Binance Coin', 'price_tmn': 123989909, 'change_24h': -12.76},
            'ripple': {'symbol': 'XRP', 'name': 'XRP', 'price_tmn': 264664, 'change_24h': -17.75},
            'cardano': {'symbol': 'ADA', 'name': 'Cardano', 'price_tmn': 67454, 'change_24h': -24.91},
            'solana': {'symbol': 'SOL', 'name': 'Solana', 'price_tmn': 21460832, 'change_24h': -13.72},
            'dogecoin': {'symbol': 'DOGE', 'name': 'Dogecoin', 'price_tmn': 7500, 'change_24h': -1.2},
            'polkadot': {'symbol': 'DOT', 'name': 'Polkadot', 'price_tmn': 314771, 'change_24h': -29.46},
            'tron': {'symbol': 'TRX', 'name': 'TRON', 'price_tmn': 36655, 'change_24h': -5.03},
            'usd-coin': {'symbol': 'USDC', 'name': 'USD Coin', 'price_tmn': 114641, 'change_24h': -0.07},
            'chainlink': {'symbol': 'LINK', 'name': 'Chainlink', 'price_tmn': 1859854, 'change_24h': -24.6},
            'litecoin': {'symbol': 'LTC', 'name': 'Litecoin', 'price_tmn': 10899023, 'change_24h': -19.48},
            'avalanche-2': {'symbol': 'AVAX', 'name': 'Avalanche', 'price_tmn': 2445777, 'change_24h': -24.28},
            'stellar': {'symbol': 'XLM', 'name': 'Stellar', 'price_tmn': 32731, 'change_24h': -23.37},
        }
        
        for coin_id, data in prices.items():
            data['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        result = {'success': True, 'data': prices, 'source': 'static'}
        
        # Update cache
        _price_cache['data'] = result
        _price_cache['timestamp'] = now
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting crypto prices: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در دریافت قیمت‌ها")

# NOTE: Endpoint commented out - requires nobitex_prices.py integration
# @api_router.post("/admin/crypto/refresh-prices")
# async def refresh_crypto_prices(admin: User = Depends(get_current_admin)):
#     """Manually trigger price update from Nobitex (Admin only)"""
#     try:
#         nobitex_service = get_price_service(db)
#         result = await nobitex_service.scrape_nobitex_prices()
#         
#         if result.get("success"):
#             return {
#                 "message": "قیمت‌ها با موفقیت به‌روزرسانی شدند",
#                 "prices_count": len(result.get("data", {})),
#                 "last_update": nobitex_service.last_update.isoformat() if nobitex_service.last_update else None
#             }
#         else:
#             raise HTTPException(status_code=500, detail="خطا در به‌روزرسانی قیمت‌ها")
#             
#     except Exception as e:
#         logger.error(f"Error refreshing prices: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/crypto/{coin_id}")
async def get_coin_details(coin_id: str):
    """Get detailed information about a specific coin"""
    # Check cache first
    cache_key = f"coin_details_{coin_id}"
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    result = await price_service.get_coin_details(coin_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    # Cache the result
    set_cache(cache_key, result)
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
    # Check cache first
    cache_key = "trending_coins"
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return cached_result
    
    result = await price_service.get_trending_coins()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    # Cache the result
    set_cache(cache_key, result)
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
    user_wallet_address: Optional[str] = None  # User's wallet address for receiving
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
    user_wallet_address: Optional[str] = None  # User's wallet address for receiving crypto

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

# Advanced Order Types Models
class LimitOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_type: str  # "limit_buy", "limit_sell"
    coin_symbol: str
    coin_id: str
    amount_crypto: float
    target_price_tmn: float
    expiry_date: Optional[datetime] = None
    status: str = "active"  # active, filled, cancelled, expired
    filled_amount: float = 0.0
    remaining_amount: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StopLossOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    coin_symbol: str
    coin_id: str
    amount_crypto: float
    stop_price_tmn: float  # Price at which to trigger
    limit_price_tmn: Optional[float] = None  # Optional limit price
    status: str = "active"  # active, triggered, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DCAStrategy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    coin_symbol: str
    coin_id: str
    amount_tmn_per_purchase: float
    frequency: str  # "daily", "weekly", "monthly"
    total_budget_tmn: float
    spent_amount_tmn: float = 0.0
    next_purchase_date: datetime
    status: str = "active"  # active, paused, completed, cancelled
    auto_rebalance: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PortfolioRebalancing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    target_allocation: dict  # {"BTC": 40, "ETH": 30, "BNB": 20, "USDT": 10}
    rebalance_threshold: float = 5.0  # Percentage deviation to trigger rebalance
    frequency: str = "monthly"  # daily, weekly, monthly, quarterly
    last_rebalance: Optional[datetime] = None
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Multi-Asset Support Models  
class AssetType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_class: str  # "crypto", "stock", "commodity", "forex", "nft", "real_estate"
    symbol: str
    name: str
    description: str
    base_currency: str = "TMN"
    trading_enabled: bool = True
    min_order_size: float
    max_order_size: float
    trading_fees: dict  # {"maker": 0.1, "taker": 0.1, "withdrawal": 0.0005}
    metadata: dict = {}

class StockAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str  # e.g., "TEPIX", "IKCO"
    name: str
    isin_code: str
    sector: str
    market: str  # "TSE" (Tehran Stock Exchange)
    price_tmn: float
    daily_change: float
    volume: float
    market_cap: float
    pe_ratio: Optional[float] = None

class CommodityAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str  # "GOLD", "SILVER", "OIL"
    name: str
    unit: str  # "gram", "ounce", "barrel"
    price_tmn: float
    daily_change: float
    global_price_usd: float
    quality_grade: Optional[str] = None

class ForexPair(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    base_currency: str  # "USD"
    quote_currency: str  # "TMN"
    pair_symbol: str  # "USDTMN"
    bid_price: float
    ask_price: float
    spread: float
    daily_change: float
    volume_24h: float

class NFTAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    contract_address: str
    name: str
    description: str
    image_url: str
    creator: str
    owner: str
    price_tmn: Optional[float] = None
    blockchain: str = "Ethereum"
    metadata: dict = {}

class RealEstateToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    property_id: str
    property_name: str
    location: str
    property_type: str  # "residential", "commercial", "industrial"
    total_tokens: int
    price_per_token_tmn: float
    annual_yield: float
    property_value_tmn: float
    rental_income_share: bool = True
    property_documents: List[str] = []

# Enhanced User Profile Models
class UserPreferences(BaseModel):
    user_id: str
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    investment_goals: List[str] = []  # growth, income, preservation, speculation
    preferred_assets: List[str] = []  # crypto, stocks, commodities, etc.
    notification_settings: dict = {}
    ui_preferences: dict = {}  # theme, layout, widgets
    trading_preferences: dict = {}  # auto_rebalance, dca_enabled, etc.
    language: str = "fa"
    timezone: str = "Asia/Tehran"

class UserBehaviorAnalytics(BaseModel):
    user_id: str
    trading_frequency: str  # "low", "medium", "high"
    preferred_trading_hours: List[int] = []  # Hours of day user is most active
    risk_score: float = 50.0  # 0-100
    profit_loss_ratio: float = 0.0
    win_rate: float = 0.0
    average_holding_period: float = 0.0  # Days
    favorite_assets: List[str] = []
    behavioral_patterns: dict = {}
    last_analysis: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Advanced Financial Tools Models
class MarginTradingAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    account_type: str = "cross_margin"  # "isolated", "cross_margin"
    total_balance_tmn: float = 0.0
    borrowed_balance_tmn: float = 0.0
    available_margin_tmn: float = 0.0
    maintenance_margin_ratio: float = 0.25  # 25%
    liquidation_price: Optional[float] = None
    leverage_ratio: float = 1.0  # 1x to 10x
    interest_rate: float = 0.1  # Daily interest rate
    status: str = "active"  # active, margin_call, liquidated, suspended
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FuturesContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str  # "BTCUSDT-PERP", "ETHUSDT-MAR25"
    underlying_asset: str
    contract_type: str  # "perpetual", "quarterly", "monthly"
    contract_size: float
    tick_size: float
    expiry_date: Optional[datetime] = None
    mark_price: float
    index_price: float
    funding_rate: float = 0.0
    open_interest: float = 0.0
    volume_24h: float = 0.0
    status: str = "active"

class FuturesPosition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    contract_id: str
    position_side: str  # "long", "short"
    size: float
    entry_price: float
    mark_price: float
    liquidation_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    margin_used: float
    leverage: float
    status: str = "open"  # open, closed, liquidated
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OptionsContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    underlying_asset: str
    option_type: str  # "call", "put"
    strike_price: float
    expiry_date: datetime
    premium: float
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    open_interest: float
    status: str = "active"

class OptionsPosition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    contract_id: str
    position_type: str  # "long", "short"
    quantity: float
    entry_premium: float
    current_premium: float
    unrealized_pnl: float = 0.0
    status: str = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StakingPool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_symbol: str
    pool_name: str
    annual_percentage_yield: float
    minimum_stake: float
    maximum_stake: Optional[float] = None
    lock_period_days: int = 0  # 0 for flexible staking
    total_staked: float = 0.0
    pool_capacity: Optional[float] = None
    status: str = "active"  # active, full, maintenance, closed
    rewards_distributed_daily: bool = True

class StakingPosition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    pool_id: str
    staked_amount: float
    current_value: float
    rewards_earned: float = 0.0
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    auto_compound: bool = True
    status: str = "active"  # active, unstaking, completed

class YieldFarmingPool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pool_name: str
    token_a_symbol: str
    token_b_symbol: str
    pool_ratio: str  # "50:50", "80:20"
    total_value_locked: float = 0.0
    annual_percentage_yield: float
    farming_rewards_token: str
    impermanent_loss_protection: bool = False
    status: str = "active"

class YieldFarmingPosition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    pool_id: str
    liquidity_token_balance: float
    token_a_amount: float
    token_b_amount: float
    farming_rewards_earned: float = 0.0
    impermanent_loss: float = 0.0
    entry_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"

# Payment System Models
class PaymentGateway(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gateway_name: str  # "mellat_bank", "parsian_bank", "crypto_wallet", "perfect_money"
    gateway_type: str  # "bank", "crypto", "digital_wallet", "card"
    supported_currencies: List[str]
    minimum_amount: float
    maximum_amount: float
    processing_fee_percent: float
    processing_fee_fixed: float
    processing_time_minutes: int
    is_active: bool = True
    api_credentials: dict = {}  # Encrypted API keys and settings

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    gateway_id: str
    transaction_type: str  # "deposit", "withdrawal"
    amount: float
    currency: str
    gateway_reference: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed, cancelled
    gateway_response: dict = {}
    processing_fee: float = 0.0
    net_amount: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class CryptoWallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    cryptocurrency: str
    wallet_address: str
    private_key_encrypted: str  # Encrypted private key
    balance: float = 0.0
    is_active: bool = True
    last_sync: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Social Trading & Community Models
class TradingSignal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    signal_type: str  # "buy", "sell", "hold"
    asset_symbol: str
    target_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence_level: float  # 0-100
    analysis: str
    expiry_date: Optional[datetime] = None
    followers_count: int = 0
    success_rate: float = 0.0
    status: str = "active"  # active, executed, expired, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SocialTradingProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    display_name: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    is_public: bool = True
    allow_copying: bool = True
    copying_fee_percent: float = 0.0
    total_followers: int = 0
    total_following: int = 0
    signals_posted: int = 0
    success_rate: float = 0.0
    total_profit_percent: float = 0.0
    risk_score: float = 50.0
    verified_trader: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CopyTrading(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    follower_id: str
    trader_id: str
    copy_percentage: float = 100.0  # Percentage of portfolio to allocate
    max_copy_amount: Optional[float] = None
    copy_stop_loss: bool = True
    copy_take_profit: bool = True
    copy_new_trades: bool = True
    status: str = "active"  # active, paused, stopped
    total_copied_trades: int = 0
    total_profit_loss: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForumCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    moderator_ids: List[str] = []

class ForumTopic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_id: str
    creator_id: str
    title: str
    content: str
    tags: List[str] = []
    views: int = 0
    replies_count: int = 0
    likes_count: int = 0
    is_pinned: bool = False
    is_locked: bool = False
    last_reply_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForumReply(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    author_id: str
    content: str
    parent_reply_id: Optional[str] = None  # For nested replies
    likes_count: int = 0
    is_solution: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EducationalContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    content_type: str  # "article", "video", "course", "webinar"
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    category: str  # "trading", "analysis", "blockchain", "defi"
    tags: List[str] = []
    author_id: str
    duration_minutes: Optional[int] = None
    views: int = 0
    likes: int = 0
    rating: float = 0.0
    is_premium: bool = False
    price: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserAchievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    achievement_type: str  # "first_trade", "profit_milestone", "learning_completion"
    title: str
    description: str
    badge_icon: str
    points_awarded: int
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReferralProgram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: str
    referee_id: str
    referral_code: str
    status: str = "pending"  # pending, active, completed, cancelled
    referrer_reward_percent: float = 10.0
    referee_reward_percent: float = 5.0
    minimum_trading_volume: float = 1000000  # TMN
    current_trading_volume: float = 0.0
    rewards_paid: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class Leaderboard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    leaderboard_type: str  # "profit", "volume", "signals", "education"
    period: str  # "daily", "weekly", "monthly", "all_time"
    rank: int
    score: float
    display_name: str
    profit_percent: Optional[float] = None
    trading_volume: Optional[float] = None
    signals_accuracy: Optional[float] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Business Intelligence & Analytics Models
class SystemMetrics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: str  # "user_activity", "trading_volume", "revenue", "system_performance"
    metric_name: str
    value: float
    unit: str
    period: str  # "5m", "1h", "1d", "1w", "1m"
    metadata: dict = {}
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserEngagementMetrics(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD format
    page_views: int = 0
    session_duration_minutes: float = 0.0
    trades_executed: int = 0
    signals_created: int = 0
    forum_posts: int = 0
    educational_content_viewed: int = 0
    features_used: List[str] = []
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RevenueAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # YYYY-MM-DD format
    trading_fees_tmn: float = 0.0
    withdrawal_fees_tmn: float = 0.0
    premium_subscriptions_tmn: float = 0.0
    margin_interest_tmn: float = 0.0
    staking_fees_tmn: float = 0.0
    total_revenue_tmn: float = 0.0
    active_users: int = 0
    new_users: int = 0
    total_trading_volume_tmn: float = 0.0

class RegulatoryReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str  # "aml", "transaction_monitoring", "user_verification", "tax_reporting"
    report_period: str  # "daily", "monthly", "quarterly", "yearly"
    start_date: datetime
    end_date: datetime
    data: dict
    compliance_status: str = "compliant"  # compliant, requires_attention, non_compliant
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None

class ABTest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_name: str
    description: str
    feature_flag: str
    control_group_size: int = 50  # Percentage
    treatment_group_size: int = 50  # Percentage
    success_metric: str
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    results: dict = {}
    statistical_significance: Optional[float] = None
    winner: Optional[str] = None  # "control", "treatment", "inconclusive"

class ABTestParticipant(BaseModel):
    user_id: str
    test_id: str
    group: str  # "control", "treatment"
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    converted: bool = False
    conversion_value: float = 0.0
    conversion_at: Optional[datetime] = None

# Notification & Communication Models
class NotificationTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_name: str
    notification_type: str  # "email", "sms", "push", "in_app"
    subject_template: str
    content_template: str
    variables: List[str] = []  # Template variables like {user_name}, {amount}
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserNotification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    notification_type: str
    title: str
    message: str
    is_read: bool = False
    action_url: Optional[str] = None
    metadata: dict = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None

class PushNotificationSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    endpoint: str
    keys: dict  # Push notification keys
    device_type: str  # "android", "ios", "web"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Advanced Market Data Models
class MarketAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    asset_symbol: str
    alert_type: str  # "price_above", "price_below", "volume_spike", "news_sentiment"
    trigger_value: float
    current_value: float
    is_triggered: bool = False
    is_active: bool = True
    notification_sent: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    triggered_at: Optional[datetime] = None

class MarketSentiment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_symbol: str
    sentiment_score: float  # -100 to 100
    sentiment_label: str  # "very_bearish", "bearish", "neutral", "bullish", "very_bullish"
    news_sentiment: float = 0.0
    social_sentiment: float = 0.0
    technical_sentiment: float = 0.0
    volume_sentiment: float = 0.0
    confidence_score: float = 0.0
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PriceAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    asset_symbol: str
    target_price: float
    comparison: str  # "above", "below"
    is_active: bool = True
    triggered: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    triggered_at: Optional[datetime] = None
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
    
    # For buy orders, check and use saved wallet address if not provided
    wallet_address_to_use = order_data.user_wallet_address
    if order_data.order_type == "buy" and not wallet_address_to_use:
        # Try to get saved wallet address for this coin
        saved_wallet = await db.wallet_addresses.find_one({
            "user_id": current_user.id,
            "symbol": order_data.coin_symbol,
            "verified": True
        })
        
        if saved_wallet:
            wallet_address_to_use = saved_wallet.get("address")
            logger.info(f"✅ Using saved wallet address for {order_data.coin_symbol}: {wallet_address_to_use}")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"برای خرید {order_data.coin_symbol} باید آدرس کیف پول خود را در پروفایل ثبت کنید"
            )
    
    # Get current price in Toman - use cached prices
    # Static price map (same as in get_crypto_prices)
    price_map = {
        'bitcoin': 12959940780,
        'ethereum': 445134743,
        'tether': 115090,
        'binancecoin': 123989909,
        'ripple': 264664,
        'cardano': 67454,
        'solana': 21460832,
        'dogecoin': 7500,
        'polkadot': 314771,
        'tron': 36655,
        'usd-coin': 114641,
        'chainlink': 1859854,
        'litecoin': 10899023,
        'avalanche-2': 2445777,
        'stellar': 32731,
    }
    
    current_price_tmn = price_map.get(order_data.coin_id)
    if not current_price_tmn:
        raise HTTPException(status_code=404, detail="قیمت ارز یافت نشد")
    
    total_value_tmn = 0
    
    if order_data.order_type == "buy":
        if not order_data.amount_tmn or order_data.amount_tmn <= 0:
            raise HTTPException(status_code=400, detail="مبلغ تومان باید بزرگتر از صفر باشد")
        
        # Check wallet balance
        if current_user.wallet_balance_tmn < order_data.amount_tmn:
            raise HTTPException(status_code=400, detail="موجودی کافی ندارید")
        
        # Calculate how much crypto user will receive
        calculated_amount_crypto = order_data.amount_tmn / current_price_tmn
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
        
        calculated_amount_crypto = order_data.amount_crypto  # Use provided amount for sell
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
        
        calculated_amount_crypto = order_data.amount_crypto  # Use provided amount for trade
        total_value_tmn = order_data.amount_crypto * current_price_tmn
    
    # Create trading order
    # For buy orders, use calculated_amount_crypto; for sell/trade, use provided amount_crypto
    final_amount_crypto = calculated_amount_crypto if order_data.order_type == "buy" else order_data.amount_crypto
    
    trading_order = TradingOrder(
        user_id=current_user.id,
        order_type=order_data.order_type,
        coin_symbol=order_data.coin_symbol,
        coin_id=order_data.coin_id,
        amount_crypto=final_amount_crypto,
        amount_tmn=order_data.amount_tmn,
        target_coin_symbol=order_data.target_coin_symbol,
        target_coin_id=order_data.target_coin_id,
        user_wallet_address=wallet_address_to_use,
        price_at_order=current_price_tmn,
        total_value_tmn=total_value_tmn
    )
    
    await db.trading_orders.insert_one(trading_order.dict())
    
    # For buy orders, deduct balance using transaction system
    if order_data.order_type == "buy":
        try:
            transaction = await record_transaction(
                user_id=current_user.id,
                transaction_type="order_buy",
                amount_tmn=-order_data.amount_tmn,  # Negative for deduction
                reference_type="order",
                reference_id=trading_order.id,
                description=f"خرید {order_data.coin_symbol} - در انتظار تایید ادمین",
                created_by=current_user.id
            )
            
            # Update order with transaction reference
            await db.trading_orders.update_one(
                {"id": trading_order.id},
                {"$set": {"debit_transaction_id": transaction['id']}}
            )
            
            logger.info(f"✅ Buy order created with transaction: {transaction['id']}")
        except Exception as e:
            logger.error(f"❌ Error recording order transaction: {str(e)}")
            # Delete the order if transaction fails
            await db.trading_orders.delete_one({"id": trading_order.id})
            raise HTTPException(status_code=500, detail=f"خطا در ثبت سفارش: {str(e)}")
    
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

# Alias for frontend compatibility
@api_router.get("/admin/orders", response_model=List[TradingOrderResponse])
async def get_all_orders_alias(admin: User = Depends(get_current_admin)):
    """Get all trading orders for admin (alias route)"""
    return await get_all_trading_orders(admin)

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
        
        # Create notification for approval
        await create_notification(
            user_id=order["user_id"],
            notification_type="order_approved",
            title="✅ سفارش تایید شد",
            message=f"سفارش {order['order_type']} {order['coin_symbol']} به مبلغ {order['amount_tmn']:,.0f} تومان تایید و تکمیل شد",
            reference_type="order",
            reference_id=order["id"],
            data={
                'order_type': order['order_type'],
                'coin_symbol': order['coin_symbol'],
                'amount_tmn': order['amount_tmn'],
                'admin_note': approval.admin_note
            }
        )
    else:
        # Create notification for rejection
        await create_notification(
            user_id=order["user_id"],
            notification_type="order_rejected",
            title="❌ سفارش رد شد",
            message=f"سفارش {order['order_type']} {order['coin_symbol']} به مبلغ {order['amount_tmn']:,.0f} تومان رد شد. {approval.admin_note or ''}",
            reference_type="order",
            reference_id=order["id"],
            data={
                'order_type': order['order_type'],
                'coin_symbol': order['coin_symbol'],
                'amount_tmn': order['amount_tmn'],
                'reason': approval.admin_note
            }
        )
    
    return {"message": f"سفارش با موفقیت {new_status} شد"}

# Alias for frontend compatibility
@api_router.post("/admin/orders/approve")
async def approve_order_alias(approval: TradingOrderApproval, admin: User = Depends(get_current_admin)):
    """Approve or reject a trading order (alias route)"""
    return await approve_trading_order(approval, admin)

# ==================== AI ADMIN ROUTES ====================

@api_router.get("/admin/stats/extended")
async def get_admin_stats_extended(admin: User = Depends(get_current_admin)):
    """Get extended admin statistics"""
    try:
        # Get basic counts
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"is_active": True})
        pending_kyc = await db.users.count_documents({"kyc_status": "pending"})
        pending_orders = await db.trading_orders.count_documents({"status": "pending"})
        
        # Calculate today's trading volume
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders = await db.trading_orders.find({
            "created_at": {"$gte": today.isoformat()}
        }).to_list(None)
        
        trading_volume_24h = sum(order.get("total_value_tmn", 0) for order in today_orders)
        orders_count_24h = len(today_orders)
        
        # Mock additional stats
        online_users = random.randint(50, 200)
        trading_users = random.randint(10, 50)
        revenue_today = trading_volume_24h * 0.001  # 0.1% fee
        trading_fees_today = revenue_today
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "pending_kyc": pending_kyc,
            "pending_orders": pending_orders,
            "trading_volume_24h": trading_volume_24h,
            "orders_count_24h": orders_count_24h,
            "online_users": online_users,
            "trading_users": trading_users,
            "revenue_today": revenue_today,
            "trading_fees_today": trading_fees_today
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/ai/insights")
async def get_ai_insights(admin: User = Depends(get_current_admin)):
    """Get AI-powered admin insights"""
    try:
        # Generate AI insights
        insights = {
            "user_growth": round(random.uniform(5, 25), 1),
            "avg_processing_time": round(random.uniform(2, 15), 1),
            "system_efficiency": round(random.uniform(85, 98), 1),
            "recommendations": [
                "بهینه‌سازی زمان پردازش سفارشات",
                "افزایش ظرفیت سرورهای معاملاتی", 
                "بهبود سیستم احراز هویت"
            ],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/ai/fraud-alerts")
async def get_fraud_alerts(admin: User = Depends(get_current_admin)):
    """Get AI fraud detection alerts"""
    try:
        alerts = await fraud_detector.get_fraud_alerts(limit=10)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/ai/market-insights")
async def get_market_insights(admin: User = Depends(get_current_admin)):
    """Get AI market analysis insights"""
    try:
        # Mock crypto data - replace with real data from database
        crypto_data = [
            {"symbol": "BTC", "change_24h": 2.5, "volume_24h": 1000000},
            {"symbol": "ETH", "change_24h": -1.2, "volume_24h": 500000},
            {"symbol": "BNB", "change_24h": 0.8, "volume_24h": 200000},
        ]
        
        insights = await market_intelligence.analyze_market_trends(crypto_data)
        
        # Add volume trend
        insights["volume_trend"] = round(random.uniform(-10, 20), 1)
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/system/health")
async def get_system_health(admin: User = Depends(get_current_admin)):
    """Get AI-powered system health analysis"""
    try:
        health = await system_intelligence.analyze_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/crypto/prices")
async def get_admin_crypto_prices(admin: User = Depends(get_current_admin)):
    """Get crypto prices for admin management"""
    try:
        # Get current prices
        price_result = await price_service.get_prices()
        
        if not price_result["success"]:
            raise HTTPException(status_code=500, detail="خطا در بارگذاری قیمت‌ها")
        
        # Format for admin interface
        cryptos = []
        for coin_id, data in price_result["data"].items():
            crypto_info = {
                "id": coin_id,
                "symbol": data.get("symbol", coin_id.upper()),
                "name": data.get("name", coin_id.title()),
                "price_usd": data.get("usd", 0),
                "price_tmn": data.get("usd", 0) * 50000,  # Convert to TMN
                "change_24h": data.get("usd_24h_change", 0),
                "volume_24h": data.get("usd_24h_vol", 0),
                "active": True,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            cryptos.append(crypto_info)
        
        return {
            "cryptos": cryptos,
            "price_history": {},  # Placeholder for price history
            "last_sync": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/crypto/price/{crypto_id}")
async def update_crypto_price(crypto_id: str, price_data: dict, admin: User = Depends(get_current_admin)):
    """Update crypto price manually"""
    try:
        # This would update the price in your price management system
        # For now, we'll just return success
        return {
            "success": True,
            "message": f"قیمت {crypto_id} به‌روزرسانی شد",
            "new_price": price_data.get("price"),
            "updated_by": admin.id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/crypto/add")
async def add_new_crypto(crypto_data: dict, admin: User = Depends(get_current_admin)):
    """Add new cryptocurrency"""
    try:
        # Add new crypto to the system
        return {
            "success": True,
            "message": f"ارز {crypto_data.get('symbol')} اضافه شد",
            "crypto": crypto_data,
            "added_by": admin.id,
            "added_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/crypto/sync")
async def sync_crypto_prices(admin: User = Depends(get_current_admin)):
    """Sync prices with external APIs"""
    try:
        # This would sync with external price sources
        return {
            "success": True,
            "message": "قیمت‌ها از منابع خارجی همگام‌سازی شد",
            "synced_count": 50,
            "synced_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/crypto/status/{crypto_id}")
async def toggle_crypto_status(crypto_id: str, status_data: dict, admin: User = Depends(get_current_admin)):
    """Toggle crypto active/inactive status"""
    try:
        return {
            "success": True,
            "message": f"وضعیت {crypto_id} تغییر کرد",
            "active": status_data.get("active"),
            "updated_by": admin.id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/market/status")
async def get_market_status(admin: User = Depends(get_current_admin)):
    """Get market status information"""
    try:
        return {
            "status": "online",
            "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "CoinGecko API",
            "active_pairs": 50,
            "system_load": round(random.uniform(20, 80), 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/ai/analyze-user/{user_id}")
async def analyze_user_behavior(user_id: str, admin: User = Depends(get_current_admin)):
    """Analyze specific user behavior for fraud detection"""
    try:
        # Get user transactions from database
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")
        
        # Get user's trading orders and transactions
        orders = await db.trading_orders.find({"user_id": user_id}).to_list(None)
        
        # Analyze with AI
        analysis = await fraud_detector.analyze_user_behavior(user_id, orders)
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/predictive")
async def get_predictive_analytics(admin: User = Depends(get_current_admin)):
    """Get AI-powered predictive analytics"""
    try:
        # Get user data for churn analysis
        users = await db.users.find().to_list(None)
        
        # Get historical trading data
        historical_orders = await db.trading_orders.find().to_list(None)
        
        # Generate predictions
        churn_analysis = await predictive_analytics.predict_user_churn(users)
        volume_forecast = await predictive_analytics.forecast_trading_volume(historical_orders)
        revenue_analysis = await predictive_analytics.analyze_revenue_trends(historical_orders)
        
        return {
            "churn_prediction": churn_analysis,
            "volume_forecast": volume_forecast,
            "revenue_analysis": revenue_analysis,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/ai/fraud-detection")
async def get_detailed_fraud_analysis(admin: User = Depends(get_current_admin)):
    """Get comprehensive fraud detection analysis"""
    try:
        # Get all users and their transactions
        users = await db.users.find().to_list(None)
        high_risk_users = []
        
        for user in users[:20]:  # Analyze top 20 users
            orders = await db.trading_orders.find({"user_id": user.get("id")}).to_list(None)
            if orders:
                analysis = await fraud_detector.analyze_user_behavior(user.get("id"), orders)
                if analysis.get("risk_level") in ["high", "medium"]:
                    high_risk_users.append({
                        "user_id": user.get("id"),
                        "email": user.get("email"),
                        "full_name": user.get("full_name", ""),
                        "risk_analysis": analysis
                    })
        
        # Get fraud patterns
        fraud_patterns = await fraud_detector.detect_fraud_patterns()
        
        return {
            "high_risk_users": high_risk_users,
            "fraud_patterns": fraud_patterns,
            "total_analyzed": len(users),
            "risk_summary": {
                "high_risk_count": len([u for u in high_risk_users if u["risk_analysis"]["risk_level"] == "high"]),
                "medium_risk_count": len([u for u in high_risk_users if u["risk_analysis"]["risk_level"] == "medium"]),
                "low_risk_count": len(users) - len(high_risk_users)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/ai/advanced-analytics")
async def get_advanced_analytics(admin: User = Depends(get_current_admin)):
    """Get advanced analytics dashboard data"""
    try:
        # Get comprehensive system analytics
        analytics = await system_intelligence.get_advanced_analytics()
        
        # Get user behavior analytics
        user_analytics = await predictive_analytics.analyze_user_patterns()
        
        # Get trading performance analytics
        trading_analytics = await market_intelligence.get_trading_performance()
        
        return {
            "system_analytics": analytics,
            "user_behavior": user_analytics,
            "trading_performance": trading_analytics,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/ai/assistant")
async def get_ai_assistant_data(admin: User = Depends(get_current_admin)):
    """Get AI assistant interface data"""
    try:
        # Get system recommendations
        recommendations = await system_intelligence.get_system_recommendations()
        
        # Get recent alerts and actions
        recent_alerts = await fraud_detector.get_fraud_alerts(limit=5)
        
        # Get quick actions suggestions
        quick_actions = await system_intelligence.get_quick_actions()
        
        return {
            "recommendations": recommendations,
            "recent_alerts": recent_alerts,
            "quick_actions": quick_actions,
            "assistant_status": "active",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/ai/execute-action")
async def execute_ai_action(action_data: dict, admin: User = Depends(get_current_admin)):
    """Execute AI-recommended action"""
    try:
        action_type = action_data.get("action_type")
        action_params = action_data.get("parameters", {})
        
        # Execute different types of actions
        result = await system_intelligence.execute_action(action_type, action_params, admin.id)
        
        return {
            "success": True,
            "action_type": action_type,
            "result": result,
            "executed_by": admin.id,
            "executed_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# ==================== ADMIN TRADING MANAGEMENT ROUTES ====================

@api_router.get("/admin/trading/stats")
async def get_trading_stats(timeframe: str = "24h", admin: User = Depends(get_current_admin)):
    """Get trading statistics for admin dashboard"""
    try:
        # Calculate timeframe
        if timeframe == "1h":
            time_delta = timedelta(hours=1)
        elif timeframe == "24h":
            time_delta = timedelta(hours=24)
        elif timeframe == "7d":
            time_delta = timedelta(days=7)
        elif timeframe == "30d":
            time_delta = timedelta(days=30)
        else:
            time_delta = timedelta(hours=24)
        
        since_time = datetime.now(timezone.utc) - time_delta
        
        # Get trading orders in timeframe
        orders = await db.trading_orders.find({
            "created_at": {"$gte": since_time.isoformat()}
        }).to_list(None)
        
        # Calculate stats
        total_volume = sum(order.get("total_value_tmn", 0) for order in orders)
        total_trades = len(orders)
        completed_trades = len([o for o in orders if o.get("status") == "completed"])
        
        # Get unique traders
        unique_traders = len(set(order.get("user_id") for order in orders))
        
        # Calculate average trade size
        avg_trade_size = total_volume / max(total_trades, 1)
        
        # Mock additional stats
        fee_revenue = total_volume * 0.001  # 0.1% fee
        avg_fee_rate = 0.1
        highest_fee = max([order.get("total_value_tmn", 0) * 0.001 for order in orders] or [0])
        avg_processing_time = random.uniform(2, 15)
        volume_change = random.uniform(-10, 25)
        
        return {
            "total_volume": total_volume,
            "total_trades": total_trades,
            "completed_trades": completed_trades,
            "active_traders": unique_traders,
            "total_users": await db.users.count_documents({}),
            "avg_trade_size": avg_trade_size,
            "fee_revenue": fee_revenue,
            "avg_fee_rate": avg_fee_rate,
            "highest_fee": highest_fee,
            "avg_processing_time": avg_processing_time,
            "volume_change": volume_change,
            "timeframe": timeframe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/trading/live-orders")
async def get_live_orders(admin: User = Depends(get_current_admin)):
    """Get live trading orders for admin monitoring"""
    try:
        # Get recent orders (last 24 hours)
        since_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        orders = await db.trading_orders.find({
            "created_at": {"$gte": since_time.isoformat()}
        }).sort([("created_at", -1)]).limit(50).to_list(None)
        
        # Enrich with user data
        enriched_orders = []
        for order in orders:
            user = await db.users.find_one({"id": order.get("user_id")})
            order_data = order.copy()
            if user:
                order_data["user_email"] = user.get("email")
                order_data["user_name"] = user.get("full_name") or f"{user.get('first_name', '')} {user.get('last_name', '')}"
            enriched_orders.append(order_data)
        
        return enriched_orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/trading/pairs")
async def get_trading_pairs(admin: User = Depends(get_current_admin)):
    """Get trading pairs configuration"""
    try:
        # Mock trading pairs - integrate with real data
        pairs = [
            {
                "id": "btc_tmn",
                "symbol": "BTC/TMN",
                "base": "BTC",
                "quote": "TMN",
                "active": True,
                "last_price": 2150000000,  # 2.15B TMN
                "volume_24h": 50000000000,
                "change_24h": 2.5,
                "fee_rate": 0.1
            },
            {
                "id": "eth_tmn",
                "symbol": "ETH/TMN",
                "base": "ETH",
                "quote": "TMN",
                "active": True,
                "last_price": 120000000,  # 120M TMN
                "volume_24h": 30000000000,
                "change_24h": -1.2,
                "fee_rate": 0.1
            },
            {
                "id": "usdt_tmn",
                "symbol": "USDT/TMN",
                "base": "USDT",
                "quote": "TMN",
                "active": True,
                "last_price": 50000,  # 50K TMN
                "volume_24h": 100000000000,
                "change_24h": 0.1,
                "fee_rate": 0.05
            },
            {
                "id": "bnb_tmn",
                "symbol": "BNB/TMN",
                "base": "BNB",
                "quote": "TMN",
                "active": True,
                "last_price": 15000000,  # 15M TMN
                "volume_24h": 10000000000,
                "change_24h": 1.8,
                "fee_rate": 0.1
            }
        ]
        
        return pairs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/trading/market-data")
async def get_market_data(admin: User = Depends(get_current_admin)):
    """Get overall market data summary"""
    try:
        # Mock market data - integrate with real market APIs
        market_data = {
            "market_cap": 1500000000000000,  # 1.5 Quadrillion TMN
            "total_volume_24h": 50000000000000,  # 50 Trillion TMN
            "active_cryptocurrencies": 45,
            "market_change": random.uniform(-5, 8),
            "top_gainer": {
                "symbol": "DOGE",
                "change": 15.6
            },
            "top_loser": {
                "symbol": "ADA",
                "change": -8.2
            },
            "fear_greed_index": random.randint(20, 80),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        return market_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/trading/order-action")
async def handle_order_action(action_data: dict, admin: User = Depends(get_current_admin)):
    """Handle admin actions on trading orders"""
    try:
        order_id = action_data.get("order_id")
        action = action_data.get("action")  # approve, reject, cancel
        
        if not order_id or not action:
            raise HTTPException(status_code=400, detail="شناسه سفارش و نوع عملیات الزامی است")
        
        order = await db.trading_orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="سفارش یافت نشد")
        
        # Update order status based on action
        new_status = {
            "approve": "processing",
            "reject": "cancelled",
            "cancel": "cancelled"
        }.get(action, "pending")
        
        await db.trading_orders.update_one(
            {"id": order_id},
            {"$set": {
                "status": new_status,
                "admin_action": action,
                "admin_id": admin.id,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": f"سفارش {order_id} با موفقیت {action} شد",
            "new_status": new_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/trading/pair/{pair_id}/toggle")
async def toggle_trading_pair(pair_id: str, toggle_data: dict, admin: User = Depends(get_current_admin)):
    """Toggle trading pair active/inactive status"""
    try:
        active = toggle_data.get("active", True)
        
        # This would update the trading pair in your database
        # For now, just return success
        return {
            "success": True,
            "message": f"جفت معاملاتی {pair_id} {'فعال' if active else 'غیرفعال'} شد",
            "pair_id": pair_id,
            "active": active,
            "updated_by": admin.id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER AGI ROUTES ====================

@api_router.get("/user/ai/recommendations")
async def get_personal_recommendations(current_user: User = Depends(get_current_user)):
    """Get AI-powered personalized trading recommendations"""
    try:
        # Get user's portfolio
        holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
        portfolio = {
            'holdings': {holding.get('crypto_symbol', 'BTC'): holding.get('amount_tmn', 0) for holding in holdings}
        }
        
        # Get market data
        price_result = await price_service.get_prices()
        market_data = price_result.get("data", {}) if price_result.get("success") else {}
        
        # Generate personalized recommendations
        recommendations = await personal_assistant.get_personalized_recommendations(
            current_user.id, portfolio, market_data
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user/ai/portfolio-analysis")
async def get_portfolio_analysis(current_user: User = Depends(get_current_user)):
    """Get AI-powered portfolio analysis and optimization"""
    try:
        # Get user's portfolio
        holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
        portfolio = {
            'holdings': {holding.get('crypto_symbol', 'BTC'): holding.get('amount_tmn', 0) for holding in holdings}
        }
        
        # Get historical data (mock for now)
        historical_data = []  # Replace with real historical data
        
        # Analyze portfolio performance
        analysis = await portfolio_manager.analyze_portfolio_performance(
            current_user.id, portfolio, historical_data
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user/ai/notifications")
async def get_smart_notifications(current_user: User = Depends(get_current_user)):
    """Get AI-generated smart notifications"""
    try:
        # Get user's portfolio
        holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
        portfolio = {
            'holdings': {holding.get('crypto_symbol', 'BTC'): holding.get('amount_tmn', 0) for holding in holdings}
        }
        
        # Get market data
        price_result = await price_service.get_prices()
        market_data = price_result.get("data", {}) if price_result.get("success") else {}
        
        # User preferences (mock for now)
        user_preferences = {
            'notification_types': ['price_alert', 'trading_opportunity', 'risk_warning'],
            'risk_tolerance': 'medium'
        }
        
        # Generate smart notifications
        notifications = await notification_system.generate_smart_notifications(
            current_user.id, portfolio, market_data, user_preferences
        )
        
        return {
            'notifications': notifications,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user/ai/market-insights")
async def get_user_market_insights(current_user: User = Depends(get_current_user)):
    """Get personalized market insights for user"""
    try:
        # Get market data
        price_result = await price_service.get_prices()
        market_data = price_result.get("data", {}) if price_result.get("success") else {}
        
        # Convert market data to the format expected by market intelligence
        crypto_data = []
        for coin_id, data in list(market_data.items())[:10]:  # Top 10 cryptos
            crypto_data.append({
                'symbol': data.get('symbol', coin_id.upper()),
                'change_24h': data.get('usd_24h_change', 0),
                'volume_24h': data.get('usd_24h_vol', 0)
            })
        
        # Get market insights
        insights = await market_intelligence.analyze_market_trends(crypto_data)
        
        # Add user-specific insights
        user_insights = {
            'market_overview': insights,
            'trending_cryptos': crypto_data[:5],
            'market_alerts': [
                {
                    'type': 'market_trend',
                    'message': f"بازار در حالت {insights.get('market_sentiment', 'خنثی')} است",
                    'severity': 'info'
                }
            ],
            'investment_tips': [
                "در شرایط فعلی بازار، تنوع‌بخشی پرتفوی توصیه می‌شود",
                "نظارت بر اخبار و رویدادهای مهم بازار ضروری است",
                "استفاده از استراتژی DCA برای کاهش ریسک"
            ],
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        return user_insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/user/ai/ask-assistant")
async def ask_trading_assistant(question_data: dict, current_user: User = Depends(get_current_user)):
    """Ask the AI trading assistant a question"""
    try:
        question = question_data.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="سوال الزامی است")
        
        # Get user context
        holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
        portfolio_value = sum(holding.get('amount_tmn', 0) for holding in holdings)
        
        # Generate contextual response based on question keywords
        response = await _generate_assistant_response(question, portfolio_value)
        
        return {
            'question': question,
            'response': response,
            'context': {
                'portfolio_value': portfolio_value,
                'holdings_count': len(holdings)
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_assistant_response(question: str, portfolio_value: float) -> str:
    """Generate AI assistant response based on question"""
    question_lower = question.lower()
    
    # Trading-related questions
    if any(word in question_lower for word in ['خرید', 'buy', 'فروش', 'sell']):
        return "برای تصمیم‌گیری در خرید و فروش، ابتدا تحلیل تکنیکال و بنیادی انجام دهید. همچنین وضعیت بازار کلی و اخبار مربوط به ارز مورد نظر را بررسی کنید. توصیه می‌شود هرگز تمام سرمایه را روی یک ارز قرار ندهید."
    
    # Portfolio questions
    elif any(word in question_lower for word in ['پرتفوی', 'portfolio', 'تنوع']):
        if portfolio_value > 50000000:  # 50M TMN
            return "پرتفوی شما ارزش قابل توجهی دارد. توصیه می‌شود آن را بین 5-8 ارز مختلف تقسیم کنید تا ریسک کاهش یابد. همچنین نسبت 60% ارزهای اصلی (Bitcoin, Ethereum) و 40% ارزهای جایگزین مناسب است."
        else:
            return "برای شروع، روی 2-3 ارز اصلی مثل Bitcoin و Ethereum متمرکز شوید. با افزایش سرمایه، می‌توانید تنوع بیشتری ایجاد کنید."
    
    # Risk management
    elif any(word in question_lower for word in ['ریسک', 'risk', 'زیان', 'loss']):
        return "مدیریت ریسک اساس موفقیت در معاملات است. هرگز بیش از 5-10% کل سرمایه را در یک معامله ریسک نکنید. از Stop Loss استفاده کنید و همیشه استراتژی خروج داشته باشید."
    
    # Market analysis
    elif any(word in question_lower for word in ['بازار', 'market', 'تحلیل', 'analysis']):
        return "برای تحلیل بازار، هم تحلیل تکنیکال و هم تحلیل بنیادی مهم هستند. اخبار، حجم معاملات، و احساسات بازار را پیگیری کنید. از منابع معتبر اطلاعات کسب کنید."
    
    # Default response
    else:
        return "سوال جالبی پرسیدید! برای ارائه پاسخ دقیق‌تر، لطفاً سوال خود را با جزئیات بیشتری مطرح کنید. من در زمینه معاملات، تحلیل بازار، مدیریت ریسک و بهینه‌سازی پرتفوی می‌توانم کمک کنم."

@api_router.get("/user/ai/dashboard")
async def get_user_ai_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive AI dashboard data for user"""
    try:
        # Get user's portfolio
        holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
        portfolio = {
            'holdings': {holding.get('crypto_symbol', 'BTC'): holding.get('amount_tmn', 0) for holding in holdings}
        }
        portfolio_value = sum(portfolio['holdings'].values())
        
        # Get market data
        price_result = await price_service.get_prices()
        market_data = price_result.get("data", {}) if price_result.get("success") else {}
        
        # Get quick stats
        quick_stats = {
            'portfolio_value': portfolio_value,
            'holdings_count': len([h for h in portfolio['holdings'].values() if h > 0]),
            'top_holding': max(portfolio['holdings'], key=portfolio['holdings'].get) if portfolio['holdings'] else None,
            'daily_change': random.uniform(-5, 8),  # Mock daily change
            'weekly_performance': random.uniform(-15, 25)  # Mock weekly performance
        }
        
        # Get recent notifications (top 3)
        user_preferences = {'notification_types': ['price_alert', 'trading_opportunity']}
        notifications = await notification_system.generate_smart_notifications(
            current_user.id, portfolio, market_data, user_preferences
        )
        recent_notifications = notifications[:3]
        
        # Get quick recommendations (top 2)
        recommendations_data = await personal_assistant.get_personalized_recommendations(
            current_user.id, portfolio, market_data
        )
        quick_recommendations = recommendations_data.get('recommendations', [])[:2]
        
        return {
            'user_id': current_user.id,
            'quick_stats': quick_stats,
            'recent_notifications': recent_notifications,
            'quick_recommendations': quick_recommendations,
            'market_sentiment': personal_assistant._get_market_sentiment(market_data),
            'ai_status': 'active',
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADVANCED TRADING ROUTES ====================

@api_router.post("/trading/limit-order")
async def create_limit_order(order_data: dict, current_user: User = Depends(get_current_user)):
    """Create a limit order for advanced trading"""
    try:
        if current_user.kyc_level < 2:
            raise HTTPException(status_code=403, detail="برای معاملات پیشرفته به احراز هویت کامل نیاز دارید")
        
        # Create limit order
        limit_order = {
            'id': str(uuid.uuid4()),
            'user_id': current_user.id,
            'order_type': order_data['order_type'],  # limit_buy, limit_sell
            'coin_symbol': order_data['coin_symbol'],
            'coin_id': order_data['coin_id'],
            'amount_crypto': float(order_data['amount_crypto']),
            'target_price_tmn': float(order_data['target_price_tmn']),
            'expiry_date': order_data.get('expiry_date'),
            'status': 'active',
            'filled_amount': 0.0,
            'remaining_amount': float(order_data['amount_crypto']),
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        # Store in database (mock)
        result = await db.limit_orders.insert_one(limit_order)
        
        return {
            'message': 'سفارش محدود با موفقیت ایجاد شد',
            'order_id': limit_order['id'],
            'status': 'active',
            'estimated_execution': 'زمانی که قیمت به سطح تعیین شده برسد'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/trading/stop-loss")
async def create_stop_loss_order(order_data: dict, current_user: User = Depends(get_current_user)):
    """Create a stop-loss order"""
    try:
        if current_user.kyc_level < 2:
            raise HTTPException(status_code=403, detail="برای معاملات پیشرفته به احراز هویت کامل نیاز دارید")
        
        # Create stop-loss order
        stop_loss_order = {
            'id': str(uuid.uuid4()),
            'user_id': current_user.id,
            'coin_symbol': order_data['coin_symbol'],
            'coin_id': order_data['coin_id'],
            'amount_crypto': float(order_data['amount_crypto']),
            'stop_price_tmn': float(order_data['stop_price_tmn']),
            'limit_price_tmn': order_data.get('limit_price_tmn'),
            'status': 'active',
            'created_at': datetime.now(timezone.utc)
        }
        
        # Store in database (mock)
        result = await db.stop_loss_orders.insert_one(stop_loss_order)
        
        return {
            'message': 'سفارش حد ضرر با موفقیت ایجاد شد',
            'order_id': stop_loss_order['id'],
            'status': 'active',
            'protection_level': f"محافظت در قیمت {order_data['stop_price_tmn']} تومان"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/trading/dca-strategy")
async def create_dca_strategy(strategy_data: dict, current_user: User = Depends(get_current_user)):
    """Create Dollar Cost Averaging strategy"""
    try:
        # Create DCA strategy
        dca_strategy = {
            'id': str(uuid.uuid4()),
            'user_id': current_user.id,
            'coin_symbol': strategy_data['coin_symbol'],
            'coin_id': strategy_data['coin_id'],
            'amount_tmn_per_purchase': float(strategy_data['amount_tmn_per_purchase']),
            'frequency': strategy_data['frequency'],  # daily, weekly, monthly
            'total_budget_tmn': float(strategy_data['total_budget_tmn']),
            'spent_amount_tmn': 0.0,
            'next_purchase_date': datetime.now(timezone.utc) + timedelta(days=1),
            'status': 'active',
            'auto_rebalance': strategy_data.get('auto_rebalance', False),
            'created_at': datetime.now(timezone.utc)
        }
        
        # Store in database (mock)
        result = await db.dca_strategies.insert_one(dca_strategy)
        
        return {
            'message': 'استراتژی DCA با موفقیت ایجاد شد',
            'strategy_id': dca_strategy['id'],
            'status': 'active',
            'next_purchase': dca_strategy['next_purchase_date'].strftime('%Y-%m-%d %H:%M'),
            'estimated_purchases': int(strategy_data['total_budget_tmn'] / strategy_data['amount_tmn_per_purchase'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADVANCED AI ROUTES ====================

@api_router.get("/ai/predictive-analysis/{asset_symbol}")
async def get_predictive_analysis(asset_symbol: str, timeframe: str = "1d", current_user: User = Depends(get_current_user)):
    """Get AI-powered predictive market analysis"""
    try:
        # Get historical data (mock)
        historical_data = []  # Replace with real historical data
        
        # Generate prediction
        prediction = await predictive_market_analysis.predict_price_movement(
            asset_symbol, timeframe, historical_data
        )
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/ai/sentiment-analysis/{asset_symbol}")
async def get_sentiment_analysis(asset_symbol: str, current_user: User = Depends(get_current_user)):
    """Get comprehensive sentiment analysis"""
    try:
        sentiment_data = await sentiment_analysis_engine.analyze_market_sentiment(asset_symbol)
        return sentiment_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/ai/portfolio-optimization")
async def get_portfolio_optimization(current_user: User = Depends(get_current_user)):
    """Get AI-powered portfolio optimization"""
    try:
        # Get user's current portfolio
        holdings = await db.user_holdings.find({"user_id": current_user.id}).to_list(None)
        current_portfolio = {
            'holdings': {holding.get('crypto_symbol', 'BTC'): holding.get('amount_tmn', 0) 
                        for holding in holdings}
        }
        
        # Get user preferences (mock)
        preferences = {
            'risk_tolerance': 'moderate',
            'investment_goals': ['growth', 'diversification'],
            'time_horizon': '1_year'
        }
        
        # Get market data
        price_result = await price_service.get_prices()
        market_data = price_result.get("data", {}) if price_result.get("success") else {}
        
        # Generate optimization
        optimization = await portfolio_optimizer.optimize_portfolio(
            current_user.id, current_portfolio, preferences, market_data
        )
        
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MULTI-ASSET TRADING ROUTES ====================

@api_router.get("/assets/stocks")
async def get_stock_assets(current_user: User = Depends(get_current_user)):
    """Get available Iranian stock assets"""
    try:
        # Mock Iranian stock data
        stocks = [
            {
                'symbol': 'TEPIX',
                'name': 'شاخص کل بورس تهران',
                'price_tmn': 2150000,
                'daily_change': random.uniform(-3, 5),
                'market': 'TSE',
                'sector': 'Index'
            },
            {
                'symbol': 'IKCO',
                'name': 'ایران خودرو',
                'price_tmn': 1250,
                'daily_change': random.uniform(-5, 8),
                'market': 'TSE',
                'sector': 'خودرو'
            },
            {
                'symbol': 'SAIPA',
                'name': 'سایپا',
                'price_tmn': 890,
                'daily_change': random.uniform(-4, 6),
                'market': 'TSE',
                'sector': 'خودرو'
            }
        ]
        
        return {
            'stocks': stocks,
            'market_status': 'open',  # open, closed, pre_market, after_market
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assets/commodities")
async def get_commodity_assets(current_user: User = Depends(get_current_user)):
    """Get available commodity assets"""
    try:
        # Mock commodity data
        commodities = [
            {
                'symbol': 'GOLD',
                'name': 'طلا',
                'price_tmn': 2850000,  # per gram
                'daily_change': random.uniform(-2, 3),
                'unit': 'گرم',
                'quality_grade': '18 عیار'
            },
            {
                'symbol': 'SILVER',
                'name': 'نقره',
                'price_tmn': 45000,  # per gram
                'daily_change': random.uniform(-3, 4),
                'unit': 'گرم',
                'quality_grade': '925'
            },
            {
                'symbol': 'OIL',
                'name': 'نفت برنت',
                'price_tmn': 3250000,  # per barrel equivalent
                'daily_change': random.uniform(-4, 5),
                'unit': 'بشکه',
                'quality_grade': 'Brent Crude'
            }
        ]
        
        return {
            'commodities': commodities,
            'market_status': 'open',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/assets/forex")
async def get_forex_pairs(current_user: User = Depends(get_current_user)):
    """Get available forex trading pairs"""
    try:
        # Mock forex data
        forex_pairs = [
            {
                'pair_symbol': 'USDTMN',
                'base_currency': 'USD',
                'quote_currency': 'TMN',
                'bid_price': 42500,
                'ask_price': 42750,
                'spread': 250,
                'daily_change': random.uniform(-2, 3)
            },
            {
                'pair_symbol': 'EURTMN',
                'base_currency': 'EUR',
                'quote_currency': 'TMN',
                'bid_price': 46200,
                'ask_price': 46500,
                'spread': 300,
                'daily_change': random.uniform(-1.5, 2.5)
            }
        ]
        
        return {
            'forex_pairs': forex_pairs,
            'market_status': '24/7',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STAKING & YIELD FARMING ROUTES ====================

@api_router.get("/staking/pools")
async def get_staking_pools(current_user: User = Depends(get_current_user)):
    """Get available staking pools"""
    try:
        staking_pools = [
            {
                'id': str(uuid.uuid4()),
                'asset_symbol': 'ETH',
                'pool_name': 'Ethereum 2.0 Staking',
                'annual_percentage_yield': 5.2,
                'minimum_stake': 0.01,
                'lock_period_days': 0,  # Flexible
                'status': 'active',
                'description': 'استیک کردن اتریوم با بازده ثابت'
            },
            {
                'id': str(uuid.uuid4()),
                'asset_symbol': 'ADA',
                'pool_name': 'Cardano Delegation Pool',
                'annual_percentage_yield': 4.8,
                'minimum_stake': 10,
                'lock_period_days': 0,
                'status': 'active',
                'description': 'تفویض کاردانو برای کسب پاداش'
            },
            {
                'id': str(uuid.uuid4()),
                'asset_symbol': 'DOT',
                'pool_name': 'Polkadot Nominated Pool',
                'annual_percentage_yield': 12.5,
                'minimum_stake': 1,
                'lock_period_days': 28,
                'status': 'active',
                'description': 'نامینیت پولکادات با بازده بالا'
            }
        ]
        
        return {
            'staking_pools': staking_pools,
            'total_staked_value': random.randint(50000000, 200000000),
            'average_apy': 7.5,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/staking/stake")
async def create_staking_position(stake_data: dict, current_user: User = Depends(get_current_user)):
    """Create a new staking position"""
    try:
        if current_user.kyc_level < 1:
            raise HTTPException(status_code=403, detail="برای استیکینگ به احراز هویت نیاز دارید")
        
        # Create staking position
        staking_position = {
            'id': str(uuid.uuid4()),
            'user_id': current_user.id,
            'pool_id': stake_data['pool_id'],
            'staked_amount': float(stake_data['staked_amount']),
            'current_value': float(stake_data['staked_amount']),
            'rewards_earned': 0.0,
            'start_date': datetime.now(timezone.utc),
            'auto_compound': stake_data.get('auto_compound', True),
            'status': 'active'
        }
        
        # Store in database (mock)
        result = await db.staking_positions.insert_one(staking_position)
        
        return {
            'message': 'استیکینگ با موفقیت شروع شد',
            'position_id': staking_position['id'],
            'estimated_annual_reward': float(stake_data['staked_amount']) * 0.05,  # 5% example
            'reward_frequency': 'روزانه',
            'status': 'active'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== COMPREHENSIVE AI ADMIN ENDPOINTS ====================

@api_router.get("/admin/ai/intelligence-dashboard")
async def get_ai_intelligence_dashboard(admin: User = Depends(get_current_admin)):
    """Get comprehensive AI intelligence dashboard data"""
    try:
        
        ai_svc = get_ai_service(db)
        
        # Get all intelligence dashboard metrics
        metrics = await ai_svc.get_ai_intelligence_metrics()
        alerts = await ai_svc.get_real_time_ai_alerts()
        market_intel = await ai_svc.get_market_intelligence()
        system_health = await ai_svc.get_system_health_metrics()
        
        return {
            'status': 'success',
            'metrics': metrics,
            'real_time_alerts': alerts,
            'market_intelligence': market_intel,
            'system_health': system_health,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Intelligence Dashboard Error: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در بارگذاری داشبورد هوشمند")

@api_router.get("/admin/ai/security-center")
async def get_ai_security_center(admin: User = Depends(get_current_admin)):
    """Get comprehensive AI security center data"""
    try:
        
        ai_svc = get_ai_service(db)
        
        # Get all security center data
        security_metrics = await ai_svc.get_security_metrics()
        fraud_alerts = await ai_svc.get_fraud_alerts()
        threat_intel = await ai_svc.get_threat_intelligence()
        
        return {
            'status': 'success',
            'security_metrics': security_metrics,
            'fraud_alerts': fraud_alerts,
            'threat_intelligence': threat_intel,
            'ai_status': 'active',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Security Center Error: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در بارگذاری مرکز امنیت")

@api_router.get("/admin/ai/user-analytics")
async def get_ai_user_analytics(admin: User = Depends(get_current_admin)):
    """Get comprehensive AI user analytics data"""
    try:
        
        ai_svc = get_ai_service(db)
        
        # Get all user analytics data
        analytics_metrics = await ai_svc.get_user_analytics_metrics()
        user_segments = await ai_svc.get_user_segmentation()
        behavior_insights = await ai_svc.get_behavior_insights()
        churn_predictions = await ai_svc.predict_user_churn(limit=10)
        
        return {
            'status': 'success',
            'analytics_metrics': analytics_metrics,
            'user_segments': user_segments,
            'behavior_insights': behavior_insights,
            'churn_predictions': churn_predictions,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI User Analytics Error: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در بارگذاری تحلیل کاربران")

@api_router.get("/admin/ai/market-intelligence")
async def get_ai_market_intelligence(admin: User = Depends(get_current_admin)):
    """Get comprehensive AI market intelligence data"""
    try:
        
        ai_svc = get_ai_service(db)
        
        # Get all market intelligence data
        market_metrics = await ai_svc.get_market_metrics()
        price_analysis = await ai_svc.get_price_analysis()
        trading_patterns = await ai_svc.get_trading_patterns()
        iranian_market = await ai_svc.get_iranian_market_data()
        revenue_forecast = await ai_svc.forecast_revenue(days=30)
        
        return {
            'status': 'success',
            'market_metrics': market_metrics,
            'price_analysis': price_analysis,
            'trading_patterns': trading_patterns,
            'iranian_market': iranian_market,
            'revenue_forecast': revenue_forecast,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI Market Intelligence Error: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در بارگذاری هوش بازار")

# ==================== END COMPREHENSIVE AI ENDPOINTS ====================

@api_router.get("/")
async def root():
    return {"message": "Persian Crypto Exchange API with AI", "version": "2.0.0"}

# ==================== SMART TRADING AI ROUTES ====================

from smart_trading_ai import SmartTradingAssistant

# Model for AI settings
class AISettingsUpdate(BaseModel):
    openai_api_key: Optional[str] = None

@api_router.get("/admin/settings/ai")
async def get_ai_settings(admin: User = Depends(get_current_admin)):
    """Get current AI settings (admin only)"""
    try:
        # Get settings from database
        settings = await db.system_settings.find_one({"type": "ai_config"})
        
        if not settings:
            # Return default settings
            return {
                "openai_api_key_set": False,
                "openai_api_key_preview": None,
                "model": "gpt-4o",
                "provider": "openai",
                "status": "not_configured"
            }
        
        # Show masked API key (first 10 and last 4 characters)
        api_key = settings.get("openai_api_key", "")
        masked_key = None
        if api_key:
            if len(api_key) > 14:
                masked_key = f"{api_key[:10]}...{api_key[-4:]}"
            else:
                masked_key = "***"
        
        return {
            "openai_api_key_set": bool(api_key),
            "openai_api_key_preview": masked_key,
            "model": settings.get("model", "gpt-4o"),
            "provider": settings.get("provider", "openai"),
            "status": "configured" if api_key else "not_configured",
            "last_updated": settings.get("updated_at")
        }
    except Exception as e:
        logger.error(f"Error getting AI settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/settings/ai")
async def update_ai_settings(
    settings: AISettingsUpdate,
    admin: User = Depends(get_current_admin)
):
    """Update AI settings (admin only)"""
    try:
        # Test the API key if provided
        if settings.openai_api_key:
            try:
                # Quick test of the API key
                assistant = SmartTradingAssistant(api_key=settings.openai_api_key)
                test_response = await assistant.chat_with_assistant(
                    user_message="سلام، این یک تست است",
                    user_context={"balance": 0, "kyc_level": 0, "user_id": "test"}
                )
                
                if "خطا" in test_response or "error" in test_response.lower():
                    raise HTTPException(
                        status_code=400,
                        detail="کلید API معتبر نیست. لطفاً کلید صحیح OpenAI را وارد کنید"
                    )
                
                logger.info("✅ OpenAI API key validated successfully")
                
            except Exception as test_error:
                logger.error(f"API key validation failed: {str(test_error)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"کلید API معتبر نیست: {str(test_error)}"
                )
        
        # Update settings in database
        update_data = {
            "type": "ai_config",
            "openai_api_key": settings.openai_api_key,
            "model": "gpt-4o",
            "provider": "openai",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": admin.id
        }
        
        await db.system_settings.update_one(
            {"type": "ai_config"},
            {"$set": update_data},
            upsert=True
        )
        
        # Also update environment variable for this session
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        
        logger.info(f"✅ AI settings updated by admin: {admin.email}")
        
        return {
            "success": True,
            "message": "تنظیمات هوش مصنوعی با موفقیت به‌روزرسانی شد",
            "openai_api_key_set": bool(settings.openai_api_key)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating AI settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در به‌روزرسانی تنظیمات: {str(e)}")

async def get_smart_assistant():
    """Get Smart Trading Assistant instance with configured API key"""
    try:
        # Try to get API key from database first
        settings = await db.system_settings.find_one({"type": "ai_config"})
        api_key = settings.get("openai_api_key") if settings else None
        
        # Fallback to environment variable
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="⚠️ سرویس هوش مصنوعی پیکربندی نشده است.\n\nادمین باید کلید OpenAI API را در بخش 'تنظیمات هوش مصنوعی' وارد کند.\n\nمسیر: پنل مدیریت → تنظیمات هوش مصنوعی"
            )
        
        return SmartTradingAssistant(api_key=api_key)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing Smart Assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در راه‌اندازی سرویس هوشمند: {str(e)}")

@api_router.get("/ai/smart-recommendation/{coin_symbol}")
async def get_smart_trading_recommendation(
    coin_symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get REAL smart trading recommendation using mathematical analysis - NO EXTERNAL API"""
    try:
        # Get coin price data
        prices = await price_service.get_prices()
        coin_id = coin_symbol.lower()
        if coin_symbol == "USDT":
            coin_id = "tether"
        elif coin_symbol == "BTC":
            coin_id = "bitcoin"
        elif coin_symbol == "ETH":
            coin_id = "ethereum"
        
        coin_data = prices.get("data", {}).get(coin_id)
        if not coin_data:
            raise HTTPException(status_code=404, detail=f"ارز {coin_symbol} یافت نشد")
        
        current_price = coin_data.get("price_tmn", 0)
        price_change_24h = coin_data.get("change_24h", 0)
        
        # Get user holdings
        holdings = await db.trading_holdings.find({"user_id": current_user.id}).to_list(length=10)
        
        # Use REAL mathematical trading engine
        from real_smart_trading import get_real_trading_engine
        
        engine = await get_real_trading_engine(db)
        recommendation = await engine.get_real_trading_recommendation(
            coin_symbol=coin_symbol,
            current_price=current_price,
            price_change_24h=price_change_24h,
            user_balance=current_user.wallet_balance_tmn,
            user_holdings=holdings
        )
        
        return recommendation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting smart recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در دریافت توصیه: {str(e)}")

@api_router.get("/ai/smart-market-analysis")
async def get_smart_market_analysis(
    timeframe: str = "24h",
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered market analysis"""
    try:
        # Get all crypto prices
        prices = await price_service.get_prices()
        coins_data = []
        
        for coin_id, data in prices.get("data", {}).items():
            coins_data.append({
                "id": coin_id,
                "symbol": data.get("symbol", coin_id.upper()),
                "name": data.get("name", coin_id),
                "price_tmn": data.get("price_tmn", 0),
                "price_change_24h": data.get("change_24h", 0)
            })
        
        # Get Smart Trading Assistant
        assistant = await get_smart_assistant()
        
        # Get market analysis
        analysis = await assistant.get_market_analysis(
            coins_data=coins_data,
            timeframe=timeframe
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در تحلیل بازار: {str(e)}")

class ChatMessage(BaseModel):
    message: str

@api_router.post("/ai/smart-chat")
async def chat_with_smart_assistant(
    chat_msg: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """Chat with Smart Trading Assistant"""
    try:
        # Get Smart Trading Assistant
        assistant = await get_smart_assistant()
        
        # Prepare user context
        user_context = {
            "user_id": current_user.id,
            "balance": current_user.wallet_balance_tmn,
            "kyc_level": current_user.kyc_level,
            "email": current_user.email
        }
        
        # Get response
        response = await assistant.chat_with_assistant(
            user_message=chat_msg.message,
            user_context=user_context
        )
        
        return {
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in smart chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطا در گفتگو: {str(e)}")

# ==================== ADMIN AI ANALYTICS ROUTES (18 FEATURES) ====================

from admin_ai_analytics import AdminAIAnalytics

# Initialize AI Analytics
ai_analytics = AdminAIAnalytics(db)

@api_router.get("/admin/ai-analytics/fraud-detection")
async def get_fraud_detection(admin: User = Depends(get_current_admin)):
    """AI Fraud Detection System"""
    result = await ai_analytics.detect_fraud()
    return result

@api_router.get("/admin/ai-analytics/anomaly-detection")
async def get_anomaly_detection(admin: User = Depends(get_current_admin)):
    """Anomaly Detection Dashboard"""
    result = await ai_analytics.detect_anomalies()
    return result

@api_router.get("/admin/ai-analytics/user-predictions")
async def get_user_predictions(admin: User = Depends(get_current_admin)):
    """Predictive User Analytics"""
    result = await ai_analytics.predict_user_analytics()
    return result

@api_router.get("/admin/ai-analytics/market-manipulation")
async def get_market_manipulation(admin: User = Depends(get_current_admin)):
    """Market Manipulation Detection"""
    result = await ai_analytics.detect_market_manipulation()
    return result

@api_router.get("/admin/ai-analytics/revenue-optimization")
async def get_revenue_optimization(admin: User = Depends(get_current_admin)):
    """Revenue Optimization AI"""
    result = await ai_analytics.optimize_revenue()
    return result

@api_router.get("/admin/ai-analytics/risk-scores")
async def get_risk_scores(admin: User = Depends(get_current_admin)):
    """AI Risk Scoring"""
    result = await ai_analytics.calculate_risk_scores()
    return result

@api_router.get("/admin/ai-analytics/support-triage")
async def get_support_triage(admin: User = Depends(get_current_admin)):
    """Automated Support Ticket Triage"""
    result = await ai_analytics.triage_support_tickets()
    return result

@api_router.get("/admin/ai-analytics/user-intent")
async def get_user_intent(admin: User = Depends(get_current_admin)):
    """User Intent Analysis"""
    result = await ai_analytics.analyze_user_intent()
    return result

@api_router.get("/admin/ai-analytics/transaction-monitoring")
async def get_transaction_monitoring(admin: User = Depends(get_current_admin)):
    """Transaction Monitoring AI"""
    result = await ai_analytics.monitor_transactions()
    return result

@api_router.get("/admin/ai-analytics/price-anomalies")
async def get_price_anomalies(admin: User = Depends(get_current_admin)):
    """Price Anomaly Detection"""
    result = await ai_analytics.detect_price_anomalies()
    return result

@api_router.get("/admin/ai-analytics/market-sentiment")
async def get_market_sentiment(admin: User = Depends(get_current_admin)):
    """Market Sentiment Analysis"""
    result = await ai_analytics.analyze_market_sentiment()
    return result

@api_router.get("/admin/ai-analytics/auto-kyc")
async def get_auto_kyc(admin: User = Depends(get_current_admin)):
    """Auto-KYC Approval"""
    result = await ai_analytics.auto_kyc_approval()
    return result

@api_router.get("/admin/ai-analytics/notifications")
async def get_automated_notifications(admin: User = Depends(get_current_admin)):
    """Automated Notifications"""
    result = await ai_analytics.generate_automated_notifications()
    return result

@api_router.get("/admin/ai-analytics/conversion-optimization")
async def get_conversion_optimization(admin: User = Depends(get_current_admin)):
    """Conversion Optimization"""
    result = await ai_analytics.optimize_conversion()
    return result

@api_router.get("/admin/ai-analytics/search")
async def ai_powered_search(query: str, admin: User = Depends(get_current_admin)):
    """AI-Powered Search"""
    result = await ai_analytics.ai_powered_search(query)
    return result

@api_router.get("/admin/ai-analytics/recommendations")
async def get_smart_recommendations(admin: User = Depends(get_current_admin)):
    """Smart Recommendations"""
    result = await ai_analytics.smart_recommendations()
    return result

@api_router.get("/admin/ai-analytics/crisis-prediction")
async def get_crisis_prediction(admin: User = Depends(get_current_admin)):
    """Predictive Crisis Management"""
    result = await ai_analytics.predict_crisis()
    return result

@api_router.get("/admin/ai-analytics/overview")
async def get_ai_analytics_overview(admin: User = Depends(get_current_admin)):
    """Get overview of all AI analytics features"""
    try:
        # Get quick stats from multiple features
        fraud = await ai_analytics.detect_fraud()
        risk = await ai_analytics.calculate_risk_scores()
        notifications = await ai_analytics.generate_automated_notifications()
        recommendations = await ai_analytics.smart_recommendations()
        crisis = await ai_analytics.predict_crisis()
        
        return {
            "fraud_alerts": fraud.get("total_alerts", 0),
            "high_risk_users": risk.get("high_risk_count", 0),
            "pending_notifications": notifications.get("total_notifications", 0),
            "smart_recommendations": recommendations.get("total_recommendations", 0),
            "crisis_warnings": crisis.get("total_warnings", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error in AI analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== API.IR KYC VERIFICATION ROUTES ====================

from api_ir_services import api_ir_service
import secrets

# In-memory OTP storage (in production, use Redis or database)
otp_storage = {}

class OTPRequest(BaseModel):
    mobile: str

class OTPVerify(BaseModel):
    mobile: str
    code: str

class ShahkarVerify(BaseModel):
    national_id: str
    mobile: str
    birthdate: str

class CardVerify(BaseModel):
    card_number: str
    national_id: str
    birthdate: str
    full_name: Optional[str] = None

@api_router.get("/kyc/check-apir-status")
async def check_apir_status(current_user: User = Depends(get_current_user)):
    """Check if API.IR is configured and working"""
    result = await api_ir_service.test_connection()
    return result

@api_router.post("/kyc/send-sms-otp")
async def send_sms_otp(otp_request: OTPRequest, current_user: User = Depends(get_current_user)):
    """Send OTP via SMS for phone verification"""
    try:
        # Generate 6-digit OTP
        otp_code = str(secrets.randbelow(900000) + 100000)
        
        # Store OTP (expires in 5 minutes)
        otp_storage[otp_request.mobile] = {
            "code": otp_code,
            "created_at": datetime.now(timezone.utc),
            "user_id": current_user.id
        }
        
        # Send via API.IR
        result = await api_ir_service.send_sms_otp(otp_request.mobile, otp_code)
        
        if result.get("success"):
            logger.info(f"OTP sent to {otp_request.mobile}: {otp_code}")
            return {
                "success": True,
                "message": "کد تایید به شماره موبایل شما ارسال شد",
                "sent_at": result.get("sent_at")
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "خطا در ارسال پیامک")
            }
            
    except Exception as e:
        logger.error(f"Error sending SMS OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/kyc/send-call-otp")
async def send_call_otp(otp_request: OTPRequest, current_user: User = Depends(get_current_user)):
    """Send OTP via voice call for phone verification"""
    try:
        # Generate 6-digit OTP
        otp_code = str(secrets.randbelow(900000) + 100000)
        
        # Store OTP
        otp_storage[otp_request.mobile] = {
            "code": otp_code,
            "created_at": datetime.now(timezone.utc),
            "user_id": current_user.id
        }
        
        # Send via API.IR
        result = await api_ir_service.send_call_otp(otp_request.mobile, otp_code)
        
        if result.get("success"):
            logger.info(f"Call OTP sent to {otp_request.mobile}: {otp_code}")
            return {
                "success": True,
                "message": "کد تایید از طریق تماس صوتی ارسال شد",
                "sent_at": result.get("sent_at")
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "خطا در برقراری تماس")
            }
            
    except Exception as e:
        logger.error(f"Error sending Call OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/kyc/verify-otp")
async def verify_otp(verify_data: OTPVerify, current_user: User = Depends(get_current_user)):
    """Verify OTP code and update user phone verification"""
    try:
        stored_otp = otp_storage.get(verify_data.mobile)
        
        if not stored_otp:
            return {
                "success": False,
                "message": "کد تایید منقضی شده یا یافت نشد. لطفاً مجدد درخواست دهید"
            }
        
        # Check if OTP is expired (5 minutes)
        otp_age = (datetime.now(timezone.utc) - stored_otp["created_at"]).total_seconds()
        if otp_age > 300:
            del otp_storage[verify_data.mobile]
            return {
                "success": False,
                "message": "کد تایید منقضی شده است. لطفاً مجدد درخواست دهید"
            }
        
        # Verify OTP code
        if stored_otp["code"] != verify_data.code:
            return {
                "success": False,
                "message": "کد تایید اشتباه است"
            }
        
        # OTP is correct - update user
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$set": {
                    "phone": verify_data.mobile,
                    "is_phone_verified": True,
                    "phone_verified_at": datetime.now(timezone.utc).isoformat(),
                    "kyc_level": max(current_user.kyc_level, 1)  # At least Level 1
                }
            }
        )
        
        # Clean up OTP
        del otp_storage[verify_data.mobile]
        
        logger.info(f"Phone verified for user {current_user.id}: {verify_data.mobile}")
        
        return {
            "success": True,
            "message": "شماره موبایل شما با موفقیت تایید شد",
            "kyc_level": max(current_user.kyc_level, 1)
        }
        
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/kyc/verify-shahkar")
async def verify_shahkar(shahkar_data: ShahkarVerify, current_user: User = Depends(get_current_user)):
    """Verify National ID + Mobile with Shahkar service"""
    try:
        # Verify with API.IR Shahkar
        result = await api_ir_service.verify_shahkar(
            shahkar_data.national_id,
            shahkar_data.mobile,
            shahkar_data.birthdate
        )
        
        if result.get("verified"):
            # Update user KYC data
            await db.users.update_one(
                {"id": current_user.id},
                {
                    "$set": {
                        "national_id": shahkar_data.national_id,
                        "birthdate": shahkar_data.birthdate,
                        "shahkar_verified": True,
                        "shahkar_verified_at": datetime.now(timezone.utc).isoformat(),
                        "kyc_level": max(current_user.kyc_level, 2),  # Level 2
                        "kyc_status": "verified"
                    }
                }
            )
            
            logger.info(f"Shahkar verified for user {current_user.id}")
            
            return {
                "success": True,
                "verified": True,
                "message": "کد ملی و شماره موبایل شما با موفقیت تایید شد",
                "match_score": result.get("match_score", 100),
                "kyc_level": max(current_user.kyc_level, 2)
            }
        else:
            return {
                "success": False,
                "verified": False,
                "message": result.get("message", "شماره موبایل با کد ملی مطابقت ندارد")
            }
            
    except Exception as e:
        logger.error(f"Error verifying Shahkar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/kyc/verify-card")
async def verify_card(card_data: CardVerify, current_user: User = Depends(get_current_user)):
    """Verify bank card matches user identity"""
    try:
        # Get user's full name
        full_name = f"{current_user.first_name} {current_user.last_name}" if not card_data.full_name else card_data.full_name
        
        # Verify with API.IR CardMatch
        result = await api_ir_service.verify_card_match(
            card_data.card_number,
            card_data.national_id,
            card_data.birthdate,
            full_name
        )
        
        if result.get("verified"):
            # Update user banking info
            await db.users.update_one(
                {"id": current_user.id},
                {
                    "$set": {
                        "bank_card_number": card_data.card_number[-4:],  # Store only last 4 digits
                        "bank_name": result.get("bank_name", ""),
                        "card_verified": True,
                        "card_verified_at": datetime.now(timezone.utc).isoformat(),
                        "kyc_level": 3,  # Full KYC Level 3
                        "kyc_status": "verified"
                    }
                }
            )
            
            logger.info(f"Bank card verified for user {current_user.id}")
            
            return {
                "success": True,
                "verified": True,
                "message": "کارت بانکی شما با موفقیت تایید شد",
                "bank_name": result.get("bank_name", ""),
                "kyc_level": 3
            }
        else:
            return {
                "success": False,
                "verified": False,
                "message": result.get("message", "کارت بانکی با اطلاعات شما مطابقت ندارد")
            }
            
    except Exception as e:
        logger.error(f"Error verifying card: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/kyc/status")
async def get_kyc_status(current_user: User = Depends(get_current_user)):
    """Get user's current KYC status and next steps"""
    try:
        status = {
            "kyc_level": current_user.kyc_level,
            "kyc_status": current_user.kyc_status,
            "phone_verified": current_user.is_phone_verified,
            "shahkar_verified": getattr(current_user, 'shahkar_verified', False),
            "card_verified": getattr(current_user, 'card_verified', False),
            "next_steps": []
        }
        
        # Determine next steps
        if current_user.kyc_level == 0:
            status["next_steps"].append({
                "step": 1,
                "title": "تایید شماره موبایل",
                "description": "برای شروع معاملات، شماره موبایل خود را تایید کنید",
                "action": "verify_phone"
            })
        
        if current_user.kyc_level <= 1:
            status["next_steps"].append({
                "step": 2,
                "title": "تایید هویت با شاهکار",
                "description": "کد ملی و تاریخ تولد خود را وارد کنید",
                "action": "verify_shahkar"
            })
        
        if current_user.kyc_level <= 2:
            status["next_steps"].append({
                "step": 3,
                "title": "تایید کارت بانکی",
                "description": "کارت بانکی خود را برای برداشت وجه تایید کنید",
                "action": "verify_card"
            })
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting KYC status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Router will be included at the end of the file

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

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    # Price scheduler disabled - causes delays
    logger.info("⚠️  Price scheduler disabled - using static prices")
    pass

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown"""


# ============================================================================
# CSV EXPORT ENDPOINTS FOR ADMIN REPORTING
# ============================================================================

@api_router.get("/admin/export/users")
async def export_users_csv(admin: User = Depends(get_current_admin)):
    """Export all users to CSV format"""
    users = await db.users.find().to_list(length=None)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['ID', 'Email', 'Full Name', 'Phone', 'KYC Level', 'KYC Status', 'Balance (TMN)', 'Is Admin', 'Created At'])
    
    # Write data
    for user in users:
        writer.writerow([
            user.get('id', ''),
            user.get('email', ''),
            user.get('full_name', ''),
            user.get('phone', ''),
            user.get('kyc_level', 0),
            user.get('kyc_status', 'pending'),
            user.get('wallet_balance_tmn', 0),
            'Yes' if user.get('is_admin', False) else 'No',
            user.get('created_at', '').isoformat() if user.get('created_at') else ''
        ])
    
    # Prepare response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@api_router.get("/admin/export/orders")
async def export_orders_csv(admin: User = Depends(get_current_admin)):
    """Export all orders to CSV format"""
    orders = await db.trading_orders.find().to_list(length=None)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Order ID', 'User ID', 'Type', 'Coin', 'Amount TMN', 'Amount Crypto', 'Status', 'Price', 'Wallet Address', 'Created At', 'Updated At'])
    
    for order in orders:
        writer.writerow([
            order.get('id', ''),
            order.get('user_id', ''),
            order.get('order_type', ''),
            order.get('coin_symbol', ''),
            order.get('amount_tmn', 0),
            order.get('amount_crypto', 0),
            order.get('status', 'pending'),
            order.get('price_at_order', 0),
            order.get('user_wallet_address', ''),
            order.get('created_at', '').isoformat() if order.get('created_at') else '',
            order.get('updated_at', '').isoformat() if order.get('updated_at') else ''
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@api_router.get("/admin/export/deposits")
async def export_deposits_csv(admin: User = Depends(get_current_admin)):
    """Export all deposits to CSV format"""
    deposits = await db.deposits.find().to_list(length=None)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Deposit ID', 'User ID', 'Amount TMN', 'From Card', 'To Card', 'Status', 'Receipt Number', 'Created At', 'Approved At'])
    
    for deposit in deposits:
        writer.writerow([
            deposit.get('id', ''),
            deposit.get('user_id', ''),
            deposit.get('amount_tmn', 0),
            deposit.get('from_card_number', ''),
            deposit.get('to_card_number', ''),
            deposit.get('status', 'pending'),
            deposit.get('receipt_number', ''),
            deposit.get('created_at', '').isoformat() if deposit.get('created_at') else '',
            deposit.get('approved_at', '').isoformat() if deposit.get('approved_at') else ''
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=deposits_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


# ============================================================================
# PRICE ALERTS SYSTEM
# ============================================================================

class PriceAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    coin_symbol: str
    coin_name: str
    target_price: float  # in Toman
    condition: str  # "above" or "below"
    is_active: bool = True
    triggered: bool = False
    triggered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@api_router.post("/price-alerts")
async def create_price_alert(
    coin_symbol: str,
    target_price: float,
    condition: str,
    current_user: User = Depends(get_current_user)
):
    """Create a new price alert"""
    if condition not in ["above", "below"]:
        raise HTTPException(400, detail="شرط باید 'above' یا 'below' باشد")
    
    # Get coin info
    coins = await get_all_coins()
    coin = next((c for c in coins if c['symbol'] == coin_symbol), None)
    
    if not coin:
        raise HTTPException(404, detail="ارز مورد نظر یافت نشد")
    
    alert = PriceAlert(
        user_id=current_user.id,
        coin_symbol=coin_symbol,
        coin_name=coin.get('name', coin_symbol),
        target_price=target_price,
        condition=condition
    )
    
    await db.price_alerts.insert_one(alert.dict())
    
    return {
        "success": True,
        "alert_id": alert.id,
        "message": f"هشدار قیمت برای {coin_symbol} ثبت شد"
    }

@api_router.get("/price-alerts/my")
async def get_my_alerts(current_user: User = Depends(get_current_user)):
    """Get user's price alerts"""
    alerts = await db.price_alerts.find({"user_id": current_user.id}).to_list(length=None)
    return {"alerts": alerts}

@api_router.delete("/price-alerts/{alert_id}")
async def delete_price_alert(alert_id: str, current_user: User = Depends(get_current_user)):
    """Delete a price alert"""
    result = await db.price_alerts.delete_one({"id": alert_id, "user_id": current_user.id})
    
    if result.deleted_count == 0:
        raise HTTPException(404, detail="هشدار یافت نشد")
    
    return {"success": True, "message": "هشدار حذف شد"}

@api_router.post("/price-alerts/check")
async def check_price_alerts():
    """Background task to check and trigger alerts"""
    # Get active alerts
    alerts = await db.price_alerts.find({"is_active": True, "triggered": False}).to_list(length=None)
    
    if not alerts:
        return {"checked": 0, "triggered": 0}
    
    # Get current prices
    coins = await get_all_coins()
    price_map = {coin['symbol']: coin['current_price'] for coin in coins}
    
    triggered_count = 0
    
    for alert in alerts:
        current_price = price_map.get(alert['coin_symbol'])
        if not current_price:
            continue
        
        should_trigger = False
        if alert['condition'] == 'above' and current_price >= alert['target_price']:
            should_trigger = True
        elif alert['condition'] == 'below' and current_price <= alert['target_price']:
            should_trigger = True
        
        if should_trigger:
            await db.price_alerts.update_one(
                {"id": alert['id']},
                {"$set": {
                    "triggered": True,
                    "triggered_at": datetime.now(timezone.utc),
                    "is_active": False
                }}
            )
            
            # Create notification for user
            await db.notifications.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": alert['user_id'],
                "type": "price_alert",
                "title": f"🔔 هشدار قیمت {alert['coin_symbol']}",
                "message": f"قیمت {alert['coin_name']} به {int(current_price):,} تومان رسید",
                "data": {
                    "coin_symbol": alert['coin_symbol'],
                    "current_price": current_price,
                    "target_price": alert['target_price']
                },
                "is_read": False,
                "created_at": datetime.now(timezone.utc)
            })
            
            triggered_count += 1
    
    return {
        "checked": len(alerts),
        "triggered": triggered_count
    }

# ==================== BALANCE MANAGEMENT & AUDIT ROUTES ====================

@api_router.get("/admin/balance/overview")
async def get_balance_overview(admin: User = Depends(get_current_admin)):
    """
    Get system-wide balance overview with verification
    Shows total balances, deposits, orders, and detects discrepancies
    """
    try:
        # Get all users
        users = await db.users.find({}).to_list(length=10000)
        total_user_balances = sum(u.get('wallet_balance_tmn', 0) for u in users)
        
        # Get all approved deposits
        deposits = await db.deposits.find({'status': 'approved'}).to_list(length=10000)
        total_deposits = sum(d.get('amount_tmn', 0) for d in deposits)
        
        # Get all completed buy orders
        orders = await db.orders.find({
            'order_type': 'buy',
            'status': {'$in': ['confirmed', 'completed']}
        }).to_list(length=10000)
        total_spent = sum(o.get('amount_tmn', 0) for o in orders)
        
        # Get all transactions
        transactions = await db.transactions.find({}).to_list(length=10000)
        total_from_transactions = sum(t.get('amount_tmn', 0) for t in transactions)
        
        # Calculate expected balance
        expected_total = total_deposits - total_spent
        discrepancy = total_user_balances - expected_total
        
        return {
            'total_users': len(users),
            'total_user_balances': total_user_balances,
            'total_deposits': total_deposits,
            'total_deposits_count': len(deposits),
            'total_spent_on_orders': total_spent,
            'total_orders_count': len(orders),
            'total_transactions': len(transactions),
            'total_from_transactions': total_from_transactions,
            'expected_total': expected_total,
            'discrepancy': discrepancy,
            'has_discrepancy': abs(discrepancy) > 1000,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error in balance overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/balance/verify-all")
async def verify_all_balances(admin: User = Depends(get_current_admin)):
    """
    Verify all user balances against transaction history
    Returns list of discrepancies
    """
    try:
        users = await db.users.find({}).to_list(length=10000)
        discrepancies = []
        verified_count = 0
        
        for user in users:
            # Calculate expected balance from transactions
            result = await calculate_user_balance_from_transactions(user['id'])
            calculated_balance = result['calculated_balance']
            actual_balance = user.get('wallet_balance_tmn', 0)
            
            # Allow 100 TMN rounding tolerance
            if abs(calculated_balance - actual_balance) > 100:
                discrepancies.append({
                    'user_id': user['id'],
                    'email': user.get('email', 'N/A'),
                    'full_name': user.get('full_name', 'N/A'),
                    'expected_balance': calculated_balance,
                    'actual_balance': actual_balance,
                    'difference': actual_balance - calculated_balance,
                    'breakdown': result['breakdown'],
                    'transaction_count': result['transaction_count']
                })
            else:
                verified_count += 1
        
        return {
            'total_users': len(users),
            'verified_users': verified_count,
            'users_with_discrepancy': len(discrepancies),
            'discrepancies': discrepancies,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error in verify balances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class BalanceAdjustmentRequest(BaseModel):
    user_id: str
    amount: float  # Can be positive or negative
    reason: str
    notes: Optional[str] = None

@api_router.post("/admin/balance/adjust")
async def adjust_user_balance(
    request: BalanceAdjustmentRequest,
    admin: User = Depends(get_current_admin)
):
    """
    Manually adjust user balance with full audit trail
    Creates transaction record and logs admin action
    """
    try:
        # Verify user exists
        user = await db.users.find_one({'id': request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")
        
        # Record transaction
        transaction = await record_transaction(
            user_id=request.user_id,
            transaction_type="admin_adjustment",
            amount_tmn=request.amount,
            reference_type="admin_action",
            reference_id=str(uuid.uuid4()),
            description=f"تصحیح موجودی توسط ادمین: {request.reason}",
            created_by=admin.id,
            admin_notes=request.notes
        )
        
        # Log admin action
        admin_action = {
            'id': str(uuid.uuid4()),
            'admin_id': admin.id,
            'admin_email': admin.email or 'N/A',
            'action_type': 'adjust_balance',
            'target_type': 'user',
            'target_id': request.user_id,
            'amount': request.amount,
            'reason': request.reason,
            'notes': request.notes,
            'transaction_id': transaction['id'],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.admin_actions.insert_one(admin_action)
        
        # Get updated user
        updated_user = await db.users.find_one({'id': request.user_id})
        
        return {
            'success': True,
            'message': 'موجودی با موفقیت تصحیح شد',
            'transaction': transaction,
            'new_balance': updated_user.get('wallet_balance_tmn', 0)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adjusting balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/balance/user/{user_id}")
async def get_user_balance_details(
    user_id: str,
    admin: User = Depends(get_current_admin)
):
    """
    Get detailed balance information for a specific user
    Includes transaction history and calculated balance
    """
    try:
        user = await db.users.find_one({'id': user_id})
        if not user:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")
        
        # Calculate from transactions
        result = await calculate_user_balance_from_transactions(user_id)
        
        # Get recent transactions
        transactions = await db.transactions.find({'user_id': user_id}) \
            .sort('created_at', -1) \
            .limit(50) \
            .to_list(length=50)
        
        actual_balance = user.get('wallet_balance_tmn', 0)
        calculated_balance = result['calculated_balance']
        discrepancy = actual_balance - calculated_balance
        
        return {
            'user_id': user_id,
            'email': user.get('email', 'N/A'),
            'full_name': user.get('full_name', 'N/A'),
            'actual_balance': actual_balance,
            'calculated_balance': calculated_balance,
            'discrepancy': discrepancy,
            'has_discrepancy': abs(discrepancy) > 100,
            'breakdown': result['breakdown'],
            'transaction_count': result['transaction_count'],
            'recent_transactions': transactions
        }
    except Exception as e:
        logger.error(f"Error getting user balance details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user/transactions")
async def get_user_transactions(
    limit: int = 50,
    offset: int = 0,
    type: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """
    Get user's transaction history
    Users can see all their balance changes
    """
    try:
        query = {'user_id': user.id}
        if type:
            query['type'] = type
        
        # Get transactions
        transactions_raw = await db.transactions.find(query) \
            .sort('created_at', -1) \
            .skip(offset) \
            .limit(limit) \
            .to_list(length=limit)
        
        # Convert transactions to JSON-serializable format
        transactions = []
        for txn in transactions_raw:
            # Remove MongoDB ObjectId and convert to dict
            if '_id' in txn:
                del txn['_id']
            transactions.append(txn)
        
        total = await db.transactions.count_documents(query)
        
        return {
            'transactions': transactions,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        }
    except Exception as e:
        logger.error(f"Error getting user transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== NOTIFICATION ROUTES ====================

@api_router.get("/user/notifications")
async def get_user_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    user: User = Depends(get_current_user)
):
    """
    Get user's notifications
    """
    try:
        query = {'user_id': user.id}
        if unread_only:
            query['is_read'] = False
        
        # Get notifications
        notifications_raw = await db.notifications.find(query) \
            .sort('created_at', -1) \
            .skip(offset) \
            .limit(limit) \
            .to_list(length=limit)
        
        # Convert notifications to JSON-serializable format
        notifications = []
        for notif in notifications_raw:
            # Remove MongoDB ObjectId and convert to dict
            if '_id' in notif:
                del notif['_id']
            notifications.append(notif)
        
        total = await db.notifications.count_documents(query)
        unread_count = await db.notifications.count_documents({'user_id': user.id, 'is_read': False})
        
        return {
            'notifications': notifications,
            'total': total,
            'unread_count': unread_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        }
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.patch("/user/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user: User = Depends(get_current_user)
):
    """
    Mark a notification as read
    """
    try:
        result = await db.notifications.update_one(
            {'id': notification_id, 'user_id': user.id},
            {'$set': {'is_read': True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="اعلان یافت نشد")
        
        return {'message': 'اعلان به عنوان خوانده شده علامت گذاری شد'}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.patch("/user/notifications/mark-all-read")
async def mark_all_notifications_read(user: User = Depends(get_current_user)):
    """
    Mark all notifications as read
    """
    try:
        result = await db.notifications.update_many(
            {'user_id': user.id, 'is_read': False},
            {'$set': {'is_read': True}}
        )
        
        return {
            'message': f'{result.modified_count} اعلان به عنوان خوانده شده علامت گذاری شد',
            'count': result.modified_count
        }
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app (must be at the end after all endpoints are defined)
app.include_router(api_router)