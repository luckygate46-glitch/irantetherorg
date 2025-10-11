import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function SimpleAuth({ onLogin }) {
  const [activeTab, setActiveTab] = useState("login");
  const [loginData, setLoginData] = useState({
    email: "",
    password: ""
  });
  const [registerData, setRegisterData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: ""
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    console.log('🔴 handleLogin CALLED!', e);
    e.preventDefault();
    console.log('🔴 preventDefault called');
    console.log('🔴 loginData:', loginData);
    console.log('🔴 API URL:', `${API}/auth/login`);
    console.log('🔴 onLogin prop:', onLogin, typeof onLogin);
    
    setLoading(true);
    setMessage("در حال ورود...");
    console.log('🔴 Set loading=true and message');
    
    try {
      console.log('🔴 About to make axios POST request...');
      const response = await axios.post(`${API}/auth/login`, loginData);
      console.log('🔴 Response received:', response);
      
      if (onLogin && typeof onLogin === 'function') {
        console.log('🔴 Calling onLogin...');
        onLogin(response.data.access_token, response.data.user);
        setMessage('ورود موفق! در حال انتقال...');
        console.log('🔴 Login successful!');
      } else {
        console.log('❌ onLogin is not a function!', onLogin);
        setMessage('خطا: تابع onLogin یافت نشد');
      }
      
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error message:', error.message);
      setMessage('خطا در ورود: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
      console.log('🔴 handleLogin completed, loading=false');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("در حال ثبت‌نام...");
    
    try {
      const response = await axios.post(`${API}/auth/register`, registerData);
      
      if (onLogin && typeof onLogin === 'function') {
        onLogin(response.data.access_token, response.data.user);
        setMessage('ثبت‌نام موفق! در حال انتقال...');
      } else {
        setMessage('خطا: تابع onLogin یافت نشد');
      }
      
    } catch (error) {
      console.error('Registration error:', error);
      setMessage('خطا در ثبت‌نام: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '4px',
    border: '1px solid #475569',
    backgroundColor: '#334155',
    color: 'white',
    boxSizing: 'border-box',
    marginBottom: '1rem'
  };

  const buttonStyle = {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '4px',
    border: 'none',
    color: 'white',
    cursor: 'pointer',
    fontSize: '1rem',
    marginBottom: '0.5rem'
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0f172a',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        backgroundColor: '#1e293b',
        padding: '2rem',
        borderRadius: '8px',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>صرافی کریپتو ایران</h2>
        <p style={{ textAlign: 'center', marginBottom: '2rem', opacity: 0.8 }}>
          برای شروع معاملات وارد شوید یا ثبت نام کنید
        </p>
        
        {/* Tab Buttons */}
        <div style={{ display: 'flex', marginBottom: '2rem', gap: '0.5rem' }}>
          <button
            onClick={() => setActiveTab("login")}
            style={{
              ...buttonStyle,
              backgroundColor: activeTab === "login" ? '#059669' : '#374151',
              marginBottom: 0
            }}
          >
            ورود
          </button>
          <button
            onClick={() => setActiveTab("register")}
            style={{
              ...buttonStyle,
              backgroundColor: activeTab === "register" ? '#059669' : '#374151',
              marginBottom: 0
            }}
          >
            ثبت‌نام
          </button>
        </div>

        {/* Login Form */}
        {activeTab === "login" && (
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>ایمیل یا نام کاربری:</label>
              <input
                type="text"
                value={loginData.email}
                onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                style={inputStyle}
                placeholder="admin یا email@example.com"
                required
              />
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>رمز عبور:</label>
              <input
                type="password"
                value={loginData.password}
                onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                style={inputStyle}
                placeholder="رمز عبور خود را وارد کنید"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              style={{
                ...buttonStyle,
                backgroundColor: loading ? '#6b7280' : '#059669',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? "در حال ورود..." : "ورود"}
            </button>
          </form>
        )}

        {/* Register Form */}
        {activeTab === "register" && (
          <form onSubmit={handleRegister}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>نام:</label>
              <input
                type="text"
                value={registerData.first_name}
                onChange={(e) => setRegisterData({...registerData, first_name: e.target.value})}
                style={inputStyle}
                placeholder="نام خود را وارد کنید"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>نام خانوادگی:</label>
              <input
                type="text"
                value={registerData.last_name}
                onChange={(e) => setRegisterData({...registerData, last_name: e.target.value})}
                style={inputStyle}
                placeholder="نام خانوادگی خود را وارد کنید"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>ایمیل:</label>
              <input
                type="email"
                value={registerData.email}
                onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                style={inputStyle}
                placeholder="email@example.com"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>شماره موبایل:</label>
              <input
                type="tel"
                value={registerData.phone}
                onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
                style={inputStyle}
                placeholder="09xxxxxxxxx"
                required
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>رمز عبور:</label>
              <input
                type="password"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                style={inputStyle}
                placeholder="رمز عبور خود را وارد کنید"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              style={{
                ...buttonStyle,
                backgroundColor: loading ? '#6b7280' : '#059669',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? "در حال ثبت‌نام..." : "ثبت‌نام"}
            </button>
          </form>
        )}
        
        {message && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem',
            borderRadius: '4px',
            backgroundColor: message.includes('خطا') ? '#7f1d1d' : '#065f46',
            color: message.includes('خطا') ? '#fecaca' : '#a7f3d0'
          }}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}