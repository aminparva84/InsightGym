import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import { useAuth } from '../context/AuthContext';
import './BannerChat.css';

const BannerChat = () => {
  const { i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyView, setHistoryView] = useState('list'); // 'list' | 'detail'
  const [conversationsList, setConversationsList] = useState([]);
  const [selectedConversationMessages, setSelectedConversationMessages] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [renamingSessionId, setRenamingSessionId] = useState(null);
  const [renameTitle, setRenameTitle] = useState('');
  const [renameSaving, setRenameSaving] = useState(false);
  const messagesContainerRef = useRef(null);

  const getAuthToken = useCallback(() => {
    const localToken = localStorage.getItem('token');
    if (localToken && localToken.trim() !== '') {
      return localToken.trim();
    }
    const authHeader = axios.defaults.headers.common['Authorization'];
    if (authHeader && typeof authHeader === 'string' && authHeader.startsWith('Bearer ')) {
      return authHeader.replace('Bearer ', '').trim();
    }
    return null;
  }, []);

  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    if (!token) {
      return {};
    }
    
    // Remove any accidental "Bearer " prefix
    let cleanToken = token.trim();
    if (cleanToken.startsWith('Bearer ')) {
      cleanToken = cleanToken.replace(/^Bearer\s+/i, '').trim();
    }
    
    // Validate token format
    if (!cleanToken.startsWith('eyJ')) {
      console.error('Invalid token format in BannerChat!');
      return {};
    }
    
    // Update axios defaults
    axios.defaults.headers.common['Authorization'] = `Bearer ${cleanToken}`;
    
    return {
      headers: {
        'Authorization': `Bearer ${cleanToken}`
      }
    };
  }, [getAuthToken]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      const el = messagesContainerRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    });
  };

  const mapHistoryToMessages = useCallback((raw) => {
    if (!Array.isArray(raw)) return [];
    const mapped = [];
    for (const item of raw) {
      if (item.message != null) mapped.push({ role: 'user', content: item.message });
      if (item.response != null) mapped.push({ role: 'assistant', content: item.response });
    }
    return mapped;
  }, []);

  const loadChatHistory = useCallback(async () => {
    try {
      const convRes = await axios.get(`${API_BASE}/api/chat/conversations`, getAxiosConfig());
      const convs = convRes.data && Array.isArray(convRes.data) ? convRes.data : [];
      if (convs.length > 0) {
        const first = convs[0];
        const sid = first.session_id;
        setCurrentSessionId(sid);
        const histRes = await axios.get(`${API_BASE}/api/chat/history?session_id=${encodeURIComponent(sid)}`, getAxiosConfig());
        setMessages(mapHistoryToMessages(histRes.data || []));
      } else {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      setMessages([]);
      setCurrentSessionId(null);
    }
  }, [API_BASE, getAxiosConfig, mapHistoryToMessages]);

  useEffect(() => {
    if (user) {
      loadChatHistory();
    }
  }, [user, loadChatHistory]);

  const startNewConversation = () => {
    setMessages([]);
    setInputMessage('');
    setCurrentSessionId(null);
    setShowHistory(false);
    setHistoryView('list');
  };

  const fetchConversations = async () => {
    setHistoryLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/chat/conversations`, getAxiosConfig());
      setConversationsList(Array.isArray(response.data) ? response.data : []);
      setHistoryView('list');
      setSelectedSessionId(null);
      setSelectedConversationMessages([]);
    } catch (error) {
      console.error('Error fetching conversations:', error);
      setConversationsList([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const selectConversation = async (sessionId) => {
    setHistoryLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/chat/history?session_id=${encodeURIComponent(sessionId)}`, getAxiosConfig());
      const mapped = mapHistoryToMessages(response.data || []);
      setMessages(mapped);
      setCurrentSessionId(sessionId);
      setShowHistory(false);
      setHistoryView('list');
      setSelectedSessionId(null);
      setSelectedConversationMessages([]);
    } catch (error) {
      console.error('Error loading conversation:', error);
    } finally {
      setHistoryLoading(false);
    }
  };

  const openHistory = () => {
    setShowHistory(true);
    fetchConversations();
  };

  const formatConversationDate = (iso) => {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (_) {
      return iso;
    }
  };

  const openRename = (conv, e) => {
    e.preventDefault();
    e.stopPropagation();
    setRenamingSessionId(conv.session_id);
    setRenameTitle(conv.title || conv.preview || '');
  };

  const cancelRename = () => {
    setRenamingSessionId(null);
    setRenameTitle('');
  };

  const saveRename = async () => {
    if (!renamingSessionId) return;
    setRenameSaving(true);
    try {
      await axios.patch(
        `${API_BASE}/api/chat/conversations/${encodeURIComponent(renamingSessionId)}`,
        { title: renameTitle.trim() },
        getAxiosConfig()
      );
      setConversationsList(prev =>
        prev.map(c => c.session_id === renamingSessionId ? { ...c, title: renameTitle.trim() || c.preview } : c)
      );
      cancelRename();
    } catch (error) {
      console.error('Error renaming conversation:', error);
    } finally {
      setRenameSaving(false);
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
        `${API_BASE}/api/chat`,
        { message: inputMessage, session_id: currentSessionId || undefined },
        getAxiosConfig()
      );

      const sid = response.data.session_id;
      if (sid) setCurrentSessionId(sid);

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
    <div className="banner-chat-container" style={{ position: 'relative' }}>
      <div className="banner-chat-header">
        <span className="banner-chat-header-title">
          {i18n.language === 'fa' ? 'چت' : 'Chat'}
        </span>
        <div className="banner-chat-header-actions">
          <button
            type="button"
            className="banner-chat-header-btn"
            onClick={openHistory}
          >
            {i18n.language === 'fa' ? 'تاریخچه' : 'History'}
          </button>
          <button
            type="button"
            className="banner-chat-header-btn"
            onClick={startNewConversation}
          >
            {i18n.language === 'fa' ? 'گفتگوی جدید' : 'New conversation'}
          </button>
        </div>
      </div>

      {showHistory && (
        <div className="banner-chat-history-overlay">
          <div className="banner-chat-history-header">
            <h3>
              {historyView === 'detail' ? (
                <button type="button" className="banner-chat-history-back" onClick={() => setHistoryView('list')}>
                  ← {i18n.language === 'fa' ? 'بازگشت' : 'Back'}
                </button>
              ) : (
                i18n.language === 'fa' ? 'تاریخچه گفتگو' : 'Conversation history'
              )}
            </h3>
            <button type="button" className="banner-chat-history-close" onClick={() => { setShowHistory(false); setHistoryView('list'); }}>
              {i18n.language === 'fa' ? 'بستن' : 'Close'}
            </button>
          </div>
          <div className="banner-chat-history-list">
            {historyLoading ? (
              <p className="banner-chat-history-empty">
                {i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}
              </p>
            ) : historyView === 'list' ? (
              conversationsList.length === 0 ? (
                <p className="banner-chat-history-empty">
                  {i18n.language === 'fa' ? 'هنوز گفتگویی ندارید.' : 'No conversations yet.'}
                </p>
              ) : (
                conversationsList.map((conv) => (
                  <div key={conv.session_id} className="banner-chat-history-conv-row-wrap">
                    <button
                      type="button"
                      className="banner-chat-history-conv-row"
                      onClick={() => selectConversation(conv.session_id)}
                    >
                      <span className="banner-chat-history-conv-preview">{conv.title || conv.preview}</span>
                      <span className="banner-chat-history-conv-date">{formatConversationDate(conv.last_at)}</span>
                    </button>
                    <button
                      type="button"
                      className="banner-chat-history-rename-btn"
                      onClick={(e) => openRename(conv, e)}
                      title={i18n.language === 'fa' ? 'تغییر نام' : 'Rename'}
                      aria-label={i18n.language === 'fa' ? 'تغییر نام' : 'Rename'}
                    >
                      ✎
                    </button>
                  </div>
                ))
              )
            ) : (
              selectedConversationMessages.length === 0 ? (
                <p className="banner-chat-history-empty">
                  {i18n.language === 'fa' ? 'پیامی در این گفتگو نیست.' : 'No messages in this conversation.'}
                </p>
              ) : (
                selectedConversationMessages.map((msg, index) => (
                  <div key={index} className={`banner-chat-history-item ${msg.role === 'user' ? 'user-msg' : 'assistant-msg'}`}>
                    {msg.content}
                  </div>
                ))
              )
            )}
          </div>
          {renamingSessionId && (
            <div className="banner-chat-rename-modal">
              <div className="banner-chat-rename-content">
                <label className="banner-chat-rename-label">
                  {i18n.language === 'fa' ? 'نام گفتگو' : 'Conversation name'}
                </label>
                <input
                  type="text"
                  className="banner-chat-rename-input"
                  value={renameTitle}
                  onChange={(e) => setRenameTitle(e.target.value)}
                  placeholder={i18n.language === 'fa' ? 'نام گفتگو' : 'Conversation name'}
                  autoFocus
                />
                <div className="banner-chat-rename-actions">
                  <button type="button" className="banner-chat-rename-cancel" onClick={cancelRename}>
                    {i18n.language === 'fa' ? 'انصراف' : 'Cancel'}
                  </button>
                  <button type="button" className="banner-chat-rename-save" onClick={saveRename} disabled={renameSaving}>
                    {renameSaving ? (i18n.language === 'fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language === 'fa' ? 'ذخیره' : 'Save')}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div ref={messagesContainerRef} className="banner-chat-messages">
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

