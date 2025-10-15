import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Shield, CreditCard, Calendar, User, CheckCircle, AlertCircle, Upload } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function KYCPage({ user, onLogout }) {
  const [kycStatus, setKycStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Level 1 KYC Data
  const [level1Data, setLevel1Data] = useState({
    full_name: "",
    national_code: "",
    birth_date: "",
    bank_card_number: ""
  });

  // Level 2 KYC Data
  const [level2Data, setLevel2Data] = useState({
    id_card_photo: null,
    selfie_type: "photo",
    selfie_data: null
  });

  useEffect(() => {
    fetchKYCStatus();
  }, []);

  const fetchKYCStatus = async () => {
    try {
      const response = await axios.get(`${API}/kyc/status`);
      setKycStatus(response.data);
      
      // Set current step based on KYC level
      if (response.data.kyc_level === 0) {
        setCurrentStep(1);
      } else if (response.data.kyc_level === 1 && response.data.kyc_status === "approved") {
        setCurrentStep(2);
      }
    } catch (error) {
      console.error('Error fetching KYC status:', error);
    }
  };

  const handleLevel1Submit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/kyc/level1`, level1Data);
      toast({
        title: "موفق",
        description: response.data.message,
      });
      fetchKYCStatus();
      setCurrentStep(2);
    } catch (error) {
      toast({
        title: "خطا",
        description: error.response?.data?.detail || "لطفا دوباره تلاش کنید",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (field, file) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setLevel2Data(prev => ({
        ...prev,
        [field]: reader.result
      }));
    };
    reader.readAsDataURL(file);
  };

  const handleLevel2Submit = async (e) => {
    e.preventDefault();
    
    if (!level2Data.id_card_photo || !level2Data.selfie_data) {
      toast({
        title: "خطا",
        description: "لطفا تمام تصاویر را بارگذاری کنید",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/kyc/level2`, level2Data);
      toast({
        title: "موفق",
        description: response.data.message,
      });
      fetchKYCStatus();
    } catch (error) {
      toast({
        title: "خطا",
        description: error.response?.data?.detail || "لطفا دوباره تلاش کنید",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  if (!kycStatus) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950" dir="rtl">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">احراز هویت</h1>
          <div className="flex items-center gap-3">
            {user?.kyc_status === 'approved' && (
              <Button onClick={() => navigate('/dashboard')} variant="outline" className="border-slate-700 text-slate-300">
                بازگشت به داشبورد
              </Button>
            )}
            <Button 
              onClick={onLogout} 
              variant="outline" 
              className="border-red-700 text-red-400 hover:bg-red-900/20"
            >
              خروج
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                kycStatus.kyc_level >= 0 ? 'bg-emerald-600' : 'bg-slate-700'
              }`}>
                {kycStatus.kyc_level >= 0 ? <CheckCircle className="w-6 h-6 text-white" /> : <span>0</span>}
              </div>
              <div>
                <p className="text-white font-semibold">سطح 0</p>
                <p className="text-xs text-slate-400">ثبت‌نام</p>
              </div>
            </div>

            <div className="flex-1 h-1 bg-slate-700 mx-4">
              <div className={`h-full ${kycStatus.kyc_level >= 1 ? 'bg-emerald-600' : 'bg-slate-700'}`} style={{width: kycStatus.kyc_level >= 1 ? '100%' : '0%'}}></div>
            </div>

            <div className="flex items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                kycStatus.kyc_level >= 1 ? 'bg-emerald-600' : 'bg-slate-700'
              }`}>
                {kycStatus.kyc_level >= 1 ? <CheckCircle className="w-6 h-6 text-white" /> : <span>1</span>}
              </div>
              <div>
                <p className="text-white font-semibold">سطح 1</p>
                <p className="text-xs text-slate-400">پایه</p>
              </div>
            </div>

            <div className="flex-1 h-1 bg-slate-700 mx-4">
              <div className={`h-full ${kycStatus.kyc_level >= 2 ? 'bg-emerald-600' : 'bg-slate-700'}`} style={{width: kycStatus.kyc_level >= 2 ? '100%' : '0%'}}></div>
            </div>

            <div className="flex items-center gap-2">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                kycStatus.kyc_level >= 2 ? 'bg-emerald-600' : 'bg-slate-700'
              }`}>
                {kycStatus.kyc_level >= 2 ? <CheckCircle className="w-6 h-6 text-white" /> : <span>2</span>}
              </div>
              <div>
                <p className="text-white font-semibold">سطح 2</p>
                <p className="text-xs text-slate-400">پیشرفته</p>
              </div>
            </div>
          </div>
        </div>

        {/* Level 1 KYC Form */}
        {kycStatus.kyc_level === 0 && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Shield className="w-6 h-6 text-emerald-400" />
                احراز هویت سطح 1 (پایه)
              </CardTitle>
              <CardDescription className="text-slate-400">
                برای شروع معاملات، لطفا اطلاعات زیر را تکمیل کنید
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLevel1Submit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="full-name" className="text-slate-200">نام و نام خانوادگی</Label>
                  <div className="relative">
                    <User className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <Input
                      id="full-name"
                      value={level1Data.full_name}
                      onChange={(e) => setLevel1Data({...level1Data, full_name: e.target.value})}
                      className="pr-10 bg-slate-800/50 border-slate-700 text-white"
                      placeholder="علی رضایی"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="national-code" className="text-slate-200">کد ملی</Label>
                  <div className="relative">
                    <CreditCard className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <Input
                      id="national-code"
                      value={level1Data.national_code}
                      onChange={(e) => setLevel1Data({...level1Data, national_code: e.target.value.replace(/\D/g, '')})}
                      className="pr-10 bg-slate-800/50 border-slate-700 text-white"
                      placeholder="1234567890"
                      maxLength={10}
                      required
                    />
                  </div>
                  <p className="text-xs text-slate-500">کد ملی باید با شماره موبایل ثبت شده مطابقت داشته باشد</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="birth-date" className="text-slate-200">تاریخ تولد</Label>
                  <div className="relative">
                    <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <Input
                      id="birth-date"
                      value={level1Data.birth_date}
                      onChange={(e) => setLevel1Data({...level1Data, birth_date: e.target.value})}
                      className="pr-10 bg-slate-800/50 border-slate-700 text-white text-left"
                      placeholder="1370/05/15"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="card-number" className="text-slate-200">شماره کارت بانکی</Label>
                  <div className="relative">
                    <CreditCard className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                    <Input
                      id="card-number"
                      value={level1Data.bank_card_number}
                      onChange={(e) => setLevel1Data({...level1Data, bank_card_number: e.target.value.replace(/\D/g, '')})}
                      className="pr-10 bg-slate-800/50 border-slate-700 text-white text-left"
                      placeholder="6037998111408758"
                      maxLength={16}
                      required
                    />
                  </div>
                  <p className="text-xs text-slate-500">کارت باید به نام شما باشد</p>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-6"
                >
                  {loading ? "در حال بررسی..." : "تایید و ادامه"}
                </Button>

                <div className="bg-amber-900/20 border border-amber-800/50 rounded-lg p-4 text-sm text-amber-300">
                  <AlertCircle className="w-4 h-4 inline ml-2" />
                  سیستم به صورت خودکار اطلاعات شما را با شاهکار تطبیق می‌دهد
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Level 2 KYC Form */}
        {kycStatus.kyc_level === 1 && kycStatus.kyc_status === "approved" && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Upload className="w-6 h-6 text-emerald-400" />
                احراز هویت سطح 2 (پیشرفته)
              </CardTitle>
              <CardDescription className="text-slate-400">
                برای برداشت ارز دیجیتال، لطفا مدارک خود را بارگذاری کنید
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLevel2Submit} className="space-y-6">
                <div className="space-y-2">
                  <Label className="text-slate-200">تصویر کارت ملی</Label>
                  <div className="border-2 border-dashed border-slate-700 rounded-lg p-6 text-center">
                    <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                    <Input
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleFileUpload('id_card_photo', e.target.files[0])}
                      className="hidden"
                      id="id-card-upload"
                    />
                    <Label htmlFor="id-card-upload" className="text-emerald-400 cursor-pointer">
                      {level2Data.id_card_photo ? "تصویر انتخاب شد ✓" : "انتخاب تصویر"}
                    </Label>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-200">عکس سلفی با کارت ملی</Label>
                  <div className="border-2 border-dashed border-slate-700 rounded-lg p-6 text-center">
                    <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                    <Input
                      type="file"
                      accept="image/*,video/*"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        setLevel2Data(prev => ({
                          ...prev,
                          selfie_type: file.type.startsWith('video') ? 'video' : 'photo'
                        }));
                        handleFileUpload('selfie_data', file);
                      }}
                      className="hidden"
                      id="selfie-upload"
                    />
                    <Label htmlFor="selfie-upload" className="text-emerald-400 cursor-pointer">
                      {level2Data.selfie_data ? "فایل انتخاب شد ✓" : "انتخاب عکس یا ویدیو"}
                    </Label>
                  </div>
                  <p className="text-xs text-slate-500">
                    در تصویر باید صورت شما، کارت ملی و متن دست‌نویس قابل مشاهده باشد
                  </p>
                </div>

                <div className="bg-blue-900/20 border border-blue-800/50 rounded-lg p-4 text-sm text-blue-300">
                  <p className="font-semibold mb-2">متن احراز هویت:</p>
                  <p className="text-xs">
                    "اینجانب [نام شما] در تاریخ [امروز] با مطالعه و قبول قوانین والکس، تعهد می‌دهم حساب کاربری خود را در اختیار دیگران قرار ندهم"
                  </p>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-6"
                >
                  {loading ? "در حال ارسال..." : "ارسال مدارک"}
                </Button>

                <div className="bg-amber-900/20 border border-amber-800/50 rounded-lg p-4 text-sm text-amber-300">
                  <AlertCircle className="w-4 h-4 inline ml-2" />
                  مدارک شما حداکثر ظرف 1 ساعت بررسی می‌شود
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Pending Status */}
        {kycStatus.kyc_status === "pending" && kycStatus.has_documents && (
          <Card className="bg-amber-900/20 border-amber-800/50">
            <CardContent className="py-8 text-center">
              <AlertCircle className="w-16 h-16 text-amber-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">در انتظار تایید ادمین</h3>
              <p className="text-slate-300">مدارک شما در حال بررسی است. نتیجه از طریق پیامک اطلاع‌رسانی خواهد شد.</p>
            </CardContent>
          </Card>
        )}

        {/* Completed */}
        {kycStatus.kyc_level === 2 && kycStatus.kyc_status === "approved" && (
          <Card className="bg-emerald-900/20 border-emerald-800/50">
            <CardContent className="py-8 text-center">
              <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">احراز هویت کامل شد!</h3>
              <p className="text-slate-300 mb-4">شما به تمام امکانات دسترسی دارید</p>
              <Button onClick={() => navigate('/dashboard')} className="bg-emerald-600 hover:bg-emerald-700">
                رفتن به داشبورد
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
