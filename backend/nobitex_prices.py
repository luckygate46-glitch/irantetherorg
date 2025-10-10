"""
Nobitex Price Scraper Service
Fetches real-time crypto prices in Toman from Nobitex.ir
Updates every 30 minutes in background
"""
import httpx
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# Map Nobitex symbols to our internal coin IDs
NOBITEX_COIN_MAP = {
    'BTC': {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'BTC'},
    'ETH': {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'ETH'},
    'USDT': {'id': 'tether', 'name': 'Tether', 'symbol': 'USDT'},
    'BNB': {'id': 'binancecoin', 'name': 'Binance Coin', 'symbol': 'BNB'},
    'XRP': {'id': 'ripple', 'name': 'XRP', 'symbol': 'XRP'},
    'ADA': {'id': 'cardano', 'name': 'Cardano', 'symbol': 'ADA'},
    'SOL': {'id': 'solana', 'name': 'Solana', 'symbol': 'SOL'},
    'DOGE': {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'DOGE'},
    'DOT': {'id': 'polkadot', 'name': 'Polkadot', 'symbol': 'DOT'},
    'TRX': {'id': 'tron', 'name': 'TRON', 'symbol': 'TRX'},
    'USDC': {'id': 'usd-coin', 'name': 'USD Coin', 'symbol': 'USDC'},
    'SHIB': {'id': 'shiba-inu', 'name': 'Shiba Inu', 'symbol': 'SHIB'},
    'AVAX': {'id': 'avalanche-2', 'name': 'Avalanche', 'symbol': 'AVAX'},
    'LINK': {'id': 'chainlink', 'name': 'Chainlink', 'symbol': 'LINK'},
    'LTC': {'id': 'litecoin', 'name': 'Litecoin', 'symbol': 'LTC'},
    'UNI': {'id': 'uniswap', 'name': 'Uniswap', 'symbol': 'UNI'},
    'MATIC': {'id': 'matic-network', 'name': 'Polygon', 'symbol': 'MATIC'},
    'XLM': {'id': 'stellar', 'name': 'Stellar', 'symbol': 'XLM'},
    'ETC': {'id': 'ethereum-classic', 'name': 'Ethereum Classic', 'symbol': 'ETC'},
    'BCH': {'id': 'bitcoin-cash', 'name': 'Bitcoin Cash', 'symbol': 'BCH'},
}

class NobitexPriceService:
    """Scrape and manage cryptocurrency prices in Toman from Nobitex"""
    
    def __init__(self, db=None):
        self.db = db
        self.last_update = None
        self.cached_prices = {}
        self.update_interval = 30 * 60  # 30 minutes in seconds
        
    async def scrape_nobitex_prices(self) -> Dict:
        """Scrape prices from Nobitex.ir website"""
        try:
            logger.info("🔄 Scraping Nobitex prices...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Add headers to mimic browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                
                response = await client.get('https://nobitex.ir/price/', headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch Nobitex page: {response.status_code}")
                    return self._get_fallback_prices()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                prices = {}
                
                # Find all crypto price elements
                # Nobitex uses various structures, we'll try to find price data
                
                # Method 1: Look for price table or list
                price_elements = soup.find_all(['tr', 'div'], class_=re.compile(r'price|coin|crypto', re.I))
                
                for element in price_elements:
                    try:
                        # Try to extract coin symbol and price
                        text = element.get_text()
                        
                        # Look for known symbols
                        for symbol, coin_info in NOBITEX_COIN_MAP.items():
                            if symbol in text or coin_info['name'] in text:
                                # Extract price (numbers with commas)
                                price_match = re.search(r'([\d,]+)\s*(?:تومان|TMN|IRT)', text)
                                if price_match:
                                    price_str = price_match.group(1).replace(',', '')
                                    price_tmn = float(price_str)
                                    
                                    # Extract 24h change if available
                                    change_match = re.search(r'([-+]?\d+\.?\d*)\s*%', text)
                                    change_24h = float(change_match.group(1)) if change_match else 0
                                    
                                    prices[coin_info['id']] = {
                                        'symbol': symbol,
                                        'name': coin_info['name'],
                                        'price_tmn': price_tmn,
                                        'change_24h': change_24h,
                                        'last_updated': datetime.now(timezone.utc).isoformat()
                                    }
                    except Exception as e:
                        continue
                
                # If scraping didn't work, try API approach (Nobitex has public API)
                if len(prices) < 5:
                    logger.warning("Scraping yielded few results, trying Nobitex API...")
                    prices = await self._fetch_nobitex_api()
                
                if prices:
                    logger.info(f"✅ Successfully fetched {len(prices)} prices from Nobitex")
                    self.cached_prices = prices
                    self.last_update = datetime.now(timezone.utc)
                    
                    # Store in database
                    if self.db:
                        await self._store_prices_in_db(prices)
                    
                    return {'success': True, 'data': prices}
                else:
                    logger.warning("No prices found, using fallback")
                    return self._get_fallback_prices()
                    
        except Exception as e:
            logger.error(f"Error scraping Nobitex: {str(e)}")
            return self._get_fallback_prices()
    
    async def _fetch_nobitex_api(self) -> Dict:
        """Fetch prices from Nobitex public API"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get('https://api.nobitex.ir/v2/orderbook/all')
                
                if response.status_code == 200:
                    data = response.json()
                    prices = {}
                    
                    # Parse API response
                    for symbol, coin_info in NOBITEX_COIN_MAP.items():
                        # Nobitex uses pairs like BTCIRT, ETHIRT
                        pair_key = f"{symbol}IRT"
                        
                        if pair_key in data:
                            pair_data = data[pair_key]
                            
                            # Get last price
                            last_price = float(pair_data.get('lastTradePrice', 0))
                            if last_price > 0:
                                prices[coin_info['id']] = {
                                    'symbol': symbol,
                                    'name': coin_info['name'],
                                    'price_tmn': last_price,
                                    'change_24h': 0,  # API might not provide this
                                    'last_updated': datetime.now(timezone.utc).isoformat()
                                }
                    
                    return prices
                    
        except Exception as e:
            logger.error(f"Error fetching Nobitex API: {str(e)}")
            return {}
    
    async def _store_prices_in_db(self, prices: Dict):
        """Store prices in MongoDB"""
        try:
            if self.db is None:
                return
            
            # Store each price with timestamp
            for coin_id, price_data in prices.items():
                await self.db.crypto_prices.update_one(
                    {'coin_id': coin_id},
                    {
                        '$set': {
                            'coin_id': coin_id,
                            'symbol': price_data['symbol'],
                            'name': price_data['name'],
                            'price_tmn': price_data['price_tmn'],
                            'change_24h': price_data['change_24h'],
                            'last_updated': price_data['last_updated'],
                            'source': 'nobitex'
                        }
                    },
                    upsert=True
                )
            
            logger.info(f"✅ Stored {len(prices)} prices in database")
            
        except Exception as e:
            logger.error(f"Error storing prices in DB: {str(e)}")
    
    async def get_prices_from_db(self) -> Dict:
        """Get cached prices from database"""
        try:
            if not self.db:
                return self._get_fallback_prices()
            
            prices_cursor = self.db.crypto_prices.find({})
            prices_list = await prices_cursor.to_list(length=None)
            
            if not prices_list:
                # No cached prices, fetch fresh
                return await self.scrape_nobitex_prices()
            
            prices = {}
            for price_doc in prices_list:
                coin_id = price_doc.get('coin_id')
                prices[coin_id] = {
                    'symbol': price_doc.get('symbol'),
                    'name': price_doc.get('name'),
                    'price_tmn': price_doc.get('price_tmn', 0),
                    'change_24h': price_doc.get('change_24h', 0),
                    'last_updated': price_doc.get('last_updated')
                }
            
            return {'success': True, 'data': prices, 'from_cache': True}
            
        except Exception as e:
            logger.error(f"Error getting prices from DB: {str(e)}")
            return self._get_fallback_prices()
    
    async def get_coin_price(self, coin_id: str) -> Optional[Dict]:
        """Get price for a specific coin"""
        prices_data = await self.get_prices_from_db()
        
        if prices_data.get('success'):
            return prices_data['data'].get(coin_id)
        
        return None
    
    def _get_fallback_prices(self) -> Dict:
        """Return realistic fallback prices in Toman"""
        # These are approximate prices as of now
        fallback = {
            'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin', 'price_tmn': 3500000000, 'change_24h': 2.5},
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum', 'price_tmn': 175000000, 'change_24h': 1.8},
            'tether': {'symbol': 'USDT', 'name': 'Tether', 'price_tmn': 63000, 'change_24h': 0.1},
            'binancecoin': {'symbol': 'BNB', 'name': 'Binance Coin', 'price_tmn': 35000000, 'change_24h': 3.2},
            'ripple': {'symbol': 'XRP', 'name': 'XRP', 'price_tmn': 35000, 'change_24h': -1.5},
            'cardano': {'symbol': 'ADA', 'name': 'Cardano', 'price_tmn': 25000, 'change_24h': 4.1},
            'solana': {'symbol': 'SOL', 'name': 'Solana', 'price_tmn': 9500000, 'change_24h': 5.3},
            'dogecoin': {'symbol': 'DOGE', 'name': 'Dogecoin', 'price_tmn': 7500, 'change_24h': -0.8},
            'polkadot': {'symbol': 'DOT', 'name': 'Polkadot', 'price_tmn': 280000, 'change_24h': 2.1},
            'tron': {'symbol': 'TRX', 'name': 'TRON', 'price_tmn': 12000, 'change_24h': 1.2},
        }
        
        for coin_id, data in fallback.items():
            data['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        logger.warning("⚠️  Using fallback prices")
        return {'success': True, 'data': fallback, 'fallback': True}

# Background task scheduler
class PriceUpdateScheduler:
    """Schedule regular price updates from Nobitex"""
    
    def __init__(self, db):
        self.db = db
        self.price_service = NobitexPriceService(db)
        self.is_running = False
        
    async def start(self):
        """Start the background price update task"""
        if self.is_running:
            logger.info("Price scheduler already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting Nobitex price update scheduler (every 30 minutes)")
        
        # Initial fetch
        await self.price_service.scrape_nobitex_prices()
        
        # Schedule updates every 30 minutes
        while self.is_running:
            try:
                await asyncio.sleep(30 * 60)  # 30 minutes
                logger.info("⏰ Scheduled price update triggered")
                await self.price_service.scrape_nobitex_prices()
            except Exception as e:
                logger.error(f"Error in price update scheduler: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop(self):
        """Stop the background task"""
        self.is_running = False
        logger.info("🛑 Stopping price update scheduler")

# Global scheduler instance
_scheduler = None

def get_price_service(db) -> NobitexPriceService:
    """Get or create price service instance"""
    return NobitexPriceService(db)

async def start_price_scheduler(db):
    """Start the global price update scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = PriceUpdateScheduler(db)
        # Start in background
        asyncio.create_task(_scheduler.start())
    return _scheduler

def stop_price_scheduler():
    """Stop the global price update scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
