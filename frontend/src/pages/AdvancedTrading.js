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

const AdvancedTrading = ({ user, onLogout }) => {
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

  const fetchCryptoPrices = async () => {
    try {
      const response = await axios.get(`${API}/crypto/prices`);
      if (response.data.success) {
        setCryptoPrices(response.data.data);
      }
    } catch (error) {
      console.error('خطا در دریافت قیمت‌های ارز:', error);
    }
  };

  const fetchUserOrders = async () => {
    try {
      // This would fetch user's existing orders
      // Mock data for now
      setUserOrders([]);
    } catch (error) {
      console.error('خطا در دریافت سفارشات:', error);
    }
  };

  const handleLimitOrder = async (e) => {
    e.preventDefault();
    if (user?.kyc_level < 2) {
      toast({
        title: 'احراز هویت ناقص',
        description: 'برای معاملات پیشرفته به احراز هویت کامل نیاز دارید',
        variant: 'destructive'
      });
      navigate('/kyc');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/trading/limit-order`, orderData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      toast({
        title: 'سفارش محدود ایجاد شد',
        description: response.data.message,
      });

      // Reset form
      setOrderData({
        ...orderData,
        amount_crypto: '',
        target_price_tmn: ''
      });

      fetchUserOrders();
    } catch (error) {
      toast({
        title: 'خطا در ایجاد سفارش',
        description: error.response?.data?.detail || 'خطا در ایجاد سفارش محدود',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStopLoss = async (e) => {
    e.preventDefault();
    if (user?.kyc_level < 2) {
      toast({
        title: 'احراز هویت ناقص',
        description: 'برای معاملات پیشرفته به احراز هویت کامل نیاز دارید',
        variant: 'destructive'
      });
      navigate('/kyc');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/trading/stop-loss`, orderData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      toast({
        title: 'حد ضرر تنظیم شد',
        description: response.data.message,
      });

      // Reset form
      setOrderData({
        ...orderData,
        amount_crypto: '',
        stop_price_tmn: ''
      });

      fetchUserOrders();
    } catch (error) {
      toast({
        title: 'خطا در تنظیم حد ضرر',
        description: error.response?.data?.detail || 'خطا در ایجاد سفارش حد ضرر',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDCAStrategy = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/trading/dca-strategy`, dcaData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      toast({
        title: 'استراتژی DCA فعال شد',
        description: response.data.message,
      });

      // Reset form
      setDcaData({
        ...dcaData,
        amount_tmn_per_purchase: '',
        total_budget_tmn: ''
      });

    } catch (error) {
      toast({
        title: 'خطا در ایجاد استراتژی',
        description: error.response?.data?.detail || 'خطا در ایجاد استراتژی DCA',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
  };

  const getCryptoPrice = (symbol) => {
    const crypto = Object.values(cryptoPrices).find(c => c.symbol?.toUpperCase() === symbol);
    return crypto?.usd_price_tmn || 0;
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <Zap className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">معاملات پیشرفته</h1>
              {user?.kyc_level < 2 && (
                <Badge className="bg-yellow-600 text-white">
                  نیاز به احراز هویت کامل
                </Badge>
              )}
            </div>
            <nav className="flex gap-4">
              <Button 
                onClick={() => navigate('/dashboard')}
                variant="ghost"
                className="text-slate-300 hover:text-white"
              >
                داشبورد
              </Button>
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
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 bg-slate-800 p-1 rounded-lg">
          {[
            { id: 'limit_orders', label: 'سفارشات محدود', icon: <Target className="w-4 h-4" /> },
            { id: 'stop_loss', label: 'حد ضرر', icon: <Shield className="w-4 h-4" /> },
            { id: 'dca_strategy', label: 'استراتژی DCA', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'portfolio_rebalance', label: 'تعادل پرتفوی', icon: <RefreshCw className="w-4 h-4" /> }
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "ghost"}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2"
            >
              {tab.icon}
              {tab.label}
            </Button>
          ))}
        </div>

        {/* KYC Warning */}
        {user?.kyc_level < 2 && (
          <Card className="bg-yellow-900/20 border-yellow-800 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-yellow-400" />
                <div>
                  <h3 className="font-semibold text-yellow-400">احراز هویت کامل مورد نیاز</h3>
                  <p className="text-sm text-yellow-300">
                    برای استفاده از معاملات پیشرفته، لطفاً احراز هویت سطح ۲ را تکمیل کنید.
                  </p>
                  <Button 
                    onClick={() => navigate('/kyc')} 
                    size="sm" 
                    className="mt-2 bg-yellow-600 hover:bg-yellow-700"
                  >
                    تکمیل احراز هویت
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Trading Panel */}
          <div className="lg:col-span-2">
            {/* Limit Orders */}
            {activeTab === 'limit_orders' && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-400" />
                    سفارشات محدود
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleLimitOrder} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">نوع سفارش</label>
                        <select
                          value={orderData.order_type}
                          onChange={(e) => setOrderData({...orderData, order_type: e.target.value})}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2"
                        >
                          <option value="limit_buy">خرید محدود</option>
                          <option value="limit_sell">فروش محدود</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">ارز دیجیتال</label>
                        <select
                          value={orderData.coin_symbol}
                          onChange={(e) => setOrderData({...orderData, coin_symbol: e.target.value})}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2"
                        >
                          <option value="BTC">Bitcoin (BTC)</option>
                          <option value="ETH">Ethereum (ETH)</option>
                          <option value="BNB">Binance Coin (BNB)</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">مقدار</label>
                        <Input
                          type="number"
                          step="0.00000001"
                          value={orderData.amount_crypto}
                          onChange={(e) => setOrderData({...orderData, amount_crypto: e.target.value})}
                          placeholder="مقدار ارز دیجیتال"
                          className="bg-slate-800 border-slate-700"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">قیمت هدف (تومان)</label>
                        <Input
                          type="number"
                          value={orderData.target_price_tmn}
                          onChange={(e) => setOrderData({...orderData, target_price_tmn: e.target.value})}
                          placeholder="قیمت مورد نظر"
                          className="bg-slate-800 border-slate-700"
                          required
                        />
                      </div>
                    </div>

                    <div className="bg-slate-800/50 p-3 rounded-lg">
                      <div className="text-sm text-slate-400">قیمت فعلی {orderData.coin_symbol}:</div>
                      <div className="text-lg font-bold text-emerald-400">
                        {formatCurrency(getCryptoPrice(orderData.coin_symbol))} تومان
                      </div>
                    </div>

                    <Button 
                      type="submit" 
                      disabled={loading || user?.kyc_level < 2}
                      className="w-full bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? 'در حال ایجاد...' : 'ایجاد سفارش محدود'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Stop Loss */}
            {activeTab === 'stop_loss' && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-red-400" />
                    حد ضرر
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleStopLoss} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">ارز دیجیتال</label>
                        <select
                          value={orderData.coin_symbol}
                          onChange={(e) => setOrderData({...orderData, coin_symbol: e.target.value})}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2"
                        >
                          <option value="BTC">Bitcoin (BTC)</option>
                          <option value="ETH">Ethereum (ETH)</option>
                          <option value="BNB">Binance Coin (BNB)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">مقدار</label>
                        <Input
                          type="number"
                          step="0.00000001"
                          value={orderData.amount_crypto}
                          onChange={(e) => setOrderData({...orderData, amount_crypto: e.target.value})}
                          placeholder="مقدار ارز دیجیتال"
                          className="bg-slate-800 border-slate-700"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">قیمت حد ضرر (تومان)</label>
                      <Input
                        type="number"
                        value={orderData.stop_price_tmn}
                        onChange={(e) => setOrderData({...orderData, stop_price_tmn: e.target.value})}
                        placeholder="قیمت فعال‌سازی حد ضرر"
                        className="bg-slate-800 border-slate-700"
                        required
                      />
                    </div>

                    <div className="bg-slate-800/50 p-3 rounded-lg">
                      <div className="text-sm text-slate-400">قیمت فعلی {orderData.coin_symbol}:</div>
                      <div className="text-lg font-bold text-emerald-400">
                        {formatCurrency(getCryptoPrice(orderData.coin_symbol))} تومان
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        حد ضرر زمانی فعال می‌شود که قیمت به سطح تعیین شده برسد
                      </div>
                    </div>

                    <Button 
                      type="submit" 
                      disabled={loading || user?.kyc_level < 2}
                      className="w-full bg-red-600 hover:bg-red-700"
                    >
                      {loading ? 'در حال تنظیم...' : 'تنظیم حد ضرر'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* DCA Strategy */}
            {activeTab === 'dca_strategy' && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-purple-400" />
                    استراتژی DCA (میانگین‌گیری هزینه)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleDCAStrategy} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">ارز دیجیتال</label>
                        <select
                          value={dcaData.coin_symbol}
                          onChange={(e) => setDcaData({...dcaData, coin_symbol: e.target.value})}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2"
                        >
                          <option value="BTC">Bitcoin (BTC)</option>
                          <option value="ETH">Ethereum (ETH)</option>
                          <option value="BNB">Binance Coin (BNB)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">دوره خرید</label>
                        <select
                          value={dcaData.frequency}
                          onChange={(e) => setDcaData({...dcaData, frequency: e.target.value})}
                          className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2"
                        >
                          <option value="daily">روزانه</option>
                          <option value="weekly">هفتگی</option>
                          <option value="monthly">ماهانه</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">مبلغ هر خرید (تومان)</label>
                        <Input
                          type="number"
                          value={dcaData.amount_tmn_per_purchase}
                          onChange={(e) => setDcaData({...dcaData, amount_tmn_per_purchase: e.target.value})}
                          placeholder="مبلغ هر خرید"
                          className="bg-slate-800 border-slate-700"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">کل بودجه (تومان)</label>
                        <Input
                          type="number"
                          value={dcaData.total_budget_tmn}
                          onChange={(e) => setDcaData({...dcaData, total_budget_tmn: e.target.value})}
                          placeholder="کل بودجه برای استراتژی"
                          className="bg-slate-800 border-slate-700"
                          required
                        />
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="auto_rebalance"
                        checked={dcaData.auto_rebalance}
                        onChange={(e) => setDcaData({...dcaData, auto_rebalance: e.target.checked})}
                        className="w-4 h-4"
                      />
                      <label htmlFor="auto_rebalance" className="text-sm">
                        تعادل خودکار پرتفوی
                      </label>
                    </div>

                    {dcaData.amount_tmn_per_purchase && dcaData.total_budget_tmn && (
                      <div className="bg-slate-800/50 p-3 rounded-lg">
                        <div className="text-sm text-slate-400">خلاصه استراتژی:</div>
                        <div className="text-sm">
                          <span className="text-purple-400">
                            {Math.floor(dcaData.total_budget_tmn / dcaData.amount_tmn_per_purchase)} خرید
                          </span>
                          {' '}با مبلغ{' '}
                          <span className="text-emerald-400">
                            {formatCurrency(dcaData.amount_tmn_per_purchase)} تومان
                          </span>
                          {' '}به صورت {dcaData.frequency === 'daily' ? 'روزانه' : 
                                         dcaData.frequency === 'weekly' ? 'هفتگی' : 'ماهانه'}
                        </div>
                      </div>
                    )}

                    <Button 
                      type="submit" 
                      disabled={loading}
                      className="w-full bg-purple-600 hover:bg-purple-700"
                    >
                      {loading ? 'در حال فعال‌سازی...' : 'فعال‌سازی استراتژی DCA'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Portfolio Rebalancing */}
            {activeTab === 'portfolio_rebalance' && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <RefreshCw className="w-5 h-5 text-green-400" />
                    تعادل‌بخشی پرتفوی
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <Coins className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">تعادل‌بخشی هوشمند</h3>
                    <p className="text-slate-400 mb-4">
                      با استفاده از هوش مصنوعی، پرتفوی خود را به طور خودکار متعادل کنید
                    </p>
                    <Button 
                      onClick={() => navigate('/ai/portfolio-analysis')}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      مشاهده تحلیل پرتفوی
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Trading Guide */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  راهنمای معاملات پیشرفته
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div>
                    <h4 className="font-semibold text-blue-400 mb-1">سفارشات محدود</h4>
                    <p className="text-slate-400">خرید یا فروش در قیمت دلخواه شما</p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-red-400 mb-1">حد ضرر</h4>
                    <p className="text-slate-400">محافظت از سرمایه در برابر ضررهای بزرگ</p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-purple-400 mb-1">استراتژی DCA</h4>
                    <p className="text-slate-400">خرید تدریجی برای کاهش ریسک</p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-green-400 mb-1">تعادل پرتفوی</h4>
                    <p className="text-slate-400">بهینه‌سازی خودکار تخصیص داراییها</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Active Orders */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-400" />
                  سفارشات فعال
                </CardTitle>
              </CardHeader>
              <CardContent>
                {userOrders.length > 0 ? (
                  <div className="space-y-3">
                    {userOrders.map((order) => (
                      <div key={order.id} className="p-3 bg-slate-800/50 rounded border">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-medium">{order.coin_symbol}</span>
                          <Badge className="text-xs">
                            {order.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-slate-400">
                          {order.order_type} • {order.amount} • {formatCurrency(order.price)} ت
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <Clock className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-slate-400 text-sm">هیچ سفارش فعالی ندارید</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Market Status */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-emerald-400" />
                  وضعیت بازار
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">وضعیت معاملات</span>
                    <Badge className="bg-green-600 text-white text-xs">فعال</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">نوسانات بازار</span>
                    <span className="text-yellow-400">متوسط</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">حجم معاملات</span>
                    <span className="text-blue-400">بالا</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedTrading;