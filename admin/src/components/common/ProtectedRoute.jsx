import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * ProtectedRoute — Route Guard scaffolding for KaamSetu Admin Web Panel.
 *
 * Prevents unauthenticated access to /admin/* routes.
 * In Phase 2/local preview, checks localStorage for `admin_auth_token` or defaults
 * to development mode allowance so UI preview flows remain testable.
 * In Phase 3, replace `isAuthenticated` check with real JWT / AuthContext verification.
 */
export default function ProtectedRoute({ children, requireAuth = true }) {
  const location = useLocation();

  // Scaffolding check: looks for auth token in localStorage or allows DEV preview
  const token = localStorage.getItem('admin_auth_token');
  const isDevPreview = import.meta.env.DEV;
  const isAuthenticated = Boolean(token) || isDevPreview;

  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  return children;
}
