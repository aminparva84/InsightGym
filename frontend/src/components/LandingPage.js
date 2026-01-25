import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthModal from './AuthModal';
import TrainingProgramsModal from './TrainingProgramsModal';
import BannerChat from './BannerChat';
import './LandingPage.css';

const LandingPage = () => {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showTrainingProgramsModal, setShowTrainingProgramsModal] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Function to aggressively prevent scroll
  const preventScroll = () => {
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  };

  useEffect(() => {
    // Only reset scroll position on mount (not blocking user scroll)
    preventScroll();
    
    // Reset scroll after a few delays to catch any automatic scrolls on mount
    const timeouts = [
      setTimeout(preventScroll, 0),
      setTimeout(preventScroll, 10),
      setTimeout(preventScroll, 50),
      setTimeout(preventScroll, 100)
    ];
    
    // Use requestAnimationFrame to ensure it happens after render
    requestAnimationFrame(() => {
      preventScroll();
      requestAnimationFrame(preventScroll);
    });
    
    // Track scroll for header styling (don't prevent user scrolling)
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
  }, []);

  // Reset scroll when user state changes (e.g., after login) - only reset, don't block
  useEffect(() => {
    // Only reset scroll once when user state changes, not continuously
    const timeout = setTimeout(() => {
      preventScroll();
    }, 0);
    
    return () => {
      clearTimeout(timeout);
    };
  }, [user]);

  const changeLanguage = () => {
    const newLang = i18n.language === 'fa' ? 'en' : 'fa';
    i18n.changeLanguage(newLang);
    document.documentElement.lang = newLang;
    // Keep direction as LTR for consistent alignment
    document.documentElement.dir = 'ltr';
  };

  const handleLoginClick = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      setShowAuthModal(true);
    }
  };

  const handleProfileClick = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      setShowAuthModal(true);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="landing-page">
      {/* Fixed Header with Glass Effect */}
      <header className={`landing-header ${isScrolled ? 'scrolled' : ''}`}>
        <div className="header-container">
          {/* Website Title */}
          <h1 className="header-title" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            {t('appName')}
          </h1>
          
          {/* Right side - Actions */}
          <div className="header-actions">
            {/* Language Toggle */}
            <button
              className={`lang-toggle ${i18n.language === 'fa' ? 'fa-active' : 'en-active'}`}
              onClick={changeLanguage}
              title={i18n.language === 'fa' ? 'Switch to English' : 'تبدیل به فارسی'}
            >
              <span className="lang-label-en">EN</span>
              <span className="lang-label-fa">فا</span>
              <span className="lang-toggle-slider"></span>
            </button>

            {/* My Profile Button */}
            {user && (
              <button
                className="header-profile-btn"
                onClick={handleProfileClick}
              >
                {t('myProfile')}
              </button>
            )}

            {/* Login/Logout Button */}
            {user ? (
              <button
                className="header-logout-btn"
                onClick={handleLogout}
              >
                {t('logout')}
              </button>
            ) : (
              <button
                className="header-login-btn"
                onClick={handleLoginClick}
              >
                {t('login')}
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="landing-content">
        {/* Banner Section - Purple-Pink Background */}
        <section className="landing-banner">
          {/* Left Side - Text and Chatbox */}
          <div className="banner-left">
            <div className="banner-text-container">
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
            
            {/* Chatbox */}
            <div className="banner-chatbox-wrapper">
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
          
          {/* Right Side - Gym Image */}
          <div className="banner-right">
            <div className="banner-image-container">
              <img 
                src="/banner-image.png" 
                alt="Fitness" 
                className="banner-image"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&h=1000&fit=crop';
                }}
              />
            </div>
          </div>
        </section>

        {/* Feature Cards Section */}
        <section className="features-section">
          <div className="features-container">
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
        </section>

        {/* Let's Start / Buy Training Programme Button */}
        <section className="lets-start-section">
          {user ? (
            <button 
              className="lets-start-btn"
              onClick={() => setShowTrainingProgramsModal(true)}
            >
              {t('buyTrainingProgramme')}
            </button>
          ) : (
            <button 
              className="lets-start-btn"
              onClick={() => setShowAuthModal(true)}
            >
              {t('letsStart')}
            </button>
          )}
        </section>
      </div>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-section">
              <h4 className="footer-title">{t('appName')}</h4>
              <p className="footer-description">
                {i18n.language === 'fa'
                  ? 'پلتفرم جامع تناسب اندام با هوش مصنوعی'
                  : 'Comprehensive fitness platform powered by AI'
                }
              </p>
            </div>

            <div className="footer-section">
              <h4 className="footer-links-title">
                {i18n.language === 'fa' ? 'لینک‌های مفید' : 'Quick Links'}
              </h4>
              <ul className="footer-links">
                <li>
                  <a href="#about" className="footer-link">{t('about')}</a>
                </li>
                <li>
                  <a href="#contact" className="footer-link">{t('contactUs')}</a>
                </li>
                <li>
                  <a href="#privacy" className="footer-link">{t('privacy')}</a>
                </li>
                <li>
                  <a href="#terms" className="footer-link">{t('terms')}</a>
                </li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-links-title">
                {i18n.language === 'fa' ? 'تماس با ما' : 'Contact'}
              </h4>
              <ul className="footer-links">
                <li>
                  <a href="mailto:info@insightgym.com" className="footer-link">
                    info@insightgym.com
                  </a>
                </li>
                <li>
                  <a href="tel:+1234567890" className="footer-link">
                    {i18n.language === 'fa' ? '+98 123 456 7890' : '+1 (234) 567-890'}
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            <p className="footer-copyright">
              © {new Date().getFullYear()} {t('appName')}. {t('copyright')}
            </p>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />

      {/* Training Programs Modal */}
      <TrainingProgramsModal 
        isOpen={showTrainingProgramsModal} 
        onClose={() => setShowTrainingProgramsModal(false)} 
      />
    </div>
  );
};

export default LandingPage;
