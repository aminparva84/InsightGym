import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import ProfileTab from './tabs/ProfileTab';
import AssistantDashboard from './tabs/AssistantDashboard';
import MembersListTab from './tabs/MembersListTab';
import InPersonSessionsTab from './tabs/InPersonSessionsTab';
import BreakRequestsTab from './tabs/BreakRequestsTab';
import MembersProgramsTab from './tabs/MembersProgramsTab';
import TrainingLevelsInfoTab from './tabs/TrainingLevelsInfoTab';
import ExerciseLibraryTab from './tabs/ExerciseLibraryTab';
import SiteSettingsTab from './tabs/SiteSettingsTab';
import HistoryTab from './tabs/HistoryTab';
import NutritionTab from './tabs/NutritionTab';
import TrainingProgramTab from './tabs/TrainingProgramTab';
import StepsTab from './tabs/StepsTab';
import OnlineLab from './tabs/OnlineLab';
import PsychologyTest from './tabs/PsychologyTest';
import MembersAndAssistantsManagementTab from './tabs/MembersAndAssistantsManagementTab';
import BreakRequestModal from './BreakRequestModal';
import ChatBox from './ChatBox';
import TrainingWithAgent from './TrainingWithAgent';
import './Dashboard.css';

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState('profile');
  const [userRole, setUserRole] = useState(null);
  const [profileComplete, setProfileComplete] = useState(true);
  const [breakRequestModalOpen, setBreakRequestModalOpen] = useState(false);
  
  useEffect(() => {
    // Check for tab query parameter
    const tabParam = searchParams.get('tab');
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  useEffect(() => {
    // Check user role and profile completion
    const checkRole = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/admin/check-admin');
        const role = response.data.role || 'member';
        setUserRole(role);
        
        // If assistant, check if profile is complete
        if (role === 'assistant') {
          try {
            const profileResponse = await axios.get('http://localhost:5000/api/admin/check-profile-complete');
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
  }, [user]);

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
        { id: 'members-assistants-management', label: i18n.language === 'fa' ? 'مدیریت اعضا و دستیاران' : 'Members and Assistants Management', icon: '👥' },
        { id: 'training-levels', label: i18n.language === 'fa' ? 'اطلاعات سطح‌های تمرینی' : 'Training Levels Info', icon: '📊' },
        { id: 'exercise-library', label: i18n.language === 'fa' ? 'کتابخانه تمرینات' : 'Exercise Library', icon: '📚' },
        { id: 'site-settings', label: i18n.language === 'fa' ? 'تنظیمات سایت' : 'Site Settings', icon: '⚙️' },
        { id: 'members-programs', label: i18n.language === 'fa' ? 'برنامه اعضا' : 'Members Programs', icon: '📋' }
      ];
    } else if (userRole === 'assistant') {
      // Assistant sees profile tab if incomplete, otherwise assistant tabs
      if (!profileComplete) {
        return [
          { id: 'profile', label: i18n.language === 'fa' ? 'پروفایل' : 'Profile', icon: '👤' }
        ];
      } else {
        return [
          { id: 'members-list', label: i18n.language === 'fa' ? 'لیست اعضا' : 'Members List', icon: '👥' },
          { id: 'break-requests', label: i18n.language === 'fa' ? 'درخواست استراحت' : 'Break Requests', icon: '⏸️' },
          { id: 'in-person-sessions', label: i18n.language === 'fa' ? 'تاریخچه جلسات حضوری' : 'In-Person Sessions', icon: '📅' },
          { id: 'members-programs', label: i18n.language === 'fa' ? 'برنامه اعضا' : 'Members Programs', icon: '📋' },
          { id: 'message-history', label: i18n.language === 'fa' ? 'تاریخچه پیام‌ها' : 'Message History', icon: '💬' }
        ];
      }
    } else {
      // Regular members see profile tab and base tabs
      const baseTabs = [
        { id: 'history', label: t('history'), icon: '📊' },
        { id: 'steps', label: i18n.language === 'fa' ? 'شمارش قدم' : 'Steps', icon: '👟' },
        { id: 'nutrition', label: t('nutrition'), icon: '🥗' },
        { id: 'training-program', label: i18n.language === 'fa' ? 'برنامه تمرینی' : 'Training Program', icon: '💪' },
        { id: 'online-lab', label: i18n.language === 'fa' ? 'آزمایشگاه آنلاین' : 'Online Laboratory', icon: '🔬' },
        { id: 'psychology-test', label: i18n.language === 'fa' ? 'تست روانشناسی' : 'Psychology Test', icon: '🧠' }
      ];
      return [
        { id: 'profile', label: i18n.language === 'fa' ? 'پروفایل' : 'Profile', icon: '👤' },
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
  }, [userRole, profileComplete]);

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
        <div className="dashboard-layout">
          {/* Left Side - Chat and Training with Agent */}
          <div className="dashboard-left">
            <ChatBox />
            <TrainingWithAgent />
          </div>

          {/* Right Side - Tabs */}
          <div className="dashboard-right">
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
                  <span className="tab-icon">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="tab-content">
              {activeTab === 'profile' && <ProfileTab />}
              {activeTab === 'members-assistants-management' && <MembersAndAssistantsManagementTab />}
              {activeTab === 'assistant-dashboard' && <AssistantDashboard />}
              {activeTab === 'members-list' && <MembersListTab />}
              {activeTab === 'in-person-sessions' && <InPersonSessionsTab />}
              {activeTab === 'members-programs' && <MembersProgramsTab />}
              {activeTab === 'training-levels' && <TrainingLevelsInfoTab />}
              {activeTab === 'exercise-library' && <ExerciseLibraryTab />}
              {activeTab === 'site-settings' && <SiteSettingsTab />}
              {activeTab === 'message-history' && <HistoryTab showOnlyMessages={true} />}
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
      </div>
      <BreakRequestModal
        isOpen={breakRequestModalOpen}
        onClose={() => setBreakRequestModalOpen(false)}
      />
    </div>
  );
};

export default Dashboard;

