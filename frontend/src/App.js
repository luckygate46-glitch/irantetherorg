import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import AuthPage from "./pages/SimpleAuth";
import Dashboard from "./pages/Dashboard";
import KYCPage from "./pages/KYCPage";
import Market from "./pages/Market";
import Wallet from "./pages/Wallet";
import Trade from "./pages/Trade";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminCards from "./pages/admin/AdminCards";
import AdminDeposits from "./pages/admin/AdminDeposits";
import AdminOrders from "./pages/admin/AdminOrders";
import AdminKYC from "./pages/admin/AdminKYC";
import AdminDashboardAI from "./pages/admin/AdminDashboardAI";
import AdminPriceManager from "./pages/admin/AdminPriceManager";
import AdminTradingManager from "./pages/admin/AdminTradingManager";
import AdminFraudDetection from "./pages/admin/AdminFraudDetection";
import AdminAdvancedAnalytics from "./pages/admin/AdminAdvancedAnalytics";
import AdminAIAssistant from "./pages/admin/AdminAIAssistant";
import UserAIDashboard from "./pages/UserAIDashboard";
import UserAIAssistant from "./pages/UserAIAssistant";
import UserAIRecommendations from "./pages/UserAIRecommendations";
import MultiAssetTrading from "./pages/MultiAssetTrading";
import StakingYieldFarming from "./pages/StakingYieldFarming";
import PortfolioAnalysis from "./pages/PortfolioAnalysis";
import KYCWaitingGame from "./pages/KYCWaitingGame";
import CurrencyExchange from "./pages/CurrencyExchange";
import SupportTickets from "./pages/SupportTickets";
import ContactUs from "./pages/ContactUs";
import Rewards from "./pages/Rewards";
import Portfolio from "./pages/Portfolio";
import UserProfile from "./pages/UserProfile";
import UserSidebarLayout from "./layouts/UserSidebarLayout";

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

  const handleUserUpdate = (updatedUser) => {
    setUser(updatedUser);
  };

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
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Dashboard user={user} onUserUpdate={handleUserUpdate} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to={user?.is_admin ? "/admin" : "/auth"} />} 
          />
          <Route 
            path="/kyc" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <KYCPage user={user} onUserUpdate={handleUserUpdate} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/market" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Market user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/wallet" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Wallet user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/trade" 
            element={user && !user.is_admin && user.kyc_level >= 2 ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Trade user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : user && !user.is_admin && user.kyc_level < 2 ? <Navigate to="/kyc" /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/trade/:asset" 
            element={user && !user.is_admin && user.kyc_level >= 2 ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Trade user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : user && !user.is_admin && user.kyc_level < 2 ? <Navigate to="/kyc" /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin" 
            element={user?.is_admin ? <AdminDashboardAI user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
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
            path="/admin/orders" 
            element={user?.is_admin ? <AdminOrders user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/kyc" 
            element={user?.is_admin ? <AdminKYC user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/prices" 
            element={user?.is_admin ? <AdminPriceManager user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/trading" 
            element={user?.is_admin ? <AdminTradingManager user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/ai/fraud" 
            element={user?.is_admin ? <AdminFraudDetection user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/ai/analytics" 
            element={user?.is_admin ? <AdminAdvancedAnalytics user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/ai/assistant" 
            element={user?.is_admin ? <AdminAIAssistant user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/ai/dashboard" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <UserAIDashboard user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/ai/assistant" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <UserAIAssistant user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/ai/recommendations" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <UserAIRecommendations user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/multi-asset" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <MultiAssetTrading user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/staking" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <StakingYieldFarming user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/ai/portfolio-analysis" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <PortfolioAnalysis user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/kyc-game" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <KYCWaitingGame user={user} onLogout={handleLogout} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/currency-exchange" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <CurrencyExchange user={user} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/support-tickets" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <SupportTickets user={user} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/contact-us" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <ContactUs user={user} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/rewards" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Rewards user={user} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
          />
          <Route 
            path="/portfolio" 
            element={user && !user.is_admin ? (
              <UserSidebarLayout user={user} onLogout={handleLogout}>
                <Portfolio user={user} />
              </UserSidebarLayout>
            ) : <Navigate to="/auth" />} 
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