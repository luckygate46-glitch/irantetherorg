import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { 
  MessageCircle, 
  Brain,
  Send,
  User,
  Bot,
  Lightbulb,
  TrendingUp,
  Shield,
  PieChart,
  DollarSign,
  Clock,
  Star,
  BookOpen,
  HelpCircle,
  Sparkles
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserAIAssistant = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      message: 'سلام! من دستیار هوشمند معاملاتی شما هستم. می‌توانم در زمینه‌های زیر به شما کمک کنم:\n\n• تحلیل بازار و ارزهای دیجیتال\n• مدیریت پرتفوی و ریسک\n• استراتژی‌های معاملاتی\n• بهینه‌سازی سرمایه‌گذاری\n\nسوال خود را بپرسید!',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [quickQuestions] = useState([
    'چگونه ریسک پرتفوی خود را کاهش دهم؟',
    'بهترین زمان برای خرید Bitcoin چیست؟',
    'چگونه پرتفوی متنوع ایجاد کنم؟',
    'تحلیل تکنیکال چیست؟',
    'چگونه از Stop Loss استفاده کنم؟',
    'DCA strategy چیست؟'
  ]);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    scrollToBottom();
  }, [user, navigate, messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      message: message.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/user/ai/ask-assistant`, {
        question: message.trim()
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        message: response.data.response,
        timestamp: response.data.generated_at,
        context: response.data.context
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('خطا در ارسال پیام:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        message: 'متأسفانه در حال حاضر امکان پاسخ‌دهی وجود ندارد. لطفاً دوباره تلاش کنید.',
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: 'خطا',
        description: 'خطا در ارتباط با دستیار هوشمند',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('fa-IR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getQuestionIcon = (question) => {
    if (question.includes('ریسک')) return <Shield className="w-4 h-4" />;
    if (question.includes('Bitcoin') || question.includes('خرید')) return <TrendingUp className="w-4 h-4" />;
    if (question.includes('پرتفوی')) return <PieChart className="w-4 h-4" />;
    if (question.includes('تحلیل')) return <BookOpen className="w-4 h-4" />;
    return <HelpCircle className="w-4 h-4" />;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white" dir="rtl">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <MessageCircle className="w-8 h-8 text-emerald-400" />
              <h1 className="text-2xl font-bold text-emerald-400">دستیار هوشمند</h1>
              <Badge className="bg-emerald-600 text-white">آنلاین</Badge>
            </div>
            <nav className="flex gap-4">
              <Button 
                onClick={() => navigate('/ai/dashboard')}
                variant="ghost"
                className="text-slate-300 hover:text-white"
              >
                داشبورد AI
              </Button>
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

      <div className="max-w-4xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Chat Area */}
          <div className="lg:col-span-3">
            <Card className="bg-slate-900 border-slate-800 h-[600px] flex flex-col">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  گفتگو با دستیار هوشمند
                </CardTitle>
              </CardHeader>
              
              {/* Messages */}
              <CardContent className="flex-1 overflow-hidden">
                <div className="h-full overflow-y-auto space-y-4 pr-2">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex gap-3 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        msg.type === 'user' 
                          ? 'bg-emerald-600' 
                          : msg.isError 
                            ? 'bg-red-600' 
                            : 'bg-purple-600'
                      }`}>
                        {msg.type === 'user' ? (
                          <User className="w-4 h-4" />
                        ) : (
                          <Bot className="w-4 h-4" />
                        )}
                      </div>
                      
                      <div className={`flex-1 ${msg.type === 'user' ? 'text-right' : ''}`}>
                        <div
                          className={`inline-block p-3 rounded-lg max-w-[80%] ${
                            msg.type === 'user'
                              ? 'bg-emerald-600 text-white'
                              : msg.isError
                                ? 'bg-red-900/20 border border-red-800 text-red-300'
                                : 'bg-slate-800 text-slate-200'
                          }`}
                        >
                          <div className="whitespace-pre-wrap">{msg.message}</div>
                          {msg.context && (
                            <div className="mt-2 pt-2 border-t border-slate-700 text-xs text-slate-400">
                              پرتفوی: {new Intl.NumberFormat('fa-IR').format(msg.context.portfolio_value)} تومان
                              {msg.context.holdings_count > 0 && ` • ${msg.context.holdings_count} دارایی`}
                            </div>
                          )}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          {formatTime(msg.timestamp)}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {loading && (
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                        <Bot className="w-4 h-4" />
                      </div>
                      <div className="bg-slate-800 p-3 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-purple-400"></div>
                          <span className="text-slate-400">در حال تفکر...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </CardContent>
              
              {/* Input Area */}
              <div className="p-4 border-t border-slate-800">
                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="سوال خود را بنویسید..."
                    className="flex-1 bg-slate-800 border-slate-700 text-white placeholder:text-slate-400"
                    disabled={loading}
                  />
                  <Button 
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || loading}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Questions */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  سوالات متداول
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {quickQuestions.map((question, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => handleSendMessage(question)}
                      disabled={loading}
                      className="w-full text-right justify-start h-auto p-3 text-xs bg-slate-800 border-slate-700 hover:bg-slate-700"
                    >
                      <div className="flex items-start gap-2">
                        {getQuestionIcon(question)}
                        <span className="flex-1 whitespace-normal leading-relaxed">
                          {question}
                        </span>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Capabilities */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  قابلیت‌های AI
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span>تحلیل بازار و روندها</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <PieChart className="w-4 h-4 text-blue-400" />
                    <span>بهینه‌سازی پرتفوی</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-red-400" />
                    <span>مدیریت ریسک</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-yellow-400" />
                    <span>آموزش معاملات</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-emerald-400" />
                    <span>استراتژی‌های سرمایه‌گذاری</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Chat Statistics */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400" />
                  آمار گفتگو
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">کل پیام‌ها</span>
                    <span className="text-white">{messages.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">پیام‌های شما</span>
                    <span className="text-emerald-400">
                      {messages.filter(m => m.type === 'user').length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">پاسخ‌های AI</span>
                    <span className="text-purple-400">
                      {messages.filter(m => m.type === 'ai').length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">وضعیت</span>
                    <Badge className="bg-green-600 text-white text-xs">فعال</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-400" />
                  نکات مفید
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-xs text-slate-300">
                  <li className="flex items-start gap-2">
                    <span className="w-1 h-1 bg-emerald-400 rounded-full mt-2"></span>
                    <span>سوالات مشخص و دقیق بپرسید</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1 h-1 bg-emerald-400 rounded-full mt-2"></span>
                    <span>از کلمات کلیدی استفاده کنید</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1 h-1 bg-emerald-400 rounded-full mt-2"></span>
                    <span>پیام‌های کوتاه بهتر پردازش می‌شوند</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="w-1 h-1 bg-emerald-400 rounded-full mt-2"></span>
                    <span>برای مشاوره دقیق‌تر جزئیات بدهید</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserAIAssistant;