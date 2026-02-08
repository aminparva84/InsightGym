import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './TipsTab.css';

const TipsTab = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTips();
  }, [i18n.language]);

  const loadTips = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/tips?language=${i18n.language}`);
      setTips(response.data);
    } catch (error) {
      console.error('Error loading tips:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">{t('loading')}...</div>;
  }

  return (
    <div className="tips-tab">
      <h2>{t('tips')}</h2>
      {tips.length === 0 ? (
        <p className="no-data">{t('noTips')}</p>
      ) : (
        <div className="tips-list">
          {tips.map(tip => (
            <div key={tip.id} className="tip-card">
              <div className="tip-header">
                <h3>{tip.title}</h3>
                {tip.category && (
                  <span className="tip-category">{tip.category}</span>
                )}
              </div>
              <div className="tip-content">
                {tip.content}
              </div>
              {tip.created_at && (
                <div className="tip-date">
                  {new Date(tip.created_at).toLocaleDateString(i18n.language === 'fa' ? 'fa-IR' : 'en-US')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TipsTab;



