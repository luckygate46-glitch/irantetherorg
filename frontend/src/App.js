import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import ProtectedRoute from "./components/ProtectedRoute";
import NotificationToastManager from "./components/NotificationToastManager";
import LandingPage from "./pages/LandingPage";
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
import AdminAISettings from "./pages/admin/AdminAISettings";
import AdminAICenter from "./pages/admin/AdminAICenter";
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

// AI Admin Components
import AIIntelligenceDashboard from "./pages/admin/AIIntelligenceDashboard";
import AISecurityCenter from "./pages/admin/AISecurityCenter";
import AIUserAnalytics from "./pages/admin/AIUserAnalytics";

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

  // Manual refresh user data
  const refreshUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const response = await axios.get(`${BACKEND_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setUser(response.data);
      console.log('✅ User data refreshed:', response.data.wallet_balance_tmn);
    } catch (error) {
      console.error('❌ Refresh failed:', error);
    }
  };

  // Auto-refresh user data every 30 seconds
  useEffect(() => {
    if (!user) return;
    
    console.log('🔄 Starting auto-refresh for user:', user.email);
    
    const refreshInterval = setInterval(async () => {
      await refreshUserData();
    }, 30000); // 30 seconds
    
    // Listen for manual balance update events
    const handleBalanceUpdate = (event) => {
      if (event.detail) {
        setUser(event.detail);
        console.log('💰 Balance manually updated');
      }
    };
    
    window.addEventListener('user-balance-updated', handleBalanceUpdate);
    
    return () => {
      console.log('🛑 Stopping auto-refresh');
      clearInterval(refreshInterval);
      window.removeEventListener('user-balance-updated', handleBalanceUpdate);
    };
  }, [user]);

  // Check if user needs KYC approval
  const needsKYC = (user) => {
    if (!user || user.is_admin) return false;
    // User needs KYC if they don't have approved KYC status
    return user.kyc_status !== 'approved';
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
      {/* Toast Notification Manager - Shows pretty popups when orders are approved */}
      {user && <NotificationToastManager />}
      
      <BrowserRouter>
        <Routes>
          <Route 
            path="/auth" 
            element={
              user ? (
                user.is_admin ? <Navigate to="/admin" /> : 
                needsKYC(user) ? <Navigate to="/kyc" /> :
                <Navigate to="/dashboard" />
              ) : <AuthPage onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <Dashboard user={user} onUserUpdate={handleUserUpdate} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/kyc" 
            element={
              user && !user.is_admin ? (
                <UserSidebarLayout user={user} onLogout={handleLogout}>
                  <KYCPage user={user} onUserUpdate={handleUserUpdate} onLogout={handleLogout} />
                </UserSidebarLayout>
              ) : <Navigate to="/auth" />
            } 
          />
          <Route 
            path="/market" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <Market user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/wallet" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <Wallet user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/trade" 
            element={
              <ProtectedRoute user={user} requiresKYC={true}>
                <UserSidebarLayout user={user} onLogout={handleLogout}>
                  <Trade user={user} onLogout={handleLogout} />
                </UserSidebarLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/trade/:asset" 
            element={
              <ProtectedRoute user={user} requiresKYC={true}>
                <UserSidebarLayout user={user} onLogout={handleLogout}>
                  <Trade user={user} onLogout={handleLogout} />
                </UserSidebarLayout>
              </ProtectedRoute>
            } 
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
            path="/admin/settings/ai" 
            element={user?.is_admin ? <AdminAISettings user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/ai-center" 
            element={user?.is_admin ? <AdminAICenter user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          
          {/* NEW AI ADMIN ROUTES */}
          <Route 
            path="/admin/ai/intelligence" 
            element={user?.is_admin ? <AIIntelligenceDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/ai/security" 
            element={user?.is_admin ? <AISecurityCenter user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/admin/ai/users" 
            element={user?.is_admin ? <AIUserAnalytics user={user} onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/ai/dashboard" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <UserAIDashboard user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai/assistant" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <UserAIAssistant user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai/recommendations" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <UserAIRecommendations user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/multi-asset" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <MultiAssetTrading user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/staking" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <StakingYieldFarming user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai/portfolio-analysis" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <PortfolioAnalysis user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/kyc-game" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <KYCWaitingGame user={user} onLogout={handleLogout} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/currency-exchange" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <CurrencyExchange user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/support-tickets" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <SupportTickets user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/contact-us" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <ContactUs user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/rewards" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <Rewards user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/portfolio" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <Portfolio user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute user={user} onLogout={handleLogout}>
                <UserProfile user={user} onUserUpdate={handleUserUpdate} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/" 
            element={<LandingPage />} 
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;