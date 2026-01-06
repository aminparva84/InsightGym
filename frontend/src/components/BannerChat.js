import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './BannerChat.css';

const BannerChat = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const getAuthToken = () => {
    const localToken = localStorage.getItem('token');
    if (localToken && localToken.trim() !== '') {
      return localToken.trim();
    }
    const authHeader = axios.defaults.headers.common['Authorization'];
    if (authHeader && typeof authHeader === 'string' && authHeader.startsWith('Bearer ')) {
      return authHeader.replace('Bearer ', '').trim();
    }
    return null;
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    if (!token) {
      return {};
    }
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  };

  useEffect(() => {
    if (user) {
      loadChatHistory();
    }
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/chat/history', getAxiosConfig());
      if (response.data && Array.isArray(response.data)) {
        setMessages(response.data);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(
        'http://localhost:5000/api/chat',
        { message: inputMessage },
        getAxiosConfig()
      );

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response || response.data.message || 'No response',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: i18n.language === 'fa' 
          ? 'خطا در ارسال پیام. لطفاً دوباره تلاش کنید.'
          : 'Error sending message. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="banner-chat-container">
      <div className="banner-chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`banner-chat-message ${msg.role}`}>
            <div className="banner-chat-message-content">
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="banner-chat-message assistant">
            <div className="banner-chat-message-content loading">
              {i18n.language === 'fa' ? 'در حال تایپ...' : 'Typing...'}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="banner-chat-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={i18n.language === 'fa' ? 'پیام خود را بنویسید...' : 'Type your message...'}
          className="banner-chat-input"
          disabled={loading}
        />
        <button type="submit" className="banner-chat-send" disabled={loading || !inputMessage.trim()}>
          {i18n.language === 'fa' ? 'ارسال' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default BannerChat;

