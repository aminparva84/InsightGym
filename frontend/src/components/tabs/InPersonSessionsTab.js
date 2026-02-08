import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import './InPersonSessionsTab.css';

const InPersonSessionsTab = () => {
  const { i18n } = useTranslation();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = useCallback(async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API endpoint when available
      // const response = await axios.get('http://localhost:5000/api/sessions', getAxiosConfig());
      // setSessions(response.data);
      setSessions([]); // Placeholder
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return (
    <div className="in-person-sessions-tab" dir="ltr">
      <div className="sessions-header">
        <h2>{i18n.language === 'fa' ? 'تاریخچه جلسات حضوری' : 'In-Person Sessions History'}</h2>
      </div>

      {loading ? (
        <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
      ) : sessions.length === 0 ? (
        <div className="no-sessions">
          <p>{i18n.language === 'fa' ? 'هیچ جلسه حضوری ثبت نشده است' : 'No in-person sessions recorded yet'}</p>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map(session => (
            <div key={session.id} className="session-card">
              <div className="session-date">
                {new Date(session.date).toLocaleDateString(i18n.language === 'fa' ? 'fa-IR' : 'en-US')}
              </div>
              <div className="session-details">
                <h3>{session.member_name}</h3>
                <p>{session.notes || '-'}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InPersonSessionsTab;



