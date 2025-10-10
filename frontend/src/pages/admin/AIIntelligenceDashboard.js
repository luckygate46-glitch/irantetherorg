import React, { useState, useEffect } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import {
  Brain, TrendingUp, Shield, Users, AlertTriangle, Eye, BarChart3, 
  Activity, Zap, Target, Cpu, Database, Globe, Smartphone, RefreshCw
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIIntelligenceDashboard = ({ user, onLogout }) => {
  const [aiMetrics, setAiMetrics] = useState({});
  const [realTimeAlerts, setRealTimeAlerts] = useState([]);
  const [marketIntelligence, setMarketIntelligence] = useState({});
  const [systemHealth, setSystemHealth] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAIData();
    const interval = setInterval(fetchAIData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAIData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch real AI intelligence dashboard data from backend
      const response = await axios.get(`${API}/admin/ai/intelligence-dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = response.data;
      
      // Set metrics from backend
      setAiMetrics({
        fraudDetectionAccuracy: data.metrics.fraud_detection_accuracy,
        riskScoreAverage: data.metrics.risk_score_average,
        automatedDecisions: data.metrics.automated_decisions,
        mlModelPerformance: data.metrics.ml_model_performance,
        predictiveAccuracy: data.metrics.predictive_accuracy,
        alertsGenerated: data.metrics.alerts_generated,
        threatsBlocked: data.metrics.threats_blocked,
        complianceScore: data.metrics.compliance_score
      });

      // Set real-time alerts
      setRealTimeAlerts(data.real_time_alerts || []);

      // Set market intelligence
      setMarketIntelligence({
        bitcoinTrend: data.market_intelligence.bitcoin_trend,
        marketSentiment: data.market_intelligence.market_sentiment,
        volumePrediction: data.market_intelligence.volume_prediction,
        priceVolatility: data.market_intelligence.price_volatility,
        iranianMarketHealth: data.market_intelligence.iranian_market_health,
        liquidityScore: data.market_intelligence.liquidity_score,
        tradingPatterns: data.market_intelligence.trading_patterns
      });

      // Set system health
      setSystemHealth({
        overallHealth: data.system_health.overall_health,
        apiResponseTime: data.system_health.api_response_time,
        databasePerformance: data.system_health.database_performance,
        serverLoad: data.system_health.server_load,
        memoryUsage: data.system_health.memory_usage,
        diskSpace: data.system_health.disk_space,
        networkLatency: data.system_health.network_latency,
        errorRate: data.system_health.error_rate
      });

    } catch (error) {
      console.error('Error fetching AI data:', error);
      // Keep existing data on error, don't clear it
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-600';
      case 'medium': return 'bg-yellow-600';
      case 'low': return 'bg-blue-600';
      default: return 'bg-gray-600';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'security': return Shield;
      case 'fraud': return AlertTriangle;
      case 'compliance': return Users;
      default: return Eye;
    }
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="ai-intelligence">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="ai-intelligence">
      <div className="space-y-6" dir="rtl">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Brain className="w-8 h-8 text-blue-500" />
              داشبورد هوش مصنوعی
            </h1>
            <p className="text-slate-400 mt-2">مرکز کنترل هوشمند و تحلیل پیشرفته</p>
          </div>
          <Button onClick={fetchAIData} variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            بروزرسانی داده‌ها
          </Button>
        </div>

        {/* AI Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-900/50 to-purple-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-blue-400" />
                دقت تشخیص تقلب
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {aiMetrics.fraudDetectionAccuracy}%
              </div>
              <p className="text-blue-300 text-sm">دقت مدل AI</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-green-400" />
                تصمیمات خودکار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {aiMetrics.automatedDecisions?.toLocaleString('fa-IR')}
              </div>
              <p className="text-green-300 text-sm">امروز</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-900/50 to-red-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-400" />
                هشدارهای فعال
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {aiMetrics.alertsGenerated}
              </div>
              <p className="text-orange-300 text-sm">نیاز به بررسی</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-900/50 to-pink-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-400" />
                عملکرد ML
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {aiMetrics.mlModelPerformance}%
              </div>
              <p className="text-purple-300 text-sm">مدل‌های فعال</p>
            </CardContent>
          </Card>
        </div>

        {/* Real-Time AI Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Eye className="w-5 h-5 text-red-500" />
              هشدارهای هوش مصنوعی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {realTimeAlerts.map(alert => {
                const Icon = getTypeIcon(alert.type);
                return (
                  <div key={alert.id} className="bg-slate-800 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <Icon className="w-5 h-5 text-white" />
                        <div>
                          <h3 className="text-white font-medium">{alert.title}</h3>
                          <p className="text-gray-400 text-sm">{alert.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity === 'high' || alert.severity === 'critical' ? 'بالا' : 
                           alert.severity === 'medium' ? 'متوسط' : 'پایین'}
                        </Badge>
                        <Badge variant="outline" className="text-green-400 border-green-400">
                          اعتماد AI: {alert.ai_confidence || alert.aiConfidence}%
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{new Date(alert.timestamp).toLocaleString('fa-IR')}</span>
                      <div className="flex gap-2">
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                          بررسی
                        </Button>
                        <Button size="sm" variant="outline">
                          نادیده گیری
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Market Intelligence & System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Market Intelligence */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-500" />
                هوش بازار
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">روند بیت کوین</p>
                  <p className="text-white font-medium">{marketIntelligence.bitcoinTrend}</p>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">حال و هوای بازار</p>
                  <p className="text-white font-medium">{marketIntelligence.marketSentiment}</p>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">پیش‌بینی حجم</p>
                  <p className="text-green-400 font-medium">{marketIntelligence.volumePrediction}</p>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">سلامت بازار ایران</p>
                  <p className="text-white font-medium">{marketIntelligence.iranianMarketHealth}%</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-500" />
                سلامت سیستم AI
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">سلامت کلی</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-slate-700 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{width: `${systemHealth.overallHealth}%`}}
                      />
                    </div>
                    <span className="text-white text-sm">{systemHealth.overallHealth}%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">زمان پاسخ API</span>
                  <span className="text-white">{systemHealth.apiResponseTime}ms</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">عملکرد پایگاه داده</span>
                  <span className="text-white">{systemHealth.databasePerformance}%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">بار سرور</span>
                  <span className="text-white">{systemHealth.serverLoad}%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">نرخ خطا</span>
                  <span className="text-green-400">{systemHealth.errorRate}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Model Performance Grid */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-500" />
              عملکرد مدل‌های هوش مصنوعی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-r from-blue-900/50 to-blue-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">تشخیص تقلب</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-blue-400">97.8%</span>
                  <Badge className="bg-green-600">فعال</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">آخرین بروزرسانی: 2 ساعت پیش</p>
              </div>
              
              <div className="bg-gradient-to-r from-green-900/50 to-green-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">پیش‌بینی قیمت</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-green-400">91.5%</span>
                  <Badge className="bg-green-600">فعال</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">آخرین بروزرسانی: 1 ساعت پیش</p>
              </div>
              
              <div className="bg-gradient-to-r from-purple-900/50 to-purple-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">تحلیل رفتار</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-purple-400">94.2%</span>
                  <Badge className="bg-green-600">فعال</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">آخرین بروزرسانی: 30 دقیقه پیش</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default AIIntelligenceDashboard;