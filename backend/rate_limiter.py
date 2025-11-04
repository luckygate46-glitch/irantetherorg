"""
Rate Limiting Configuration
Protects API endpoints from abuse and DDoS attacks
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit tiers
RATE_LIMITS = {
    # Authentication endpoints - strict limits
    "auth_login": "5/minute",  # 5 login attempts per minute
    "auth_register": "3/minute",  # 3 registrations per minute
    
    # Public endpoints - moderate limits
    "public": "60/minute",  # 60 requests per minute
    
    # User endpoints - generous limits
    "user": "120/minute",  # 120 requests per minute
    
    # Admin endpoints - very generous
    "admin": "300/minute",  # 300 requests per minute
    
    # Trading endpoints - moderate (prevent spam orders)
    "trading": "30/minute",  # 30 trades per minute
    
    # File upload - strict
    "upload": "10/minute",  # 10 uploads per minute
}

def get_rate_limit_message(persian=True):
    """Get rate limit error message"""
    if persian:
        return "تعداد درخواست‌های شما از حد مجاز گذشته است. لطفا کمی صبر کنید."
    return "Rate limit exceeded. Please try again later."
