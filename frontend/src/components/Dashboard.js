import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ProfileTab from './tabs/ProfileTab';
import HistoryTab from './tabs/HistoryTab';
import NutritionTab from './tabs/NutritionTab';
import TrainingProgramTab from './tabs/TrainingProgramTab';
import ChatBox from './ChatBox';
import TrainingWithAgent from './TrainingWithAgent';
import './Dashboard.css';

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('profile');

  const changeLanguage = () => {
    const newLang = i18n.language === 'fa' ? 'en' : 'fa';
    i18n.changeLanguage(newLang);
    document.documentElement.lang = newLang;
    // Don't change direction for topbar, only for content
  };

  const tabs = [
    { id: 'profile', label: i18n.language === 'fa' ? 'پروفایل' : 'Profile', icon: '👤' },
    { id: 'history', label: t('history'), icon: '📊' },
    { id: 'nutrition', label: t('nutrition'), icon: '🥗' },
    { id: 'training-program', label: i18n.language === 'fa' ? 'برنامه تمرینی' : 'Training Program', icon: '💪' }
  ];

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
              {activeTab === 'history' && <HistoryTab />}
              {activeTab === 'nutrition' && <NutritionTab />}
              {activeTab === 'training-program' && <TrainingProgramTab />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

