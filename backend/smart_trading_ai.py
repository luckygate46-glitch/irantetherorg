"""
Smart Trading Assistant AI Service
Provides Persian language trading recommendations using OpenAI
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

class SmartTradingAssistant:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Smart Trading Assistant with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-4o"
        self.provider = "openai"
        
    def _create_chat(self, session_id: str, system_message: str) -> LlmChat:
        """Create LlmChat instance with configuration"""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.provider, self.model)
        return chat
    
    async def get_trading_recommendation(
        self, 
        coin_symbol: str,
        current_price: float,
        price_change_24h: float,
        user_balance: float,
        user_holdings: List[Dict] = None
    ) -> Dict:
        """
        Get AI-powered trading recommendation for a specific coin
        
        Args:
            coin_symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'USDT')
            current_price: Current price in Toman
            price_change_24h: 24h price change percentage
            user_balance: User's wallet balance in Toman
            user_holdings: List of user's current holdings
            
        Returns:
            Dict with recommendation, confidence, and reasoning in Persian
        """
        try:
            system_message = """شما یک دستیار هوشمند معاملات ارزهای دیجیتال هستید که به زبان فارسی پاسخ می‌دهید.
وظیفه شما تحلیل وضعیت بازار و ارائه توصیه‌های معاملاتی دقیق و کاربردی است.

قوانین شما:
1. همیشه به زبان فارسی پاسخ دهید
2. توصیه‌های واضح و قابل اجرا ارائه دهید (خرید، فروش، یا نگهداری)
3. دلایل خود را به طور خلاصه و واضح توضیح دهید
4. سطح اطمینان خود را مشخص کنید (بالا، متوسط، پایین)
5. به وضعیت مالی کاربر توجه کنید و توصیه‌های واقع‌بینانه ارائه دهید
6. از اصطلاحات ساده و قابل فهم استفاده کنید"""

            # Prepare user prompt with market data
            holdings_text = ""
            if user_holdings:
                holdings_text = "\n\nدارایی‌های فعلی کاربر:\n"
                for holding in user_holdings[:5]:  # Show top 5
                    holdings_text += f"- {holding.get('coin_symbol')}: {holding.get('amount', 0):.4f} واحد\n"
            
            price_trend = "افزایشی" if price_change_24h > 0 else "کاهشی" if price_change_24h < 0 else "ثابت"
            
            user_prompt = f"""لطفاً برای ارز {coin_symbol} توصیه معاملاتی ارائه دهید:

📊 اطلاعات بازار:
- قیمت فعلی: {current_price:,.0f} تومان
- تغییر ۲۴ ساعته: {price_change_24h:.2f}%
- روند: {price_trend}

💰 اطلاعات کاربر:
- موجودی کیف پول: {user_balance:,.0f} تومان{holdings_text}

لطفاً در قالب JSON پاسخ دهید:
{{
    "recommendation": "خرید" یا "فروش" یا "نگهداری",
    "confidence": "بالا" یا "متوسط" یا "پایین",
    "reasoning": "دلیل توصیه (۲-۳ جمله)",
    "suggested_amount": مبلغ پیشنهادی بر اساس موجودی (عدد),
    "risk_level": "کم" یا "متوسط" یا "زیاد",
    "key_points": ["نکته کلیدی ۱", "نکته کلیدی ۲", "نکته کلیدی ۳"]
}}"""

            # Create chat and get response
            session_id = f"trading_{coin_symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            chat = self._create_chat(session_id, system_message)
            
            message = UserMessage(text=user_prompt)
            response = await chat.send_message(message)
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                response_text = response.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                recommendation_data = json.loads(response_text)
                
                # Add metadata
                recommendation_data["coin_symbol"] = coin_symbol
                recommendation_data["timestamp"] = datetime.now().isoformat()
                recommendation_data["current_price"] = current_price
                
                return recommendation_data
                
            except json.JSONDecodeError:
                # If JSON parsing fails, raise error - no fallback
                raise Exception(f"خطا در تجزیه پاسخ AI: {response[:200]}")
                
        except Exception as e:
            print(f"Error in get_trading_recommendation: {str(e)}")
            # Return fallback recommendation
            return {
                "coin_symbol": coin_symbol,
                "recommendation": "نگهداری",
                "confidence": "پایین",
                "reasoning": f"خطا در تحلیل: {str(e)}. لطفاً دقایقی دیگر امتحان کنید.",
                "suggested_amount": 0,
                "risk_level": "نامشخص",
                "key_points": ["خطا در ارتباط با سرویس تحلیل هوشمند"],
                "timestamp": datetime.now().isoformat(),
                "current_price": current_price,
                "error": str(e)
            }
    
    async def get_market_analysis(
        self,
        coins_data: List[Dict],
        timeframe: str = "24h"
    ) -> Dict:
        """
        Get overall market analysis and trends
        
        Args:
            coins_data: List of coins with their data
            timeframe: Analysis timeframe (e.g., '24h', '7d', '30d')
            
        Returns:
            Dict with market analysis in Persian
        """
        try:
            system_message = """شما یک تحلیلگر بازار ارزهای دیجیتال هستید که به زبان فارسی گزارش ارائه می‌دهید.
وظیفه شما تحلیل کلی وضعیت بازار و ارائه بینش‌های مفید برای معامله‌گران است."""

            # Prepare market data summary
            top_gainers = sorted(coins_data, key=lambda x: x.get('price_change_24h', 0), reverse=True)[:3]
            top_losers = sorted(coins_data, key=lambda x: x.get('price_change_24h', 0))[:3]
            
            gainers_text = "\n".join([
                f"- {coin.get('symbol')}: +{coin.get('price_change_24h', 0):.2f}%"
                for coin in top_gainers
            ])
            
            losers_text = "\n".join([
                f"- {coin.get('symbol')}: {coin.get('price_change_24h', 0):.2f}%"
                for coin in top_losers
            ])
            
            user_prompt = f"""لطفاً تحلیل کلی از وضعیت بازار ارائه دهید:

📈 بیشترین رشدها ({timeframe}):
{gainers_text}

📉 بیشترین کاهش‌ها ({timeframe}):
{losers_text}

تعداد کل ارزها: {len(coins_data)}

لطفاً در قالب JSON پاسخ دهید:
{{
    "overall_sentiment": "صعودی" یا "نزولی" یا "خنثی",
    "market_summary": "خلاصه وضعیت بازار (۲-۳ جمله)",
    "opportunities": ["فرصت ۱", "فرصت ۲"],
    "risks": ["ریسک ۱", "ریسک ۲"],
    "recommendation": "توصیه کلی برای معامله‌گران"
}}"""

            session_id = f"market_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            chat = self._create_chat(session_id, system_message)
            
            message = UserMessage(text=user_prompt)
            response = await chat.send_message(message)
            
            # Parse JSON response
            try:
                response_text = response.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                analysis_data = json.loads(response_text)
                analysis_data["timestamp"] = datetime.now().isoformat()
                analysis_data["timeframe"] = timeframe
                
                return analysis_data
                
            except json.JSONDecodeError:
                return {
                    "overall_sentiment": "خنثی",
                    "market_summary": response[:300],
                    "opportunities": [],
                    "risks": [],
                    "recommendation": "بررسی دقیق‌تر بازار توصیه می‌شود",
                    "timestamp": datetime.now().isoformat(),
                    "timeframe": timeframe
                }
                
        except Exception as e:
            print(f"Error in get_market_analysis: {str(e)}")
            return {
                "overall_sentiment": "نامشخص",
                "market_summary": f"خطا در تحلیل بازار: {str(e)}",
                "opportunities": [],
                "risks": ["خطا در ارتباط با سرویس تحلیل"],
                "recommendation": "لطفاً دقایقی دیگر امتحان کنید",
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "error": str(e)
            }
    
    async def chat_with_assistant(
        self,
        user_message: str,
        user_context: Dict,
        chat_history: List[Dict] = None
    ) -> str:
        """
        Interactive chat with trading assistant
        
        Args:
            user_message: User's question or request
            user_context: User's portfolio and balance info
            chat_history: Previous chat messages
            
        Returns:
            Assistant's response in Persian
        """
        try:
            system_message = f"""شما یک دستیار هوشمند معاملات ارزهای دیجیتال هستید.
کاربر فعلی:
- موجودی: {user_context.get('balance', 0):,.0f} تومان
- سطح KYC: {user_context.get('kyc_level', 0)}

به سوالات کاربر درباره معاملات، قیمت‌ها، و استراتژی‌های سرمایه‌گذاری به زبان فارسی پاسخ دهید.
پاسخ‌های خود را کوتاه، واضح، و کاربردی نگه دارید."""

            session_id = f"chat_{user_context.get('user_id', 'unknown')}_{datetime.now().strftime('%Y%m%d')}"
            chat = self._create_chat(session_id, system_message)
            
            message = UserMessage(text=user_message)
            response = await chat.send_message(message)
            
            return response
            
        except Exception as e:
            print(f"Error in chat_with_assistant: {str(e)}")
            return f"متأسفانه در حال حاضر نمی‌توانم به سوال شما پاسخ دهم. خطا: {str(e)}"
