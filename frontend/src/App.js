import React, { useEffect, useLayoutEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import AdminPage from './components/AdminPage';
import PurchasePage from './components/PurchasePage';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';
import './themes.css';

// Sync theme with user profile: unisex when not logged in, male/female based on profile.gender.
// useLayoutEffect so theme is applied before paint (avoids orange flash then switch).
function ThemeSync({ children }) {
  const { user, loading } = useAuth();
  useLayoutEffect(() => {
    const theme = (() => {
      if (loading || !user) return 'unisex';
      const gender = user.profile?.gender;
      if (gender === 'male') return 'male';
      if (gender === 'female') return 'female';
      return 'unisex';
    })();
    document.documentElement.setAttribute('data-theme', theme);
  }, [user, loading]);
  return children;
}

// No scroll-to-top on route change (avoids unwanted scroll when e.g. member logs in and goes to dashboard)
function ScrollToTop() {
  return null;
}

function App() {
  // Ensure direction is always LTR on mount
  useEffect(() => {
    document.documentElement.dir = 'ltr';
    document.body.dir = 'ltr';
  }, []);

  return (
    <AuthProvider>
      <ThemeSync>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <ScrollToTop />
          <AppRoutes />
        </Router>
      </ThemeSync>
    </AuthProvider>
  );
}

function AppRoutes() {
  const { user, loading } = useAuth();
  const { i18n } = useTranslation();
  
  // Ensure direction stays LTR when language changes
  useEffect(() => {
    document.documentElement.dir = 'ltr';
    document.body.dir = 'ltr';
  }, [i18n.language]);

  if (loading) {
    return <div className="loading-container">Loading...</div>;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/" replace />} />
      <Route path="/admin" element={user ? <AdminPage /> : <Navigate to="/" replace />} />
      <Route path="/purchase" element={user ? <PurchasePage /> : <Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

