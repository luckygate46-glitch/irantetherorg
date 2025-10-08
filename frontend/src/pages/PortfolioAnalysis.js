import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  PieChart,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Target,
  Shield,
  Star,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Activity,
  DollarSign,
  Percent,
  Users,
  Brain,
  Lightbulb,
  Settings
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PortfolioAnalysis = ({ user, onLogout }) => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [optimizationData, setOptimizationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchPortfolioAnalysis();
  }, [user, navigate]);

  const fetchPortfolioAnalysis = async () => {
    try {
      setLoading(true);
      
      // Get portfolio analysis
      const analysisResponse = await axios.get(`${API}/user/ai/portfolio-analysis`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setPortfolioData(analysisResponse.data);

      // Get portfolio optimization
      const optimizationResponse = await axios.get(`${API}/ai/portfolio-optimization`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setOptimizationData(optimizationResponse.data);

    } catch (error) {
      console.error('خطا در بارگذاری تحلیل پرتفوی:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات تحلیل پرتفوی',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOptimizePortfolio = async () => {
    try {
      setOptimizing(true);
      const response = await axios.get(`${API}/ai/portfolio-optimization`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      setOptimizationData(response.data);
      toast({
        title: 'بهینه‌سازی انجام شد',
        description: 'تحلیل و پیشنهادات بهینه‌سازی به‌روزرسانی شد',
      });
    } catch (error) {
      toast({
        title: 'خطا در بهینه‌سازی',
        description: 'خطا در انجام بهینه‌سازی پرتفوی',
        variant: 'destructive'
      });
    } finally {
      setOptimizing(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
  };

  const formatPercent = (percent) => {
    const sign = percent >= 0 ? '+' : '';
    return `${sign}${percent?.toFixed(1) || 0}%`;
  };

  const getPerformanceColor = (value) => {
    if (value > 0) return 'text-green-400';
    if (value < 0) return 'text-red-400';
    return 'text-slate-400';
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  const getRiskText = (level) => {
    switch (level) {
      case 'high': return 'بالا';
      case 'medium': return 'متوسط';
      case 'low': return 'پایین';
      default: return level;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-400">بارگذاری تحلیل پرتفوی...</p>
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
              <PieChart className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">تحلیل پرتفوی</h1>
            </div>
            <nav className="flex gap-4">
              <Button 
                onClick={() => navigate('/ai/dashboard')}
                variant="ghost"
                className="text-slate-300 hover:text-white"
              >
                داشبورد AI
              </Button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={fetchPortfolioAnalysis} variant="outline" size="sm" disabled={loading}>
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
        {portfolioData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Portfolio Overview */}
            <div className="lg:col-span-2 space-y-6">
              {/* Current Portfolio Stats */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-emerald-400" />
                    نمای کلی پرتفوی
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-emerald-400">
                        {formatCurrency(portfolioData.current_value || 0)} ت
                      </div>
                      <div className="text-sm text-slate-400">ارزش کل</div>
                    </div>

                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getPerformanceColor(portfolioData.performance_metrics?.total_return_percent || 0)}`}>
                        {formatPercent(portfolioData.performance_metrics?.total_return_percent || 0)}
                      </div>
                      <div className="text-sm text-slate-400">بازدهی کل</div>
                    </div>

                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">
                        {portfolioData.diversification_score?.toFixed(1) || 0}%
                      </div>
                      <div className="text-sm text-slate-400">تنوع پرتفوی</div>
                    </div>

                    <div className="text-center">
                      <div className={`text-2xl font-bold ${getRiskColor(portfolioData.risk_level)}`}>
                        {getRiskText(portfolioData.risk_level)}
                      </div>
                      <div className="text-sm text-slate-400">سطح ریسک</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Performance Metrics */}
              {portfolioData.performance_metrics && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-purple-400" />
                      معیارهای عملکرد
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-400">بازدهی روزانه:</span>
                          <span className={getPerformanceColor(portfolioData.performance_metrics.daily_return)}>
                            {formatPercent(portfolioData.performance_metrics.daily_return)}
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-slate-400">بازدهی هفتگی:</span>
                          <span className={getPerformanceColor(portfolioData.performance_metrics.weekly_return)}>
                            {formatPercent(portfolioData.performance_metrics.weekly_return)}
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-slate-400">بازدهی ماهانه:</span>
                          <span className={getPerformanceColor(portfolioData.performance_metrics.monthly_return)}>
                            {formatPercent(portfolioData.performance_metrics.monthly_return)}
                          </span>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-400">نسبت شارپ:</span>
                          <span className="text-blue-400">{portfolioData.performance_metrics.sharpe_ratio?.toFixed(2)}</span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-slate-400">حداکثر افت:</span>
                          <span className="text-red-400">{formatPercent(portfolioData.performance_metrics.max_drawdown)}</span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-slate-400">نوسانات:</span>
                          <span className="text-yellow-400">{formatPercent(portfolioData.performance_metrics.volatility)}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Portfolio Allocation */}
              {portfolioData.current_allocation && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-blue-400" />
                      تخصیص فعلی پرتفوی
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(portfolioData.current_allocation).map(([asset, percentage]) => (
                        <div key={asset} className="flex justify-between items-center">
                          <span className="text-slate-300">{asset}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-slate-700 rounded-full">
                              <div 
                                className="h-full bg-blue-500 rounded-full transition-all duration-300"
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                            <span className="text-sm text-slate-400 w-12">{percentage?.toFixed(1)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Optimization Recommendations */}
              {optimizationData?.rebalancing_actions?.length > 0 && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Target className="w-5 h-5 text-emerald-400" />
                        پیشنهادات بهینه‌سازی
                      </div>
                      <Button 
                        onClick={handleOptimizePortfolio}
                        disabled={optimizing}
                        size="sm"
                        className="bg-emerald-600 hover:bg-emerald-700"
                      >
                        {optimizing ? 'در حال بهینه‌سازی...' : 'بهینه‌سازی مجدد'}
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {optimizationData.rebalancing_actions.map((action, index) => (
                        <div key={index} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2">
                              {action.action === 'buy' ? (
                                <TrendingUp className="w-4 h-4 text-green-400" />
                              ) : (
                                <TrendingDown className="w-4 h-4 text-red-400" />
                              )}
                              <span className="font-medium">{action.asset}</span>
                            </div>
                            <Badge className={`text-xs ${
                              action.priority === 'high' ? 'bg-red-600' :
                              action.priority === 'medium' ? 'bg-yellow-600' : 'bg-green-600'
                            } text-white`}>
                              {action.priority === 'high' ? 'بالا' :
                               action.priority === 'medium' ? 'متوسط' : 'پایین'}
                            </Badge>
                          </div>
                          
                          <p className="text-sm text-slate-300 mb-2">{action.reason}</p>
                          
                          <div className="text-sm text-slate-400">
                            مبلغ: {formatCurrency(action.amount_tmn)} تومان
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Risk Analysis */}
              {optimizationData?.risk_analysis && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-orange-400" />
                      تحلیل ریسک
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${getRiskColor(optimizationData.risk_analysis.risk_level)}`}>
                          {getRiskText(optimizationData.risk_analysis.risk_level)}
                        </div>
                        <div className="text-sm text-slate-400">سطح ریسک کلی</div>
                      </div>

                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">نوسانات پرتفوی:</span>
                          <span className="text-yellow-400">
                            {optimizationData.risk_analysis.portfolio_volatility_percent?.toFixed(1)}%
                          </span>
                        </div>

                        <div className="flex justify-between">
                          <span className="text-slate-400">ارزش در معرض ریسک:</span>
                          <span className="text-red-400">
                            {optimizationData.risk_analysis.value_at_risk_95_percent?.toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      {optimizationData.risk_analysis.recommendations?.length > 0 && (
                        <div className="bg-slate-800/30 rounded-lg p-3">
                          <div className="text-sm font-medium text-orange-400 mb-2">توصیه‌های ریسک:</div>
                          <ul className="space-y-1 text-xs">
                            {optimizationData.risk_analysis.recommendations.map((rec, index) => (
                              <li key={index} className="text-slate-300 flex items-start gap-2">
                                <span className="w-1 h-1 bg-orange-400 rounded-full mt-2"></span>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Expected Returns */}
              {optimizationData?.expected_returns && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-400" />
                      بازدهی مورد انتظار
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-emerald-400">
                          {optimizationData.expected_returns.portfolio_expected_return_percent?.toFixed(1)}%
                        </div>
                        <div className="text-sm text-slate-400">بازدهی سالانه مورد انتظار</div>
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">حالت خوشبینانه:</span>
                          <span className="text-green-400">
                            +{optimizationData.expected_returns.return_scenarios?.optimistic?.toFixed(1)}%
                          </span>
                        </div>

                        <div className="flex justify-between">
                          <span className="text-slate-400">حالت واقع‌بینانه:</span>
                          <span className="text-blue-400">
                            +{optimizationData.expected_returns.return_scenarios?.realistic?.toFixed(1)}%
                          </span>
                        </div>

                        <div className="flex justify-between">
                          <span className="text-slate-400">حالت بدبینانه:</span>
                          <span className="text-red-400">
                            +{optimizationData.expected_returns.return_scenarios?.pessimistic?.toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      <div className="bg-slate-800/30 rounded-lg p-3 text-xs text-slate-400">
                        بازدهی‌ها برای بازه زمانی {optimizationData.expected_returns.time_horizon} با 
                        فاصله اطمینان {optimizationData.expected_returns.confidence_interval} محاسبه شده‌اند.
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Quick Actions */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-blue-400" />
                    اقدامات سریع
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button 
                      onClick={() => navigate('/ai/recommendations')}
                      className="w-full justify-start bg-blue-600 hover:bg-blue-700"
                      size="sm"
                    >
                      <Target className="w-4 h-4 mr-2" />
                      پیشنهادات معاملاتی
                    </Button>

                    <Button 
                      onClick={() => navigate('/advanced-trade')}
                      className="w-full justify-start bg-purple-600 hover:bg-purple-700"
                      size="sm"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      معاملات پیشرفته
                    </Button>

                    <Button 
                      onClick={() => navigate('/ai/assistant')}
                      className="w-full justify-start bg-emerald-600 hover:bg-emerald-700"
                      size="sm"
                    >
                      <Brain className="w-4 h-4 mr-2" />
                      مشاوره با AI
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!portfolioData && !loading && (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-8 text-center">
              <PieChart className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">پرتفوی خالی</h3>
              <p className="text-slate-400 mb-4">
                برای شروع تحلیل، ابتدا مقداری ارز دیجیتال خریداری کنید
              </p>
              <Button 
                onClick={() => navigate('/trade')}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                شروع معامله
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PortfolioAnalysis;