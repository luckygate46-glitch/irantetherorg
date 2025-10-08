import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  TrendingUp,
  TrendingDown,
  Building2,
  Coins,
  DollarSign,
  Globe,
  BarChart3,
  Star,
  Activity,
  Layers,
  Gem,
  Home,
  RefreshCw,
  Eye,
  ShoppingCart
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MultiAssetTrading = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('crypto');
  const [assets, setAssets] = useState({
    crypto: [],
    stocks: [],
    commodities: [],
    forex: []
  });
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchAssetData();
  }, [user, navigate, activeTab]);

  const fetchAssetData = async () => {
    try {
      setRefreshing(true);
      let response;
      
      switch (activeTab) {
        case 'crypto':
          response = await axios.get(`${API}/crypto/prices`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          if (response.data.success) {
            const cryptoList = Object.entries(response.data.data).map(([id, data]) => ({
              id,
              symbol: data.symbol?.toUpperCase() || id.toUpperCase(),
              name: data.name || id,
              price_tmn: data.usd_price_tmn || 0,
              change_24h: data.usd_24h_change || 0,
              volume_24h: data.usd_24h_vol || 0,
              market_cap: data.market_cap || 0
            }));
            setAssets(prev => ({ ...prev, crypto: cryptoList }));
          }
          break;
          
        case 'stocks':
          response = await axios.get(`${API}/assets/stocks`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          setAssets(prev => ({ ...prev, stocks: response.data.stocks || [] }));
          break;
          
        case 'commodities':
          response = await axios.get(`${API}/assets/commodities`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          setAssets(prev => ({ ...prev, commodities: response.data.commodities || [] }));
          break;
          
        case 'forex':
          response = await axios.get(`${API}/assets/forex`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          setAssets(prev => ({ ...prev, forex: response.data.forex_pairs || [] }));
          break;
      }
    } catch (error) {
      console.error('خطا در بارگذاری داده‌های دارایی:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات بازار',
        variant: 'destructive'
      });
    } finally {
      setRefreshing(false);
    }
  };

  const formatCurrency = (amount, unit = 'تومان') => {
    return `${new Intl.NumberFormat('fa-IR').format(Math.round(amount))} ${unit}`;
  };

  const formatPercent = (percent) => {
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent?.toFixed(2) || 0}%`;
  };

  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-400';
    if (change < 0) return 'text-red-400';
    return 'text-slate-400';
  };

  const getChangeIcon = (change) => {
    if (change > 0) return <TrendingUp className="w-4 h-4" />;
    if (change < 0) return <TrendingDown className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
  };

  const handleTrade = (asset) => {
    if (user?.kyc_level < 1) {
      toast({
        title: 'احراز هویت مورد نیاز',
        description: 'برای معاملات به احراز هویت نیاز دارید',
        variant: 'destructive'
      });
      navigate('/kyc');
      return;
    }

    // Navigate to appropriate trading interface
    if (activeTab === 'crypto') {
      navigate('/trade', { state: { selectedCoin: asset } });
    } else {
      toast({
        title: 'به زودی',
        description: `معاملات ${activeTab === 'stocks' ? 'سهام' : activeTab === 'commodities' ? 'کالا' : 'فارکس'} به زودی فعال خواهد شد`,
      });
    }
  };

  const renderAssetCard = (asset, type) => {
    const isPositiveChange = (asset.change_24h || asset.daily_change || 0) > 0;
    const change = asset.change_24h || asset.daily_change || 0;

    return (
      <Card key={asset.id || asset.symbol} className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors">
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-lg">{asset.symbol || asset.pair_symbol}</h3>
                {type === 'crypto' && (
                  <Badge className="text-xs bg-blue-600">کریپتو</Badge>
                )}
                {type === 'stocks' && (
                  <Badge className="text-xs bg-green-600">{asset.sector}</Badge>
                )}
                {type === 'commodities' && (
                  <Badge className="text-xs bg-yellow-600">{asset.unit}</Badge>
                )}
                {type === 'forex' && (
                  <Badge className="text-xs bg-purple-600">فارکس</Badge>
                )}
              </div>
              <p className="text-sm text-slate-400 truncate">{asset.name}</p>
            </div>
            <div className="text-right">
              <div className="font-bold text-lg">
                {type === 'forex' ? 
                  formatCurrency(asset.bid_price) : 
                  formatCurrency(asset.price_tmn || asset.current_price)
                }
              </div>
              {type === 'commodities' && (
                <div className="text-xs text-slate-400">هر {asset.unit}</div>
              )}
            </div>
          </div>

          <div className="flex justify-between items-center mb-3">
            <div className={`flex items-center gap-1 ${getChangeColor(change)}`}>
              {getChangeIcon(change)}
              <span className="text-sm font-medium">
                {formatPercent(change)}
              </span>
            </div>
            
            {(asset.volume_24h || asset.volume) && (
              <div className="text-xs text-slate-500">
                حجم: {formatCurrency(asset.volume_24h || asset.volume)}
              </div>
            )}
          </div>

          {type === 'forex' && (
            <div className="flex justify-between text-xs text-slate-400 mb-3">
              <span>خرید: {formatCurrency(asset.bid_price)}</span>
              <span>فروش: {formatCurrency(asset.ask_price)}</span>
              <span>اسپرد: {asset.spread}</span>
            </div>
          )}

          {type === 'stocks' && asset.market && (
            <div className="text-xs text-slate-500 mb-3">
              بازار: {asset.market}
              {asset.pe_ratio && ` • P/E: ${asset.pe_ratio}`}
            </div>
          )}

          {type === 'commodities' && asset.quality_grade && (
            <div className="text-xs text-slate-500 mb-3">
              کیفیت: {asset.quality_grade}
            </div>
          )}

          <div className="flex gap-2">
            <Button 
              size="sm" 
              onClick={() => handleTrade(asset)}
              className="flex-1 bg-emerald-600 hover:bg-emerald-700"
            >
              <ShoppingCart className="w-3 h-3 mr-1" />
              معامله
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              className="px-3"
            >
              <Eye className="w-3 h-3" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  const getTabIcon = (tab) => {
    switch (tab) {
      case 'crypto': return <Coins className="w-4 h-4" />;
      case 'stocks': return <Building2 className="w-4 h-4" />;
      case 'commodities': return <Gem className="w-4 h-4" />;
      case 'forex': return <Globe className="w-4 h-4" />;
      default: return <BarChart3 className="w-4 h-4" />;
    }
  };

  const getTabLabel = (tab) => {
    switch (tab) {
      case 'crypto': return 'ارزهای دیجیتال';
      case 'stocks': return 'بورس و سهام';
      case 'commodities': return 'کالاها';
      case 'forex': return 'ارزهای خارجی';
      default: return tab;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <Layers className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">معاملات چندگانه</h1>
              {refreshing && <div className="animate-spin w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>}
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
            <Button onClick={fetchAssetData} variant="outline" size="sm" disabled={refreshing}>
              <RefreshCw className="w-4 h-4" />
            </Button>
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
          {['crypto', 'stocks', 'commodities', 'forex'].map((tab) => (
            <Button
              key={tab}
              variant={activeTab === tab ? "default" : "ghost"}
              onClick={() => setActiveTab(tab)}
              className="flex items-center gap-2 flex-1"
            >
              {getTabIcon(tab)}
              {getTabLabel(tab)}
              <Badge className="ml-2 text-xs">
                {assets[tab]?.length || 0}
              </Badge>
            </Button>
          ))}
        </div>

        {/* Market Overview */}
        <Card className="bg-slate-900 border-slate-800 mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              نمای کلی بازار {getTabLabel(activeTab)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-400">
                  {assets[activeTab]?.length || 0}
                </div>
                <div className="text-sm text-slate-400">تعداد داراییها</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {activeTab === 'forex' ? '24/7' : 'فعال'}
                </div>
                <div className="text-sm text-slate-400">وضعیت بازار</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {assets[activeTab]?.filter(a => (a.change_24h || a.daily_change || 0) > 0).length || 0}
                </div>
                <div className="text-sm text-slate-400">در رشد</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">
                  {assets[activeTab]?.filter(a => (a.change_24h || a.daily_change || 0) < 0).length || 0}
                </div>
                <div className="text-sm text-slate-400">در نزول</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Assets Grid */}
        {assets[activeTab]?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {assets[activeTab].map(asset => renderAssetCard(asset, activeTab))}
          </div>
        ) : (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-8 text-center">
              <div className="flex flex-col items-center gap-4">
                {refreshing ? (
                  <>
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
                    <p className="text-slate-400">در حال بارگذاری {getTabLabel(activeTab)}...</p>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center">
                      {getTabIcon(activeTab)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-2">
                        {activeTab === 'crypto' ? 'داده‌های ارز دیجیتال در دسترس نیست' :
                         `بازار ${getTabLabel(activeTab)} به زودی`}
                      </h3>
                      <p className="text-slate-400 mb-4">
                        {activeTab === 'crypto' ? 
                          'لطفاً صفحه را مجدداً بارگذاری کنید' :
                          `معاملات ${getTabLabel(activeTab)} در آینده نزدیک راه‌اندازی خواهد شد`
                        }
                      </p>
                      <Button onClick={fetchAssetData} className="bg-emerald-600 hover:bg-emerald-700">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        تلاش مجدد
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Coming Soon Features */}
        {activeTab !== 'crypto' && assets[activeTab]?.length > 0 && (
          <Card className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border-blue-800 mt-6">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <Star className="w-6 h-6 text-yellow-400" />
                <h3 className="text-xl font-semibold">ویژگی‌های در راه</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                  <span>معاملات آنی</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                  <span>سفارشات پیشرفته</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                  <span>تحلیل تکنیکال</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <span>هشدارهای قیمتی</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                  <span>پرتفوی ترکیبی</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>نمودارهای پیشرفته</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MultiAssetTrading;