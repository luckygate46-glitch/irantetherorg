import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Edit, 
  Save, 
  X, 
  Plus,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Target,
  Zap,
  Settings,
  Globe,
  Activity
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPriceManager = ({ user, onLogout }) => {
  const [cryptos, setCryptos] = useState([]);
  const [editingCrypto, setEditingCrypto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [newCrypto, setNewCrypto] = useState({ symbol: '', name: '', price: '', change_24h: '' });
  const [showAddForm, setShowAddForm] = useState(false);
  const [priceHistory, setPriceHistory] = useState({});
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [marketStatus, setMarketStatus] = useState(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchCryptoData();
    fetchMarketStatus();
    
    // Auto-update every 30 seconds if enabled
    let interval;
    if (autoUpdate) {
      interval = setInterval(fetchCryptoData, 30000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [user, navigate, autoUpdate]);

  const fetchCryptoData = async () => {
    try {
      const response = await axios.get(`${API}/admin/crypto/prices`);
      setCryptos(response.data.cryptos || []);
      setPriceHistory(response.data.price_history || {});
    } catch (error) {
      console.error('خطا در بارگذاری قیمت‌ها:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری قیمت‌های ارزهای دیجیتال',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketStatus = async () => {
    try {
      const response = await axios.get(`${API}/admin/market/status`);
      setMarketStatus(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری وضعیت بازار:', error);
    }
  };

  const updateCryptoPrice = async (cryptoId, newPrice, spread = 0) => {
    try {
      setUpdating(true);
      await axios.put(`${API}/admin/crypto/price/${cryptoId}`, {
        price: parseFloat(newPrice),
        spread: parseFloat(spread),
        updated_by: user.id
      });
      
      toast({
        title: 'موفق',
        description: 'قیمت با موفقیت به‌روزرسانی شد',
      });
      
      fetchCryptoData();
      setEditingCrypto(null);
    } catch (error) {
      console.error('خطا در به‌روزرسانی قیمت:', error);
      toast({
        title: 'خطا',
        description: error.response?.data?.detail || 'خطا در به‌روزرسانی قیمت',
        variant: 'destructive'
      });
    } finally {
      setUpdating(false);
    }
  };

  const addNewCrypto = async () => {
    try {
      setUpdating(true);
      await axios.post(`${API}/admin/crypto/add`, {
        symbol: newCrypto.symbol.toUpperCase(),
        name: newCrypto.name,
        price: parseFloat(newCrypto.price),
        change_24h: parseFloat(newCrypto.change_24h) || 0
      });
      
      toast({
        title: 'موفق',
        description: 'ارز دیجیتال جدید اضافه شد',
      });
      
      setNewCrypto({ symbol: '', name: '', price: '', change_24h: '' });
      setShowAddForm(false);
      fetchCryptoData();
    } catch (error) {
      console.error('خطا در اضافه کردن ارز:', error);
      toast({
        title: 'خطا',
        description: error.response?.data?.detail || 'خطا در اضافه کردن ارز دیجیتال',
        variant: 'destructive'
      });
    } finally {
      setUpdating(false);
    }
  };

  const syncWithExternalAPI = async () => {
    try {
      setUpdating(true);
      await axios.post(`${API}/admin/crypto/sync`);
      
      toast({
        title: 'موفق',
        description: 'قیمت‌ها از منابع خارجی همگام‌سازی شد',
      });
      
      fetchCryptoData();
    } catch (error) {
      console.error('خطا در همگام‌سازی:', error);
      toast({
        title: 'خطا',
        description: 'خطا در همگام‌سازی با منابع خارجی',
        variant: 'destructive'
      });
    } finally {
      setUpdating(false);
    }
  };

  const toggleCryptoStatus = async (cryptoId, active) => {
    try {
      await axios.put(`${API}/admin/crypto/status/${cryptoId}`, {
        active: !active
      });
      
      toast({
        title: 'موفق',
        description: `ارز ${active ? 'غیرفعال' : 'فعال'} شد`,
      });
      
      fetchCryptoData();
    } catch (error) {
      console.error('خطا در تغییر وضعیت:', error);
      toast({
        title: 'خطا',
        description: 'خطا در تغییر وضعیت ارز',
        variant: 'destructive'
      });
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
  };

  const formatPrice = (price) => {
    if (price >= 1000000) {
      return (price / 1000000).toFixed(2) + 'M';
    } else if (price >= 1000) {
      return (price / 1000).toFixed(2) + 'K';
    } else {
      return price.toFixed(2);
    }
  };

  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-slate-200';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'bg-green-600';
      case 'maintenance': return 'bg-yellow-600';
      case 'offline': return 'bg-red-600';
      default: return 'bg-slate-600';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-200">بارگذاری مدیریت قیمت‌ها...</p>
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
              <DollarSign className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">مدیریت قیمت‌های ارزهای دیجیتال</h1>
            </div>
            <nav className="flex gap-4">
              <a href="/admin" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/admin/users" className="text-slate-300 hover:text-white transition-colors">کاربران</a>
              <a href="/admin/orders" className="text-slate-300 hover:text-white transition-colors">سفارشات</a>
              <a href="/admin/trading" className="text-slate-300 hover:text-white transition-colors">معاملات</a>
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
        {/* Market Status */}
        {marketStatus && (
          <Card className="bg-slate-900 border-slate-800 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-semibold">وضعیت بازار</h3>
                  </div>
                  <Badge className={`${getStatusColor(marketStatus.status)}`}>
                    {marketStatus.status === 'online' ? 'آنلاین' : 
                     marketStatus.status === 'maintenance' ? 'تعمیرات' : 'آفلاین'}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-sm text-slate-200">
                  <span>آخرین به‌روزرسانی: {marketStatus.last_update}</span>
                  <span>منبع: {marketStatus.source}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Control Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-blue-400" />
                کنترل‌های سیستم
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">به‌روزرسانی خودکار</span>
                <Button
                  onClick={() => setAutoUpdate(!autoUpdate)}
                  variant={autoUpdate ? "default" : "outline"}
                  size="sm"
                >
                  {autoUpdate ? 'فعال' : 'غیرفعال'}
                </Button>
              </div>
              
              <Button 
                onClick={syncWithExternalAPI}
                disabled={updating}
                className="w-full"
              >
                <Globe className="w-4 h-4 mr-2" />
                {updating ? 'در حال همگام‌سازی...' : 'همگام‌سازی با منابع خارجی'}
              </Button>
              
              <Button 
                onClick={fetchCryptoData}
                variant="outline"
                className="w-full"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                بروزرسانی دستی
              </Button>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                آمار بازار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-200">تعداد ارزها</span>
                  <span className="text-sm font-semibold">{cryptos.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-200">ارزهای فعال</span>
                  <span className="text-sm font-semibold text-green-400">
                    {cryptos.filter(c => c.active).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-200">میانگین تغییر</span>
                  <span className={`text-sm font-semibold ${getChangeColor(
                    cryptos.reduce((acc, c) => acc + (c.change_24h || 0), 0) / cryptos.length
                  )}`}>
                    {((cryptos.reduce((acc, c) => acc + (c.change_24h || 0), 0) / cryptos.length) || 0).toFixed(2)}%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-emerald-400" />
                افزودن ارز جدید
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!showAddForm ? (
                <Button 
                  onClick={() => setShowAddForm(true)}
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  اضافه کردن ارز
                </Button>
              ) : (
                <div className="space-y-3">
                  <Input
                    placeholder="نماد (BTC)"
                    value={newCrypto.symbol}
                    onChange={(e) => setNewCrypto({...newCrypto, symbol: e.target.value})}
                  />
                  <Input
                    placeholder="نام (Bitcoin)"
                    value={newCrypto.name}
                    onChange={(e) => setNewCrypto({...newCrypto, name: e.target.value})}
                  />
                  <Input
                    placeholder="قیمت (تومان)"
                    type="number"
                    value={newCrypto.price}
                    onChange={(e) => setNewCrypto({...newCrypto, price: e.target.value})}
                  />
                  <div className="flex gap-2">
                    <Button onClick={addNewCrypto} disabled={updating} size="sm">
                      <Save className="w-3 h-3 mr-1" />
                      ذخیره
                    </Button>
                    <Button onClick={() => setShowAddForm(false)} variant="outline" size="sm">
                      <X className="w-3 h-3 mr-1" />
                      لغو
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Crypto Prices Table */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-emerald-400" />
                قیمت‌های ارزهای دیجیتال
              </div>
              <Badge variant="outline" className="text-emerald-400 border-emerald-400">
                {cryptos.filter(c => c.active).length} ارز فعال
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-slate-800">
                  <tr>
                    <th className="text-right p-3 text-sm font-semibold text-slate-300">ارز</th>
                    <th className="text-right p-3 text-sm font-semibold text-slate-300">قیمت (تومان)</th>
                    <th className="text-right p-3 text-sm font-semibold text-slate-300">تغییر 24س</th>
                    <th className="text-right p-3 text-sm font-semibold text-slate-300">وضعیت</th>
                    <th className="text-right p-3 text-sm font-semibold text-slate-300">آخرین به‌روزرسانی</th>
                    <th className="text-right p-3 text-sm font-semibold text-slate-300">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {cryptos.map((crypto) => (
                    <tr key={crypto.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                      <td className="p-3">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-slate-800 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold">{crypto.symbol?.charAt(0)}</span>
                          </div>
                          <div>
                            <div className="font-semibold">{crypto.symbol}</div>
                            <div className="text-xs text-slate-200">{crypto.name}</div>
                          </div>
                        </div>
                      </td>
                      
                      <td className="p-3">
                        {editingCrypto === crypto.id ? (
                          <div className="flex items-center gap-2">
                            <Input
                              type="number"
                              defaultValue={crypto.price_tmn}
                              className="w-32"
                              id={`price-${crypto.id}`}
                            />
                            <Button 
                              size="sm" 
                              onClick={() => {
                                const newPrice = document.getElementById(`price-${crypto.id}`).value;
                                updateCryptoPrice(crypto.id, newPrice);
                              }}
                              disabled={updating}
                            >
                              <Save className="w-3 h-3" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => setEditingCrypto(null)}
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2">
                            <span className="font-semibold">
                              {formatCurrency(crypto.price_tmn || 0)}
                            </span>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setEditingCrypto(crypto.id)}
                            >
                              <Edit className="w-3 h-3" />
                            </Button>
                          </div>
                        )}
                      </td>
                      
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          {crypto.change_24h >= 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-400" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-400" />
                          )}
                          <span className={getChangeColor(crypto.change_24h)}>
                            {crypto.change_24h >= 0 ? '+' : ''}{crypto.change_24h?.toFixed(2) || 0}%
                          </span>
                        </div>
                      </td>
                      
                      <td className="p-3">
                        <Badge 
                          className={`cursor-pointer ${crypto.active ? 'bg-green-600' : 'bg-slate-600'}`}
                          onClick={() => toggleCryptoStatus(crypto.id, crypto.active)}
                        >
                          {crypto.active ? 'فعال' : 'غیرفعال'}
                        </Badge>
                      </td>
                      
                      <td className="p-3">
                        <div className="text-sm text-slate-200">
                          {crypto.last_updated ? new Date(crypto.last_updated).toLocaleDateString('fa-IR') : 'نامشخص'}
                        </div>
                      </td>
                      
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            <BarChart3 className="w-3 h-3" />
                          </Button>
                          <Button size="sm" variant="outline" className="text-red-400 hover:text-red-300">
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminPriceManager;