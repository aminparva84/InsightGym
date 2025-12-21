import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import ProfileTab from './tabs/ProfileTab';
import HistoryTab from './tabs/HistoryTab';
import NutritionTab from './tabs/NutritionTab';
import TipsTab from './tabs/TipsTab';
import InjuriesTab from './tabs/InjuriesTab';
import FloatingChatButton from './FloatingChatButton';
import './Dashboard.css';

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    document.documentElement.lang = lng;
    document.documentElement.dir = lng === 'fa' ? 'rtl' : 'ltr';
  };

  const tabs = [
    { id: 'profile', label: i18n.language === 'fa' ? 'پروفایل' : 'Profile', icon: '👤' },
    { id: 'history', label: t('history'), icon: '📊' },
    { id: 'nutrition', label: t('nutrition'), icon: '🥗' },
    { id: 'tips', label: t('tips'), icon: '💡' },
    { id: 'injuries', label: t('injuries'), icon: '🏥' }
  ];

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-container">
          <h1 className="app-logo">{t('appName')}</h1>
          <div className="nav-actions">
            <button
              className={`lang-btn ${i18n.language === 'fa' ? 'active' : ''}`}
              onClick={() => changeLanguage('fa')}
            >
              {t('farsi')}
            </button>
            <button
              className={`lang-btn ${i18n.language === 'en' ? 'active' : ''}`}
              onClick={() => changeLanguage('en')}
            >
              {t('english')}
            </button>
            <span className="username">{user?.username}</span>
            <button className="logout-btn" onClick={logout}>
              {t('logout')}
            </button>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="tabs-container">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
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
          {activeTab === 'tips' && <TipsTab />}
          {activeTab === 'injuries' && <InjuriesTab />}
        </div>
      </div>

      <FloatingChatButton />
    </div>
  );
};

export default Dashboard;

