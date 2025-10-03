import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { ArrowRight, Mail, Lock, User, Phone, TrendingUp } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AuthPage({ onLogin }) {
  const [activeTab, setActiveTab] = useState("login");
  const { toast } = useToast();
  
  // Login state
  const [loginData, setLoginData] = useState({
    email: "",
    password: ""
  });
  
  // Register state
  const [registerData, setRegisterData] = useState({
    email: "",
    password: "",
    full_name: "",
    phone: ""
  });

  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/login`, loginData);
      onLogin(response.data.access_token, response.data.user);
      toast({
        title: "ورود موفق",
        description: `خوش آمدید ${response.data.user.full_name}`,
      });
    } catch (error) {
      toast({
        title: "خطا در ورود",
        description: error.response?.data?.detail || "لطفا دوباره تلاش کنید",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/register`, registerData);
      onLogin(response.data.access_token, response.data.user);
      toast({
        title: "ثبت‌نام موفق",
        description: `حساب شما با موفقیت ایجاد شد`,
      });
    } catch (error) {
      toast({
        title: "خطا در ثبت‌نام",
        description: error.response?.data?.detail || "لطفا دوباره تلاش کنید",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden" dir="rtl">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 -right-20 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 -left-20 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-3xl"></div>
      </div>

      {/* Grid pattern overlay */}
      <div className="absolute inset-0" style={{
        backgroundImage: `radial-gradient(circle at 1px 1px, rgb(148 163 184 / 0.05) 1px, transparent 0)`,
        backgroundSize: '40px 40px'
      }}></div>

      <div className="relative z-10 container mx-auto px-4 py-12 flex items-center justify-center min-h-screen">
        <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
          
          {/* Right side - Branding */}
          <div className="text-white space-y-6 order-2 md:order-1">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-l from-emerald-400 to-teal-300 bg-clip-text text-transparent">
                صرافی کریپتو ایران
              </h1>
            </div>
            
            <h2 className="text-4xl md:text-5xl font-bold leading-tight">
              معاملات ارز دیجیتال
              <br />
              <span className="text-emerald-400">آسان و امن</span>
            </h2>
            
            <p className="text-slate-400 text-lg leading-relaxed">
              خرید و فروش بیت کوین، اتریوم و دیگر ارزهای دیجیتال با بهترین نرخ و سریع‌ترین تراکنش‌ها
            </p>

            <div className="grid grid-cols-3 gap-4 pt-6">
              <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-emerald-400">24/7</div>
                <div className="text-sm text-slate-400 mt-1">پشتیبانی</div>
              </div>
              <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-emerald-400">100%</div>
                <div className="text-sm text-slate-400 mt-1">امنیت</div>
              </div>
              <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-emerald-400">سریع</div>
                <div className="text-sm text-slate-400 mt-1">تراکنش</div>
              </div>
            </div>
          </div>

          {/* Left side - Auth Form */}
          <div className="order-1 md:order-2">
            <Card className="bg-slate-900/80 backdrop-blur-xl border-slate-800 shadow-2xl">
              <CardHeader className="text-center space-y-2">
                <CardTitle className="text-2xl text-white">به صرافی خوش آمدید</CardTitle>
                <CardDescription className="text-slate-400">
                  برای شروع معاملات وارد شوید یا ثبت‌نام کنید
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-2 bg-slate-800/50">
                    <TabsTrigger 
                      value="login"
                      data-testid="login-tab"
                      className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white"
                    >
                      ورود
                    </TabsTrigger>
                    <TabsTrigger 
                      value="register"
                      data-testid="register-tab"
                      className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white"
                    >
                      ثبت‌نام
                    </TabsTrigger>
                  </TabsList>

                  {/* Login Tab */}
                  <TabsContent value="login" className="space-y-4 mt-6">
                    <form onSubmit={handleLogin} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="login-email" className="text-slate-200">ایمیل یا نام کاربری</Label>
                        <div className="relative">
                          <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                          <Input
                            id="login-email"
                            data-testid="login-email-input"
                            type="text"
                            placeholder="admin یا email@example.com"
                            value={loginData.email}
                            onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                            className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="login-password" className="text-slate-200">رمز عبور</Label>
                        <div className="relative">
                          <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                          <Input
                            id="login-password"
                            data-testid="login-password-input"
                            type="password"
                            placeholder="رمز عبور خود را وارد کنید"
                            value={loginData.password}
                            onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                            className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>
                      </div>

                      <Button
                        type="submit"
                        data-testid="login-submit-button"
                        disabled={loading}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-6 rounded-lg transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                      >
                        {loading ? "در حال ورود..." : "ورود"}
                        {!loading && <ArrowRight className="mr-2 w-5 h-5" />}
                      </Button>
                    </form>
                  </TabsContent>

                  {/* Register Tab */}
                  <TabsContent value="register" className="space-y-4 mt-6">
                    <form onSubmit={handleRegister} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="register-name" className="text-slate-200">نام و نام خانوادگی</Label>
                        <div className="relative">
                          <User className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                          <Input
                            id="register-name"
                            data-testid="register-name-input"
                            type="text"
                            placeholder="نام کامل خود را وارد کنید"
                            value={registerData.full_name}
                            onChange={(e) => setRegisterData({...registerData, full_name: e.target.value})}
                            className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="register-email" className="text-slate-200">ایمیل</Label>
                        <div className="relative">
                          <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                          <Input
                            id="register-email"
                            data-testid="register-email-input"
                            type="email"
                            placeholder="email@example.com"
                            value={registerData.email}
                            onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                            className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="register-phone" className="text-slate-200">شماره موبایل (اختیاری)</Label>
                        <div className="relative">
                          <Phone className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                          <Input
                            id="register-phone"
                            data-testid="register-phone-input"
                            type="tel"
                            placeholder="09123456789"
                            value={registerData.phone}
                            onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
                            className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="register-password" className="text-slate-200">رمز عبور</Label>
                        <div className="relative">
                          <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                          <Input
                            id="register-password"
                            data-testid="register-password-input"
                            type="password"
                            placeholder="حداقل 6 کاراکتر"
                            value={registerData.password}
                            onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                            className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>
                      </div>

                      <Button
                        type="submit"
                        data-testid="register-submit-button"
                        disabled={loading}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-6 rounded-lg transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                      >
                        {loading ? "در حال ثبت‌نام..." : "ثبت‌نام"}
                        {!loading && <ArrowRight className="mr-2 w-5 h-5" />}
                      </Button>
                    </form>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}