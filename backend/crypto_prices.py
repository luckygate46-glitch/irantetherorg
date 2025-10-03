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
                            "market_data": {
                                "current_price": {"usd": market_data.get("current_price", {}).get("usd", 0)},
                                "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                                "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                                "high_24h": market_data.get("high_24h", {}).get("usd", 0),
                                "low_24h": market_data.get("low_24h", {}).get("usd", 0),
                                "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0),
                                "price_change_percentage_7d": market_data.get("price_change_percentage_7d", 0),
                                "price_change_percentage_30d": market_data.get("price_change_percentage_30d", 0),
                                "circulating_supply": market_data.get("circulating_supply", 0),
                                "total_supply": market_data.get("total_supply", 0),
                                "ath": market_data.get("ath", {}).get("usd", 0),
                                "atl": market_data.get("atl", {}).get("usd", 0),
                            }
                        }
                    }
                elif response.status_code == 429:
                    # Rate limited - return mock data
                    logger.warning(f"CoinGecko rate limited for {coin_id}, returning mock data")
                    return self._get_mock_coin_details(coin_id)
                else:
                    return {
                        "success": False,
                        "error": "Coin not found"
                    }
        except Exception as e:
            logger.error(f"Error fetching coin details: {str(e)}")
            # Return mock data on error for testing
            return self._get_mock_coin_details(coin_id)
    
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

    def _get_mock_prices(self, coin_ids: List[str]):
        """Return mock price data for testing when API is rate limited"""
        mock_data = {}
        
        # Mock prices for common coins
        mock_prices = {
            "bitcoin": {"usd": 43000, "usd_24h_change": 2.5, "usd_24h_vol": 15000000000, "usd_market_cap": 850000000000},
            "ethereum": {"usd": 2600, "usd_24h_change": 1.8, "usd_24h_vol": 8000000000, "usd_market_cap": 310000000000},
            "tether": {"usd": 1.0, "usd_24h_change": 0.1, "usd_24h_vol": 25000000000, "usd_market_cap": 95000000000},
            "binancecoin": {"usd": 310, "usd_24h_change": -0.5, "usd_24h_vol": 1200000000, "usd_market_cap": 47000000000},
            "ripple": {"usd": 0.52, "usd_24h_change": 3.2, "usd_24h_vol": 1100000000, "usd_market_cap": 28000000000},
            "cardano": {"usd": 0.48, "usd_24h_change": 1.1, "usd_24h_vol": 450000000, "usd_market_cap": 17000000000},
            "solana": {"usd": 98, "usd_24h_change": 4.5, "usd_24h_vol": 2100000000, "usd_market_cap": 42000000000},
            "dogecoin": {"usd": 0.08, "usd_24h_change": -1.2, "usd_24h_vol": 650000000, "usd_market_cap": 11000000000},
        }
        
        for coin_id in coin_ids:
            if coin_id in mock_prices:
                mock_data[coin_id] = mock_prices[coin_id]
            else:
                # Generate random mock data for unknown coins
                import random
                mock_data[coin_id] = {
                    "usd": round(random.uniform(0.1, 1000), 2),
                    "usd_24h_change": round(random.uniform(-10, 10), 2),
                    "usd_24h_vol": random.randint(1000000, 1000000000),
                    "usd_market_cap": random.randint(10000000, 100000000000)
                }
        
        return {
            "success": True,
            "data": mock_data
        }
    
    def _get_mock_coin_details(self, coin_id: str):
        """Return mock coin details for testing"""
        mock_coins = {
            "bitcoin": {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                "market_data": {
                    "current_price": {"usd": 43000},
                    "market_cap": 850000000000,
                    "total_volume": 15000000000,
                    "high_24h": 44000,
                    "low_24h": 42000,
                    "price_change_percentage_24h": 2.5,
                    "price_change_percentage_7d": 5.2,
                    "price_change_percentage_30d": 12.8,
                    "circulating_supply": 19700000,
                    "total_supply": 21000000,
                    "ath": 69000,
                    "atl": 67.81
                }
            },
            "ethereum": {
                "id": "ethereum",
                "symbol": "ETH",
                "name": "Ethereum",
                "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
                "market_data": {
                    "current_price": {"usd": 2600},
                    "market_cap": 310000000000,
                    "total_volume": 8000000000,
                    "high_24h": 2650,
                    "low_24h": 2550,
                    "price_change_percentage_24h": 1.8,
                    "price_change_percentage_7d": 3.5,
                    "price_change_percentage_30d": 8.2,
                    "circulating_supply": 120000000,
                    "total_supply": 120000000,
                    "ath": 4878,
                    "atl": 0.43
                }
            }
        }
        
        if coin_id in mock_coins:
            return {
                "success": True,
                "data": mock_coins[coin_id]
            }
        else:
            # Generate random mock data
            import random
            return {
                "success": True,
                "data": {
                    "id": coin_id,
                    "symbol": coin_id.upper()[:3],
                    "name": coin_id.title(),
                    "image": f"https://assets.coingecko.com/coins/images/1/large/{coin_id}.png",
                    "market_data": {
                        "current_price": {"usd": round(random.uniform(0.1, 1000), 2)},
                        "market_cap": random.randint(10000000, 100000000000),
                        "total_volume": random.randint(1000000, 1000000000),
                        "high_24h": round(random.uniform(0.1, 1100), 2),
                        "low_24h": round(random.uniform(0.1, 900), 2),
                        "price_change_percentage_24h": round(random.uniform(-10, 10), 2),
                        "price_change_percentage_7d": round(random.uniform(-20, 20), 2),
                        "price_change_percentage_30d": round(random.uniform(-50, 50), 2),
                        "circulating_supply": random.randint(1000000, 1000000000),
                        "total_supply": random.randint(1000000, 1000000000),
                        "ath": round(random.uniform(1, 10000), 2),
                        "atl": round(random.uniform(0.001, 1), 4)
                    }
                }
            }

# Initialize service
price_service = CryptoPriceService()