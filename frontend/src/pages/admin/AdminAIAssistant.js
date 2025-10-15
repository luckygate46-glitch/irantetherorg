import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Bot, 
  Lightbulb, 
  AlertTriangle, 
  CheckCircle,
  Settings,
  Play,
  Clock,
  Shield,
  Zap,
  Database,
  RefreshCw,
  Target,
  Activity,
  TrendingUp,
  Users,
  BarChart3,
  FileText,
  Download
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminAIAssistant = ({ user, onLogout }) => {
  const [assistantData, setAssistantData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(null);
  const [actionHistory, setActionHistory] = useState([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchAssistantData();
  }, [user, navigate]);

  const fetchAssistantData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/ai/assistant`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      setAssistantData(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری داده‌های دستیار هوشمند:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات دستیار هوشمند',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const executeAction = async (actionId) => {
    try {
      setExecuting(actionId);
      const response = await axios.post(`${API}/admin/ai/execute-action`, {
        action_type: actionId,
        parameters: {}
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.data.success) {
        toast({
          title: 'عملیات موفق',
          description: response.data.result.message,
        });
        
        // Add to action history
        setActionHistory(prev => [{
          id: Date.now(),
          action: actionId,
          result: response.data.result,
          timestamp: new Date().toLocaleString('fa-IR')
        }, ...prev.slice(0, 9)]); // Keep last 10 actions

        // Refresh assistant data
        fetchAssistantData();
      } else {
        toast({
          title: 'خطا در اجرا',
          description: response.data.result.message,
          variant: 'destructive'
        });
      }
    } catch (error) {
      console.error('خطا در اجرای عملیات:', error);
      toast({
        title: 'خطا',
        description: 'خطا در اجرای عملیات',
        variant: 'destructive'
      });
    } finally {
      setExecuting(null);
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'performance': return <Zap className="w-4 h-4" />;
      case 'security': return <Shield className="w-4 h-4" />;
      case 'scalability': return <TrendingUp className="w-4 h-4" />;
      case 'monitoring': return <Activity className="w-4 h-4" />;
      case 'maintenance': return <Settings className="w-4 h-4" />;
      case 'backup': return <Database className="w-4 h-4" />;
      case 'data': return <RefreshCw className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-600 text-white';
      case 'medium': return 'bg-yellow-600 text-white';
      case 'low': return 'bg-green-600 text-white';
      default: return 'bg-slate-600 text-white';
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'very_low': return 'text-green-400';
      case 'low': return 'text-yellow-400';
      case 'medium': return 'text-orange-400';
      case 'high': return 'text-red-400';
      default: return 'text-slate-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-slate-200">بارگذاری دستیار هوشمند...</p>
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
              <Bot className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">دستیار هوشمند ادمین</h1>
              <Badge className="bg-emerald-600 text-white">
                {assistantData?.assistant_status === 'active' ? 'فعال' : 'غیرفعال'}
              </Badge>
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
            <Button onClick={fetchAssistantData} variant="outline" size="sm">
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* System Recommendations */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  توصیه‌های سیستم
                </CardTitle>
              </CardHeader>
              <CardContent>
                {assistantData?.recommendations?.length > 0 ? (
                  <div className="space-y-4">
                    {assistantData.recommendations.map((rec) => (
                      <div key={rec.id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex items-center gap-2">
                            {getCategoryIcon(rec.category)}
                            <h4 className="font-medium">{rec.title}</h4>
                          </div>
                          <div className="flex gap-2">
                            <Badge className={getPriorityColor(rec.priority)}>
                              {rec.priority === 'high' ? 'بالا' : rec.priority === 'medium' ? 'متوسط' : 'پایین'}
                            </Badge>
                            <Badge variant="outline">
                              {rec.category}
                            </Badge>
                          </div>
                        </div>
                        
                        <p className="text-sm text-slate-300 mb-3">{rec.description}</p>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 text-sm">
                          <div>
                            <span className="text-slate-200">اقدام پیشنهادی:</span>
                            <p className="text-blue-400">{rec.action}</p>
                          </div>
                          <div>
                            <span className="text-slate-200">تأثیر مورد انتظار:</span>
                            <p className="text-green-400">{rec.estimated_impact}</p>
                          </div>
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <Badge variant="outline" className="text-xs">
                            سختی: {rec.difficulty === 'high' ? 'بالا' : rec.difficulty === 'medium' ? 'متوسط' : 'پایین'}
                          </Badge>
                          <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700">
                            اجرای توصیه
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-2" />
                    <p className="text-slate-200">همه چیز عالی است! توصیه‌ای وجود ندارد.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-400" />
                  اقدامات سریع
                </CardTitle>
              </CardHeader>
              <CardContent>
                {assistantData?.quick_actions?.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {assistantData.quick_actions.map((action) => (
                      <div key={action.id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                          {getCategoryIcon(action.category)}
                          <h4 className="font-medium text-sm">{action.title}</h4>
                        </div>
                        
                        <p className="text-xs text-slate-200 mb-3">{action.description}</p>
                        
                        <div className="flex justify-between items-center mb-3 text-xs">
                          <span className="text-slate-300">زمان: {action.estimated_time}</span>
                          <span className={`font-medium ${getRiskColor(action.risk_level)}`}>
                            ریسک: {action.risk_level === 'very_low' ? 'بسیار کم' : 
                                   action.risk_level === 'low' ? 'کم' : 
                                   action.risk_level === 'medium' ? 'متوسط' : 'بالا'}
                          </span>
                        </div>
                        
                        <Button 
                          size="sm" 
                          onClick={() => executeAction(action.id)}
                          disabled={executing === action.id}
                          className="w-full bg-blue-600 hover:bg-blue-700"
                        >
                          {executing === action.id ? (
                            <>
                              <div className="animate-spin w-3 h-3 border border-white border-t-transparent rounded-full mr-2" />
                              در حال اجرا...
                            </>
                          ) : (
                            <>
                              <Play className="w-3 h-3 mr-1" />
                              اجرا
                            </>
                          )}
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                    <p className="text-slate-200">اقدام سریعی در دسترس نیست</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Alerts */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-orange-400" />
                  هشدارهای اخیر
                </CardTitle>
              </CardHeader>
              <CardContent>
                {assistantData?.recent_alerts?.length > 0 ? (
                  <div className="space-y-3">
                    {assistantData.recent_alerts.map((alert, index) => (
                      <div key={index} className="p-3 bg-slate-800/50 rounded border border-slate-700">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium">{alert.title}</span>
                          <Badge className="text-xs bg-orange-600 text-white">
                            {alert.risk_level === 'high' ? 'بالا' : 
                             alert.risk_level === 'medium' ? 'متوسط' : 'پایین'}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-200">{alert.description}</p>
                        <div className="text-xs text-slate-300 mt-2">{alert.timestamp}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
                    <p className="text-xs text-slate-200">هیچ هشدار اخیری نیست</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Action History */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-green-400" />
                  تاریخچه اقدامات
                </CardTitle>
              </CardHeader>
              <CardContent>
                {actionHistory.length > 0 ? (
                  <div className="space-y-3">
                    {actionHistory.map((action) => (
                      <div key={action.id} className="p-3 bg-slate-800/50 rounded border border-slate-700">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium">
                            {action.action === 'restart_api' ? 'راه‌اندازی مجدد API' :
                             action.action === 'clear_cache' ? 'پاک‌سازی حافظه موقت' :
                             action.action === 'backup_db' ? 'پشتیبان‌گیری پایگاه داده' :
                             action.action === 'sync_prices' ? 'همگام‌سازی قیمت‌ها' :
                             action.action}
                          </span>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        </div>
                        <p className="text-xs text-slate-200">{action.result.message}</p>
                        <div className="text-xs text-slate-300 mt-1">{action.timestamp}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <Activity className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-xs text-slate-200">هیچ اقدامی انجام نشده</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                  آمار سریع
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-200">توصیه‌های فعال</span>
                    <span className="text-purple-400">{assistantData?.recommendations?.length || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-200">اقدامات سریع</span>
                    <span className="text-blue-400">{assistantData?.quick_actions?.length || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-200">هشدارهای اخیر</span>
                    <span className="text-orange-400">{assistantData?.recent_alerts?.length || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-200">اقدامات انجام شده</span>
                    <span className="text-green-400">{actionHistory.length}</span>
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

export default AdminAIAssistant;