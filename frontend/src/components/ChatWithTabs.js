import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ChatBox from './ChatBox';
import AskProgressCheck from './AskProgressCheck';
import TrainerInbox from './TrainerInbox';
import './ChatWithTabs.css';

const ChatWithTabs = ({ userRole }) => {
  const { i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState('ai');

  const isTrainer = userRole === 'admin' || userRole === 'assistant';

  return (
    <div className="chat-with-tabs" dir="ltr">
      <div className="chat-with-tabs-header">
        <button
          type="button"
          className={`chat-with-tabs-btn ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <span className="chat-tab-icon">🤖</span>
          {i18n.language === 'fa' ? 'چت با AI' : 'AI Chat'}
        </button>
        <button
          type="button"
          className={`chat-with-tabs-btn ${activeTab === 'trainer' ? 'active' : ''}`}
          onClick={() => setActiveTab('trainer')}
        >
          <span className="chat-tab-icon">💬</span>
          {isTrainer
            ? (i18n.language === 'fa' ? 'پیام‌های اعضا' : 'Messages')
            : (i18n.language === 'fa' ? 'پیام به مربی' : 'Trainer')}
        </button>
      </div>
      <div className="chat-with-tabs-content">
        {activeTab === 'ai' && <ChatBox />}
        {activeTab === 'trainer' && (
          isTrainer ? <TrainerInbox /> : <AskProgressCheck />
        )}
      </div>
    </div>
  );
};

export default ChatWithTabs;
