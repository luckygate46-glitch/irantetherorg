"""
Abantether Web Scraper - Reads actual prices from abantether.com/coins
Uses crawl_tool to extract real-time cryptocurrency prices in Toman
"""
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Coin mapping
COIN_MAP = {
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
    'TON': {'id': 'the-open-network', 'name': 'Toncoin', 'symbol': 'TON'},
    'DAI': {'id': 'dai', 'name': 'Dai', 'symbol': 'DAI'},
    'XLM': {'id': 'stellar', 'name': 'Stellar', 'symbol': 'XLM'},
    'BCH': {'id': 'bitcoin-cash', 'name': 'Bitcoin Cash', 'symbol': 'BCH'},
}

def parse_abantether_prices(markdown_content: str) -> Dict:
    """
    Parse cryptocurrency prices from Abantether markdown content
    
    Example format from markdown:
    | [![BTC](...) بیت کوینBTC](link) | 12,959,940,780 خرید 12,834,946,999 فروش | ... | -6.38% | ...
    """
    prices = {}
    
    try:
        # Split by lines
        lines = markdown_content.split('\n')
        
        for line in lines:
            # Look for table rows with coin data
            if '|' not in line or 'خرید' not in line:
                continue
            
            try:
                # Extract symbol from the line
                symbol_match = re.search(r'\]\(https://abantether\.com/coin/([A-Z]+)\)', line)
                if not symbol_match:
                    continue
                
                symbol = symbol_match.group(1)
                
                if symbol not in COIN_MAP:
                    continue
                
                coin_info = COIN_MAP[symbol]
                
                # Extract buy price (first number before "خرید")
                # Format: 12,959,940,780 خرید or 115,090 خرید
                price_match = re.search(r'([\d,]+)\s*خرید', line)
                if not price_match:
                    continue
                
                price_str = price_match.group(1).replace(',', '')
                price_tmn = float(price_str)
                
                # Extract 24h change (percentage)
                # Format: -6.38% or 0.19%
                change_match = re.search(r'([-+]?\d+\.?\d*)\s*%', line)
                change_24h = 0
                if change_match:
                    change_24h = float(change_match.group(1))
                
                # Store the price data
                prices[coin_info['id']] = {
                    'symbol': symbol,
                    'name': coin_info['name'],
                    'price_tmn': price_tmn,
                    'change_24h': change_24h,
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'source': 'abantether'
                }
                
                logger.info(f"✅ Parsed {symbol}: {price_tmn:,.0f} تومان (Change: {change_24h:+.2f}%)")
                
            except Exception as e:
                logger.debug(f"Error parsing line: {str(e)}")
                continue
        
        return prices
        
    except Exception as e:
        logger.error(f"Error parsing Abantether markdown: {str(e)}")
        return {}

async def fetch_abantether_prices_with_crawl() -> Dict:
    """
    Fetch prices from Abantether using crawl_tool integration
    Note: This function should be called from the main service
    """
    # This will be called by the main price service
    logger.info("📊 Ready to fetch Abantether prices via crawl tool")
    return {}
