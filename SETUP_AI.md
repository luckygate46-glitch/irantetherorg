# Smart Trading AI Setup Guide

## Security-First Setup

This guide will help you configure the Smart Trading AI feature securely without exposing your OpenAI API key in code.

## Option 1: Using Admin Panel (Recommended)

1. **Login to Admin Panel**
   - Go to your application URL
   - Login with admin credentials
   - Navigate to: `Settings → AI Settings` (تنظیمات هوش مصنوعی)

2. **Enter Your OpenAI API Key**
   - Get your API key from: https://platform.openai.com/api-keys
   - Paste it in the "کلید OpenAI API" field
   - Click "تست و ذخیره" (Test & Save)

3. **Verify**
   - The system will validate your key
   - If valid, it will be stored securely in the database
   - You'll see a success message

## Option 2: Using MongoDB Directly (Advanced)

If you prefer to set the key directly in the database:

```bash
# Connect to MongoDB
mongosh

# Use your database
use crypto_exchange

# Insert or update AI settings
db.system_settings.updateOne(
  { type: "ai_config" },
  { 
    $set: {
      type: "ai_config",
      openai_api_key: "YOUR_API_KEY_HERE",
      model: "gpt-4o",
      provider: "openai",
      updated_at: new Date().toISOString()
    }
  },
  { upsert: true }
)
```

## Option 3: Environment Variable (Docker/Production)

Add to your backend `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Then restart the backend:
```bash
sudo supervisorctl restart backend
```

## Security Best Practices

✅ **DO:**
- Use the admin panel to set the key (most secure)
- Store the key only in the database or environment variables
- Never commit API keys to version control
- Rotate your API keys regularly

❌ **DON'T:**
- Hardcode API keys in source code
- Share API keys in chat messages
- Commit `.env` files with real keys
- Use API keys in frontend JavaScript

## Features Enabled After Setup

Once configured, users will have access to:

1. **Smart Trading Recommendations** (توصیه‌های هوشمند معاملاتی)
   - AI-powered buy/sell/hold recommendations
   - Risk analysis and suggested amounts
   - Persian language responses

2. **Market Analysis** (تحلیل بازار)
   - Overall market sentiment
   - Top gainers and losers analysis
   - Investment opportunities

3. **AI Chat Assistant** (دستیار چت هوشمند)
   - Answer trading questions
   - Explain market conditions
   - Provide personalized advice

## Cost Considerations

- OpenAI charges per API call
- Typical costs: $0.01 - $0.10 per recommendation
- Monitor usage at: https://platform.openai.com/usage
- Set usage limits in your OpenAI account

## Troubleshooting

**"کلید API معتبر نیست" (Invalid API Key)**
- Check if the key is copied correctly
- Ensure no extra spaces
- Verify the key is active at platform.openai.com

**"خطا در ارتباط با سرویس" (Service Connection Error)**
- Check internet connectivity
- Verify OpenAI services are operational
- Check API usage limits

**Features Not Working**
- Verify API key is saved in admin settings
- Check backend logs: `tail -f /var/log/supervisor/backend.*.log`
- Restart backend: `sudo supervisorctl restart backend`

## Support

For issues or questions, check the logs or contact support.
