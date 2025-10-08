import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Coins,
  TrendingUp,
  Lock,
  Unlock,
  Clock,
  Target,
  Percent,
  DollarSign,
  Calendar,
  Shield,
  Zap,
  BarChart3,
  RefreshCw,
  Star,
  AlertTriangle,
  CheckCircle,
  Settings,
  Layers,
  Gem
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StakingYieldFarming = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('staking_pools');
  const [stakingPools, setStakingPools] = useState([]);
  const [yieldPools, setYieldPools] = useState([]);
  const [userPositions, setUserPositions] = useState([]);
  const [selectedPool, setSelectedPool] = useState(null);
  const [stakeAmount, setStakeAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchPoolData();
    fetchUserPositions();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchPoolData();
      fetchUserPositions();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [user, navigate]);

  const fetchPoolData = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get(`${API}/staking/pools`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      setStakingPools(response.data.staking_pools || []);
      // Mock yield farming pools
      setYieldPools([
        {
          id: '1',
          pool_name: 'BTC-ETH LP',
          token_a_symbol: 'BTC',
          token_b_symbol: 'ETH',
          pool_ratio: '50:50',
          annual_percentage_yield: 15.8,
          total_value_locked: 125000000000,
          farming_rewards_token: 'FARM',
          status: 'active'
        },
        {
          id: '2',
          pool_name: 'ETH-USDT LP',
          token_a_symbol: 'ETH',
          token_b_symbol: 'USDT',
          pool_ratio: '50:50',
          annual_percentage_yield: 12.4,
          total_value_locked: 89000000000,
          farming_rewards_token: 'FARM',
          status: 'active'
        }
      ]);
    } catch (error) {
      console.error('خطا در دریافت اطلاعات استخرها:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری اطلاعات استخرها',
        variant: 'destructive'
      });
    } finally {
      setRefreshing(false);
    }
  };

  const fetchUserPositions = async () => {
    try {
      // Mock user positions - replace with real API call
      setUserPositions([]);
    } catch (error) {
      console.error('خطا در دریافت پوزیشن‌های کاربر:', error);
    }
  };

  const handleStake = async (pool) => {
    if (!stakeAmount || parseFloat(stakeAmount) <= 0) {
      toast({
        title: 'مبلغ نامعتبر',
        description: 'لطفاً مبلغ معتبری برای استیک وارد کنید',
        variant: 'destructive'
      });
      return;
    }

    if (parseFloat(stakeAmount) < pool.minimum_stake) {
      toast({
        title: 'مبلغ کمتر از حداقل',
        description: `حداقل مبلغ استیک ${pool.minimum_stake} ${pool.asset_symbol} است`,
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/staking/stake`, {
        pool_id: pool.id,
        staked_amount: parseFloat(stakeAmount),
        auto_compound: true
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      toast({
        title: 'استیک موفق',
        description: response.data.message,
      });

      setStakeAmount('');
      setSelectedPool(null);
      fetchUserPositions();
    } catch (error) {
      toast({
        title: 'خطا در استیک',
        description: error.response?.data?.detail || 'خطا در فرآیند استیک',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(amount));
  };

  const formatPercent = (percent) => {
    return `${percent?.toFixed(1) || 0}%`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-600 text-white';
      case 'full': return 'bg-yellow-600 text-white';
      case 'maintenance': return 'bg-orange-600 text-white';
      case 'closed': return 'bg-red-600 text-white';
      default: return 'bg-slate-600 text-white';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'فعال';
      case 'full': return 'پر';
      case 'maintenance': return 'تعمیرات';
      case 'closed': return 'بسته';
      default: return status;
    }
  };

  const getLockPeriodText = (days) => {
    if (days === 0) return 'بدون قفل';
    if (days === 1) return '1 روز';
    if (days < 30) return `${days} روز`;
    if (days < 365) return `${Math.round(days / 30)} ماه`;
    return `${Math.round(days / 365)} سال`;
  };

  const renderStakingPool = (pool) => (
    <Card key={pool.id} className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Coins className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{pool.asset_symbol}</h3>
              <p className="text-sm text-slate-400">{pool.pool_name}</p>
            </div>
          </div>
          <Badge className={getStatusColor(pool.status)}>
            {getStatusText(pool.status)}
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-slate-800/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <Percent className="w-4 h-4 text-green-400" />
              <span className="text-sm text-slate-400">بازده سالانه</span>
            </div>
            <div className="text-xl font-bold text-green-400">
              {formatPercent(pool.annual_percentage_yield)}
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <Lock className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-slate-400">دوره قفل</span>
            </div>
            <div className="text-lg font-semibold text-blue-400">
              {getLockPeriodText(pool.lock_period_days)}
            </div>
          </div>
        </div>

        <div className="space-y-2 mb-4 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-400">حداقل استیک:</span>
            <span className="text-white">{pool.minimum_stake} {pool.asset_symbol}</span>
          </div>
          
          {pool.maximum_stake && (
            <div className="flex justify-between">
              <span className="text-slate-400">حداکثر استیک:</span>
              <span className="text-white">{pool.maximum_stake} {pool.asset_symbol}</span>
            </div>
          )}
          
          <div className="flex justify-between">
            <span className="text-slate-400">کل استیک شده:</span>
            <span className="text-emerald-400">{formatCurrency(pool.total_staked || 0)} {pool.asset_symbol}</span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-slate-400">پاداش:</span>
            <span className="text-purple-400">{pool.rewards_distributed_daily ? 'روزانه' : 'هفتگی'}</span>
          </div>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-3 mb-4">
          <p className="text-xs text-slate-400">{pool.description || 'استیک کردن برای کسب درآمد ثابت و حمایت از شبکه'}</p>
        </div>

        <Button 
          onClick={() => setSelectedPool(pool)}
          disabled={pool.status !== 'active'}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700"
        >
          {pool.status === 'active' ? 'استیک کردن' : 'غیرفعال'}
        </Button>
      </CardContent>
    </Card>
  );

  const renderYieldPool = (pool) => (
    <Card key={pool.id} className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">{pool.pool_name}</h3>
              <p className="text-sm text-slate-400">
                {pool.token_a_symbol}/{pool.token_b_symbol} • {pool.pool_ratio}
              </p>
            </div>
          </div>
          <Badge className={getStatusColor(pool.status)}>
            {getStatusText(pool.status)}
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-slate-800/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <Percent className="w-4 h-4 text-green-400" />
              <span className="text-sm text-slate-400">بازده سالانه</span>
            </div>
            <div className="text-xl font-bold text-green-400">
              {formatPercent(pool.annual_percentage_yield)}
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-slate-400">TVL</span>
            </div>
            <div className="text-lg font-semibold text-blue-400">
              {formatCurrency(pool.total_value_locked)} ت
            </div>
          </div>
        </div>

        <div className="space-y-2 mb-4 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-400">پاداش در:</span>
            <span className="text-purple-400">{pool.farming_rewards_token}</span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-slate-400">محافظت IL:</span>
            <span className={pool.impermanent_loss_protection ? 'text-green-400' : 'text-red-400'}>
              {pool.impermanent_loss_protection ? 'بله' : 'خیر'}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-3 mb-4">
          <p className="text-xs text-slate-400">
            ارائه نقدینگی و کسب درآمد از کارمزد معاملات و پاداش‌های فارمینگ
          </p>
        </div>

        <Button 
          disabled={pool.status !== 'active'}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-700"
        >
          {pool.status === 'active' ? 'ورود به استخر' : 'غیرفعال'}
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <Gem className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">استیکینگ و فارمینگ</h1>
              {refreshing && <div className="animate-spin w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full"></div>}
            </div>
            <nav className="flex gap-4">
              <Button 
                onClick={() => navigate('/dashboard')}
                variant="ghost"
                className="text-slate-300 hover:text-white"
              >
                داشبورد
              </Button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button onClick={fetchPoolData} variant="outline" size="sm" disabled={refreshing}>
              <RefreshCw className="w-4 h-4" />
            </Button>
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
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 bg-slate-800 p-1 rounded-lg">
          {[
            { id: 'staking_pools', label: 'استخرهای استیکینگ', icon: <Coins className="w-4 h-4" /> },
            { id: 'yield_farming', label: 'فارمینگ بازده', icon: <Layers className="w-4 h-4" /> },
            { id: 'my_positions', label: 'پوزیشن‌های من', icon: <Star className="w-4 h-4" /> }
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "ghost"}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2 flex-1"
            >
              {tab.icon}
              {tab.label}
            </Button>
          ))}
        </div>

        {/* Overview Stats */}
        <Card className="bg-slate-900 border-slate-800 mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              نمای کلی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-400">
                  {stakingPools.length}
                </div>
                <div className="text-sm text-slate-400">استخر استیکینگ</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  {yieldPools.length}
                </div>
                <div className="text-sm text-slate-400">استخر فارمینگ</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {stakingPools.reduce((avg, pool) => avg + (pool.annual_percentage_yield || 0), 0) / (stakingPools.length || 1)}%
                </div>
                <div className="text-sm text-slate-400">میانگین APY</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {userPositions.length}
                </div>
                <div className="text-sm text-slate-400">پوزیشن‌های شما</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* KYC Warning */}
        {user?.kyc_level < 1 && (
          <Card className="bg-yellow-900/20 border-yellow-800 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-yellow-400" />
                <div>
                  <h3 className="font-semibold text-yellow-400">احراز هویت مورد نیاز</h3>
                  <p className="text-sm text-yellow-300">
                    برای شرکت در استیکینگ و فارمینگ، لطفاً احراز هویت خود را تکمیل کنید.
                  </p>
                  <Button 
                    onClick={() => navigate('/kyc')} 
                    size="sm" 
                    className="mt-2 bg-yellow-600 hover:bg-yellow-700"
                  >
                    شروع احراز هویت
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Content based on active tab */}
        {activeTab === 'staking_pools' && (
          <>
            <h2 className="text-xl font-semibold mb-4">استخرهای استیکینگ</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {stakingPools.map(renderStakingPool)}
            </div>
          </>
        )}

        {activeTab === 'yield_farming' && (
          <>
            <h2 className="text-xl font-semibold mb-4">استخرهای فارمینگ بازده</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {yieldPools.map(renderYieldPool)}
            </div>
          </>
        )}

        {activeTab === 'my_positions' && (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-8 text-center">
              <Star className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">پوزیشنی ندارید</h3>
              <p className="text-slate-400 mb-4">
                هنوز در هیچ استخر استیکینگ یا فارمینگی شرکت نکرده‌اید
              </p>
              <Button 
                onClick={() => setActiveTab('staking_pools')}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                مشاهده استخرها
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Staking Modal */}
        {selectedPool && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-md m-4">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>استیک کردن {selectedPool.asset_symbol}</span>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setSelectedPool(null)}
                  >
                    ✕
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="bg-slate-800/50 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-400">بازده سالانه:</span>
                        <div className="text-green-400 font-semibold">
                          {formatPercent(selectedPool.annual_percentage_yield)}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-400">دوره قفل:</span>
                        <div className="text-blue-400 font-semibold">
                          {getLockPeriodText(selectedPool.lock_period_days)}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      مقدار برای استیک ({selectedPool.asset_symbol})
                    </label>
                    <Input
                      type="number"
                      step="0.00000001"
                      value={stakeAmount}
                      onChange={(e) => setStakeAmount(e.target.value)}
                      placeholder={`حداقل ${selectedPool.minimum_stake}`}
                      className="bg-slate-800 border-slate-700"
                    />
                    <div className="text-xs text-slate-500 mt-1">
                      حداقل: {selectedPool.minimum_stake} {selectedPool.asset_symbol}
                      {selectedPool.maximum_stake && ` • حداکثر: ${selectedPool.maximum_stake} ${selectedPool.asset_symbol}`}
                    </div>
                  </div>

                  {stakeAmount && parseFloat(stakeAmount) > 0 && (
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <div className="text-sm">
                        <div className="flex justify-between mb-1">
                          <span className="text-slate-400">درآمد سالانه تقریبی:</span>
                          <span className="text-green-400">
                            {formatCurrency(parseFloat(stakeAmount) * (selectedPool.annual_percentage_yield / 100))} {selectedPool.asset_symbol}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">درآمد ماهانه تقریبی:</span>
                          <span className="text-emerald-400">
                            {formatCurrency(parseFloat(stakeAmount) * (selectedPool.annual_percentage_yield / 100) / 12)} {selectedPool.asset_symbol}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button 
                      onClick={() => setSelectedPool(null)}
                      variant="outline"
                      className="flex-1"
                    >
                      انصراف
                    </Button>
                    <Button 
                      onClick={() => handleStake(selectedPool)}
                      disabled={loading || !stakeAmount || user?.kyc_level < 1}
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? 'در حال استیک...' : 'تأیید استیک'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default StakingYieldFarming;