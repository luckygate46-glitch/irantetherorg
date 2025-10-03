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
            <div className="text-slate-400">در انتظار</div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-blue-400">
              {orders.filter(o => o.status === 'approved').length}
            </div>
            <div className="text-slate-400">تایید شده</div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-green-400">
              {orders.filter(o => o.status === 'completed').length}
            </div>
            <div className="text-slate-400">تکمیل شده</div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-2xl font-bold text-red-400">
              {orders.filter(o => o.status === 'rejected').length}
            </div>
            <div className="text-slate-400">رد شده</div>
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-800">
                <tr>
                  <th className="px-4 py-3 text-right">کاربر</th>
                  <th className="px-4 py-3 text-right">نوع</th>
                  <th className="px-4 py-3 text-right">ارز</th>
                  <th className="px-4 py-3 text-right">مقدار</th>
                  <th className="px-4 py-3 text-right">ارزش (تومان)</th>
                  <th className="px-4 py-3 text-right">وضعیت</th>
                  <th className="px-4 py-3 text-right">تاریخ</th>
                  <th className="px-4 py-3 text-right">عملیات</th>
                </tr>
              </thead>
              <tbody>
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="px-4 py-8 text-center text-slate-400">
                      هیچ سفارشی یافت نشد
                    </td>
                  </tr>
                ) : (
                  orders.map(order => (
                    <tr key={order.id} className="border-t border-slate-800 hover:bg-slate-800/50">
                      <td className="px-4 py-3">
                        <div>
                          <div className="font-semibold">{order.user_name || 'بدون نام'}</div>
                          <div className="text-sm text-slate-400">{order.user_email}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          order.order_type === 'buy' ? 'bg-green-600' :
                          order.order_type === 'sell' ? 'bg-red-600' : 'bg-blue-600'
                        }`}>
                          {getOrderTypeText(order.order_type)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          <div className="font-semibold">{order.coin_symbol}</div>
                          {order.target_coin_symbol && (
                            <div className="text-sm text-slate-400">→ {order.target_coin_symbol}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          {order.order_type === 'buy' ? (
                            <div>{formatNumber(order.amount_tmn)} ت</div>
                          ) : (
                            <div>{order.amount_crypto} {order.coin_symbol}</div>
                          )}
                          {order.order_type === 'trade' && order.target_coin_symbol && (
                            <div className="text-sm text-slate-400">
                              → {((order.amount_crypto * order.price_at_order) / order.price_at_order).toFixed(8)} {order.target_coin_symbol}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-semibold">{formatNumber(order.total_value_tmn)}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(order.status)}`}>
                          {getStatusText(order.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm">
                          {new Date(order.created_at).toLocaleDateString('fa-IR')}
                        </div>
                        <div className="text-xs text-slate-400">
                          {new Date(order.created_at).toLocaleTimeString('fa-IR')}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {order.status === 'pending' && (
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleOrderAction(order.id, 'approve')}
                              disabled={processingId === order.id}
                              className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-slate-700 rounded text-xs transition-colors"
                            >
                              {processingId === order.id ? '...' : 'تایید'}
                            </button>
                            <button
                              onClick={() => {
                                const note = prompt('دلیل رد (اختیاری):');
                                if (note !== null) {
                                  handleOrderAction(order.id, 'reject', note);
                                }
                              }}
                              disabled={processingId === order.id}
                              className="px-3 py-1 bg-red-600 hover:bg-red-700 disabled:bg-slate-700 rounded text-xs transition-colors"
                            >
                              رد
                            </button>
                          </div>
                        )}
                        {order.status !== 'pending' && (
                          <span className="text-sm text-slate-400">
                            {order.status === 'approved' ? 'تایید شده' :
                             order.status === 'completed' ? 'تکمیل' : 'پردازش شده'}
                          </span>
                        )}
                        {order.admin_note && (
                          <div className="text-xs text-slate-400 mt-1">
                            یادداشت: {order.admin_note}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminOrders;