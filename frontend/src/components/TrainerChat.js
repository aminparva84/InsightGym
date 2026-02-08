import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import './TrainerChat.css';

const API_BASE = `${getApiBase()}/api/messages`;

const TrainerChat = () => {
  const { i18n } = useTranslation();
  const [trainer, setTrainer] = useState(null);
  const [messages, setMessages] = useState([]);
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingThread, setLoadingThread] = useState(true);
  const [error, setError] = useState(null);
  const messagesContainerRef = useRef(null);

  const getAuthToken = () => localStorage.getItem('token') || '';
  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  const loadThreads = async () => {
    try {
      const config = getAxiosConfig();
      if (!config.headers?.Authorization) {
        setError(i18n.language === 'fa' ? 'لطفاً وارد شوید.' : 'Please log in.');
        setLoadingThread(false);
        return null;
      }
      const res = await axios.get(API_BASE, { ...config, timeout: 15000 });
      const trainerData = res.data.trainer || (res.data.threads && res.data.threads[0] ? { id: res.data.threads[0].user_id, username: res.data.threads[0].username } : null);
      setTrainer(trainerData);
      setError(trainerData ? null : (res.data.message || null));
      return res.data;
    } catch (err) {
      const isNetworkError = !err.response && (err.message === 'Network Error' || err.code === 'ERR_NETWORK');
      setError(isNetworkError
        ? (i18n.language === 'fa' ? 'اتصال برقرار نشد. لطفاً اتصال سرور (backend) را بررسی کنید.' : 'Cannot connect to server. Please verify the backend is reachable.')
        : (err.response?.data?.error || err.message));
      setTrainer(null);
      return null;
    }
  };

  const loadThread = async (trainerId) => {
    if (!trainerId) return;
    setLoadingThread(true);
    try {
      const res = await axios.get(`${API_BASE}/thread/${trainerId}`, { ...getAxiosConfig(), timeout: 15000 });
      setMessages(res.data.messages || []);
    } catch (err) {
      setMessages([]);
    } finally {
      setLoadingThread(false);
    }
  };

  useEffect(() => {
    loadThreads().then((data) => {
      const tid = data?.trainer?.id || (data?.threads?.[0]?.user_id);
      if (!tid) setLoadingThread(false);
    });
  }, []);

  useEffect(() => {
    if (trainer?.id) loadThread(trainer.id);
  }, [trainer?.id]);

  useEffect(() => {
    const el = messagesContainerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!body.trim() || loading || !trainer) return;
    setLoading(true);
    const text = body.trim();
    setBody('');
    const tempId = 'temp-' + Date.now();
    setMessages(prev => [...prev, { id: tempId, body: text, created_at: new Date().toISOString(), is_mine: true }]);
    try {
      const res = await axios.post(API_BASE, { body: text }, getAxiosConfig());
      setMessages(prev => [
        ...prev.filter(m => String(m.id) !== tempId),
        { ...res.data, is_mine: true }
      ]);
    } catch (err) {
      setMessages(prev => prev.filter(m => String(m.id) !== tempId));
      setBody(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trainer-chat-container" dir="ltr">
      <div className="trainer-chat-header">
        <h3>{i18n.language === 'fa' ? 'پیام به مربی' : 'Message your trainer'}</h3>
        {trainer && <span className="trainer-name">{trainer.username}</span>}
      </div>
      {loadingThread && !trainer ? (
        <div className="trainer-chat-empty">
          <p>{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</p>
        </div>
      ) : !trainer ? (
        <div className="trainer-chat-empty">
          <p>{error || (i18n.language === 'fa' ? 'هنوز مربی به شما اختصاص داده نشده است.' : 'No trainer assigned yet.')}</p>
        </div>
      ) : (
        <>
          <div className="trainer-chat-messages" ref={messagesContainerRef}>
            {loadingThread ? (
              <div className="trainer-chat-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
            ) : messages.length === 0 ? (
              <div className="trainer-chat-empty">
                <p>{i18n.language === 'fa' ? 'هنوز پیامی رد و بدل نشده است.' : 'No messages yet.'}</p>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`trainer-msg ${msg.is_mine ? 'mine' : 'theirs'}`}>
                  <div className="trainer-msg-content">{msg.body}</div>
                  <div className="trainer-msg-time">
                    {msg.created_at ? new Date(msg.created_at).toLocaleString(i18n.language === 'fa' ? 'fa-IR' : 'en-US') : ''}
                  </div>
                </div>
              ))
            )}
            <div />
          </div>
          <form className="trainer-chat-form" onSubmit={handleSend}>
            <input
              type="text"
              className="trainer-chat-input"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder={i18n.language === 'fa' ? 'پیام به مربی...' : 'Message your trainer...'}
              disabled={loading}
            />
            <button type="submit" className="trainer-chat-send" disabled={loading || !body.trim()}>
              {i18n.language === 'fa' ? 'ارسال' : 'Send'}
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default TrainerChat;
