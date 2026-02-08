import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './AISettingsTab.css';

const API_BASE = getApiBase();

const PROVIDER_IDS = ['openai', 'anthropic', 'gemini', 'vertex'];
const PROVIDER_NAMES = { auto: 'Auto', openai: 'OpenAI', anthropic: 'Anthropic', gemini: 'Gemini', vertex: 'Vertex AI' };
const PROVIDER_NAMES_FA = { auto: 'خودکار', openai: 'اوپن‌ای‌آی', anthropic: 'آنتروپیک', gemini: 'جمینی', vertex: 'ورتکس' };

const AISettingsTab = () => {
  const { i18n } = useTranslation();
  const fa = i18n.language === 'fa';
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(null);
  const [settings, setSettings] = useState({ selected_provider: 'openai', providers: {} });
  const [keys, setKeys] = useState({ openai: '', anthropic: '', gemini: '', vertex: '' });
  const [kbStatus, setKbStatus] = useState(null);
  const [kbContent, setKbContent] = useState('');
  const [kbLoading, setKbLoading] = useState(false);
  const [kbSaving, setKbSaving] = useState(false);
  const [kbIndexing, setKbIndexing] = useState(false);

  const getAuthToken = useCallback(() => {
    const t = localStorage.getItem('token');
    return t && t.trim() ? t.trim() : null;
  }, []);
  const getAxiosConfig = useCallback(() => ({
    headers: {
      Authorization: `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    },
  }), [getAuthToken]);

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/api/admin/ai-settings`, getAxiosConfig());
      setSettings(res.data || { selected_provider: 'auto', providers: {} });
      setKeys({ openai: '', anthropic: '', gemini: '', vertex: '' });
    } catch (err) {
      console.error('Error fetching AI settings:', err);
      setSettings({ selected_provider: 'auto', providers: {} });
    } finally {
      setLoading(false);
    }
  }, [getAxiosConfig]);

  const fetchKbStatus = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/admin/website-kb/status`, getAxiosConfig());
      setKbStatus(res.data || null);
    } catch (err) {
      setKbStatus(null);
    }
  }, [getAxiosConfig]);

  const fetchKbSource = useCallback(async () => {
    try {
      setKbLoading(true);
      const res = await axios.get(`${API_BASE}/api/admin/website-kb/source`, getAxiosConfig());
      setKbContent(res.data?.content || '');
    } catch (err) {
      setKbContent('');
    } finally {
      setKbLoading(false);
    }
  }, [getAxiosConfig]);

  useEffect(() => {
    fetchSettings();
    fetchKbStatus();
    fetchKbSource();
  }, [fetchSettings, fetchKbStatus, fetchKbSource]);

  const handleSaveKey = async (provider) => {
    const key = (keys[provider] || '').trim();
    try {
      setSaving(true);
      await axios.put(
        `${API_BASE}/api/admin/ai-settings`,
        {
          [provider]: { api_key: key || null },
        },
        getAxiosConfig()
      );
      if (fa) alert('ذخیره شد');
      else alert('Saved');
      setKeys((p) => ({ ...p, [provider]: '' }));
      await fetchSettings();
    } catch (err) {
      console.error('Error saving AI settings:', err);
      if (fa) alert('خطا در ذخیره');
      else alert('Error saving');
    } finally {
      setSaving(false);
    }
  };

  const handleSelectProvider = async (provider) => {
    try {
      setSaving(true);
      await axios.put(
        `${API_BASE}/api/admin/ai-settings`,
        { selected_provider: provider },
        getAxiosConfig()
      );
      if (fa) alert('ارائه‌دهنده AI ذخیره شد');
      else alert('AI provider saved');
      setSettings((s) => ({ ...s, selected_provider: provider }));
    } catch (err) {
      console.error('Error updating selected provider:', err);
      if (fa) alert('خطا در ذخیره');
      else alert('Error saving');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async (provider, useFormKey = false) => {
    setTesting(provider);
    try {
      const body = useFormKey && keys[provider] ? { provider, api_key: keys[provider].trim() } : { provider };
      const res = await axios.post(`${API_BASE}/api/admin/ai-settings/test`, body, getAxiosConfig());
      const ok = res.data && res.data.success;
      if (fa) alert(ok ? 'کلید API معتبر است.' : (res.data?.message || 'خطا در تست'));
      else alert(ok ? 'API key is valid.' : (res.data?.message || 'Test failed'));
      await fetchSettings();
    } catch (err) {
      if (fa) alert('خطا: ' + (err.response?.data?.message || err.message));
      else alert('Error: ' + (err.response?.data?.message || err.message));
    } finally {
      setTesting(null);
    }
  };

  const handleSaveKbSource = async () => {
    try {
      setKbSaving(true);
      await axios.put(
        `${API_BASE}/api/admin/website-kb/source`,
        { content: kbContent },
        getAxiosConfig()
      );
      if (fa) alert('محتوا ذخیره شد');
      else alert('KB content saved');
      fetchKbStatus();
    } catch (err) {
      if (fa) alert('خطا در ذخیره محتوا');
      else alert('Error saving KB content');
    } finally {
      setKbSaving(false);
    }
  };

  const handleReindexKb = async () => {
    try {
      setKbIndexing(true);
      await axios.post(`${API_BASE}/api/admin/website-kb/reindex`, {}, getAxiosConfig());
      if (fa) alert('ایندکس KB به‌روزرسانی شد');
      else alert('KB reindexed');
      fetchKbStatus();
    } catch (err) {
      if (fa) alert('خطا در ایندکس KB');
      else alert('Error reindexing KB');
    } finally {
      setKbIndexing(false);
    }
  };

  const providers = settings.providers || {};
  const validProviders = PROVIDER_IDS.filter(
    (p) => providers[p]?.sdk_installed && providers[p]?.has_key && providers[p]?.is_valid
  );
  const displayValue = ['auto', ...validProviders].includes(settings.selected_provider)
    ? settings.selected_provider
    : 'auto';

  if (loading) {
    return (
      <div className="ai-settings-tab">
        <p className="ai-settings-loading">{fa ? 'در حال بارگذاری...' : 'Loading...'}</p>
      </div>
    );
  }

  return (
    <div className="ai-settings-tab">
      <h2>{fa ? 'تنظیمات AI' : 'AI Settings'}</h2>
      <p className="ai-settings-desc">
        {fa
          ? 'ارائه‌دهنده AI برای چت و تولید متن را انتخاب کنید. برای هر ارائه‌دهنده کلید API را وارد کرده و تست کنید.'
          : 'Choose which AI provider to use for chat and text generation. Enter API key for each provider and test.'}
      </p>
      <p className="ai-settings-desc">
        {fa
          ? 'برای Vertex AI می‌توانید از کلید Gemini استفاده کنید.'
          : 'For Vertex AI, you can use your Gemini API key.'}
      </p>

      <div className="ai-settings-selected">
        <label>{fa ? 'ارائه‌دهنده فعلی' : 'Current provider'}</label>
        <select
          value={displayValue}
          onChange={(e) => handleSelectProvider(e.target.value)}
          disabled={saving}
        >
          <option value="auto">{fa ? 'خودکار (اولین معتبر)' : 'Auto (first valid)'}</option>
          {validProviders.length === 0 ? (
            <option value="openai" disabled>{fa ? 'هیچ ارائه‌دهنده معتبری نیست' : 'No valid provider'}</option>
          ) : (
            validProviders.map((p) => (
              <option key={p} value={p}>
                {fa ? PROVIDER_NAMES_FA[p] : PROVIDER_NAMES[p]}
              </option>
            ))
          )}
        </select>
        {validProviders.length === 0 && (
          <p className="ai-settings-warn">
            {fa ? 'حداقل یک ارائه‌دهنده را با کلید معتبر پیکربندی و تست کنید.' : 'Configure and test at least one provider with a valid key.'}
          </p>
        )}
      </div>

      <div className="ai-settings-table-wrap">
        <table className="ai-settings-table">
          <thead>
            <tr>
              <th>{fa ? 'ارائه‌دهنده' : 'Provider'}</th>
              <th>{fa ? 'نصب SDK' : 'SDK installed'}</th>
              <th>{fa ? 'کلید API' : 'API key'}</th>
              <th>{fa ? 'منبع' : 'Source'}</th>
              <th>{fa ? 'معتبر' : 'Valid'}</th>
              <th>{fa ? 'آخرین تست' : 'Last test'}</th>
              <th>{fa ? 'کلید API / اقدامات' : 'API key / Actions'}</th>
            </tr>
          </thead>
          <tbody>
            {PROVIDER_IDS.map((id) => {
              const p = providers[id] || {};
              const name = fa ? PROVIDER_NAMES_FA[id] : PROVIDER_NAMES[id];
              const canUse = p.sdk_installed && p.has_key && p.is_valid;
              return (
                <tr key={id} className={canUse ? 'valid' : ''}>
                  <td className="ai-settings-cell-name">{name}</td>
                  <td>{p.sdk_installed ? (fa ? 'بله' : 'Yes') : (fa ? 'خیر' : 'No')}</td>
                  <td>{p.has_key ? (fa ? 'وارد شده' : 'Set') : (fa ? 'وارد نشده' : 'Not set')}</td>
                  <td>{p.source || '—'}</td>
                  <td>{p.is_valid ? (fa ? 'بله' : 'Yes') : (fa ? 'خیر' : 'No')}</td>
                  <td>{p.last_tested_at ? new Date(p.last_tested_at).toLocaleString() : '—'}</td>
                  <td>
                    <div className="ai-settings-cell-actions">
                      <input
                        type="password"
                        placeholder={fa ? 'کلید API' : 'API key'}
                        value={keys[id] || ''}
                        onChange={(e) => setKeys((k) => ({ ...k, [id]: e.target.value }))}
                        className="ai-settings-key-input"
                      />
                      <button
                        type="button"
                        className="ai-settings-btn ai-settings-btn-save"
                        onClick={() => handleSaveKey(id)}
                        disabled={saving}
                      >
                        {fa ? 'ذخیره' : 'Save'}
                      </button>
                      <button
                        type="button"
                        className="ai-settings-btn ai-settings-btn-test"
                        onClick={() => handleTest(id, true)}
                        disabled={testing !== null}
                      >
                        {testing === id ? '…' : fa ? 'تست' : 'Test'}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="ai-kb-section">
        <h3>{fa ? 'پایگاه دانش سایت (KB)' : 'Website Knowledge Base (KB)'}</h3>
        <p className="ai-settings-desc">
          {fa
            ? 'محتوای دانش سایت را ویرایش کنید و سپس ایندکس را به‌روزرسانی نمایید.'
            : 'Edit the website KB content and then reindex to update embeddings.'}
        </p>
        <div className="ai-kb-meta">
          <span>
            {fa ? 'تعداد بخش‌ها:' : 'Chunks:'} {kbStatus?.count ?? 0}
          </span>
          <span>
            {fa ? 'آخرین بروزرسانی:' : 'Last updated:'} {kbStatus?.updated_at ? new Date(kbStatus.updated_at).toLocaleString() : '—'}
          </span>
        </div>
        <textarea
          className="ai-kb-textarea"
          rows={10}
          value={kbContent}
          onChange={(e) => setKbContent(e.target.value)}
          placeholder={fa ? 'محتوای KB را اینجا وارد کنید...' : 'Enter KB content here...'}
          disabled={kbLoading}
        />
        <div className="ai-kb-actions">
          <button
            type="button"
            className="ai-settings-btn ai-settings-btn-save"
            onClick={handleSaveKbSource}
            disabled={kbSaving || kbLoading}
          >
            {kbSaving ? (fa ? 'در حال ذخیره...' : 'Saving...') : (fa ? 'ذخیره' : 'Save')}
          </button>
          <button
            type="button"
            className="ai-settings-btn ai-settings-btn-test"
            onClick={handleReindexKb}
            disabled={kbIndexing || kbLoading}
          >
            {kbIndexing ? (fa ? 'در حال ایندکس...' : 'Indexing...') : (fa ? 'به‌روزرسانی ایندکس' : 'Reindex')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AISettingsTab;
