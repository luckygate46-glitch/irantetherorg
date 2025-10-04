import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Brain, 
  Shield, 
  TrendingUp, 
  AlertTriangle, 
  Eye, 
  Zap,
  BarChart3,
  Users,
  CreditCard,
  Clock,
  Bot,
  Cpu,
  Activity,
  Target,
  Lightbulb,
  Settings,
  DollarSign,
  PieChart,
  LineChart,
  Bell,
  Search,
  Filter,
  RefreshCw
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboardAI = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [fraudAlerts, setFraudAlerts] = useState([]);
  const [marketInsights, setMarketInsights] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchDashboardData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [user, navigate]);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const [statsRes, aiRes, fraudRes, marketRes, healthRes] = await Promise.all([
        axios.get(`${API}/admin/stats`),
        axios.get(`${API}/admin/ai/insights`),
        axios.get(`${API}/admin/ai/fraud-alerts`),
        axios.get(`${API}/admin/ai/market-insights`),
        axios.get(`${API}/admin/system/health`)
      ]);

      setStats(statsRes.data);
      setAiInsights(aiRes.data);
      setFraudAlerts(fraudRes.data);
      setMarketInsights(marketRes.data);
      setSystemHealth(healthRes.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌ها:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات داشبورد',
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

  const getHealthColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return 'bg-red-600';
      case 'medium': return 'bg-yellow-600';
      case 'low': return 'bg-green-600';
      default: return 'bg-slate-600';
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
              <h1 className="text-2xl font-bold text-emerald-400">داشبورد هوشمند ادمین</h1>
              {refreshing && <div className="animate-spin w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>}
            </div>
            <nav className="flex gap-4">
              <a href="/admin/users" className="text-slate-300 hover:text-white transition-colors">کاربران</a>
              <a href="/admin/kyc" className="text-slate-300 hover:text-white transition-colors">احراز هویت</a>
              <a href="/admin/orders" className="text-slate-300 hover:text-white transition-colors">سفارشات</a>
              <a href="/admin/trading" className="text-slate-300 hover:text-white transition-colors">معاملات</a>
              <a href="/admin/prices" className="text-slate-300 hover:text-white transition-colors">قیمت‌ها</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={fetchDashboardData} variant="outline" size="sm" disabled={refreshing}>
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
        {/* AI System Health Alert */}
        {systemHealth && systemHealth.score < 80 && (
          <Card className="bg-red-900/20 border-red-800 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-red-400" />
                <div>
                  <h3 className="font-semibold text-red-400">هشدار سلامت سیستم</h3>
                  <p className="text-sm text-red-300">وضعیت سیستم: {systemHealth.score}% - نیاز به بررسی</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Real-time Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Users Stats */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" />
                کاربران فعال
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.active_users || 0}</div>
              <p className="text-xs text-slate-400">از {stats?.total_users || 0} کل کاربران</p>
              {aiInsights?.user_growth && (
                <div className="flex items-center gap-1 mt-2">
                  <TrendingUp className="w-3 h-3 text-green-400" />
                  <span className="text-xs text-green-400">+{aiInsights.user_growth}% این هفته</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Trading Volume */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-400" />
                حجم معاملات (24س)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats?.trading_volume_24h || 0)} ت</div>
              <p className="text-xs text-slate-400">{stats?.orders_count_24h || 0} سفارش</p>
              {marketInsights?.volume_trend && (
                <div className="flex items-center gap-1 mt-2">
                  <TrendingUp className={`w-3 h-3 ${marketInsights.volume_trend > 0 ? 'text-green-400' : 'text-red-400'}`} />
                  <span className={`text-xs ${marketInsights.volume_trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {marketInsights.volume_trend > 0 ? '+' : ''}{marketInsights.volume_trend}% نسبت به دیروز
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pending Orders */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="w-4 h-4 text-yellow-400" />
                سفارشات در انتظار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.pending_orders || 0}</div>
              <p className="text-xs text-slate-400">نیاز به بررسی</p>
              {aiInsights?.avg_processing_time && (
                <div className="text-xs text-slate-400 mt-2">
                  میانگین زمان پردازش: {aiInsights.avg_processing_time} دقیقه
                </div>
              )}
            </CardContent>
          </Card>

          {/* System Health */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4 text-purple-400" />
                سلامت سیستم
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getHealthColor(systemHealth?.score || 0)}`}>
                {systemHealth?.score || 0}%
              </div>
              <p className="text-xs text-slate-400">عملکرد کلی</p>
              <div className="w-full bg-slate-800 rounded-full h-2 mt-2">
                <div 
                  className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${systemHealth?.score || 0}%` }}
                ></div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights and Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Fraud Detection Alerts */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-red-400" />
                هشدارهای امنیتی هوشمند
              </CardTitle>
            </CardHeader>
            <CardContent>
              {fraudAlerts.length === 0 ? (
                <div className="text-center py-8">
                  <Shield className="w-12 h-12 text-green-400 mx-auto mb-2" />
                  <p className="text-slate-400">هیچ تهدید امنیتی شناسایی نشده</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {fraudAlerts.slice(0, 5).map((alert, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                      <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium">{alert.title}</span>
                          <Badge className={`text-xs ${getRiskColor(alert.risk_level)}`}>
                            {alert.risk_level === 'high' ? 'بالا' : alert.risk_level === 'medium' ? 'متوسط' : 'پایین'}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-400">{alert.description}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Button size="sm" variant="outline" className="text-xs">
                            بررسی
                          </Button>
                          <span className="text-xs text-slate-500">{alert.timestamp}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Market Intelligence */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                تحلیل هوشمند بازار
              </CardTitle>
            </CardHeader>
            <CardContent>
              {marketInsights ? (
                <div className="space-y-4">
                  <div className="p-3 bg-slate-800/50 rounded-lg">
                    <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                      <Target className="w-4 h-4 text-blue-400" />
                      پیش‌بینی قیمت
                    </h4>
                    <div className="space-y-2">
                      {marketInsights.predictions?.map((pred, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-sm">{pred.symbol}</span>
                          <div className="flex items-center gap-2">
                            <span className={`text-sm ${pred.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                              {pred.trend === 'up' ? '↗' : '↘'} {pred.prediction}%
                            </span>
                            <span className="text-xs text-slate-400">{pred.confidence}% اطمینان</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-3 bg-slate-800/50 rounded-lg">
                    <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                      توصیه‌های هوشمند
                    </h4>
                    <ul className="space-y-1">
                      {marketInsights.recommendations?.map((rec, index) => (
                        <li key={index} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Brain className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                  <p className="text-slate-400">در حال تحلیل داده‌های بازار...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="bg-slate-900 border-slate-800 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              اقدامات سریع هوشمند
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button 
                onClick={() => navigate('/admin/prices')}
                className="h-20 bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
              >
                <div className="text-center">
                  <DollarSign className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-sm font-semibold">مدیریت قیمت‌ها</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/admin/ai/fraud')}
                className="h-20 bg-gradient-to-br from-red-600 to-red-700 hover:from-red-700 hover:to-red-800"
              >
                <div className="text-center">
                  <Shield className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-sm font-semibold">تشخیص کلاهبرداری</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/admin/ai/analytics')}
                className="h-20 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800"
              >
                <div className="text-center">
                  <BarChart3 className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-sm font-semibold">تحلیل‌های پیشرفته</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/admin/ai/assistant')}
                className="h-20 bg-gradient-to-br from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800"
              >
                <div className="text-center">
                  <Bot className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-sm font-semibold">دستیار هوشمند</span>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* System Performance Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-sm">عملکرد API</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-xs text-slate-400">میانگین پاسخ</span>
                  <span className="text-xs">{systemHealth?.api_response_time || 0}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-slate-400">درخواست‌های موفق</span>
                  <span className="text-xs text-green-400">{systemHealth?.success_rate || 0}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-slate-400">RPS</span>
                  <span className="text-xs">{systemHealth?.requests_per_second || 0}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-sm">کاربران آنلاین</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400 mb-2">
                {stats?.online_users || 0}
              </div>
              <div className="text-xs text-slate-400">
                {stats?.trading_users || 0} نفر در حال معامله
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-sm">درآمد امروز</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400 mb-2">
                {formatCurrency(stats?.revenue_today || 0)} ت
              </div>
              <div className="text-xs text-slate-400">
                کارمزد معاملات: {formatCurrency(stats?.trading_fees_today || 0)} ت
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardAI;