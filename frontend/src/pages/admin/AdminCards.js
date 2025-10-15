import { useState, useEffect } from "react";
import axios from "axios";
import AdminLayout from "@/components/AdminLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Plus, CreditCard, User, Trash2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminCards({ user, onLogout }) {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newCard, setNewCard] = useState({
    card_number: "",
    cardholder_name: ""
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchCards();
  }, []);

  const fetchCards = async () => {
    try {
      const response = await axios.get(`${API}/admin/cards`);
      setCards(response.data);
    } catch (error) {
      console.error('Error fetching cards:', error);
      toast({
        title: "خطا",
        description: "بارگذاری کارت‌ها با خطا مواجه شد",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createCard = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/admin/cards`, newCard);
      toast({
        title: "موفق",
        description: "کارت جدید با موفقیت اضافه شد"
      });
      setDialogOpen(false);
      setNewCard({ card_number: "", cardholder_name: "" });
      fetchCards();
    } catch (error) {
      console.error('Error creating card:', error);
      toast({
        title: "خطا",
        description: "افزودن کارت با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const toggleCard = async (cardId, isActive) => {
    try {
      await axios.put(`${API}/admin/cards/${cardId}?is_active=${!isActive}`);
      toast({
        title: "موفق",
        description: isActive ? "کارت غیرفعال شد" : "کارت فعال شد"
      });
      fetchCards();
    } catch (error) {
      console.error('Error toggling card:', error);
      toast({
        title: "خطا",
        description: "تغییر وضعیت کارت با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const deleteCard = async (cardId) => {
    if (!window.confirm('آیا از حذف این کارت اطمینان دارید؟')) return;
    
    try {
      await axios.delete(`${API}/admin/cards/${cardId}`);
      toast({
        title: "موفق",
        description: "کارت حذف شد"
      });
      fetchCards();
    } catch (error) {
      console.error('Error deleting card:', error);
      toast({
        title: "خطا",
        description: "حذف کارت با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="cards">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="cards">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">مدیریت کارت‌های بانکی</h1>
            <p className="text-slate-200 mt-2">کارت‌های مقصد برای واریز کاربران</p>
          </div>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-emerald-600 hover:bg-emerald-700" data-testid="add-card-button">
                <Plus className="ml-2 w-5 h-5" />
                افزودن کارت جدید
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-900 border-slate-800">
              <DialogHeader>
                <DialogTitle className="text-white">افزودن کارت بانکی</DialogTitle>
                <DialogDescription className="text-slate-200">
                  شماره کارت جدید برای دریافت واریزی‌ها
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={createCard} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="card-number" className="text-slate-200">شماره کارت</Label>
                  <Input
                    id="card-number"
                    data-testid="card-number-input"
                    placeholder="6037998111408758"
                    value={newCard.card_number}
                    onChange={(e) => setNewCard({...newCard, card_number: e.target.value})}
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                    maxLength={16}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cardholder-name" className="text-slate-200">نام صاحب کارت</Label>
                  <Input
                    id="cardholder-name"
                    data-testid="cardholder-name-input"
                    placeholder="ایلیا فراستی"
                    value={newCard.cardholder_name}
                    onChange={(e) => setNewCard({...newCard, cardholder_name: e.target.value})}
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                  />
                </div>
                <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700" data-testid="submit-card-button">
                  افزودن کارت
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {cards.length === 0 ? (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="py-12 text-center">
              <CreditCard className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-200">هیچ کارتی ثبت نشده است</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {cards.map((card) => (
              <Card 
                key={card.id} 
                className={`${card.is_active ? 'bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border-emerald-800/50' : 'bg-slate-900/50 border-slate-800'}`}
                data-testid={`card-item-${card.id}`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-white flex items-center gap-2">
                      <CreditCard className="w-5 h-5" />
                      شماره کارت
                    </CardTitle>
                    {card.is_active ? (
                      <Badge className="bg-emerald-600 text-white">فعال</Badge>
                    ) : (
                      <Badge className="bg-slate-600 text-white">غیرفعال</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-2xl font-mono text-white tracking-wider">
                      {card.card_number.match(/.{1,4}/g)?.join(' ')}
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-2 text-slate-300">
                    <User className="w-4 h-4 text-slate-300" />
                    <span>{card.cardholder_name}</span>
                  </div>
                  
                  <div className="text-xs text-slate-300">
                    تاریخ ثبت: {new Date(card.created_at).toLocaleDateString('fa-IR')}
                  </div>

                  <div className="flex items-center gap-2 pt-4 border-t border-slate-700">
                    <div className="flex-1 flex items-center gap-2">
                      <span className="text-sm text-slate-200">وضعیت:</span>
                      <Switch
                        checked={card.is_active}
                        onCheckedChange={() => toggleCard(card.id, card.is_active)}
                        data-testid={`card-toggle-${card.id}`}
                      />
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteCard(card.id)}
                      className="border-red-800 text-red-400 hover:bg-red-900/20"
                      data-testid={`card-delete-${card.id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
