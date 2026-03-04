import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import './ContactPage.css';

const ContactPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const API_BASE = getApiBase();
  const [siteSettings, setSiteSettings] = useState(null);

  useEffect(() => {
    const fetchSiteSettings = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/site-settings`);
        setSiteSettings(response.data || {});
      } catch (error) {
        console.error('Error fetching site settings:', error);
        setSiteSettings({});
      }
    };
    fetchSiteSettings();
  }, [API_BASE]);

  const email = siteSettings?.contact_email?.trim() || 'info@insightgym.com';
  const phone = siteSettings?.contact_phone?.trim() || (i18n.language === 'fa' ? '+98 123 456 7890' : '+1 (234) 567-890');
  const address = i18n.language === 'fa' ? siteSettings?.address_fa?.trim() : siteSettings?.address_en?.trim();

  return (
    <div className="contact-page">
      <div className="contact-container">
        <h1 className="contact-title">{t('contactUs')}</h1>
        <div className="contact-content">
          <a href={`mailto:${email}`} className="contact-link">{email}</a>
          <a href={`tel:${phone.replace(/\s/g, '')}`} className="contact-link">{phone}</a>
          {address && <p className="contact-address">{address}</p>}
        </div>
        <button className="contact-back-btn" onClick={() => navigate('/')}>
          {i18n.language === 'fa' ? 'بازگشت' : 'Back'}
        </button>
      </div>
    </div>
  );
};

export default ContactPage;
