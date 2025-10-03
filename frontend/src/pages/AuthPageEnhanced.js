import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { ArrowRight, Mail, Lock, User, Phone, TrendingUp, CreditCard, Calendar, Shield } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AuthPageEnhanced({ onLogin }) {
  const [activeTab, setActiveTab] = useState("login");
  const { toast } = useToast();
  
  // Login state
  const [loginData, setLoginData] = useState({
    email: "",
    password: ""
  });
  
  // Register state with OTP (simplified)
  const [registerData, setRegisterData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: ""
  });

  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [otpVerified, setOtpVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);

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

  const sendOTP = async () => {
    if (!registerData.phone || registerData.phone.length !== 11) {
      toast({
        title: "خطا",
        description: "شماره موبایل باید 11 رقم باشد",
        variant: "destructive"
      });
      return;
    }

    setOtpLoading(true);
    try {
      await axios.post(`${API}/otp/send`, { phone: registerData.phone });
      setOtpSent(true);
      toast({
        title: "ارسال موفق",
        description: "کد تایید به شماره موبایل شما ارسال شد",
      });
    } catch (error) {
      toast({
        title: "خطا در ارسال کد",
        description: error.response?.data?.detail || "لطفا دوباره تلاش کنید",
        variant: "destructive"
      });
    } finally {
      setOtpLoading(false);
    }
  };

  const verifyOTP = async () => {
    if (!otpCode || otpCode.length !== 5) {
      toast({
        title: "خطا",
        description: "کد تایید باید 5 رقم باشد",
        variant: "destructive"
      });
      return;
    }

    setOtpLoading(true);
    try {
      await axios.post(`${API}/otp/verify`, { 
        phone: registerData.phone, 
        code: otpCode 
      });
      setOtpVerified(true);
      toast({
        title: "تایید موفق",
        description: "شماره موبایل شما تایید شد",
      });
    } catch (error) {
      toast({
        title: "خطا در تایید",
        description: error.response?.data?.detail || "کد وارد شده اشتباه است",
        variant: "destructive"
      });
    } finally {
      setOtpLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    if (!otpVerified) {
      toast({
        title: "خطا",
        description: "لطفا ابتدا شماره موبایل خود را تایید کنید",
        variant: "destructive"
      });
      return;
    }

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
        <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
          
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
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-6 rounded-lg"
                      >
                        {loading ? "در حال ورود..." : "ورود"}
                        {!loading && <ArrowRight className="mr-2 w-5 h-5" />}
                      </Button>
                    </form>
                  </TabsContent>

                  {/* Register Tab with OTP - SIMPLIFIED */}
                  <TabsContent value="register" className="space-y-4 mt-6">
                    <form onSubmit={handleRegister} className="space-y-4">
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

                      {/* Phone with OTP */}
                      <div className="space-y-2">
                        <Label htmlFor="register-phone" className="text-slate-200 flex items-center gap-2">
                          شماره موبایل
                          {otpVerified && <Shield className="w-4 h-4 text-emerald-400" />}
                        </Label>
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Phone className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                            <Input
                              id="register-phone"
                              data-testid="register-phone-input"
                              type="tel"
                              placeholder="09123456789"
                              value={registerData.phone}
                              onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
                              className="pr-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500"
                              disabled={otpVerified}
                              required
                            />
                          </div>
                          {!otpVerified && (
                            <Button
                              type="button"
                              onClick={sendOTP}
                              disabled={otpLoading || !registerData.phone}
                              className="bg-teal-600 hover:bg-teal-700"
                              data-testid="send-otp-button"
                            >
                              {otpLoading ? "..." : otpSent ? "ارسال مجدد" : "ارسال کد"}
                            </Button>
                          )}
                        </div>
                      </div>

                      {/* OTP Verification */}
                      {otpSent && !otpVerified && (
                        <div className="space-y-2 bg-teal-900/20 border border-teal-800/50 rounded-lg p-4">
                          <Label htmlFor="otp-code" className="text-slate-200">کد تایید (5 رقم)</Label>
                          <div className="flex gap-2">
                            <Input
                              id="otp-code"
                              data-testid="otp-code-input"
                              type="text"
                              maxLength={5}
                              placeholder="12345"
                              value={otpCode}
                              onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                              className="bg-slate-800/50 border-slate-700 text-white text-center text-lg tracking-widest"
                            />
                            <Button
                              type="button"
                              onClick={verifyOTP}
                              disabled={otpLoading || otpCode.length !== 5}
                              className="bg-emerald-600 hover:bg-emerald-700"
                              data-testid="verify-otp-button"
                            >
                              {otpLoading ? "..." : "تایید"}
                            </Button>
                          </div>
                        </div>
                      )}

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
                        disabled={loading || !otpVerified}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-6 rounded-lg disabled:opacity-50"
                      >
                        {loading ? "در حال ثبت‌نام..." : "ثبت‌نام"}
                        {!loading && <ArrowRight className="mr-2 w-5 h-5" />}
                      </Button>
                      
                      <p className="text-xs text-slate-400 text-center">
                        با ثبت‌نام، می‌توانید قیمت‌ها را مشاهده کنید. برای معامله باید احراز هویت کنید.
                      </p>
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
