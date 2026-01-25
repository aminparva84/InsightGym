import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './ChatBox.css';

const ChatBox = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const getAuthToken = () => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(
        'http://localhost:5000/api/chat',
        { message: inputMessage.trim() },
        getAxiosConfig()
      );

      const aiMessage = {
        role: 'assistant',
        content: response.data.response || response.data.message || 'No response',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: i18n.language === 'fa' 
          ? 'خطا در ارسال پیام. لطفاً دوباره تلاش کنید.'
          : 'Error sending message. Please try again.',
        timestamp: new Date().toISOString(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbox-container" dir="ltr">
      <div className="chatbox-header">
        <h3>{i18n.language === 'fa' ? 'چت با AI' : 'Chat with AI'}</h3>
      </div>
      <div className="chatbox-messages">
        {messages.length === 0 ? (
          <div className="chatbox-empty">
            <p>{i18n.language === 'fa' ? 'پیامی ارسال نشده است. شروع به گفتگو کنید!' : 'No messages yet. Start a conversation!'}</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message assistant">
            <div className="message-content loading">
              {i18n.language === 'fa' ? 'در حال تایپ...' : 'Typing...'}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chatbox-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="chatbox-input"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={i18n.language === 'fa' ? 'پیام خود را بنویسید...' : 'Type your message...'}
          disabled={loading}
        />
        <button type="submit" className="chatbox-send-btn" disabled={loading || !inputMessage.trim()}>
          {i18n.language === 'fa' ? 'ارسال' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatBox;

