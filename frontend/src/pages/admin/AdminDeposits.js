import { useState, useEffect } from "react";
import axios from "axios";
import AdminLayout from "@/components/AdminLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Clock, CheckCircle, XCircle, User, Mail, CreditCard, Calendar, DollarSign } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminDeposits({ user, onLogout }) {
  const [deposits, setDeposits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDeposit, setSelectedDeposit] = useState(null);
  const [adminNote, setAdminNote] = useState("");
  const [actionType, setActionType] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchDeposits();
  }, []);

  const fetchDeposits = async () => {
    try {
      const response = await axios.get(`${API}/admin/deposits`);
      // Sort by created_at desc
      const sortedDeposits = response.data.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
      setDeposits(sortedDeposits);
    } catch (error) {
      console.error('Error fetching deposits:', error);
      toast({
        title: "خطا",
        description: "بارگذاری درخواست‌ها با خطا مواجه شد",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const openApprovalDialog = (deposit, action) => {
    setSelectedDeposit(deposit);
    setActionType(action);
    setAdminNote("");
  };

  const handleApproval = async () => {
    if (!selectedDeposit || !actionType) return;

    try {
      await axios.post(`${API}/admin/deposits/approve`, {
        deposit_id: selectedDeposit.id,
        action: actionType,
        admin_note: adminNote || undefined
      });
      
      toast({
        title: "موفق",
        description: actionType === 'approve' ? "درخواست تایید شد" : "درخواست رد شد"
      });
      
      setSelectedDeposit(null);
      setActionType(null);
      setAdminNote("");
      fetchDeposits();
    } catch (error) {
      console.error('Error processing deposit:', error);
      toast({
        title: "خطا",
        description: error.response?.data?.detail || "پردازش درخواست با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-amber-600 text-white"><Clock className="w-3 h-3 ml-1" />در انتظار</Badge>;
      case 'approved':
        return <Badge className="bg-emerald-600 text-white"><CheckCircle className="w-3 h-3 ml-1" />تایید شده</Badge>;
      case 'rejected':
        return <Badge className="bg-red-600 text-white"><XCircle className="w-3 h-3 ml-1" />رد شده</Badge>;
      default:
        return <Badge className="bg-slate-600 text-white">{status}</Badge>;
    }
  };

  const pendingDeposits = deposits.filter(d => d.status === 'pending');
  const processedDeposits = deposits.filter(d => d.status !== 'pending');

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="deposits">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="deposits">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">مدیریت درخواست‌های واریز</h1>
            <p className="text-slate-200 mt-2">بررسی و تایید واریزی‌های کاربران</p>
          </div>
          <Badge className="bg-amber-600 text-white px-4 py-2">
            {pendingDeposits.length} در انتظار
          </Badge>
        </div>

        {/* Pending Deposits */}
        {pendingDeposits.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-400" />
              درخواست‌های در انتظار تایید
            </h2>
            {pendingDeposits.map((deposit) => (
              <Card key={deposit.id} className="bg-gradient-to-r from-amber-900/20 to-orange-900/20 border-amber-800/50" data-testid={`deposit-pending-${deposit.id}`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-white">
                      درخواست واریز #{deposit.id.slice(0, 8)}
                    </CardTitle>
                    {getStatusBadge(deposit.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-slate-300">
                        <User className="w-4 h-4 text-slate-300" />
                        <span className="text-sm">نام: {deposit.user_name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <Mail className="w-4 h-4 text-slate-300" />
                        <span className="text-sm">{deposit.user_email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <CreditCard className="w-4 h-4 text-slate-300" />
                        <span className="text-sm font-mono">{deposit.card_number}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-slate-300">
                        <DollarSign className="w-4 h-4 text-slate-300" />
                        <span className="text-lg font-bold text-white">
                          {deposit.amount.toLocaleString('fa-IR')} تومان
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <Calendar className="w-4 h-4 text-slate-300" />
                        <span className="text-sm">
                          {new Date(deposit.created_at).toLocaleString('fa-IR')}
                        </span>
                      </div>
                      {deposit.transaction_id && (
                        <div className="text-sm text-slate-200">
                          شناسه تراکنش: {deposit.transaction_id}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4 border-t border-slate-700">
                    <Button
                      onClick={() => openApprovalDialog(deposit, 'approve')}
                      className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                      data-testid={`approve-deposit-${deposit.id}`}
                    >
                      <CheckCircle className="ml-2 w-5 h-5" />
                      تایید واریز
                    </Button>
                    <Button
                      onClick={() => openApprovalDialog(deposit, 'reject')}
                      className="flex-1 bg-red-600 hover:bg-red-700"
                      data-testid={`reject-deposit-${deposit.id}`}
                    >
                      <XCircle className="ml-2 w-5 h-5" />
                      رد درخواست
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Processed Deposits */}
        {processedDeposits.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">تاریخچه درخواست‌ها</h2>
            {processedDeposits.map((deposit) => (
              <Card key={deposit.id} className="bg-slate-900/50 border-slate-800" data-testid={`deposit-processed-${deposit.id}`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-white text-base">
                      #{deposit.id.slice(0, 8)} - {deposit.user_name}
                    </CardTitle>
                    {getStatusBadge(deposit.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm">
                    <div className="space-y-1">
                      <p className="text-slate-200">{deposit.user_email}</p>
                      <p className="text-white font-semibold">
                        {deposit.amount.toLocaleString('fa-IR')} تومان
                      </p>
                    </div>
                    <div className="text-left">
                      <p className="text-slate-200 text-xs">
                        {new Date(deposit.updated_at).toLocaleString('fa-IR')}
                      </p>
                      {deposit.admin_note && (
                        <p className="text-slate-300 text-xs mt-1">یادداشت: {deposit.admin_note}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {deposits.length === 0 && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="py-12 text-center">
              <DollarSign className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-200">هیچ درخواستی ثبت نشده است</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Approval Dialog */}
      <Dialog open={!!selectedDeposit} onOpenChange={() => {setSelectedDeposit(null); setActionType(null);}}>
        <DialogContent className="bg-slate-900 border-slate-800">
          <DialogHeader>
            <DialogTitle className="text-white">
              {actionType === 'approve' ? 'تایید درخواست واریز' : 'رد درخواست واریز'}
            </DialogTitle>
            <DialogDescription className="text-slate-200">
              {actionType === 'approve' 
                ? 'با تایید این درخواست، موجودی حساب کاربر افزایش می‌یابد'
                : 'لطفا دلیل رد درخواست را بنویسید'}
            </DialogDescription>
          </DialogHeader>
          {selectedDeposit && (
            <div className="space-y-4">
              <div className="p-4 bg-slate-800 rounded-lg space-y-2">
                <p className="text-white font-semibold">
                  مبلغ: {selectedDeposit.amount.toLocaleString('fa-IR')} تومان
                </p>
                <p className="text-slate-200 text-sm">کاربر: {selectedDeposit.user_name}</p>
              </div>
              
              <div className="space-y-2">
                <label className="text-slate-200 text-sm">یادداشت (اختیاری)</label>
                <Textarea
                  value={adminNote}
                  onChange={(e) => setAdminNote(e.target.value)}
                  placeholder="توضیحات یا یادداشت برای این تراکنش..."
                  className="bg-slate-800 border-slate-700 text-white"
                  rows={3}
                  data-testid="admin-note-textarea"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={handleApproval}
                  className={`flex-1 ${actionType === 'approve' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-red-600 hover:bg-red-700'}`}
                  data-testid="confirm-action-button"
                >
                  {actionType === 'approve' ? 'تایید نهایی' : 'رد نهایی'}
                </Button>
                <Button
                  onClick={() => {setSelectedDeposit(null); setActionType(null);}}
                  variant="outline"
                  className="border-slate-700 text-slate-300"
                  data-testid="cancel-action-button"
                >
                  انصراف
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </AdminLayout>
  );
}
