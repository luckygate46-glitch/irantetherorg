import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Shield, 
  AlertTriangle, 
  User, 
  TrendingUp,
  Eye,
  Ban,
  CheckCircle,
  XCircle,
  Activity,
  Clock,
  BarChart3,
  Users,
  Search,
  Filter
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminFraudDetection = ({ user, onLogout }) => {
  const [fraudData, setFraudData] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchFraudData();
  }, [user, navigate]);

  const fetchFraudData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/ai/fraud-detection`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setFraudData(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌های تشخیص کلاهبرداری:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات تشخیص کلاهبرداری',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const analyzeUser = async (userId) => {
    try {
      setAnalyzing(true);
      const response = await axios.post(`${API}/admin/ai/analyze-user/${userId}`, {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setSelectedUser(response.data);
      toast({
        title: 'تحلیل کامل شد',
        description: 'تحلیل کاربر با موفقیت انجام شد',
      });
    } catch (error) {
      console.error('خطا در تحلیل کاربر:', error);
      toast({
        title: 'خطا',
        description: 'خطا در تحلیل کاربر',
        variant: 'destructive'
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return 'bg-red-600 text-white';
      case 'medium': return 'bg-yellow-600 text-white';
      case 'low': return 'bg-green-600 text-white';
      default: return 'bg-slate-600 text-white';
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'high': return <XCircle className="w-4 h-4" />;
      case 'medium': return <AlertTriangle className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-200">بارگذاری سیستم تشخیص کلاهبرداری...</p>
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
              <Shield className="w-8 h-8 text-red-400" />
              <h1 className="text-2xl font-bold text-emerald-400">سیستم تشخیص کلاهبرداری</h1>
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
        {/* Summary Cards */}
        {fraudData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  کاربران پرخطر
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-400">
                  {fraudData.risk_summary?.high_risk_count || 0}
                </div>
                <p className="text-xs text-slate-200">نیاز به بررسی فوری</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Eye className="w-4 h-4 text-yellow-400" />
                  کاربران متوسط
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-400">
                  {fraudData.risk_summary?.medium_risk_count || 0}
                </div>
                <p className="text-xs text-slate-200">نظارت دقیق‌تر</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  کاربران ایمن
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-400">
                  {fraudData.risk_summary?.low_risk_count || 0}
                </div>
                <p className="text-xs text-slate-200">وضعیت عادی</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-purple-400" />
                  کل حوادث
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-400">
                  {fraudData.fraud_patterns?.total_incidents || 0}
                </div>
                <p className="text-xs text-slate-200">در 24 ساعت گذشته</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* High Risk Users */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-red-400" />
                کاربران پرخطر
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {fraudData?.high_risk_users?.length > 0 ? (
                  fraudData.high_risk_users.map((user, index) => (
                    <div key={index} className="p-4 bg-slate-800/50 rounded-lg border-l-4 border-red-500">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium">{user.full_name || user.email}</div>
                          <div className="text-sm text-slate-200">{user.email}</div>
                        </div>
                        <Badge className={getRiskColor(user.risk_analysis.risk_level)}>
                          {getRiskIcon(user.risk_analysis.risk_level)}
                          <span className="mr-1">
                            {user.risk_analysis.risk_level === 'high' ? 'بالا' : 
                             user.risk_analysis.risk_level === 'medium' ? 'متوسط' : 'پایین'}
                          </span>
                        </Badge>
                      </div>
                      
                      <div className="text-sm text-slate-300 mb-3">
                        امتیاز ریسک: {Math.round(user.risk_analysis.risk_score * 100)}%
                      </div>
                      
                      {user.risk_analysis.risk_factors?.length > 0 && (
                        <div className="mb-3">
                          <div className="text-xs text-slate-200 mb-1">عوامل ریسک:</div>
                          <ul className="text-xs space-y-1">
                            {user.risk_analysis.risk_factors.map((factor, i) => (
                              <li key={i} className="text-yellow-400 flex items-center gap-1">
                                <span className="w-1 h-1 bg-yellow-400 rounded-full"></span>
                                {factor}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => analyzeUser(user.user_id)}
                          disabled={analyzing}
                        >
                          {analyzing ? 'در حال تحلیل...' : 'تحلیل دقیق'}
                        </Button>
                        <Button size="sm" variant="destructive">
                          اقدام فوری
                        </Button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <Shield className="w-12 h-12 text-green-400 mx-auto mb-2" />
                    <p className="text-slate-200">کاربر پرخطری شناسایی نشده</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Fraud Patterns */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                الگوهای کلاهبرداری
              </CardTitle>
            </CardHeader>
            <CardContent>
              {fraudData?.fraud_patterns ? (
                <div className="space-y-4">
                  <div className="text-center mb-4">
                    <div className="text-3xl font-bold text-purple-400 mb-1">
                      {fraudData.fraud_patterns.overall_risk_score}%
                    </div>
                    <div className="text-sm text-slate-200">امتیاز ریسک کلی سیستم</div>
                  </div>

                  {Object.entries(fraudData.fraud_patterns.patterns || {}).map(([key, pattern]) => (
                    <div key={key} className="p-3 bg-slate-800/50 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="font-medium text-sm">{pattern.name}</h4>
                        <Badge className="bg-slate-700 text-white text-xs">
                          {pattern.detected_count} مورد
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-200 mb-2">{pattern.description}</p>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-300">{pattern.affected_users} کاربر</span>
                        <span className={`font-medium ${
                          pattern.risk_score > 0.7 ? 'text-red-400' : 
                          pattern.risk_score > 0.5 ? 'text-yellow-400' : 'text-green-400'
                        }`}>
                          {Math.round(pattern.risk_score * 100)}% ریسک
                        </span>
                      </div>
                    </div>
                  ))}

                  {fraudData.fraud_patterns.recommendations && (
                    <div className="mt-6 p-3 bg-blue-900/20 border border-blue-800 rounded-lg">
                      <h4 className="font-medium text-blue-400 mb-2 text-sm">توصیه‌های امنیتی</h4>
                      <ul className="space-y-1">
                        {fraudData.fraud_patterns.recommendations.map((rec, index) => (
                          <li key={index} className="text-xs text-blue-300 flex items-center gap-2">
                            <span className="w-1 h-1 bg-blue-400 rounded-full"></span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                  <p className="text-slate-200">در حال تحلیل الگوهای کلاهبرداری...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* User Analysis Modal */}
        {selectedUser && (
          <Card className="bg-slate-900 border-slate-800 mt-6">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <User className="w-5 h-5 text-blue-400" />
                  تحلیل دقیق کاربر
                </span>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setSelectedUser(null)}
                >
                  ✕
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-medium mb-2">اطلاعات کلی</h4>
                  <div className="space-y-2 text-sm">
                    <div>کاربر: {selectedUser.user_id}</div>
                    <div>امتیاز ریسک: {Math.round(selectedUser.risk_score * 100)}%</div>
                    <div>سطح خطر: 
                      <Badge className={`mr-2 ${getRiskColor(selectedUser.risk_level)}`}>
                        {selectedUser.risk_level === 'high' ? 'بالا' : 
                         selectedUser.risk_level === 'medium' ? 'متوسط' : 'پایین'}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">عوامل ریسک</h4>
                  <ul className="space-y-1 text-sm">
                    {selectedUser.risk_factors?.map((factor, index) => (
                      <li key={index} className="text-yellow-400 flex items-center gap-2">
                        <AlertTriangle className="w-3 h-3" />
                        {factor}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium mb-2">توصیه‌های اقدام</h4>
                  <ul className="space-y-1 text-sm">
                    {selectedUser.recommendations?.map((rec, index) => (
                      <li key={index} className="text-blue-400 flex items-center gap-2">
                        <CheckCircle className="w-3 h-3" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default AdminFraudDetection;