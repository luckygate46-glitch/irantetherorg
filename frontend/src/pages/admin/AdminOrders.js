import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminOrders = ({ user, onLogout }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchOrders();
  }, [user, navigate]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/trading/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری سفارشات:', error);
      alert('خطا در بارگذاری سفارشات');
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/admin/export/orders`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `orders_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      
      alert('✅ فایل CSV با موفقیت دانلود شد!');
    } catch (error) {
      console.error('خطا در دانلود CSV:', error);
      alert('خطا در دانلود فایل');
    }
  };

  const handleOrderAction = async (orderId, action, note = '') => {
    try {
      setProcessingId(orderId);
      await axios.post(`${API}/admin/trading/orders/approve`, {
        order_id: orderId,
        action,
        admin_note: note
      });
      
      alert(`سفارش با موفقیت ${action === 'approve' ? 'تایید' : 'رد'} شد`);
      fetchOrders(); // Refresh the list
    } catch (error) {
      console.error('خطا در پردازش سفارش:', error);
      alert(error.response?.data?.detail || 'خطا در پردازش سفارش');
    } finally {
      setProcessingId(null);
    }
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text).then(() => {
      alert(`✅ ${label} کپی شد: ${text}`);
    }).catch(err => {
      console.error('خطا در کپی:', err);
    });
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(num));
  };

  const getOrderTypeText = (type) => {
    switch (type) {
      case 'buy': return 'خرید';
      case 'sell': return 'فروش';
      case 'trade': return 'تبدیل';
      default: return type;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-600';
      case 'approved': return 'bg-blue-600';
      case 'completed': return 'bg-green-600';
      case 'rejected': return 'bg-red-600';
      default: return 'bg-slate-600';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending': return 'در انتظار';
      case 'approved': return 'تایید شده';
      case 'completed': return 'تکمیل شده';
      case 'rejected': return 'رد شده';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-emerald-400">🎛️ مدیریت سفارشات</h1>
            <nav className="flex gap-4">
              <a href="/admin" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/admin/users" className="text-slate-300 hover:text-white transition-colors">کاربران</a>
              <a href="/admin/cards" className="text-slate-300 hover:text-white transition-colors">کارت‌ها</a>
              <a href="/admin/deposits" className="text-slate-300 hover:text-white transition-colors">واریزها</a>
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
        {/* Export Button */}
        <div className="mb-6 flex justify-between items-center">
          <button
            onClick={exportToCSV}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold flex items-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            دانلود CSV
          </button>
          <div className="text-slate-400">
            تعداد کل سفارشات: {orders.length}
          </div>
        </div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">سفارشات معاملاتی</h2>
          <button
            onClick={fetchOrders}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors"
          >
            بروزرسانی
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-yellow-400">
              {orders.filter(o => o.status === 'pending').length}
            </div>
            <div className="text-slate-200">در انتظار</div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-blue-400">
              {orders.filter(o => o.status === 'approved').length}
            </div>
            <div className="text-slate-200">تایید شده</div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-green-400">
              {orders.filter(o => o.status === 'completed').length}
            </div>
            <div className="text-slate-200">تکمیل شده</div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-red-400">
              {orders.filter(o => o.status === 'rejected').length}
            </div>
            <div className="text-slate-200">رد شده</div>
          </div>
        </div>

        {/* Orders List */}
        <div className="space-y-4">
          {orders.length === 0 ? (
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-8 text-center text-slate-400">
              هیچ سفارشی یافت نشد
            </div>
          ) : (
            orders.map(order => (
              <div key={order.id} className="bg-slate-900 rounded-xl border border-slate-800 p-6 hover:border-emerald-500/50 transition-all">
                {/* Header Row */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-3 py-1 rounded-lg font-bold ${
                        order.order_type === 'buy' ? 'bg-green-600 text-white' :
                        order.order_type === 'sell' ? 'bg-red-600 text-white' : 'bg-blue-600 text-white'
                      }`}>
                        {getOrderTypeText(order.order_type)}
                      </span>
                      <span className={`px-3 py-1 rounded-lg ${getStatusColor(order.status)} text-white`}>
                        {getStatusText(order.status)}
                      </span>
                      <span className="text-2xl font-bold text-white">{order.coin_symbol}</span>
                    </div>
                    <div className="text-slate-400 text-sm">
                      {new Date(order.created_at).toLocaleDateString('fa-IR')} • {new Date(order.created_at).toLocaleTimeString('fa-IR')}
                    </div>
                  </div>
                  <div className="text-left">
                    <div className="text-2xl font-bold text-emerald-400">
                      {formatNumber(order.total_value_tmn)} تومان
                    </div>
                    <div className="text-slate-400 text-sm">
                      {order.amount_crypto && `${order.amount_crypto} ${order.coin_symbol}`}
                    </div>
                  </div>
                </div>

                {/* User Info & Wallet Section - PROMINENT */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {/* User Info */}
                  <div className="bg-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-400 mb-2">📋 اطلاعات کاربر</div>
                    <div className="text-white font-semibold mb-1">{order.user_name || 'بدون نام'}</div>
                    <div className="text-slate-300 text-sm">{order.user_email}</div>
                    {order.user_phone && (
                      <div className="text-slate-300 text-sm mt-1">📱 {order.user_phone}</div>
                    )}
                  </div>

                  {/* WALLET ADDRESS - MOST PROMINENT */}
                  <div className="bg-gradient-to-br from-emerald-900/50 to-emerald-800/30 border-2 border-emerald-500/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-xs text-emerald-300 font-bold">💳 آدرس کیف پول کاربر ({order.coin_symbol})</div>
                      {order.user_wallet_addresses && order.user_wallet_addresses[order.coin_symbol]?.verified && (
                        <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded">✓ تایید شده</span>
                      )}
                    </div>
                    {order.wallet_address ? (
                      <div>
                        <div className="bg-slate-900 rounded p-3 mb-2 font-mono text-sm text-emerald-300 break-all">
                          {order.wallet_address}
                        </div>
                        <button
                          onClick={() => copyToClipboard(order.wallet_address, 'آدرس کیف پول')}
                          className="w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-semibold text-white transition-colors flex items-center justify-center gap-2"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          کپی آدرس
                        </button>
                      </div>
                    ) : (
                      <div className="text-yellow-400 text-sm">⚠️ کاربر آدرس کیف پول ثبت نکرده است</div>
                    )}
                  </div>
                </div>

                {/* All User Wallets */}
                {order.user_wallet_addresses && Object.keys(order.user_wallet_addresses).length > 0 && (
                  <div className="bg-slate-800/50 rounded-lg p-4 mb-4">
                    <div className="text-xs text-slate-400 mb-3">🔑 تمام کیف پول‌های کاربر</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {Object.entries(order.user_wallet_addresses).map(([symbol, wallet]) => (
                        <div key={symbol} className="bg-slate-900 rounded p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-white font-semibold">{symbol}</span>
                            {wallet.verified && (
                              <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">✓</span>
                            )}
                          </div>
                          <div className="font-mono text-xs text-slate-300 break-all mb-2">
                            {wallet.address}
                          </div>
                          <button
                            onClick={() => copyToClipboard(wallet.address, `آدرس ${symbol}`)}
                            className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
                          >
                            📋 کپی
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Order Details */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                  <div>
                    <div className="text-slate-400">مقدار کریپتو</div>
                    <div className="text-white font-semibold">{order.amount_crypto || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-slate-400">مقدار تومان</div>
                    <div className="text-white font-semibold">{formatNumber(order.amount_tmn || 0)}</div>
                  </div>
                  <div>
                    <div className="text-slate-400">قیمت واحد</div>
                    <div className="text-white font-semibold">{formatNumber(order.price_at_order)}</div>
                  </div>
                  <div>
                    <div className="text-slate-400">شناسه سفارش</div>
                    <div className="text-white font-mono text-xs">{order.id.substring(0, 8)}...</div>
                  </div>
                </div>

                {/* Admin Note */}
                {order.admin_note && (
                  <div className="bg-blue-900/30 border border-blue-500/50 rounded-lg p-3 mb-4">
                    <div className="text-xs text-blue-300 mb-1">📝 یادداشت ادمین</div>
                    <div className="text-white text-sm">{order.admin_note}</div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 items-center">
                  {order.status === 'pending' ? (
                    <>
                      <button
                        onClick={() => handleOrderAction(order.id, 'approve')}
                        disabled={processingId === order.id}
                        className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-500 disabled:bg-slate-700 rounded-lg font-bold text-white transition-colors"
                      >
                        {processingId === order.id ? '⏳ در حال پردازش...' : '✅ تایید و ارسال به کیف پول'}
                      </button>
                      <button
                        onClick={() => {
                          const note = prompt('دلیل رد (اختیاری):');
                          if (note !== null) {
                            handleOrderAction(order.id, 'reject', note);
                          }
                        }}
                        disabled={processingId === order.id}
                        className="px-6 py-3 bg-red-600 hover:bg-red-500 disabled:bg-slate-700 rounded-lg font-bold text-white transition-colors"
                      >
                        ❌ رد
                      </button>
                    </>
                  ) : (
                    <div className="flex-1 text-center py-3 bg-slate-800 rounded-lg text-slate-400">
                      {order.status === 'approved' && '✓ تایید شده - آماده ارسال'}
                      {order.status === 'completed' && '✓ تکمیل شده'}
                      {order.status === 'rejected' && '✗ رد شده'}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminOrders;