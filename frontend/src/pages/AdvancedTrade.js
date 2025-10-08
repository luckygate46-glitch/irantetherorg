import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  Shield,
  Zap,
  BarChart3,
  DollarSign,
  Calendar,
  Settings,
  AlertTriangle,
  CheckCircle,
  PlayCircle,
  PauseCircle,
  RefreshCw,
  Coins
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdvancedTrade = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('limit_orders');
  const [loading, setLoading] = useState(false);
  const [orderData, setOrderData] = useState({
    coin_symbol: 'BTC',
    coin_id: 'bitcoin',
    amount_crypto: '',
    target_price_tmn: '',
    stop_price_tmn: '',
    order_type: 'limit_buy'
  });
  const [dcaData, setDcaData] = useState({
    coin_symbol: 'BTC',
    coin_id: 'bitcoin',
    amount_tmn_per_purchase: '',
    frequency: 'weekly',
    total_budget_tmn: '',
    auto_rebalance: false
  });
  const [userOrders, setUserOrders] = useState([]);
  const [cryptoPrices, setCryptoPrices] = useState({});
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchCryptoPrices();
    fetchUserOrders();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      const [coinsRes, ordersRes, alertsRes, portfolioRes] = await Promise.all([
        axios.get(`${API}/crypto/prices`),
        axios.get(`${API}/trading/orders/active`),
        axios.get(`${API}/user/price-alerts`),
        axios.get(`${API}/trading/portfolio/detailed`)
      ]);

      if (coinsRes.data.success) {
        const coinsList = Object.entries(coinsRes.data.data).map(([id, data]) => ({
          id,
          symbol: data.symbol?.toUpperCase() || id.toUpperCase(),
          name: data.name || id,
          current_price: data.usd || 0,
          price_change_24h: data.usd_24h_change || 0,
          volume_24h: data.usd_24h_vol || 0
        })).slice(0, 20);
        
        setCoins(coinsList);
        if (!selectedCoin && coinsList.length > 0) {
          setSelectedCoin(coinsList[0]);
        }
      }

      setActiveOrders(ordersRes.data);
      setPriceAlerts(alertsRes.data);
      setPortfolio(portfolioRes.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌ها:', error);
    } finally {
      setLoading(false);
    }
  };

  const placeAdvancedOrder = async () => {
    try {
      if (!selectedCoin || !orderData.amount) {
        toast({
          title: "خطا",
          description: "لطفا اطلاعات سفارش را کامل کنید",
          variant: "destructive"
        });
        return;
      }

      const orderPayload = {
        coin_symbol: selectedCoin.symbol,
        coin_id: selectedCoin.id,
        order_type: orderType,
        order_side: orderSide,
        amount: parseFloat(orderData.amount),
        price: orderType === 'market' ? selectedCoin.current_price : parseFloat(orderData.price),
        stop_price: orderData.stopPrice ? parseFloat(orderData.stopPrice) : null,
        take_profit_price: orderData.takeProfitPrice ? parseFloat(orderData.takeProfitPrice) : null
      };

      await axios.post(`${API}/trading/advanced-order`, orderPayload);
      
      toast({
        title: "سفارش ثبت شد",
        description: `سفارش ${orderType} برای ${selectedCoin.symbol} ثبت شد`,
      });

      // Reset form
      setOrderData({ amount: '', price: '', stopPrice: '', takeProfitPrice: '' });
      fetchData();
      
    } catch (error) {
      console.error('خطا در ثبت سفارش:', error);
      toast({
        title: "خطا در ثبت سفارش",
        description: error.response?.data?.detail || "لطفا دوباره تلاش کنید",
        variant: "destructive"
      });
    }
  };

  const createPriceAlert = async () => {
    try {
      if (!selectedCoin || !orderData.price) {
        toast({
          title: "خطا",
          description: "لطفا ارز و قیمت هدف را انتخاب کنید",
          variant: "destructive"
        });
        return;
      }

      await axios.post(`${API}/user/price-alert`, {
        coin_symbol: selectedCoin.symbol,
        coin_id: selectedCoin.id,
        target_price: parseFloat(orderData.price),
        condition: orderData.price > selectedCoin.current_price ? 'above' : 'below'
      });
      
      toast({
        title: "هشدار قیمت ایجاد شد",
        description: `هشدار برای ${selectedCoin.symbol} در قیمت ${formatPrice(orderData.price)} تومان`,
      });

      fetchData();
      
    } catch (error) {
      console.error('خطا در ایجاد هشدار:', error);
      toast({
        title: "خطا",
        description: "خطا در ایجاد هشدار قیمت",
        variant: "destructive"
      });
    }
  };

  const cancelOrder = async (orderId) => {
    try {
      await axios.delete(`${API}/trading/order/${orderId}`);
      toast({
        title: "سفارش لغو شد",
        description: "سفارش با موفقیت لغو شد",
      });
      fetchData();
    } catch (error) {
      console.error('خطا در لغو سفارش:', error);
      toast({
        title: "خطا",
        description: "خطا در لغو سفارش",
        variant: "destructive"
      });
    }
  };

  const formatPrice = (price) => {
    const tmn_price = price * 50000;
    return new Intl.NumberFormat('fa-IR').format(Math.round(tmn_price));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
  };

  const getOrderTypeIcon = (type) => {
    switch (type) {
      case 'limit': return <Target className="w-4 h-4 text-blue-400" />;
      case 'stop_loss': return <Shield className="w-4 h-4 text-red-400" />;
      case 'take_profit': return <TrendingUp className="w-4 h-4 text-green-400" />;
      default: return <Zap className="w-4 h-4 text-yellow-400" />;
    }
  };

  if (user?.kyc_level < 2) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center" dir="rtl">
        <Card className="bg-slate-900 border-slate-800 max-w-md">
          <CardContent className="p-8 text-center">
            <Shield className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">دسترسی محدود</h2>
            <p className="text-slate-400 mb-4">
              برای استفاده از معاملات پیشرفته باید احراز هویت سطح ۲ را تکمیل کنید
            </p>
            <Button onClick={() => window.location.href = '/kyc'}>
              تکمیل احراز هویت
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

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
            <h1 className="text-2xl font-bold text-emerald-400">⚡ معاملات پیشرفته</h1>
            <nav className="flex gap-4">
              <a href="/dashboard" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/trade" className="text-slate-300 hover:text-white transition-colors">معاملات ساده</a>
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
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Coin Selection & Advanced Order Panel */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Coin Selection */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>انتخاب ارز</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3 max-h-40 overflow-y-auto">
                  {coins.map(coin => (
                    <div
                      key={coin.id}
                      onClick={() => setSelectedCoin(coin)}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedCoin?.id === coin.id
                          ? 'bg-emerald-600 border-emerald-500'
                          : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold">{coin.symbol}</div>
                          <div className="text-xs text-slate-400">{formatPrice(coin.current_price)} ت</div>
                        </div>
                        <div className={`text-sm ${
                          coin.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {coin.price_change_24h >= 0 ? '+' : ''}{coin.price_change_24h?.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Advanced Order Form */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle>سفارش پیشرفته</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                
                {/* Order Type Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">نوع سفارش</label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { value: 'market', label: 'بازاری', icon: <Zap className="w-4 h-4" /> },
                      { value: 'limit', label: 'محدود', icon: <Target className="w-4 h-4" /> },
                      { value: 'stop_loss', label: 'ضرر محدود', icon: <Shield className="w-4 h-4" /> },
                      { value: 'take_profit', label: 'سود محدود', icon: <TrendingUp className="w-4 h-4" /> }
                    ].map(type => (
                      <Button
                        key={type.value}
                        onClick={() => setOrderType(type.value)}
                        variant={orderType === type.value ? 'default' : 'outline'}
                        className="flex items-center gap-2"
                      >
                        {type.icon}
                        {type.label}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Buy/Sell Toggle */}
                <div>
                  <label className="block text-sm font-medium mb-2">نوع معامله</label>
                  <div className="flex border border-slate-700 rounded-lg">
                    <Button
                      onClick={() => setOrderSide('buy')}
                      className={`flex-1 rounded-r-lg rounded-l-none ${
                        orderSide === 'buy' ? 'bg-green-600' : 'bg-slate-800'
                      }`}
                    >
                      خرید
                    </Button>
                    <Button
                      onClick={() => setOrderSide('sell')}
                      className={`flex-1 rounded-l-lg rounded-r-none ${
                        orderSide === 'sell' ? 'bg-red-600' : 'bg-slate-800'
                      }`}
                    >
                      فروش
                    </Button>
                  </div>
                </div>

                {selectedCoin && (
                  <div className="p-3 bg-slate-800 rounded-lg">
                    <div className="text-sm text-slate-400 mb-1">ارز انتخابی:</div>
                    <div className="font-bold text-lg">{selectedCoin.symbol}</div>
                    <div className="text-emerald-400">{formatPrice(selectedCoin.current_price)} تومان</div>
                  </div>
                )}

                {/* Amount */}
                <div>
                  <label className="block text-sm font-medium mb-2">مقدار</label>
                  <Input
                    type="number"
                    placeholder="مقدار برای معامله"
                    value={orderData.amount}
                    onChange={(e) => setOrderData({...orderData, amount: e.target.value})}
                  />
                </div>

                {/* Price (for limit orders) */}
                {orderType !== 'market' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">قیمت هدف (تومان)</label>
                    <Input
                      type="number"
                      placeholder="قیمت مورد نظر"
                      value={orderData.price}
                      onChange={(e) => setOrderData({...orderData, price: e.target.value})}
                    />
                  </div>
                )}

                {/* Stop Loss */}
                {(orderType === 'stop_loss' || orderType === 'take_profit') && (
                  <div>
                    <label className="block text-sm font-medium mb-2">قیمت توقف (تومان)</label>
                    <Input
                      type="number"
                      placeholder="قیمت توقف ضرر"
                      value={orderData.stopPrice}
                      onChange={(e) => setOrderData({...orderData, stopPrice: e.target.value})}
                    />
                  </div>
                )}

                <div className="flex gap-2">
                  <Button onClick={placeAdvancedOrder} className="flex-1">
                    ثبت سفارش {orderSide === 'buy' ? 'خرید' : 'فروش'}
                  </Button>
                  <Button onClick={createPriceAlert} variant="outline">
                    <Bell className="w-4 h-4 mr-2" />
                    هشدار قیمت
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Portfolio Summary */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  خلاصه پورتفولیو
                </CardTitle>
              </CardHeader>
              <CardContent>
                {portfolio.length === 0 ? (
                  <p className="text-slate-400 text-center py-4">هیچ دارایی‌ای در پورتفولیو نیست</p>
                ) : (
                  <div className="space-y-3">
                    {portfolio.map((asset, index) => (
                      <div key={index} className="flex justify-between items-center p-3 bg-slate-800 rounded-lg">
                        <div>
                          <div className="font-semibold">{asset.symbol}</div>
                          <div className="text-sm text-slate-400">{asset.amount} {asset.symbol}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">{formatCurrency(asset.value_tmn)} ت</div>
                          <div className={`text-sm ${asset.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {asset.pnl >= 0 ? '+' : ''}{asset.pnl?.toFixed(2)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Active Orders */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-yellow-400" />
                  سفارشات فعال
                </CardTitle>
              </CardHeader>
              <CardContent>
                {activeOrders.length === 0 ? (
                  <p className="text-slate-400 text-center py-4">سفارش فعالی وجود ندارد</p>
                ) : (
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {activeOrders.map((order) => (
                      <div key={order.id} className="p-3 bg-slate-800 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <div className="flex items-center gap-2">
                            {getOrderTypeIcon(order.order_type)}
                            <span className="font-semibold">{order.coin_symbol}</span>
                            <Badge className={`text-xs ${order.order_side === 'buy' ? 'bg-green-600' : 'bg-red-600'}`}>
                              {order.order_side === 'buy' ? 'خرید' : 'فروش'}
                            </Badge>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => cancelOrder(order.id)}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                        <div className="text-sm text-slate-400">
                          مقدار: {order.amount} | قیمت: {formatPrice(order.price)} ت
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Price Alerts */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-orange-400" />
                  هشدارهای قیمت
                </CardTitle>
              </CardHeader>
              <CardContent>
                {priceAlerts.length === 0 ? (
                  <p className="text-slate-400 text-center py-4">هشدار قیمتی تنظیم نشده</p>
                ) : (
                  <div className="space-y-3">
                    {priceAlerts.map((alert) => (
                      <div key={alert.id} className="p-3 bg-slate-800 rounded-lg">
                        <div className="flex justify-between items-center">
                          <div>
                            <div className="font-semibold">{alert.coin_symbol}</div>
                            <div className="text-sm text-slate-400">
                              {alert.condition === 'above' ? 'بالای' : 'زیر'} {formatPrice(alert.target_price)} ت
                            </div>
                          </div>
                          <Badge className={alert.triggered ? 'bg-green-600' : 'bg-yellow-600'}>
                            {alert.triggered ? 'فعال شده' : 'در انتظار'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedTrade;