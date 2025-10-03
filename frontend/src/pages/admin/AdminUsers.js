import { useState, useEffect } from "react";
import axios from "axios";
import AdminLayout from "@/components/AdminLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { Mail, Phone, Calendar, Wallet, Shield, CheckCircle, XCircle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminUsers({ user, onLogout }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast({
        title: "خطا",
        description: "بارگذاری کاربران با خطا مواجه شد",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const updateUser = async (userId, updates) => {
    try {
      await axios.put(`${API}/admin/users/${userId}`, updates);
      toast({
        title: "موفق",
        description: "اطلاعات کاربر به‌روزرسانی شد"
      });
      fetchUsers();
    } catch (error) {
      console.error('Error updating user:', error);
      toast({
        title: "خطا",
        description: "به‌روزرسانی با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <AdminLayout user={user} onLogout={onLogout} currentPage="users">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout user={user} onLogout={onLogout} currentPage="users">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">مدیریت کاربران</h1>
            <p className="text-slate-400 mt-2">مشاهده و مدیریت کاربران سیستم</p>
          </div>
          <Badge className="bg-emerald-600 text-white px-4 py-2">
            {users.length} کاربر
          </Badge>
        </div>

        <div className="grid gap-4">
          {users.map((u) => (
            <Card key={u.id} className="bg-slate-900/50 border-slate-800" data-testid={`user-card-${u.id}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-white flex items-center gap-2">
                      {u.full_name}
                      {u.is_admin && (
                        <Badge className="bg-amber-600 text-white">مدیر</Badge>
                      )}
                    </CardTitle>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4 text-sm">
                      <div className="flex items-center gap-2 text-slate-300">
                        <Mail className="w-4 h-4 text-slate-500" />
                        {u.email}
                      </div>
                      {u.phone && (
                        <div className="flex items-center gap-2 text-slate-300">
                          <Phone className="w-4 h-4 text-slate-500" />
                          {u.phone}
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-slate-300">
                        <Wallet className="w-4 h-4 text-slate-500" />
                        موجودی: {u.wallet_balance_tmn.toLocaleString('fa-IR')} تومان
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <Calendar className="w-4 h-4 text-slate-500" />
                        {new Date(u.created_at).toLocaleDateString('fa-IR')}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Active Status */}
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      {u.is_active ? (
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span className="text-sm text-slate-300">وضعیت حساب</span>
                    </div>
                    <Switch
                      checked={u.is_active}
                      onCheckedChange={(checked) => updateUser(u.id, { is_active: checked })}
                      data-testid={`user-active-toggle-${u.id}`}
                    />
                  </div>

                  {/* Verified Status */}
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      {u.is_verified ? (
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                      <span className="text-sm text-slate-300">تایید احراز هویت</span>
                    </div>
                    <Switch
                      checked={u.is_verified}
                      onCheckedChange={(checked) => updateUser(u.id, { is_verified: checked })}
                      data-testid={`user-verified-toggle-${u.id}`}
                    />
                  </div>

                  {/* Admin Status */}
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4 text-amber-500" />
                      <span className="text-sm text-slate-300">دسترسی مدیر</span>
                    </div>
                    <Switch
                      checked={u.is_admin}
                      onCheckedChange={(checked) => updateUser(u.id, { is_admin: checked })}
                      data-testid={`user-admin-toggle-${u.id}`}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AdminLayout>
  );
}
