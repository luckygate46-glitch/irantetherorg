"""
Crypto Price Fetching Service using CoinGecko API
"""
import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Top cryptocurrencies for Iranian market
TOP_COINS = [
    "bitcoin", "ethereum", "tether", "binancecoin", "ripple",
    "cardano", "solana", "dogecoin", "polkadot", "tron",
    "usd-coin", "shiba-inu", "avalanche-2", "chainlink", "litecoin"
]

class CryptoPriceService:
    """Fetch and manage cryptocurrency prices"""
    
    async def get_prices(self, coins: Optional[List[str]] = None, vs_currency: str = "usd"):
        """Get current prices for multiple cryptocurrencies"""
        try:
            coin_ids = ",".join(coins or TOP_COINS)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{COINGECKO_BASE_URL}/simple/price",
                    params={
                        "ids": coin_ids,
                        "vs_currencies": vs_currency,
                        "include_24hr_change": "true",
                        "include_24hr_vol": "true",
                        "include_market_cap": "true"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                elif response.status_code == 429:
                    # Rate limited - return mock data for testing
                    logger.warning("CoinGecko rate limited, returning mock data")
                    return self._get_mock_prices(coins or TOP_COINS)
                else:
                    return {
                        "success": False,
                        "error": "Failed to fetch prices"
                    }
        except Exception as e:
            logger.error(f"Error fetching prices: {str(e)}")
            # Return mock data on error for testing
            return self._get_mock_prices(coins or TOP_COINS)
    
    async def get_coin_details(self, coin_id: str):
        """Get detailed information about a specific coin"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{COINGECKO_BASE_URL}/coins/{coin_id}",
                    params={
                        "localization": "false",
                        "tickers": "false",
                        "community_data": "false",
                        "developer_data": "false"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract relevant data
                    market_data = data.get("market_data", {})
                    
                    return {
                        "success": True,
                        "data": {
                            "id": data.get("id"),
                            "symbol": data.get("symbol", "").upper(),
                            "name": data.get("name"),
                            "image": data.get("image", {}).get("large"),
                            "current_price": market_data.get("current_price", {}).get("usd", 0),
                            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                            "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                            "high_24h": market_data.get("high_24h", {}).get("usd", 0),
                            "low_24h": market_data.get("low_24h", {}).get("usd", 0),
                            "price_change_24h": market_data.get("price_change_percentage_24h", 0),
                            "price_change_7d": market_data.get("price_change_percentage_7d", 0),
                            "price_change_30d": market_data.get("price_change_percentage_30d", 0),
                            "circulating_supply": market_data.get("circulating_supply", 0),
                            "total_supply": market_data.get("total_supply", 0),
                            "ath": market_data.get("ath", {}).get("usd", 0),
                            "atl": market_data.get("atl", {}).get("usd", 0),
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Coin not found"
                    }
        except Exception as e:
            logger.error(f"Error fetching coin details: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_market_chart(self, coin_id: str, days: int = 7):
        """Get historical market data for charting"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart",
                    params={
                        "vs_currency": "usd",
                        "days": days
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to fetch chart data"
                    }
        except Exception as e:
            logger.error(f"Error fetching chart data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_trending_coins(self):
        """Get currently trending coins"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{COINGECKO_BASE_URL}/search/trending",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    trending = data.get("coins", [])
                    
                    return {
                        "success": True,
                        "data": [
                            {
                                "id": coin["item"]["id"],
                                "name": coin["item"]["name"],
                                "symbol": coin["item"]["symbol"],
                                "market_cap_rank": coin["item"]["market_cap_rank"],
                                "thumb": coin["item"]["thumb"]
                            }
                            for coin in trending[:10]
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to fetch trending coins"
                    }
        except Exception as e:
            logger.error(f"Error fetching trending coins: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_coins(self, query: str):
        """Search for coins by name or symbol"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{COINGECKO_BASE_URL}/search",
                    params={"query": query},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    coins = data.get("coins", [])
                    
                    return {
                        "success": True,
                        "data": [
                            {
                                "id": coin["id"],
                                "name": coin["name"],
                                "symbol": coin["symbol"],
                                "market_cap_rank": coin.get("market_cap_rank"),
                                "thumb": coin.get("thumb")
                            }
                            for coin in coins[:20]
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": "Search failed"
                    }
        except Exception as e:
            logger.error(f"Error searching coins: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize service
price_service = CryptoPriceService()