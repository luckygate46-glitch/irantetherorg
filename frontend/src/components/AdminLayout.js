import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { LogOut, TrendingUp, LayoutDashboard, Users, CreditCard, TrendingDown } from "lucide-react";

export default function AdminLayout({ user, onLogout, children, currentPage }) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { id: 'dashboard', label: 'داشبورد', icon: LayoutDashboard, path: '/admin' },
    { id: 'users', label: 'کاربران', icon: Users, path: '/admin/users' },
    { id: 'cards', label: 'کارت‌ها', icon: CreditCard, path: '/admin/cards' },
    { id: 'deposits', label: 'واریزی‌ها', icon: TrendingDown, path: '/admin/deposits' },
  ];

  const aiMenuItems = [
    { id: 'ai-center', label: '🤖 مرکز هوش مصنوعی', path: '/admin/ai-center' },
    { id: 'ai-settings', label: '⚙️ تنظیمات AI', path: '/admin/settings/ai' },
  ];

  return (
    <div className="min-h-screen bg-slate-950" dir="rtl">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">پنل مدیریت</h1>
              <p className="text-xs text-emerald-400">صرافی کریپتو ایران</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-slate-400">مدیر سیستم</p>
              <p className="text-white font-semibold">{user.full_name}</p>
            </div>
            <Button
              onClick={onLogout}
              data-testid="admin-logout-button"
              variant="outline"
              className="border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              <LogOut className="ml-2 w-4 h-4" />
              خروج
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 border-l border-slate-800 bg-slate-900/30 min-h-[calc(100vh-73px)] p-4">
          <nav className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <button
                  key={item.id}
                  onClick={() => navigate(item.path)}
                  data-testid={`admin-menu-${item.id}`}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right transition-colors ${
                    isActive
                      ? 'bg-emerald-600 text-white'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}

            {/* AI Settings Section */}
            <div className="pt-4 mt-4 border-t border-slate-700">
              <div className="text-xs text-slate-500 uppercase px-4 mb-2">هوش مصنوعی</div>
              {aiMenuItems.map((item) => {
                const isActive = location.pathname === item.path;
                
                return (
                  <button
                    key={item.id}
                    onClick={() => navigate(item.path)}
                    data-testid={`admin-menu-${item.id}`}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-right transition-colors ${
                      isActive
                        ? 'bg-emerald-600 text-white'
                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    <span className="font-medium">{item.label}</span>
                  </button>
                );
              })}
            </div>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}