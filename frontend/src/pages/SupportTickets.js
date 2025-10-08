import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Ticket, Plus, Clock, CheckCircle, AlertCircle, MessageSquare, Send } from 'lucide-react';

const SupportTickets = ({ user }) => {
  const [tickets, setTickets] = useState([]);
  const [showNewTicket, setShowNewTicket] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [newTicket, setNewTicket] = useState({
    subject: '',
    category: 'general',
    priority: 'medium',
    description: ''
  });
  const [newMessage, setNewMessage] = useState('');

  // Sample tickets data
  const sampleTickets = [
    {
      id: '1001',
      subject: 'مشکل در واریز',
      category: 'deposit',
      priority: 'high',
      status: 'open',
      created_at: '2024-10-08T10:30:00',
      updated_at: '2024-10-08T14:20:00',
      messages: [
        {
          id: 1,
          sender: 'user',
          message: 'سلام، من واریز کردم ولی به حساب اضافه نشد.',
          timestamp: '2024-10-08T10:30:00'
        },
        {
          id: 2,
          sender: 'support',
          message: 'سلام، لطفا شماره تراکنش را ارسال کنید.',
          timestamp: '2024-10-08T11:15:00'
        }
      ]
    },
    {
      id: '1002',
      subject: 'سوال درباره KYC',
      category: 'kyc',
      priority: 'medium',
      status: 'resolved',
      created_at: '2024-10-07T09:15:00',
      updated_at: '2024-10-07T16:45:00',
      messages: [
        {
          id: 1,
          sender: 'user',
          message: 'چه مدارکی برای KYC سطح 2 نیاز است؟',
          timestamp: '2024-10-07T09:15:00'
        },
        {
          id: 2,
          sender: 'support',
          message: 'برای KYC سطح 2 نیاز به کارت ملی و سلفی دارید.',
          timestamp: '2024-10-07T16:45:00'
        }
      ]
    }
  ];

  useEffect(() => {
    setTickets(sampleTickets);
  }, []);

  const categories = [
    { value: 'general', label: 'عمومی' },
    { value: 'deposit', label: 'واریز' },
    { value: 'withdrawal', label: 'برداشت' },
    { value: 'trading', label: 'معاملات' },
    { value: 'kyc', label: 'احراز هویت' },
    { value: 'technical', label: 'فنی' }
  ];

  const priorities = [
    { value: 'low', label: 'کم', color: 'bg-green-500' },
    { value: 'medium', label: 'متوسط', color: 'bg-yellow-500' },
    { value: 'high', label: 'بالا', color: 'bg-red-500' }
  ];

  const getStatusBadge = (status) => {
    const statusConfig = {
      open: { label: 'باز', variant: 'default' },
      in_progress: { label: 'در حال بررسی', variant: 'secondary' },
      resolved: { label: 'حل شده', variant: 'success' },
      closed: { label: 'بسته شده', variant: 'destructive' }
    };
    
    return statusConfig[status] || statusConfig.open;
  };

  const getPriorityColor = (priority) => {
    const config = priorities.find(p => p.value === priority);
    return config ? config.color : 'bg-gray-500';
  };

  const handleNewTicket = () => {
    if (!newTicket.subject || !newTicket.description) {
      alert('لطفا موضوع و توضیحات را پر کنید');
      return;
    }

    const ticket = {
      id: (tickets.length + 1001).toString(),
      subject: newTicket.subject,
      category: newTicket.category,
      priority: newTicket.priority,
      status: 'open',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: [
        {
          id: 1,
          sender: 'user',
          message: newTicket.description,
          timestamp: new Date().toISOString()
        }
      ]
    };

    setTickets([ticket, ...tickets]);
    setNewTicket({ subject: '', category: 'general', priority: 'medium', description: '' });
    setShowNewTicket(false);
    alert('تیکت شما با موفقیت ثبت شد');
  };

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedTicket) return;

    const updatedTickets = tickets.map(ticket => {
      if (ticket.id === selectedTicket.id) {
        return {
          ...ticket,
          messages: [
            ...ticket.messages,
            {
              id: ticket.messages.length + 1,
              sender: 'user',
              message: newMessage,
              timestamp: new Date().toISOString()
            }
          ],
          updated_at: new Date().toISOString()
        };
      }
      return ticket;
    });

    setTickets(updatedTickets);
    setSelectedTicket(updatedTickets.find(t => t.id === selectedTicket.id));
    setNewMessage('');
  };

  if (selectedTicket) {
    return (
      <div className="p-6" dir="rtl">
        <div className="mb-6">
          <Button
            variant="outline"
            onClick={() => setSelectedTicket(null)}
            className="mb-4"
          >
            ← بازگشت به لیست تیکت‌ها
          </Button>
          
          <div className="flex items-center gap-3 mb-2">
            <Ticket className="w-6 h-6 text-blue-500" />
            <h1 className="text-xl font-bold text-white">تیکت #{selectedTicket.id}</h1>
            <Badge {...getStatusBadge(selectedTicket.status)}>
              {getStatusBadge(selectedTicket.status).label}
            </Badge>
          </div>
          
          <p className="text-gray-400">{selectedTicket.subject}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Messages */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-white">پیام‌ها</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {selectedTicket.messages.map(message => (
                  <div
                    key={message.id}
                    className={`p-3 rounded-lg ${
                      message.sender === 'user' 
                        ? 'bg-blue-600/20 mr-8' 
                        : 'bg-slate-700 ml-8'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-white">
                        {message.sender === 'user' ? 'شما' : 'پشتیبانی'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(message.timestamp).toLocaleString('fa-IR')}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm">{message.message}</p>
                  </div>
                ))}
              </div>

              {/* Send Message */}
              {selectedTicket.status !== 'closed' && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="flex gap-2">
                    <textarea
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="پیام خود را بنویسید..."
                      className="flex-1 bg-slate-700 border border-slate-600 rounded-md p-3 text-white resize-none"
                      rows="3"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!newMessage.trim()}
                      className="self-end"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Ticket Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white">جزئیات تیکت</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <span className="text-sm text-gray-400">شماره تیکت:</span>
                <p className="text-white font-mono">#{selectedTicket.id}</p>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">موضوع:</span>
                <p className="text-white">{selectedTicket.subject}</p>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">دسته‌بندی:</span>
                <p className="text-white">
                  {categories.find(c => c.value === selectedTicket.category)?.label}
                </p>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">اولویت:</span>
                <div className="flex items-center gap-2 mt-1">
                  <div className={`w-3 h-3 rounded-full ${getPriorityColor(selectedTicket.priority)}`}></div>
                  <span className="text-white">
                    {priorities.find(p => p.value === selectedTicket.priority)?.label}
                  </span>
                </div>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">تاریخ ایجاد:</span>
                <p className="text-white">
                  {new Date(selectedTicket.created_at).toLocaleDateString('fa-IR')}
                </p>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">آخرین بروزرسانی:</span>
                <p className="text-white">
                  {new Date(selectedTicket.updated_at).toLocaleDateString('fa-IR')}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Ticket className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-2xl font-bold text-white">تیکت‌های پشتیبانی</h1>
            <p className="text-gray-400">مدیریت درخواست‌های پشتیبانی شما</p>
          </div>
        </div>
        
        <Button
          onClick={() => setShowNewTicket(!showNewTicket)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          تیکت جدید
        </Button>
      </div>

      {/* New Ticket Form */}
      {showNewTicket && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white">ایجاد تیکت جدید</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  موضوع
                </label>
                <input
                  type="text"
                  value={newTicket.subject}
                  onChange={(e) => setNewTicket({...newTicket, subject: e.target.value})}
                  placeholder="موضوع تیکت را وارد کنید"
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  دسته‌بندی
                </label>
                <select
                  value={newTicket.category}
                  onChange={(e) => setNewTicket({...newTicket, category: e.target.value})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                >
                  {categories.map(category => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  اولویت
                </label>
                <select
                  value={newTicket.priority}
                  onChange={(e) => setNewTicket({...newTicket, priority: e.target.value})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                >
                  {priorities.map(priority => (
                    <option key={priority.value} value={priority.value}>
                      {priority.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                توضیحات
              </label>
              <textarea
                value={newTicket.description}
                onChange={(e) => setNewTicket({...newTicket, description: e.target.value})}
                placeholder="مشکل یا سوال خود را به تفصیل بنویسید"
                className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white resize-none"
                rows="4"
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleNewTicket} className="bg-blue-600 hover:bg-blue-700">
                ثبت تیکت
              </Button>
              <Button variant="outline" onClick={() => setShowNewTicket(false)}>
                انصراف
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tickets List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white">لیست تیکت‌ها</CardTitle>
        </CardHeader>
        <CardContent>
          {tickets.length === 0 ? (
            <div className="text-center py-8">
              <Ticket className="w-12 h-12 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-400">هنوز تیکتی ثبت نکرده‌اید</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tickets.map(ticket => (
                <div
                  key={ticket.id}
                  className="bg-slate-800 rounded-lg p-4 cursor-pointer hover:bg-slate-700 transition-colors"
                  onClick={() => setSelectedTicket(ticket)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm text-gray-400">#{ticket.id}</span>
                      <h3 className="font-medium text-white">{ticket.subject}</h3>
                    </div>
                    <Badge {...getStatusBadge(ticket.status)}>
                      {getStatusBadge(ticket.status).label}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <div className="flex items-center gap-4">
                      <span>
                        {categories.find(c => c.value === ticket.category)?.label}
                      </span>
                      <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${getPriorityColor(ticket.priority)}`}></div>
                        {priorities.find(p => p.value === ticket.priority)?.label}
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" />
                        {ticket.messages.length}
                      </div>
                    </div>
                    <span>{new Date(ticket.updated_at).toLocaleDateString('fa-IR')}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SupportTickets;