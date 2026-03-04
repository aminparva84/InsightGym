import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { useLayout } from '../context/LayoutContext';
import landingHeroImg from '../assets/images/landing-hero.webp';
import heroIconSection11 from '../assets/images/hero-icon-section11.webp';
import heroIconTrainingPlan from '../assets/images/hero-icon-training-plan.webp';
import heroIconProfile from '../assets/images/hero-icon-profile.webp';
import heroIconSection4 from '../assets/images/hero-icon-section4.webp';
import heroIconAiChat from '../assets/images/hero-icon-ai-chat.webp';
import './LandingPage.css';

const LandingPage = () => {
  const { i18n, t } = useTranslation();
  const { user } = useAuth();
  const layout = useLayout();

  const openAuthIfNeeded = (e) => {
    if (!user) {
      e.preventDefault();
      layout?.openAuthModal?.();
    }
  };

  return (
    <div className="landing-page">
      {/* Banner - Background + Hero centered */}
      <section className="landing-banner">
        <div className="banner-hero-wrapper">
          <div className="banner-hero">
            <img src={landingHeroImg} alt="" className="banner-hero-image" />
          </div>
          {/* Section 3 (2 o'clock) - Training Plan */}
          <Link
            to={user ? '/dashboard?tab=training-program' : '#'}
            className="hero-circle-icon hero-circle-icon--section-3"
            aria-label={t('trainingPlan')}
            onClick={openAuthIfNeeded}
          >
            <img src={heroIconTrainingPlan} alt="" />
          </Link>

          {/* Section 4 (3 o'clock) - Progress Trend (روند تغییرات) - out of circle */}
          <Link
            to={user ? '/dashboard?tab=history&view=progress' : '#'}
            className="hero-circle-icon hero-circle-icon--section-4"
            aria-label={t('progressTrend')}
            onClick={openAuthIfNeeded}
          >
            <img src={heroIconSection4} alt="" />
          </Link>

          {/* Section 7 (6 o'clock) - Profile - out of circle */}
          <Link
            to={user ? '/dashboard?tab=profile' : '#'}
            className="hero-circle-icon hero-circle-icon--section-7"
            aria-label={t('profile')}
            onClick={openAuthIfNeeded}
          >
            <img src={heroIconProfile} alt="" />
          </Link>

          {/* Section 9 (9 o'clock) - AI Chat - opens same chatbox as floating button */}
          <button
            type="button"
            className="hero-circle-icon hero-circle-icon--section-9"
            aria-label={t('aiChat')}
            onClick={(e) => {
              e.preventDefault();
              layout?.openChatModal?.();
            }}
          >
            <img src={heroIconAiChat} alt="" />
          </button>

          {/* Section 11 (11 o'clock) - Contact Us */}
          <Link
            to="/contact"
            className="hero-circle-icon hero-circle-icon--section-11"
            aria-label={t('contactUs')}
          >
            <img src={heroIconSection11} alt="" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
