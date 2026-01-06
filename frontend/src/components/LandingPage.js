import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthModal from './AuthModal';
import BannerChat from './BannerChat';
import './LandingPage.css';

const LandingPage = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const changeLanguage = () => {
    const newLang = i18n.language === 'fa' ? 'en' : 'fa';
    i18n.changeLanguage(newLang);
    document.documentElement.lang = newLang;
    // Don't change direction for topbar - keep it LTR
    // Only change direction for content areas if needed
  };

  const handleLoginClick = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      setShowAuthModal(true);
    }
  };

  return (
    <div className="landing-page">
      {/* Fixed Topbar */}
      <nav className={`landing-topbar ${isScrolled ? 'scrolled' : ''}`}>
        <div className="topbar-container">
          {/* Right side - Title */}
          <h1 className="topbar-title" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            {t('appName')}
          </h1>
          
          {/* Left side - Language toggle and Login/Dashboard */}
          <div className="topbar-actions">
            <button
              className={`lang-toggle ${i18n.language === 'fa' ? 'fa-active' : 'en-active'}`}
              onClick={changeLanguage}
              title={i18n.language === 'fa' ? 'Switch to English' : 'تبدیل به فارسی'}
            >
              <span className="lang-label-en">EN</span>
              <span className="lang-label-fa">فا</span>
              <span className="lang-toggle-slider"></span>
            </button>
            <button
              className="topbar-login-btn"
              onClick={handleLoginClick}
            >
              {user 
                ? (i18n.language === 'fa' ? 'داشبورد' : 'Dashboard')
                : (i18n.language === 'fa' ? 'ورود' : 'Login')
              }
            </button>
          </div>
        </div>
      </nav>

      <div className="landing-content">
        {/* Banner Section */}
        <div className="landing-banner">
          <div className="banner-content">
            <div className="banner-content-wrapper">
              <div className="banner-details">
                <h2 className="banner-title">
                  {i18n.language === 'fa' ? (
                    <>
                      <span className="banner-title-line">فراتر از تمرین؛</span>
                      <span className="banner-title-line">مسیری علمی به</span>
                      <span className="banner-title-line">تناسب اندام ماندگار</span>
                    </>
                  ) : (
                    <>
                      <span className="banner-title-line">Beyond Exercise;</span>
                      <span className="banner-title-line">A Scientific Path to</span>
                      <span className="banner-title-line">Lasting Fitness</span>
                    </>
                  )}
                </h2>
              </div>
              
              {/* Chatbox - Only for registered users */}
              {user ? (
                <div className="banner-chatbox">
                  <BannerChat />
                </div>
              ) : (
                <div className="banner-chatbox-placeholder">
                  <p className="chatbox-placeholder-text">
                    {i18n.language === 'fa'
                      ? 'سلام! چطور می‌تونم کمکتون کنم؟ برای استفاده از چت با هوش مصنوعی، لطفاً وارد شوید'
                      : 'Hello! How can I help you? Please log in to use AI chat'
                    }
                  </p>
                </div>
              )}
            </div>
          </div>
          
          <div className="banner-image-container">
            <img 
              src="/banner-image.png" 
              alt="Fitness" 
              className="banner-image"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/500x400/26CCC2/FFFFFF?text=Fitness';
              }}
            />
          </div>
        </div>

        {/* Feature Cards Section */}
        <div className="features-section">
          <div className="feature-cards">
            {/* Lose Weight Card */}
            <div className="feature-card">
              <div className="feature-icon">⚖️</div>
              <h3 className="feature-title">
                {i18n.language === 'fa' ? 'کاهش وزن' : 'Lose Weight'}
              </h3>
              <p className="feature-description">
                {i18n.language === 'fa'
                  ? 'برنامه‌های تمرینی و تغذیه‌ای تخصصی برای کاهش وزن سالم و پایدار'
                  : 'Specialized workout and nutrition plans for healthy and sustainable weight loss'
                }
              </p>
            </div>

            {/* Gain Weight Card */}
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3 className="feature-title">
                {i18n.language === 'fa' ? 'افزایش وزن' : 'Gain Weight'}
              </h3>
              <p className="feature-description">
                {i18n.language === 'fa'
                  ? 'راهنمایی‌های تخصصی برای افزایش وزن سالم و عضله‌سازی'
                  : 'Expert guidance for healthy weight gain and muscle building'
                }
              </p>
            </div>

            {/* Gain Muscle Card */}
            <div className="feature-card">
              <div className="feature-icon">💪</div>
              <h3 className="feature-title">
                {i18n.language === 'fa' ? 'افزایش عضله' : 'Gain Muscle'}
              </h3>
              <p className="feature-description">
                {i18n.language === 'fa'
                  ? 'برنامه‌های تمرینی قدرتی برای ساخت عضلات و افزایش قدرت'
                  : 'Strength training programs for muscle building and power increase'
                }
              </p>
            </div>

            {/* Shape Fitting Card */}
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3 className="feature-title">
                {i18n.language === 'fa' ? 'تناسب اندام' : 'Shape Fitting'}
              </h3>
              <p className="feature-description">
                {i18n.language === 'fa'
                  ? 'برنامه‌های جامع برای رسیدن به تناسب اندام و فرم ایده‌آل'
                  : 'Comprehensive programs to achieve fitness and ideal body shape'
                }
              </p>
            </div>

            {/* Healthy Diet Card */}
            <div className="feature-card">
              <div className="feature-icon">🥗</div>
              <h3 className="feature-title">
                {i18n.language === 'fa' ? 'رژیم غذایی سالم' : 'Healthy Diet'}
              </h3>
              <p className="feature-description">
                {i18n.language === 'fa'
                  ? 'برنامه‌های غذایی متعادل و سالم برای تغذیه مناسب'
                  : 'Balanced and healthy meal plans for proper nutrition'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Let's Start Button */}
        <div className="lets-start-section">
          <button 
            className="lets-start-btn"
            onClick={() => setShowAuthModal(true)}
          >
            {i18n.language === 'fa' ? 'شروع کنیم' : "Let's Start"}
          </button>
        </div>
      </div>

      {/* Auth Modal */}
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
    </div>
  );
};

export default LandingPage;
