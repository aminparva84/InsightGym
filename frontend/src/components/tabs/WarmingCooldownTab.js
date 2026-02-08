import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './WarmingCooldownTab.css';

const API_BASE = getApiBase();

const defaultPhase = () => ({ title_fa: '', title_en: '', steps: [] });
const defaultStep = () => ({ title_fa: '', title_en: '', body_fa: '', body_en: '' });

const WarmingCooldownTab = () => {
  const { i18n } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState({
    warming: defaultPhase(),
    cooldown: defaultPhase(),
    ending_message_fa: '',
    ending_message_en: ''
  });

  const getAuthToken = () => localStorage.getItem('token') || '';
  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${getAuthToken()}`, 'Content-Type': 'application/json' }
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`${API_BASE}/api/admin/session-phases`, getAxiosConfig());
        const d = res.data || {};
        setData({
          warming: d.warming && typeof d.warming === 'object'
            ? { title_fa: d.warming.title_fa || '', title_en: d.warming.title_en || '', steps: Array.isArray(d.warming.steps) ? d.warming.steps.map(s => ({ ...defaultStep(), ...s })) : [] }
            : defaultPhase(),
          cooldown: d.cooldown && typeof d.cooldown === 'object'
            ? { title_fa: d.cooldown.title_fa || '', title_en: d.cooldown.title_en || '', steps: Array.isArray(d.cooldown.steps) ? d.cooldown.steps.map(s => ({ ...defaultStep(), ...s })) : [] }
            : defaultPhase(),
          ending_message_fa: d.ending_message_fa || '',
          ending_message_en: d.ending_message_en || ''
        });
      } catch (err) {
        console.error('Error loading session phases:', err);
        setData({ warming: defaultPhase(), cooldown: defaultPhase(), ending_message_fa: '', ending_message_en: '' });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const setWarming = (updater) => setData(prev => ({ ...prev, warming: updater(prev.warming) }));
  const setCooldown = (updater) => setData(prev => ({ ...prev, cooldown: updater(prev.cooldown) }));

  const addStep = (phase) => {
    if (phase === 'warming') setWarming(w => ({ ...w, steps: [...(w.steps || []), defaultStep()] }));
    if (phase === 'cooldown') setCooldown(c => ({ ...c, steps: [...(c.steps || []), defaultStep()] }));
  };

  const removeStep = (phase, index) => {
    if (phase === 'warming') setWarming(w => ({ ...w, steps: (w.steps || []).filter((_, i) => i !== index) }));
    if (phase === 'cooldown') setCooldown(c => ({ ...c, steps: (c.steps || []).filter((_, i) => i !== index) }));
  };

  const updateStep = (phase, index, field, value) => {
    if (phase === 'warming') {
      setWarming(w => {
        const steps = [...(w.steps || [])];
        steps[index] = { ...(steps[index] || defaultStep()), [field]: value };
        return { ...w, steps };
      });
    }
    if (phase === 'cooldown') {
      setCooldown(c => {
        const steps = [...(c.steps || [])];
        steps[index] = { ...(steps[index] || defaultStep()), [field]: value };
        return { ...c, steps };
      });
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_BASE}/api/admin/session-phases`, data, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'ذخیره شد' : 'Saved');
    } catch (err) {
      console.error('Error saving:', err);
      alert(i18n.language === 'fa' ? 'خطا در ذخیره' : 'Error saving');
    } finally {
      setSaving(false);
    }
  };

  const renderPhase = (key, phase, setPhase) => {
    const fa = i18n.language === 'fa';
    const titleLabel = key === 'warming'
      ? (fa ? 'گرم کردن' : 'Warming')
      : (fa ? 'سرد کردن و تنفس' : 'Cooldown & Breathing');
    const steps = phase.steps || [];
    return (
      <section key={key} className="warming-cooldown-phase">
        <h3>{titleLabel}</h3>
        <div className="phase-titles">
          <div className="form-group">
            <label>{fa ? 'عنوان (فارسی)' : 'Title (FA)'}</label>
            <input
              type="text"
              value={phase.title_fa}
              onChange={(e) => setPhase(p => ({ ...p, title_fa: e.target.value }))}
              placeholder={fa ? 'گرم کردن' : 'Warming'}
            />
          </div>
          <div className="form-group">
            <label>{fa ? 'عنوان (انگلیسی)' : 'Title (EN)'}</label>
            <input
              type="text"
              value={phase.title_en}
              onChange={(e) => setPhase(p => ({ ...p, title_en: e.target.value }))}
              placeholder="Warming"
            />
          </div>
        </div>
        <div className="phase-steps">
          <h4>{fa ? 'زیرمراحل' : 'Sub-steps'}</h4>
          {steps.map((step, idx) => (
            <div key={idx} className="step-block">
              <div className="step-row">
                <input
                  type="text"
                  className="step-title-fa"
                  value={step.title_fa}
                  onChange={(e) => updateStep(key, idx, 'title_fa', e.target.value)}
                  placeholder={fa ? 'عنوان مرحله' : 'Step title (FA)'}
                />
                <input
                  type="text"
                  className="step-title-en"
                  value={step.title_en}
                  onChange={(e) => updateStep(key, idx, 'title_en', e.target.value)}
                  placeholder={fa ? 'Step title (EN)' : 'Step title (EN)'}
                />
                <button type="button" className="step-remove" onClick={() => removeStep(key, idx)}>×</button>
              </div>
              <div className="step-bodies">
                <textarea
                  rows={2}
                  value={step.body_fa}
                  onChange={(e) => updateStep(key, idx, 'body_fa', e.target.value)}
                  placeholder={fa ? 'توضیح (فارسی)' : 'Description (FA)'}
                />
                <textarea
                  rows={2}
                  value={step.body_en}
                  onChange={(e) => updateStep(key, idx, 'body_en', e.target.value)}
                  placeholder={fa ? 'Description (EN)' : 'Description (EN)'}
                />
              </div>
            </div>
          ))}
          <button type="button" className="btn-add-step" onClick={() => addStep(key)}>
            {fa ? '+ افزودن زیرمرحله' : '+ Add sub-step'}
          </button>
        </div>
      </section>
    );
  };

  if (loading) {
    return <div className="warming-cooldown-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  const fa = i18n.language === 'fa';
  return (
    <div className="warming-cooldown-tab" dir="ltr">
      <div className="warming-cooldown-header">
        <h2>{fa ? 'گرم کردن و سرد کردن (جلسه تمرین)' : 'Warming & Cooldown (Session Steps)'}</h2>
        <p className="warming-cooldown-desc">
          {fa ? 'محتوای گرم کردن و سرد کردن و تنفس را برای نمایش به اعضا در هر جلسه تمرین تنظیم کنید. زیرمراحل را اضافه کنید.' : 'Set warming and cooldown/breathing content shown to members in each training session. Add sub-steps as needed.'}
        </p>
        <button type="button" className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? (fa ? 'در حال ذخیره...' : 'Saving...') : (fa ? 'ذخیره' : 'Save')}
        </button>
      </div>
      <div className="warming-cooldown-form">
        {renderPhase('warming', data.warming, setWarming)}
        {renderPhase('cooldown', data.cooldown, setCooldown)}
        <section className="warming-cooldown-phase">
          <h3>{fa ? 'پیام پایانی (تشویق عضو)' : 'Ending message (encourage member)'}</h3>
          <div className="form-group">
            <label>{fa ? 'متن (فارسی)' : 'Text (FA)'}</label>
            <textarea
              rows={3}
              value={data.ending_message_fa}
              onChange={(e) => setData(prev => ({ ...prev, ending_message_fa: e.target.value }))}
              placeholder={fa ? 'عالی بود! ادامه بده.' : 'Great job! Keep it up.'}
            />
          </div>
          <div className="form-group">
            <label>{fa ? 'متن (انگلیسی)' : 'Text (EN)'}</label>
            <textarea
              rows={3}
              value={data.ending_message_en}
              onChange={(e) => setData(prev => ({ ...prev, ending_message_en: e.target.value }))}
              placeholder="Great job! Keep it up."
            />
          </div>
        </section>
        <div className="form-actions">
          <button type="button" className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? (fa ? 'در حال ذخیره...' : 'Saving...') : (fa ? 'ذخیره' : 'Save')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WarmingCooldownTab;
