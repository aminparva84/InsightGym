import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { LayoutContext } from '../context/LayoutContext';
import BannerChat from './BannerChat';
import AuthModal from './AuthModal';
import TrainingProgramsModal from './TrainingProgramsModal';
import './AppLayout.css';

function HeaderMenuItem({ children, selected, onClick, as: Component = 'a', ...props }) {
  const ref = useRef(null);
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  const [hovering, setHovering] = useState(false);

  const handleMouseMove = useCallback((e) => {
    const rect = ref.current?.getBoundingClientRect();
    if (rect) {
      setMouse({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      setHovering(true);
    }
  }, []);

  const handleMouseLeave = useCallback(() => setHovering(false), []);

  return (
    <Component
      ref={ref}
      className={`app-layout-header-menu-item ${selected ? 'app-layout-header-menu-item--selected' : ''}`}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {hovering && (
        <span
          className="app-layout-header-menu-item-hover"
          style={{
            left: mouse.x,
            top: mouse.y,
          }}
          aria-hidden="true"
        />
      )}
      <span className="app-layout-header-menu-item-text">{children}</span>
    </Component>
  );
}

const AppLayout = () => {
  const { i18n, t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [chatModalOpen, setChatModalOpen] = useState(false);
  const [chatModalClosing, setChatModalClosing] = useState(false);
  const [chatMenuOpen, setChatMenuOpen] = useState(false);
  const [headerMenuOpen, setHeaderMenuOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [trainingProgramsModalOpen, setTrainingProgramsModalOpen] = useState(false);
  const closeTimeoutRef = useRef(null);
  const bannerChatRef = useRef(null);

  const handleCloseChat = () => {
    setChatModalClosing(true);
    closeTimeoutRef.current = setTimeout(() => {
      setChatModalOpen(false);
      setChatModalClosing(false);
    }, 250);
  };

  useEffect(() => () => {
    if (closeTimeoutRef.current) clearTimeout(closeTimeoutRef.current);
  }, []);

  const handleChatMenuAction = useCallback((action) => {
    if (bannerChatRef.current) {
      if (action === 'history') bannerChatRef.current.openHistory();
      if (action === 'new') bannerChatRef.current.startNewConversation();
    }
    setChatMenuOpen(false);
  }, []);

  const openAuthIfNeeded = useCallback(
    (e) => {
      if (!user) {
        e?.preventDefault?.();
        setAuthModalOpen(true);
      }
    },
    [user]
  );

  const isSelected = useCallback(
    (path, search) => {
      if (!path) return false;
      if (location.pathname !== path) return false;
      if (!search) return true;
      const params = new URLSearchParams(location.search);
      for (const [k, v] of Object.entries(search)) {
        if (params.get(k) !== String(v)) return false;
      }
      return true;
    },
    [location]
  );

  const layoutContextValue = {
    openAuthModal: () => setAuthModalOpen(true),
    openTrainingProgramsModal: () => setTrainingProgramsModalOpen(true),
    openChatModal: () => setChatModalOpen(true),
    headerMenuOpen,
    setHeaderMenuOpen,
  };

  return (
    <LayoutContext.Provider value={layoutContextValue}>
      {/* Header - glass effect, same as landing page */}
      <header className="app-layout-header">
        <div className="app-layout-header-container">
          <button
            type="button"
            className={`app-layout-lang-toggle ${(i18n.language || '').startsWith('fa') ? 'lang-fa' : 'lang-en'}`}
            onClick={() => {
              const next = (i18n.language || '').startsWith('fa') ? 'en' : 'fa';
              i18n.changeLanguage(next);
              document.documentElement.lang = next;
            }}
            aria-label={(i18n.language || '').startsWith('fa') ? 'Switch to English' : 'تغییر به فارسی'}
          >
            <span className="app-layout-lang-toggle-label app-layout-lang-toggle-label--left">ENG</span>
            <span className="app-layout-lang-toggle-label app-layout-lang-toggle-label--right">فا</span>
            <span className="app-layout-lang-toggle-thumb">
              {(i18n.language || '').startsWith('fa') ? 'فا' : 'ENG'}
            </span>
          </button>

          <div className="app-layout-header-right">
            <button
              type="button"
              className="app-layout-bell-btn"
              onClick={() => (user ? navigate('/dashboard') : setAuthModalOpen(true))}
              aria-label={t('notifications')}
              title={t('notifications')}
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="22" height="22" aria-hidden="true">
                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
              </svg>
            </button>
            {user ? (
              <button
                type="button"
                className="app-layout-dashboard-btn"
                onClick={() => navigate('/dashboard')}
              >
                {t('dashboard')}
              </button>
            ) : (
              <button
                type="button"
                className="app-layout-login-btn"
                onClick={() => setAuthModalOpen(true)}
              >
                {t('login')}
              </button>
            )}
            {user && (
              <button
                type="button"
                className="app-layout-logout-btn"
                onClick={() => { logout(); navigate('/'); }}
              >
                {t('logout')}
              </button>
            )}
            <button
              className="app-layout-hamburger-btn"
              onClick={() => setHeaderMenuOpen((o) => !o)}
              aria-label={t('menu')}
              aria-expanded={headerMenuOpen}
            >
              <svg className="app-layout-hamburger-icon" viewBox="0 0 24 24" fill="currentColor" width="28" height="28" aria-hidden="true">
                <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className={`app-layout-main ${headerMenuOpen ? 'app-layout-main--menu-open' : ''}`}>
        <Outlet />
      </main>

      {/* Header menu - slides from right, pushes content */}
      {headerMenuOpen && (
        <>
          <div
            className="app-layout-header-menu-backdrop"
            onClick={() => setHeaderMenuOpen(false)}
            aria-hidden="true"
          />
          <nav
            className="app-layout-header-menu"
            role="navigation"
            aria-label={t('menu')}
          >
            <div className="app-layout-header-menu-inner">
              <HeaderMenuItem
                as={user ? 'a' : 'button'}
                href={user ? '/dashboard?tab=training-program' : undefined}
                selected={isSelected('/dashboard', { tab: 'training-program' })}
                onClick={(e) => {
                  if (!user) openAuthIfNeeded(e);
                  else setHeaderMenuOpen(false);
                }}
              >
                {t('trainingPlan')}
              </HeaderMenuItem>
              <HeaderMenuItem
                as={user ? 'a' : 'button'}
                href={user ? '/dashboard?tab=history&view=progress' : undefined}
                selected={isSelected('/dashboard', { tab: 'history', view: 'progress' })}
                onClick={(e) => {
                  if (!user) openAuthIfNeeded(e);
                  else setHeaderMenuOpen(false);
                }}
              >
                {t('progressTrend')}
              </HeaderMenuItem>
              <HeaderMenuItem
                as={user ? 'a' : 'button'}
                href={user ? '/dashboard?tab=profile' : undefined}
                selected={isSelected('/dashboard', { tab: 'profile' })}
                onClick={(e) => {
                  if (!user) openAuthIfNeeded(e);
                  else setHeaderMenuOpen(false);
                }}
              >
                {t('profile')}
              </HeaderMenuItem>
              <HeaderMenuItem
                as="button"
                selected={false}
                onClick={() => {
                  setHeaderMenuOpen(false);
                  setChatModalOpen(true);
                }}
              >
                {t('aiChat')}
              </HeaderMenuItem>
              <HeaderMenuItem
                as="a"
                href="/contact"
                selected={isSelected('/contact')}
                onClick={() => setHeaderMenuOpen(false)}
              >
                {t('contactUs')}
              </HeaderMenuItem>
            </div>
          </nav>
        </>
      )}

      {/* Floating chat - same as landing page */}
      <div className={`app-layout-floating-chat ${chatModalOpen ? 'app-layout-floating-chat--open' : ''}`}>
        {(!chatModalOpen || chatModalClosing) && (
          <button
            type="button"
            className={`app-layout-floating-chat-btn ${chatModalClosing ? 'app-layout-floating-chat-btn--reveal' : ''}`}
            onClick={() => !chatModalClosing && setChatModalOpen(true)}
            aria-label={t('aiChat')}
          >
            {t('writeYourMessage')}
            <span className="app-layout-floating-chat-dots" aria-hidden="true">
              <span className="app-layout-floating-chat-dot">.</span>
              <span className="app-layout-floating-chat-dot">.</span>
              <span className="app-layout-floating-chat-dot">.</span>
            </span>
          </button>
        )}
        {chatModalOpen && (
          <div className={`app-layout-floating-chat-panel ${chatModalClosing ? 'app-layout-floating-chat-panel--closing' : ''}`}>
            <div className="app-layout-floating-chat-panel-header">
              {user ? (
                <div className="app-layout-floating-chat-panel-menu-wrap">
                  <button
                    type="button"
                    className="app-layout-floating-chat-panel-hamburger"
                    onClick={() => setChatMenuOpen((o) => !o)}
                    aria-label={t('menu')}
                    aria-expanded={chatMenuOpen}
                  >
                    <svg className="app-layout-floating-chat-panel-hamburger-icon" viewBox="0 0 24 24" fill="currentColor" width="48" height="48" aria-hidden="true">
                      <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
                    </svg>
                  </button>
                  {chatMenuOpen && (
                    <>
                      <div className="app-layout-floating-chat-panel-menu-backdrop" onClick={() => setChatMenuOpen(false)} aria-hidden="true" />
                      <div className="app-layout-floating-chat-panel-menu">
                        <button type="button" className="app-layout-floating-chat-panel-menu-item" onClick={() => handleChatMenuAction('new')}>
                          {i18n.language === 'fa' ? 'گفتگوی جدید' : 'New conversation'}
                        </button>
                        <button type="button" className="app-layout-floating-chat-panel-menu-item" onClick={() => handleChatMenuAction('history')}>
                          {i18n.language === 'fa' ? 'تاریخچه' : 'History'}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="app-layout-floating-chat-panel-header-spacer" aria-hidden="true" />
              )}
              <span className="app-layout-floating-chat-panel-title">{t('aiChat')}</span>
              <button
                type="button"
                className="app-layout-floating-chat-panel-close"
                onClick={handleCloseChat}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <div className="app-layout-floating-chat-panel-content">
              {user ? (
                <BannerChat ref={bannerChatRef} hideHeader onOpenBuyModal={() => { handleCloseChat(); setTrainingProgramsModalOpen(true); }} />
              ) : (
                <div className="app-layout-chat-login-prompt">
                  <p>{i18n.language === 'fa' ? 'برای استفاده از چت با هوش مصنوعی، لطفاً وارد شوید.' : 'Please log in to use AI chat.'}</p>
                  <button type="button" className="app-layout-chat-login-btn" onClick={() => setAuthModalOpen(true)}>
                    {t('login')}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <TrainingProgramsModal
        isOpen={trainingProgramsModalOpen}
        onClose={() => setTrainingProgramsModalOpen(false)}
      />

      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
    </LayoutContext.Provider>
  );
};

export default AppLayout;
