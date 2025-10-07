import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Target, 
  TrendingUp,
  TrendingDown,
  Activity,
  User,
  PieChart,
  DollarSign,
  Shield,
  Clock,
  Star,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Lightbulb,
  BarChart3
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserAIRecommendations = ({ user, onLogout }) => {
  const [recommendationsData, setRecommendationsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchRecommendations();
  }, [user, navigate]);

  const fetchRecommendations = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get(`${API}/user/ai/recommendations`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setRecommendationsData(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری پیشنهادات:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری پیشنهادات هوشمند',
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

  const getActionColor = (action) => {
    switch (action) {
      case 'buy':
      case 'hold_or_buy':
      case 'new_investment':
        return 'bg-green-600 text-white';
      case 'sell':
      case 'consider_selling':
        return 'bg-red-600 text-white';
      case 'hold':
        return 'bg-yellow-600 text-white';
      default:
        return 'bg-slate-600 text-white';
    }
  };

  const getActionText = (action) => {
    switch (action) {
      case 'buy':
      case 'hold_or_buy':
        return 'خرید';
      case 'sell':
      case 'consider_selling':
        return 'فروش';
      case 'hold':
        return 'نگهداری';
      case 'new_investment':
        return 'سرمایه‌گذاری جدید';
      default:
        return action;
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'buy':
      case 'hold_or_buy':
      case 'new_investment':
        return <TrendingUp className="w-4 h-4" />;
      case 'sell':
      case 'consider_selling':
        return <TrendingDown className="w-4 h-4" />;
      case 'hold':
        return <Activity className="w-4 h-4" />;
      default:
        return <Target className="w-4 h-4" />;
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'conservative':
        return 'text-green-400';
      case 'moderate':
        return 'text-yellow-400';
      case 'aggressive':
        return 'text-red-400';
      default:
        return 'text-slate-400';
    }
  };

  const getRiskText = (riskLevel) => {
    switch (riskLevel) {
      case 'conservative':
        return 'محافظه‌کارانه';
      case 'moderate':
        return 'متوسط';
      case 'aggressive':
        return 'تهاجمی';
      default:
        return riskLevel;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'bullish':
        return 'text-green-400';
      case 'bearish':
        return 'text-red-400';
      default:
        return 'text-slate-400';
    }
  };

  const getSentimentText = (sentiment) => {
    switch (sentiment) {
      case 'bullish':
        return 'صعودی';
      case 'bearish':
        return 'نزولی';
      default:
        return 'خنثی';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-400">بارگذاری پیشنهادات هوشمند...</p>
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
              <Target className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">پیشنهادات هوشمند</h1>
              {refreshing && <div className="animate-spin w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>}
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
            <Button onClick={fetchRecommendations} variant="outline" size="sm" disabled={refreshing}>
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
        {recommendationsData && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main Recommendations */}
            <div className="lg:col-span-3 space-y-6">
              {/* Market Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-blue-400" />
                      وضعیت بازار
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-xl font-bold ${getSentimentColor(recommendationsData.market_sentiment)}`}>
                      {getSentimentText(recommendationsData.market_sentiment)}
                    </div>
                    <p className="text-xs text-slate-400">تحلیل کلی بازار</p>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Shield className="w-4 h-4 text-orange-400" />
                      ریسک پرتفوی
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-xl font-bold ${getRiskColor(recommendationsData.risk_assessment?.level)}`}>
                      {recommendationsData.risk_assessment?.level === 'high' ? 'بالا' :
                       recommendationsData.risk_assessment?.level === 'medium' ? 'متوسط' : 'پایین'}
                    </div>
                    <p className="text-xs text-slate-400">
                      امتیاز: {recommendationsData.risk_assessment?.score || 0}
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <User className="w-4 h-4 text-purple-400" />
                      پروفایل ریسک
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-xl font-bold ${getRiskColor(recommendationsData.user_profile?.risk_profile)}`}>
                      {getRiskText(recommendationsData.user_profile?.risk_profile)}
                    </div>
                    <p className="text-xs text-slate-400">
                      تنوع: {recommendationsData.user_profile?.diversification_score || 0}%
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Trading Recommendations */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-400" />
                    پیشنهادات معاملاتی
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {recommendationsData.recommendations?.length > 0 ? (
                    <div className="space-y-4">
                      {recommendationsData.recommendations.map((rec, index) => (
                        <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-3">
                              <div className={`p-2 rounded-lg ${getActionColor(rec.action)}`}>
                                {getActionIcon(rec.action)}
                              </div>
                              <div>
                                <h4 className="font-semibold text-lg">{rec.crypto}</h4>
                                <Badge className={getActionColor(rec.action)}>
                                  {getActionText(rec.action)}
                                </Badge>
                              </div>
                            </div>
                            <div className="text-left">
                              <div className="text-sm text-slate-400">اطمینان</div>
                              <div className="text-lg font-bold text-emerald-400">{rec.confidence}%</div>
                            </div>
                          </div>
                          
                          <p className="text-slate-300 mb-3">{rec.reason}</p>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                            {rec.current_amount && (
                              <div className="bg-slate-800 p-2 rounded">
                                <div className="text-slate-400">مقدار فعلی</div>
                                <div className="font-medium">{formatCurrency(rec.current_amount)} ت</div>
                              </div>
                            )}
                            
                            {rec.suggested_amount && (
                              <div className="bg-slate-800 p-2 rounded">
                                <div className="text-slate-400">مقدار پیشنهادی</div>
                                <div className="font-medium">{formatCurrency(rec.suggested_amount)} ت</div>
                              </div>
                            )}
                            
                            {rec.suggested_allocation && (
                              <div className="bg-slate-800 p-2 rounded">
                                <div className="text-slate-400">درصد پیشنهادی</div>
                                <div className="font-medium">{rec.suggested_allocation}%</div>
                              </div>
                            )}
                            
                            <div className="bg-slate-800 p-2 rounded">
                              <div className="text-slate-400">بازه زمانی</div>
                              <div className="font-medium">
                                {rec.timeframe === 'short_term' ? 'کوتاه مدت' :
                                 rec.timeframe === 'medium_term' ? 'میان مدت' : 'بلند مدت'}
                              </div>
                            </div>
                            
                            <div className="bg-slate-800 p-2 rounded">
                              <div className="text-slate-400">سطح ریسک</div>
                              <div className={`font-medium ${getRiskColor(rec.risk_level)}`}>
                                {getRiskText(rec.risk_level)}
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex gap-2 mt-4">
                            <Button 
                              size="sm" 
                              className="bg-emerald-600 hover:bg-emerald-700"
                              onClick={() => navigate('/trade')}
                            >
                              اجرای معامله
                            </Button>
                            <Button size="sm" variant="outline">
                              جزئیات بیشتر
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Target className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                      <p className="text-slate-400">در حال حاضر پیشنهادی وجود ندارد</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* User Profile Summary */}
              {recommendationsData.user_profile && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5 text-purple-400" />
                      پروفایل شما
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">ارزش پرتفوی</span>
                        <span className="text-emerald-400">
                          {formatCurrency(recommendationsData.user_profile.portfolio_value)} ت
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">پروفایل ریسک</span>
                        <span className={getRiskColor(recommendationsData.user_profile.risk_profile)}>
                          {getRiskText(recommendationsData.user_profile.risk_profile)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">تنوع پرتفوی</span>
                        <span className={`${
                          recommendationsData.user_profile.diversification_score > 70 ? 'text-green-400' :
                          recommendationsData.user_profile.diversification_score > 40 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {recommendationsData.user_profile.diversification_score}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">تجربه معاملاتی</span>
                        <span className="text-blue-400">
                          {recommendationsData.user_profile.trading_experience === 'beginner' ? 'مبتدی' :
                           recommendationsData.user_profile.trading_experience === 'intermediate' ? 'متوسط' : 'پیشرفته'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">هدف سرمایه‌گذاری</span>
                        <span className="text-purple-400">
                          {recommendationsData.user_profile.investment_goals === 'growth' ? 'رشد' :
                           recommendationsData.user_profile.investment_goals === 'income' ? 'درآمد' : 'حفظ سرمایه'}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Risk Assessment */}
              {recommendationsData.risk_assessment && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-orange-400" />
                      ارزیابی ریسک
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${
                          recommendationsData.risk_assessment.level === 'high' ? 'text-red-400' :
                          recommendationsData.risk_assessment.level === 'medium' ? 'text-yellow-400' :
                          'text-green-400'
                        }`}>
                          {recommendationsData.risk_assessment.level === 'high' ? 'بالا' :
                           recommendationsData.risk_assessment.level === 'medium' ? 'متوسط' : 'پایین'}
                        </div>
                        <div className="text-sm text-slate-400">سطح ریسک کلی</div>
                      </div>
                      
                      <div className="w-full bg-slate-800 rounded-full h-3">
                        <div 
                          className={`h-3 rounded-full transition-all duration-300 ${
                            recommendationsData.risk_assessment.level === 'high' ? 'bg-red-500' :
                            recommendationsData.risk_assessment.level === 'medium' ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(100, recommendationsData.risk_assessment.score)}%` }}
                        />
                      </div>
                      
                      {recommendationsData.risk_assessment.factors?.length > 0 && (
                        <div>
                          <div className="text-sm font-medium text-slate-300 mb-2">عوامل ریسک:</div>
                          <ul className="space-y-1">
                            {recommendationsData.risk_assessment.factors.map((factor, index) => (
                              <li key={index} className="text-xs text-orange-400 flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" />
                                {factor}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Quick Actions */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-400" />
                    اقدامات سریع
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Button 
                      onClick={() => navigate('/ai/portfolio-analysis')}
                      className="w-full justify-start bg-blue-600 hover:bg-blue-700"
                      size="sm"
                    >
                      <PieChart className="w-4 h-4 mr-2" />
                      تحلیل پرتفوی
                    </Button>
                    <Button 
                      onClick={() => navigate('/ai/market-insights')}
                      className="w-full justify-start bg-purple-600 hover:bg-purple-700"
                      size="sm"
                    >
                      <BarChart3 className="w-4 h-4 mr-2" />
                      تحلیل بازار
                    </Button>
                    <Button 
                      onClick={() => navigate('/trade')}
                      className="w-full justify-start bg-emerald-600 hover:bg-emerald-700"
                      size="sm"
                    >
                      <DollarSign className="w-4 h-4 mr-2" />
                      شروع معامله
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Last Update */}
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-400" />
                    آخرین به‌روزرسانی
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-slate-300">
                    {recommendationsData.generated_at && 
                      new Date(recommendationsData.generated_at).toLocaleString('fa-IR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })
                    }
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    پیشنهادات بر اساس آخرین داده‌های بازار
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserAIRecommendations;