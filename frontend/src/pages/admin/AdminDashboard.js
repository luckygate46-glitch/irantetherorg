import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import AdminLayout from "@/components/AdminLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, TrendingUp, CreditCard, Clock, Shield } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminDashboard({ user, onLogout }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="dashboard">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">داشبورد مدیریت</h1>
          <p className="text-slate-300 mt-2">خلاصه آمار سیستم</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total Users */}
          <Card 
            className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border-emerald-800/50 cursor-pointer hover:scale-105 transition-transform"
            onClick={() => navigate('/admin/users')}
            data-testid="admin-total-users-card"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-300 text-sm font-medium">کل کاربران</CardTitle>
                <Users className="w-5 h-5 text-emerald-400" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{stats?.total_users || 0}</p>
              <p className="text-sm text-emerald-400 mt-1">
                {stats?.active_users || 0} کاربر فعال
              </p>
            </CardContent>
          </Card>

          {/* Total Deposits */}
          <Card 
            className="bg-gradient-to-br from-blue-900/30 to-cyan-900/30 border-blue-800/50 cursor-pointer hover:scale-105 transition-transform"
            onClick={() => navigate('/admin/deposits')}
            data-testid="admin-total-deposits-card"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-300 text-sm font-medium">کل واریزی‌ها</CardTitle>
                <TrendingUp className="w-5 h-5 text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">
                {(stats?.total_deposits || 0).toLocaleString('fa-IR')}
              </p>
              <p className="text-sm text-blue-400 mt-1">تومان</p>
            </CardContent>
          </Card>

          {/* Pending Deposits */}
          <Card 
            className="bg-gradient-to-br from-amber-900/30 to-orange-900/30 border-amber-800/50 cursor-pointer hover:scale-105 transition-transform"
            onClick={() => navigate('/admin/deposits')}
            data-testid="admin-pending-deposits-card"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-300 text-sm font-medium">در انتظار تایید</CardTitle>
                <Clock className="w-5 h-5 text-amber-400" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{stats?.pending_deposits || 0}</p>
              <p className="text-sm text-amber-400 mt-1">درخواست واریز</p>
            </CardContent>
          </Card>

          {/* Total Cards */}
          <Card 
            className="bg-gradient-to-br from-violet-900/30 to-purple-900/30 border-violet-800/50 cursor-pointer hover:scale-105 transition-transform"
            onClick={() => navigate('/admin/cards')}
            data-testid="admin-total-cards-card"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-300 text-sm font-medium">کارت‌های فعال</CardTitle>
                <CreditCard className="w-5 h-5 text-violet-400" />
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white">{stats?.total_cards || 0}</p>
              <p className="text-sm text-violet-400 mt-1">کارت بانکی</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">دسترسی سریع</CardTitle>
            <CardDescription className="text-slate-200">
              مدیریت بخش‌های مختلف سیستم
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              <button
                onClick={() => navigate('/admin/users')}
                className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors text-right"
                data-testid="quick-action-users"
              >
                <Users className="w-8 h-8 text-emerald-400 mb-3" />
                <h3 className="text-white font-semibold mb-2">مدیریت کاربران</h3>
                <p className="text-sm text-slate-200">مشاهده و مدیریت کاربران سیستم</p>
              </button>

              <button
                onClick={() => navigate('/admin/cards')}
                className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors text-right"
                data-testid="quick-action-cards"
              >
                <CreditCard className="w-8 h-8 text-violet-400 mb-3" />
                <h3 className="text-white font-semibold mb-2">مدیریت کارت‌ها</h3>
                <p className="text-sm text-slate-200">افزودن و مدیریت شماره کارت‌ها</p>
              </button>

              <button
                onClick={() => navigate('/admin/deposits')}
                className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors text-right"
                data-testid="quick-action-deposits"
              >
                <TrendingUp className="w-8 h-8 text-blue-400 mb-3" />
                <h3 className="text-white font-semibold mb-2">تایید واریزی‌ها</h3>
                <p className="text-sm text-slate-200">بررسی و تایید درخواست‌های واریز</p>
              </button>

              <button
                onClick={() => navigate('/admin/orders')}
                className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors text-right"
                data-testid="quick-action-orders"
              >
                <TrendingUp className="w-8 h-8 text-purple-400 mb-3" />
                <h3 className="text-white font-semibold mb-2">مدیریت سفارشات</h3>
                <p className="text-sm text-slate-200">بررسی و تایید سفارشات معاملاتی</p>
              </button>

              <button
                onClick={() => navigate('/admin/kyc')}
                className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:bg-slate-800 transition-colors text-right"
                data-testid="quick-action-kyc"
              >
                <Shield className="w-8 h-8 text-orange-400 mb-3" />
                <h3 className="text-white font-semibold mb-2">احراز هویت</h3>
                <p className="text-sm text-slate-200">بررسی و تایید مدارک کاربران</p>
              </button>

              <button
                onClick={() => navigate('/admin/backup')}
                className="p-6 bg-gradient-to-br from-emerald-800/50 to-teal-800/50 border border-emerald-700 rounded-lg hover:from-emerald-700/50 hover:to-teal-700/50 transition-all text-right"
                data-testid="quick-action-backup"
              >
                <svg className="w-8 h-8 text-emerald-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <h3 className="text-white font-semibold mb-2">💾 پشتیبان‌گیری</h3>
                <p className="text-sm text-slate-200">دانلود و مدیریت نسخه‌های پشتیبان دیتابیس</p>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}