import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Trade = ({ user, onLogout }) => {
  const { asset } = useParams(); // Get asset from URL parameter
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('buy');
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [coins, setCoins] = useState([]);
  const [myHoldings, setMyHoldings] = useState([]);
  const [myOrders, setMyOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [orderLoading, setOrderLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Order form states
  const [buyAmount, setBuyAmount] = useState('');
  const [sellAmount, setSellAmount] = useState('');
  const [tradeAmount, setTradeAmount] = useState('');
  const [targetCoin, setTargetCoin] = useState(null);
  const [walletAddress, setWalletAddress] = useState('');
  
  // AI Recommendation states
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [showAiPanel, setShowAiPanel] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    // If asset parameter is provided, select it automatically
    if (asset && coins.length > 0) {
      const assetCoin = coins.find(coin => 
        coin.symbol.toLowerCase() === asset.toLowerCase() ||
        coin.name.toLowerCase() === asset.toLowerCase()
      );
      if (assetCoin) {
        setSelectedCoin(assetCoin);
      }
    } else if (!selectedCoin && coins.length > 0) {
      // If no coin is selected and no asset parameter, default to first popular coin (usually BTC or USDT)
      const defaultCoin = coins.find(coin => coin.symbol === 'USDT') || coins[0];
      if (defaultCoin) {
        console.log('🪙 Auto-selecting default coin:', defaultCoin.symbol);
        setSelectedCoin(defaultCoin);
      }
    }
  }, [asset, coins]);

  useEffect(() => {
    // Fetch AI recommendation when coin is selected
    if (selectedCoin && showAiPanel) {
      fetchAiRecommendation(selectedCoin.symbol);
    }
  }, [selectedCoin]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const [pricesRes, holdingsRes, ordersRes] = await Promise.all([
        axios.get(`${API}/crypto/prices`),
        axios.get(`${API}/trading/holdings/my`, config),
        axios.get(`${API}/trading/orders/my`, config)
      ]);

      if (pricesRes.data.success) {
        const coinsList = Object.entries(pricesRes.data.data).map(([id, data]) => ({
          id,
          symbol: data.symbol?.toUpperCase() || id.toUpperCase(),
          name: data.name || id,
          current_price: data.price_tmn || 0,  // Now in Toman from Nobitex
          price_change_24h: data.change_24h || 0,
          image: `https://assets.coingecko.com/coins/images/${getImageId(id)}/small/${id}.png`,
          last_updated: data.last_updated
        }));
        
        setCoins(coinsList);
        if (!selectedCoin && coinsList.length > 0) {
          setSelectedCoin(coinsList[0]);
        }
      }

      setMyHoldings(holdingsRes.data);
      setMyOrders(ordersRes.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌ها:', error);
    } finally {
      setLoading(false);
    }
  };

  const getImageId = (coinId) => {
    const imageMap = {
      'bitcoin': 1,
      'ethereum': 279,
      'tether': 325,
      'binancecoin': 825,
      'solana': 4128,
      'usd-coin': 6319,
      'steth': 13442,
      'xrp': 44,
      'dogecoin': 5,
      'tron': 1094
    };
    return imageMap[coinId] || 1;
  };

  const fetchAiRecommendation = async (coinSymbol) => {
    if (!coinSymbol) return;
    
    try {
      setAiLoading(true);
      setAiError(null);
      
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const response = await axios.get(`${API}/ai/smart-recommendation/${coinSymbol}`, config);
      setAiRecommendation(response.data);
      console.log('✅ AI Recommendation:', response.data);
    } catch (error) {
      console.error('❌ Error fetching AI recommendation:', error);
      
      // Check if it's a configuration error - hide AI panel if service is not configured
      if (error.response?.status === 503) {
        console.log('ℹ️ AI service not configured - hiding AI panel');
        setShowAiPanel(false); // Auto-hide the panel instead of showing error
      } else {
        setAiError('خطا در دریافت توصیه هوشمند');
      }
    } finally {
      setAiLoading(false);
    }
  };

  const checkWalletAddress = async (coinSymbol) => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const response = await axios.get(`${API}/user/wallet-addresses`, config);
      const walletAddresses = response.data || [];
      
      // Check if user has a wallet for this specific coin
      const hasWallet = walletAddresses.some(wallet => 
        wallet.symbol === coinSymbol && wallet.verified
      );
      
      return { hasWallet, walletAddresses };
    } catch (error) {
      console.error('Error checking wallet addresses:', error);
      return { hasWallet: false, walletAddresses: [] };
    }
  };

  const handleOrder = async (orderType) => {
    console.log('🔴 BUTTON CLICKED! Order type:', orderType);
    console.log('🪙 Selected coin:', selectedCoin);
    console.log('👤 User:', user);
    
    if (!selectedCoin) {
      alert('لطفا یک ارز انتخاب کنید');
      return;
    }

    setOrderLoading(true);
    
    try {
      // Check for wallet address before placing buy order
      if (orderType === 'buy') {
        console.log('🔍 Checking wallet address...');
        try {
          const { hasWallet, walletAddresses } = await checkWalletAddress(selectedCoin.symbol);
          console.log('✅ Wallet check result:', hasWallet);
          console.log('📋 Available wallets:', walletAddresses);
          
          if (!hasWallet) {
            setOrderLoading(false);
            const shouldAddWallet = window.confirm(
              `برای خرید ${selectedCoin.symbol} نیاز به آدرس کیف پول دارید.\n\nآیا می‌خواهید الان آدرس کیف پول خود را اضافه کنید؟`
            );
            
            if (shouldAddWallet) {
              // Redirect to profile page
              navigate('/profile?tab=wallets');
              return;
            } else {
              return; // Cancel the order
            }
          } else {
            // User has wallet saved - use it automatically
            const savedWallet = walletAddresses.find(w => w.symbol === selectedCoin.symbol && w.verified);
            if (savedWallet) {
              console.log('✅ Using saved wallet address:', savedWallet.address);
              // We'll use this in the orderData below
            }
          }
        } catch (walletError) {
          console.error('⚠️ Wallet check error (continuing anyway):', walletError);
          // Continue with order even if wallet check fails - backend will validate
        }
      }

      const orderData = {
        order_type: orderType,
        coin_symbol: selectedCoin.symbol,
        coin_id: selectedCoin.id
      };

      if (orderType === 'buy') {
        const amount = parseFloat(buyAmount);
        console.log('💵 Buy amount:', amount);
        
        if (!amount || amount <= 0) {
          alert('لطفا مبلغ معتبری وارد کنید');
          setOrderLoading(false);
          return;
        }
        
        // Check if user has sufficient balance
        const userBalance = user?.wallet_balance_tmn || 0;
        console.log('💰 Balance check:', { amount, userBalance, user });
        
        if (amount > userBalance) {
          setOrderLoading(false);
          alert(`موجودی شما کافی نیست.\nمبلغ درخواستی: ${new Intl.NumberFormat('fa-IR').format(amount)} تومان\nموجودی فعلی: ${new Intl.NumberFormat('fa-IR').format(userBalance)} تومان`);
          return;
        }
        
        orderData.amount_tmn = amount;
        
        // Include wallet address if provided, otherwise backend will use saved one
        if (walletAddress && walletAddress.trim() !== '') {
          orderData.user_wallet_address = walletAddress;
          console.log('📬 Using provided wallet address');
        } else {
          console.log('📬 Will use saved wallet address from profile');
        }
      } else if (orderType === 'sell') {
        const amount = parseFloat(sellAmount);
        if (!amount || amount <= 0) {
          alert('لطفا مقدار معتبری وارد کنید');
          setOrderLoading(false);
          return;
        }
        orderData.amount_crypto = amount;
      } else if (orderType === 'trade') {
        const amount = parseFloat(tradeAmount);
        if (!amount || amount <= 0 || !targetCoin) {
          alert('لطفا مقدار معتبری وارد کنید و ارز مقصد را انتخاب کنید');
          setOrderLoading(false);
          return;
        }
        orderData.amount_crypto = amount;
        orderData.target_coin_symbol = targetCoin.symbol;
        orderData.target_coin_id = targetCoin.id;
      }

      console.log('📤 Sending order to backend:', orderData);
      const token = localStorage.getItem('token');
      
      if (!token) {
        alert('لطفا ابتدا وارد شوید');
        setOrderLoading(false);
        navigate('/auth');
        return;
      }
      
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const response = await axios.post(`${API}/trading/order`, orderData, config);
      console.log('✅ Order response:', response.data);
      
      // Refresh user data to get updated balance
      try {
        const userResponse = await axios.get(`${API}/auth/me`, config);
        console.log('✅ Balance updated:', userResponse.data.wallet_balance_tmn);
        // Trigger parent component to update user state
        window.dispatchEvent(new CustomEvent('user-balance-updated', { detail: userResponse.data }));
      } catch (refreshError) {
        console.error('⚠️ Balance refresh failed:', refreshError);
      }
      
      // Generate invoice/faktor
      const orderId = response.data.order?.id || `ORD-${Date.now()}`;
      const orderDate = new Date().toLocaleDateString('fa-IR');
      const orderTime = new Date().toLocaleTimeString('fa-IR');
      
      // Show detailed success message with faktor (invoice)
      const successMsg = orderType === 'buy' 
        ? `╔═══════════════════════════════╗
║        🧾 فاکتور خرید        ║
╚═══════════════════════════════╝

✅ سفارش شما با موفقیت ثبت شد!

📋 شماره سفارش: ${orderId}
📅 تاریخ: ${orderDate}
🕐 ساعت: ${orderTime}

💰 مبلغ پرداختی: ${new Intl.NumberFormat('fa-IR').format(orderData.amount_tmn)} تومان
🪙 ارز درخواستی: ${selectedCoin.symbol}
📊 قیمت: ${new Intl.NumberFormat('fa-IR').format(selectedCoin.current_price)} تومان
💎 مقدار تقریبی: ${(orderData.amount_tmn / selectedCoin.current_price).toFixed(8)} ${selectedCoin.symbol}

✔️ مبلغ از موجودی شما کسر شد
⏳ وضعیت: در انتظار تایید ادمین

📌 مراحل بعدی:
1️⃣ ادمین سفارش شما را بررسی می‌کند
2️⃣ پس از تایید، ارز به کیف پول شما واریز می‌شود
3️⃣ اعلان تایید به شما ارسال خواهد شد

⏱️ زمان تقریبی: 1-24 ساعت

💡 می‌توانید وضعیت سفارش را در بخش "سفارشات من" پیگیری کنید

🙏 از صبر و شکیبایی شما سپاسگزاریم`
        : orderType === 'sell'
        ? `╔═══════════════════════════════╗
║        🧾 فاکتور فروش        ║
╚═══════════════════════════════╝

✅ سفارش فروش شما با موفقیت ثبت شد!

📋 شماره سفارش: ${orderId}
📅 تاریخ: ${orderDate}

💎 مقدار: ${orderData.amount_crypto} ${selectedCoin.symbol}
💰 ارزش تقریبی: ${new Intl.NumberFormat('fa-IR').format(orderData.amount_crypto * selectedCoin.current_price)} تومان

⏳ وضعیت: در انتظار تایید ادمین

🙏 از صبر شما سپاسگزاریم`
        : '✅ سفارش شما با موفقیت ثبت شد!';
      
      alert(successMsg);
      
      // Clear form and refresh data
      setBuyAmount('');
      setSellAmount('');
      setTradeAmount('');
      setWalletAddress('');
      setTargetCoin(null);
      
      // Refresh page data to show updated balance and orders
      await fetchData();
      
      console.log('✅ Order completed successfully, data refreshed');
      
    } catch (error) {
      console.error('❌ Error creating order:', error);
      console.error('❌ Error details:', error.response?.data);
      
      let errorMsg = 'خطای نامشخص در ثبت سفارش';
      
      if (error.response) {
        // Server responded with error
        if (error.response.status === 401 || error.response.status === 403) {
          errorMsg = 'لطفا ابتدا وارد حساب کاربری خود شوید';
        } else if (error.response.data?.detail) {
          errorMsg = error.response.data.detail;
        } else {
          errorMsg = `خطا: ${error.response.status}`;
        }
      } else if (error.request) {
        // Request made but no response
        errorMsg = 'خطا در ارتباط با سرور. لطفا اتصال اینترنت خود را بررسی کنید';
      } else {
        errorMsg = error.message || 'خطای نامشخص';
      }
      
      alert('❌ خطا در ثبت سفارش:\n\n' + errorMsg);
    } finally {
      setOrderLoading(false);
      console.log('🏁 handleOrder completed');
    }
  };

  const filteredCoins = coins.filter(coin => 
    coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(2) + 'K';
    return num?.toFixed(2) || '0';
  };

  const formatPrice = (price) => {
    // Price is already in Toman from backend, no conversion needed
    return new Intl.NumberFormat('fa-IR').format(Math.round(price));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-emerald-400">🚀 معاملات</h1>
            <nav className="flex gap-4">
              <a href="/dashboard" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/market" className="text-slate-300 hover:text-white transition-colors">بازار</a>
              <a href="/wallet" className="text-slate-300 hover:text-white transition-colors">کیف پول</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-300">سلام {user?.full_name || user?.email}</span>
            <button
              onClick={onLogout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              خروج
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Coin Selection Panel */}
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <h2 className="text-xl font-bold mb-4">انتخاب ارز</h2>
            
            <input
              type="text"
              placeholder="جستجوی ارز..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg mb-4 text-white placeholder-slate-400"
            />

            <div className="space-y-2 max-h-80 overflow-y-auto">
              {filteredCoins.map(coin => (
                <div
                  key={coin.id}
                  onClick={() => setSelectedCoin(coin)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedCoin?.id === coin.id
                      ? 'bg-emerald-600 border-emerald-500'
                      : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <img src={coin.image} alt={coin.name} className="w-8 h-8" />
                    <div className="flex-1">
                      <div className="font-semibold">{coin.symbol}</div>
                      <div className="text-sm text-slate-400">{coin.name}</div>
                    </div>
                    <div className="text-left">
                      <div className="font-semibold">{formatPrice(coin.current_price)} ت</div>
                      <div className={`text-sm ${
                        coin.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {coin.price_change_24h >= 0 ? '+' : ''}{coin.price_change_24h?.toFixed(2) || 0}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trading Panel */}
          <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <h2 className="text-xl font-bold mb-4">معاملات</h2>
            
            {/* Tabs */}
            <div className="flex border border-slate-700 rounded-lg mb-6">
              {['buy', 'sell', 'trade'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-2 px-4 rounded-lg transition-colors ${
                    activeTab === tab
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-800 text-slate-300 hover:text-white'
                  }`}
                >
                  {tab === 'buy' ? 'خرید' : tab === 'sell' ? 'فروش' : 'تبدیل'}
                </button>
              ))}
            </div>

            {selectedCoin && (
              <div className="mb-6 p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <img src={selectedCoin.image} alt={selectedCoin.name} className="w-10 h-10" />
                  <div>
                    <div className="font-bold text-lg">{selectedCoin.symbol}</div>
                    <div className="text-slate-400">{selectedCoin.name}</div>
                  </div>
                </div>
                <div className="text-2xl font-bold text-emerald-400">
                  {formatPrice(selectedCoin.current_price)} تومان
                </div>
              </div>
            )}

            {/* AI Smart Recommendation Panel */}
            {activeTab === 'buy' && selectedCoin && showAiPanel && (
              <div className="mb-6 bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-bold text-purple-300 flex items-center gap-2">
                    🤖 توصیه هوشمند معاملاتی
                  </h3>
                  <button
                    onClick={() => setShowAiPanel(false)}
                    className="text-slate-400 hover:text-white text-sm"
                  >
                    ✕
                  </button>
                </div>

                {aiLoading && (
                  <div className="flex items-center gap-3 text-slate-300">
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-purple-400"></div>
                    <span>در حال تحلیل...</span>
                  </div>
                )}

                {aiError && (
                  <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 text-red-200 text-sm">
                    {aiError}
                  </div>
                )}

                {!aiLoading && !aiError && aiRecommendation && (
                  <div className="space-y-3">
                    {/* Recommendation Badge */}
                    <div className="flex items-center gap-3">
                      <span className={`px-4 py-2 rounded-lg font-bold text-lg ${
                        aiRecommendation.recommendation === 'خرید' ? 'bg-green-600' :
                        aiRecommendation.recommendation === 'فروش' ? 'bg-red-600' :
                        'bg-yellow-600'
                      }`}>
                        {aiRecommendation.recommendation === 'خرید' && '🟢'}
                        {aiRecommendation.recommendation === 'فروش' && '🔴'}
                        {aiRecommendation.recommendation === 'نگهداری' && '🟡'}
                        {' '}
                        {aiRecommendation.recommendation}
                      </span>
                      <span className="text-sm text-slate-300">
                        اطمینان: <span className="font-semibold">{aiRecommendation.confidence}</span>
                      </span>
                      <span className={`text-sm px-2 py-1 rounded ${
                        aiRecommendation.risk_level === 'کم' ? 'bg-green-900/50 text-green-300' :
                        aiRecommendation.risk_level === 'زیاد' ? 'bg-red-900/50 text-red-300' :
                        'bg-yellow-900/50 text-yellow-300'
                      }`}>
                        ریسک: {aiRecommendation.risk_level}
                      </span>
                    </div>

                    {/* Reasoning */}
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-sm text-slate-200 leading-relaxed">
                        {aiRecommendation.reasoning}
                      </p>
                    </div>

                    {/* Suggested Amount */}
                    {aiRecommendation.suggested_amount > 0 && (
                      <div className="bg-purple-900/30 rounded-lg p-3">
                        <span className="text-sm text-purple-200">
                          💡 مبلغ پیشنهادی: {' '}
                          <span className="font-bold text-lg">
                            {new Intl.NumberFormat('fa-IR').format(aiRecommendation.suggested_amount)} تومان
                          </span>
                        </span>
                      </div>
                    )}

                    {/* Key Points */}
                    {aiRecommendation.key_points && aiRecommendation.key_points.length > 0 && (
                      <div className="space-y-1">
                        {aiRecommendation.key_points.map((point, index) => (
                          <div key={index} className="flex items-start gap-2 text-sm text-slate-300">
                            <span className="text-purple-400">•</span>
                            <span>{point}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="text-xs text-slate-400 pt-2 border-t border-slate-700">
                      ⚠️ این توصیه توسط هوش مصنوعی تولید شده و نباید به تنهایی مبنای تصمیم‌گیری قرار گیرد
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Show AI Panel Button */}
            {activeTab === 'buy' && !showAiPanel && (
              <button
                onClick={() => {
                  setShowAiPanel(true);
                  if (selectedCoin) fetchAiRecommendation(selectedCoin.symbol);
                }}
                className="mb-4 w-full py-2 bg-purple-900/30 hover:bg-purple-900/50 border border-purple-700 rounded-lg text-purple-300 font-medium transition-colors"
              >
                🤖 نمایش توصیه هوشمند
              </button>
            )}

            {/* Buy Form */}
            {activeTab === 'buy' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">مبلغ (تومان)</label>
                  <input
                    type="number"
                    value={buyAmount}
                    onChange={(e) => setBuyAmount(e.target.value)}
                    placeholder="مبلغی که میخواهید خرج کنید"
                    className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg"
                  />
                  {buyAmount && selectedCoin && (
                    <div className="text-sm text-slate-400 mt-1">
                      ≈ {(parseFloat(buyAmount) / selectedCoin.current_price).toFixed(8)} {selectedCoin.symbol}
                    </div>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">
                    آدرس کیف پول {selectedCoin?.symbol} 
                    <span className="text-slate-500 text-xs mr-2">(اختیاری)</span>
                  </label>
                  <input
                    type="text"
                    value={walletAddress}
                    onChange={(e) => setWalletAddress(e.target.value)}
                    placeholder={`آدرس کیف پول ذخیره شده در پروفایل استفاده می‌شود`}
                    className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg text-left"
                    dir="ltr"
                  />
                  <div className="text-xs text-green-500 mt-1">
                    💡 اگر خالی بگذارید، آدرس ذخیره شده در پروفایل استفاده می‌شود
                  </div>
                </div>
                <div className="text-sm text-slate-300 bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                  💰 موجودی کیف پول: <span className="font-bold text-emerald-400">{new Intl.NumberFormat('fa-IR').format(user?.wallet_balance_tmn || 0)} تومان</span>
                </div>
                
                {!buyAmount && (
                  <div className="text-sm text-amber-400 bg-amber-900/20 p-3 rounded-lg border border-amber-700/50 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    لطفاً مبلغ خرید را وارد کنید
                  </div>
                )}
                
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (buyAmount && selectedCoin && !orderLoading) {
                      handleOrder('buy');
                    } else {
                      alert('لطفاً مبلغ را وارد کنید و ارز را انتخاب کنید');
                    }
                  }}
                  disabled={orderLoading || !buyAmount || !selectedCoin}
                  className={`w-full py-4 rounded-lg font-bold text-lg transition-all flex items-center justify-center gap-2 ${
                    orderLoading || !buyAmount || !selectedCoin
                      ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02]'
                  }`}
                >
                  {orderLoading ? (
                    <>
                      <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      در حال ثبت سفارش...
                    </>
                  ) : (
                    <>
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      ثبت سفارش خرید
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Sell Form */}
            {activeTab === 'sell' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">مقدار {selectedCoin?.symbol}</label>
                  <input
                    type="number"
                    step="any"
                    value={sellAmount}
                    onChange={(e) => setSellAmount(e.target.value)}
                    placeholder={`مقدار ${selectedCoin?.symbol} که میخواهید بفروشید`}
                    className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg"
                  />
                  {sellAmount && selectedCoin && (
                    <div className="text-sm text-slate-400 mt-1">
                      ≈ {formatPrice(parseFloat(sellAmount) * selectedCoin.current_price)} تومان
                    </div>
                  )}
                </div>
                <div className="text-sm text-slate-400">
                  موجودی: {(() => {
                    const holding = myHoldings.find(h => h.coin_symbol === selectedCoin?.symbol);
                    return holding ? holding.amount.toFixed(8) : '0';
                  })()} {selectedCoin?.symbol}
                </div>
                <button
                  onClick={() => handleOrder('sell')}
                  disabled={orderLoading}
                  className="w-full py-3 bg-red-600 hover:bg-red-700 disabled:bg-slate-700 rounded-lg font-semibold transition-colors"
                >
                  {orderLoading ? 'در حال ثبت...' : 'ثبت سفارش فروش'}
                </button>
              </div>
            )}

            {/* Trade Form */}
            {activeTab === 'trade' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">مقدار {selectedCoin?.symbol}</label>
                  <input
                    type="number"
                    step="any"
                    value={tradeAmount}
                    onChange={(e) => setTradeAmount(e.target.value)}
                    placeholder={`مقدار ${selectedCoin?.symbol} برای تبدیل`}
                    className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">تبدیل به</label>
                  <select
                    value={targetCoin?.id || ''}
                    onChange={(e) => {
                      const coin = coins.find(c => c.id === e.target.value);
                      setTargetCoin(coin);
                    }}
                    className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg"
                  >
                    <option value="">انتخاب ارز مقصد...</option>
                    {coins.filter(c => c.id !== selectedCoin?.id).map(coin => (
                      <option key={coin.id} value={coin.id}>
                        {coin.symbol} - {coin.name}
                      </option>
                    ))}
                  </select>
                </div>

                {tradeAmount && selectedCoin && targetCoin && (
                  <div className="p-3 bg-slate-800 rounded-lg text-sm">
                    <div>از: {tradeAmount} {selectedCoin.symbol}</div>
                    <div>به: ≈ {(parseFloat(tradeAmount) * selectedCoin.current_price / targetCoin.current_price).toFixed(8)} {targetCoin.symbol}</div>
                  </div>
                )}

                <button
                  onClick={() => handleOrder('trade')}
                  disabled={orderLoading}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 rounded-lg font-semibold transition-colors"
                >
                  {orderLoading ? 'در حال ثبت...' : 'ثبت سفارش تبدیل'}
                </button>
              </div>
            )}
          </div>

          {/* Holdings & Orders Panel */}
          <div className="space-y-6">
            {/* My Holdings */}
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <h3 className="text-lg font-bold mb-4">دارایی‌های من</h3>
              <div className="space-y-3">
                {myHoldings.length === 0 ? (
                  <div className="text-slate-400 text-center py-4">
                    هنوز هیچ ارزی ندارید
                  </div>
                ) : (
                  myHoldings.map(holding => (
                    <div key={holding.id} className="p-3 bg-slate-800 rounded-lg">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-semibold">{holding.coin_symbol}</span>
                        <span className={`text-sm ${
                          holding.pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {holding.pnl_percent >= 0 ? '+' : ''}{holding.pnl_percent?.toFixed(2) || 0}%
                        </span>
                      </div>
                      <div className="text-sm text-slate-400">
                        مقدار: {holding.amount?.toFixed(8) || 0}
                      </div>
                      <div className="text-sm text-slate-400">
                        ارزش: {new Intl.NumberFormat('fa-IR').format(Math.round(holding.total_value_tmn || 0))} ت
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Recent Orders */}
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
              <h3 className="text-lg font-bold mb-4">سفارشات اخیر</h3>
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {myOrders.length === 0 ? (
                  <div className="text-slate-400 text-center py-4">
                    هیچ سفارشی ثبت نشده
                  </div>
                ) : (
                  myOrders.slice(0, 10).map(order => (
                    <div key={order.id} className="p-3 bg-slate-800 rounded-lg">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm">
                          {order.order_type === 'buy' ? '🟢 خرید' : 
                           order.order_type === 'sell' ? '🔴 فروش' : '🔄 تبدیل'} {order.coin_symbol}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          order.status === 'completed' ? 'bg-green-600' :
                          order.status === 'approved' ? 'bg-blue-600' :
                          order.status === 'pending' ? 'bg-yellow-600' : 'bg-red-600'
                        }`}>
                          {order.status === 'completed' ? 'تکمیل' :
                           order.status === 'approved' ? 'تایید' :
                           order.status === 'pending' ? 'در انتظار' : 'رد شده'}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400">
                        {order.order_type === 'buy' ? 
                          `${new Intl.NumberFormat('fa-IR').format(order.amount_tmn)} تومان` :
                          `${order.amount_crypto} ${order.coin_symbol}`}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Trade;