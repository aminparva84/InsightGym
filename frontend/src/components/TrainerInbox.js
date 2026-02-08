import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import './TrainerInbox.css';

const API_BASE = `${getApiBase()}/api/messages`;
const ADMIN_BASE = `${getApiBase()}/api/admin`;

const TrainerInbox = () => {
  const { i18n } = useTranslation();
  const [threads, setThreads] = useState([]);
  const [selectedMember, setSelectedMember] = useState(null);
  const [messages, setMessages] = useState([]);
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingThreads, setLoadingThreads] = useState(true);
  const [loadingThread, setLoadingThread] = useState(false);
  const [progressCheckRequests, setProgressCheckRequests] = useState([]);
  const [loadingProgressRequests, setLoadingProgressRequests] = useState(false);
  const [respondingId, setRespondingId] = useState(null);
  const messagesContainerRef = useRef(null);

  const getAuthToken = () => localStorage.getItem('token') || '';
  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  const loadProgressCheckRequests = async () => {
    setLoadingProgressRequests(true);
    try {
      const res = await axios.get(`${ADMIN_BASE}/progress-check-requests?status=pending`, getAxiosConfig());
      setProgressCheckRequests(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setProgressCheckRequests([]);
    } finally {
      setLoadingProgressRequests(false);
    }
  };

  const respondProgressCheck = async (reqId, action) => {
    setRespondingId(reqId);
    try {
      await axios.patch(`${ADMIN_BASE}/progress-check-requests/${reqId}`, { action }, { ...getAxiosConfig(), headers: { ...getAxiosConfig().headers, 'Content-Type': 'application/json' } });
      setProgressCheckRequests(prev => prev.filter(r => r.id !== reqId));
    } catch (err) {
      console.error('Error responding to progress check:', err);
    } finally {
      setRespondingId(null);
    }
  };

  const loadThreads = async () => {
    setLoadingThreads(true);
    try {
      const res = await axios.get(API_BASE, getAxiosConfig());
      let list = res.data.threads || [];
      if (list.length === 0) {
        try {
          const membersRes = await axios.get(`${ADMIN_BASE}/members`, getAxiosConfig());
          const members = membersRes.data || [];
          list = members.map(m => ({
            user_id: m.id,
            username: m.username || m.email || 'Member',
            last_message: null,
            last_at: null,
            unread_count: 0
          }));
        } catch (_) {}
      }
      setThreads(list);
    } catch (err) {
      setThreads([]);
    } finally {
      setLoadingThreads(false);
    }
  };

  const loadThread = async (memberId, username) => {
    if (!memberId) return;
    setSelectedMember({ id: memberId, username: username || threads.find(t => t.user_id === memberId)?.username || 'Member' });
    setLoadingThread(true);
    try {
      const res = await axios.get(`${API_BASE}/thread/${memberId}`, getAxiosConfig());
      setMessages(res.data.messages || []);
      if (res.data.other_user) {
        setSelectedMember(res.data.other_user);
      }
    } catch (err) {
      setMessages([]);
    } finally {
      setLoadingThread(false);
    }
  };

  useEffect(() => {
    loadThreads();
    loadProgressCheckRequests();
  }, []);

  useEffect(() => {
    const el = messagesContainerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const handleSelectMember = (thread) => {
    loadThread(thread.user_id, thread.username);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!body.trim() || loading || !selectedMember) return;
    setLoading(true);
    const text = body.trim();
    setBody('');
    const tempId = 'temp-' + Date.now();
    setMessages(prev => [...prev, { id: tempId, body: text, created_at: new Date().toISOString(), is_mine: true }]);
    try {
      const res = await axios.post(API_BASE, { recipient_id: selectedMember.id, body: text }, getAxiosConfig());
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

  const fa = i18n.language === 'fa';
  return (
    <div className="trainer-inbox-container" dir="ltr">
      <div className="trainer-inbox-header">
        <h3>{fa ? 'پیام‌ها و درخواست‌ها' : 'Messages & requests'}</h3>
      </div>
      <div className="trainer-inbox-progress-requests">
        <h4>{fa ? 'درخواست‌های بررسی پیشرفت' : 'Progress check requests'}</h4>
        {loadingProgressRequests ? (
          <div className="trainer-inbox-loading">{fa ? 'در حال بارگذاری...' : 'Loading...'}</div>
        ) : progressCheckRequests.length === 0 ? (
          <p className="trainer-inbox-empty-progress">{fa ? 'درخواستی در انتظار نیست.' : 'No pending requests.'}</p>
        ) : (
          <ul className="progress-check-request-list">
            {progressCheckRequests.map((req) => (
              <li key={req.id} className="progress-check-request-item">
                <span className="progress-check-member">{req.member_username || `Member #${req.member_id}`}</span>
                <span className="progress-check-date">{req.requested_at ? new Date(req.requested_at).toLocaleString(fa ? 'fa-IR' : 'en-US', { dateStyle: 'short', timeStyle: 'short' }) : ''}</span>
                <div className="progress-check-actions">
                  <button type="button" className="progress-check-accept" onClick={() => respondProgressCheck(req.id, 'accept')} disabled={respondingId === req.id}>
                    {respondingId === req.id ? '…' : (fa ? 'پذیرش' : 'Accept')}
                  </button>
                  <button type="button" className="progress-check-deny" onClick={() => respondProgressCheck(req.id, 'deny')} disabled={respondingId === req.id}>
                    {respondingId === req.id ? '…' : (fa ? 'رد' : 'Deny')}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="trainer-inbox-body">
        <div className="trainer-inbox-list">
          {loadingThreads ? (
            <div className="trainer-inbox-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
          ) : threads.length === 0 ? (
            <div className="trainer-inbox-empty-list">
              <p>{i18n.language === 'fa' ? 'هنوز پیامی از اعضا ندارید.' : 'No messages from members yet.'}</p>
            </div>
          ) : (
            threads.map((thread) => (
              <button
                key={thread.user_id}
                type="button"
                className={`trainer-inbox-thread-btn ${selectedMember?.id === thread.user_id ? 'active' : ''}`}
                onClick={() => handleSelectMember(thread)}
              >
                <span className="thread-username">{thread.username}</span>
                {thread.unread_count > 0 && (
                  <span className="thread-unread">{thread.unread_count}</span>
                )}
              </button>
            ))
          )}
        </div>
        <div className="trainer-inbox-chat">
          {!selectedMember ? (
            <div className="trainer-inbox-select-prompt">
              <p>{i18n.language === 'fa' ? 'یک عضو را انتخاب کنید تا گفتگو را ببینید.' : 'Select a member to view the conversation.'}</p>
            </div>
          ) : (
            <>
              <div className="trainer-inbox-chat-header">
                <span>{selectedMember.username}</span>
              </div>
              <div className="trainer-inbox-messages" ref={messagesContainerRef}>
                {loadingThread ? (
                  <div className="trainer-inbox-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
                ) : messages.length === 0 ? (
                  <div className="trainer-inbox-empty-msgs">
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
                  placeholder={i18n.language === 'fa' ? 'پاسخ به عضو...' : 'Reply to member...'}
                  disabled={loading}
                />
                <button type="submit" className="trainer-chat-send" disabled={loading || !body.trim()}>
                  {i18n.language === 'fa' ? 'ارسال' : 'Send'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainerInbox;
