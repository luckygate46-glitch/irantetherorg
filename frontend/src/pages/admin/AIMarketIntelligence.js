import React, { useState, useEffect } from 'react';
import AdminLayout from '@/layouts/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import {
  TrendingUp, TrendingDown, BarChart3, PieChart, Activity, Globe,
  DollarSign, Bitcoin, Zap, Target, Brain, AlertTriangle, RefreshCw
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIMarketIntelligence = ({ user, onLogout }) => {
  const [marketMetrics, setMarketMetrics] = useState({});
  const [priceAnalysis, setPriceAnalysis] = useState([]);
  const [tradingPatterns, setTradingPatterns] = useState([]);
  const [marketPredictions, setMarketPredictions] = useState([]);
  const [iranianMarketData, setIranianMarketData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketIntelligence();
    const interval = setInterval(fetchMarketIntelligence, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMarketIntelligence = async () => {
    try {
      setLoading(true);
      
      // Simulate AI market intelligence data
      setMarketMetrics({
        globalVolume24h: 89540000000,
        iranianVolume24h: 45600000000,
        marketCap: 2340000000000,
        dominanceBTC: 45.7,
        volatilityIndex: 62.3,
        fearGreedIndex: 67,
        liquidityScore: 89.2,
        arbitrageOpportunities: 12
      });

      setPriceAnalysis([
        {
          symbol: 'BTC',
          name: 'Bitcoin',
          price: 2150000000,
          change24h: 3.45,
          prediction: 'صعودی',
          confidence: 87.2,
          resistance: 2200000000,
          support: 2050000000,
          volume: 1250000000,
          aiSignal: 'خرید'
        },
        {
          symbol: 'ETH',
          name: 'Ethereum',
          price: 145000000,
          change24h: -1.23,
          prediction: 'نزولی کوتاه مدت',
          confidence: 72.8,
          resistance: 150000000,
          support: 140000000,
          volume: 850000000,
          aiSignal: 'نگهداری'
        },
        {
          symbol: 'USDT',
          name: 'Tether',
          price: 525000,
          change24h: 0.02,
          prediction: 'ثبات',
          confidence: 98.5,
          resistance: 530000,
          support: 520000,
          volume: 2100000000,
          aiSignal: 'خنثی'
        }
      ]);

      setTradingPatterns([
        {
          id: 1,
          pattern: 'الگوی کف دوگانه در BTC',
          timeframe: '4 ساعته',
          probability: 78.9,
          action: 'خرید',
          target: 2300000000,
          stopLoss: 2080000000
        },
        {
          id: 2,
          pattern: 'شکست مقاومت در ETH',
          timeframe: '1 ساعته',
          probability: 65.4,
          action: 'خرید محتاطانه',
          target: 152000000,
          stopLoss: 143000000
        },
        {
          id: 3,
          pattern: 'واگرایی نزولی در ADA',
          timeframe: '6 ساعته',
          probability: 82.1,
          action: 'فروش',
          target: 11500,
          stopLoss: 13200
        }
      ]);

      setMarketPredictions([
        {
          crypto: 'BTC',
          timeframe: '24 ساعت',
          prediction: '+4.2%',
          confidence: 73.5,
          factors: ['شاخص ترس و طمع', 'حجم معاملات', 'تحلیل تکنیکال']
        },
        {
          crypto: 'ETH',
          timeframe: '1 هفته',
          prediction: '+12.8%',
          confidence: 68.9,
          factors: ['ترقی شبکه', 'DeFi رشد', 'حجم نهادی']
        },
        {
          crypto: 'BNB',
          timeframe: '1 ماه',
          prediction: '+25.4%',
          confidence: 61.2,
          factors: ['رشد اکوسیستم', 'سوختن توکن', 'شراکت‌های جدید']
        }
      ]);

      setIranianMarketData({
        dailyVolume: 45600000000,
        activeTraders: 12847,
        topCoin: 'BTC',
        sentiment: 'مثبت',
        iranianPremium: 2.3,
        regulatoryScore: 7.5,
        adoptionRate: 23.7,
        marketMaturity: 'در حال رشد'
      });

    } catch (error) {
      console.error('Error fetching market intelligence:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChangeColor = (change) => {
    return change > 0 ? 'text-green-400' : change < 0 ? 'text-red-400' : 'text-gray-400';
  };

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'خرید': return 'bg-green-600';
      case 'فروش': return 'bg-red-600';
      case 'نگهداری': return 'bg-yellow-600';
      default: return 'bg-gray-600';
    }
  };

  const getActionColor = (action) => {
    if (action.includes('خرید')) return 'text-green-400';
    if (action.includes('فروش')) return 'text-red-400';
    return 'text-yellow-400';
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="ai-market">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="ai-market">
      <div className="space-y-6" dir="rtl">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-green-500" />
              هوش بازار کریپتو
            </h1>
            <p className="text-slate-400 mt-2">تحلیل هوشمند و پیش‌بینی بازار ایران و جهان</p>
          </div>
          <Button onClick={fetchMarketIntelligence} variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            بروزرسانی
          </Button>
        </div>

        {/* Market Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-green-400" />
                حجم جهانی ۲۴ساعته
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                ${(marketMetrics.globalVolume24h / 1000000000).toFixed(1)}B
              </div>
              <p className="text-green-300 text-sm">میلیارد دلار</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Bitcoin className="w-5 h-5 text-orange-400" />
                تسلط بیت کوین
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {marketMetrics.dominanceBTC}%
              </div>
              <p className="text-blue-300 text-sm">از کل بازار</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-900/50 to-pink-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-400" />
                شاخص ترس و طمع
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {marketMetrics.fearGreedIndex}
              </div>
              <p className="text-purple-300 text-sm">طمع متوسط</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-900/50 to-red-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-orange-400" />
                نقدینگی بازار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {marketMetrics.liquidityScore}%
              </div>
              <p className="text-orange-300 text-sm">عالی</p>
            </CardContent>
          </Card>
        </div>

        {/* Price Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              تحلیل قیمت هوشمند
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {priceAnalysis.map(crypto => (
                <div key={crypto.symbol} className="bg-slate-800 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-6 gap-4 items-center">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-sm">{crypto.symbol}</span>
                      </div>
                      <div>
                        <h3 className="text-white font-medium">{crypto.name}</h3>
                        <p className="text-gray-400 text-sm">{crypto.symbol}</p>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-white font-medium">
                        {crypto.price.toLocaleString('fa-IR')} تومان
                      </p>
                      <p className={`text-sm ${getChangeColor(crypto.change24h)}`}>
                        {crypto.change24h > 0 ? '+' : ''}{crypto.change24h}%
                      </p>
                    </div>
                    
                    <div>
                      <p className="text-gray-400 text-xs">پیش‌بینی</p>
                      <p className="text-white text-sm">{crypto.prediction}</p>
                      <p className="text-blue-400 text-xs">اعتماد: {crypto.confidence}%</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-400 text-xs">مقاومت/حمایت</p>
                      <p className="text-red-400 text-sm">{crypto.resistance.toLocaleString('fa-IR')}</p>
                      <p className="text-green-400 text-sm">{crypto.support.toLocaleString('fa-IR')}</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-400 text-xs">حجم ۲۴ساعته</p>
                      <p className="text-white text-sm">{crypto.volume.toLocaleString('fa-IR')}</p>
                    </div>
                    
                    <div>
                      <Badge className={getSignalColor(crypto.aiSignal)}>
                        سیگنال AI: {crypto.aiSignal}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Trading Patterns & Market Predictions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Trading Patterns */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-500" />
                الگوهای معاملاتی شناسایی شده
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {tradingPatterns.map(pattern => (
                  <div key={pattern.id} className="bg-slate-800 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium text-sm">{pattern.pattern}</h4>
                      <Badge className="bg-blue-600">
                        احتمال: {pattern.probability}%
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <p className="text-gray-400">بازه زمانی</p>
                        <p className="text-white">{pattern.timeframe}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">اقدام پیشنهادی</p>
                        <p className={getActionColor(pattern.action)}>{pattern.action}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">هدف قیمتی</p>
                        <p className="text-green-400">{pattern.target.toLocaleString('fa-IR')}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">حد ضرر</p>
                        <p className="text-red-400">{pattern.stopLoss.toLocaleString('fa-IR')}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Market Predictions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-500" />
                پیش‌بینی‌های بازار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {marketPredictions.map((prediction, index) => (
                  <div key={index} className="bg-slate-800 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{prediction.crypto}</h4>
                      <div className="text-left">
                        <p className={`font-bold ${prediction.prediction.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                          {prediction.prediction}
                        </p>
                        <p className="text-gray-400 text-xs">{prediction.timeframe}</p>
                      </div>
                    </div>
                    
                    <div className="mb-2">
                      <p className="text-blue-400 text-xs">سطح اعتماد: {prediction.confidence}%</p>
                    </div>
                    
                    <div>
                      <p className="text-gray-400 text-xs mb-1">عوامل تأثیرگذار:</p>
                      <div className="flex flex-wrap gap-1">
                        {prediction.factors.map(factor => (
                          <Badge key={factor} variant="outline" className="text-xs">
                            {factor}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Iranian Market Intelligence */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-orange-500" />
              هوش بازار ایران
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-green-900/50 to-emerald-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">حجم روزانه</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-green-400">
                    {(iranianMarketData.dailyVolume / 1000000000).toFixed(1)}B
                  </span>
                  <Badge className="bg-green-600">تومان</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">میلیارد تومان</p>
              </div>
              
              <div className="bg-gradient-to-r from-blue-900/50 to-blue-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">معامله‌گران فعال</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-blue-400">
                    {iranianMarketData.activeTraders?.toLocaleString('fa-IR')}
                  </span>
                  <Badge className="bg-blue-600">کاربر</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">امروز</p>
              </div>
              
              <div className="bg-gradient-to-r from-purple-900/50 to-purple-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">حال و هوای بازار</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-purple-400">
                    {iranianMarketData.sentiment}
                  </span>
                  <Badge className="bg-green-600">خوب</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">تحلیل AI</p>
              </div>
              
              <div className="bg-gradient-to-r from-orange-900/50 to-red-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">نرخ پذیرش</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-orange-400">
                    {iranianMarketData.adoptionRate}%
                  </span>
                  <Badge className="bg-yellow-600">رشد</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">ماهانه</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default AIMarketIntelligence;