#!/usr/bin/env python3
"""
Test sell order functionality after user has crypto holdings
"""

import asyncio
import httpx
import json
from datetime import datetime

BACKEND_URL = "https://crypto-genius-7.preview.emergentagent.com/api"

async def test_sell_order_workflow():
    """Test complete sell order workflow"""
    print("🚀 Testing Sell Order Workflow")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login regular user
        response = await client.post(f"{BACKEND_URL}/auth/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        
        if response.status_code != 200:
            print("❌ Failed to login regular user")
            return
        
        user_data = response.json()
        regular_headers = {"Authorization": f"Bearer {user_data['access_token']}"}
        
        # Login admin user
        response = await client.post(f"{BACKEND_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "testpass123"
        })
        
        if response.status_code != 200:
            print("❌ Failed to login admin user")
            return
        
        admin_data = response.json()
        admin_headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
        
        # Check current holdings
        response = await client.get(f"{BACKEND_URL}/trading/holdings/my", headers=regular_headers)
        if response.status_code == 200:
            holdings = response.json()
            btc_holdings = [h for h in holdings if h.get("coin_symbol") == "BTC"]
            
            if btc_holdings:
                btc_amount = btc_holdings[0].get("amount", 0)
                print(f"✅ Current BTC holdings: {btc_amount}")
                
                # Create sell order for half of holdings
                sell_amount = btc_amount / 2
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=regular_headers,
                    json={
                        "order_type": "sell",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_crypto": sell_amount
                    }
                )
                
                if response.status_code in [200, 201]:
                    order_data = response.json()
                    sell_order_id = order_data.get("id")
                    print(f"✅ Created sell order: {sell_order_id}, Amount: {sell_amount} BTC")
                    
                    # Admin approve sell order
                    response = await client.post(f"{BACKEND_URL}/admin/trading/orders/approve", 
                        headers=admin_headers,
                        json={
                            "order_id": sell_order_id,
                            "action": "approve",
                            "admin_note": "Test sell order approval"
                        }
                    )
                    
                    if response.status_code == 200:
                        print("✅ Admin approved sell order")
                        
                        # Check updated balance
                        response = await client.get(f"{BACKEND_URL}/auth/me", headers=regular_headers)
                        if response.status_code == 200:
                            user_info = response.json()
                            new_balance = user_info.get("wallet_balance_tmn", 0)
                            print(f"✅ Updated TMN balance: {new_balance}")
                        
                        # Check updated holdings
                        response = await client.get(f"{BACKEND_URL}/trading/holdings/my", headers=regular_headers)
                        if response.status_code == 200:
                            new_holdings = response.json()
                            new_btc_holdings = [h for h in new_holdings if h.get("coin_symbol") == "BTC"]
                            if new_btc_holdings:
                                new_btc_amount = new_btc_holdings[0].get("amount", 0)
                                print(f"✅ Updated BTC holdings: {new_btc_amount}")
                            else:
                                print("✅ No BTC holdings remaining")
                    else:
                        print(f"❌ Failed to approve sell order: {response.text}")
                else:
                    print(f"❌ Failed to create sell order: {response.text}")
            else:
                print("ℹ️  No BTC holdings found - need to create and approve a buy order first")
        else:
            print(f"❌ Failed to get holdings: {response.text}")

async def test_trade_order_workflow():
    """Test crypto-to-crypto trade order"""
    print("\n🔄 Testing Trade Order Workflow")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login users
        response = await client.post(f"{BACKEND_URL}/auth/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        
        if response.status_code != 200:
            print("❌ Failed to login regular user")
            return
        
        user_data = response.json()
        regular_headers = {"Authorization": f"Bearer {user_data['access_token']}"}
        
        response = await client.post(f"{BACKEND_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "testpass123"
        })
        
        if response.status_code != 200:
            print("❌ Failed to login admin user")
            return
        
        admin_data = response.json()
        admin_headers = {"Authorization": f"Bearer {admin_data['access_token']}"}
        
        # Check current BTC holdings
        response = await client.get(f"{BACKEND_URL}/trading/holdings/my", headers=regular_headers)
        if response.status_code == 200:
            holdings = response.json()
            btc_holdings = [h for h in holdings if h.get("coin_symbol") == "BTC"]
            
            if btc_holdings and btc_holdings[0].get("amount", 0) > 0:
                btc_amount = btc_holdings[0].get("amount", 0)
                trade_amount = min(btc_amount / 4, 0.001)  # Trade small amount
                
                print(f"✅ Current BTC: {btc_amount}, Trading: {trade_amount}")
                
                # Create trade order (BTC -> ETH)
                response = await client.post(f"{BACKEND_URL}/trading/order", 
                    headers=regular_headers,
                    json={
                        "order_type": "trade",
                        "coin_symbol": "BTC",
                        "coin_id": "bitcoin",
                        "amount_crypto": trade_amount,
                        "target_coin_symbol": "ETH",
                        "target_coin_id": "ethereum"
                    }
                )
                
                if response.status_code in [200, 201]:
                    order_data = response.json()
                    trade_order_id = order_data.get("id")
                    print(f"✅ Created trade order: {trade_order_id}")
                    
                    # Admin approve trade order
                    response = await client.post(f"{BACKEND_URL}/admin/trading/orders/approve", 
                        headers=admin_headers,
                        json={
                            "order_id": trade_order_id,
                            "action": "approve",
                            "admin_note": "Test trade order approval"
                        }
                    )
                    
                    if response.status_code == 200:
                        print("✅ Admin approved trade order")
                        
                        # Check updated holdings
                        response = await client.get(f"{BACKEND_URL}/trading/holdings/my", headers=regular_headers)
                        if response.status_code == 200:
                            new_holdings = response.json()
                            print("✅ Updated holdings:")
                            for holding in new_holdings:
                                print(f"  - {holding.get('coin_symbol')}: {holding.get('amount')}")
                    else:
                        print(f"❌ Failed to approve trade order: {response.text}")
                else:
                    print(f"❌ Failed to create trade order: {response.text}")
            else:
                print("ℹ️  No BTC holdings for trading")

async def main():
    """Main test runner"""
    await test_sell_order_workflow()
    await test_trade_order_workflow()
    print("\n🏁 Sell and Trade Order Tests Complete!")

if __name__ == "__main__":
    asyncio.run(main())