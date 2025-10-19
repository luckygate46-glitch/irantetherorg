import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import NotificationBell from '../components/NotificationBell';
import {
  User, Settings, CreditCard, Wallet, Shield, Bell,
  TrendingUp, History, PieChart, FileText, DollarSign, AlertTriangle,
  Brain, Lightbulb, Search, BarChart3, Bot, Smartphone,
  Coins, Wheat, ArrowRightLeft, Gem, Gift, HelpCircle,
  Ticket, Phone, LogOut, Menu, X, ChevronDown, ChevronRight,
  Home, Star, Clock, Trophy, Gamepad2
} from 'lucide-react';

const UserSidebarLayout = ({ children, user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    profile: false,
    trading: false,
    ai: false,
    services: false,
    support: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Filter menu items based on KYC approval status
  const getMenuItems = () => {
    // Check if user has KYC approval
    const hasKYCApproval = user?.kyc_status === 'approved';
    
    // If user doesn't have KYC approval, show minimal menu
    if (!hasKYCApproval) {
      return [
        {
          id: 'kyc',
          title: '✋ تکمیل احراز هویت',
          icon: Shield,
          path: '/kyc',
          badge: 'اقدام فوری',
          className: 'bg-amber-600/20 border-2 border-amber-500 hover:bg-amber-600/30 animate-pulse'
        }
      ];
    }

    // Full menu for approved users
    const baseItems = [
      {
        id: 'dashboard',
        title: 'داشبورد اصلی',
        icon: Home,
        path: '/dashboard',
        badge: null
      },
    {
      id: 'profile',
      title: 'پروفایل و تنظیمات',
      icon: User,
      expandable: true,
      children: [
        { title: 'پروفایل کاربری', icon: User, path: '/profile', badge: null },
        { title: 'اطلاعات بانکی', icon: CreditCard, path: '/banking-info', badge: null },
        { title: 'آدرس کیف پول', icon: Wallet, path: '/wallet-addresses', badge: null },
        { title: 'تنظیمات امنیتی', icon: Shield, path: '/security-settings', badge: null },
        { title: 'تنظیمات اطلاع‌رسانی', icon: Bell, path: '/notification-settings', badge: null },
      ]
    },
    {
      id: 'trading',
      title: 'معاملات و مالی',
      icon: TrendingUp,
      expandable: true,
      children: [
        { title: 'بازار', icon: BarChart3, path: '/market', badge: null },
        { title: 'معاملات', icon: TrendingUp, path: '/trade', badge: 'KYC 2', disabled: user?.kyc_level < 2 },
        { title: 'سابقه معاملات', icon: History, path: '/trading-history', badge: null },
        { title: 'پرتفوی من', icon: PieChart, path: '/portfolio', badge: null },
        { title: 'سفارشات باز', icon: FileText, path: '/open-orders', badge: null },
        { title: 'تراکنش‌ها', icon: DollarSign, path: '/transactions', badge: null },
        { title: 'هشدارهای قیمت', icon: AlertTriangle, path: '/price-alerts', badge: null },
      ]
    },
    {
      id: 'ai',
      title: 'هوش مصنوعی و تحلیل',
      icon: Brain,
      expandable: true,
      children: [
        { title: 'دستیار هوشمند', icon: Brain, path: '/ai/dashboard', badge: 'AI' },
        { title: 'مشاور AI', icon: Bot, path: '/ai/assistant', badge: 'جدید' },
        { title: 'پیشنهادات AI', icon: Lightbulb, path: '/ai/recommendations', badge: null },
        { title: 'تحلیل بازار', icon: Search, path: '/market-analysis', badge: null },
        { title: 'تحلیل پرتفوی', icon: BarChart3, path: '/ai/portfolio-analysis', badge: null },
        { title: 'ربات معاملاتی', icon: Bot, path: '/trading-bot', badge: 'به زودی' },
        { title: 'سیگنال‌های هوشمند', icon: Smartphone, path: '/smart-signals', badge: null },
      ]
    },
    {
      id: 'services',
      title: 'خدمات و ابزارها',
      icon: Gem,
      expandable: true,
      children: [
        { title: 'استیکینگ', icon: Coins, path: '/staking', badge: 'KYC 1', disabled: user?.kyc_level < 1 },
        { title: 'فارمینگ', icon: Wheat, path: '/farming', badge: null },
        { title: 'تبدیل ارز', icon: ArrowRightLeft, path: '/currency-exchange', badge: 'جدید' },
        { title: 'بازارهای متنوع', icon: Gem, path: '/multi-asset', badge: null },
        { title: 'پاداش‌ها', icon: Gift, path: '/rewards', badge: null },
        { title: 'آکادمی', icon: HelpCircle, path: '/academy', badge: null },
      ]
    },
    {
      id: 'support',
      title: 'پشتیبانی و قانونی',
      icon: HelpCircle,
      expandable: true,
      children: [
        { title: 'تیکت پشتیبانی', icon: Ticket, path: '/support-tickets', badge: null },
        { title: 'تماس با ما', icon: Phone, path: '/contact-us', badge: null },
        { title: 'مدارک KYC', icon: FileText, path: '/kyc', badge: user?.kyc_level === 0 ? 'اقدام کنید' : null },
        { title: 'قوانین و مقررات', icon: FileText, path: '/terms', badge: null },
      ]
    }
  ];

    // Filter items based on KYC level
    if (user?.kyc_level < 2) {
      // Remove trading-related items for users without KYC level 2
      const tradingSection = baseItems.find(item => item.id === 'trading');
      if (tradingSection) {
        tradingSection.children = tradingSection.children.filter(child => 
          !['معاملات', 'سابقه معاملات', 'سفارشات باز'].includes(child.title)
        );
      }
      
      // Remove advanced AI features for users without proper KYC
      const aiSection = baseItems.find(item => item.id === 'ai');
      if (aiSection) {
        aiSection.children = aiSection.children.filter(child => 
          !['ربات معاملاتی', 'سیگنال‌های هوشمند'].includes(child.title)
        );
      }
    }

    return baseItems;
  };

  const menuItems = getMenuItems();

  // Special items (outside sections) - only show game if KYC is pending/not approved
  const specialItems = user?.kyc_status !== 'approved' ? [] : 
    user?.kyc_level < 2 ? [
      {
        id: 'kyc-game',
        title: 'بازی انتظار KYC',
        icon: Gamepad2,
        path: '/kyc-game',
        badge: 'بازی کنید!',
        className: 'bg-purple-600/20 border border-purple-500/30 hover:bg-purple-600/30'
      }
    ] : [];

  const isActiveRoute = (path) => {
    return location.pathname === path;
  };

  const renderMenuItem = (item, isChild = false) => {
    const Icon = item.icon;
    const isActive = isActiveRoute(item.path);
    const isDisabled = item.disabled;

    if (item.expandable) {
      const isExpanded = expandedSections[item.id];
      return (
        <div key={item.id} className="w-full">
          <Button
            variant="ghost"
            className={`w-full h-auto py-3 px-4 ${isChild ? 'mr-4' : ''} text-white hover:bg-slate-700`}
            onClick={() => toggleSection(item.id)}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-3 flex-1">
                <Icon className="w-5 h-5 shrink-0" />
                <span className="text-sm font-medium text-right">{item.title}</span>
              </div>
              {isExpanded ? 
                <ChevronDown className="w-4 h-4 shrink-0" /> : 
                <ChevronRight className="w-4 h-4 shrink-0" />
              }
            </div>
          </Button>
          
          {isExpanded && (
            <div className="mr-6 mt-1 space-y-1 border-r border-slate-600">
              {item.children.map(child => renderMenuItem(child, true))}
            </div>
          )}
        </div>
      );
    }

    return (
      <Button
        key={item.path || item.id}
        variant={isActive ? "secondary" : "ghost"}
        className={`w-full h-auto py-3 px-4 ${isChild ? 'mr-4' : ''} text-white hover:bg-slate-700 ${
          isDisabled ? 'opacity-50 cursor-not-allowed' : ''
        } ${item.className || ''}`}
        onClick={() => !isDisabled && navigate(item.path)}
        disabled={isDisabled}
      >
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <Icon className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium text-right truncate">{item.title}</span>
          </div>
          {item.badge && (
            <Badge 
              variant={item.badge === 'جدید' || item.badge === 'بازی کنید!' ? "default" : 
                     item.badge === 'اقدام کنید' ? "destructive" : "secondary"}
              className="text-xs shrink-0 mr-2"
            >
              {item.badge}
            </Badge>
          )}
        </div>
      </Button>
    );
  };

  return (
    <div className="flex h-screen bg-slate-900" dir="rtl">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:static inset-y-0 right-0 z-50 w-80 bg-slate-800 border-l border-slate-700 
        transform ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'} 
        md:translate-x-0 transition-transform duration-300 ease-in-out
        flex flex-col overflow-hidden
      `}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-slate-700 shrink-0">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shrink-0">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="text-white font-semibold text-sm leading-tight">صرافی کریپتو ایران</h2>
                <p className="text-gray-400 text-xs truncate">{user?.full_name || 'کاربر'}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden shrink-0"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Wallet Balance with Refresh */}
          <div className="mt-3 p-3 bg-slate-700/50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="text-xs text-gray-400 mb-1">موجودی کیف پول</div>
                <div className="text-emerald-400 font-bold text-lg">
                  {new Intl.NumberFormat('fa-IR').format(user?.wallet_balance_tmn || 0)} تومان
                </div>
              </div>
              <button
                onClick={async () => {
                  try {
                    const token = localStorage.getItem('token');
                    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/me`, {
                      headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await response.json();
                    window.location.reload(); // Simple refresh
                  } catch (error) {
                    console.error('Refresh error:', error);
                  }
                }}
                className="p-2 hover:bg-slate-600 rounded-lg transition-colors"
                title="بروزرسانی موجودی"
              >
                <svg className="w-5 h-5 text-gray-400 hover:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* KYC Status Warning */}
          {user?.kyc_status !== 'approved' && (
            <div className="mt-4 p-4 bg-gradient-to-br from-amber-600/20 to-orange-600/20 border-2 border-amber-500 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-5 h-5 text-amber-400" />
                <span className="text-amber-300 font-bold text-sm">احراز هویت لازم است!</span>
              </div>
              <p className="text-amber-200 text-xs mb-3 leading-relaxed">
                برای دسترسی به امکانات صرافی، لطفاً احراز هویت خود را تکمیل کنید و منتظر تایید ادمین باشید.
              </p>
              <Button
                variant="default"
                size="sm"
                className="w-full bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs h-9"
                onClick={() => navigate('/kyc')}
              >
                <Shield className="w-4 h-4 ml-1" />
                تکمیل احراز هویت
              </Button>
            </div>
          )}

          {/* KYC Status (for approved users) */}
          {user?.kyc_status === 'approved' && (
            <div className="mt-4 p-3 bg-slate-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-300">وضعیت KYC:</span>
                <Badge 
                  variant={user?.kyc_level === 2 ? "default" : user?.kyc_level === 1 ? "secondary" : "destructive"}
                  className="text-xs"
                >
                  سطح {user?.kyc_level || 0}
                </Badge>
              </div>
              {user?.kyc_level < 2 && (
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs h-8"
                  onClick={() => navigate('/kyc-game')}
                >
                  <Gamepad2 className="w-3 h-3 ml-1" />
                  <span>بازی کنید</span>
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-2 py-4 space-y-2">
          {/* Dashboard */}
          <div className="mb-4">
            {renderMenuItem(menuItems[0])}
          </div>

          {/* Special Items */}
          <div className="space-y-2 mb-4">
            {specialItems.map(item => renderMenuItem(item))}
          </div>

          <div className="border-t border-slate-700 my-4 mx-2"></div>

          {/* Main Sections */}
          <div className="space-y-2">
            {menuItems.slice(1).map(section => renderMenuItem(section))}
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-700">
          <Button
            variant="ghost"
            className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-900/20"
            onClick={onLogout}
          >
            <LogOut className="w-5 h-5 ml-2" />
            خروج از حساب
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <div className="md:hidden bg-slate-800 border-b border-slate-700 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-white font-semibold">صرافی کریپتو ایران</h1>
            <div className="flex items-center gap-2">
              <NotificationBell />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default UserSidebarLayout;