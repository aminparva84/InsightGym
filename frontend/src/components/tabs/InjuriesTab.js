import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './InjuriesTab.css';

const InjuriesTab = () => {
  const { t, i18n } = useTranslation();
  const [injuries, setInjuries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedInjury, setSelectedInjury] = useState(null);

  useEffect(() => {
    loadInjuries();
  }, [i18n.language]);

  const loadInjuries = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/api/injuries?language=${i18n.language}`);
      setInjuries(response.data);
    } catch (error) {
      console.error('Error loading injuries:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">{t('loading')}...</div>;
  }

  return (
    <div className="injuries-tab">
      <h2>{t('injuries')}</h2>
      {injuries.length === 0 ? (
        <p className="no-data">{t('noInjuries')}</p>
      ) : (
        <div className="injuries-container">
          <div className="injuries-list">
            {injuries.map(injury => (
              <div
                key={injury.id}
                className={`injury-item ${selectedInjury?.id === injury.id ? 'active' : ''}`}
                onClick={() => setSelectedInjury(injury)}
              >
                <h3>{injury.title}</h3>
                <p className="injury-preview">
                  {injury.description.substring(0, 100)}...
                </p>
              </div>
            ))}
          </div>
          {selectedInjury && (
            <div className="injury-details">
              <h3>{selectedInjury.title}</h3>
              <div className="detail-section">
                <h4>{i18n.language === 'fa' ? 'توضیحات' : 'Description'}</h4>
                <p>{selectedInjury.description}</p>
              </div>
              {selectedInjury.prevention && (
                <div className="detail-section">
                  <h4>{i18n.language === 'fa' ? 'پیشگیری' : 'Prevention'}</h4>
                  <p>{selectedInjury.prevention}</p>
                </div>
              )}
              {selectedInjury.treatment && (
                <div className="detail-section">
                  <h4>{i18n.language === 'fa' ? 'درمان' : 'Treatment'}</h4>
                  <p>{selectedInjury.treatment}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InjuriesTab;



