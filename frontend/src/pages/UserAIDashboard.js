import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Bot, 
  Brain,
  TrendingUp, 
  TrendingDown,
  DollarSign, 
  PieChart,
  Bell,
  MessageCircle,
  BarChart3,
  Target,
  Shield,
  Lightbulb,
  Activity,
  ArrowRight,
  ArrowLeft,
  Star,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserAIDashboard = ({ user, onLogout }) => {
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchAIData();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchAIData, 60000);
    return () => clearInterval(interval);
  }, [user, navigate]);

  const fetchAIData = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get(`${API}/user/ai/dashboard`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setAiData(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌های AI:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات داشبورد هوشمند',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
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

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'bullish': return 'text-green-400';
      case 'bearish': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getSentimentText = (sentiment) => {
    switch (sentiment) {
      case 'bullish': return 'صعودی';
      case 'bearish': return 'نزولی';
      default: return 'خنثی';
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'price_alert': return <TrendingUp className="w-4 h-4" />;
      case 'trading_opportunity': return <Target className="w-4 h-4" />;
      case 'risk_warning': return <Shield className="w-4 h-4" />;
      case 'portfolio_alert': return <PieChart className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-400">بارگذاری داشبورد هوشمند...</p>
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
              <Brain className="w-8 h-8 text-purple-400" />
              <h1 className="text-2xl font-bold text-emerald-400">داشبورد هوشمند من</h1>
              <Badge className="bg-emerald-600 text-white">
                {aiData?.ai_status === 'active' ? 'فعال' : 'غیرفعال'}
              </Badge>
              {refreshing && <div className="animate-spin w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>}
            </div>
            <nav className="flex gap-4">
              <Button 
                onClick={() => navigate('/dashboard')}
                variant="ghost"
                className="text-slate-300 hover:text-white"
              >
                داشبورد اصلی
              </Button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={fetchAIData} variant="outline" size="sm" disabled={refreshing}>
              <Activity className="w-4 h-4" />
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
        {/* Quick Stats */}
        {aiData?.quick_stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                  ارزش پرتفوی
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-emerald-400">
                  {formatCurrency(aiData.quick_stats.portfolio_value)} ت
                </div>
                <div className="flex items-center gap-2 mt-2">
                  {getChangeIcon(aiData.quick_stats.daily_change)}
                  <span className={`text-sm ${getChangeColor(aiData.quick_stats.daily_change)}`}>
                    {aiData.quick_stats.daily_change > 0 ? '+' : ''}{aiData.quick_stats.daily_change?.toFixed(1)}% امروز
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <PieChart className="w-4 h-4 text-blue-400" />
                  تعداد داراییها
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-400">
                  {aiData.quick_stats.holdings_count}
                </div>
                <p className="text-xs text-slate-400">
                  {aiData.quick_stats.top_holding && `بیشترین: ${aiData.quick_stats.top_holding}`}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-purple-400" />
                  عملکرد هفتگی
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getChangeColor(aiData.quick_stats.weekly_performance)}`}>
                  {aiData.quick_stats.weekly_performance > 0 ? '+' : ''}{aiData.quick_stats.weekly_performance?.toFixed(1)}%
                </div>
                <p className="text-xs text-slate-400">7 روز گذشته</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Activity className="w-4 h-4 text-yellow-400" />
                  وضعیت بازار
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-xl font-bold ${getSentimentColor(aiData.market_sentiment)}`}>
                  {getSentimentText(aiData.market_sentiment)}
                </div>
                <p className="text-xs text-slate-400">تحلیل کلی بازار</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AI Recommendations */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-900 border-slate-800 mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  پیشنهادهای هوشمند
                </CardTitle>
              </CardHeader>
              <CardContent>
                {aiData?.quick_recommendations?.length > 0 ? (
                  <div className="space-y-4">
                    {aiData.quick_recommendations.map((rec, index) => (
                      <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-blue-400" />
                            <span className="font-medium">{rec.crypto}</span>
                          </div>
                          <Badge 
                            className={`text-xs ${
                              rec.action === 'buy' || rec.action === 'hold_or_buy' ? 'bg-green-600' : 
                              rec.action === 'sell' || rec.action === 'consider_selling' ? 'bg-red-600' : 
                              'bg-yellow-600'
                            } text-white`}
                          >
                            {rec.action === 'buy' || rec.action === 'hold_or_buy' ? 'خرید' :
                             rec.action === 'sell' || rec.action === 'consider_selling' ? 'فروش' : 'نگهداری'}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-300 mb-2">{rec.reason}</p>
                        <div className="flex justify-between items-center text-xs text-slate-400">
                          <span>اطمینان: {rec.confidence}%</span>
                          <span>بازه زمانی: {rec.timeframe}</span>
                        </div>
                      </div>
                    ))}
                    
                    <div className="pt-4 border-t border-slate-700">
                      <Button 
                        onClick={() => navigate('/ai/recommendations')}
                        className="w-full bg-emerald-600 hover:bg-emerald-700"
                      >
                        مشاهده همه پیشنهادها
                        <ArrowLeft className="w-4 h-4 mr-2" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Target className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                    <p className="text-slate-400">در حال تحلیل بازار برای پیشنهادات بهتر...</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-emerald-400" />
                  دستیار هوشمند
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button 
                    onClick={() => navigate('/ai/portfolio-analysis')}
                    className="h-20 bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                  >
                    <div className="text-center">
                      <PieChart className="w-6 h-6 mx-auto mb-1" />
                      <span className="text-sm font-semibold">تحلیل پرتفوی</span>
                    </div>
                  </Button>

                  <Button 
                    onClick={() => navigate('/ai/market-insights')}
                    className="h-20 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800"
                  >
                    <div className="text-center">
                      <BarChart3 className="w-6 h-6 mx-auto mb-1" />
                      <span className="text-sm font-semibold">تحلیل بازار</span>
                    </div>
                  </Button>

                  <Button 
                    onClick={() => navigate('/ai/assistant')}
                    className="h-20 bg-gradient-to-br from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800"
                  >
                    <div className="text-center">
                      <MessageCircle className="w-6 h-6 mx-auto mb-1" />
                      <span className="text-sm font-semibold">چت با AI</span>
                    </div>
                  </Button>

                  <Button 
                    onClick={() => navigate('/ai/notifications')}
                    className="h-20 bg-gradient-to-br from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800"
                  >
                    <div className="text-center">
                      <Bell className="w-6 h-6 mx-auto mb-1" />
                      <span className="text-sm font-semibold">هشدارهای هوشمند</span>
                    </div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Notifications */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-orange-400" />
                  هشدارهای اخیر
                </CardTitle>
              </CardHeader>
              <CardContent>
                {aiData?.recent_notifications?.length > 0 ? (
                  <div className="space-y-3">
                    {aiData.recent_notifications.map((notification, index) => (
                      <div key={index} className="p-3 bg-slate-800/50 rounded border border-slate-700">
                        <div className="flex items-start gap-2">
                          {getNotificationIcon(notification.type)}
                          <div className="flex-1">
                            <div className="font-medium text-sm">{notification.title}</div>
                            <p className="text-xs text-slate-400 mt-1">{notification.message || notification.description}</p>
                            {notification.timestamp && (
                              <div className="text-xs text-slate-500 mt-2">{notification.timestamp}</div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="w-full mt-3"
                      onClick={() => navigate('/ai/notifications')}
                    >
                      همه هشدارها
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <p className="text-xs text-slate-400">هیچ هشدار جدیدی نیست</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* AI Status */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  وضعیت AI
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">سیستم AI</span>
                    <Badge className="bg-green-600 text-white">فعال</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">آخرین تحلیل</span>
                    <span className="text-slate-300">الان</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">پیشنهادات</span>
                    <span className="text-emerald-400">{aiData?.quick_recommendations?.length || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">هشدارها</span>
                    <span className="text-orange-400">{aiData?.recent_notifications?.length || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Performance Summary */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400" />
                  خلاصه عملکرد
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">بازدهی کل</span>
                    <span className={getChangeColor(aiData?.quick_stats?.weekly_performance || 0)}>
                      {aiData?.quick_stats?.weekly_performance > 0 ? '+' : ''}{aiData?.quick_stats?.weekly_performance?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">بهترین دارایی</span>
                    <span className="text-green-400">{aiData?.quick_stats?.top_holding || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">تنوع پرتفوی</span>
                    <span className="text-blue-400">
                      {aiData?.quick_stats?.holdings_count > 4 ? 'عالی' : 
                       aiData?.quick_stats?.holdings_count > 2 ? 'متوسط' : 'کم'}
                    </span>
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

export default UserAIDashboard;