import React from 'react';

const OrderConfirmationModal = ({ isOpen, onClose, orderData }) => {
  if (!isOpen) return null;

  const downloadFactor = () => {
    const factorText = `
╔═══════════════════════════════╗
║        🧾 فاکتور خرید        ║
╚═══════════════════════════════╝

✅ سفارش شما با موفقیت ثبت شد!

📋 شماره سفارش: ${orderData.orderId}
📅 تاریخ: ${orderData.persianDate}
🕐 ساعت: ${orderData.orderTime}

💰 مبلغ پرداختی: ${orderData.amount_tmn.toLocaleString('fa-IR')} تومان
🪙 ارز درخواستی: ${orderData.coin_symbol}
📊 قیمت هر واحد: ${orderData.price_per_coin.toLocaleString('fa-IR')} تومان
💎 مقدار تقریبی: ${orderData.amount_crypto} ${orderData.coin_symbol}

✔️ مبلغ از موجودی شما کسر شد
⏳ وضعیت: در انتظار تایید ادمین

📌 مراحل بعدی:
1️⃣ ادمین سفارش شما را بررسی می‌کند
2️⃣ پس از تایید، ارز به کیف پول شما واریز می‌شود
3️⃣ اعلان تایید به شما ارسال خواهد شد

⏱️ زمان تقریبی: 1-24 ساعت

💡 می‌توانید وضعیت سفارش را در بخش "سفارشات من" پیگیری کنید

🙏 از صبر و شکیبایی شما سپاسگزاریم
    `;

    const blob = new Blob([factorText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `factor-${orderData.orderId}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" onClick={onClose}>
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border-2 border-green-500/30" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center animate-bounce">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">✅ سفارش ثبت شد!</h2>
                <p className="text-green-100 text-sm">سفارش شما با موفقیت در سیستم ثبت گردید</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Order Details */}
          <div className="bg-slate-700/50 rounded-xl p-5 space-y-4">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
              </svg>
              جزئیات سفارش
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-slate-400 text-sm mb-1">شماره سفارش</p>
                <p className="text-white font-mono text-sm">{orderData.orderId}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm mb-1">تاریخ و ساعت</p>
                <p className="text-white text-sm">{orderData.persianDate} - {orderData.orderTime}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm mb-1">مبلغ پرداختی</p>
                <p className="text-green-400 font-bold text-lg">{orderData.amount_tmn.toLocaleString('fa-IR')} تومان</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm mb-1">ارز درخواستی</p>
                <p className="text-white font-bold text-lg">{orderData.coin_symbol}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm mb-1">مقدار تقریبی</p>
                <p className="text-blue-400 font-bold">{orderData.amount_crypto} {orderData.coin_symbol}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm mb-1">قیمت واحد</p>
                <p className="text-white">{orderData.price_per_coin.toLocaleString('fa-IR')} تومان</p>
              </div>
            </div>
          </div>

          {/* Automated Process Info */}
          <div className="bg-blue-900/30 border-2 border-blue-500/30 rounded-xl p-5">
            <h3 className="text-lg font-bold text-blue-300 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
              </svg>
              فرآیندهای خودکار انجام شده
            </h3>
            <ul className="space-y-2 text-sm text-blue-100">
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">✓</span>
                <span>موجودی کیف پول شما {orderData.amount_tmn.toLocaleString('fa-IR')} تومان کسر گردید</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">✓</span>
                <span>تراکنش مالی در سیستم ثبت شد (شماره تراکنش: {orderData.transactionId?.substring(0, 8)}...)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">✓</span>
                <span>سفارش در صف تایید ادمین قرار گرفت</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-yellow-400 mt-0.5">⏳</span>
                <span>پس از تایید ادمین، اعلان به شما ارسال خواهد شد</span>
              </li>
            </ul>
          </div>

          {/* Next Steps */}
          <div className="bg-purple-900/30 border-2 border-purple-500/30 rounded-xl p-5">
            <h3 className="text-lg font-bold text-purple-300 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              مراحل بعدی چیست؟
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-purple-300 font-bold flex-shrink-0">1</div>
                <div>
                  <p className="text-white font-semibold">بررسی توسط ادمین</p>
                  <p className="text-slate-400 text-xs mt-1">ادمین سفارش شما را بررسی و تایید می‌کند</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-purple-300 font-bold flex-shrink-0">2</div>
                <div>
                  <p className="text-white font-semibold">واریز ارز دیجیتال</p>
                  <p className="text-slate-400 text-xs mt-1">پس از تایید، {orderData.coin_symbol} به آدرس کیف پول شما واریز می‌شود</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-purple-500/30 rounded-full flex items-center justify-center text-purple-300 font-bold flex-shrink-0">3</div>
                <div>
                  <p className="text-white font-semibold">دریافت اعلان</p>
                  <p className="text-slate-400 text-xs mt-1">اعلان تایید به شما ارسال می‌شود و می‌توانید در "سفارشات من" پیگیری کنید</p>
                </div>
              </div>
            </div>
            <div className="mt-4 bg-purple-800/30 rounded-lg p-3 flex items-center gap-3">
              <svg className="w-5 h-5 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <p className="text-purple-200 text-xs">⏱️ زمان تقریبی تایید: 1 تا 24 ساعت</p>
            </div>
          </div>

          {/* Suggestions */}
          <div className="bg-amber-900/30 border-2 border-amber-500/30 rounded-xl p-5">
            <h3 className="text-lg font-bold text-amber-300 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              توصیه‌های مفید
            </h3>
            <ul className="space-y-2 text-sm text-amber-100">
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-0.5">💡</span>
                <span>می‌توانید در بخش "سفارشات من" وضعیت سفارش را پیگیری کنید</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-0.5">💡</span>
                <span>اعلان‌های خود را از طریق آیکون زنگ بررسی کنید</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-0.5">💡</span>
                <span>برای سفارش‌های بیشتر، ابتدا موجودی کیف پول خود را شارژ کنید</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-slate-700 flex gap-3">
          <button
            onClick={downloadFactor}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            دانلود فاکتور
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-3 px-6 rounded-lg font-semibold transition-all"
          >
            متوجه شدم، متشکرم!
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmationModal;
