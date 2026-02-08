import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import ProfileTab from './tabs/ProfileTab';
import AssistantDashboard from './tabs/AssistantDashboard';
import MembersListTab from './tabs/MembersListTab';
import InPersonSessionsTab from './tabs/InPersonSessionsTab';
import BreakRequestsTab from './tabs/BreakRequestsTab';
import MembersProgramsTab from './tabs/MembersProgramsTab';
import TrainingInfoTab from './tabs/TrainingInfoTab';
import TrainingPlansProductsTab from './tabs/TrainingPlansProductsTab';
import SiteSettingsTab from './tabs/SiteSettingsTab';
import AISettingsTab from './tabs/AISettingsTab';
import HistoryTab from './tabs/HistoryTab';
import NutritionTab from './tabs/NutritionTab';
import TrainingProgramTab from './tabs/TrainingProgramTab';
import StepsTab from './tabs/StepsTab';
import OnlineLab from './tabs/OnlineLab';
import PsychologyTest from './tabs/PsychologyTest';
import MembersAndAssistantsManagementTab from './tabs/MembersAndAssistantsManagementTab';
import BreakRequestModal from './BreakRequestModal';
import ChatWithTabs from './ChatWithTabs';
import TrainingWithAgent from './TrainingWithAgent';
import DashboardIcon from './DashboardIcon';
import './Dashboard.css';

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState('profile');
  const [userRole, setUserRole] = useState(null);
  const [profileComplete, setProfileComplete] = useState(true);
  const [breakRequestModalOpen, setBreakRequestModalOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [notificationsError, setNotificationsError] = useState(null);
  const [trialStatus, setTrialStatus] = useState(null);

  const getAuthToken = useCallback(() => localStorage.getItem('token') || '', []);
  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
  }, [getAuthToken]);

  const loadNotifications = useCallback(async () => {
    if (!user) return;
    try {
      setNotificationsLoading(true);
      setNotificationsError(null);
      const res = await axios.get(
        `${API_BASE}/api/member/notifications?language=${i18n.language || 'fa'}`,
        getAxiosConfig()
      );
      setNotifications(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Error loading notifications:', err);
      setNotifications([]);
      setNotificationsError(err.response?.data?.error || err.message || 'Failed to load');
    } finally {
      setNotificationsLoading(false);
    }
  }, [API_BASE, i18n.language, user, getAxiosConfig]);

  useEffect(() => {
    if (user && userRole) loadNotifications();
  }, [user, userRole, loadNotifications]);

  useEffect(() => {
    if (!user || userRole !== 'member') return;
    const loadTrialStatus = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/member/trial-status`, getAxiosConfig());
        setTrialStatus(res.data || null);
      } catch (err) {
        setTrialStatus(null);
      }
    };
    loadTrialStatus();
  }, [API_BASE, getAxiosConfig, user, userRole]);

  // Refetch notifications when opening the dropdown so the list is fresh
  useEffect(() => {
    if (notificationsOpen && user) loadNotifications();
  }, [notificationsOpen, user, loadNotifications]);

  const unreadCount = notifications.filter((n) => !n.read_at).length;

  const markNotificationRead = async (id) => {
    try {
      await axios.patch(
        `${API_BASE}/api/member/notifications/${id}/read`,
        {},
        getAxiosConfig()
      );
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
      );
    } catch (err) {
      console.error('Error marking notification read:', err);
    }
  };

  const markAllNotificationsRead = async () => {
    try {
      await axios.patch(
        `${API_BASE}/api/member/notifications/read-all`,
        {},
        getAxiosConfig()
      );
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, read_at: n.read_at || new Date().toISOString() }))
      );
    } catch (err) {
      console.error('Error marking all read:', err);
    }
  };

  const handleNotificationClick = (n) => {
    if (!n.read_at) markNotificationRead(n.id);
    if (n.link) setActiveTab(n.link.replace('?tab=', '').trim() || 'training-program');
    setNotificationsOpen(false);
  };

  // Close dropdown when clicking outside. Use setTimeout so the click that opened it doesn't immediately close it.
  useEffect(() => {
    if (!notificationsOpen) return;
    const onOutside = (e) => {
      if (e.target.closest('.topbar-notifications-wrap')) return;
      setNotificationsOpen(false);
    };
    const t = setTimeout(() => document.addEventListener('click', onOutside), 0);
    return () => {
      clearTimeout(t);
      document.removeEventListener('click', onOutside);
    };
  }, [notificationsOpen]);

  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam) setActiveTab(tabParam);
  }, [searchParams]);

  useEffect(() => {
    // Check user role and profile completion
    const checkRole = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/admin/check-admin`);
        const role = response.data.role || 'member';
        setUserRole(role);
        
        // If assistant, check if profile is complete
        if (role === 'assistant') {
          try {
            const profileResponse = await axios.get(`${API_BASE}/api/admin/check-profile-complete`);
            const isComplete = profileResponse.data.profile_complete;
            setProfileComplete(isComplete);
            
            // If profile not complete, show profile tab
            if (!isComplete) {
              setActiveTab('profile');
            }
          } catch (error) {
            console.error('Error checking profile completion:', error);
          }
        }
      } catch (error) {
        setUserRole('member');
      }
    };
    if (user) {
      checkRole();
    }
  }, [API_BASE, user]);

  const changeLanguage = () => {
    const newLang = i18n.language === 'fa' ? 'en' : 'fa';
    i18n.changeLanguage(newLang);
    document.documentElement.lang = newLang;
    // Keep direction as LTR for consistent alignment
    document.documentElement.dir = 'ltr';
    document.body.dir = 'ltr';
  };

  // Determine tabs based on user role
  const getTabs = () => {
    if (userRole === 'admin') {
      // Admin tabs
      return [
        { id: 'members-assistants-management', label: i18n.language === 'fa' ? 'مدیریت اعضا و دستیاران' : 'Members and Assistants Management', icon: 'people' },
        { id: 'training-info', label: i18n.language === 'fa' ? 'اطلاعات تمرین' : 'Training Info', icon: 'menu_book' },
        { id: 'training-plans-products', label: i18n.language === 'fa' ? 'برنامه‌ها و بسته‌های خرید' : 'Training Plans & Packages', icon: 'assignment' },
        { id: 'ai-settings', label: i18n.language === 'fa' ? 'تنظیمات AI' : 'AI Settings', icon: 'smart_toy' },
        { id: 'site-settings', label: i18n.language === 'fa' ? 'تنظیمات سایت' : 'Site Settings', icon: 'settings' },
        { id: 'members-programs', label: i18n.language === 'fa' ? 'برنامه اعضا' : 'Members Programs', icon: 'assignment' }
      ];
    } else if (userRole === 'assistant') {
      // Assistant sees profile tab if incomplete, otherwise assistant tabs
      if (!profileComplete) {
        return [
          { id: 'profile', label: i18n.language === 'fa' ? 'پروفایل' : 'Profile', icon: 'person' }
        ];
      } else {
        return [
          { id: 'members-list', label: i18n.language === 'fa' ? 'لیست اعضا' : 'Members List', icon: 'people' },
          { id: 'break-requests', label: i18n.language === 'fa' ? 'درخواست استراحت' : 'Break Requests', icon: 'pause' },
          { id: 'in-person-sessions', label: i18n.language === 'fa' ? 'تاریخچه جلسات حضوری' : 'In-Person Sessions', icon: 'event' },
          { id: 'members-programs', label: i18n.language === 'fa' ? 'برنامه اعضا' : 'Members Programs', icon: 'assignment' }
        ];
      }
    } else {
      // Regular members see profile tab, Training with Agent tab, and base tabs
      const baseTabs = [
        { id: 'training-with-agent', label: i18n.language === 'fa' ? 'تمرین با دستیار' : 'Training with Agent', icon: 'smart_toy' },
        { id: 'history', label: t('history'), icon: 'bar_chart' },
        { id: 'steps', label: i18n.language === 'fa' ? 'شمارش قدم' : 'Steps', icon: 'directions_walk' },
        { id: 'nutrition', label: t('nutrition'), icon: 'restaurant' },
        { id: 'training-program', label: i18n.language === 'fa' ? 'برنامه تمرینی' : 'Training Program', icon: 'fitness_center' },
        { id: 'online-lab', label: i18n.language === 'fa' ? 'آزمایشگاه آنلاین' : 'Online Laboratory', icon: 'science' },
        { id: 'psychology-test', label: i18n.language === 'fa' ? 'تست روانشناسی' : 'Psychology Test', icon: 'psychology' }
      ];
      return [
        { id: 'profile', label: i18n.language === 'fa' ? 'پروفایل' : 'Profile', icon: 'person' },
        ...baseTabs
      ];
    }
  };

  const tabs = getTabs();
  
  // Set default active tab based on role
  useEffect(() => {
    if (userRole === 'admin' && activeTab === 'profile') {
      setActiveTab('members-assistants-management');
    } else if (userRole === 'assistant' && activeTab === 'profile' && profileComplete) {
      setActiveTab('members-list');
    } else if (userRole === 'assistant' && activeTab === 'assistant-dashboard') {
      setActiveTab('members-list');
    }
  }, [userRole, profileComplete, activeTab]);

  return (
    <div className="dashboard">
      <nav className="dashboard-topbar">
        <div className="topbar-container">
          {/* Right side - Title */}
          <h1 className="topbar-title" onClick={() => {
            // Navigate to landing page but keep user logged in
            navigate('/');
          }} style={{ cursor: 'pointer' }}>
            {t('appName')}
          </h1>
          
          {/* Left side - Language toggle and Logout */}
          <div className="topbar-actions">
            {(userRole === 'member' || userRole === 'admin' || userRole === 'assistant') && (
              <div className="topbar-notifications-wrap">
                <button
                  type="button"
                  className="topbar-notifications-btn"
                  onClick={(e) => { e.stopPropagation(); setNotificationsOpen((o) => !o); }}
                  title={i18n.language === 'fa' ? 'اعلان‌ها' : 'Notifications'}
                  aria-label="Notifications"
                >
                  <svg className="notification-bell-icon" viewBox="0 0 24 24" fill="currentColor" width="22" height="22">
                    <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
                  </svg>
                  {unreadCount > 0 && (
                    <span className="notification-badge" aria-hidden="true">{unreadCount > 99 ? '99+' : unreadCount}</span>
                  )}
                </button>
                {notificationsOpen && (
                  <div className="topbar-notifications-dropdown">
                    <div className="notifications-dropdown-header">
                      <span>{i18n.language === 'fa' ? 'اعلان‌ها' : 'Notifications'}</span>
                      {unreadCount > 0 && (
                        <button type="button" className="notifications-mark-all" onClick={markAllNotificationsRead}>
                          {i18n.language === 'fa' ? 'همه خوانده شد' : 'Mark all read'}
                        </button>
                      )}
                    </div>
                    <div className="notifications-dropdown-list">
                      {notificationsLoading ? (
                        <div className="notifications-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
                      ) : notificationsError ? (
                        <div className="notifications-error">
                          {i18n.language === 'fa' ? 'خطا در بارگذاری اعلان‌ها' : 'Error loading notifications'}
                          <button type="button" className="notifications-retry" onClick={() => loadNotifications()}>
                            {i18n.language === 'fa' ? 'تلاش مجدد' : 'Retry'}
                          </button>
                        </div>
                      ) : notifications.length === 0 ? (
                        <div className="notifications-empty">{i18n.language === 'fa' ? 'اعلانی نیست' : 'No notifications'}</div>
                      ) : (
                        notifications.map((n) => (
                          <button
                            key={n.id}
                            type="button"
                            className={`notification-item ${!n.read_at ? 'unread' : ''}`}
                            onClick={() => handleNotificationClick(n)}
                          >
                            {n.type && (
                              <span className="notification-type-badge" data-type={n.type}>
                                {n.type === 'trainer_note' ? (i18n.language === 'fa' ? 'یادداشت مربی' : 'Trainer note') :
                                 n.type === 'message' ? (i18n.language === 'fa' ? 'پیام' : 'Message') :
                                 n.type === 'reminder' ? (i18n.language === 'fa' ? 'یادآوری' : 'Reminder') :
                                 n.type}
                              </span>
                            )}
                            <strong>{n.title}</strong>
                            {n.body && <span className="notification-body">{n.body}</span>}
                            {n.voice_url && (
                              <audio controls src={`${API_BASE}${n.voice_url}`} preload="metadata" className="notification-audio" />
                            )}
                            {n.created_at && <span className="notification-time">{new Date(n.created_at).toLocaleString(i18n.language === 'fa' ? 'fa-IR' : 'en-US', { dateStyle: 'short', timeStyle: 'short' })}</span>}
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            {userRole === 'member' && (
              <button
                type="button"
                className="topbar-break-request-btn"
                onClick={() => setBreakRequestModalOpen(true)}
                title={i18n.language === 'fa' ? 'درخواست استراحت' : 'Request a break'}
              >
                {i18n.language === 'fa' ? 'استراحت' : 'Break'}
              </button>
            )}
            <button
              type="button"
              className={`lang-toggle ${i18n.language === 'fa' ? 'fa-active' : 'en-active'}`}
              onClick={changeLanguage}
              title={i18n.language === 'fa' ? 'Switch to English' : 'تبدیل به فارسی'}
            >
              <span className="lang-label-en">EN</span>
              <span className="lang-label-fa">فا</span>
              <span className="lang-toggle-slider"></span>
            </button>
            <span className="username">{user?.username}</span>
            <button type="button" className="topbar-logout-btn" onClick={logout}>
              {t('logout')}
            </button>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        {userRole === 'member' && trialStatus && (
          <div className={`trial-banner ${trialStatus.trial_ended ? 'trial-ended' : 'trial-active'}`}>
            {trialStatus.is_trial_active ? (
              <span>
                {i18n.language === 'fa'
                  ? `دوره آزمایشی رایگان: ${trialStatus.days_left === 0 ? 'امروز آخرین روز' : `${trialStatus.days_left} روز باقی‌مانده`}`
                  : `Free trial: ${trialStatus.days_left === 0 ? 'Last day today' : `${trialStatus.days_left} days left`}`}
              </span>
            ) : trialStatus.trial_ended ? (
              <span>
                {i18n.language === 'fa' ? 'دوره آزمایشی ۷ روزه شما به پایان رسید. برای ادامه از تمام امکانات، اشتراک تهیه کنید.' : 'Your 7-day free trial has ended. Subscribe to continue using all features.'}
              </span>
            ) : null}
          </div>
        )}
        <div className="dashboard-layout">
          {/* 1. Chatbox - full width */}
          <div className="dashboard-chat-row">
            <ChatWithTabs userRole={userRole} />
          </div>

          {/* 2. Tabs - full width */}
          <div className="tabs-container">
            {tabs.map(tab => (
              <button
                key={tab.id}
                type="button"
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setActiveTab(tab.id);
                }}
              >
                <span className="tab-icon"><DashboardIcon name={tab.icon} /></span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* 3. Tab content - full width */}
          <div className="tab-content">
            {activeTab === 'profile' && <ProfileTab />}
            {activeTab === 'training-with-agent' && <TrainingWithAgent />}
            {activeTab === 'members-assistants-management' && <MembersAndAssistantsManagementTab />}
            {activeTab === 'assistant-dashboard' && <AssistantDashboard />}
            {activeTab === 'members-list' && <MembersListTab />}
            {activeTab === 'in-person-sessions' && <InPersonSessionsTab />}
            {activeTab === 'members-programs' && <MembersProgramsTab />}
            {activeTab === 'training-info' && <TrainingInfoTab />}
            {activeTab === 'training-plans-products' && <TrainingPlansProductsTab />}
            {activeTab === 'ai-settings' && <AISettingsTab />}
            {activeTab === 'site-settings' && <SiteSettingsTab />}
            {activeTab === 'history' && <HistoryTab />}
            {activeTab === 'nutrition' && <NutritionTab />}
            {activeTab === 'training-program' && <TrainingProgramTab />}
            {activeTab === 'steps' && <StepsTab />}
            {activeTab === 'break-requests' && <BreakRequestsTab />}
            {activeTab === 'online-lab' && <OnlineLab />}
            {activeTab === 'psychology-test' && <PsychologyTest />}
          </div>
        </div>
      </div>
      <BreakRequestModal
        isOpen={breakRequestModalOpen}
        onClose={() => setBreakRequestModalOpen(false)}
      />
    </div>
  );
};

export default Dashboard;

