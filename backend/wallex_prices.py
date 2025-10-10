"""
Wallex Price Service
Fetches real-time crypto prices in Toman from Wallex API
Official Iranian Exchange API
"""
import httpx
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Wallex API Configuration
WALLEX_API_KEY = "16402|z4Ecrm71K4sQieWClbz27BPLbmfjcnIkzRMCg2JF"
WALLEX_BASE_URL = "https://api.wallex.ir"
WALLEX_MARKETS_ENDPOINT = "/hector/web/v1/markets"

# Symbol mapping from Wallex to our internal IDs
WALLEX_SYMBOL_MAP = {
    'BTCTMN': {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
    'ETHTMN': {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
    'USDTTMN': {'id': 'tether', 'symbol': 'USDT', 'name': 'Tether'},
    'BNBTMN': {'id': 'binancecoin', 'symbol': 'BNB', 'name': 'Binance Coin'},
    'XRPTMN': {'id': 'ripple', 'symbol': 'XRP', 'name': 'XRP'},
    'ADATMN': {'id': 'cardano', 'symbol': 'ADA', 'name': 'Cardano'},
    'SOLTMN': {'id': 'solana', 'symbol': 'SOL', 'name': 'Solana'},
    'DOGETMN': {'id': 'dogecoin', 'symbol': 'DOGE', 'name': 'Dogecoin'},
    'DOTTMN': {'id': 'polkadot', 'symbol': 'DOT', 'name': 'Polkadot'},
    'TRXTMN': {'id': 'tron', 'symbol': 'TRX', 'name': 'TRON'},
    'USDCTMN': {'id': 'usd-coin', 'symbol': 'USDC', 'name': 'USD Coin'},
    'SHIBTMN': {'id': 'shiba-inu', 'symbol': 'SHIB', 'name': 'Shiba Inu'},
    'AVAXTMN': {'id': 'avalanche-2', 'symbol': 'AVAX', 'name': 'Avalanche'},
    'LINKTMN': {'id': 'chainlink', 'symbol': 'LINK', 'name': 'Chainlink'},
    'LTCTMN': {'id': 'litecoin', 'symbol': 'LTC', 'name': 'Litecoin'},
    'UNITMT': {'id': 'uniswap', 'symbol': 'UNI', 'name': 'Uniswap'},
    'TONTMN': {'id': 'the-open-network', 'symbol': 'TON', 'name': 'Toncoin'},
    'DAITMT': {'id': 'dai', 'symbol': 'DAI', 'name': 'Dai'},
    'XLMTMN': {'id': 'stellar', 'symbol': 'XLM', 'name': 'Stellar'},
    'BCHTMN': {'id': 'bitcoin-cash', 'symbol': 'BCH', 'name': 'Bitcoin Cash'},
}

class WallexPriceService:
    """Fetch cryptocurrency prices from Wallex API"""
    
    def __init__(self):
        self.api_key = WALLEX_API_KEY
        self.base_url = WALLEX_BASE_URL
        self.last_update = None
        self.cached_prices = {}
    
    async def fetch_prices(self) -> Dict:
        """Fetch all market prices from Wallex"""
        try:
            logger.info("🔄 Fetching prices from Wallex API...")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    'x-api-key': self.api_key,
                    'Accept': 'application/json'
                }
                
                response = await client.get(
                    f"{self.base_url}{WALLEX_MARKETS_ENDPOINT}",
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Wallex API error: {response.status_code}")
                    return {'success': False, 'data': {}}
                
                data = response.json()
                
                if not data.get('result', {}).get('success'):
                    logger.error("Wallex API returned unsuccessful response")
                    return {'success': False, 'data': {}}
                
                markets = data.get('result', {}).get('markets', [])
                prices = {}
                
                for market in markets:
                    try:
                        symbol = market.get('symbol', '')
                        
                        # Only process TMN-based markets
                        if symbol not in WALLEX_SYMBOL_MAP:
                            continue
                        
                        coin_info = WALLEX_SYMBOL_MAP[symbol]
                        
                        # Get price (already in Toman)
                        price_str = market.get('price', '0')
                        price_tmn = float(price_str) if price_str else 0
                        
                        # Get 24h change
                        change_str = market.get('change_24h', '0')
                        change_24h = float(change_str) if change_str else 0
                        
                        if price_tmn > 0:
                            prices[coin_info['id']] = {
                                'symbol': coin_info['symbol'],
                                'name': coin_info['name'],
                                'price_tmn': price_tmn,
                                'change_24h': change_24h,
                                'last_updated': datetime.now(timezone.utc).isoformat(),
                                'source': 'wallex'
                            }
                            
                            logger.info(f"✅ {coin_info['symbol']}: {price_tmn:,.0f} تومان ({change_24h:+.2f}%)")
                    
                    except Exception as e:
                        logger.debug(f"Error parsing market: {str(e)}")
                        continue
                
                if prices:
                    logger.info(f"✅ Fetched {len(prices)} prices from Wallex")
                    self.cached_prices = prices
                    self.last_update = datetime.now(timezone.utc)
                    return {'success': True, 'data': prices}
                else:
                    logger.warning("No prices found in Wallex response")
                    return {'success': False, 'data': {}}
                
        except Exception as e:
            logger.error(f"Error fetching Wallex prices: {str(e)}")
            return {'success': False, 'data': {}}
    
    async def get_coin_price(self, coin_id: str) -> Optional[Dict]:
        """Get price for a specific coin"""
        if not self.cached_prices:
            result = await self.fetch_prices()
            if not result.get('success'):
                return None
        
        return self.cached_prices.get(coin_id)
    
    def get_cached_prices(self) -> Dict:
        """Get cached prices"""
        if self.cached_prices:
            return {'success': True, 'data': self.cached_prices}
        return {'success': False, 'data': {}}

# Global instance
_wallex_service = None

def get_wallex_service() -> WallexPriceService:
    """Get or create Wallex service instance"""
    global _wallex_service
    if _wallex_service is None:
        _wallex_service = WallexPriceService()
    return _wallex_service
