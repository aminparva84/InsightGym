import React from 'react';
import { useTranslation } from 'react-i18next';
import BannerChat from './BannerChat';
import { useAuth } from '../context/AuthContext';
import './LandingChatModal.css';

const LandingChatModal = ({ isOpen, onClose, onOpenAuth, onOpenBuyModal }) => {
  const { user } = useAuth();
  const { i18n } = useTranslation();

  if (!isOpen) return null;

  return (
    <>
      <div
        className="landing-chat-modal-overlay"
        onClick={onClose}
        role="dialog"
        aria-modal="true"
        aria-label="AI Chat"
      />
      <div className="landing-chat-modal" onClick={(e) => e.stopPropagation()} dir="ltr">
        <div className="landing-chat-modal-header">
          <span className="landing-chat-modal-title">AI Chat</span>
          <button
            type="button"
            className="landing-chat-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>
        <div className="landing-chat-modal-content">
          {user ? (
            <BannerChat onOpenBuyModal={onOpenBuyModal} />
          ) : (
            <div className="landing-chat-login-prompt">
              <p>{i18n.language === 'fa' ? 'برای استفاده از چت با هوش مصنوعی، لطفاً وارد شوید.' : 'Please log in to use AI chat.'}</p>
              <button type="button" className="landing-chat-login-btn" onClick={() => { onClose(); onOpenAuth?.(); }}>
                {i18n.language === 'fa' ? 'ورود' : 'Log in'}
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default LandingChatModal;
