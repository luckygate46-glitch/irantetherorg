import { Navigate } from 'react-router-dom';
import UserSidebarLayout from '../layouts/UserSidebarLayout';

export default function ProtectedRoute({ user, onLogout, requiresKYC = true, children }) {
  // Not authenticated
  if (!user) {
    return <Navigate to="/auth" />;
  }

  // Admin users go to admin panel
  if (user.is_admin) {
    return <Navigate to="/admin" />;
  }

  // Check if KYC approval is required
  if (requiresKYC && user.kyc_status !== 'approved') {
    return <Navigate to="/kyc" />;
  }

  // Render the protected component with sidebar
  return (
    <UserSidebarLayout user={user} onLogout={onLogout}>
      {children}
    </UserSidebarLayout>
  );
}
