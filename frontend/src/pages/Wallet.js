import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Wallet as WalletIcon, ArrowDownCircle, Copy, CheckCircle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Wallet({ user }) {
  const [depositDialog, setDepositDialog] = useState(false);
  const [depositAmount, setDepositAmount] = useState("");
  const [depositLoading, setDepositLoading] = useState(false);
  const [cards, setCards] = useState([]);
  const [myDeposits, setMyDeposits] = useState([]);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCards();
    fetchMyDeposits();
  }, []);

  const fetchCards = async () => {
    try {
      const response = await axios.get(`${API}/cards`);
      setCards(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const fetchMyDeposits = async () => {
    try {
      const response = await axios.get(`${API}/deposits/my`);
      setMyDeposits(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleDeposit = async () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      toast({ title: "خطا", description: "مبلغ را وارد کنید", variant: "destructive" });
      return;
    }

    if (user.kyc_level < 1) {
      toast({ title: "خطا", description: "ابتدا احراز هویت کنید", variant: "destructive" });
      navigate('/kyc');
      return;
    }

    setDepositLoading(true);
    try {
      await axios.post(`${API}/deposits`, {
        amount: parseFloat(depositAmount),
        card_number: user.bank_card_number || cards[0]?.card_number
      });
      
      toast({ title: "موفق", description: "درخواست واریز ثبت شد" });
      setDepositDialog(false);
      setDepositAmount("");
      fetchMyDeposits();
    } catch (error) {
      toast({ title: "خطا", description: error.response?.data?.detail || "خطا", variant: "destructive" });
    } finally {
      setDepositLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast({ title: "کپی شد", description: "شماره کارت کپی شد" });
  };

  return (
    <div className="min-h-screen bg-slate-950" dir="rtl">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">کیف پول</h1>
          <Button onClick={() => navigate('/dashboard')} variant="outline">داشبورد</Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border-emerald-800/50 mb-6">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <WalletIcon className="w-6 h-6" />
              موجودی کیف پول
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-white mb-4">
              {user.wallet_balance_tmn.toLocaleString('fa-IR')} تومان
            </p>
            <Button 
              className="bg-emerald-600 hover:bg-emerald-700 w-full"
              onClick={() => setDepositDialog(true)}
              disabled={user.kyc_level < 1}
            >
              <ArrowDownCircle className="ml-2 w-5 h-5" />
              واریز تومان
            </Button>
            {user.kyc_level < 1 && (
              <p className="text-amber-400 text-sm mt-2 text-center">
                برای واریز باید احراز هویت کنید
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">تاریخچه واریز</CardTitle>
          </CardHeader>
          <CardContent>
            {myDeposits.length === 0 ? (
              <p className="text-slate-400 text-center py-8">هیچ واریزی ثبت نشده</p>
            ) : (
              <div className="space-y-3">
                {myDeposits.map((deposit) => (
                  <div key={deposit.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div>
                      <p className="text-white font-semibold">{deposit.amount.toLocaleString('fa-IR')} تومان</p>
                      <p className="text-xs text-slate-400">{new Date(deposit.created_at).toLocaleDateString('fa-IR')}</p>
                    </div>
                    <span className={`px-3 py-1 rounded text-sm ${
                      deposit.status === 'approved' ? 'bg-emerald-600 text-white' :
                      deposit.status === 'rejected' ? 'bg-red-600 text-white' :
                      'bg-amber-600 text-white'
                    }`}>
                      {deposit.status === 'approved' ? 'تایید شده' : deposit.status === 'rejected' ? 'رد شده' : 'در انتظار'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Dialog open={depositDialog} onOpenChange={setDepositDialog}>
        <DialogContent className="bg-slate-900 border-slate-800">
          <DialogHeader>
            <DialogTitle className="text-white">واریز کارت به کارت</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {cards.map((card) => (
              <div key={card.id} className="p-4 bg-slate-800 rounded-lg">
                <p className="text-slate-400 text-sm mb-2">شماره کارت:</p>
                <div className="flex items-center justify-between">
                  <p className="text-white font-mono text-lg">{card.card_number.match(/.{1,4}/g).join(' ')}</p>
                  <Button size="sm" variant="outline" onClick={() => copyToClipboard(card.card_number)}>
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-slate-400 text-sm mt-2">نام: {card.cardholder_name}</p>
              </div>
            ))}
            
            <div className="space-y-2">
              <Label className="text-slate-200">مبلغ (تومان)</Label>
              <Input
                type="number"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white"
                placeholder="مثال: 1000000"
              />
            </div>

            <div className="bg-blue-900/20 border border-blue-800/50 rounded p-3 text-sm text-blue-300">
              <p>1. مبلغ را به کارت بالا واریز کنید</p>
              <p>2. مبلغ را اینجا وارد کنید</p>
              <p>3. درخواست شما ظرف 10 دقیقه تایید می‌شود</p>
            </div>

            <Button 
              onClick={handleDeposit} 
              disabled={depositLoading}
              className="w-full bg-emerald-600 hover:bg-emerald-700"
            >
              {depositLoading ? "در حال ثبت..." : "ثبت درخواست واریز"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
