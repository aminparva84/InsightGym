import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ChatPanel from './ChatPanel';
import './FloatingChatButton.css';

const FloatingChatButton = () => {
  const { t, i18n } = useTranslation();
  const [showChat, setShowChat] = useState(false);

  return (
    <>
      <button 
        className="floating-chat-button"
        onClick={() => setShowChat(!showChat)}
        aria-label={t('chat')}
      >
        <span className="chat-icon">🤖</span>
        {showChat && <span className="chat-badge">✕</span>}
      </button>
      {showChat && <ChatPanel onClose={() => setShowChat(false)} />}
    </>
  );
};

export default FloatingChatButton;

