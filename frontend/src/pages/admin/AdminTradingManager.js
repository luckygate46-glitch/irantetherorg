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
  BarChart3, 
  Users, 
  DollarSign, 
  Clock,
  Activity,
  Zap,
  Target,
  PieChart,
  LineChart,
  ArrowUpRight,
  ArrowDownRight,
  Pause,
  Play,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Settings,
  Filter,
  Search,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminTradingManager = ({ user, onLogout }) => {
  const [tradingStats, setTradingStats] = useState(null);
  const [liveOrders, setLiveOrders] = useState([]);
  const [tradingPairs, setTradingPairs] = useState([]);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchTradingData();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchTradingData, 10000);
    return () => clearInterval(interval);
  }, [user, navigate, selectedTimeframe]);

  const fetchTradingData = async () => {
    try {
      const [statsRes, ordersRes, pairsRes, marketRes] = await Promise.all([
        axios.get(`${API}/admin/trading/stats?timeframe=${selectedTimeframe}`),
        axios.get(`${API}/admin/trading/live-orders`),
        axios.get(`${API}/admin/trading/pairs`),
        axios.get(`${API}/admin/trading/market-data`)
      ]);

      setTradingStats(statsRes.data);
      setLiveOrders(ordersRes.data);
      setTradingPairs(pairsRes.data);
      setMarketData(marketRes.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌های معاملاتی:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات معاملاتی',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOrderAction = async (orderId, action) => {
    try {
      await axios.post(`${API}/admin/trading/order-action`, {
        order_id: orderId,
        action: action
      });
      
      toast({
        title: 'موفق',
        description: `سفارش با موفقیت ${action === 'approve' ? 'تایید' : action === 'reject' ? 'رد' : 'لغو'} شد`,
      });
      
      fetchTradingData();
    } catch (error) {
      console.error('خطا در عملیات سفارش:', error);
      toast({
        title: 'خطا',
        description: error.response?.data?.detail || 'خطا در انجام عملیات',
        variant: 'destructive'
      });
    }
  };

  const toggleTradingPair = async (pairId, active) => {
    try {
      await axios.put(`${API}/admin/trading/pair/${pairId}/toggle`, {
        active: !active
      });
      
      toast({
        title: 'موفق',
        description: `جفت ارز ${active ? 'غیرفعال' : 'فعال'} شد`,
      });
      
      fetchTradingData();
    } catch (error) {
      console.error('خطا در تغییر وضعیت جفت ارز:', error);
      toast({
        title: 'خطا',
        description: 'خطا در تغییر وضعیت جفت ارز',
        variant: 'destructive'
      });
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-600';
      case 'pending': return 'bg-yellow-600';
      case 'cancelled': return 'bg-red-600';
      case 'processing': return 'bg-blue-600';
      default: return 'bg-slate-600';
    }
  };

  const getOrderTypeIcon = (type) => {
    switch (type) {
      case 'buy': return <ArrowUpRight className="w-4 h-4 text-green-400" />;
      case 'sell': return <ArrowDownRight className="w-4 h-4 text-red-400" />;
      case 'trade': return <TrendingUp className="w-4 h-4 text-blue-400" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const filteredOrders = liveOrders.filter(order => {
    const matchesSearch = order.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.coin_symbol?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || order.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-200">بارگذاری مدیریت معاملات...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-purple-400" />
              <h1 className="text-2xl font-bold text-emerald-400">مدیریت معاملات و بروکریج</h1>
            </div>
            <nav className="flex gap-4">
              <a href="/admin" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/admin/users" className="text-slate-300 hover:text-white transition-colors">کاربران</a>
              <a href="/admin/kyc" className="text-slate-300 hover:text-white transition-colors">احراز هویت</a>
              <a href="/admin/prices" className="text-slate-300 hover:text-white transition-colors">قیمت‌ها</a>
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
        {/* Trading Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-400" />
                حجم معاملات ({selectedTimeframe})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-400">
                {formatCurrency(tradingStats?.total_volume || 0)} ت
              </div>
              <p className="text-xs text-slate-200">
                {tradingStats?.total_trades || 0} معامله انجام شده
              </p>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="w-3 h-3 text-green-400" />
                <span className="text-xs text-green-400">
                  +{tradingStats?.volume_change || 0}% نسبت به قبل
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" />
                معامله‌گران فعال
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">
                {tradingStats?.active_traders || 0}
              </div>
              <p className="text-xs text-slate-200">
                از {tradingStats?.total_users || 0} کل کاربران
              </p>
              <div className="text-xs text-slate-200 mt-2">
                میانگین معامله: {formatCurrency(tradingStats?.avg_trade_size || 0)} ت
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-yellow-400" />
                درآمد کارمزد
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-400">
                {formatCurrency(tradingStats?.fee_revenue || 0)} ت
              </div>
              <p className="text-xs text-slate-200">
                نرخ میانگین: %{tradingStats?.avg_fee_rate || 0}
              </p>
              <div className="text-xs text-slate-200 mt-2">
                بیشترین کارمزد: {formatCurrency(tradingStats?.highest_fee || 0)} ت
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="w-4 h-4 text-purple-400" />
                سفارشات در انتظار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-400">
                {liveOrders.filter(o => o.status === 'pending').length}
              </div>
              <p className="text-xs text-slate-200">
                نیاز به بررسی ادمین
              </p>
              <div className="text-xs text-slate-200 mt-2">
                میانگین انتظار: {tradingStats?.avg_processing_time || 0} دقیقه
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Timeframe and Controls */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-200">بازه زمانی:</span>
            {['1h', '24h', '7d', '30d'].map(tf => (
              <Button
                key={tf}
                onClick={() => setSelectedTimeframe(tf)}
                variant={selectedTimeframe === tf ? 'default' : 'outline'}
                size="sm"
              >
                {tf}
              </Button>
            ))}
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-slate-200" />
              <Input
                placeholder="جستجوی کاربر یا ارز..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-48"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-200" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
              >
                <option value="all">همه وضعیت‌ها</option>
                <option value="pending">در انتظار</option>
                <option value="processing">در حال پردازش</option>
                <option value="completed">تکمیل شده</option>
                <option value="cancelled">لغو شده</option>
              </select>
            </div>
            
            <Button onClick={fetchTradingData} variant="outline" size="sm">
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Live Orders */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-emerald-400" />
                    سفارشات زنده
                  </div>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-400">
                    {filteredOrders.length} سفارش
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {filteredOrders.length === 0 ? (
                    <div className="text-center py-8">
                      <Activity className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                      <p className="text-slate-200">سفارش جدیدی وجود ندارد</p>
                    </div>
                  ) : (
                    filteredOrders.map((order) => (
                      <div key={order.id} className="p-4 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            {getOrderTypeIcon(order.order_type)}
                            <div>
                              <div className="font-semibold text-sm">
                                {order.order_type === 'buy' ? 'خرید' : 
                                 order.order_type === 'sell' ? 'فروش' : 'تبدیل'} {order.coin_symbol}
                              </div>
                              <div className="text-xs text-slate-200">{order.user_email}</div>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <div className="text-sm font-semibold">
                              {order.order_type === 'buy' ? 
                                `${formatCurrency(order.amount_tmn)} ت` :
                                `${order.amount_crypto} ${order.coin_symbol}`
                              }
                            </div>
                            <Badge className={`text-xs ${getStatusColor(order.status)}`}>
                              {order.status === 'pending' ? 'در انتظار' :
                               order.status === 'processing' ? 'در حال پردازش' :
                               order.status === 'completed' ? 'تکمیل' : 'لغو شده'}
                            </Badge>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-xs text-slate-200">
                          <span>{new Date(order.created_at).toLocaleString('fa-IR')}</span>
                          <div className="flex items-center gap-2">
                            {order.status === 'pending' && (
                              <>
                                <Button 
                                  size="sm" 
                                  className="bg-green-600 hover:bg-green-700"
                                  onClick={() => handleOrderAction(order.id, 'approve')}
                                >
                                  <CheckCircle className="w-3 h-3" />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  className="text-red-400 hover:text-red-300"
                                  onClick={() => handleOrderAction(order.id, 'reject')}
                                >
                                  <Trash2 className="w-3 h-3" />
                                </Button>
                              </>
                            )}
                            <Button size="sm" variant="outline">
                              <Eye className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                        
                        {order.target_coin_symbol && (
                          <div className="mt-2 text-xs text-slate-200 bg-slate-800 p-2 rounded">
                            تبدیل به: {order.target_coin_symbol}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Trading Pairs Management */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-orange-400" />
                جفت‌های معاملاتی
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {tradingPairs.map((pair) => (
                  <div key={pair.id} className="p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-semibold text-sm">{pair.symbol}</div>
                      <Badge 
                        className={`cursor-pointer text-xs ${pair.active ? 'bg-green-600' : 'bg-slate-600'}`}
                        onClick={() => toggleTradingPair(pair.id, pair.active)}
                      >
                        {pair.active ? 'فعال' : 'غیرفعال'}
                      </Badge>
                    </div>
                    
                    <div className="text-xs text-slate-200 space-y-1">
                      <div className="flex justify-between">
                        <span>حجم 24س:</span>
                        <span>{formatCurrency(pair.volume_24h || 0)} ت</span>
                      </div>
                      <div className="flex justify-between">
                        <span>آخرین قیمت:</span>
                        <span>{formatCurrency(pair.last_price || 0)} ت</span>
                      </div>
                      <div className="flex justify-between">
                        <span>تغییر 24س:</span>
                        <span className={pair.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}>
                          {pair.change_24h >= 0 ? '+' : ''}{pair.change_24h?.toFixed(2) || 0}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1 mt-2">
                      <Button size="sm" variant="outline" className="text-xs">
                        <Settings className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-xs">
                        <BarChart3 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              
              <Button className="w-full mt-4" variant="outline">
                <Target className="w-4 h-4 mr-2" />
                اضافه کردن جفت جدید
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Market Data Summary */}
        {marketData && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="w-5 h-5 text-blue-400" />
                خلاصه وضعیت بازار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-emerald-400">
                    {marketData.market_cap ? formatCurrency(marketData.market_cap) : 'N/A'}
                  </div>
                  <div className="text-sm text-slate-200">ارزش کل بازار</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">
                    {marketData.total_volume_24h ? formatCurrency(marketData.total_volume_24h) : 'N/A'}
                  </div>
                  <div className="text-sm text-slate-200">حجم معاملات 24س</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-400">
                    {marketData.active_cryptocurrencies || 0}
                  </div>
                  <div className="text-sm text-slate-200">ارزهای فعال</div>
                </div>
                
                <div className="text-center">
                  <div className={`text-2xl font-bold ${marketData.market_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {marketData.market_change >= 0 ? '+' : ''}{marketData.market_change?.toFixed(2) || 0}%
                  </div>
                  <div className="text-sm text-slate-200">تغییر کل بازار</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AdminTradingManager;