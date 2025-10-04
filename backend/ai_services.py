"""
AI Services for Persian Crypto Exchange
Includes: Market Analysis, Trading Signals, Chatbot, Price Predictions
"""
import os
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from datetime import datetime, timezone
import json
import random
import logging

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Load environment
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# ==================== AI CHATBOT ====================

class PersianCryptoBot:
    """AI Chatbot for Persian crypto exchange"""
    
    def __init__(self):
        self.system_message = """شما یک دستیار هوشمند فارسی‌زبان برای صرافی ارز دیجیتال هستید.
وظایف شما:
1. پاسخ به سوالات کاربران درباره خرید، فروش، واریز و برداشت
2. راهنمایی احراز هویت (KYC)
3. توضیح ارزهای دیجیتال مختلف
4. کمک در حل مشکلات
5. ارائه نکات امنیتی

همیشه به فارسی پاسخ دهید. مودب، دقیق و مفید باشید."""
    
    async def chat(self, user_message: str, session_id: str, conversation_history: list = None):
        """Send message to AI and get response"""
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=session_id,
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=user_message)
            response = await chat.send_message(message)
            
            return {
                "success": True,
                "message": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "متاسفانه خطایی رخ داد. لطفا دوباره تلاش کنید."
            }

# ==================== MARKET ANALYST ====================

class MarketAnalyst:
    """AI-powered market analysis and insights"""
    
    def __init__(self):
        self.system_message = """شما یک تحلیلگر بازار ارزهای دیجیتال هستید.
وظایف شما:
1. تحلیل قیمت و روند بازار
2. شناسایی الگوهای معاملاتی
3. ارائه نکات خرید و فروش
4. تحلیل احساسات بازار
5. هشدارهای ریسک

به فارسی و به صورت تخصصی اما قابل فهم پاسخ دهید."""
    
    async def analyze_market(self, coin_data: dict):
        """Analyze market data and provide insights"""
        try:
            prompt = f"""
تحلیل بازار {coin_data.get('name', 'ارز دیجیتال')}:

قیمت فعلی: ${coin_data.get('current_price', 0):,.2f}
تغییرات 24 ساعت: {coin_data.get('price_change_24h', 0):.2f}%
حجم معاملات: ${coin_data.get('volume', 0):,.0f}
بالاترین قیمت 24h: ${coin_data.get('high_24h', 0):,.2f}
پایین‌ترین قیمت 24h: ${coin_data.get('low_24h', 0):,.2f}

لطفا یک تحلیل کوتاه (حداکثر 3 جمله) و یک توصیه معاملاتی ارائه دهید.
"""
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"market_analysis_{datetime.now().timestamp()}",
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=prompt)
            analysis = await chat.send_message(message)
            
            return {
                "success": True,
                "analysis": analysis,
                "coin": coin_data.get('symbol', 'CRYPTO'),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_trading_signals(self, market_data: list):
        """Generate trading signals for multiple coins"""
        try:
            coins_summary = "\n".join([
                f"{coin['symbol']}: ${coin['current_price']:,.2f} ({coin['price_change_24h']:.2f}%)"
                for coin in market_data[:5]
            ])
            
            prompt = f"""
داده‌های بازار فعلی:
{coins_summary}

لطفا 3 سیگنال معاملاتی برتر امروز را با توجه به تغییرات قیمت، حجم و روند ارائه دهید.
هر سیگنال شامل: نام ارز، توصیه (خرید/فروش/نگهداری)، دلیل کوتاه
"""
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"signals_{datetime.now().timestamp()}",
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=prompt)
            signals = await chat.send_message(message)
            
            return {
                "success": True,
                "signals": signals,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# ==================== PORTFOLIO ADVISOR ====================

class PortfolioAdvisor:
    """AI-powered portfolio analysis and recommendations"""
    
    def __init__(self):
        self.system_message = """شما یک مشاور سبد سرمایه ارزهای دیجیتال هستید.
وظایف شما:
1. تحلیل سبد سرمایه کاربر
2. ارائه پیشنهادات متنوع‌سازی
3. محاسبه ریسک و بازده
4. توصیه‌های بهینه‌سازی
5. استراتژی بلندمدت

به فارسی و با در نظر گرفتن مدیریت ریسک پاسخ دهید."""
    
    async def analyze_portfolio(self, portfolio: dict):
        """Analyze user's portfolio and provide recommendations"""
        try:
            holdings_summary = "\n".join([
                f"{asset['symbol']}: {asset['amount']} واحد (ارزش: ${asset['value']:,.2f})"
                for asset in portfolio.get('holdings', [])
            ])
            
            prompt = f"""
تحلیل سبد سرمایه:

کل ارزش: ${portfolio.get('total_value', 0):,.2f}
سود/زیان کل: {portfolio.get('total_pnl_percent', 0):.2f}%

دارایی‌ها:
{holdings_summary}

لطفا:
1. وضعیت کلی سبد را ارزیابی کنید
2. ریسک‌ها را شناسایی کنید
3. پیشنهادات بهینه‌سازی ارائه دهید
"""
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"portfolio_{datetime.now().timestamp()}",
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=prompt)
            advice = await chat.send_message(message)
            
            return {
                "success": True,
                "advice": advice,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# ==================== PRICE PREDICTOR ====================

class PricePredictor:
    """AI-based price prediction (educational purposes)"""
    
    def __init__(self):
        self.system_message = """شما یک تحلیلگر پیش‌بینی قیمت ارزهای دیجیتال هستید.
توجه: پیش‌بینی‌های شما فقط برای آموزش و نباید به عنوان مشاوره سرمایه‌گذاری استفاده شوند.

از تحلیل تکنیکال، احساسات بازار و روندهای تاریخی استفاده کنید."""
    
    async def predict_price(self, coin_data: dict, timeframe: str = "24h"):
        """Predict future price movement"""
        try:
            prompt = f"""
پیش‌بینی قیمت {coin_data.get('name')} برای {timeframe} آینده:

قیمت فعلی: ${coin_data.get('current_price', 0):,.2f}
روند 24 ساعت: {coin_data.get('price_change_24h', 0):.2f}%
حجم: ${coin_data.get('volume', 0):,.0f}

لطفا:
1. احتمال افزایش/کاهش قیمت
2. محدوده قیمتی پیش‌بینی شده
3. سطح اطمینان
4. عوامل تاثیرگذار

⚠️ هشدار: این پیش‌بینی صرفا آموزشی است و تضمینی ندارد.
"""
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"predict_{datetime.now().timestamp()}",
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=prompt)
            prediction = await chat.send_message(message)
            
            return {
                "success": True,
                "prediction": prediction,
                "timeframe": timeframe,
                "disclaimer": "این پیش‌بینی صرفا جنبه آموزشی دارد",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# ==================== RISK ANALYZER ====================

class RiskAnalyzer:
    """AI-powered risk assessment"""
    
    def __init__(self):
        self.system_message = """شما یک تحلیلگر ریسک برای معاملات ارز دیجیتال هستید.
وظایف شما:
1. ارزیابی ریسک تراکنش‌ها
2. شناسایی الگوهای مشکوک
3. هشدارهای امنیتی
4. توصیه‌های مدیریت ریسک

همیشه ایمنی کاربر را در اولویت قرار دهید."""
    
    async def assess_transaction_risk(self, transaction: dict):
        """Assess risk level of a transaction"""
        try:
            # Simple rule-based risk scoring
            risk_score = 0
            risk_factors = []
            
            # High amount
            if transaction.get('amount', 0) > 10000:
                risk_score += 30
                risk_factors.append("مبلغ بالا")
            
            # New user
            if transaction.get('user_age_days', 365) < 7:
                risk_score += 25
                risk_factors.append("کاربر جدید")
            
            # Unusual time
            hour = datetime.now().hour
            if hour < 6 or hour > 23:
                risk_score += 15
                risk_factors.append("ساعت غیرمعمول")
            
            # Determine risk level
            if risk_score >= 60:
                level = "high"
                level_fa = "بالا"
                color = "red"
            elif risk_score >= 30:
                level = "medium"
                level_fa = "متوسط"
                color = "yellow"
            else:
                level = "low"
                level_fa = "پایین"
                color = "green"
            
            return {
                "success": True,
                "risk_level": level,
                "risk_level_fa": level_fa,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "color": color,
                "recommendation": self._get_risk_recommendation(level),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_risk_recommendation(self, level):
        """Get recommendation based on risk level"""
        recommendations = {
            "low": "تراکنش امن به نظر می‌رسد. می‌توانید ادامه دهید.",
            "medium": "لطفا اطلاعات تراکنش را بررسی کنید و در صورت شک، با پشتیبانی تماس بگیرید.",
            "high": "⚠️ این تراکنش ریسک بالایی دارد. قبل از ادامه حتما با پشتیبانی مشورت کنید."
        }
        return recommendations.get(level, "لطفا با احتیاط ادامه دهید.")

# ==================== NEWS SUMMARIZER ====================

class NewsSummarizer:
    """AI-powered crypto news summarization"""
    
    def __init__(self):
        self.system_message = """شما یک خبرنگار تحلیلگر اخبار ارزهای دیجیتال هستید.
وظایف شما:
1. خلاصه‌سازی اخبار مهم
2. تحلیل تاثیر اخبار بر بازار
3. شناسایی اخبار مهم و فوری
4. ترجمه و تفسیر اخبار جهانی

به فارسی و به صورت خلاصه و دقیق پاسخ دهید."""
    
    async def summarize_news(self, news_items: list):
        """Summarize multiple news items"""
        try:
            news_text = "\n".join([
                f"- {item['title']}: {item.get('description', '')[:100]}"
                for item in news_items[:5]
            ])
            
            prompt = f"""
اخبار مهم ارزهای دیجیتال امروز:

{news_text}

لطفا:
1. مهم‌ترین خبر را شناسایی کنید
2. خلاصه‌ای از کل اخبار در 2-3 جمله
3. تاثیر احتمالی بر بازار
"""
            
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"news_{datetime.now().timestamp()}",
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")
            
            message = UserMessage(text=prompt)
            summary = await chat.send_message(message)
            
            return {
                "success": True,
                "summary": summary,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Initialize services
chatbot = PersianCryptoBot()
market_analyst = MarketAnalyst()
portfolio_advisor = PortfolioAdvisor()
price_predictor = PricePredictor()
risk_analyzer = RiskAnalyzer()
news_summarizer = NewsSummarizer()