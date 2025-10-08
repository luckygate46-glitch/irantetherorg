import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Gift, Star, Trophy, Coins, Users, TrendingUp, Calendar, CheckCircle, Clock } from 'lucide-react';

const Rewards = ({ user }) => {
  const [userPoints, setUserPoints] = useState(1250);
  const [userLevel, setUserLevel] = useState('برنزی');
  const [claimedRewards, setClaimedRewards] = useState([]);
  const [dailyCheckIn, setDailyCheckIn] = useState({
    streak: 5,
    canClaim: true,
    lastClaim: null
  });

  const rewards = [
    {
      id: 1,
      title: 'بونوس خوش‌آمدگویی',
      description: 'پاداش ثبت‌نام موفق',
      points: 100,
      type: 'bonus',
      icon: Gift,
      color: 'bg-purple-600',
      available: true
    },
    {
      id: 2,
      title: 'تخفیف کارمزد معامله',
      description: '50% تخفیف کارمزد برای 7 روز',
      points: 500,
      type: 'discount',
      icon: TrendingUp,
      color: 'bg-green-600',
      available: true
    },
    {
      id: 3,
      title: 'پاداش KYC سطح 2',
      description: 'تکمیل احراز هویت کامل',
      points: 300,
      type: 'milestone',
      icon: CheckCircle,
      color: 'bg-blue-600',
      available: user?.kyc_level >= 2,
      requirement: 'KYC سطح 2'
    },
    {
      id: 4,
      title: 'پاداش معاملات',
      description: 'اتمام 10 معامله موفق',
      points: 200,
      type: 'trading',
      icon: Trophy,
      color: 'bg-yellow-600',
      available: false,
      requirement: '10 معامله موفق'
    },
    {
      id: 5,
      title: 'دعوت از دوستان',
      description: 'دعوت 3 کاربر جدید',
      points: 1000,
      type: 'referral',
      icon: Users,
      color: 'bg-indigo-600',
      available: false,
      requirement: '3 دعوت موفق'
    }
  ];

  const levels = [
    { name: 'برنزی', minPoints: 0, maxPoints: 999, benefits: ['پشتیبانی عادی', 'دسترسی به بازار'] },
    { name: 'نقره‌ای', minPoints: 1000, maxPoints: 4999, benefits: ['تخفیف 5% کارمزد', 'پشتیبانی اولویت‌دار'] },
    { name: 'طلایی', minPoints: 5000, maxPoints: 19999, benefits: ['تخفیف 10% کارمزد', 'دسترسی به سیگنال‌ها'] },
    { name: 'پلاتینیوم', minPoints: 20000, maxPoints: Infinity, benefits: ['تخفیف 20% کارمزد', 'مشاوره اختصاصی'] }
  ];

  const dailyTasks = [
    { id: 1, title: 'ورود روزانه', reward: 10, completed: true },
    { id: 2, title: 'مشاهده قیمت‌ها', reward: 5, completed: true },
    { id: 3, title: 'یک معامله انجام دهید', reward: 50, completed: false },
    { id: 4, title: 'بررسی اخبار', reward: 15, completed: false }
  ];

  const getCurrentLevel = () => {
    return levels.find(level => userPoints >= level.minPoints && userPoints <= level.maxPoints) || levels[0];
  };

  const getNextLevel = () => {
    const currentLevel = getCurrentLevel();
    const currentIndex = levels.indexOf(currentLevel);
    return levels[currentIndex + 1] || null;
  };

  const claimReward = (rewardId) => {
    const reward = rewards.find(r => r.id === rewardId);
    if (reward && reward.available && !claimedRewards.includes(rewardId)) {
      setUserPoints(userPoints + reward.points);
      setClaimedRewards([...claimedRewards, rewardId]);
      alert(`تبریک! شما ${reward.points} امتیاز دریافت کردید`);
    }
  };

  const claimDailyCheckIn = () => {
    if (dailyCheckIn.canClaim) {
      const bonusPoints = dailyCheckIn.streak * 10;
      setUserPoints(userPoints + bonusPoints);
      setDailyCheckIn({
        streak: dailyCheckIn.streak + 1,
        canClaim: false,
        lastClaim: new Date().toISOString()
      });
      alert(`تبریک! ${bonusPoints} امتیاز برای ${dailyCheckIn.streak + 1} روز ورود مداوم دریافت کردید`);
    }
  };

  const currentLevel = getCurrentLevel();
  const nextLevel = getNextLevel();
  const progressPercent = nextLevel ? 
    ((userPoints - currentLevel.minPoints) / (nextLevel.minPoints - currentLevel.minPoints)) * 100 : 100;

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <div className="flex items-center gap-3 mb-6">
        <Gift className="w-8 h-8 text-purple-500" />
        <div>
          <h1 className="text-2xl font-bold text-white">پاداش‌ها و امتیازات</h1>
          <p className="text-gray-400">امتیاز جمع کنید و از پاداش‌های ویژه بهره‌مند شوید</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Status */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              وضعیت امتیازات شما
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white">{userPoints.toLocaleString()}</h3>
                <p className="text-gray-400">امتیاز کل</p>
              </div>
              <Badge className="text-lg px-4 py-2" variant="secondary">
                {currentLevel.name}
              </Badge>
            </div>

            {nextLevel && (
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">پیشرفت تا سطح {nextLevel.name}</span>
                  <span className="text-white">
                    {userPoints}/{nextLevel.minPoints}
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(progressPercent, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  {nextLevel.minPoints - userPoints} امتیاز تا سطح بعدی
                </p>
              </div>
            )}

            <div className="bg-slate-800 rounded-lg p-4">
              <h4 className="text-white font-medium mb-2">مزایای سطح {currentLevel.name}:</h4>
              <ul className="text-sm text-gray-300 space-y-1">
                {currentLevel.benefits.map((benefit, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Daily Check-in */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-500" />
              ورود روزانه
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-1">
                {dailyCheckIn.streak}
              </div>
              <p className="text-gray-400 text-sm">روز مداوم</p>
            </div>

            <Button
              onClick={claimDailyCheckIn}
              disabled={!dailyCheckIn.canClaim}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {dailyCheckIn.canClaim ? (
                <>
                  <Gift className="w-4 h-4 mr-2" />
                  دریافت {dailyCheckIn.streak * 10} امتیاز
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  امروز دریافت شد
                </>
              )}
            </Button>

            <div className="text-center text-xs text-gray-400">
              امتیاز روزانه: {dailyCheckIn.streak * 10} امتیاز
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Available Rewards */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Gift className="w-5 h-5" />
              پاداش‌های در دسترس
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {rewards.map(reward => {
                const Icon = reward.icon;
                const isClaimed = claimedRewards.includes(reward.id);
                
                return (
                  <div
                    key={reward.id}
                    className={`
                      bg-slate-800 rounded-lg p-4 border
                      ${reward.available ? 'border-slate-600' : 'border-slate-700 opacity-50'}
                    `}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className={`p-2 rounded-lg ${reward.color}`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-white">{reward.title}</h3>
                        <p className="text-sm text-gray-400">{reward.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-yellow-500">
                          +{reward.points}
                        </div>
                        <div className="text-xs text-gray-400">امتیاز</div>
                      </div>
                    </div>
                    
                    {!reward.available && reward.requirement && (
                      <p className="text-xs text-orange-400 mb-2">
                        نیاز: {reward.requirement}
                      </p>
                    )}
                    
                    <Button
                      onClick={() => claimReward(reward.id)}
                      disabled={!reward.available || isClaimed}
                      className="w-full"
                      variant={isClaimed ? "secondary" : "default"}
                    >
                      {isClaimed ? (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          دریافت شد
                        </>
                      ) : reward.available ? (
                        <>
                          <Gift className="w-4 h-4 mr-2" />
                          دریافت پاداش
                        </>
                      ) : (
                        <>
                          <Clock className="w-4 h-4 mr-2" />
                          در دسترس نیست
                        </>
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Daily Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              ماموریت‌های روزانه
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dailyTasks.map(task => (
                <div
                  key={task.id}
                  className={`
                    bg-slate-800 rounded-lg p-3 border
                    ${task.completed ? 'border-green-600/30 bg-green-900/10' : 'border-slate-600'}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {task.completed ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <Clock className="w-5 h-5 text-gray-400" />
                      )}
                      <span className={`${task.completed ? 'text-green-300' : 'text-white'}`}>
                        {task.title}
                      </span>
                    </div>
                    <Badge variant={task.completed ? "success" : "secondary"}>
                      +{task.reward}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t border-slate-700">
              <p className="text-center text-sm text-gray-400">
                امتیاز کسب شده امروز: {dailyTasks.filter(t => t.completed).reduce((sum, t) => sum + t.reward, 0)} امتیاز
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Levels Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Trophy className="w-5 h-5" />
            سطح‌های امتیازات
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {levels.map((level, index) => (
              <div
                key={index}
                className={`
                  p-4 rounded-lg border-2 transition-all
                  ${level.name === currentLevel.name 
                    ? 'border-purple-500 bg-purple-900/20' 
                    : 'border-slate-600 bg-slate-800'
                  }
                `}
              >
                <div className="text-center mb-3">
                  <h3 className={`font-bold text-lg ${
                    level.name === currentLevel.name ? 'text-purple-300' : 'text-white'
                  }`}>
                    {level.name}
                  </h3>
                  <p className="text-sm text-gray-400">
                    {level.minPoints.toLocaleString()} - {
                      level.maxPoints === Infinity ? '∞' : level.maxPoints.toLocaleString()
                    } امتیاز
                  </p>
                </div>
                
                <ul className="text-xs text-gray-300 space-y-1">
                  {level.benefits.map((benefit, bIndex) => (
                    <li key={bIndex} className="flex items-center gap-1">
                      <div className="w-1 h-1 bg-gray-400 rounded-full" />
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Rewards;