import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut, Wallet, TrendingUp, User, CheckCircle, XCircle } from "lucide-react";

export default function Dashboard({ user, onLogout }) {
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
              <p className="text-white font-semibold">{user.full_name}</p>
            </div>
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
                {user.wallet_balance_tmn.toLocaleString('fa-IR')} تومان
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

        {/* Welcome Message */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">به داشبورد خود خوش آمدید</CardTitle>
            <CardDescription className="text-slate-400">
              سیستم احراز هویت با موفقیت راه‌اندازی شد. بزودی امکانات بیشتری اضافه خواهد شد:
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-slate-300">
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                سیستم واریز و برداشت (کارت به کارت)
              </li>
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                خرید و فروش ارزهای دیجیتال
              </li>
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                نمودارهای معاملاتی زنده
              </li>
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                سیستم KYC و احراز هویت
              </li>
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                ربات سیگنال‌های معاملاتی
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}