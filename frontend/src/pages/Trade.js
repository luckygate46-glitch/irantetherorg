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
    }
  }, [asset, coins]);

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
    if (!selectedCoin) {
      alert('لطفا یک ارز انتخاب کنید');
      return;
    }

    // Check for wallet address before placing buy order
    if (orderType === 'buy') {
      const { hasWallet } = await checkWalletAddress(selectedCoin.symbol);
      
      if (!hasWallet) {
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
      }
    }

    setOrderLoading(true);
    try {
      const orderData = {
        order_type: orderType,
        coin_symbol: selectedCoin.symbol,
        coin_id: selectedCoin.id
      };

      if (orderType === 'buy') {
        const amount = parseFloat(buyAmount);
        if (!amount || amount <= 0) {
          alert('لطفا مبلغ معتبری وارد کنید');
          return;
        }
        
        // Check if user has sufficient balance
        const userBalance = user?.wallet_balance_tmn || 0;
        if (amount > userBalance) {
          alert(`موجودی شما کافی نیست. موجودی فعلی: ${new Intl.NumberFormat('fa-IR').format(userBalance)} تومان`);
          return;
        }
        
        orderData.amount_tmn = amount;
      } else if (orderType === 'sell') {
        const amount = parseFloat(sellAmount);
        if (!amount || amount <= 0) {
          alert('لطفا مقدار معتبری وارد کنید');
          return;
        }
        orderData.amount_crypto = amount;
      } else if (orderType === 'trade') {
        const amount = parseFloat(tradeAmount);
        if (!amount || amount <= 0 || !targetCoin) {
          alert('لطفا مقدار معتبری وارد کنید و ارز مقصد را انتخاب کنید');
          return;
        }
        orderData.amount_crypto = amount;
        orderData.target_coin_symbol = targetCoin.symbol;
        orderData.target_coin_id = targetCoin.id;
      }

      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.post(`${API}/trading/order`, orderData, config);
      
      alert('سفارش شما ثبت شد و در انتظار تایید ادمین است');
      
      // Clear form and refresh data
      setBuyAmount('');
      setSellAmount('');
      setTradeAmount('');
      setTargetCoin(null);
      fetchData();
      
    } catch (error) {
      console.error('خطا در ثبت سفارش:', error);
      alert(error.response?.data?.detail || 'خطا در ثبت سفارش');
    } finally {
      setOrderLoading(false);
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
                <div className="text-sm text-slate-400">
                  موجودی کیف پول: {new Intl.NumberFormat('fa-IR').format(user?.wallet_balance_tmn || 0)} تومان
                </div>
                <button
                  onClick={() => handleOrder('buy')}
                  disabled={orderLoading}
                  className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-slate-700 rounded-lg font-semibold transition-colors"
                >
                  {orderLoading ? 'در حال ثبت...' : 'ثبت سفارش خرید'}
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