"""
Database Index Creation Script
Adds indexes to MongoDB collections for improved query performance
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def create_indexes():
    """Create all necessary indexes for optimal performance"""
    
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.crypto_exchange
    
    print("="*70)
    print("📊 CREATING DATABASE INDEXES")
    print("="*70)
    
    indexes_created = []
    
    try:
        # Users collection indexes
        print("\n1️⃣ Users Collection:")
        await db.users.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.users.create_index("email", unique=True)
        print("   ✅ Index on 'email' (unique)")
        
        await db.users.create_index("phone")
        print("   ✅ Index on 'phone'")
        
        await db.users.create_index([("kyc_status", 1), ("is_admin", 1)])
        print("   ✅ Compound index on 'kyc_status' + 'is_admin'")
        
        await db.users.create_index("created_at")
        print("   ✅ Index on 'created_at'")
        
        # Trading orders collection indexes
        print("\n2️⃣ Trading Orders Collection:")
        await db.trading_orders.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.trading_orders.create_index("user_id")
        print("   ✅ Index on 'user_id'")
        
        await db.trading_orders.create_index("status")
        print("   ✅ Index on 'status'")
        
        await db.trading_orders.create_index([("status", 1), ("created_at", -1)])
        print("   ✅ Compound index on 'status' + 'created_at' (DESC)")
        
        await db.trading_orders.create_index([("user_id", 1), ("status", 1)])
        print("   ✅ Compound index on 'user_id' + 'status'")
        
        await db.trading_orders.create_index("created_at")
        print("   ✅ Index on 'created_at'")
        
        # Wallet addresses collection indexes
        print("\n3️⃣ Wallet Addresses Collection:")
        await db.wallet_addresses.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.wallet_addresses.create_index("user_id")
        print("   ✅ Index on 'user_id'")
        
        await db.wallet_addresses.create_index([("user_id", 1), ("coin_symbol", 1)], unique=True)
        print("   ✅ Compound index on 'user_id' + 'coin_symbol' (unique)")
        
        await db.wallet_addresses.create_index("address")
        print("   ✅ Index on 'address'")
        
        # Transactions collection indexes
        print("\n4️⃣ Transactions Collection:")
        await db.transactions.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.transactions.create_index("user_id")
        print("   ✅ Index on 'user_id'")
        
        await db.transactions.create_index([("user_id", 1), ("created_at", -1)])
        print("   ✅ Compound index on 'user_id' + 'created_at' (DESC)")
        
        await db.transactions.create_index("type")
        print("   ✅ Index on 'type'")
        
        await db.transactions.create_index("created_at")
        print("   ✅ Index on 'created_at'")
        
        # Notifications collection indexes
        print("\n5️⃣ Notifications Collection:")
        await db.notifications.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.notifications.create_index("user_id")
        print("   ✅ Index on 'user_id'")
        
        await db.notifications.create_index([("user_id", 1), ("is_read", 1)])
        print("   ✅ Compound index on 'user_id' + 'is_read'")
        
        await db.notifications.create_index([("user_id", 1), ("created_at", -1)])
        print("   ✅ Compound index on 'user_id' + 'created_at' (DESC)")
        
        # Deposits collection indexes
        print("\n6️⃣ Deposits Collection:")
        await db.deposits.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.deposits.create_index("user_id")
        print("   ✅ Index on 'user_id'")
        
        await db.deposits.create_index("status")
        print("   ✅ Index on 'status'")
        
        await db.deposits.create_index([("status", 1), ("created_at", -1)])
        print("   ✅ Compound index on 'status' + 'created_at' (DESC)")
        
        await db.deposits.create_index("created_at")
        print("   ✅ Index on 'created_at'")
        
        # Trading holdings collection indexes (if exists)
        print("\n7️⃣ Trading Holdings Collection:")
        await db.trading_holdings.create_index("id", unique=True)
        print("   ✅ Index on 'id' (unique)")
        
        await db.trading_holdings.create_index("user_id")
        print("   ✅ Index on 'user_id'")
        
        await db.trading_holdings.create_index([("user_id", 1), ("coin_symbol", 1)])
        print("   ✅ Compound index on 'user_id' + 'coin_symbol'")
        
        print("\n" + "="*70)
        print("✅ ALL INDEXES CREATED SUCCESSFULLY!")
        print("="*70)
        
        # Show index statistics
        print("\n📊 INDEX STATISTICS:")
        collections = ['users', 'trading_orders', 'wallet_addresses', 'transactions', 
                      'notifications', 'deposits', 'trading_holdings']
        
        for coll_name in collections:
            coll = db[coll_name]
            indexes = await coll.index_information()
            print(f"\n{coll_name}: {len(indexes)} indexes")
            for idx_name, idx_info in indexes.items():
                print(f"  - {idx_name}: {idx_info.get('key', [])}")
        
        print("\n" + "="*70)
        print("🚀 Database performance optimized!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_indexes())
