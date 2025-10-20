import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ user, requiresKYC = true, children }) {
  // Not authenticated
  if (!user) {
    return <Navigate to="/auth" />;
  }

  // Admin users can access everything - skip KYC check
  if (user.is_admin) {
    return children;
  }

  // Check if KYC approval is required for regular users
  if (requiresKYC && user.kyc_status !== 'approved') {
    return <Navigate to="/kyc" />;
  }

  // Render the protected component
  return children;
}
