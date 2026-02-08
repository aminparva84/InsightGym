import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthModal from './AuthModal';
import TrainingProgramsModal from './TrainingProgramsModal';
import BannerChat from './BannerChat';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import './LandingPage.css';

const LandingPage = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showTrainingProgramsModal, setShowTrainingProgramsModal] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [hasTrainingProgram, setHasTrainingProgram] = useState(false);
  const [checkingProgram, setCheckingProgram] = useState(false);
  const [siteSettings, setSiteSettings] = useState(null);

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

  // Fetch site settings for footer (contact, social)
  useEffect(() => {
    const fetchSiteSettings = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/site-settings`);
        setSiteSettings(response.data || {});
      } catch (error) {
        console.error('Error fetching site settings:', error);
        setSiteSettings({});
      }
    };
    fetchSiteSettings();
  }, []);

  // Check if user has a training program
  useEffect(() => {
    const checkTrainingProgram = async () => {
      if (!user) {
        setHasTrainingProgram(false);
        return;
      }

      setCheckingProgram(true);
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setHasTrainingProgram(false);
          setCheckingProgram(false);
          return;
        }

        const response = await axios.get(`${API_BASE}/api/training-programs`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          setHasTrainingProgram(true);
        } else {
          setHasTrainingProgram(false);
        }
      } catch (error) {
        console.error('Error checking training program:', error);
        setHasTrainingProgram(false);
      } finally {
        setCheckingProgram(false);
      }
    };

    checkTrainingProgram();
  }, [user]);

  useEffect(() => {
    document.documentElement.lang = i18n.language;
    document.documentElement.dir = 'ltr';
  }, [i18n.language]);

  const changeLanguage = () => {
    const newLang = i18n.language === 'fa' ? 'en' : 'fa';
    i18n.changeLanguage(newLang);
    document.documentElement.lang = newLang;
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
              <h1 className="banner-brand">
                {i18n.language === 'fa' ? 'باشگاهی با قدرت هوش مصنوعی' : 'Powered by AI GYM'}
              </h1>
              <h2 className="banner-title">
                {i18n.language === 'fa' ? (
                  <>
                    <span className="banner-title-line">فراتر از تمرین — هوشمندتر تمرین کنید.</span>
                    <span className="banner-title-line">مسیر هوش‌مصنوعی شما به</span>
                    <span className="banner-title-line">تناسب اندام ماندگار و نتایج واقعی.</span>
                  </>
                ) : (
                  <>
                    <span className="banner-title-line">Beyond Exercise — Train Smarter.</span>
                    <span className="banner-title-line">Your AI-Powered Path to</span>
                    <span className="banner-title-line">Lasting Fitness & Real Results.</span>
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
        </section>

        <section className="intro-section">
          <div className="intro-container">
            <div className="intro-card">
              <div className="intro-header">
                <span className="intro-badge">{t('introBadge')}</span>
                <h2 className="intro-title">{t('introHeadline')}</h2>
              </div>
              <p className="intro-text">{t('introParagraph1')}</p>
              <p className="intro-text">{t('introParagraph2')}</p>
              <p className="intro-text">{t('introParagraph3')}</p>

              <h3 className="intro-subtitle">{t('introFeaturesTitle')}</h3>
              <div className="intro-list">
                <div className="intro-item">
                  <span className="intro-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 8h-2V6a4 4 0 0 0-8 0v2H8v8h2v2a4 4 0 0 0 8 0v-2h2V8zm-8-2a2 2 0 0 1 4 0v2h-4V6zm4 12a2 2 0 0 1-4 0v-2h4v2z"/></svg>
                  </span>
                  <div>
                    <h4>{t('introFeature1Title')}</h4>
                    <p>{t('introFeature1Desc')}</p>
                  </div>
                </div>
                <div className="intro-item">
                  <span className="intro-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 2h6a2 2 0 0 1 2 2v2h2a2 2 0 0 1 2 2v8a4 4 0 0 1-4 4h-2v2h-6v-2H7a4 4 0 0 1-4-4V8a2 2 0 0 1 2-2h2V4a2 2 0 0 1 2-2zm0 2v2h6V4H9zm-2 6h10v2H7v-2zm0 4h6v2H7v-2z"/></svg>
                  </span>
                  <div>
                    <h4>{t('introFeature2Title')}</h4>
                    <p>{t('introFeature2Desc')}</p>
                  </div>
                </div>
                <div className="intro-item">
                  <span className="intro-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.46 3 5.74V20a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-5.26A7 7 0 0 0 19 9a7 7 0 0 0-7-7zm2 18h-4v-4h4v4zm.12-6H9.88A5 5 0 1 1 14.12 14z"/></svg>
                  </span>
                  <div>
                    <h4>{t('introFeature3Title')}</h4>
                    <p>{t('introFeature3Desc')}</p>
                  </div>
                </div>
                <div className="intro-item">
                  <span className="intro-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 19h16v2H4v-2zm1-3h2V7H5v9zm4 0h2V4H9v12zm4 0h2V10h-2v6zm4 0h2V6h-2v10z"/></svg>
                  </span>
                  <div>
                    <h4>{t('introFeature4Title')}</h4>
                    <p>{t('introFeature4Desc')}</p>
                  </div>
                </div>
                <div className="intro-item">
                  <span className="intro-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-6l-4 4v-4H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm2 4h12v2H6V8zm0 4h8v2H6v-2z"/></svg>
                  </span>
                  <div>
                    <h4>{t('introFeature5Title')}</h4>
                    <p>{t('introFeature5Desc')}</p>
                  </div>
                </div>
              </div>

              <p className="intro-closing">{t('introClosing')}</p>
            </div>
          </div>
        </section>

        {/* Feature Cards Section - Glass theme matching banner */}
        <section className="features-section">
          <div className="features-container">
            <div className="feature-cards">
              {/* Lose Weight Card */}
              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                </div>
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
                <div className="feature-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6h-6z"/></svg>
                </div>
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
                <div className="feature-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9 3.57 6 6.57 4.57 5 3 6.57 2 8.14 4.57 9.71 7 6.57 10.14 4.57 11.57 6 13l2-2 2.43 2.43 1.43-1.43-2.43-2.43L22 8.14 20.57 6.71 17 10.29 8.43 1.71 12-1.86 10.57-3.29 9-1.71 6-4.71 4.57-6.29 3-4.71 2-3.14 4.57-1.57 7 4.29 10.14 2.57 11.57 4 13l2-2 4.29 4.29 1.43-1.43-4.29-4.29L22 6.29 20.57 4.86 17 8.43 8.43-0.14 12-3.71 10.57-5.14 9-3.57 6-6.57 4.57-8 3-6.57 2-5 4.57-3.43 7 5.43 10.14 3.57 11.57 5 13.43 5.43 15.86 8.29 18.71 12 15.43l2.57 2.57-1.43 1.43-2.57-2.57L17 20.57 20.57 24 22 22.57 18.43 19.43 20.57 14.86z"/></svg>
                </div>
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
                <div className="feature-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                </div>
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
                <div className="feature-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M11 9H9V2H7v7H5V2H3v7c0 2.12 1.66 3.84 3.75 3.97V22h2.5v-9.03C11.34 12.84 13 11.12 13 9V2h-2v7zm5-3v8c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2z"/></svg>
                </div>
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
              onClick={() => {
                if (hasTrainingProgram) {
                  navigate('/dashboard?tab=training-program');
                } else {
                  setShowTrainingProgramsModal(true);
                }
              }}
              disabled={checkingProgram}
            >
              {checkingProgram 
                ? (i18n.language === 'fa' ? 'در حال بررسی...' : 'Checking...')
                : (hasTrainingProgram 
                    ? (i18n.language === 'fa' ? 'مشاهده برنامه تمرینی' : 'See the Training Programme')
                    : t('buyTrainingProgramme')
                  )
              }
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
                {(siteSettings && (i18n.language === 'fa' ? siteSettings.app_description_fa : siteSettings.app_description_en)) ||
                  (i18n.language === 'fa'
                    ? 'پلتفرم جامع تناسب اندام با هوش مصنوعی'
                    : 'Comprehensive fitness platform powered by AI')
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
                  <a href={`mailto:${(siteSettings?.contact_email || 'info@insightgym.com').trim()}`} className="footer-link">
                    {(siteSettings?.contact_email || 'info@insightgym.com').trim() || 'info@insightgym.com'}
                  </a>
                </li>
                <li>
                  <a href={`tel:${(siteSettings?.contact_phone || '+1234567890').replace(/\s/g, '')}`} className="footer-link">
                    {siteSettings?.contact_phone?.trim() || (i18n.language === 'fa' ? '+98 123 456 7890' : '+1 (234) 567-890')}
                  </a>
                </li>
                {siteSettings?.address_fa?.trim() && i18n.language === 'fa' && (
                  <li className="footer-address">{siteSettings.address_fa}</li>
                )}
                {siteSettings?.address_en?.trim() && i18n.language !== 'fa' && (
                  <li className="footer-address">{siteSettings.address_en}</li>
                )}
              </ul>
            </div>

            {(siteSettings?.instagram_url || siteSettings?.telegram_url || siteSettings?.whatsapp_url ||
              siteSettings?.twitter_url || siteSettings?.facebook_url || siteSettings?.linkedin_url || siteSettings?.youtube_url) && (
              <div className="footer-section footer-social-section">
                <h4 className="footer-links-title">
                  {i18n.language === 'fa' ? 'شبکه‌های اجتماعی' : 'Social Media'}
                </h4>
                <ul className="footer-social-links">
                  {siteSettings.instagram_url && (
                    <li>
                      <a href={siteSettings.instagram_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="Instagram" aria-label="Instagram">
                        <span className="footer-social-icon">📷</span> Instagram
                      </a>
                    </li>
                  )}
                  {siteSettings.telegram_url && (
                    <li>
                      <a href={siteSettings.telegram_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="Telegram" aria-label="Telegram">
                        <span className="footer-social-icon">✈️</span> Telegram
                      </a>
                    </li>
                  )}
                  {siteSettings.whatsapp_url && (
                    <li>
                      <a href={siteSettings.whatsapp_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="WhatsApp" aria-label="WhatsApp">
                        <span className="footer-social-icon">💬</span> WhatsApp
                      </a>
                    </li>
                  )}
                  {siteSettings.twitter_url && (
                    <li>
                      <a href={siteSettings.twitter_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="Twitter" aria-label="Twitter">
                        <span className="footer-social-icon">𝕏</span> Twitter
                      </a>
                    </li>
                  )}
                  {siteSettings.facebook_url && (
                    <li>
                      <a href={siteSettings.facebook_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="Facebook" aria-label="Facebook">
                        <span className="footer-social-icon">f</span> Facebook
                      </a>
                    </li>
                  )}
                  {siteSettings.linkedin_url && (
                    <li>
                      <a href={siteSettings.linkedin_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="LinkedIn" aria-label="LinkedIn">
                        <span className="footer-social-icon">in</span> LinkedIn
                      </a>
                    </li>
                  )}
                  {siteSettings.youtube_url && (
                    <li>
                      <a href={siteSettings.youtube_url} target="_blank" rel="noopener noreferrer" className="footer-social-link" title="YouTube" aria-label="YouTube">
                        <span className="footer-social-icon">▶</span> YouTube
                      </a>
                    </li>
                  )}
                </ul>
              </div>
            )}
          </div>

          <div className="footer-bottom">
            <p className="footer-copyright">
              © {new Date().getFullYear()} {t('appName')}. {siteSettings?.copyright_text || t('copyright')}
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
