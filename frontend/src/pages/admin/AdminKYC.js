import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Shield, 
  Eye, 
  CheckCircle, 
  XCircle, 
  Clock, 
  User, 
  CreditCard, 
  Calendar,
  Phone,
  Mail,
  AlertTriangle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminKYC = ({ user, onLogout }) => {
  const [pendingKYCs, setPendingKYCs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const [selectedKYC, setSelectedKYC] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user || !user.is_admin) {
      navigate('/auth');
      return;
    }
    fetchPendingKYCs();
  }, [user, navigate]);

  const fetchPendingKYCs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/kyc/pending`);
      setPendingKYCs(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری KYC:', error);
      toast({
        title: 'خطا',
        description: 'خطا در بارگذاری درخواست‌های احراز هویت',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKYCAction = async (userId, action, kycLevel = 2, adminNote = '') => {
    try {
      setProcessingId(userId);
      await axios.post(`${API}/admin/kyc/approve`, {
        user_id: userId,
        action,
        kyc_level: kycLevel,
        admin_note: adminNote
      });
      
      toast({
        title: 'موفق',
        description: `احراز هویت با موفقیت ${action === 'approve' ? 'تایید' : 'رد'} شد`,
      });
      
      fetchPendingKYCs();
      setShowModal(false);
      setSelectedKYC(null);
    } catch (error) {
      console.error('خطا در پردازش KYC:', error);
      toast({
        title: 'خطا',
        description: error.response?.data?.detail || 'خطا در پردازش درخواست',
        variant: 'destructive'
      });
    } finally {
      setProcessingId(null);
    }
  };

  const openKYCModal = (kyc) => {
    setSelectedKYC(kyc);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedKYC(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'نامشخص';
    return new Date(dateString).toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-emerald-400">🛡️ مدیریت احراز هویت</h1>
            <nav className="flex gap-4">
              <a href="/admin" className="text-slate-300 hover:text-white transition-colors">داشبورد</a>
              <a href="/admin/users" className="text-slate-300 hover:text-white transition-colors">کاربران</a>
              <a href="/admin/orders" className="text-slate-300 hover:text-white transition-colors">سفارشات</a>
              <a href="/admin/deposits" className="text-slate-300 hover:text-white transition-colors">واریزها</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">درخواست‌های احراز هویت در انتظار</h2>
          <button
            onClick={fetchPendingKYCs}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors"
          >
            بروزرسانی
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2 text-yellow-400">
                <Clock className="w-5 h-5" />
                در انتظار بررسی
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{pendingKYCs.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2 text-blue-400">
                <Shield className="w-5 h-5" />
                سطح 2 (پیشرفته)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{pendingKYCs.filter(kyc => kyc.kyc_documents).length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2 text-emerald-400">
                <AlertTriangle className="w-5 h-5" />
                نیاز به اقدام
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{pendingKYCs.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* KYC Requests */}
        {pendingKYCs.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="text-center py-12">
              <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-200 mb-2">
                درخواست احراز هویت جدیدی وجود ندارد
              </h3>
              <p className="text-slate-300">
                تمام درخواست‌های احراز هویت پردازش شده‌اند
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {pendingKYCs.map((kyc) => (
              <Card key={kyc.id} className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors">
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* User Info */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 mb-4">
                        <User className="w-5 h-5 text-emerald-400" />
                        <h3 className="text-lg font-semibold">{kyc.full_name || 'نام نامشخص'}</h3>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm text-slate-200">
                        <Mail className="w-4 h-4" />
                        <span>{kyc.email}</span>
                      </div>
                      
                      {kyc.phone && (
                        <div className="flex items-center gap-2 text-sm text-slate-200">
                          <Phone className="w-4 h-4" />
                          <span>{kyc.phone}</span>
                        </div>
                      )}
                      
                      {kyc.national_code && (
                        <div className="flex items-center gap-2 text-sm text-slate-200">
                          <CreditCard className="w-4 h-4" />
                          <span>کد ملی: {kyc.national_code}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 text-sm text-slate-200">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(kyc.submitted_at)}</span>
                      </div>
                    </div>

                    {/* KYC Status */}
                    <div className="space-y-3">
                      <div className="flex flex-col gap-2">
                        <Badge variant="secondary" className="w-fit bg-yellow-600 text-white">
                          <Clock className="w-3 h-3 mr-1" />
                          در انتظار تایید
                        </Badge>
                        
                        <Badge variant="outline" className="w-fit border-blue-600 text-blue-400">
                          سطح 2 - پیشرفته
                        </Badge>
                      </div>
                      
                      {kyc.kyc_documents && (
                        <div className="text-sm text-slate-200">
                          <p>✅ عکس کارت ملی ارسال شده</p>
                          <p>✅ تصویر سلفی ارسال شده</p>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-3">
                      <Button 
                        onClick={() => openKYCModal(kyc)}
                        className="w-full bg-blue-600 hover:bg-blue-700"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        بررسی مدارک
                      </Button>
                      
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleKYCAction(kyc.id, 'approve')}
                          disabled={processingId === kyc.id}
                          className="flex-1 bg-green-600 hover:bg-green-700"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          {processingId === kyc.id ? '...' : 'تایید'}
                        </Button>
                        
                        <Button
                          onClick={() => handleKYCAction(kyc.id, 'reject', 2, 'مدارک نامعتبر')}
                          disabled={processingId === kyc.id}
                          className="flex-1 bg-red-600 hover:bg-red-700"
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          رد
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* KYC Document Modal */}
      {showModal && selectedKYC && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="bg-slate-900 border-slate-800 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader className="border-b border-slate-800">
              <CardTitle className="flex items-center justify-between">
                <span>بررسی مدارک - {selectedKYC.full_name}</span>
                <Button onClick={closeModal} variant="outline" size="sm">
                  بستن
                </Button>
              </CardTitle>
            </CardHeader>
            
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* User Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold mb-4">اطلاعات کاربر</h3>
                  
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-200">نام و نام خانوادگی:</span>
                      <span>{selectedKYC.full_name}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-slate-200">ایمیل:</span>
                      <span>{selectedKYC.email}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-slate-200">تلفن:</span>
                      <span>{selectedKYC.phone}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-slate-200">کد ملی:</span>
                      <span>{selectedKYC.national_code}</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-slate-200">تاریخ ارسال:</span>
                      <span>{formatDate(selectedKYC.submitted_at)}</span>
                    </div>
                  </div>
                </div>

                {/* Document Images */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold mb-4">مدارک ارسالی</h3>
                  
                  {selectedKYC.kyc_documents && (
                    <div className="space-y-4">
                      {selectedKYC.kyc_documents.id_card_photo && (
                        <div>
                          <p className="text-sm text-slate-200 mb-2">عکس کارت ملی:</p>
                          <img 
                            src={selectedKYC.kyc_documents.id_card_photo} 
                            alt="کارت ملی"
                            className="w-full rounded-lg border border-slate-700"
                          />
                        </div>
                      )}
                      
                      {selectedKYC.kyc_documents.selfie_data && (
                        <div>
                          <p className="text-sm text-slate-200 mb-2">تصویر سلفی:</p>
                          <img 
                            src={selectedKYC.kyc_documents.selfie_data} 
                            alt="تصویر سلفی"
                            className="w-full rounded-lg border border-slate-700"
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 mt-6 pt-6 border-t border-slate-800">
                <Button
                  onClick={() => handleKYCAction(selectedKYC.id, 'approve')}
                  disabled={processingId === selectedKYC.id}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="w-4 h-4 mr-2" />
                  {processingId === selectedKYC.id ? 'در حال پردازش...' : 'تایید احراز هویت'}
                </Button>
                
                <Button
                  onClick={() => handleKYCAction(selectedKYC.id, 'reject', 2, 'مدارک نامعتبر یا نامطابق')}
                  disabled={processingId === selectedKYC.id}
                  className="flex-1 bg-red-600 hover:bg-red-700"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  رد احراز هویت
                </Button>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  یادداشت ادمین (اختیاری):
                </label>
                <textarea
                  className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg text-white"
                  rows="3"
                  placeholder="یادداشت یا دلیل رد..."
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AdminKYC;