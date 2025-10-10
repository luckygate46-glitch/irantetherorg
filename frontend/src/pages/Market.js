import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Search, ArrowRight } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Market({ user }) {
  const [prices, setPrices] = useState({});
  const [trending, setTrending] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMarketData = async () => {
    try {
      const [pricesRes, trendingRes] = await Promise.all([
        axios.get(`${API}/crypto/prices`),
        axios.get(`${API}/crypto/trending/coins`)
      ]);

      if (pricesRes.data.success) setPrices(pricesRes.data.data);
      if (trendingRes.data.success) setTrending(trendingRes.data.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const coinList = [
    { id: 'bitcoin', name: 'Bitcoin', symbol: 'BTC', icon: '₿' },
    { id: 'ethereum', name: 'Ethereum', symbol: 'ETH', icon: 'Ξ' },
    { id: 'tether', name: 'Tether', symbol: 'USDT', icon: '₮' },
    { id: 'binancecoin', name: 'BNB', symbol: 'BNB', icon: 'Ⓑ' },
    { id: 'ripple', name: 'Ripple', symbol: 'XRP', icon: 'Ʀ' },
    { id: 'cardano', name: 'Cardano', symbol: 'ADA', icon: '₳' },
    { id: 'solana', name: 'Solana', symbol: 'SOL', icon: '◎' },
    { id: 'dogecoin', name: 'Dogecoin', symbol: 'DOGE', icon: 'Ð' },
  ];

  const filteredCoins = coinList.filter(coin => 
    coin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    coin.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950" dir="rtl">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-white">بازار ارزهای دیجیتال</h1>
            <Button onClick={() => navigate('/dashboard')} variant="outline" className="border-slate-700">
              داشبورد
            </Button>
          </div>
          
          <div className="relative max-w-md">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <Input
              type="text"
              placeholder="جستجوی ارز دیجیتال..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pr-10 bg-slate-800/50 border-slate-700 text-white"
            />
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {trending.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-amber-400" />
              ارزهای پرطرفدار
            </h2>
            <div className="flex gap-4 overflow-x-auto pb-4">
              {trending.slice(0, 5).map((coin) => (
                <Card key={coin.id} className="min-w-[200px] bg-slate-900/50 border-slate-800">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <img src={coin.thumb} alt={coin.name} className="w-8 h-8 rounded-full" />
                      <div>
                        <p className="text-white font-semibold">{coin.symbol.toUpperCase()}</p>
                        <p className="text-xs text-slate-400">{coin.name}</p>
                      </div>
                    </div>
                    <Badge className="mt-2 bg-amber-600">#{coin.market_cap_rank}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        <div className="grid gap-4">
          {filteredCoins.map((coin) => {
            const coinData = prices[coin.id];
            if (!coinData) return null;

            // Now prices are in Toman from Nobitex
            const price = coinData.price_tmn || 0;
            const change = coinData.change_24h || 0;
            const isPositive = change >= 0;

            return (
              <Card 
                key={coin.id} 
                className="bg-slate-900/50 border-slate-800 hover:border-emerald-600 transition-colors"
                data-testid={`coin-card-${coin.id}`}
              >
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-full flex items-center justify-center text-2xl">
                        {coin.icon}
                      </div>
                      <div>
                        <h3 className="text-white font-bold text-lg">{coin.symbol}</h3>
                        <p className="text-slate-400 text-sm">{coin.name}</p>
                      </div>
                    </div>

                    <div className="text-center md:text-right">
                      <p className="text-slate-400 text-xs mb-1">قیمت فعلی</p>
                      <p className="text-white font-bold text-xl">
                        {price.toLocaleString('fa-IR')} تومان
                      </p>
                    </div>

                    <div className="text-center md:text-right">
                      <p className="text-slate-400 text-xs mb-1">تغییرات 24 ساعت</p>
                      <div className="flex items-center justify-center md:justify-start gap-2">
                        {isPositive ? (
                          <TrendingUp className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <TrendingDown className="w-5 h-5 text-red-400" />
                        )}
                        <span className={`font-bold text-lg ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                          {isPositive ? '+' : ''}{change.toFixed(2)}%
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-center">
                      <Button 
                        className="bg-emerald-600 hover:bg-emerald-700 w-full md:w-auto"
                        onClick={() => {
                          if (user?.kyc_level >= 1) {
                            navigate(`/trade/${coin.id}`);
                          } else {
                            navigate('/kyc');
                          }
                        }}
                      >
                        معامله
                        <ArrowRight className="mr-2 w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
