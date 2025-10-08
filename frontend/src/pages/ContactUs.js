import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Phone, Mail, Clock, MapPin, MessageCircle, Send, Headphones, HelpCircle } from 'lucide-react';

const ContactUs = ({ user }) => {
  const [contactForm, setContactForm] = useState({
    subject: '',
    department: 'support',
    message: '',
    phone: user?.phone || '',
    email: user?.email || ''
  });
  const [loading, setLoading] = useState(false);

  const departments = [
    { value: 'support', label: 'پشتیبانی فنی', icon: Headphones },
    { value: 'trading', label: 'واحد معاملات', icon: MessageCircle },
    { value: 'kyc', label: 'احراز هویت', icon: HelpCircle },
    { value: 'financial', label: 'واحد مالی', icon: Phone },
    { value: 'legal', label: 'مسائل حقوقی', icon: Mail }
  ];

  const contactMethods = [
    {
      title: 'تلفن پشتیبانی',
      icon: Phone,
      details: '021-1234-5678',
      description: '24 ساعته، 7 روز هفته',
      color: 'text-green-500'
    },
    {
      title: 'ایمیل',
      icon: Mail,
      details: 'support@irantrader.com',
      description: 'پاسخ در کمتر از 2 ساعت',
      color: 'text-blue-500'
    },
    {
      title: 'چت آنلاین',
      icon: MessageCircle,
      details: 'فعال',
      description: 'از ساعت 8 صبح تا 11 شب',
      color: 'text-purple-500'
    },
    {
      title: 'ساعات کاری',
      icon: Clock,
      details: 'شنبه تا پنج‌شنبه',
      description: '8:00 صبح - 11:00 شب',
      color: 'text-orange-500'
    }
  ];

  const faqs = [
    {
      question: 'چگونه KYC خود را تکمیل کنم؟',
      answer: 'برای تکمیل KYC از منوی کناری وارد بخش احراز هویت شوید و مراحل را دنبال کنید.'
    },
    {
      question: 'چرا واریز من به حساب اضافه نشده؟',
      answer: 'واریز‌ها معمولاً تا 30 دقیقه طول می‌کشد. در صورت تأخیر با پشتیبانی تماس بگیرید.'
    },
    {
      question: 'حداقل مبلغ برای معامله چقدر است؟',
      answer: 'حداقل مبلغ برای هر معامله 10 هزار تومان است.'
    },
    {
      question: 'آیا می‌توانم از خارج از ایران استفاده کنم؟',
      answer: 'در حال حاضر صرافی فقط برای کاربران ایرانی فعال است.'
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!contactForm.subject || !contactForm.message) {
      alert('لطفا موضوع و پیام را پر کنید');
      return;
    }

    setLoading(true);
    
    try {
      // Simulate form submission
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      alert('پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.');
      setContactForm({
        subject: '',
        department: 'support',
        message: '',
        phone: user?.phone || '',
        email: user?.email || ''
      });
    } catch (error) {
      alert('خطا در ارسال پیام. لطفا مجدداً تلاش کنید.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <div className="flex items-center gap-3 mb-6">
        <Phone className="w-8 h-8 text-blue-500" />
        <div>
          <h1 className="text-2xl font-bold text-white">تماس با ما</h1>
          <p className="text-gray-400">ما اینجاییم تا به شما کمک کنیم</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contact Form */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Send className="w-5 h-5" />
              ارسال پیام
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  موضوع
                </label>
                <input
                  type="text"
                  value={contactForm.subject}
                  onChange={(e) => setContactForm({...contactForm, subject: e.target.value})}
                  placeholder="موضوع پیام شما"
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  بخش مرتبط
                </label>
                <select
                  value={contactForm.department}
                  onChange={(e) => setContactForm({...contactForm, department: e.target.value})}
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                >
                  {departments.map(dept => (
                    <option key={dept.value} value={dept.value}>
                      {dept.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    شماره تلفن
                  </label>
                  <input
                    type="tel"
                    value={contactForm.phone}
                    onChange={(e) => setContactForm({...contactForm, phone: e.target.value})}
                    placeholder="09xxxxxxxxx"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    ایمیل
                  </label>
                  <input
                    type="email"
                    value={contactForm.email}
                    onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                    placeholder="email@example.com"
                    className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  پیام شما
                </label>
                <textarea
                  value={contactForm.message}
                  onChange={(e) => setContactForm({...contactForm, message: e.target.value})}
                  placeholder="پیام، سوال یا مشکل خود را به تفصیل بنویسید..."
                  className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white resize-none"
                  rows="5"
                  required
                />
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  'در حال ارسال...'
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    ارسال پیام
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <div className="space-y-6">
          {/* Contact Methods */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white">راه‌های ارتباطی</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {contactMethods.map((method, index) => {
                  const Icon = method.icon;
                  return (
                    <div key={index} className="flex items-start gap-3 p-3 bg-slate-800 rounded-lg">
                      <Icon className={`w-6 h-6 ${method.color} mt-1`} />
                      <div className="flex-1">
                        <h3 className="font-medium text-white">{method.title}</h3>
                        <p className="text-lg text-gray-300 mt-1">{method.details}</p>
                        <p className="text-sm text-gray-400">{method.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white">دسترسی سریع</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {departments.map(dept => {
                const Icon = dept.icon;
                return (
                  <Button
                    key={dept.value}
                    variant="outline"
                    className="w-full justify-start h-auto p-3"
                    onClick={() => setContactForm({...contactForm, department: dept.value})}
                  >
                    <Icon className="w-5 h-5 ml-3" />
                    <div className="text-right">
                      <div className="font-medium">{dept.label}</div>
                      <div className="text-xs text-gray-400">
                        {dept.value === 'support' && 'مشکلات فنی و عمومی'}
                        {dept.value === 'trading' && 'سوالات مربوط به معاملات'}
                        {dept.value === 'kyc' && 'احراز هویت و تایید مدارک'}
                        {dept.value === 'financial' && 'واریز، برداشت و مسائل مالی'}
                        {dept.value === 'legal' && 'مسائل حقوقی و قانونی'}
                      </div>
                    </div>
                  </Button>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* FAQ Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <HelpCircle className="w-5 h-5" />
            سوالات متداول
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-slate-800 rounded-lg p-4">
                <h3 className="font-medium text-white mb-2">{faq.question}</h3>
                <p className="text-gray-300 text-sm">{faq.answer}</p>
              </div>
            ))}
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-400 mb-3">سوال شما در لیست نیست؟</p>
            <Button 
              variant="outline"
              onClick={() => document.querySelector('textarea').focus()}
            >
              سوال خود را بپرسید
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Emergency Contact */}
      <Card className="bg-red-900/20 border border-red-600/30">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <Phone className="w-6 h-6 text-red-400" />
            <div>
              <h3 className="font-medium text-red-300">تماس اضطراری</h3>
              <p className="text-red-200 text-sm">
                در صورت مشکلات امنیتی یا سرقت حساب: <span className="font-mono">021-9999-0000</span>
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ContactUs;