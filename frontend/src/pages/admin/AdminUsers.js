import { useState, useEffect } from "react";
import axios from "axios";
import AdminLayout from "@/components/AdminLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { 
  Mail, Phone, Calendar, Shield, CheckCircle, XCircle, Search, Filter,
  UserX, UserCheck, StickyNote, Tag, Activity, Download, Users, AlertTriangle,
  Lock, Unlock, Trash2, MoreVertical, Eye, X, ChevronDown, ChevronUp
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminUsers({ user, onLogout }) {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const { toast } = useToast();
  
  // Filters and Search
  const [searchText, setSearchText] = useState("");
  const [kycLevelFilter, setKycLevelFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showFilters, setShowFilters] = useState(false);
  
  // Selection
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  
  // Modals
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserDetails, setShowUserDetails] = useState(false);
  const [showSuspendModal, setShowSuspendModal] = useState(false);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [showTagModal, setShowTagModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  
  // Form data
  const [suspensionDuration, setSuspensionDuration] = useState("");
  const [suspensionReason, setSuspensionReason] = useState("");
  const [newNote, setNewNote] = useState("");
  const [newTag, setNewTag] = useState("");
  const [userNotes, setUserNotes] = useState([]);
  const [userActivity, setUserActivity] = useState([]);

  useEffect(() => {
    fetchUsers();
    fetchStats();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [users, searchText, kycLevelFilter, statusFilter]);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
      setFilteredUsers(response.data);
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

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/users/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...users];

    // Search filter
    if (searchText) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(u => 
        u.full_name?.toLowerCase().includes(search) ||
        u.email?.toLowerCase().includes(search) ||
        u.phone?.includes(search)
      );
    }

    // KYC level filter
    if (kycLevelFilter !== "all") {
      filtered = filtered.filter(u => u.kyc_level === parseInt(kycLevelFilter));
    }

    // Status filter
    if (statusFilter === "suspended") {
      filtered = filtered.filter(u => u.is_suspended);
    } else if (statusFilter === "active") {
      filtered = filtered.filter(u => !u.is_suspended);
    } else if (statusFilter === "admin") {
      filtered = filtered.filter(u => u.is_admin);
    }

    setFilteredUsers(filtered);
  };

  const suspendUser = async () => {
    if (!selectedUser) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/admin/users/${selectedUser.id}/suspend`,
        {
          duration: suspensionDuration ? parseInt(suspensionDuration) : null,
          reason: suspensionReason
        },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast({
        title: "موفق",
        description: "کاربر با موفقیت تعلیق شد"
      });
      
      setShowSuspendModal(false);
      setSuspensionDuration("");
      setSuspensionReason("");
      fetchUsers();
    } catch (error) {
      toast({
        title: "خطا",
        description: "تعلیق کاربر با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const unsuspendUser = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/admin/users/${userId}/unsuspend`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast({
        title: "موفق",
        description: "تعلیق کاربر لغو شد"
      });
      
      fetchUsers();
    } catch (error) {
      toast({
        title: "خطا",
        description: "لغو تعلیق با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const addNote = async () => {
    if (!selectedUser || !newNote.trim()) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/admin/users/${selectedUser.id}/notes`,
        { note: newNote },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast({
        title: "موفق",
        description: "یادداشت اضافه شد"
      });
      
      setNewNote("");
      setShowNoteModal(false);
      if (showUserDetails) {
        fetchUserNotes(selectedUser.id);
      }
    } catch (error) {
      toast({
        title: "خطا",
        description: "افزودن یادداشت با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const addTag = async () => {
    if (!selectedUser || !newTag.trim()) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/admin/users/${selectedUser.id}/tags`,
        { tag: newTag },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast({
        title: "موفق",
        description: "برچسب اضافه شد"
      });
      
      setNewTag("");
      setShowTagModal(false);
      fetchUsers();
    } catch (error) {
      toast({
        title: "خطا",
        description: "افزودن برچسب با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const removeTag = async (userId, tag) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${API}/admin/users/${userId}/tags/${tag}`,
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast({
        title: "موفق",
        description: "برچسب حذف شد"
      });
      
      fetchUsers();
    } catch (error) {
      toast({
        title: "خطا",
        description: "حذف برچسب با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const fetchUserNotes = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/admin/users/${userId}/notes`,
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setUserNotes(response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  const fetchUserActivity = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/admin/users/${userId}/activity`,
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setUserActivity(response.data);
    } catch (error) {
      console.error('Error fetching activity:', error);
    }
  };

  const showUserDetailsModal = async (u) => {
    setSelectedUser(u);
    setShowUserDetails(true);
    await fetchUserNotes(u.id);
    await fetchUserActivity(u.id);
  };

  const toggleSelectUser = (userId) => {
    if (selectedUsers.includes(userId)) {
      setSelectedUsers(selectedUsers.filter(id => id !== userId));
    } else {
      setSelectedUsers([...selectedUsers, userId]);
    }
  };

  const toggleSelectAll = () => {
    if (selectAll) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(filteredUsers.map(u => u.id));
    }
    setSelectAll(!selectAll);
  };

  const bulkSuspend = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API}/admin/users/bulk-action`,
        {
          user_ids: selectedUsers,
          action: "suspend",
          reason: "عملیات گروهی"
        },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast({
        title: "موفق",
        description: `${selectedUsers.length} کاربر تعلیق شدند`
      });
      
      setSelectedUsers([]);
      setSelectAll(false);
      setShowBulkModal(false);
      fetchUsers();
    } catch (error) {
      toast({
        title: "خطا",
        description: "عملیات گروهی با خطا مواجه شد",
        variant: "destructive"
      });
    }
  };

  const exportUsers = () => {
    const csvData = filteredUsers.map(u => ({
      'نام': u.full_name,
      'ایمیل': u.email,
      'تلفن': u.phone,
      'سطح KYC': u.kyc_level,
      'وضعیت KYC': u.kyc_status,
      'تاریخ ثبت': u.created_at
    }));

    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `users_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const getKycBadgeColor = (level) => {
    if (level === 0) return 'bg-gray-600';
    if (level === 1) return 'bg-blue-600';
    return 'bg-green-600';
  };

  const getStatusBadgeColor = (status) => {
    if (status === 'approved') return 'bg-green-600';
    if (status === 'pending') return 'bg-yellow-600';
    return 'bg-red-600';
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
      <div className="space-y-6" dir="rtl">
        {/* Header with Stats */}
        <div>
          <h1 className="text-3xl font-bold text-white">مدیریت کاربران</h1>
          <p className="text-slate-200 mt-2">مشاهده و مدیریت پیشرفته کاربران</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-900/50 to-blue-800/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-300 text-sm">کل کاربران</p>
                    <p className="text-2xl font-bold text-white">{stats.total_users}</p>
                  </div>
                  <Users className="w-8 h-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-900/50 to-green-800/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-300 text-sm">کاربران فعال</p>
                    <p className="text-2xl font-bold text-white">{stats.active_users}</p>
                  </div>
                  <UserCheck className="w-8 h-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-red-900/50 to-red-800/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-300 text-sm">تعلیق شده</p>
                    <p className="text-2xl font-bold text-white">{stats.suspended_users}</p>
                  </div>
                  <UserX className="w-8 h-8 text-red-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-900/50 to-purple-800/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-300 text-sm">KYC در انتظار</p>
                    <p className="text-2xl font-bold text-white">{stats.kyc_stats.pending}</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-purple-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Search and Filters */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute right-3 top-3 w-5 h-5 text-slate-200" />
                  <Input
                    type="text"
                    placeholder="جستجو بر اساس نام، ایمیل یا تلفن..."
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    className="pr-10 bg-slate-800 border-slate-700 text-white"
                  />
                </div>
              </div>

              <Button
                onClick={() => setShowFilters(!showFilters)}
                variant="outline"
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                فیلترها
                {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>

              <Button onClick={exportUsers} variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                خروجی CSV
              </Button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-700">
                <div>
                  <label className="block text-sm text-slate-300 mb-2">سطح KYC</label>
                  <select
                    value={kycLevelFilter}
                    onChange={(e) => setKycLevelFilter(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
                  >
                    <option value="all">همه</option>
                    <option value="0">سطح 0</option>
                    <option value="1">سطح 1</option>
                    <option value="2">سطح 2</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-slate-300 mb-2">وضعیت</label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
                  >
                    <option value="all">همه</option>
                    <option value="active">فعال</option>
                    <option value="suspended">تعلیق شده</option>
                    <option value="admin">مدیر</option>
                  </select>
                </div>

                <div className="flex items-end">
                  <Button
                    onClick={() => {
                      setSearchText("");
                      setKycLevelFilter("all");
                      setStatusFilter("all");
                    }}
                    variant="outline"
                    className="w-full"
                  >
                    پاک کردن فیلترها
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Bulk Actions */}
        {selectedUsers.length > 0 && (
          <Card className="bg-blue-900/30 border-blue-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-white font-medium">
                    {selectedUsers.length} کاربر انتخاب شده
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedUsers([]);
                      setSelectAll(false);
                    }}
                  >
                    لغو انتخاب
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => setShowBulkModal(true)}
                    className="gap-2"
                  >
                    <UserX className="w-4 h-4" />
                    تعلیق گروهی
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Info */}
        <div className="flex items-center justify-between text-slate-200 text-sm">
          <span>نمایش {filteredUsers.length} از {users.length} کاربر</span>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={selectAll}
              onChange={toggleSelectAll}
              className="w-4 h-4 rounded"
            />
            <span>انتخاب همه</span>
          </div>
        </div>

        {/* Users List */}
        <div className="grid gap-4">
          {filteredUsers.map((u) => (
            <Card key={u.id} className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(u.id)}
                    onChange={() => toggleSelectUser(u.id)}
                    className="w-5 h-5 rounded mt-1"
                  />

                  {/* User Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-white font-bold text-lg">{u.full_name}</h3>
                          {u.is_admin && (
                            <Badge className="bg-amber-600">مدیر</Badge>
                          )}
                          {u.is_suspended && (
                            <Badge className="bg-red-600">تعلیق شده</Badge>
                          )}
                          <Badge className={getKycBadgeColor(u.kyc_level)}>
                            KYC {u.kyc_level}
                          </Badge>
                          <Badge className={getStatusBadgeColor(u.kyc_status || 'none')}>
                            {u.kyc_status === 'approved' ? 'تایید شده' : 
                             u.kyc_status === 'pending' ? 'در انتظار' : 'رد شده'}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                          <div className="flex items-center gap-2 text-slate-300">
                            <Mail className="w-4 h-4 text-slate-300" />
                            {u.email}
                          </div>
                          {u.phone && (
                            <div className="flex items-center gap-2 text-slate-300">
                              <Phone className="w-4 h-4 text-slate-300" />
                              {u.phone}
                            </div>
                          )}
                        </div>

                        {/* Tags */}
                        {u.tags && u.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {u.tags.map((tag, idx) => (
                              <div
                                key={idx}
                                className="flex items-center gap-1 bg-slate-800 px-2 py-1 rounded text-xs text-slate-300"
                              >
                                <Tag className="w-3 h-3" />
                                {tag}
                                <button
                                  onClick={() => removeTag(u.id, tag)}
                                  className="hover:text-red-400 ml-1"
                                >
                                  <X className="w-3 h-3" />
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => showUserDetailsModal(u)}
                          className="gap-2"
                        >
                          <Eye className="w-4 h-4" />
                          جزئیات
                        </Button>

                        {!u.is_suspended ? (
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => {
                              setSelectedUser(u);
                              setShowSuspendModal(true);
                            }}
                            className="gap-2"
                          >
                            <Lock className="w-4 h-4" />
                            تعلیق
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => unsuspendUser(u.id)}
                            className="gap-2 text-green-400 border-green-600 hover:bg-green-900/20"
                          >
                            <Unlock className="w-4 h-4" />
                            لغو تعلیق
                          </Button>
                        )}

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedUser(u);
                            setShowNoteModal(true);
                          }}
                        >
                          <StickyNote className="w-4 h-4" />
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedUser(u);
                            setShowTagModal(true);
                          }}
                        >
                          <Tag className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredUsers.length === 0 && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="p-8 text-center">
              <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-200">هیچ کاربری یافت نشد</p>
            </CardContent>
          </Card>
        )}

        {/* Suspend Modal */}
        {showSuspendModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle className="text-white">تعلیق کاربر</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-2">
                    مدت تعلیق (روز) - برای دائمی خالی بگذارید
                  </label>
                  <Input
                    type="number"
                    value={suspensionDuration}
                    onChange={(e) => setSuspensionDuration(e.target.value)}
                    placeholder="مثال: 7 برای یک هفته"
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-300 mb-2">دلیل تعلیق</label>
                  <textarea
                    value={suspensionReason}
                    onChange={(e) => setSuspensionReason(e.target.value)}
                    rows={3}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
                    placeholder="دلیل تعلیق را وارد کنید..."
                  />
                </div>

                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowSuspendModal(false);
                      setSuspensionDuration("");
                      setSuspensionReason("");
                    }}
                  >
                    انصراف
                  </Button>
                  <Button variant="destructive" onClick={suspendUser}>
                    تعلیق کاربر
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Note Modal */}
        {showNoteModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle className="text-white">افزودن یادداشت</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  rows={4}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
                  placeholder="یادداشت خود را وارد کنید..."
                />

                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowNoteModal(false);
                      setNewNote("");
                    }}
                  >
                    انصراف
                  </Button>
                  <Button onClick={addNote}>افزودن یادداشت</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tag Modal */}
        {showTagModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle className="text-white">افزودن برچسب</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  placeholder="نام برچسب را وارد کنید..."
                  className="bg-slate-800 border-slate-700 text-white"
                />

                <div className="flex flex-wrap gap-2">
                  <Button size="sm" variant="outline" onClick={() => setNewTag("VIP")}>
                    VIP
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setNewTag("مشکوک")}>
                    مشکوک
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setNewTag("تایید شده")}>
                    تایید شده
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setNewTag("پرخطر")}>
                    پرخطر
                  </Button>
                </div>

                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowTagModal(false);
                      setNewTag("");
                    }}
                  >
                    انصراف
                  </Button>
                  <Button onClick={addTag}>افزودن برچسب</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* User Details Modal */}
        {showUserDetails && selectedUser && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto p-4">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-4xl my-8">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white">جزئیات کاربر: {selectedUser.full_name}</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowUserDetails(false)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* User Basic Info */}
                <div className="grid grid-cols-2 gap-4 pb-4 border-b border-slate-700">
                  <div>
                    <p className="text-slate-200 text-sm">ایمیل</p>
                    <p className="text-white">{selectedUser.email}</p>
                  </div>
                  <div>
                    <p className="text-slate-200 text-sm">تلفن</p>
                    <p className="text-white">{selectedUser.phone || '-'}</p>
                  </div>
                  <div>
                    <p className="text-slate-200 text-sm">سطح KYC</p>
                    <Badge className={getKycBadgeColor(selectedUser.kyc_level)}>
                      سطح {selectedUser.kyc_level}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-slate-200 text-sm">وضعیت</p>
                    <Badge className={selectedUser.is_suspended ? 'bg-red-600' : 'bg-green-600'}>
                      {selectedUser.is_suspended ? 'تعلیق شده' : 'فعال'}
                    </Badge>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <h3 className="text-white font-bold mb-3 flex items-center gap-2">
                    <StickyNote className="w-5 h-5" />
                    یادداشت‌ها ({userNotes.length})
                  </h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {userNotes.map((note) => (
                      <div key={note.id} className="bg-slate-800 rounded p-3">
                        <p className="text-white text-sm">{note.note}</p>
                        <div className="flex items-center justify-between mt-2 text-xs text-slate-200">
                          <span>توسط: {note.created_by_name}</span>
                          <span>{new Date(note.created_at).toLocaleString('fa-IR')}</span>
                        </div>
                      </div>
                    ))}
                    {userNotes.length === 0 && (
                      <p className="text-slate-200 text-sm text-center py-4">
                        یادداشتی ثبت نشده است
                      </p>
                    )}
                  </div>
                </div>

                {/* Activity Log */}
                <div>
                  <h3 className="text-white font-bold mb-3 flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    فعالیت‌ها ({userActivity.length})
                  </h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {userActivity.map((activity, idx) => (
                      <div key={idx} className="bg-slate-800 rounded p-3 flex items-center justify-between">
                        <div>
                          <p className="text-white text-sm">
                            {activity.action === 'user_suspended' ? 'تعلیق کاربر' :
                             activity.action === 'user_unsuspended' ? 'لغو تعلیق' :
                             activity.action}
                          </p>
                          {activity.details && (
                            <p className="text-slate-200 text-xs mt-1">
                              {activity.details.reason}
                            </p>
                          )}
                        </div>
                        <span className="text-xs text-slate-200">
                          {new Date(activity.timestamp).toLocaleString('fa-IR')}
                        </span>
                      </div>
                    ))}
                    {userActivity.length === 0 && (
                      <p className="text-slate-200 text-sm text-center py-4">
                        فعالیتی ثبت نشده است
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Bulk Action Modal */}
        {showBulkModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="bg-slate-900 border-slate-800 w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle className="text-white">تعلیق گروهی</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-slate-300">
                  آیا مطمئن هستید که می‌خواهید {selectedUsers.length} کاربر را تعلیق کنید؟
                </p>

                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => setShowBulkModal(false)}
                  >
                    انصراف
                  </Button>
                  <Button variant="destructive" onClick={bulkSuspend}>
                    تعلیق همه
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}