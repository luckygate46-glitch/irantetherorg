import React, { useState, useEffect } from 'react';
import AdminLayout from '@/layouts/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import {
  Users, TrendingUp, UserCheck, UserX, Brain, Target, 
  Activity, BarChart3, PieChart, Clock, Star, AlertCircle, RefreshCw
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIUserAnalytics = ({ user, onLogout }) => {
  const [userMetrics, setUserMetrics] = useState({});
  const [userSegments, setUserSegments] = useState([]);
  const [riskScores, setRiskScores] = useState([]);
  const [behaviorInsights, setBehaviorInsights] = useState([]);
  const [churnPredictions, setChurnPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserAnalytics();
    const interval = setInterval(fetchUserAnalytics, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchUserAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch real AI user analytics data from backend
      const response = await axios.get(`${API}/admin/ai/user-analytics`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = response.data;
      
      // Set metrics from backend
      setUserMetrics({
        totalUsers: data.analytics_metrics.total_users,
        activeUsers: data.analytics_metrics.active_users,
        newUsersToday: data.analytics_metrics.new_users_today,
        highValueUsers: data.analytics_metrics.high_value_users,
        averageRiskScore: data.analytics_metrics.average_risk_score,
        churnRate: data.analytics_metrics.churn_rate,
        lifetimeValue: data.analytics_metrics.lifetime_value,
        engagementScore: data.analytics_metrics.engagement_score
      });

      // Set user segments from backend
      setUserSegments(data.user_segments || []);

      // Set risk scores (keep empty for now, can be extended later)
      setRiskScores([]);

      // Set behavior insights from backend
      setBehaviorInsights(data.behavior_insights || []);

      // Set churn predictions from backend
      setChurnPredictions(data.churn_predictions || []);

    } catch (error) {
      console.error('Error fetching user analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return 'text-red-400 bg-red-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'low': return 'text-green-400 bg-green-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return 'bg-red-600';
      case 'medium': return 'bg-yellow-600';
      case 'low': return 'bg-blue-600';
      default: return 'bg-gray-600';
    }
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="ai-user-analytics">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="ai-user-analytics">
      <div className="space-y-6" dir="rtl">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-500" />
              تحلیل هوشمند کاربران
            </h1>
            <p className="text-slate-400 mt-2">درک عمیق رفتار و الگوهای کاربران</p>
          </div>
          <Button onClick={fetchUserAnalytics} variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            بروزرسانی
          </Button>
        </div>

        {/* User Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-900/50 to-purple-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-400" />
                کل کاربران
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {userMetrics.totalUsers?.toLocaleString('fa-IR')}
              </div>
              <p className="text-blue-300 text-sm">ثبت نام شده</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-400" />
                کاربران فعال
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {userMetrics.activeUsers?.toLocaleString('fa-IR')}
              </div>
              <p className="text-green-300 text-sm">۳۰ روز گذشته</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-900/50 to-red-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-orange-400" />
                کاربران جدید
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {userMetrics.newUsersToday}
              </div>
              <p className="text-orange-300 text-sm">امروز</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-900/50 to-pink-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Star className="w-5 h-5 text-purple-400" />
                ارزش متوسط کاربر
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {userMetrics.lifetimeValue?.toLocaleString('fa-IR')}
              </div>
              <p className="text-purple-300 text-sm">تومان</p>
            </CardContent>
          </Card>
        </div>

        {/* User Segmentation */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <PieChart className="w-5 h-5 text-green-500" />
              بخش‌بندی هوشمند کاربران
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {userSegments.map(segment => (
                <div key={segment.id} className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-white font-medium">{segment.name}</h3>
                    <Badge className={segment.growthRate.startsWith('+') ? 'bg-green-600' : 'bg-red-600'}>
                      {segment.growthRate}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 mb-3">
                    <div>
                      <p className="text-gray-400 text-xs">تعداد کاربران</p>
                      <p className="text-white font-medium">{segment.users.toLocaleString('fa-IR')}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">حجم متوسط</p>
                      <p className="text-white font-medium">{segment.avgVolume.toLocaleString('fa-IR')} تومان</p>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <Badge className={getRiskColor(segment.riskLevel)}>
                      ریسک {segment.riskLevel === 'high' ? 'بالا' : segment.riskLevel === 'medium' ? 'متوسط' : 'کم'}
                    </Badge>
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {segment.characteristics.map(char => (
                      <Badge key={char} variant="outline" className="text-xs">
                        {char}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Risk Scores & Behavioral Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Scores */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-red-500" />
                نمرات ریسک کاربران
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {riskScores.map(score => (
                  <div key={score.userId} className="bg-slate-800 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{score.name}</h4>
                      <Badge className={getRiskColor(score.riskLevel)}>
                        {score.riskScore}/10
                      </Badge>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{score.reason}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>اعتماد AI: {score.confidence}%</span>
                      <span>آخرین فعالیت: {new Date(score.lastActivity).toLocaleTimeString('fa-IR')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Behavioral Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-500" />
                بینش‌های رفتاری
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {behaviorInsights.map(insight => (
                  <div key={insight.id} className="bg-slate-800 rounded-lg p-3">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-white font-medium text-sm">{insight.insight}</h4>
                      <Badge className={getImpactColor(insight.impact)}>
                        {insight.impact === 'high' ? 'بالا' : insight.impact === 'medium' ? 'متوسط' : 'کم'}
                      </Badge>
                    </div>
                    <p className="text-blue-400 text-xs mb-2">دسته: {insight.category}</p>
                    <p className="text-gray-400 text-sm">{insight.recommendation}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Churn Predictions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              پیش‌بینی ترک کاربران
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {churnPredictions.map(prediction => (
                <div key={prediction.userId} className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-white font-medium">{prediction.name}</h3>
                      <p className="text-gray-400 text-sm">{prediction.reason}</p>
                    </div>
                    <div className="text-left">
                      <p className="text-red-400 font-bold text-lg">{prediction.churnProbability}%</p>
                      <p className="text-gray-400 text-xs">{prediction.daysToChurn} روز</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <p className="text-blue-400 text-sm">{prediction.suggestedAction}</p>
                    <div className="flex gap-2">
                      <Button size="sm" className="bg-green-600 hover:bg-green-700">
                        اقدام فوری
                      </Button>
                      <Button size="sm" variant="outline">
                        برنامه‌ریزی
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* User Engagement Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              روند مشارکت کاربران
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-blue-900/50 to-blue-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">نرخ مشارکت</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-blue-400">{userMetrics.engagementScore}%</span>
                  <Badge className="bg-green-600">+5.2%</Badge>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-red-900/50 to-red-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">نرخ ترک</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-red-400">{userMetrics.churnRate}%</span>
                  <Badge className="bg-red-600">-2.1%</Badge>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-green-900/50 to-green-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">کاربران پرارزش</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-green-400">{userMetrics.highValueUsers}</span>
                  <Badge className="bg-green-600">+8.7%</Badge>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-900/50 to-purple-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">نمره ریسک متوسط</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-purple-400">{userMetrics.averageRiskScore}</span>
                  <Badge className="bg-yellow-600">-0.3</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default AIUserAnalytics;