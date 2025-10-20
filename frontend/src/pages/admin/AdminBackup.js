import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminBackup = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  useEffect(() => {
    fetchStats();
    fetchBackups();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/backup/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('خطا در دریافت آمار:', error);
    }
  };

  const fetchBackups = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/backup/list`);
      setBackups(response.data.backups || []);
    } catch (error) {
      console.error('خطا در دریافت لیست پشتیبان‌ها:', error);
    } finally {
      setLoading(false);
    }
  };

  const createBackup = async () => {
    if (!window.confirm('آیا مطمئن هستید که می‌خواهید نسخه پشتیبان جدید ایجاد کنید؟')) {
      return;
    }

    try {
      setCreating(true);
      await axios.post(`${API}/admin/backup/create`);
      alert('✅ نسخه پشتیبان با موفقیت ایجاد شد!');
      fetchBackups();
    } catch (error) {
      console.error('خطا در ایجاد نسخه پشتیبان:', error);
      alert('خطا در ایجاد نسخه پشتیبان: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCreating(false);
    }
  };

  const downloadFullDatabase = async () => {
    if (!window.confirm('آیا می‌خواهید کل دیتابیس را دانلود کنید؟ (ممکن است حجم زیادی داشته باشد)')) {
      return;
    }

    try {
      const response = await axios.get(`${API}/admin/backup/database`);
      
      // Create JSON blob and download
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = window.URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `database_full_export_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      alert('✅ دیتابیس کامل دانلود شد!');
    } catch (error) {
      console.error('خطا در دانلود دیتابیس:', error);
      alert('خطا در دانلود دیتابیس: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteBackup = async (filename) => {
    if (!window.confirm(`آیا مطمئن هستید که می‌خواهید "${filename}" را حذف کنید؟`)) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/backup/${filename}`);
      alert('✅ نسخه پشتیبان حذف شد!');
      fetchBackups();
    } catch (error) {
      console.error('خطا در حذف نسخه پشتیبان:', error);
      alert('خطا در حذف: ' + (error.response?.data?.detail || error.message));
    }
  };

  const downloadBackup = (filename) => {
    const link = document.createElement('a');
    link.href = `${API}/admin/backup/download/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/json') {
      setUploadedFile(file);
    } else {
      alert('لطفا یک فایل JSON انتخاب کنید');
    }
  };

  const restoreFromBackup = async () => {
    if (!uploadedFile) {
      alert('لطفا ابتدا یک فایل بک‌آپ انتخاب کنید');
      return;
    }

    const confirmMessage = `⚠️ هشدار: این عملیات تمام داده‌های فعلی را حذف کرده و با داده‌های بک‌آپ جایگزین می‌کند.

آیا مطمئن هستید که می‌خواهید ادامه دهید؟

این عملیات غیرقابل بازگشت است!`;

    if (!window.confirm(confirmMessage)) {
      return;
    }

    // Second confirmation
    if (!window.confirm('آیا واقعا مطمئن هستید؟ تمام داده‌های فعلی حذف خواهند شد!')) {
      return;
    }

    try {
      setRestoring(true);

      // Read file
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const backupData = JSON.parse(e.target.result);

          // Validate backup structure
          if (!backupData.collections) {
            alert('فرمت فایل بک‌آپ نامعتبر است');
            return;
          }

          // Send to server
          const response = await axios.post(`${API}/admin/backup/restore`, backupData);

          if (response.data.success) {
            alert(`✅ بازگردانی با موفقیت انجام شد!\n\n` +
              `کالکشن‌های بازگردانی شده: ${response.data.details.collections_restored.length}\n` +
              `تعداد داده‌ها: ${response.data.details.total_documents_restored}`
            );
            
            // Refresh stats
            fetchStats();
            setUploadedFile(null);
          } else {
            alert('خطا در بازگردانی: ' + JSON.stringify(response.data.details));
          }
        } catch (error) {
          console.error('Error restoring:', error);
          alert('خطا در بازگردانی: ' + (error.response?.data?.detail || error.message));
        } finally {
          setRestoring(false);
        }
      };

      reader.readAsText(uploadedFile);
    } catch (error) {
      console.error('Error reading file:', error);
      alert('خطا در خواندن فایل: ' + error.message);
      setRestoring(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR') + ' ' + date.toLocaleTimeString('fa-IR');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-emerald-400">💾 پشتیبان‌گیری دیتابیس</h1>
            <nav className="flex gap-4">
              <a href="/admin" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/admin/users" className="text-slate-300 hover:text-white transition-colors">کاربران</a>
              <a href="/admin/orders" className="text-slate-300 hover:text-white transition-colors">سفارشات</a>
              <a href="/admin/deposits" className="text-slate-300 hover:text-white transition-colors">واریزها</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-300">سلام {user?.email}</span>
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
        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <button
            onClick={downloadFullDatabase}
            className="p-6 bg-gradient-to-br from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 rounded-xl transition-all transform hover:scale-105 shadow-lg"
          >
            <div className="flex items-center justify-center gap-3 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span className="text-xl font-bold">دانلود کامل دیتابیس</span>
            </div>
            <p className="text-emerald-100 text-sm">دانلود فوری تمام داده‌ها به صورت JSON</p>
          </button>

          <button
            onClick={createBackup}
            disabled={creating}
            className="p-6 bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-700 disabled:to-slate-800 rounded-xl transition-all transform hover:scale-105 shadow-lg"
          >
            <div className="flex items-center justify-center gap-3 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="text-xl font-bold">
                {creating ? 'در حال ایجاد...' : 'ایجاد نسخه پشتیبان جدید'}
              </span>
            </div>
            <p className="text-blue-100 text-sm">ذخیره نسخه پشتیبان در سرور</p>
          </button>
        </div>

        {/* Database Stats */}
        {stats && (
          <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 mb-8">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              آمار دیتابیس
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-3xl font-bold text-emerald-400">{stats.total_collections}</div>
                <div className="text-slate-300">تعداد کالکشن‌ها</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-3xl font-bold text-blue-400">{stats.total_documents}</div>
                <div className="text-slate-300">تعداد کل داده‌ها</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-3xl font-bold text-purple-400">{stats.total_size_mb} MB</div>
                <div className="text-slate-300">حجم تقریبی</div>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold text-slate-300 mb-3">جزئیات کالکشن‌ها:</h3>
              {stats.collections?.map((col, idx) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-3 flex justify-between items-center">
                  <div>
                    <span className="font-semibold text-white">{col.name}</span>
                    <span className="text-slate-400 text-sm mr-3">
                      {col.document_count} سند
                    </span>
                  </div>
                  <div className="text-slate-400 text-sm">
                    {col.estimated_size_kb} KB
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Backup List */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
          <div className="p-6 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
              نسخه‌های پشتیبان ({backups.length})
            </h2>
            <button
              onClick={fetchBackups}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors text-sm"
            >
              🔄 بروزرسانی
            </button>
          </div>

          {loading ? (
            <div className="p-12 flex justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
            </div>
          ) : backups.length === 0 ? (
            <div className="p-12 text-center text-slate-400">
              <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p className="text-lg">هیچ نسخه پشتیبانی یافت نشد</p>
              <p className="text-sm mt-2">با کلیک روی "ایجاد نسخه پشتیبان جدید" اولین پشتیبان را بسازید</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-800">
              {backups.map((backup, idx) => (
                <div key={idx} className="p-6 hover:bg-slate-800/30 transition-colors">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="font-bold text-white">{backup.filename}</span>
                      </div>
                      <div className="text-sm text-slate-400 space-y-1">
                        <div>📅 تاریخ ایجاد: {formatDate(backup.created_at)}</div>
                        <div>💾 حجم: {backup.size_mb} MB</div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => downloadBackup(backup.filename)}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg transition-colors flex items-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        دانلود
                      </button>
                      <button
                        onClick={() => deleteBackup(backup.filename)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg transition-colors"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-900/30 border border-blue-500/50 rounded-xl p-6">
          <h3 className="font-bold text-blue-300 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            راهنمای استفاده
          </h3>
          <ul className="space-y-2 text-sm text-blue-100">
            <li className="flex items-start gap-2">
              <span className="text-blue-400">•</span>
              <span><strong>دانلود کامل دیتابیس:</strong> تمام داده‌های دیتابیس را به صورت فوری دانلود می‌کند (فایل JSON)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400">•</span>
              <span><strong>ایجاد نسخه پشتیبان:</strong> یک نسخه پشتیبان در سرور ذخیره می‌شود که بعداً قابل دانلود است</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400">•</span>
              <span><strong>توصیه:</strong> حداقل هفته‌ای یکبار نسخه پشتیبان بگیرید</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400">•</span>
              <span><strong>نوع دیتابیس:</strong> MongoDB (فرمت JSON)</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdminBackup;
