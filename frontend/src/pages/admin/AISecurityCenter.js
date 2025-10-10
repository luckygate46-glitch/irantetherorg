import React, { useState, useEffect } from 'react';
import AdminLayout from '../../layouts/AdminLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import {
  Shield, AlertTriangle, Eye, Lock, Fingerprint, Globe, Smartphone,
  Users, Activity, Zap, Target, Database, Search, Filter, RefreshCw
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AISecurityCenter = ({ user, onLogout }) => {
  const [securityMetrics, setSecurityMetrics] = useState({});
  const [fraudAlerts, setFraudAlerts] = useState([]);
  const [suspiciousActivities, setSuspiciousActivities] = useState([]);
  const [threatIntelligence, setThreatIntelligence] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 15000); // Update every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch real AI security data from backend
      const response = await axios.get(`${API}/admin/ai/security-center`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = response.data;
      
      // Set metrics from backend
      setSecurityMetrics({
        threatsBlocked: data.security_metrics.threats_blocked,
        fraudDetected: data.security_metrics.fraud_detected,
        suspiciousLogins: data.security_metrics.suspicious_logins,
        amlViolations: data.security_metrics.aml_violations,
        riskScore: data.security_metrics.risk_score,
        falsePositives: data.security_metrics.false_positives,
        responseTime: data.security_metrics.response_time,
        confidenceLevel: data.security_metrics.confidence_level
      });

      // Set fraud alerts from backend
      setFraudAlerts(data.fraud_alerts || []);

      // Keep suspicious activities as mock for now (can be added to backend later)
      setSuspiciousActivities([]);

      // Set threat intelligence from backend
      setThreatIntelligence({
        globalThreats: data.threat_intelligence.global_threats,
        iranianThreats: data.threat_intelligence.iranian_threats,
        blockedIPs: data.threat_intelligence.blocked_ips,
        maliciousTransactions: data.threat_intelligence.malicious_transactions,
        phishingAttempts: data.threat_intelligence.phishing_attempts,
        ddosAttempts: data.threat_intelligence.ddos_attempts
      });

    } catch (error) {
      console.error('Error fetching security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-600';
      case 'high': return 'bg-orange-600';
      case 'medium': return 'bg-yellow-600';
      case 'low': return 'bg-blue-600';
      default: return 'bg-gray-600';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'investigating': return 'bg-red-600';
      case 'pending_review': return 'bg-yellow-600';
      case 'auto_resolved': return 'bg-green-600';
      default: return 'bg-gray-600';
    }
  };

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const filteredAlerts = fraudAlerts.filter(alert => {
    if (activeFilter === 'all') return true;
    return alert.type === activeFilter;
  });

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="ai-security">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="ai-security">
      <div className="space-y-6" dir="rtl">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Shield className="w-8 h-8 text-red-500" />
              مرکز امنیت هوش مصنوعی
            </h1>
            <p className="text-slate-400 mt-2">تشخیص تقلب و مراقبت پیشرفته</p>
          </div>
          <Button onClick={fetchSecurityData} variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            بروزرسانی
          </Button>
        </div>

        {/* Security Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-red-900/50 to-pink-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-red-400" />
                تهدیدات مسدود شده
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {securityMetrics.threatsBlocked}
              </div>
              <p className="text-red-300 text-sm">امروز</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-900/50 to-red-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-400" />
                تقلب شناسایی شده
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {securityMetrics.fraudDetected}
              </div>
              <p className="text-orange-300 text-sm">نیاز به بررسی</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-900/50 to-orange-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Eye className="w-5 h-5 text-yellow-400" />
                ورود مشکوک
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {securityMetrics.suspiciousLogins}
              </div>
              <p className="text-yellow-300 text-sm">۲۴ ساعت گذشته</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-green-400" />
                سطح اعتماد AI
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {securityMetrics.confidenceLevel}%
              </div>
              <p className="text-green-300 text-sm">دقت تشخیص</p>
            </CardContent>
          </Card>
        </div>

        {/* Fraud Alert Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Filter className="w-5 h-5" />
              فیلتر هشدارهای تقلب
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 flex-wrap">
              {[
                { id: 'all', label: 'همه موارد' },
                { id: 'money_laundering', label: 'پولشویی' },
                { id: 'identity_theft', label: 'سرقت هویت' },
                { id: 'trading_manipulation', label: 'دستکاری معاملات' }
              ].map(filter => (
                <Button
                  key={filter.id}
                  variant={activeFilter === filter.id ? "default" : "outline"}
                  onClick={() => setActiveFilter(filter.id)}
                  className="text-sm"
                >
                  {filter.label}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Fraud Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              هشدارهای تقلب فعال
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredAlerts.map(alert => (
                <div key={alert.id} className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-white font-medium">{alert.title}</h3>
                      <p className="text-gray-400 text-sm">{alert.description}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity === 'critical' ? 'بحرانی' :
                         alert.severity === 'high' ? 'بالا' :
                         alert.severity === 'medium' ? 'متوسط' : 'پایین'}
                      </Badge>
                      <Badge className={getStatusColor(alert.status)}>
                        {alert.status === 'investigating' ? 'در حال بررسی' :
                         alert.status === 'pending_review' ? 'منتظر بررسی' : 'حل شده'}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-gray-400 text-xs">شناسه کاربر</p>
                      <p className="text-white text-sm">{alert.userId}</p>
                    </div>
                    {alert.amount && (
                      <div>
                        <p className="text-gray-400 text-xs">مبلغ</p>
                        <p className="text-white text-sm">{alert.amount.toLocaleString('fa-IR')} تومان</p>
                      </div>
                    )}
                    <div>
                      <p className="text-gray-400 text-xs">سطح اعتماد</p>
                      <p className="text-white text-sm">{alert.confidence}%</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">زمان تشخیص</p>
                      <p className="text-white text-sm">
                        {new Date(alert.timestamp).toLocaleTimeString('fa-IR')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      {alert.aiTags.map(tag => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" className="bg-red-600 hover:bg-red-700">
                        بررسی فوری
                      </Button>
                      <Button size="sm" variant="outline">
                        ارسال به تیم امنیت
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Threat Intelligence & Suspicious Activities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Threat Intelligence */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-500" />
                هوش تهدیدات
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">تهدیدات جهانی</p>
                  <p className="text-white font-bold text-lg">{threatIntelligence.globalThreats}</p>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">تهدیدات ایرانی</p>
                  <p className="text-white font-bold text-lg">{threatIntelligence.iranianThreats}</p>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">IP های مسدود</p>
                  <p className="text-red-400 font-bold text-lg">{threatIntelligence.blockedIPs}</p>
                </div>
                <div className="bg-slate-800 rounded p-3">
                  <p className="text-gray-400 text-sm">حملات فیشینگ</p>
                  <p className="text-orange-400 font-bold text-lg">{threatIntelligence.phishingAttempts}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Suspicious Activities */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-yellow-500" />
                فعالیت‌های مشکوک
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {suspiciousActivities.map(activity => (
                  <div key={activity.id} className="bg-slate-800 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium text-sm">{activity.user}</h4>
                      <Badge className={getRiskLevelColor(activity.riskLevel)}>
                        {activity.riskLevel === 'high' ? 'پرخطر' :
                         activity.riskLevel === 'medium' ? 'متوسط' : 'کم خطر'}
                      </Badge>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{activity.activity}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>IP: {activity.ip} | {activity.location}</span>
                      <span>{new Date(activity.timestamp).toLocaleTimeString('fa-IR')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Model Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-purple-500" />
              وضعیت مدل‌های امنیتی AI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-r from-red-900/50 to-pink-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">مدل تشخیص تقلب</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-red-400">97.8%</span>
                  <Badge className="bg-green-600">فعال</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">آخرین آموزش: دیروز</p>
              </div>
              
              <div className="bg-gradient-to-r from-orange-900/50 to-red-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">مدل تحلیل رفتاری</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-orange-400">94.2%</span>
                  <Badge className="bg-green-600">فعال</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">آخرین آموزش: 3 روز پیش</p>
              </div>
              
              <div className="bg-gradient-to-r from-blue-900/50 to-purple-800/50 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">مدل تشخیص هویت</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-blue-400">96.1%</span>
                  <Badge className="bg-green-600">فعال</Badge>
                </div>
                <p className="text-gray-400 text-sm mt-2">آخرین آموزش: 1 هفته پیش</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default AISecurityCenter;