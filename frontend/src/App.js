import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import AuthPage from "./pages/AuthPageEnhanced";
import Dashboard from "./pages/Dashboard";
import KYCPage from "./pages/KYCPage";
import Market from "./pages/Market";
import Wallet from "./pages/Wallet";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminCards from "./pages/admin/AdminCards";
import AdminDeposits from "./pages/admin/AdminDeposits";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Axios interceptor for auth token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get(`${API}/auth/me`);
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/auth" 
            element={user ? <Navigate to={user.is_admin ? "/admin" : "/dashboard"} /> : <AuthPage onLogin={handleLogin} />} 
          />
          <Route 
            path="/dashboard" 
            element={user && !user.is_admin ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to={user?.is_admin ? "/admin" : "/auth"} />} 
          />
          <Route 
            path="/kyc" 
            element={user ? <KYCPage user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/market" 
            element={user ? <Market user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/wallet" 
            element={user ? <Wallet user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin" 
            element={user?.is_admin ? <AdminDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/users" 
            element={user?.is_admin ? <AdminUsers user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/cards" 
            element={user?.is_admin ? <AdminCards user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/deposits" 
            element={user?.is_admin ? <AdminDeposits user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/" 
            element={<Navigate to={user ? (user.is_admin ? "/admin" : "/dashboard") : "/auth"} />} 
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;