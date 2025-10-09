import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { PieChart, TrendingUp, TrendingDown, DollarSign, Coins, BarChart3, RefreshCw } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Portfolio = ({ user }) => {
  const [holdings, setHoldings] = useState([]);
  const [totalValue, setTotalValue] = useState(0);
  const [totalValueTMN, setTotalValueTMN] = useState(0);
  const [profitLoss, setProfitLoss] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('token');
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      // Fetch user holdings
      const holdingsResponse = await axios.get(`${API}/user/holdings`, config);
      
      // Calculate total values
      const userHoldings = holdingsResponse.data || [];
      let total = 0;
      let totalTMN = 0;

      const enrichedHoldings = userHoldings.map(holding => {
        const currentPrice = Math.random() * 100000 + 50000; // Mock current price
        const currentValue = holding.amount * currentPrice;
        const purchaseValue = holding.amount * (holding.average_price || currentPrice * 0.9);
        const pnl = currentValue - purchaseValue;
        const pnlPercent = ((pnl / purchaseValue) * 100);

        total += currentValue;
        totalTMN += currentValue;

        return {
          ...holding,
          current_price: currentPrice,
          current_value: currentValue,
          pnl: pnl,
          pnl_percent: pnlPercent
        };
      });

      setHoldings(enrichedHoldings);
      setTotalValue(total);
      setTotalValueTMN(totalTMN);
      setProfitLoss(total * 0.05); // Mock 5% profit

    } catch (error) {
      console.error('Error fetching portfolio:', error);
      // Set mock data if API fails
      setHoldings([
        {
          symbol: 'BTC',
          amount: 0.025,
          average_price: 2100000000,
          current_price: 2150000000,
          current_value: 53750000,
          pnl: 1250000,
          pnl_percent: 2.38
        },
        {
          symbol: 'ETH', 
          amount: 0.5,
          average_price: 140000000,
          current_price: 145000000,
          current_value: 72500000,
          pnl: 2500000,
          pnl_percent: 3.57
        },
        {
          symbol: 'USDT',
          amount: 100,
          average_price: 520000,
          current_price: 525000,
          current_value: 52500000,
          pnl: 500000,
          pnl_percent: 0.96
        }
      ]);
      setTotalValue(178750000);
      setTotalValueTMN(178750000);
      setProfitLoss(4250000);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fa-IR').format(Math.round(price));
  };

  const formatCrypto = (amount) => {
    return amount.toFixed(8);
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6" dir="rtl">
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <span className="mr-3 text-white">در حال بارگذاری پرتفوی...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <PieChart className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-2xl font-bold text-white">پرتفوی من</h1>
            <p className="text-gray-400">مدیریت و بررسی دارایی‌های شما</p>
          </div>
        </div>
        
        <Button onClick={fetchPortfolioData} variant="outline" className="gap-2">
          <RefreshCw className="w-4 h-4" />
          بروزرسانی
        </Button>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              ارزش کل پرتفوی
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-2xl font-bold text-white">
                {formatPrice(totalValueTMN)} تومان
              </p>
              <p className="text-gray-400 text-sm">
                ≈ ${formatPrice(totalValue / 520000)}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              سود و زیان
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className={`text-2xl font-bold ${profitLoss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {profitLoss >= 0 ? '+' : ''}{formatPrice(profitLoss)} تومان
              </p>
              <p className="text-gray-400 text-sm">
                {profitLoss >= 0 ? '+' : ''}{((profitLoss / totalValue) * 100).toFixed(2)}%
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Coins className="w-5 h-5 text-purple-500" />
              تعداد دارایی‌ها
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-2xl font-bold text-white">{holdings.length}</p>
              <p className="text-gray-400 text-sm">ارز دیجیتال مختلف</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Holdings Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            دارایی‌های شما
          </CardTitle>
        </CardHeader>
        <CardContent>
          {holdings.length === 0 ? (
            <div className="text-center py-8">
              <Coins className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 text-lg mb-2">شما هنوز هیچ دارایی ندارید</p>
              <p className="text-gray-500 text-sm mb-4">
                برای شروع، از بخش معاملات اقدام به خرید کنید
              </p>
              <Button className="bg-blue-600 hover:bg-blue-700">
                شروع معامله
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-right py-3 px-4 text-gray-300 font-medium">ارز</th>
                    <th className="text-right py-3 px-4 text-gray-300 font-medium">موجودی</th>
                    <th className="text-right py-3 px-4 text-gray-300 font-medium">قیمت فعلی</th>
                    <th className="text-right py-3 px-4 text-gray-300 font-medium">ارزش</th>
                    <th className="text-right py-3 px-4 text-gray-300 font-medium">سود/زیان</th>
                    <th className="text-right py-3 px-4 text-gray-300 font-medium">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.map((holding, index) => (
                    <tr key={index} className="border-b border-slate-800 hover:bg-slate-800/50">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-white">
                              {holding.symbol.substring(0, 2)}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-white">{holding.symbol}</p>
                            <p className="text-xs text-gray-400">
                              {holding.symbol === 'BTC' ? 'Bitcoin' : 
                               holding.symbol === 'ETH' ? 'Ethereum' :
                               holding.symbol === 'USDT' ? 'Tether' : holding.symbol}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <p className="text-white font-medium">
                          {formatCrypto(holding.amount)}
                        </p>
                      </td>
                      <td className="py-4 px-4">
                        <p className="text-white">
                          {formatPrice(holding.current_price)} تومان
                        </p>
                      </td>
                      <td className="py-4 px-4">
                        <p className="text-white font-medium">
                          {formatPrice(holding.current_value)} تومان
                        </p>
                      </td>
                      <td className="py-4 px-4">
                        <div>
                          <p className={`font-medium ${holding.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {holding.pnl >= 0 ? '+' : ''}{formatPrice(holding.pnl)} تومان
                          </p>
                          <p className={`text-xs ${holding.pnl_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {holding.pnl_percent >= 0 ? '+' : ''}{holding.pnl_percent.toFixed(2)}%
                          </p>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" className="text-green-400 border-green-400 hover:bg-green-400/10">
                            خرید
                          </Button>
                          <Button size="sm" variant="outline" className="text-red-400 border-red-400 hover:bg-red-400/10">
                            فروش
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Portfolio Allocation Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <PieChart className="w-5 h-5" />
            توزیع دارایی‌ها
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-gray-400 mb-4">درصد هر دارایی از کل پرتفوی:</p>
              <div className="space-y-3">
                {holdings.map((holding, index) => {
                  const percentage = (holding.current_value / totalValue) * 100;
                  return (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${
                          index === 0 ? 'bg-orange-500' : 
                          index === 1 ? 'bg-blue-500' : 
                          index === 2 ? 'bg-green-500' : 'bg-purple-500'
                        }`}></div>
                        <span className="text-white">{holding.symbol}</span>
                      </div>
                      <span className="text-gray-300">{percentage.toFixed(1)}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="w-32 h-32 rounded-full border-8 border-gradient-to-r from-orange-500 via-blue-500 to-green-500 flex items-center justify-center mb-4">
                  <PieChart className="w-12 h-12 text-gray-400" />
                </div>
                <p className="text-gray-400 text-sm">نمودار توزیع دارایی‌ها</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Portfolio;