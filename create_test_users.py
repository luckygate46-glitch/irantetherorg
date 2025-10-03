#!/usr/bin/env python3
"""
Create test users for trading system testing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import bcrypt
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def create_test_users():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print(f'Connected to MongoDB: {mongo_url}, DB: {db_name}')
    
    # Hash password
    password = 'testpass123'
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # Create regular user with KYC Level 2
    regular_user = {
        'id': str(uuid.uuid4()),
        'email': 'testuser@example.com',
        'password_hash': hashed,
        'phone': '09123456789',
        'full_name': 'علی احمدی',
        'national_code': '1234567890',
        'is_active': True,
        'is_phone_verified': True,
        'kyc_level': 2,  # Level 2 for trading
        'kyc_status': 'approved',
        'is_admin': False,
        'wallet_balance_tmn': 5000000.0,  # 5M TMN for testing
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    
    # Create admin user
    admin_user = {
        'id': str(uuid.uuid4()),
        'email': 'admin@example.com',
        'password_hash': hashed,
        'phone': '09123456788',
        'full_name': 'مدیر سیستم',
        'national_code': '0987654321',
        'is_active': True,
        'is_phone_verified': True,
        'kyc_level': 2,
        'kyc_status': 'approved',
        'is_admin': True,
        'wallet_balance_tmn': 10000000.0,  # 10M TMN
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    
    # Delete existing users first
    await db.users.delete_many({'email': {'$in': ['testuser@example.com', 'admin@example.com']}})
    
    # Insert new users
    result1 = await db.users.insert_one(regular_user)
    result2 = await db.users.insert_one(admin_user)
    
    print('✅ Test users created:')
    print(f'Regular User: {regular_user["email"]} (KYC Level {regular_user["kyc_level"]}, Balance: {regular_user["wallet_balance_tmn"]} TMN)')
    print(f'Admin User: {admin_user["email"]} (Admin: {admin_user["is_admin"]})')
    print(f'Regular user ID: {result1.inserted_id}')
    print(f'Admin user ID: {result2.inserted_id}')
    
    # Also create some test card numbers
    card_data = {
        'id': str(uuid.uuid4()),
        'card_number': '1234567890123456',
        'cardholder_name': 'بانک تست',
        'is_active': True,
        'created_at': datetime.now(timezone.utc)
    }
    
    await db.card_numbers.delete_many({'card_number': '1234567890123456'})
    await db.card_numbers.insert_one(card_data)
    print(f'✅ Test card created: {card_data["card_number"]}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_users())