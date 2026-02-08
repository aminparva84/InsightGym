import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import './BreakRequestModal.css';

const API_BASE = getApiBase();

const getAuthConfig = () => {
  const token = localStorage.getItem('token');
  return token ? { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } } : {};
};

const BreakRequestModal = ({ isOpen, onClose, onSuccess }) => {
  const { i18n } = useTranslation();
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const fa = i18n.language === 'fa';

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = (message || '').trim();
    if (!trimmed) {
      setError(fa ? 'لطفاً پیام را وارد کنید.' : 'Please enter a message.');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await axios.post(`${API_BASE}/api/member/break-request`, { message: trimmed }, getAuthConfig());
      setMessage('');
      onSuccess && onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || (fa ? 'خطا در ارسال.' : 'Failed to send.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="break-request-modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="break-request-modal" onClick={(e) => e.stopPropagation()} dir="ltr">
        <div className="break-request-modal-header">
          <h3>{fa ? 'درخواست استراحت' : 'Request a break'}</h3>
          <button type="button" className="break-request-modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        <p className="break-request-modal-desc">
          {fa ? 'پیام شما به ادمین یا مربی که با شما کار می‌کند ارسال می‌شود.' : 'Your message will be sent to the admin or assistant who works with you.'}
        </p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="break-request-message">{fa ? 'پیام' : 'Message'}</label>
          <textarea
            id="break-request-message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={fa ? 'دلیل یا مدت استراحت را بنویسید...' : 'Write your reason or break duration...'}
            rows={4}
          />
          {error && <p className="break-request-modal-error">{error}</p>}
          <div className="break-request-modal-actions">
            <button type="button" onClick={onClose}>
              {fa ? 'انصراف' : 'Cancel'}
            </button>
            <button type="submit" disabled={submitting}>
              {submitting ? (fa ? 'در حال ارسال...' : 'Sending...') : (fa ? 'ارسال' : 'Send')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BreakRequestModal;
