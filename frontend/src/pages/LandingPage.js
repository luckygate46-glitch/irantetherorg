import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function LandingPage() {
  const navigate = useNavigate();
  const [prices, setPrices] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
    fetchPrices();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const fetchPrices = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/crypto/prices`);
      const data = await response.json();
      
      if (data.data) {
        // Get top 6 cryptocurrencies
        const pricesArray = Object.values(data.data).slice(0, 6);
        setPrices(pricesArray);
      }
    } catch (error) {
      console.error('Error fetching prices:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="fixed top-0 w-full bg-slate-900/80 backdrop-blur-lg border-b border-slate-800 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">₿</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-emerald-400">صرافی کریپتو ایران</h1>
              <p className="text-xs text-slate-400">معاملات امن و سریع</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-slate-300">خوش آمدید، {user.full_name || user.email}</span>
                <button
                  onClick={() => navigate(user.is_admin ? '/admin' : '/dashboard')}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg font-semibold transition-colors"
                >
                  پنل کاربری
                </button>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                >
                  خروج
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => navigate('/auth')}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg font-semibold transition-colors"
                >
                  ورود
                </button>
                <button
                  onClick={() => navigate('/auth')}
                  className="px-6 py-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-lg font-semibold transition-colors"
                >
                  ثبت‌نام
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-emerald-900/30 border border-emerald-700 rounded-full text-emerald-300 text-sm">
            🚀 پلتفرم معاملات ارز دیجیتال در ایران
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-l from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
            خرید و فروش ارز دیجیتال
            <br />
            ساده، سریع و امن
          </h1>
          
          <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            با صرافی کریپتو ایران، به راحتی بیت کوین، اتریوم، تتر و سایر ارزهای دیجیتال را خریداری کنید.
            با پشتیبانی ۲۴ساعته، کارمزد پایین و امنیت بالا.
          </p>
          
          <div className="flex justify-center gap-4 mb-16">
            <button
              onClick={() => navigate(user ? (user.is_admin ? '/admin' : '/dashboard') : '/auth')}
              className="px-8 py-4 bg-gradient-to-l from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg font-bold text-lg transition-all transform hover:scale-105 shadow-lg shadow-emerald-900/50"
            >
              {user ? 'ورود به پنل' : 'شروع کنید - رایگان'}
            </button>
            <button
              onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg font-bold text-lg transition-all"
            >
              بیشتر بدانید
            </button>
          </div>

          {/* Live Prices Ticker */}
          <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-6">
            <div className="text-sm text-slate-400 mb-4">قیمت‌های لحظه‌ای</div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {prices.map((coin, index) => (
                <div key={index} className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-sm text-slate-400 mb-1">{coin.name}</div>
                  <div className="text-lg font-bold text-white mb-1">
                    {new Intl.NumberFormat('fa-IR').format(Math.round(coin.price_tmn))}
                  </div>
                  <div className={`text-sm font-semibold ${
                    coin.change_24h > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {coin.change_24h > 0 ? '▲' : '▼'} {Math.abs(coin.change_24h).toFixed(2)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">چرا صرافی کریپتو ایران؟</h2>
            <p className="text-xl text-slate-400">ویژگی‌های منحصر به فرد ما</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-emerald-500 transition-colors">
              <div className="w-12 h-12 bg-emerald-600 rounded-lg flex items-center justify-center text-2xl mb-4">
                🔒
              </div>
              <h3 className="text-xl font-bold mb-3">امنیت بالا</h3>
              <p className="text-slate-400">
                با استفاده از جدیدترین تکنولوژی‌های امنیتی، دارایی‌های شما در امان است. احراز هویت دو مرحله‌ای و رمزنگاری پیشرفته.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-emerald-500 transition-colors">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center text-2xl mb-4">
                ⚡
              </div>
              <h3 className="text-xl font-bold mb-3">معاملات سریع</h3>
              <p className="text-slate-400">
                خرید و فروش آنی ارزهای دیجیتال. پردازش سریع سفارشات و انتقال فوری به کیف پول شما.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-emerald-500 transition-colors">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center text-2xl mb-4">
                💰
              </div>
              <h3 className="text-xl font-bold mb-3">کارمزد پایین</h3>
              <p className="text-slate-400">
                با کارمزدهای رقابتی و شفاف، بیشترین سود را از معاملات خود ببرید. بدون هزینه‌های پنهان.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-emerald-500 transition-colors">
              <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center text-2xl mb-4">
                🤖
              </div>
              <h3 className="text-xl font-bold mb-3">هوش مصنوعی</h3>
              <p className="text-slate-400">
                دستیار هوشمند معاملاتی که به شما کمک می‌کند بهترین تصمیمات را بگیرید. تحلیل بازار و پیشنهادات شخصی‌سازی شده.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-emerald-500 transition-colors">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center text-2xl mb-4">
                💳
              </div>
              <h3 className="text-xl font-bold mb-3">واریز و برداشت آسان</h3>
              <p className="text-slate-400">
                واریز تومانی با کارت بانکی و برداشت سریع به حساب شما. پشتیبانی از تمام بانک‌های ایرانی.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-emerald-500 transition-colors">
              <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center text-2xl mb-4">
                📞
              </div>
              <h3 className="text-xl font-bold mb-3">پشتیبانی ۲۴/۷</h3>
              <p className="text-slate-400">
                تیم پشتیبانی ما همیشه در دسترس شماست. پاسخگویی سریع به سوالات و مشکلات شما.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">چگونه شروع کنم؟</h2>
            <p className="text-xl text-slate-400">در ۳ مرحله ساده</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-4">
                ۱
              </div>
              <h3 className="text-2xl font-bold mb-3">ثبت‌نام کنید</h3>
              <p className="text-slate-400">
                با ایمیل یا شماره موبایل خود ثبت‌نام کنید. فقط ۲ دقیقه طول می‌کشد.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-4">
                ۲
              </div>
              <h3 className="text-2xl font-bold mb-3">احراز هویت</h3>
              <p className="text-slate-400">
                برای امنیت بیشتر، هویت خود را تایید کنید. فرآیند ساده و سریع.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-4">
                ۳
              </div>
              <h3 className="text-2xl font-bold mb-3">شروع معامله</h3>
              <p className="text-slate-400">
                موجودی خود را شارژ کنید و اولین خرید خود را انجام دهید. همین الان!
              </p>
            </div>
          </div>

          <div className="text-center mt-12">
            <button
              onClick={() => navigate('/auth')}
              className="px-12 py-4 bg-gradient-to-l from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-lg font-bold text-xl transition-all transform hover:scale-105 shadow-lg shadow-emerald-900/50"
            >
              همین الان شروع کنید 🚀
            </button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold text-emerald-400 mb-2">+۱۰,۰۰۰</div>
              <div className="text-slate-400">کاربر فعال</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-blue-400 mb-2">+۱۵</div>
              <div className="text-slate-400">ارز دیجیتال</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-purple-400 mb-2">۲۴/۷</div>
              <div className="text-slate-400">پشتیبانی</div>
            </div>
            <div>
              <div className="text-5xl font-bold text-orange-400 mb-2">۹۹.۹%</div>
              <div className="text-slate-400">آپتایم سرور</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-l from-emerald-900/50 to-teal-900/50 border border-emerald-700 rounded-2xl p-12">
            <h2 className="text-4xl font-bold mb-4">آماده‌اید؟</h2>
            <p className="text-xl text-slate-300 mb-8">
              به جمع هزاران کاربر راضی بپیوندید و سفر خود در دنیای ارزهای دیجیتال را شروع کنید.
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => navigate('/auth')}
                className="px-8 py-4 bg-white text-slate-900 hover:bg-slate-100 rounded-lg font-bold text-lg transition-all transform hover:scale-105"
              >
                ثبت‌نام رایگان
              </button>
              <button
                onClick={() => navigate('/auth')}
                className="px-8 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg font-bold text-lg transition-all"
              >
                ورود به حساب
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="font-bold text-lg mb-4">صرافی کریپتو ایران</h3>
              <p className="text-slate-400 text-sm">
                پلتفرم معاملات ارز دیجیتال در ایران با امنیت بالا و پشتیبانی ۲۴ساعته
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-4">خدمات</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="/auth" className="hover:text-emerald-400">خرید ارز دیجیتال</a></li>
                <li><a href="/auth" className="hover:text-emerald-400">فروش ارز دیجیتال</a></li>
                <li><a href="/auth" className="hover:text-emerald-400">کیف پول</a></li>
                <li><a href="/auth" className="hover:text-emerald-400">احراز هویت</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-4">پشتیبانی</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li><a href="/auth" className="hover:text-emerald-400">تماس با ما</a></li>
                <li><a href="/auth" className="hover:text-emerald-400">سوالات متداول</a></li>
                <li><a href="/auth" className="hover:text-emerald-400">راهنما</a></li>
                <li><a href="/auth" className="hover:text-emerald-400">قوانین و مقررات</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-4">تماس</h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li>📧 info@cryptoiran.com</li>
                <li>📞 ۰۲۱-۱۲۳۴۵۶۷۸</li>
                <li>📍 تهران، ایران</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center text-slate-400 text-sm">
            <p>© ۲۰۲۵ صرافی کریپتو ایران. تمامی حقوق محفوظ است.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
