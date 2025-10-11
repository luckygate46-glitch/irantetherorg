import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { User, Wallet, CreditCard, Shield, Bell, Save, Plus, Trash2, Copy, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserProfile = ({ user, onUserUpdate }) => {
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  });
  
  const [walletAddresses, setWalletAddresses] = useState([]);
  const [bankingInfo, setBankingInfo] = useState({
    card_number: '',
    bank_name: '',
    account_holder: '',
    iban: ''
  });
  
  const [newWallet, setNewWallet] = useState({
    symbol: 'BTC',
    address: '',
    label: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  const cryptoOptions = [
    { symbol: 'BTC', name: 'Bitcoin', icon: '₿' },
    { symbol: 'ETH', name: 'Ethereum', icon: 'Ξ' },
    { symbol: 'USDT', name: 'Tether', icon: '₮' },
    { symbol: 'BNB', name: 'Binance Coin', icon: 'Ⓑ' },
    { symbol: 'ADA', name: 'Cardano', icon: '₳' },
    { symbol: 'DOT', name: 'Polkadot', icon: '●' },
    { symbol: 'SOL', name: 'Solana', icon: '◎' },
    { symbol: 'XRP', name: 'Ripple', icon: 'X' }
  ];

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      // Fetch wallet addresses
      const walletsResponse = await axios.get(`${API}/user/wallet-addresses`, config);
      setWalletAddresses(walletsResponse.data || []);

      // Fetch banking info  
      const bankingResponse = await axios.get(`${API}/user/banking-info`, config);
      setBankingInfo(bankingResponse.data || {});

    } catch (error) {
      console.error('Error fetching user data:', error);
      // Set mock data for demo
      setWalletAddresses([
        {
          id: '1',
          symbol: 'BTC',
          address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
          label: 'کیف پول اصلی',
          verified: true
        },
        {
          id: '2', 
          symbol: 'ETH',
          address: '0x742d35Cc6635C0532925a3b8D784d584d8F851de',
          label: 'کیف پول دوم',
          verified: false
        }
      ]);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.put(`${API}/user/profile`, profileData, config);
      
      if (onUserUpdate) {
        onUserUpdate(response.data);
      }
      
      alert('پروفایل با موفقیت بروزرسانی شد');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('خطا در بروزرسانی پروفایل');
    } finally {
      setLoading(false);
    }
  };

  const handleAddWallet = async () => {
    if (!newWallet.address || !newWallet.symbol) {
      alert('لطفا آدرس کیف پول و نوع ارز را وارد کنید');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const response = await axios.post(`${API}/user/wallet-addresses`, newWallet, config);
      
      setWalletAddresses([...walletAddresses, response.data]);
      setNewWallet({ symbol: 'BTC', address: '', label: '' });
      alert('آدرس کیف پول با موفقیت اضافه شد');
    } catch (error) {
      console.error('Error adding wallet:', error);
      alert('خطا در افزودن کیف پول');
    }
  };

  const handleDeleteWallet = async (walletId) => {
    if (!confirm('آیا از حذف این کیف پول اطمینان دارید؟')) return;

    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      await axios.delete(`${API}/user/wallet-addresses/${walletId}`, config);
      
      setWalletAddresses(walletAddresses.filter(w => w.id !== walletId));
      alert('کیف پول حذف شد');
    } catch (error) {
      console.error('Error deleting wallet:', error);
      alert('خطا در حذف کیف پول');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('آدرس کپی شد');
  };

  const validateWalletAddress = (symbol, address) => {
    // Basic validation - just check if address has minimum length
    // Admin will verify the actual address validity
    if (!address || address.trim().length < 20) {
      return false;
    }
    
    // Very basic pattern checking - accept most common formats
    const patterns = {
      BTC: /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$/,
      ETH: /^0x[a-fA-F0-9]{40}$/,
      USDT: /^(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[A-Za-z1-9]{33})$/,  // ERC20, Omni, TRC20
      BNB: /^(bnb[a-z0-9]{39}|0x[a-fA-F0-9]{40})$/,
      ADA: /^addr1[a-z0-9]{50,}$/,
      DOT: /^1[a-zA-Z0-9]{46,47}$/,
      SOL: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/,
      XRP: /^r[a-zA-Z0-9]{24,34}$/
    };

    // If no pattern for this symbol, just check minimum length
    if (!patterns[symbol]) {
      return address.trim().length >= 20;
    }

    return patterns[symbol].test(address);
  };

  return (
    <div className="p-6 space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <User className="w-8 h-8 text-blue-500" />
        <div>
          <h1 className="text-2xl font-bold text-white">پروفایل کاربری</h1>
          <p className="text-gray-400">مدیریت اطلاعات شخصی و کیف پول‌ها</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-slate-800 rounded-lg p-1 mb-6">
        {[
          { id: 'profile', label: 'اطلاعات شخصی', icon: User },
          { id: 'wallets', label: 'کیف پول‌ها', icon: Wallet },
          { id: 'banking', label: 'اطلاعات بانکی', icon: CreditCard },
          { id: 'security', label: 'امنیت', icon: Shield }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "ghost"}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 flex-1"
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </Button>
          );
        })}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <User className="w-5 h-5" />
              اطلاعات شخصی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">نام</label>
                  <input
                    type="text"
                    value={profileData.first_name}
                    onChange={(e) => setProfileData({...profileData, first_name: e.target.value})}
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">نام خانوادگی</label>
                  <input
                    type="text"
                    value={profileData.last_name}
                    onChange={(e) => setProfileData({...profileData, last_name: e.target.value})}
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">ایمیل</label>
                  <input
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">شماره موبایل</label>
                  <input
                    type="tel"
                    value={profileData.phone}
                    onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                    required
                  />
                </div>
              </div>
              
              <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700">
                <Save className="w-4 h-4 mr-2" />
                {loading ? 'در حال ذخیره...' : 'ذخیره تغییرات'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Wallets Tab */}
      {activeTab === 'wallets' && (
        <div className="space-y-6">
          {/* Add New Wallet */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Plus className="w-5 h-5" />
                افزودن کیف پول جدید
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">نوع ارز</label>
                  <select
                    value={newWallet.symbol}
                    onChange={(e) => setNewWallet({...newWallet, symbol: e.target.value})}
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  >
                    {cryptoOptions.map(crypto => (
                      <option key={crypto.symbol} value={crypto.symbol}>
                        {crypto.icon} {crypto.name} ({crypto.symbol})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">آدرس کیف پول</label>
                  <input
                    type="text"
                    value={newWallet.address}
                    onChange={(e) => setNewWallet({...newWallet, address: e.target.value})}
                    placeholder="آدرس کیف پول خود را وارد کنید"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                    required
                  />
                  {newWallet.address && (
                    <div className="mt-1">
                      {validateWalletAddress(newWallet.symbol, newWallet.address) ? (
                        <span className="text-green-400 text-xs flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" />
                          آدرس معتبر
                        </span>
                      ) : (
                        <span className="text-red-400 text-xs flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          آدرس نامعتبر
                        </span>
                      )}
                    </div>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">برچسب (اختیاری)</label>
                  <input
                    type="text"
                    value={newWallet.label}
                    onChange={(e) => setNewWallet({...newWallet, label: e.target.value})}
                    placeholder="مثال: کیف پول اصلی"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>
              </div>
              
              <Button 
                onClick={handleAddWallet} 
                className="mt-4 bg-green-600 hover:bg-green-700"
                disabled={!newWallet.address || !validateWalletAddress(newWallet.symbol, newWallet.address)}
              >
                <Plus className="w-4 h-4 mr-2" />
                افزودن کیف پول
              </Button>
            </CardContent>
          </Card>

          {/* Existing Wallets */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Wallet className="w-5 h-5" />
                کیف پول‌های شما
              </CardTitle>
            </CardHeader>
            <CardContent>
              {walletAddresses.length === 0 ? (
                <div className="text-center py-8">
                  <Wallet className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400 text-lg mb-2">هنوز کیف پولی اضافه نکرده‌اید</p>
                  <p className="text-gray-500 text-sm">
                    برای خرید ارز دیجیتال، ابتدا آدرس کیف پول خود را اضافه کنید
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {walletAddresses.map((wallet) => (
                    <div key={wallet.id} className="bg-slate-800 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-bold">
                              {cryptoOptions.find(c => c.symbol === wallet.symbol)?.icon || wallet.symbol}
                            </span>
                          </div>
                          <div>
                            <h3 className="text-white font-medium flex items-center gap-2">
                              {cryptoOptions.find(c => c.symbol === wallet.symbol)?.name || wallet.symbol}
                              {wallet.verified ? (
                                <Badge className="bg-green-600 text-xs">تایید شده</Badge>
                              ) : (
                                <Badge variant="outline" className="text-xs">در انتظار تایید</Badge>
                              )}
                            </h3>
                            {wallet.label && (
                              <p className="text-gray-400 text-sm">{wallet.label}</p>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyToClipboard(wallet.address)}
                          >
                            <Copy className="w-3 h-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeleteWallet(wallet.id)}
                            className="text-red-400 border-red-400 hover:bg-red-400/10"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="bg-slate-900 rounded p-3">
                        <p className="text-xs text-gray-400 mb-1">آدرس کیف پول:</p>
                        <p className="text-white font-mono text-sm break-all">{wallet.address}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Banking Tab */}
      {activeTab === 'banking' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <CreditCard className="w-5 h-5" />
              اطلاعات بانکی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">شماره کارت</label>
                  <input
                    type="text"
                    value={bankingInfo.card_number}
                    onChange={(e) => setBankingInfo({...bankingInfo, card_number: e.target.value})}
                    placeholder="0000-0000-0000-0000"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">نام بانک</label>
                  <input
                    type="text"
                    value={bankingInfo.bank_name}
                    onChange={(e) => setBankingInfo({...bankingInfo, bank_name: e.target.value})}
                    placeholder="نام بانک"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">نام صاحب حساب</label>
                  <input
                    type="text"
                    value={bankingInfo.account_holder}
                    onChange={(e) => setBankingInfo({...bankingInfo, account_holder: e.target.value})}
                    placeholder="نام و نام خانوادگی"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">شماره شبا</label>
                  <input
                    type="text"
                    value={bankingInfo.iban}
                    onChange={(e) => setBankingInfo({...bankingInfo, iban: e.target.value})}
                    placeholder="IR000000000000000000000000"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>
              </div>
              
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Save className="w-4 h-4 mr-2" />
                ذخیره اطلاعات بانکی
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Shield className="w-5 h-5" />
              تنظیمات امنیتی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="bg-slate-800 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">وضعیت KYC</h3>
                <div className="flex items-center gap-2">
                  <Badge variant={user?.kyc_level >= 2 ? "default" : "destructive"}>
                    سطح {user?.kyc_level || 0}
                  </Badge>
                  {user?.kyc_level >= 2 ? (
                    <span className="text-green-400 text-sm">احراز هویت تکمیل شده</span>
                  ) : (
                    <span className="text-orange-400 text-sm">احراز هویت ناقص</span>
                  )}
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-4">
                <h3 className="text-white font-medium mb-2">تغییر رمز عبور</h3>
                <div className="space-y-3">
                  <input
                    type="password"
                    placeholder="رمز عبور فعلی"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                  <input
                    type="password"
                    placeholder="رمز عبور جدید"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                  <input
                    type="password"
                    placeholder="تکرار رمز عبور جدید"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                  <Button className="bg-red-600 hover:bg-red-700">
                    تغییر رمز عبور
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default UserProfile;