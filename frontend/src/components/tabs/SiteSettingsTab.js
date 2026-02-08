import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './SiteSettingsTab.css';

const API_BASE = getApiBase();

const SiteSettingsTab = () => {
  const { i18n } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    contact_email: '',
    contact_phone: '',
    address_fa: '',
    address_en: '',
    app_description_fa: '',
    app_description_en: '',
    instagram_url: '',
    telegram_url: '',
    whatsapp_url: '',
    twitter_url: '',
    facebook_url: '',
    linkedin_url: '',
    youtube_url: '',
    copyright_text: ''
  });

  const getAuthToken = useCallback(() => {
    const t = localStorage.getItem('token');
    return t && t.trim() ? t.trim() : null;
  }, []);
  const getAxiosConfig = useCallback(() => ({
    headers: {
      Authorization: `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    }
  }), [getAuthToken]);

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/admin/site-settings`, getAxiosConfig());
      setFormData({
        contact_email: response.data.contact_email || '',
        contact_phone: response.data.contact_phone || '',
        address_fa: response.data.address_fa || '',
        address_en: response.data.address_en || '',
        app_description_fa: response.data.app_description_fa || '',
        app_description_en: response.data.app_description_en || '',
        instagram_url: response.data.instagram_url || '',
        telegram_url: response.data.telegram_url || '',
        whatsapp_url: response.data.whatsapp_url || '',
        twitter_url: response.data.twitter_url || '',
        facebook_url: response.data.facebook_url || '',
        linkedin_url: response.data.linkedin_url || '',
        youtube_url: response.data.youtube_url || '',
        copyright_text: response.data.copyright_text || ''
      });
    } catch (error) {
      console.error('Error fetching site settings:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت تنظیمات سایت' : 'Error fetching site settings');
    } finally {
      setLoading(false);
    }
  }, [getAxiosConfig, i18n.language]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_BASE}/api/admin/site-settings`, formData, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'تنظیمات سایت ذخیره شد' : 'Site settings saved');
    } catch (error) {
      console.error('Error saving site settings:', error);
      alert(i18n.language === 'fa'
        ? `خطا در ذخیره: ${error.response?.data?.error || error.message}`
        : `Error saving: ${error.response?.data?.error || error.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="site-settings-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  return (
    <div className="site-settings-tab" dir="ltr">
      <div className="site-settings-header">
        <h2>{i18n.language === 'fa' ? 'تنظیمات سایت و فوتر' : 'Website & Footer Settings'}</h2>
        <button type="button" className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? (i18n.language === 'fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language === 'fa' ? 'ذخیره' : 'Save')}
        </button>
      </div>

      <div className="site-settings-form">
        <section className="site-settings-section">
          <h3>{i18n.language === 'fa' ? 'اطلاعات تماس' : 'Contact Info'}</h3>
          <div className="form-row">
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'ایمیل تماس' : 'Contact Email'}</label>
              <input
                type="email"
                value={formData.contact_email}
                onChange={(e) => handleChange('contact_email', e.target.value)}
                placeholder="info@example.com"
              />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'شماره تماس' : 'Contact Phone'}</label>
              <input
                type="text"
                value={formData.contact_phone}
                onChange={(e) => handleChange('contact_phone', e.target.value)}
                placeholder="+98 21 1234 5678"
              />
            </div>
          </div>
          <div className="form-group">
            <label>{i18n.language === 'fa' ? 'آدرس (فارسی)' : 'Address (FA)'}</label>
            <input
              type="text"
              value={formData.address_fa}
              onChange={(e) => handleChange('address_fa', e.target.value)}
              placeholder={i18n.language === 'fa' ? 'تهران، خیابان...' : 'Tehran, ...'}
            />
          </div>
          <div className="form-group">
            <label>{i18n.language === 'fa' ? 'آدرس (انگلیسی)' : 'Address (EN)'}</label>
            <input
              type="text"
              value={formData.address_en}
              onChange={(e) => handleChange('address_en', e.target.value)}
              placeholder="Tehran, ..."
            />
          </div>
        </section>

        <section className="site-settings-section">
          <h3>{i18n.language === 'fa' ? 'توضیحات اپ (فوتر)' : 'App Description (Footer)'}</h3>
          <div className="form-group">
            <label>{i18n.language === 'fa' ? 'توضیحات (فارسی)' : 'Description (FA)'}</label>
            <textarea
              value={formData.app_description_fa}
              onChange={(e) => handleChange('app_description_fa', e.target.value)}
              rows="2"
              placeholder={i18n.language === 'fa' ? 'پلتفرم جامع تناسب اندام با هوش مصنوعی' : 'Comprehensive fitness platform powered by AI'}
            />
          </div>
          <div className="form-group">
            <label>{i18n.language === 'fa' ? 'توضیحات (انگلیسی)' : 'Description (EN)'}</label>
            <textarea
              value={formData.app_description_en}
              onChange={(e) => handleChange('app_description_en', e.target.value)}
              rows="2"
              placeholder="Comprehensive fitness platform powered by AI"
            />
          </div>
        </section>

        <section className="site-settings-section">
          <h3>{i18n.language === 'fa' ? 'شبکه‌های اجتماعی' : 'Social Media'}</h3>
          <p className="section-hint">{i18n.language === 'fa' ? 'لینک کامل صفحه (مثال: https://instagram.com/...) را وارد کنید.' : 'Enter full profile URL (e.g. https://instagram.com/...).'}</p>
          <div className="form-row">
            <div className="form-group">
              <label>Instagram</label>
              <input
                type="url"
                value={formData.instagram_url}
                onChange={(e) => handleChange('instagram_url', e.target.value)}
                placeholder="https://instagram.com/..."
              />
            </div>
            <div className="form-group">
              <label>Telegram</label>
              <input
                type="url"
                value={formData.telegram_url}
                onChange={(e) => handleChange('telegram_url', e.target.value)}
                placeholder="https://t.me/..."
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>WhatsApp</label>
              <input
                type="url"
                value={formData.whatsapp_url}
                onChange={(e) => handleChange('whatsapp_url', e.target.value)}
                placeholder="https://wa.me/..."
              />
            </div>
            <div className="form-group">
              <label>Twitter / X</label>
              <input
                type="url"
                value={formData.twitter_url}
                onChange={(e) => handleChange('twitter_url', e.target.value)}
                placeholder="https://twitter.com/..."
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Facebook</label>
              <input
                type="url"
                value={formData.facebook_url}
                onChange={(e) => handleChange('facebook_url', e.target.value)}
                placeholder="https://facebook.com/..."
              />
            </div>
            <div className="form-group">
              <label>LinkedIn</label>
              <input
                type="url"
                value={formData.linkedin_url}
                onChange={(e) => handleChange('linkedin_url', e.target.value)}
                placeholder="https://linkedin.com/..."
              />
            </div>
          </div>
          <div className="form-group">
            <label>YouTube</label>
            <input
              type="url"
              value={formData.youtube_url}
              onChange={(e) => handleChange('youtube_url', e.target.value)}
              placeholder="https://youtube.com/..."
            />
          </div>
        </section>

        <section className="site-settings-section">
          <h3>{i18n.language === 'fa' ? 'کپی‌رایت' : 'Copyright'}</h3>
          <div className="form-group">
            <label>{i18n.language === 'fa' ? 'متن کپی‌رایت (اختیاری)' : 'Copyright text (optional)'}</label>
            <input
              type="text"
              value={formData.copyright_text}
              onChange={(e) => handleChange('copyright_text', e.target.value)}
              placeholder={i18n.language === 'fa' ? 'تمامی حقوق محفوظ است' : 'All rights reserved'}
            />
          </div>
        </section>

        <div className="form-actions">
          <button type="button" className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? (i18n.language === 'fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language === 'fa' ? 'ذخیره تنظیمات' : 'Save Settings')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SiteSettingsTab;
