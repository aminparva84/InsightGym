import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import AdminPage from './components/AdminPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

// Component to scroll to top on route change (only resets, doesn't block user scroll)
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    // Reset scroll position on route change (not blocking user scroll)
    const resetScroll = () => {
      window.scrollTo(0, 0);
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    };
    
    // Reset scroll a few times to catch delayed scrolls
    resetScroll();
    const timeout1 = setTimeout(resetScroll, 0);
    const timeout2 = setTimeout(resetScroll, 10);
    const timeout3 = setTimeout(resetScroll, 50);
    
    // Use requestAnimationFrame
    requestAnimationFrame(() => {
      resetScroll();
    });
    
    return () => {
      clearTimeout(timeout1);
      clearTimeout(timeout2);
      clearTimeout(timeout3);
    };
  }, [pathname]);

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
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <ScrollToTop />
        <AppRoutes />
      </Router>
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
    </Routes>
  );
}

export default App;

