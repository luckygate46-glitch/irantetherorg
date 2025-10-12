#!/usr/bin/env python3
"""
Secure OpenAI API Key Setup Script
Usage: python set_openai_key.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import getpass

async def set_api_key():
    """Set OpenAI API key securely in database"""
    print("=" * 60)
    print("Smart Trading AI - Secure API Key Setup")
    print("=" * 60)
    print()
    
    # Get MongoDB URL from environment
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/crypto_exchange")
    
    print(f"📊 Connecting to database...")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_default_database()
    
    # Get API key from user (hidden input)
    print()
    print("🔑 Please enter your OpenAI API key:")
    print("   (Input will be hidden for security)")
    api_key = getpass.getpass("   API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    if not api_key.startswith("sk-"):
        print("⚠️  Warning: API key should start with 'sk-'")
        confirm = input("   Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled.")
            return
    
    # Save to database
    print()
    print("💾 Saving API key to database...")
    
    try:
        update_data = {
            "type": "ai_config",
            "openai_api_key": api_key,
            "model": "gpt-4o",
            "provider": "openai",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "setup_script"
        }
        
        result = await db.system_settings.update_one(
            {"type": "ai_config"},
            {"$set": update_data},
            upsert=True
        )
        
        if result.modified_count > 0 or result.upserted_id:
            print("✅ API key saved successfully!")
            print()
            print("📝 Next steps:")
            print("   1. Restart backend: sudo supervisorctl restart backend")
            print("   2. Test in admin panel: /admin/settings/ai")
            print("   3. Start using AI features!")
        else:
            print("⚠️  No changes made (key might already be the same)")
            
    except Exception as e:
        print(f"❌ Error saving API key: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    print()
    print("⚠️  SECURITY NOTICE:")
    print("   - This script stores your API key in the database")
    print("   - Never commit this script with hardcoded keys")
    print("   - Never share your API key with others")
    print()
    
    asyncio.run(set_api_key())
