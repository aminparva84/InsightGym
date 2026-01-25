import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import ProgressTrend from './ProgressTrend';
import './HistoryTab.css';

const HistoryTab = ({ showOnlyMessages = false }) => {
  const { t, i18n } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const [exercises, setExercises] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [activeView, setActiveView] = useState(showOnlyMessages ? 'chat' : 'exercises');
  const [loading, setLoading] = useState(true);

  // Get auth token
  const getAuthToken = () => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  useEffect(() => {
    if (!authLoading && user) {
      loadData();
    } else if (!authLoading && !user) {
      setLoading(false);
    }
  }, [authLoading, user]);

  const loadData = async () => {
    const token = getAuthToken();
    if (!token) {
      console.warn('No token found for loading history');
      setLoading(false);
      return;
    }

    try {
      const [exercisesRes, chatRes] = await Promise.all([
        axios.get('http://localhost:5000/api/exercises', getAxiosConfig()),
        axios.get('http://localhost:5000/api/chat/history', getAxiosConfig())
      ]);
      setExercises(exercisesRes.data);
      setChatHistory(chatRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      if (error.response?.status === 401 || error.response?.status === 422) {
        console.warn('Authentication error loading history');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">{t('loading')}...</div>;
  }

  return (
    <div className="history-tab">
      {!showOnlyMessages && (
        <div className="history-tabs">
          <button
            type="button"
            className={`history-tab-btn ${activeView === 'exercises' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setActiveView('exercises');
            }}
          >
            {t('exerciseHistory')}
          </button>
          <button
            type="button"
            className={`history-tab-btn ${activeView === 'chat' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setActiveView('chat');
            }}
          >
            {t('chatHistory')}
          </button>
          <button
            type="button"
            className={`history-tab-btn ${activeView === 'progress' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setActiveView('progress');
            }}
          >
            {i18n.language === 'fa' ? 'روند تغییرات' : 'Progress Trend'}
          </button>
        </div>
      )}

      {activeView === 'exercises' && (
        <div className="history-content">
          <h2>{t('exerciseHistory')}</h2>
          {exercises.length === 0 ? (
            <p className="no-data">{t('noExercises')}</p>
          ) : (
            <div className="table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>{t('date')}</th>
                    <th>{t('exerciseName')}</th>
                    <th>{t('exerciseType')}</th>
                    <th>{t('duration')}</th>
                    <th>{t('caloriesBurned')}</th>
                    <th>{t('notes')}</th>
                  </tr>
                </thead>
                <tbody>
                  {exercises.map(ex => (
                    <tr key={ex.id}>
                      <td>{new Date(ex.date).toLocaleDateString(i18n.language === 'fa' ? 'fa-IR' : 'en-US')}</td>
                      <td>{ex.exercise_name}</td>
                      <td>{ex.exercise_type || '-'}</td>
                      <td>{ex.duration || '-'}</td>
                      <td>{ex.calories_burned || '-'}</td>
                      <td>{ex.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeView === 'chat' && (
        <div className="history-content">
          <h2>{t('chatHistory')}</h2>
          {chatHistory.length === 0 ? (
            <p className="no-data">{t('noHistory')}</p>
          ) : (
            <div className="chat-history-list">
              {chatHistory.map(chat => (
                <div key={chat.id} className="chat-history-item">
                  <div className="chat-message">
                    <strong>{i18n.language === 'fa' ? 'شما:' : 'You:'}</strong> {chat.message}
                  </div>
                  <div className="chat-response">
                    <strong>{i18n.language === 'fa' ? 'دستیار:' : 'Assistant:'}</strong> {chat.response}
                  </div>
                  <div className="chat-timestamp">
                    {new Date(chat.timestamp).toLocaleString(i18n.language === 'fa' ? 'fa-IR' : 'en-US')}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeView === 'progress' && (
        <ProgressTrend />
      )}
    </div>
  );
};

export default HistoryTab;

