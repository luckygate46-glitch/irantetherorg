import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AdminLayout from '../../components/AdminLayout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminAICenter({ user, onLogout }) {
  const [activeFeature, setActiveFeature] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [listening, setListening] = useState(false);

  // Feature categories with icons
  const features = {
    overview: { name: 'نمای کلی', icon: '📊', category: 'main' },
    
    // Security & Fraud
    fraud: { name: 'تشخیص تقلب', icon: '🔒', category: 'security' },
    anomaly: { name: 'تشخیص ناهنجاری', icon: '⚠️', category: 'security' },
    risk: { name: 'امتیاز ریسک', icon: '🎯', category: 'security' },
    transaction: { name: 'نظارت تراکنش‌ها', icon: '👁️', category: 'security' },
    
    // Analytics
    users: { name: 'تحلیل کاربران', icon: '👥', category: 'analytics' },
    manipulation: { name: 'دستکاری بازار', icon: '📈', category: 'analytics' },
    revenue: { name: 'بهینه‌سازی درآمد', icon: '💰', category: 'analytics' },
    intent: { name: 'تحلیل قصد کاربر', icon: '🎭', category: 'analytics' },
    
    // Market Intelligence
    price: { name: 'ناهنجاری قیمت', icon: '💹', category: 'market' },
    sentiment: { name: 'تحلیل احساسات', icon: '😊', category: 'market' },
    
    // Automation
    kyc: { name: 'تایید خودکار KYC', icon: '✅', category: 'automation' },
    support: { name: 'تریاژ پشتیبانی', icon: '🎫', category: 'automation' },
    notifications: { name: 'اعلان‌های هوشمند', icon: '🔔', category: 'automation' },
    
    // Business Intelligence
    conversion: { name: 'بهینه‌سازی تبدیل', icon: '📊', category: 'business' },
    search: { name: 'جستجوی هوشمند', icon: '🔍', category: 'business' },
    recommendations: { name: 'پیشنهادات هوشمند', icon: '💡', category: 'business' },
    crisis: { name: 'مدیریت بحران', icon: '🚨', category: 'business' },
  };

  const categories = {
    main: { name: 'اصلی', color: 'emerald' },
    security: { name: 'امنیت و تقلب', color: 'red' },
    analytics: { name: 'تحلیل و گزارش', color: 'blue' },
    market: { name: 'اطلاعات بازار', color: 'purple' },
    automation: { name: 'اتوماسیون', color: 'green' },
    business: { name: 'هوش تجاری', color: 'orange' },
  };

  useEffect(() => {
    fetchData();
  }, [activeFeature]);

  // Voice Command Setup
  useEffect(() => {
    if (voiceEnabled && 'webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.lang = 'fa-IR';
      recognition.continuous = false;
      
      recognition.onstart = () => setListening(true);
      recognition.onend = () => setListening(false);
      
      recognition.onresult = (event) => {
        const command = event.results[0][0].transcript.toLowerCase();
        handleVoiceCommand(command);
      };
      
      if (listening) {
        recognition.start();
      }
      
      return () => recognition.stop();
    }
  }, [voiceEnabled, listening]);

  const handleVoiceCommand = (command) => {
    // Simple voice command mapping
    const commandMap = {
      'تقلب': 'fraud',
      'ناهنجاری': 'anomaly',
      'ریسک': 'risk',
      'کاربران': 'users',
      'درآمد': 'revenue',
      'بازار': 'sentiment',
      'نظارت': 'transaction',
    };
    
    for (const [keyword, feature] of Object.entries(commandMap)) {
      if (command.includes(keyword)) {
        setActiveFeature(feature);
        break;
      }
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const endpoints = {
        overview: '/admin/ai-analytics/overview',
        fraud: '/admin/ai-analytics/fraud-detection',
        anomaly: '/admin/ai-analytics/anomaly-detection',
        users: '/admin/ai-analytics/user-predictions',
        manipulation: '/admin/ai-analytics/market-manipulation',
        revenue: '/admin/ai-analytics/revenue-optimization',
        risk: '/admin/ai-analytics/risk-scores',
        support: '/admin/ai-analytics/support-triage',
        intent: '/admin/ai-analytics/user-intent',
        transaction: '/admin/ai-analytics/transaction-monitoring',
        price: '/admin/ai-analytics/price-anomalies',
        sentiment: '/admin/ai-analytics/market-sentiment',
        kyc: '/admin/ai-analytics/auto-kyc',
        notifications: '/admin/ai-analytics/notifications',
        conversion: '/admin/ai-analytics/conversion-optimization',
        recommendations: '/admin/ai-analytics/recommendations',
        crisis: '/admin/ai-analytics/crisis-prediction',
      };
      
      const endpoint = endpoints[activeFeature];
      if (endpoint) {
        const response = await axios.get(`${API}${endpoint}`, config);
        setData(response.data);
      }
    } catch (error) {
      console.error('Error fetching AI data:', error);
      setData({ error: 'خطا در دریافت داده‌ها' });
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      );
    }

    if (!data) return null;

    switch (activeFeature) {
      case 'overview':
        return <OverviewDashboard data={data} />;
      case 'fraud':
        return <FraudDetection data={data} />;
      case 'anomaly':
        return <AnomalyDetection data={data} />;
      case 'users':
        return <UserPredictions data={data} />;
      case 'manipulation':
        return <MarketManipulation data={data} />;
      case 'revenue':
        return <RevenueOptimization data={data} />;
      case 'risk':
        return <RiskScoring data={data} />;
      case 'support':
        return <SupportTriage data={data} />;
      case 'intent':
        return <UserIntent data={data} />;
      case 'transaction':
        return <TransactionMonitoring data={data} />;
      case 'price':
        return <PriceAnomalies data={data} />;
      case 'sentiment':
        return <MarketSentiment data={data} />;
      case 'kyc':
        return <AutoKYC data={data} />;
      case 'notifications':
        return <AutomatedNotifications data={data} />;
      case 'conversion':
        return <ConversionOptimization data={data} />;
      case 'recommendations':
        return <SmartRecommendations data={data} />;
      case 'crisis':
        return <CrisisManagement data={data} />;
      default:
        return <div>انتخاب کنید</div>;
    }
  };

  return (
    <AdminLayout user={user} onLogout={onLogout}>
      <div className="flex h-screen" dir="rtl">
        {/* Sidebar */}
        <div className="w-64 bg-slate-900 border-l border-slate-800 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-xl font-bold text-emerald-400 mb-4 flex items-center gap-2">
              🤖 مرکز هوش مصنوعی
            </h2>
            
            {/* Voice Command Toggle */}
            <button
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={`w-full mb-4 p-3 rounded-lg transition-colors ${
                voiceEnabled ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-slate-800 hover:bg-slate-700'
              }`}
            >
              {listening ? '🎤 در حال گوش دادن...' : voiceEnabled ? '🎤 دستور صوتی فعال' : '🎤 فعال‌سازی دستور صوتی'}
            </button>

            {/* Feature List by Category */}
            {Object.entries(categories).map(([catKey, category]) => {
              const catFeatures = Object.entries(features).filter(([_, f]) => f.category === catKey);
              if (catFeatures.length === 0) return null;

              return (
                <div key={catKey} className="mb-6">
                  <div className={`text-xs uppercase text-${category.color}-400 font-semibold mb-2`}>
                    {category.name}
                  </div>
                  {catFeatures.map(([key, feature]) => (
                    <button
                      key={key}
                      onClick={() => setActiveFeature(key)}
                      className={`w-full text-right p-3 rounded-lg mb-1 transition-colors flex items-center gap-2 ${
                        activeFeature === key
                          ? 'bg-emerald-600 text-white'
                          : 'text-slate-300 hover:bg-slate-800'
                      }`}
                    >
                      <span>{feature.icon}</span>
                      <span className="text-sm">{feature.name}</span>
                    </button>
                  ))}
                </div>
              );
            })}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto bg-slate-950 p-6">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span>{features[activeFeature]?.icon}</span>
                {features[activeFeature]?.name}
              </h1>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors"
              >
                🔄 به‌روزرسانی
              </button>
            </div>

            {renderContent()}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}

// Component for each feature (simplified versions - you can expand these)

const OverviewDashboard = ({ data }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
    <StatCard title="هشدارهای تقلب" value={data.fraud_alerts || 0} icon="🔒" color="red" />
    <StatCard title="کاربران پرریسک" value={data.high_risk_users || 0} icon="⚠️" color="orange" />
    <StatCard title="اعلان‌های معلق" value={data.pending_notifications || 0} icon="🔔" color="blue" />
    <StatCard title="پیشنهادات هوشمند" value={data.smart_recommendations || 0} icon="💡" color="green" />
    <StatCard title="هشدارهای بحران" value={data.crisis_warnings || 0} icon="🚨" color="purple" />
  </div>
);

const StatCard = ({ title, value, icon, color }) => (
  <div className={`bg-slate-900 border border-${color}-700 rounded-lg p-4`}>
    <div className="text-2xl mb-2">{icon}</div>
    <div className="text-2xl font-bold text-white mb-1">{value}</div>
    <div className="text-sm text-slate-200">{title}</div>
  </div>
);

const FraudDetection = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-3 gap-4 mb-6">
      <StatCard title="کل هشدارها" value={data.total_alerts || 0} icon="🚨" color="red" />
      <StatCard title="اولویت بالا" value={data.high_severity || 0} icon="⚠️" color="orange" />
      <StatCard title="اولویت متوسط" value={data.medium_severity || 0} icon="ℹ️" color="yellow" />
    </div>
    
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">هشدارهای اخیر</h3>
      <div className="space-y-3">
        {data.alerts && data.alerts.slice(0, 10).map((alert, idx) => (
          <div key={idx} className={`p-4 rounded-lg border ${
            alert.severity === 'high' ? 'bg-red-900/20 border-red-700' : 'bg-yellow-900/20 border-yellow-700'
          }`}>
            <div className="font-semibold text-white mb-1">{alert.description}</div>
            <div className="text-sm text-slate-200">{alert.details}</div>
          </div>
        ))}
        {(!data.alerts || data.alerts.length === 0) && (
          <div className="text-center text-slate-200 py-8">✅ هیچ مورد مشکوکی یافت نشد</div>
        )}
      </div>
    </div>
  </div>
);

const AnomalyDetection = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-3 gap-4 mb-6">
      <StatCard title="ناهنجاری‌ها" value={data.total_anomalies || 0} icon="⚠️" color="orange" />
      <StatCard title="میانگین سفارشات روزانه" value={Math.round(data.avg_daily_orders || 0)} icon="📊" color="blue" />
      <StatCard title="میانگین حجم روزانه" value={`${(data.avg_daily_volume || 0) / 1000000}M`} icon="💰" color="green" />
    </div>
    
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">ناهنجاری‌های شناسایی شده</h3>
      <div className="space-y-3">
        {data.anomalies && data.anomalies.map((anomaly, idx) => (
          <div key={idx} className="p-4 bg-orange-900/20 border border-orange-700 rounded-lg">
            <div className="font-semibold text-white mb-1">{anomaly.description}</div>
            <div className="text-sm text-slate-200">تاریخ: {anomaly.date}</div>
          </div>
        ))}
        {(!data.anomalies || data.anomalies.length === 0) && (
          <div className="text-center text-slate-200 py-8">✅ هیچ ناهنجاری یافت نشد</div>
        )}
      </div>
    </div>
  </div>
);

const UserPredictions = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-3 gap-4 mb-6">
      <StatCard title="کاربران با ارزش" value={data.high_value_count || 0} icon="💎" color="green" />
      <StatCard title="ریسک ترک" value={data.churn_risk_count || 0} icon="⚠️" color="orange" />
      <StatCard title="کاربران غیرفعال" value={data.inactive_count || 0} icon="😴" color="slate" />
    </div>
    
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-slate-900 rounded-lg p-6">
        <h3 className="text-lg font-bold text-green-400 mb-4">💎 کاربران با ارزش بالا</h3>
        <div className="space-y-2">
          {data.high_value_users && data.high_value_users.slice(0, 5).map((user, idx) => (
            <div key={idx} className="p-3 bg-green-900/20 border border-green-700 rounded-lg">
              <div className="text-sm text-white">{user.email}</div>
              <div className="text-xs text-slate-200">
                {user.orders} سفارش • {(user.volume / 1000000).toFixed(1)}M تومان
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="bg-slate-900 rounded-lg p-6">
        <h3 className="text-lg font-bold text-orange-400 mb-4">⚠️ ریسک ترک سرویس</h3>
        <div className="space-y-2">
          {data.churn_risk_users && data.churn_risk_users.slice(0, 5).map((user, idx) => (
            <div key={idx} className="p-3 bg-orange-900/20 border border-orange-700 rounded-lg">
              <div className="text-sm text-white">{user.email}</div>
              <div className="text-xs text-slate-200">
                {user.days_inactive} روز غیرفعال • {user.previous_orders} سفارش قبلی
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

const MarketManipulation = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="کل هشدارها" value={data.total_alerts || 0} icon="📈" color="red" />
      <StatCard title="اولویت بالا" value={data.high_severity || 0} icon="🚨" color="orange" />
    </div>
    
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">فعالیت‌های مشکوک</h3>
      <div className="space-y-3">
        {data.alerts && data.alerts.map((alert, idx) => (
          <div key={idx} className="p-4 bg-red-900/20 border border-red-700 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <div className="font-semibold text-white">{alert.description}</div>
              <span className="px-2 py-1 bg-red-600 text-xs rounded">{alert.type}</span>
            </div>
            {alert.coin && <div className="text-sm text-slate-200">ارز: {alert.coin}</div>}
            {alert.order_count && <div className="text-sm text-slate-200">تعداد سفارش: {alert.order_count}</div>}
          </div>
        ))}
        {(!data.alerts || data.alerts.length === 0) && (
          <div className="text-center text-slate-200 py-8">✅ فعالیت مشکوکی یافت نشد</div>
        )}
      </div>
    </div>
  </div>
);

const RevenueOptimization = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-3 gap-4 mb-6">
      <StatCard title="درآمد ماهانه" value={`${(data.current_monthly_revenue || 0) / 1000000}M`} icon="💰" color="green" />
      <StatCard title="حجم کل" value={`${(data.total_volume || 0) / 1000000}M`} icon="📊" color="blue" />
      <StatCard title="سفارشات تکمیل شده" value={data.completed_orders || 0} icon="✅" color="emerald" />
    </div>
    
    <div className="bg-slate-900 rounded-lg p-6 mb-4">
      <h3 className="text-lg font-bold text-white mb-4">سطوح کاربری</h3>
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-emerald-900/20 border border-emerald-700 rounded-lg">
          <div className="text-2xl font-bold text-emerald-400">{data.user_tiers?.high_volume || 0}</div>
          <div className="text-sm text-slate-200">حجم بالا (&gt;100M)</div>
        </div>
        <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
          <div className="text-2xl font-bold text-blue-400">{data.user_tiers?.medium_volume || 0}</div>
          <div className="text-sm text-slate-200">حجم متوسط (10-100M)</div>
        </div>
        <div className="p-4 bg-slate-800 border border-slate-600 rounded-lg">
          <div className="text-2xl font-bold text-slate-200">{data.user_tiers?.low_volume || 0}</div>
          <div className="text-sm text-slate-200">حجم پایین (&lt;10M)</div>
        </div>
      </div>
    </div>
    
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">💡 پیشنهادات بهینه‌سازی</h3>
      <div className="space-y-3">
        {data.recommendations && data.recommendations.map((rec, idx) => (
          <div key={idx} className="p-4 bg-emerald-900/20 border border-emerald-700 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <div className="font-semibold text-white">{rec.title}</div>
              <span className={`px-2 py-1 text-xs rounded ${
                rec.priority === 'high' ? 'bg-red-600' : 'bg-yellow-600'
              }`}>{rec.priority === 'high' ? 'بالا' : 'متوسط'}</span>
            </div>
            <div className="text-sm text-slate-300 mb-2">{rec.description}</div>
            {rec.estimated_increase && (
              <div className="text-sm text-emerald-400">افزایش تخمینی: {rec.estimated_increase}</div>
            )}
            {rec.estimated_revenue && (
              <div className="text-sm text-emerald-400">درآمد تخمینی: {rec.estimated_revenue}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Add similar components for other features...
// For brevity, I'll create simplified versions

const RiskScoring = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="کاربران پرریسک" value={data.high_risk_count || 0} icon="🔴" color="red" />
      <StatCard title="کاربران ریسک متوسط" value={data.medium_risk_count || 0} icon="🟡" color="yellow" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-red-400 mb-4">کاربران پرریسک</h3>
      <div className="space-y-2">
        {data.high_risk_users && data.high_risk_users.slice(0, 10).map((user, idx) => (
          <div key={idx} className="p-3 bg-red-900/20 border border-red-700 rounded-lg">
            <div className="flex justify-between">
              <span className="text-white">{user.email}</span>
              <span className="text-red-400 font-bold">امتیاز: {user.risk_score}</span>
            </div>
            <div className="text-xs text-slate-200 mt-1">{user.risk_factors?.join(' • ')}</div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const SupportTriage = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="کل تیکت‌ها" value={data.total_tickets || 0} icon="🎫" color="blue" />
      <StatCard title="اولویت بالا" value={data.high_priority || 0} icon="🔴" color="red" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">تیکت‌های نیازمند بررسی</h3>
      <div className="space-y-2">
        {data.tickets && data.tickets.map((ticket, idx) => (
          <div key={idx} className={`p-3 rounded-lg border ${
            ticket.priority === 'high' ? 'bg-red-900/20 border-red-700' : 'bg-yellow-900/20 border-yellow-700'
          }`}>
            <div className="text-white font-semibold">{ticket.description}</div>
            <div className="text-sm text-slate-200 mt-1">{ticket.suggested_action}</div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const UserIntent = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-4 gap-4 mb-6">
      <StatCard title="کل کاربران" value={data.total_users || 0} icon="👥" color="blue" />
      <StatCard title="بدون KYC" value={data.stages?.registered_no_kyc || 0} icon="⚠️" color="orange" />
      <StatCard title="بدون سفارش" value={data.stages?.kyc_no_orders || 0} icon="😴" color="yellow" />
      <StatCard title="معامله‌گران فعال" value={data.stages?.active_traders || 0} icon="✅" color="green" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6 mb-4">
      <h3 className="text-lg font-bold text-white mb-4">نرخ تبدیل</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
          <div className="text-3xl font-bold text-blue-400">{data.conversion_rates?.kyc_conversion || 0}%</div>
          <div className="text-sm text-slate-200">تبدیل به KYC</div>
        </div>
        <div className="p-4 bg-green-900/20 border border-green-700 rounded-lg">
          <div className="text-3xl font-bold text-green-400">{data.conversion_rates?.trading_conversion || 0}%</div>
          <div className="text-sm text-slate-200">تبدیل به معامله</div>
        </div>
      </div>
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">💡 بینش‌ها و پیشنهادات</h3>
      <div className="space-y-2">
        {data.insights && data.insights.map((insight, idx) => (
          <div key={idx} className="p-4 bg-emerald-900/20 border border-emerald-700 rounded-lg">
            <div className="text-white font-semibold mb-1">{insight.description}</div>
            <div className="text-sm text-emerald-400">{insight.suggestion}</div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const TransactionMonitoring = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="تراکنش‌های اخیر" value={data.total_transactions || 0} icon="💳" color="blue" />
      <StatCard title="حجم کل" value={`${((data.total_volume || 0) / 1000000).toFixed(1)}M`} icon="💰" color="green" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">هشدارهای نظارتی</h3>
      <div className="space-y-2">
        {data.alerts && data.alerts.map((alert, idx) => (
          <div key={idx} className={`p-3 rounded-lg border ${
            alert.severity === 'high' ? 'bg-red-900/20 border-red-700' : 'bg-yellow-900/20 border-yellow-700'
          }`}>
            <div className="text-white">{alert.description}</div>
            {alert.amount && <div className="text-sm text-slate-200">مبلغ: {alert.amount.toLocaleString('fa-IR')} تومان</div>}
          </div>
        ))}
        {(!data.alerts || data.alerts.length === 0) && (
          <div className="text-center text-slate-200 py-8">✅ همه تراکنش‌ها عادی هستند</div>
        )}
      </div>
    </div>
  </div>
);

const PriceAnomalies = ({ data }) => (
  <div className="bg-slate-900 rounded-lg p-6">
    <h3 className="text-lg font-bold text-white mb-4">ناهنجاری‌های قیمت</h3>
    <div className="space-y-2">
      {data.anomalies && data.anomalies.map((anomaly, idx) => (
        <div key={idx} className="p-4 bg-purple-900/20 border border-purple-700 rounded-lg">
          <div className="text-white">{anomaly.description}</div>
        </div>
      ))}
      {data.status === 'ready' && (
        <div className="text-center text-slate-200 py-8">
          ℹ️ سیستم آماده است. نیاز به تاریخچه قیمت برای تشخیص ناهنجاری
        </div>
      )}
    </div>
  </div>
);

const MarketSentiment = ({ data }) => (
  <div className="space-y-4">
    <div className="bg-slate-900 rounded-lg p-8 text-center mb-6">
      <div className={`text-6xl font-bold mb-4 ${
        data.sentiment === 'صعودی' ? 'text-green-400' :
        data.sentiment === 'نزولی' ? 'text-red-400' : 'text-yellow-400'
      }`}>
        {data.sentiment === 'صعودی' ? '📈' : data.sentiment === 'نزولی' ? '📉' : '➡️'}
      </div>
      <div className="text-3xl font-bold text-white mb-2">احساسات بازار: {data.sentiment}</div>
      <div className="text-xl text-slate-200">حالت کلی: {data.mood}</div>
    </div>
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-slate-900 rounded-lg p-6">
        <div className="text-green-400 text-4xl font-bold mb-2">{data.buy_percentage?.toFixed(1)}%</div>
        <div className="text-slate-200">خریدها</div>
        <div className="text-sm text-slate-300">{(data.buy_volume / 1000000).toFixed(1)}M تومان</div>
      </div>
      <div className="bg-slate-900 rounded-lg p-6">
        <div className="text-red-400 text-4xl font-bold mb-2">{data.sell_percentage?.toFixed(1)}%</div>
        <div className="text-slate-200">فروش‌ها</div>
        <div className="text-sm text-slate-300">{(data.sell_volume / 1000000).toFixed(1)}M تومان</div>
      </div>
    </div>
  </div>
);

const AutoKYC = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="تایید خودکار" value={data.auto_approve_count || 0} icon="✅" color="green" />
      <StatCard title="بررسی دستی" value={data.manual_review_count || 0} icon="👁️" color="yellow" />
    </div>
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-slate-900 rounded-lg p-6">
        <h3 className="text-lg font-bold text-green-400 mb-4">✅ آماده تایید خودکار</h3>
        <div className="space-y-2">
          {data.auto_approve_candidates && data.auto_approve_candidates.slice(0, 5).map((user, idx) => (
            <div key={idx} className="p-3 bg-green-900/20 border border-green-700 rounded-lg">
              <div className="text-white text-sm">{user.email}</div>
              <div className="text-xs text-slate-200">امتیاز ریسک: {user.risk_score}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-slate-900 rounded-lg p-6">
        <h3 className="text-lg font-bold text-yellow-400 mb-4">👁️ نیاز به بررسی</h3>
        <div className="space-y-2">
          {data.manual_review_needed && data.manual_review_needed.slice(0, 5).map((user, idx) => (
            <div key={idx} className="p-3 bg-yellow-900/20 border border-yellow-700 rounded-lg">
              <div className="text-white text-sm">{user.email}</div>
              <div className="text-xs text-slate-200">امتیاز ریسک: {user.risk_score}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

const AutomatedNotifications = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="کل اعلان‌ها" value={data.total_notifications || 0} icon="🔔" color="blue" />
      <StatCard title="اولویت بالا" value={data.high_priority || 0} icon="🔴" color="red" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">اعلان‌های هوشمند</h3>
      <div className="space-y-2">
        {data.notifications && data.notifications.map((notif, idx) => (
          <div key={idx} className={`p-4 rounded-lg border ${
            notif.priority === 'high' ? 'bg-red-900/20 border-red-700' :
            notif.priority === 'medium' ? 'bg-yellow-900/20 border-yellow-700' :
            'bg-blue-900/20 border-blue-700'
          }`}>
            <div className="flex justify-between items-start mb-2">
              <div className="font-semibold text-white">{notif.title}</div>
              <span className={`px-2 py-1 text-xs rounded ${
                notif.priority === 'high' ? 'bg-red-600' :
                notif.priority === 'medium' ? 'bg-yellow-600' : 'bg-blue-600'
              }`}>{notif.priority === 'high' ? 'بالا' : notif.priority === 'medium' ? 'متوسط' : 'پایین'}</span>
            </div>
            <div className="text-sm text-slate-300">{notif.message}</div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const ConversionOptimization = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-3 gap-4 mb-6">
      <StatCard title="کل ثبت‌نام‌ها" value={data.total_registered || 0} icon="👥" color="blue" />
      <StatCard title="KYC تکمیل" value={data.kyc_completed || 0} icon="✅" color="green" />
      <StatCard title="با سفارش" value={data.users_with_orders || 0} icon="🛒" color="emerald" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6 mb-4">
      <h3 className="text-lg font-bold text-white mb-4">نرخ‌های تبدیل</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-green-900/20 border border-green-700 rounded-lg">
          <div className="text-4xl font-bold text-green-400">{data.conversion_rates?.kyc_conversion || 0}%</div>
          <div className="text-slate-200">تبدیل KYC</div>
        </div>
        <div className="p-4 bg-emerald-900/20 border border-emerald-700 rounded-lg">
          <div className="text-4xl font-bold text-emerald-400">{data.conversion_rates?.trading_conversion || 0}%</div>
          <div className="text-slate-200">تبدیل به معامله</div>
        </div>
      </div>
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">گلوگاه‌ها و پیشنهادات</h3>
      <div className="space-y-3">
        {data.bottlenecks && data.bottlenecks.map((bottleneck, idx) => (
          <div key={idx} className="p-4 bg-orange-900/20 border border-orange-700 rounded-lg">
            <div className="font-semibold text-white mb-2">مرحله: {bottleneck.stage}</div>
            <div className="text-sm text-slate-300 mb-2">
              نرخ فعلی: {bottleneck.current_rate}% • هدف: {bottleneck.target_rate}%
            </div>
            <div className="text-sm text-emerald-400">پیشنهادات:</div>
            <ul className="list-disc list-inside text-sm text-slate-300 mr-4">
              {bottleneck.suggestions?.map((sug, sidx) => (
                <li key={sidx}>{sug}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const SmartRecommendations = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="کل پیشنهادات" value={data.total_recommendations || 0} icon="💡" color="emerald" />
      <StatCard title="اولویت بالا" value={data.high_priority || 0} icon="🔴" color="red" />
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">پیشنهادات هوشمند برای اقدام</h3>
      <div className="space-y-3">
        {data.recommendations && data.recommendations.map((rec, idx) => (
          <div key={idx} className="p-4 bg-emerald-900/20 border border-emerald-700 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <div className="font-semibold text-white">{rec.title}</div>
              <span className={`px-2 py-1 text-xs rounded ${
                rec.priority === 'high' ? 'bg-red-600' :
                rec.priority === 'medium' ? 'bg-yellow-600' : 'bg-blue-600'
              }`}>{rec.priority === 'high' ? 'بالا' : rec.priority === 'medium' ? 'متوسط' : 'پایین'}</span>
            </div>
            <div className="text-sm text-slate-300 mb-2">{rec.description}</div>
            {rec.count && <div className="text-sm text-emerald-400">تعداد: {rec.count}</div>}
          </div>
        ))}
      </div>
    </div>
  </div>
);

const CrisisManagement = ({ data }) => (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4 mb-6">
      <StatCard title="کل هشدارها" value={data.total_warnings || 0} icon="🚨" color="red" />
      <StatCard title="وضعیت سیستم" value={data.system_health === 'good' ? 'خوب' : 'نیاز به توجه'} 
        icon={data.system_health === 'good' ? '✅' : '⚠️'} 
        color={data.system_health === 'good' ? 'green' : 'yellow'} />
    </div>
    <div className="bg-slate-900 rounded-lg p-6">
      <h3 className="text-lg font-bold text-white mb-4">هشدارهای پیشگیرانه</h3>
      <div className="space-y-3">
        {data.warnings && data.warnings.map((warning, idx) => (
          <div key={idx} className={`p-4 rounded-lg border ${
            warning.severity === 'high' ? 'bg-red-900/20 border-red-700' :
            warning.severity === 'medium' ? 'bg-yellow-900/20 border-yellow-700' :
            'bg-blue-900/20 border-blue-700'
          }`}>
            <div className="flex justify-between items-start mb-2">
              <div className="font-semibold text-white">{warning.description}</div>
              <span className={`px-2 py-1 text-xs rounded ${
                warning.severity === 'high' ? 'bg-red-600' :
                warning.severity === 'medium' ? 'bg-yellow-600' : 'bg-blue-600'
              }`}>{warning.severity === 'high' ? 'بالا' : warning.severity === 'medium' ? 'متوسط' : 'پایین'}</span>
            </div>
            <div className="text-sm text-slate-300 mb-1">نوع: {warning.type}</div>
            <div className="text-sm text-emerald-400">توصیه: {warning.recommendation}</div>
          </div>
        ))}
        {(!data.warnings || data.warnings.length === 0) && (
          <div className="text-center text-slate-200 py-8">✅ هیچ هشداری وجود ندارد - سیستم سالم است</div>
        )}
      </div>
    </div>
  </div>
);
