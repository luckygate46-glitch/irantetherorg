import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function SimpleAuth({ onLogin }) {
  const [loginData, setLoginData] = useState({
    email: "admin",
    password: "istari118"
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("در حال ورود...");
    
    try {
      console.log('Attempting login with:', loginData);
      console.log('API URL:', API);
      
      const response = await axios.post(`${API}/auth/login`, loginData);
      console.log('Login response:', response.data);
      
      if (onLogin && typeof onLogin === 'function') {
        onLogin(response.data.access_token, response.data.user);
        setMessage('ورود موفق! در حال انتقال...');
      } else {
        setMessage('خطا: تابع onLogin یافت نشد');
      }
      
    } catch (error) {
      console.error('Login error:', error);
      setMessage('خطا در ورود: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
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
        <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>صرافی کریپتو ایران</h2>
        
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>ایمیل:</label>
            <input
              type="text"
              value={loginData.email}
              onChange={(e) => setLoginData({...loginData, email: e.target.value})}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '4px',
                border: '1px solid #475569',
                backgroundColor: '#334155',
                color: 'white',
                boxSizing: 'border-box'
              }}
              required
            />
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>رمز عبور:</label>
            <input
              type="password"
              value={loginData.password}
              onChange={(e) => setLoginData({...loginData, password: e.target.value})}
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: '4px',
                border: '1px solid #475569',
                backgroundColor: '#334155',
                color: 'white',
                boxSizing: 'border-box'
              }}
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              borderRadius: '4px',
              border: 'none',
              backgroundColor: loading ? '#6b7280' : '#059669',
              color: 'white',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '1rem'
            }}
          >
            {loading ? "در حال ورود..." : "ورود"}
          </button>
        </form>
        
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