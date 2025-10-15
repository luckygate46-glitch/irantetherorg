import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Cpu,
  Database,
  Shield,
  Users,
  Globe,
  Smartphone,
  Monitor,
  Tablet,
  Clock,
  PieChart,
  LineChart,
  Target,
  Zap,
  AlertTriangle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminAdvancedAnalytics = ({ user, onLogout }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState('system');
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchAnalyticsData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAnalyticsData, 30000);
    return () => clearInterval(interval);
  }, [user, navigate]);

  const fetchAnalyticsData = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get(`${API}/admin/ai/advanced-analytics`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌های تحلیل پیشرفته:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات تحلیل پیشرفته',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(num));
  };

  const getPerformanceColor = (value, thresholds = { good: 80, warning: 50 }) => {
    if (value >= thresholds.good) return 'text-green-400';
    if (value >= thresholds.warning) return 'text-yellow-400';
    return 'text-red-400';
  };

  const renderMetricCard = (title, value, unit = '', icon, color = 'text-blue-400') => (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          {React.cloneElement(icon, { className: `w-4 h-4 ${color}` })}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${color}`}>
          {typeof value === 'number' ? formatNumber(value) : value} {unit}
        </div>
      </CardContent>
    </Card>
  );

  const renderTrendChart = (data, title, color = 'rgb(34, 197, 94)') => (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-24 flex items-end gap-1">
          {data?.map((value, index) => (
            <div
              key={index}
              className="flex-1 rounded-t"
              style={{
                height: `${Math.max(8, (value / Math.max(...data)) * 100)}%`,
                backgroundColor: color,
                opacity: 0.7 + (value / Math.max(...data)) * 0.3
              }}
              title={`ساعت ${index}: ${value}%`}
            />
          ))}
        </div>
        <div className="text-xs text-slate-200 mt-2">24 ساعت گذشته</div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-200">بارگذاری تحلیل‌های پیشرفته...</p>
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
              <h1 className="text-2xl font-bold text-emerald-400">تحلیل‌های پیشرفته</h1>
              {refreshing && <div className="animate-spin w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>}
            </div>
            <nav className="flex gap-4">
              <Button 
                onClick={() => navigate('/admin/dashboard')}
                variant="ghost"
                className="text-slate-300 hover:text-white"
              >
                داشبورد
              </Button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={fetchAnalyticsData} variant="outline" size="sm" disabled={refreshing}>
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
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'system', label: 'سیستم', icon: <Cpu className="w-4 h-4" /> },
            { id: 'users', label: 'کاربران', icon: <Users className="w-4 h-4" /> },
            { id: 'trading', label: 'معاملات', icon: <TrendingUp className="w-4 h-4" /> }
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={selectedTab === tab.id ? "default" : "outline"}
              onClick={() => setSelectedTab(tab.id)}
              className="flex items-center gap-2"
            >
              {tab.icon}
              {tab.label}
            </Button>
          ))}
        </div>

        {/* System Analytics Tab */}
        {selectedTab === 'system' && analyticsData?.system_analytics && (
          <div className="space-y-6">
            {/* Performance Trends */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4">
              {analyticsData.system_analytics.performance_trends && (
                <>
                  {renderTrendChart(
                    analyticsData.system_analytics.performance_trends.cpu_trend,
                    'استفاده از CPU',
                    'rgb(239, 68, 68)'
                  )}
                  {renderTrendChart(
                    analyticsData.system_analytics.performance_trends.memory_trend,
                    'استفاده از حافظه',
                    'rgb(34, 197, 94)'
                  )}
                  {renderTrendChart(
                    analyticsData.system_analytics.performance_trends.disk_trend,
                    'استفاده از دیسک',
                    'rgb(59, 130, 246)'
                  )}
                  {renderTrendChart(
                    analyticsData.system_analytics.performance_trends.network_trend,
                    'ترافیک شبکه',
                    'rgb(168, 85, 247)'
                  )}
                </>
              )}
            </div>

            {/* API Metrics */}
            {analyticsData.system_analytics.api_metrics && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    عملکرد API
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    {renderMetricCard(
                      'کل درخواست‌ها (24س)',
                      analyticsData.system_analytics.api_metrics.total_requests_24h,
                      '',
                      <Activity />,
                      'text-blue-400'
                    )}
                    {renderMetricCard(
                      'نرخ خطا',
                      analyticsData.system_analytics.api_metrics.error_rate_24h.toFixed(1),
                      '%',
                      <AlertTriangle />,
                      getPerformanceColor(100 - analyticsData.system_analytics.api_metrics.error_rate_24h)
                    )}
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-medium text-slate-300">عملکرد API endpoints</h4>
                    {Object.entries(analyticsData.system_analytics.api_metrics.endpoint_performance || {}).map(([endpoint, metrics]) => (
                      <div key={endpoint} className="p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex justify-between items-center">
                          <code className="text-sm text-emerald-400">{endpoint}</code>
                          <div className="flex gap-4 text-sm">
                            <span className="text-slate-200">
                              زمان پاسخ: <span className="text-white">{Math.round(metrics.avg_time)}ms</span>
                            </span>
                            <span className="text-slate-200">
                              موفقیت: <span className={getPerformanceColor(metrics.success_rate)}>{metrics.success_rate.toFixed(1)}%</span>
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Database and Security Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {analyticsData.system_analytics.database_metrics && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="w-5 h-5 text-green-400" />
                      عملکرد پایگاه داده
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">استفاده از Connection Pool</span>
                        <span className={getPerformanceColor(100 - analyticsData.system_analytics.database_metrics.connection_pool_usage)}>
                          {Math.round(analyticsData.system_analytics.database_metrics.connection_pool_usage)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">عملکرد Query</span>
                        <span className={getPerformanceColor(analyticsData.system_analytics.database_metrics.query_performance)}>
                          {Math.round(analyticsData.system_analytics.database_metrics.query_performance)}ms
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">کارایی ذخیره‌سازی</span>
                        <span className={getPerformanceColor(analyticsData.system_analytics.database_metrics.storage_efficiency)}>
                          {Math.round(analyticsData.system_analytics.database_metrics.storage_efficiency)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">وضعیت بکاپ</span>
                        <Badge className="bg-green-600 text-white">
                          {analyticsData.system_analytics.database_metrics.backup_status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {analyticsData.system_analytics.security_metrics && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-red-400" />
                      امنیت سیستم
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">تلاش‌های ورود ناموفق</span>
                        <span className="text-red-400">
                          {formatNumber(analyticsData.system_analytics.security_metrics.failed_login_attempts)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">IP های مسدود</span>
                        <span className="text-yellow-400">
                          {formatNumber(analyticsData.system_analytics.security_metrics.blocked_ips)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">هشدارهای امنیتی</span>
                        <span className="text-orange-400">
                          {formatNumber(analyticsData.system_analytics.security_metrics.security_alerts)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-200">وضعیت SSL</span>
                        <Badge className="bg-green-600 text-white">
                          {analyticsData.system_analytics.security_metrics.ssl_status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        )}

        {/* User Behavior Tab */}
        {selectedTab === 'users' && analyticsData?.user_behavior && (
          <div className="space-y-6">
            {/* User Engagement Metrics */}
            {analyticsData.user_behavior.patterns?.engagement_metrics && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {renderMetricCard(
                  'کاربران فعال روزانه',
                  analyticsData.user_behavior.patterns.engagement_metrics.daily_active_users,
                  '',
                  <Users />,
                  'text-blue-400'
                )}
                {renderMetricCard(
                  'کاربران فعال هفتگی',
                  analyticsData.user_behavior.patterns.engagement_metrics.weekly_active_users,
                  '',
                  <Users />,
                  'text-green-400'
                )}
                {renderMetricCard(
                  'کاربران فعال ماهانه',
                  analyticsData.user_behavior.patterns.engagement_metrics.monthly_active_users,
                  '',
                  <Users />,
                  'text-purple-400'
                )}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Geographic Distribution */}
              {analyticsData.user_behavior.patterns?.geographic_distribution && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Globe className="w-5 h-5 text-blue-400" />
                      توزیع جغرافیایی کاربران
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(analyticsData.user_behavior.patterns.geographic_distribution).map(([city, percentage]) => (
                        <div key={city} className="flex justify-between items-center">
                          <span className="text-slate-300 capitalize">{city}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-slate-700 rounded-full">
                              <div 
                                className="h-full bg-blue-500 rounded-full"
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                            <span className="text-sm text-slate-200 w-12">{Math.round(percentage)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Device Preferences */}
              {analyticsData.user_behavior.patterns?.device_preferences && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Smartphone className="w-5 h-5 text-green-400" />
                      ترجیحات دستگاه
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        { key: 'mobile', label: 'موبایل', icon: <Smartphone className="w-4 h-4" />, color: 'bg-green-500' },
                        { key: 'desktop', label: 'دسکتاپ', icon: <Monitor className="w-4 h-4" />, color: 'bg-blue-500' },
                        { key: 'tablet', label: 'تبلت', icon: <Tablet className="w-4 h-4" />, color: 'bg-purple-500' }
                      ].map((device) => {
                        const percentage = analyticsData.user_behavior.patterns.device_preferences[device.key];
                        return (
                          <div key={device.key} className="flex justify-between items-center">
                            <div className="flex items-center gap-2 text-slate-300">
                              {device.icon}
                              {device.label}
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-20 h-2 bg-slate-700 rounded-full">
                                <div 
                                  className={`h-full ${device.color} rounded-full`}
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                              <span className="text-sm text-slate-200 w-12">{Math.round(percentage)}%</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* User Insights */}
            {analyticsData.user_behavior.insights && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-yellow-400" />
                    بینش‌های کاربری
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analyticsData.user_behavior.insights.map((insight, index) => (
                      <li key={index} className="flex items-center gap-2 text-slate-300">
                        <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Trading Performance Tab */}
        {selectedTab === 'trading' && analyticsData?.trading_performance && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {renderMetricCard(
                'امتیاز کلی عملکرد',
                analyticsData.trading_performance.overall_score,
                '%',
                <BarChart3 />,
                getPerformanceColor(analyticsData.trading_performance.overall_score)
              )}
              {analyticsData.trading_performance.performance_metrics && (
                <>
                  {renderMetricCard(
                    'نرخ موفقیت اجرا',
                    analyticsData.trading_performance.performance_metrics.execution_speed?.success_rate?.toFixed(1),
                    '%',
                    <Zap />,
                    getPerformanceColor(analyticsData.trading_performance.performance_metrics.execution_speed?.success_rate)
                  )}
                  {renderMetricCard(
                    'عمق بازار',
                    analyticsData.trading_performance.performance_metrics.liquidity_analysis?.market_depth?.toFixed(1),
                    '%',
                    <TrendingUp />,
                    getPerformanceColor(analyticsData.trading_performance.performance_metrics.liquidity_analysis?.market_depth)
                  )}
                  {renderMetricCard(
                    'رضایت کاربران',
                    analyticsData.trading_performance.performance_metrics.user_satisfaction?.user_retention?.toFixed(1),
                    '%',
                    <Users />,
                    getPerformanceColor(analyticsData.trading_performance.performance_metrics.user_satisfaction?.user_retention)
                  )}
                </>
              )}
            </div>

            {/* Detailed Performance Metrics */}
            {analyticsData.trading_performance.performance_metrics && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="w-5 h-5 text-blue-400" />
                      سرعت اجرای سفارشات
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-slate-200">میانگین زمان اجرا</span>
                        <span className="text-white">
                          {analyticsData.trading_performance.performance_metrics.execution_speed.avg_order_execution?.toFixed(1)}s
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-200">سریع‌ترین اجرا</span>
                        <span className="text-green-400">
                          {analyticsData.trading_performance.performance_metrics.execution_speed.fastest_execution?.toFixed(1)}s
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-200">کندترین اجرا</span>
                        <span className="text-red-400">
                          {analyticsData.trading_performance.performance_metrics.execution_speed.slowest_execution?.toFixed(1)}s
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-green-400" />
                      تحلیل نقدینگی
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-slate-200">اسپرد Bid-Ask</span>
                        <span className="text-white">
                          {analyticsData.trading_performance.performance_metrics.liquidity_analysis.bid_ask_spread?.toFixed(2)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-200">ثبات حجم</span>
                        <span className={getPerformanceColor(analyticsData.trading_performance.performance_metrics.liquidity_analysis.volume_consistency)}>
                          {analyticsData.trading_performance.performance_metrics.liquidity_analysis.volume_consistency?.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Recommendations */}
            {analyticsData.trading_performance.recommendations && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-yellow-400" />
                    توصیه‌های بهینه‌سازی
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {analyticsData.trading_performance.recommendations.map((recommendation, index) => (
                      <li key={index} className="flex items-center gap-2 text-slate-300">
                        <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                        {recommendation}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAdvancedAnalytics;