import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { ArrowRightLeft, TrendingUp, Clock, AlertCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CurrencyExchange = ({ user }) => {
  const [fromCurrency, setFromCurrency] = useState('BTC');
  const [toCurrency, setToCurrency] = useState('ETH');
  const [amount, setAmount] = useState('');
  const [exchangeRate, setExchangeRate] = useState(0);
  const [estimatedOutput, setEstimatedOutput] = useState(0);
  const [loading, setLoading] = useState(false);
  const [exchangeHistory, setExchangeHistory] = useState([]);

  const currencies = [
    { code: 'BTC', name: 'Bitcoin', icon: '₿' },
    { code: 'ETH', name: 'Ethereum', icon: 'Ξ' },
    { code: 'ADA', name: 'Cardano', icon: '₳' },
    { code: 'DOT', name: 'Polkadot', icon: '●' },
    { code: 'USDT', name: 'Tether', icon: '₮' },
    { code: 'BNB', name: 'Binance Coin', icon: 'Ⓑ' }
  ];

  useEffect(() => {
    if (amount && fromCurrency && toCurrency) {
      calculateExchange();
    }
  }, [amount, fromCurrency, toCurrency]);

  const calculateExchange = async () => {
    try {
      setLoading(true);
      // Simulate exchange rate calculation
      const rate = Math.random() * 10 + 0.1;
      setExchangeRate(rate);
      setEstimatedOutput(parseFloat(amount) * rate);
    } catch (error) {
      console.error('Error calculating exchange:', error);
    } finally {
      setLoading(false);
    }
  };

  const swapCurrencies = () => {
    const temp = fromCurrency;
    setFromCurrency(toCurrency);
    setToCurrency(temp);
  };

  const handleExchange = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      alert('لطفا مقدار معتبر وارد کنید');
      return;
    }

    try {
      setLoading(true);
      
      // Simulate exchange transaction
      const newTransaction = {
        id: Date.now().toString(),
        from: fromCurrency,
        to: toCurrency,
        amount: parseFloat(amount),
        received: estimatedOutput,
        rate: exchangeRate,
        timestamp: new Date().toISOString(),
        status: 'completed'
      };

      setExchangeHistory([newTransaction, ...exchangeHistory]);
      setAmount('');
      setEstimatedOutput(0);
      
      alert('تبدیل ارز با موفقیت انجام شد!');
    } catch (error) {
      alert('خطا در انجام تبدیل ارز');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <div className="flex items-center gap-3 mb-6">
        <ArrowRightLeft className="w-8 h-8 text-blue-500" />
        <div>
          <h1 className="text-2xl font-bold text-white">تبدیل ارز</h1>
          <p className="text-gray-400">تبدیل آسان و سریع ارزهای دیجیتال</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Exchange Form */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <ArrowRightLeft className="w-5 h-5" />
              تبدیل ارز
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* From Currency */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                از ارز:
              </label>
              <div className="flex gap-2">
                <select
                  value={fromCurrency}
                  onChange={(e) => setFromCurrency(e.target.value)}
                  className="flex-1 bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                >
                  {currencies.map(currency => (
                    <option key={currency.code} value={currency.code}>
                      {currency.icon} {currency.name} ({currency.code})
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="مقدار"
                  className="w-32 bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                />
              </div>
            </div>

            {/* Swap Button */}
            <div className="flex justify-center">
              <Button
                variant="outline"
                size="sm"
                onClick={swapCurrencies}
                className="rounded-full w-10 h-10 p-0"
              >
                <ArrowRightLeft className="w-4 h-4" />
              </Button>
            </div>

            {/* To Currency */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                به ارز:
              </label>
              <div className="flex gap-2">
                <select
                  value={toCurrency}
                  onChange={(e) => setToCurrency(e.target.value)}
                  className="flex-1 bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                >
                  {currencies.map(currency => (
                    <option key={currency.code} value={currency.code}>
                      {currency.icon} {currency.name} ({currency.code})
                    </option>
                  ))}
                </select>
                <div className="w-32 bg-slate-800 border border-slate-600 rounded-md px-3 py-2 text-gray-300 flex items-center">
                  {estimatedOutput.toFixed(6)}
                </div>
              </div>
            </div>

            {/* Exchange Rate */}
            {exchangeRate > 0 && (
              <div className="bg-slate-800 rounded-lg p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">نرخ تبدیل:</span>
                  <span className="text-white">
                    1 {fromCurrency} = {exchangeRate.toFixed(6)} {toCurrency}
                  </span>
                </div>
              </div>
            )}

            {/* Exchange Button */}
            <Button
              onClick={handleExchange}
              disabled={loading || !amount || parseFloat(amount) <= 0}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  در حال انجام...
                </>
              ) : (
                <>
                  <ArrowRightLeft className="w-4 h-4 mr-2" />
                  تبدیل کن
                </>
              )}
            </Button>

            {/* Warning */}
            <div className="bg-orange-900/20 border border-orange-600/30 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5" />
                <div className="text-sm text-orange-300">
                  <p className="font-medium mb-1">توجه:</p>
                  <p>نرخ‌های تبدیل ممکن است تا زمان تأیید نهایی تغییر کند.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Exchange History */}
        <Card>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="w-5 h-5" />
              تاریخچه تبدیل
            </CardTitle>
          </CardHeader>
          <CardContent>
            {exchangeHistory.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                <p className="text-gray-400">هنوز تبدیل ارزی انجام نداده‌اید</p>
              </div>
            ) : (
              <div className="space-y-3">
                {exchangeHistory.map(transaction => (
                  <div key={transaction.id} className="bg-slate-800 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="text-white text-sm font-medium">
                          {transaction.from} → {transaction.to}
                        </span>
                      </div>
                      <Badge variant="success" className="text-xs">
                        {transaction.status === 'completed' ? 'موفق' : 'در انتظار'}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                      <div>مقدار: {transaction.amount} {transaction.from}</div>
                      <div>دریافت: {transaction.received.toFixed(6)} {transaction.to}</div>
                      <div>نرخ: {transaction.rate.toFixed(6)}</div>
                      <div>زمان: {new Date(transaction.timestamp).toLocaleTimeString('fa-IR')}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Popular Exchange Pairs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white">جفت ارزهای محبوب</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { from: 'BTC', to: 'ETH', rate: '15.234' },
              { from: 'ETH', to: 'ADA', rate: '1,245.67' },
              { from: 'BTC', to: 'USDT', rate: '43,250.00' },
              { from: 'ETH', to: 'USDT', rate: '2,840.50' }
            ].map((pair, index) => (
              <Button
                key={index}
                variant="outline"
                className="h-auto p-3 flex flex-col items-center gap-1"
                onClick={() => {
                  setFromCurrency(pair.from);
                  setToCurrency(pair.to);
                }}
              >
                <div className="text-sm font-medium">
                  {pair.from}/{pair.to}
                </div>
                <div className="text-xs text-gray-400">
                  {pair.rate}
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CurrencyExchange;