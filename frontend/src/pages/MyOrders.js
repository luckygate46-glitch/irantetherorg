import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import UserSidebarLayout from '../layouts/UserSidebarLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, XCircle, FileText, Download, Eye } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MyOrders = ({ user, onLogout }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showFactor, setShowFactor] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/trading/orders/my`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-600">در انتظار تایید</Badge>;
      case 'approved':
        return <Badge className="bg-green-600">تایید شده</Badge>;
      case 'rejected':
        return <Badge className="bg-red-600">رد شده</Badge>;
      case 'completed':
        return <Badge className="bg-blue-600">تکمیل شده</Badge>;
      default:
        return <Badge className="bg-gray-600">{status}</Badge>;
    }
  };

  const getOrderTypeBadge = (type) => {
    switch (type) {
      case 'buy':
        return <Badge className="bg-green-700">خرید</Badge>;
      case 'sell':
        return <Badge className="bg-red-700">فروش</Badge>;
      case 'trade':
        return <Badge className="bg-blue-700">معامله</Badge>;
      default:
        return <Badge>{type}</Badge>;
    }
  };

  const showOrderFactor = (order) => {
    setSelectedOrder(order);
    setShowFactor(true);
  };

  const downloadFactor = (order) => {
    const factorText = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧾 فاکتور سفارش - صرافی کریپتو ایران
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 شماره سفارش: ${order.id}
📅 تاریخ: ${new Date(order.created_at).toLocaleString('fa-IR')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 جزئیات سفارش
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

نوع سفارش: ${order.order_type === 'buy' ? 'خرید' : order.order_type === 'sell' ? 'فروش' : 'معامله'}
ارز دیجیتال: ${order.coin_symbol}
مقدار: ${order.amount_crypto?.toFixed(8) || 'N/A'} ${order.coin_symbol}
قیمت واحد: ${new Intl.NumberFormat('fa-IR').format(order.price_at_order)} تومان
مبلغ کل: ${new Intl.NumberFormat('fa-IR').format(order.total_value_tmn)} تومان

${order.user_wallet_address ? `آدرس کیف پول: ${order.user_wallet_address}` : ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 وضعیت سفارش
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

وضعیت: ${order.status === 'pending' ? '⏳ در انتظار تایید ادمین' : 
          order.status === 'approved' ? '✅ تایید شده' : 
          order.status === 'rejected' ? '❌ رد شده' : 
          '✅ تکمیل شده'}

${order.admin_note ? `یادداشت ادمین: ${order.admin_note}` : ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ توجه
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• این فاکتور صرفاً جهت اطلاع شما صادر شده است
• پس از تایید ادمین، ارز به کیف پول شما ارسال می‌شود
• در صورت هرگونه سوال با پشتیبانی تماس بگیرید

صرافی کریپتو ایران 🇮🇷
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `.trim();

    const blob = new Blob([factorText], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `factor_${order.id}.txt`;
    link.click();
  };

  if (loading) {
    return (
      <UserSidebarLayout user={user} onLogout={onLogout}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      </UserSidebarLayout>
    );
  }

  return (
    <UserSidebarLayout user={user} onLogout={onLogout}>
      <div className="space-y-6" dir="rtl">
        <div>
          <h1 className="text-3xl font-bold text-white">سفارشات من</h1>
          <p className="text-slate-400 mt-2">مشاهده و پیگیری سفارشات خرید و فروش</p>
        </div>

        {orders.length === 0 ? (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-12 text-center">
              <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400 text-lg">شما هنوز سفارشی ثبت نکرده‌اید</p>
              <Button 
                onClick={() => navigate('/market')}
                className="mt-4 bg-emerald-600 hover:bg-emerald-700"
              >
                شروع معامله
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {orders.map((order) => (
              <Card key={order.id} className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-full flex items-center justify-center text-2xl">
                        💰
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          {getOrderTypeBadge(order.order_type)}
                          <span className="text-white font-bold text-lg">{order.coin_symbol}</span>
                          {getStatusBadge(order.status)}
                        </div>
                        <p className="text-slate-400 text-sm">
                          {new Date(order.created_at).toLocaleString('fa-IR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => showOrderFactor(order)}
                        className="gap-2"
                      >
                        <Eye className="w-4 h-4" />
                        مشاهده فاکتور
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadFactor(order)}
                        className="gap-2"
                      >
                        <Download className="w-4 h-4" />
                        دانلود
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-800 rounded-lg p-4">
                    <div>
                      <p className="text-slate-400 text-xs mb-1">مقدار</p>
                      <p className="text-white font-medium">
                        {order.amount_crypto?.toFixed(8)} {order.coin_symbol}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs mb-1">قیمت</p>
                      <p className="text-white font-medium">
                        {new Intl.NumberFormat('fa-IR').format(order.price_at_order)} تومان
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs mb-1">مبلغ کل</p>
                      <p className="text-white font-medium">
                        {new Intl.NumberFormat('fa-IR').format(order.total_value_tmn)} تومان
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-xs mb-1">وضعیت</p>
                      {order.status === 'pending' && (
                        <p className="text-yellow-400 font-medium">⏳ در انتظار</p>
                      )}
                      {order.status === 'approved' && (
                        <p className="text-green-400 font-medium">✅ تایید شده</p>
                      )}
                      {order.status === 'rejected' && (
                        <p className="text-red-400 font-medium">❌ رد شده</p>
                      )}
                    </div>
                  </div>

                  {order.admin_note && (
                    <div className="mt-4 bg-blue-900/20 border border-blue-700 rounded p-3">
                      <p className="text-blue-300 text-sm">
                        <strong>یادداشت ادمین:</strong> {order.admin_note}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Factor Modal */}
        {showFactor && selectedOrder && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white flex items-center gap-2">
                    <FileText className="w-6 h-6" />
                    فاکتور سفارش
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowFactor(false)}
                  >
                    بستن
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Factor Header */}
                <div className="text-center bg-gradient-to-r from-emerald-900/50 to-teal-900/50 rounded-lg p-6 border border-emerald-700">
                  <h2 className="text-2xl font-bold text-white mb-2">صرافی کریپتو ایران 🇮🇷</h2>
                  <p className="text-emerald-300">فاکتور رسمی خرید ارز دیجیتال</p>
                </div>

                {/* Order Info */}
                <div className="bg-slate-800 rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                    <span className="text-slate-400">شماره فاکتور:</span>
                    <span className="text-white font-mono text-sm">{selectedOrder.id.slice(0, 8).toUpperCase()}</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                    <span className="text-slate-400">تاریخ و ساعت:</span>
                    <span className="text-white">{new Date(selectedOrder.created_at).toLocaleString('fa-IR')}</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                    <span className="text-slate-400">نوع سفارش:</span>
                    {getOrderTypeBadge(selectedOrder.order_type)}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">وضعیت:</span>
                    {getStatusBadge(selectedOrder.status)}
                  </div>
                </div>

                {/* Purchase Details */}
                <div className="bg-slate-800 rounded-lg p-4">
                  <h3 className="text-white font-bold mb-3 pb-2 border-b border-slate-700">جزئیات خرید</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">ارز دیجیتال:</span>
                      <span className="text-white font-bold text-lg">{selectedOrder.coin_symbol}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">مقدار:</span>
                      <span className="text-emerald-400 font-bold">
                        {selectedOrder.amount_crypto?.toFixed(8)} {selectedOrder.coin_symbol}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">قیمت هر واحد:</span>
                      <span className="text-white">
                        {new Intl.NumberFormat('fa-IR').format(selectedOrder.price_at_order)} تومان
                      </span>
                    </div>
                    <div className="flex items-center justify-between pt-3 border-t border-slate-700">
                      <span className="text-slate-400 font-bold">مبلغ کل پرداختی:</span>
                      <span className="text-white font-bold text-xl">
                        {new Intl.NumberFormat('fa-IR').format(selectedOrder.total_value_tmn)} تومان
                      </span>
                    </div>
                  </div>
                </div>

                {/* Wallet Address */}
                {selectedOrder.user_wallet_address && (
                  <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                    <h3 className="text-blue-300 font-bold mb-2">آدرس کیف پول دریافت کننده</h3>
                    <p className="text-white font-mono text-sm break-all" dir="ltr">
                      {selectedOrder.user_wallet_address}
                    </p>
                  </div>
                )}

                {/* Status Message */}
                {selectedOrder.status === 'pending' && (
                  <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <Clock className="w-8 h-8 text-yellow-500" />
                      <div>
                        <h3 className="text-yellow-300 font-bold mb-1">⏳ در انتظار تایید ادمین</h3>
                        <p className="text-yellow-200 text-sm">
                          سفارش شما در صف بررسی قرار گرفته است. پس از تایید ادمین، ارز به کیف پول شما ارسال خواهد شد.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {selectedOrder.status === 'approved' && (
                  <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-8 h-8 text-green-500" />
                      <div>
                        <h3 className="text-green-300 font-bold mb-1">✅ سفارش تایید شد!</h3>
                        <p className="text-green-200 text-sm">
                          ارز دیجیتال شما به کیف پول ارسال شده است. موجودی خود را بررسی کنید.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {selectedOrder.status === 'rejected' && (
                  <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <XCircle className="w-8 h-8 text-red-500" />
                      <div>
                        <h3 className="text-red-300 font-bold mb-1">❌ سفارش رد شد</h3>
                        <p className="text-red-200 text-sm">
                          متاسفانه سفارش شما توسط ادمین رد شد.
                          {selectedOrder.admin_note && ` دلیل: ${selectedOrder.admin_note}`}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    onClick={() => downloadFactor(selectedOrder)}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700 gap-2"
                  >
                    <Download className="w-4 h-4" />
                    دانلود فاکتور
                  </Button>
                  <Button
                    onClick={() => setShowFactor(false)}
                    variant="outline"
                    className="flex-1"
                  >
                    بستن
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </UserSidebarLayout>
  );
};

export default MyOrders;
