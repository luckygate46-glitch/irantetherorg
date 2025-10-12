import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AdminLayout from '../../components/AdminLayout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminAISettings({ user, onLogout }) {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showApiKey, setShowApiKey] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      const response = await axios.get(`${API}/admin/settings/ai`, config);
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching AI settings:', error);
      setMessage({
        type: 'error',
        text: 'خطا در بارگذاری تنظیمات: ' + (error.response?.data?.detail || error.message)
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    if (!apiKey || apiKey.trim() === '') {
      setMessage({ type: 'error', text: 'لطفاً کلید API را وارد کنید' });
      return;
    }

    try {
      setSaving(true);
      setMessage({ type: '', text: '' });

      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.post(
        `${API}/admin/settings/ai`,
        { openai_api_key: apiKey },
        config
      );

      setMessage({ type: 'success', text: response.data.message });
      setApiKey('');
      setShowApiKey(false);
      
      // Refresh settings
      await fetchSettings();
    } catch (error) {
      console.error('Error saving AI settings:', error);
      setMessage({
        type: 'error',
        text: 'خطا در ذخیره تنظیمات: ' + (error.response?.data?.detail || error.message)
      });
    } finally {
      setSaving(false);
    }
  };

  const handleTestKey = async () => {
    if (!apiKey || apiKey.trim() === '') {
      setMessage({ type: 'error', text: 'لطفاً ابتدا کلید API را وارد کنید' });
      return;
    }

    try {
      setTesting(true);
      setMessage({ type: 'info', text: 'در حال تست کلید API...' });

      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      // Test by saving (which includes validation)
      await axios.post(
        `${API}/admin/settings/ai`,
        { openai_api_key: apiKey },
        config
      );

      setMessage({ type: 'success', text: '✅ کلید API معتبر است و با موفقیت ذخیره شد!' });
      setApiKey('');
      setShowApiKey(false);
      await fetchSettings();
    } catch (error) {
      console.error('Error testing API key:', error);
      setMessage({
        type: 'error',
        text: '❌ کلید API معتبر نیست: ' + (error.response?.data?.detail || error.message)
      });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout}>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout}>
      <div className="p-6 max-w-4xl mx-auto" dir="rtl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">⚙️ تنظیمات هوش مصنوعی</h1>
          <p className="text-slate-400">مدیریت کلید API و پیکربندی سرویس‌های هوشمند</p>
        </div>

        {message.text && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-900/50 border border-green-700 text-green-200' :
            message.type === 'error' ? 'bg-red-900/50 border border-red-700 text-red-200' :
            'bg-blue-900/50 border border-blue-700 text-blue-200'
          }`}>
            {message.text}
          </div>
        )}

        {/* Current Status Card */}
        <div className="bg-slate-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-4">📊 وضعیت فعلی</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-700 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">وضعیت سرویس</div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  settings?.status === 'configured' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <div className="text-white font-semibold">
                  {settings?.status === 'configured' ? '✅ فعال' : '❌ غیرفعال'}
                </div>
              </div>
            </div>

            <div className="bg-slate-700 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">مدل هوش مصنوعی</div>
              <div className="text-white font-semibold">{settings?.model || 'gpt-4o'}</div>
            </div>

            <div className="bg-slate-700 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">ارائه‌دهنده</div>
              <div className="text-white font-semibold">OpenAI</div>
            </div>

            <div className="bg-slate-700 rounded-lg p-4">
              <div className="text-slate-400 text-sm mb-1">کلید API</div>
              <div className="text-white font-semibold">
                {settings?.openai_api_key_set ? (
                  <span className="text-green-400">
                    {settings?.openai_api_key_preview || '***'}
                  </span>
                ) : (
                  <span className="text-red-400">تنظیم نشده</span>
                )}
              </div>
            </div>
          </div>

          {settings?.last_updated && (
            <div className="mt-4 text-sm text-slate-400">
              آخرین به‌روزرسانی: {new Date(settings.last_updated).toLocaleString('fa-IR')}
            </div>
          )}
        </div>

        {/* API Key Configuration Card */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">🔑 پیکربندی کلید API</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                کلید OpenAI API
              </label>
              <div className="relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-proj-..."
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-emerald-500 focus:outline-none"
                  dir="ltr"
                />
                <button
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  {showApiKey ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              <p className="mt-2 text-sm text-slate-400">
                💡 برای دریافت کلید API خود به <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:underline">platform.openai.com</a> مراجعه کنید
              </p>
              <div className="mt-3 p-3 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                <p className="text-sm text-yellow-200">
                  ⚠️ <strong>نکته امنیتی:</strong> از کلید API شخصی خود استفاده کنید. این کلید به صورت امن در دیتابیس ذخیره می‌شود و هرگز در کد قرار نمی‌گیرد.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleTestKey}
                disabled={saving || testing || !apiKey}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
              >
                {testing ? (
                  <span className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    در حال تست...
                  </span>
                ) : (
                  '🧪 تست و ذخیره'
                )}
              </button>

              <button
                onClick={handleSaveSettings}
                disabled={saving || testing || !apiKey}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
              >
                {saving ? (
                  <span className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    در حال ذخیره...
                  </span>
                ) : (
                  '💾 ذخیره'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Information Card */}
        <div className="bg-slate-800 rounded-lg p-6 mt-6">
          <h2 className="text-xl font-bold text-white mb-4">ℹ️ راهنما</h2>
          
          <div className="space-y-3 text-slate-300">
            <div className="flex items-start gap-3">
              <div className="text-emerald-400 mt-1">✓</div>
              <div>
                <strong>دستیار هوشمند معاملات:</strong> توصیه‌های خرید و فروش به زبان فارسی
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="text-emerald-400 mt-1">✓</div>
              <div>
                <strong>تحلیل بازار:</strong> تحلیل کلی وضعیت بازار و فرصت‌های سرمایه‌گذاری
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="text-emerald-400 mt-1">✓</div>
              <div>
                <strong>چت هوشمند:</strong> پاسخگویی به سوالات کاربران درباره معاملات
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="text-yellow-400 mt-1">⚠</div>
              <div>
                <strong>هزینه:</strong> استفاده از API هزینه‌هایی دارد که به حساب OpenAI شما اعمال می‌شود
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="text-red-400 mt-1">🔒</div>
              <div>
                <strong>امنیت:</strong> کلید API به صورت امن در دیتابیس ذخیره می‌شود
              </div>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
