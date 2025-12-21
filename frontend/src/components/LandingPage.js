import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import RegistrationForm from './RegistrationForm';
import './LandingPage.css';

const LandingPage = () => {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    setLoading(false);
    if (!result.success) {
      setError(result.error);
    }
  };

  const handleRegistrationComplete = () => {
    // Registration successful, user is automatically logged in
    setShowRegistrationForm(false);
  };

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    document.documentElement.lang = lng;
    document.documentElement.dir = lng === 'fa' ? 'rtl' : 'ltr';
  };

  return (
    <div className="landing-page">
      {/* Animated Background */}
      <div className="animated-background">
        <div className="gradient-orb orb-1" style={{
          left: `${mousePosition.x / 20}px`,
          top: `${mousePosition.y / 20}px`
        }}></div>
        <div className="gradient-orb orb-2" style={{
          left: `${mousePosition.x / 15}px`,
          top: `${mousePosition.y / 15}px`
        }}></div>
        <div className="gradient-orb orb-3" style={{
          left: `${mousePosition.x / 25}px`,
          top: `${mousePosition.y / 25}px`
        }}></div>
      </div>

      <nav className="landing-nav">
        <div className="nav-container">
          <h1 className="app-logo">
            <span className="logo-icon">💪</span>
            {t('appName')}
          </h1>
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
          </div>
        </div>
      </nav>

      <div className="landing-content">
        <div className="landing-hero">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="badge-icon">✨</span>
              <span>{i18n.language === 'fa' ? 'پلتفرم هوشمند تناسب اندام' : 'Smart Fitness Platform'}</span>
            </div>
            <h2 className="hero-title">
              <span className="title-line">{t('welcome')}</span>
              <span className="title-accent">{t('appName')}</span>
            </h2>
            <p className="hero-subtitle">
              {i18n.language === 'fa' 
                ? 'همراه هوشمند شما برای تناسب اندام و سلامتی'
                : 'Your smart companion for fitness and health'}
            </p>
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">{i18n.language === 'fa' ? 'پشتیبانی' : 'Support'}</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">AI</div>
                <div className="stat-label">{i18n.language === 'fa' ? 'دستیار هوشمند' : 'AI Assistant'}</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">100%</div>
                <div className="stat-label">{i18n.language === 'fa' ? 'شخصی‌سازی' : 'Personalized'}</div>
              </div>
            </div>
          </div>
          
          {/* Hero Image Gallery with Animation */}
          <div className="hero-images">
            <div className="image-wrapper">
              <img src="/pics/2.jpeg" alt="Fitness" className="hero-image" />
              <div className="image-overlay"></div>
            </div>
            <div className="image-wrapper">
              <img src="/pics/3.jpeg" alt="Fitness" className="hero-image" />
              <div className="image-overlay"></div>
            </div>
            <div className="image-wrapper">
              <img src="/pics/4.jpeg" alt="Fitness" className="hero-image" />
              <div className="image-overlay"></div>
            </div>
            <div className="image-wrapper">
              <img src="/pics/WhatsApp Image 2025-12-21 at 12.39.08 AM.jpeg" alt="Fitness" className="hero-image" />
              <div className="image-overlay"></div>
            </div>
          </div>
        </div>

        <div className="features-section">
          <h3 className="section-title">
            {i18n.language === 'fa' ? 'ویژگی‌های منحصر به فرد' : 'Unique Features'}
          </h3>
          <div className="fitness-items">
            <div className="fitness-card" data-aos="fade-up" data-aos-delay="0">
              <div className="card-icon">🏋️</div>
              <div className="card-image-wrapper">
                <img src="/pics/2.jpeg" alt="Personal Training" className="fitness-card-image" />
                <div className="card-gradient"></div>
              </div>
              <div className="card-content">
                <h3>{i18n.language === 'fa' ? 'تمرینات شخصی' : 'Personal Training'}</h3>
                <p>{i18n.language === 'fa' 
                  ? 'برنامه‌های تمرینی متناسب با اهداف شما'
                  : 'Customized workout plans for your goals'}</p>
                <div className="card-arrow">→</div>
              </div>
            </div>
            <div className="fitness-card" data-aos="fade-up" data-aos-delay="100">
              <div className="card-icon">🥗</div>
              <div className="card-image-wrapper">
                <img src="/pics/3.jpeg" alt="Nutrition Plans" className="fitness-card-image" />
                <div className="card-gradient"></div>
              </div>
              <div className="card-content">
                <h3>{i18n.language === 'fa' ? 'برنامه تغذیه' : 'Nutrition Plans'}</h3>
                <p>{i18n.language === 'fa' 
                  ? 'برنامه‌های غذایی ۲ و ۴ هفته‌ای'
                  : '2 and 4 week meal plans'}</p>
                <div className="card-arrow">→</div>
              </div>
            </div>
            <div className="fitness-card" data-aos="fade-up" data-aos-delay="200">
              <div className="card-icon">🤖</div>
              <div className="card-image-wrapper">
                <img src="/pics/4.jpeg" alt="AI Assistant" className="fitness-card-image" />
                <div className="card-gradient"></div>
              </div>
              <div className="card-content">
                <h3>{i18n.language === 'fa' ? 'دستیار هوشمند' : 'AI Assistant'}</h3>
                <p>{i18n.language === 'fa' 
                  ? 'راهنمایی و پشتیبانی ۲۴/۷'
                  : '24/7 guidance and support'}</p>
                <div className="card-arrow">→</div>
              </div>
            </div>
            <div className="fitness-card" data-aos="fade-up" data-aos-delay="300">
              <div className="card-icon">📊</div>
              <div className="card-image-wrapper">
                <img src="/pics/WhatsApp Image 2025-12-21 at 12.39.08 AM.jpeg" alt="Progress Tracking" className="fitness-card-image" />
                <div className="card-gradient"></div>
              </div>
              <div className="card-content">
                <h3>{i18n.language === 'fa' ? 'پیگیری پیشرفت' : 'Progress Tracking'}</h3>
                <p>{i18n.language === 'fa' 
                  ? 'ثبت و بررسی تاریخچه تمرینات'
                  : 'Track and review your exercise history'}</p>
                <div className="card-arrow">→</div>
              </div>
            </div>
          </div>
        </div>

        {showRegistrationForm ? (
          <RegistrationForm onComplete={handleRegistrationComplete} />
        ) : (
          <div className="auth-container">
            <div className="auth-tabs">
              <button
                className={`auth-tab ${isLogin ? 'active' : ''}`}
                onClick={() => setIsLogin(true)}
              >
                {t('login')}
              </button>
              <button
                className={`auth-tab ${!isLogin ? 'active' : ''}`}
                onClick={() => {
                  setIsLogin(false);
                  setShowRegistrationForm(true);
                }}
              >
                {t('register')}
              </button>
            </div>

            <form className="auth-form" onSubmit={handleLoginSubmit}>
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-group">
                <label>{t('username')}</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>{t('password')}</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? t('loading') : t('login')}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default LandingPage;
