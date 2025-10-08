import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut, Wallet, TrendingUp, User, CheckCircle, XCircle, AlertTriangle, RefreshCw, Brain } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard({ user, onLogout, onUserUpdate }) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [currentUser, setCurrentUser] = useState(user);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    setCurrentUser(user);
    
    // Auto-refresh user data every 30 seconds to check for KYC updates
    const interval = setInterval(() => {
      refreshUserData(false); // Silent refresh
    }, 30000);

    return () => clearInterval(interval);
  }, [user]);

  const refreshUserData = async (showNotification = true) => {
    try {
      setRefreshing(true);
      const response = await axios.get(`${API}/auth/me`);
      const updatedUser = response.data;
      
      setCurrentUser(updatedUser);
      
      // Notify parent component about user update
      if (onUserUpdate) {
        onUserUpdate(updatedUser);
      }
      
      // Check if KYC status changed
      if (user.kyc_level !== updatedUser.kyc_level && showNotification) {
        if (updatedUser.kyc_level === 2) {
          toast({
            title: "احراز هویت تایید شد! 🎉",
            description: "سطح احراز هویت شما به سطح ۲ ارتقا یافت. اکنون می‌توانید معامله کنید.",
          });
        } else if (updatedUser.kyc_level === 1) {
          toast({
            title: "احراز هویت سطح ۱ تایید شد ✅",
            description: "اکنون می‌توانید به کیف پول دسترسی داشته باشید.",
          });
        }
      }
      
      // Check if KYC status was approved
      if (user.kyc_status !== updatedUser.kyc_status && updatedUser.kyc_status === "approved" && showNotification) {
        toast({
          title: "وضعیت احراز هویت به‌روزرسانی شد",
          description: "احراز هویت شما تایید شده است",
        });
      }
      
      if (showNotification) {
        toast({
          title: "به‌روزرسانی موفق",
          description: "اطلاعات حساب شما به‌روزرسانی شد",
        });
      }
    } catch (error) {
      console.error('خطا در به‌روزرسانی اطلاعات کاربر:', error);
      if (showNotification) {
        toast({
          title: "خطا",
          description: "خطا در به‌روزرسانی اطلاعات",
          variant: "destructive"
        });
      }
    } finally {
      setRefreshing(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-slate-950" dir="rtl">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-white">صرافی کریپتو ایران</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-slate-400">خوش آمدید</p>
              <p className="text-white font-semibold">{currentUser.full_name || currentUser.email}</p>
            </div>
            <Button
              onClick={() => refreshUserData(true)}
              variant="outline"
              size="sm"
              className="border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 ml-2"
              disabled={refreshing}
            >
              <RefreshCw className={`w-4 h-4 ml-2 ${refreshing ? 'animate-spin' : ''}`} />
              بروزرسانی
            </Button>
            <Button
              onClick={onLogout}
              data-testid="logout-button"
              variant="outline"
              className="border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              <LogOut className="ml-2 w-4 h-4" />
              خروج
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* KYC Warning */}
        {currentUser.kyc_level < 1 && (
          <Card className="bg-amber-900/20 border-amber-800/50 mb-6" data-testid="kyc-warning">
            <CardContent className="py-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <AlertTriangle className="w-10 h-10 text-amber-400" />
                  <div>
                    <h3 className="text-xl font-bold text-white mb-1">
                      احراز هویت خود را تکمیل کنید
                    </h3>
                    <p className="text-slate-300">
                      برای استفاده از امکانات معاملاتی، واریز و برداشت، باید احراز هویت کنید
                    </p>
                  </div>
                </div>
                <Button 
                  onClick={() => navigate('/kyc')}
                  className="bg-amber-600 hover:bg-amber-700"
                  data-testid="complete-kyc-button"
                >
                  تکمیل احراز هویت
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Wallet Card */}
          <Card className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border-emerald-800/50">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Wallet className="w-5 h-5" />
                موجودی کیف پول
              </CardTitle>
              <CardDescription className="text-slate-400">تومان ایران (TMN)</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-white" data-testid="wallet-balance">
                {currentUser.wallet_balance_tmn.toLocaleString('fa-IR')} تومان
              </p>
            </CardContent>
          </Card>

          {/* Profile Status */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <User className="w-5 h-5" />
                وضعیت حساب
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">تایید ایمیل</span>
                {user.is_verified ? (
                  <CheckCircle className="w-5 h-5 text-emerald-500" data-testid="verified-icon" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" data-testid="not-verified-icon" />
                )}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">وضعیت حساب</span>
                {user.is_active ? (
                  <span className="text-emerald-500 text-sm font-semibold">فعال</span>
                ) : (
                  <span className="text-red-500 text-sm font-semibold">غیرفعال</span>
                )}
              </div>
              {user.is_admin && (
                <div className="mt-2 px-3 py-1 bg-amber-500/20 border border-amber-500/30 rounded text-amber-400 text-sm text-center">
                  مدیر سیستم
                </div>
              )}
            </CardContent>
          </Card>

          {/* User Info */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">اطلاعات کاربری</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <span className="text-slate-400">ایمیل:</span>
                <p className="text-white mt-1">{user.email}</p>
              </div>
              {user.phone && (
                <div>
                  <span className="text-slate-400">موبایل:</span>
                  <p className="text-white mt-1">{user.phone}</p>
                </div>
              )}
              <div>
                <span className="text-slate-400">تاریخ عضویت:</span>
                <p className="text-white mt-1">
                  {new Date(user.created_at).toLocaleDateString('fa-IR')}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="bg-slate-900/50 border-slate-800 mb-6">
          <CardHeader>
            <CardTitle className="text-white">دسترسی سریع</CardTitle>
            <CardDescription className="text-slate-400">
              به امکانات مختلف دسترسی داشته باشید
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              <Button 
                onClick={() => navigate('/market')}
                className="h-20 bg-gradient-to-br from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800"
              >
                <div className="text-center">
                  <TrendingUp className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">بازار ارزها</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/trade')}
                className="h-20 bg-gradient-to-br from-purple-600 to-indigo-700 hover:from-purple-700 hover:to-indigo-800"
                disabled={currentUser.kyc_level < 2}
              >
                <div className="text-center">
                  <TrendingUp className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">معاملات</span>
                </div>
              </Button>
              
              <Button 
                onClick={() => navigate('/wallet')}
                className="h-20 bg-gradient-to-br from-blue-600 to-cyan-700 hover:from-blue-700 hover:to-cyan-800"
                disabled={currentUser.kyc_level < 1}
              >
                <div className="text-center">
                  <Wallet className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">کیف پول</span>
                </div>
              </Button>
              
              <Button 
                onClick={() => navigate('/kyc')}
                className="h-20 bg-gradient-to-br from-amber-600 to-orange-700 hover:from-amber-700 hover:to-orange-800"
              >
                <div className="text-center">
                  <User className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">احراز هویت</span>
                </div>
              </Button>
              
              <Button 
                onClick={() => navigate('/ai/dashboard')}
                className="h-20 bg-gradient-to-br from-violet-600 to-purple-700 hover:from-violet-700 hover:to-purple-800"
              >
                <div className="text-center">
                  <Brain className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">دستیار هوشمند</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/advanced-trade')}
                className="h-20 bg-gradient-to-br from-red-600 to-pink-700 hover:from-red-700 hover:to-pink-800"
                disabled={currentUser.kyc_level < 2}
              >
                <div className="text-center">
                  <TrendingUp className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">معاملات پیشرفته</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/multi-asset')}
                className="h-20 bg-gradient-to-br from-green-600 to-emerald-700 hover:from-green-700 hover:to-emerald-800"
              >
                <div className="text-center">
                  <RefreshCw className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">بازارهای متنوع</span>
                </div>
              </Button>

              <Button 
                onClick={() => navigate('/staking')}
                className="h-20 bg-gradient-to-br from-yellow-600 to-amber-700 hover:from-yellow-700 hover:to-amber-800"
                disabled={currentUser.kyc_level < 1}
              >
                <div className="text-center">
                  <TrendingUp className="w-6 h-6 mx-auto mb-1" />
                  <span className="text-base font-semibold">استیکینگ</span>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Features Overview */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">امکانات صرافی</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-slate-300">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                سیستم واریز و برداشت (کارت به کارت)
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                خرید و فروش ارزهای دیجیتال
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                قیمت‌های زنده بازار
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                سیستم KYC با شاهکار
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                دستیار هوشمند و پیشنهادات معاملاتی
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                معاملات پیشرفته (حد ضرر، سفارش محدود، DCA)
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                بازارهای متنوع (سهام، کالا، فارکس)
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                استیکینگ و فارمینگ بازده
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                تحلیل‌های پیشرفته و بهینه‌سازی پرتفوی
              </li>
              <li className="flex items-center gap-2">
                <div className="w-5 h-5 bg-slate-700 rounded-full flex items-center justify-center text-xs">AMZ</div>
                خرید از آمازون با ارزهای دیجیتال (به زودی)
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}