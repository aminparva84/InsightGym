import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { getApiBase } from '../services/apiBase';
import './ChatBox.css';

const API_BASE = getApiBase();

const ChatBox = () => {
  const { i18n } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('chat');
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [historyView, setHistoryView] = useState('list');
  const [conversationsList, setConversationsList] = useState([]);
  const [selectedConversationMessages, setSelectedConversationMessages] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [renamingSessionId, setRenamingSessionId] = useState(null);
  const [renameTitle, setRenameTitle] = useState('');
  const [renameSaving, setRenameSaving] = useState(false);
  const messagesContainerRef = useRef(null);

  const getAuthToken = useCallback(() => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  }, []);

  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const text = inputMessage.trim();
    if (!text || loading) return;

    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const endpoint = mode === 'actions' ? `${API_BASE}/api/ai/plan` : `${API_BASE}/api/chat`;
      const response = await axios.post(
        endpoint,
        { message: text, session_id: currentSessionId || undefined },
        getAxiosConfig()
      );

      const sid = response.data.session_id;
      if (sid) setCurrentSessionId(sid);

      const aiMessage = {
        role: 'assistant',
        content: response.data.assistant_response || response.data.response || response.data.message || 'No response',
        timestamp: new Date().toISOString()
      };
      if (mode === 'actions') {
        aiMessage.results = response.data.results || [];
        aiMessage.actions = response.data.actions || [];
        aiMessage.errors = response.data.errors || [];
      }

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

  const renderActionResults = (msg) => {
    if (!msg || !Array.isArray(msg.results) || msg.results.length === 0) return null;
    return (
      <div className="message-results">
        {msg.errors && msg.errors.length > 0 && (
          <div className="message-result-error">
            {(msg.errors || []).join(', ')}
          </div>
        )}
        {msg.results.map((res, idx) => {
          const action = res.action || 'action';
          const status = res.status || 'ok';
          const data = res.data;
          return (
            <div key={`${action}-${idx}`} className={`message-result-item ${status}`}>
              <div className="message-result-title">
                {action} {status !== 'ok' ? `(${status})` : ''}
              </div>
              {status !== 'ok' && res.error && (
                <div className="message-result-error">{res.error}</div>
              )}
              {action === 'search_exercises' && Array.isArray(data) && (
                <ul className="message-result-list">
                  {data.map((ex) => (
                    <li key={ex.id || ex.name}>
                      {ex.name || ex.name_fa || ex.name_en}
                    </li>
                  ))}
                </ul>
              )}
              {action === 'create_workout_plan' && data && data.response && (
                <pre className="message-result-pre">{data.response}</pre>
              )}
              {action === 'update_user_profile' && data && data.updated && (
                <pre className="message-result-pre">{JSON.stringify(data.updated, null, 2)}</pre>
              )}
              {action === 'progress_check' && data && (
                <div className="message-result-text">
                  {i18n.language === 'fa' ? 'وضعیت:' : 'Status:'} {data.status}
                </div>
              )}
              {action === 'trainer_message' && data && (
                <div className="message-result-text">
                  {i18n.language === 'fa' ? 'ارسال شد به:' : 'Sent to:'} {data.recipient_id}
                </div>
              )}
              {action === 'site_settings' && data && data.updated && (
                <pre className="message-result-pre">{JSON.stringify(data.updated, null, 2)}</pre>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="chatbox-container" dir="ltr" style={{ position: 'relative' }}>
      <div className="chatbox-header">
        <h3>
          {mode === 'actions'
            ? (i18n.language === 'fa' ? 'اقدامات AI' : 'AI Actions')
            : (i18n.language === 'fa' ? 'چت با AI' : 'Chat with AI')}
        </h3>
        <div className="chatbox-header-actions">
          <div className="chatbox-mode-toggle">
            <button
              type="button"
              className={`chatbox-mode-btn ${mode === 'chat' ? 'active' : ''}`}
              onClick={() => setMode('chat')}
            >
              {i18n.language === 'fa' ? 'چت' : 'Chat'}
            </button>
            <button
              type="button"
              className={`chatbox-mode-btn ${mode === 'actions' ? 'active' : ''}`}
              onClick={() => setMode('actions')}
            >
              {i18n.language === 'fa' ? 'اقدامات' : 'Actions'}
            </button>
          </div>
          <button type="button" className="chatbox-header-btn" onClick={openHistory}>
            {i18n.language === 'fa' ? 'تاریخچه' : 'History'}
          </button>
          <button type="button" className="chatbox-header-btn" onClick={startNewConversation}>
            {i18n.language === 'fa' ? 'گفتگوی جدید' : 'New conversation'}
          </button>
        </div>
      </div>

      {showHistory && (
        <div className="chatbox-history-overlay">
          <div className="chatbox-history-header">
            <h3>
              {historyView === 'detail' ? (
                <button type="button" className="chatbox-history-back" onClick={() => setHistoryView('list')}>
                  ← {i18n.language === 'fa' ? 'بازگشت' : 'Back'}
                </button>
              ) : (
                i18n.language === 'fa' ? 'تاریخچه گفتگو' : 'Conversation history'
              )}
            </h3>
            <button type="button" className="chatbox-history-close" onClick={() => { setShowHistory(false); setHistoryView('list'); }}>
              {i18n.language === 'fa' ? 'بستن' : 'Close'}
            </button>
          </div>
          <div className="chatbox-history-list">
            {historyLoading ? (
              <p className="chatbox-history-empty">
                {i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}
              </p>
            ) : historyView === 'list' ? (
              conversationsList.length === 0 ? (
                <p className="chatbox-history-empty">
                  {i18n.language === 'fa' ? 'هنوز گفتگویی ندارید.' : 'No conversations yet.'}
                </p>
              ) : (
                conversationsList.map((conv) => (
                  <div key={conv.session_id} className="chatbox-history-conv-row-wrap">
                    <button
                      type="button"
                      className="chatbox-history-conv-row"
                      onClick={() => selectConversation(conv.session_id)}
                    >
                      <span className="chatbox-history-conv-preview">{conv.title || conv.preview}</span>
                      <span className="chatbox-history-conv-date">{formatConversationDate(conv.last_at)}</span>
                    </button>
                    <button
                      type="button"
                      className="chatbox-history-rename-btn"
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
                <p className="chatbox-history-empty">
                  {i18n.language === 'fa' ? 'پیامی در این گفتگو نیست.' : 'No messages in this conversation.'}
                </p>
              ) : (
                selectedConversationMessages.map((msg, index) => (
                  <div key={index} className={`chatbox-history-item ${msg.role === 'user' ? 'user-msg' : 'assistant-msg'}`}>
                    {msg.content}
                  </div>
                ))
              )
            )}
          </div>
          {renamingSessionId && (
            <div className="chatbox-rename-modal">
              <div className="chatbox-rename-content">
                <label className="chatbox-rename-label">
                  {i18n.language === 'fa' ? 'نام گفتگو' : 'Conversation name'}
                </label>
                <input
                  type="text"
                  className="chatbox-rename-input"
                  value={renameTitle}
                  onChange={(e) => setRenameTitle(e.target.value)}
                  placeholder={i18n.language === 'fa' ? 'نام گفتگو' : 'Conversation name'}
                  autoFocus
                />
                <div className="chatbox-rename-actions">
                  <button type="button" className="chatbox-rename-cancel" onClick={cancelRename}>
                    {i18n.language === 'fa' ? 'انصراف' : 'Cancel'}
                  </button>
                  <button type="button" className="chatbox-rename-save" onClick={saveRename} disabled={renameSaving}>
                    {renameSaving ? (i18n.language === 'fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language === 'fa' ? 'ذخیره' : 'Save')}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="chatbox-messages" ref={messagesContainerRef}>
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
              {renderActionResults(msg)}
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
        <div />
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

