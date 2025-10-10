#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verify_wallets():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    # Update all wallet addresses for admin user to be verified
    result = await db.wallet_addresses.update_many(
        {'user_id': 'admin-user-001'},
        {'$set': {'verified': True}}
    )
    
    print(f'Updated {result.modified_count} wallet addresses to verified')
    
    # Check current wallet addresses
    cursor = db.wallet_addresses.find({'user_id': 'admin-user-001'})
    wallets = await cursor.to_list(length=None)
    print(f'Admin wallet addresses:')
    for wallet in wallets:
        print(f'  - {wallet["symbol"]}: verified={wallet["verified"]}')
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(verify_wallets())