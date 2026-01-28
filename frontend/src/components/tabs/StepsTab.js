import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './StepsTab.css';

const API_BASE = 'http://localhost:5000';

const getAuthConfig = () => {
  const token = localStorage.getItem('token');
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
};

const StepsTab = () => {
  const { i18n } = useTranslation();
  const [todaySteps, setTodaySteps] = useState(null);
  const [manualSteps, setManualSteps] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const today = new Date().toISOString().slice(0, 10);

  const loadSteps = useCallback(async () => {
    try {
      const from = new Date();
      from.setDate(from.getDate() - 30);
      const to = new Date();
      const res = await axios.get(
        `${API_BASE}/api/member/steps?from_date=${from.toISOString().slice(0, 10)}&to_date=${to.toISOString().slice(0, 10)}`,
        getAuthConfig()
      );
      const list = Array.isArray(res.data) ? res.data : [];
      setHistory(list);
      const todayEntry = list.find((e) => e.date === today);
      setTodaySteps(todayEntry ? todayEntry.steps : null);
      setManualSteps(todayEntry ? String(todayEntry.steps) : '');
    } catch (err) {
      console.error('Error loading steps:', err);
      setHistory([]);
      setTodaySteps(null);
    } finally {
      setLoading(false);
    }
  }, [today]);

  useEffect(() => {
    loadSteps();
  }, [loadSteps]);

  // Device step count (e.g. Pedometer API) can be wired here when available on target platforms

  const saveSteps = async (stepsValue, source = 'manual') => {
    const steps = parseInt(stepsValue, 10);
    if (isNaN(steps) || steps < 0) return;
    setSaving(true);
    try {
      await axios.post(
        `${API_BASE}/api/member/steps`,
        { date: today, steps, source },
        { ...getAuthConfig(), headers: { ...getAuthConfig().headers, 'Content-Type': 'application/json' } }
      );
      setTodaySteps(steps);
      setManualSteps(String(steps));
      loadSteps();
    } catch (err) {
      console.error('Error saving steps:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleManualSubmit = (e) => {
    e.preventDefault();
    saveSteps(manualSteps, 'manual');
  };

  const fa = i18n.language === 'fa';
  return (
    <div className="steps-tab" dir="ltr">
      <div className="steps-header">
        <h2>{fa ? 'شمارش قدم' : 'Step Counter'}</h2>
        <p className="steps-subtitle">
          {fa ? 'قدم‌های امروز را وارد کنید یا از دستگاه (موبایل) استفاده کنید.' : 'Enter your steps for today or use your device (mobile).'}
        </p>
      </div>

      {loading ? (
        <div className="steps-loading">{fa ? 'در حال بارگذاری...' : 'Loading...'}</div>
      ) : (
        <>
          <div className="steps-today-card">
            <h3>{fa ? 'امروز' : 'Today'}</h3>
            <div className="steps-today-value">
              {(todaySteps !== null && todaySteps !== undefined) ? todaySteps : '—'}
            </div>
            <p className="steps-source">
              {todaySteps != null && (fa ? 'ثبت شده' : 'Recorded')}
            </p>
            <form onSubmit={handleManualSubmit} className="steps-manual-form">
              <label htmlFor="steps-input">{fa ? 'تعداد قدم' : 'Number of steps'}</label>
              <input
                id="steps-input"
                type="number"
                min="0"
                step="1"
                value={manualSteps}
                onChange={(e) => setManualSteps(e.target.value)}
                placeholder={fa ? 'مثلاً 5000' : 'e.g. 5000'}
              />
              <button type="submit" disabled={saving}>
                {saving ? (fa ? 'در حال ذخیره...' : 'Saving...') : (fa ? 'ذخیره' : 'Save')}
              </button>
            </form>
          </div>

          <div className="steps-history">
            <h3>{fa ? 'تاریخچه (۳۰ روز گذشته)' : 'History (last 30 days)'}</h3>
            {history.length === 0 ? (
              <p className="steps-no-history">{fa ? 'هنوز قدمی ثبت نشده است.' : 'No steps recorded yet.'}</p>
            ) : (
              <ul className="steps-history-list">
                {history.slice(0, 14).map((entry) => (
                  <li key={entry.date} className="steps-history-item">
                    <span className="steps-history-date">{entry.date}</span>
                    <span className="steps-history-steps">{entry.steps}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default StepsTab;
