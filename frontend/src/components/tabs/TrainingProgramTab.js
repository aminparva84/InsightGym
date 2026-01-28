import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import './TrainingProgramTab.css';

const TrainingProgramTab = () => {
  const { t, i18n } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const [programs, setPrograms] = useState([]);
  const [weeklyGoals, setWeeklyGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedSessions, setExpandedSessions] = useState(new Set());
  const [goalUpdating, setGoalUpdating] = useState(new Set());

  const getAuthToken = () => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  useEffect(() => {
    if (!authLoading && user) {
      loadPrograms();
      loadWeeklyGoals();
    } else if (!authLoading && !user) {
      setLoading(false);
    }
  }, [authLoading, user]);

  const loadWeeklyGoals = async () => {
    const token = getAuthToken();
    if (!token) return;
    try {
      const config = getAxiosConfig();
      const response = await axios.get('http://localhost:5000/api/member/weekly-goals?language=' + (i18n.language || 'fa'), config);
      setWeeklyGoals(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Error loading weekly goals:', err);
      setWeeklyGoals([]);
    }
  };

  const toggleGoalComplete = async (goalId, currentCompleted) => {
    setGoalUpdating(prev => new Set(prev).add(goalId));
    try {
      const config = getAxiosConfig();
      await axios.patch('http://localhost:5000/api/member/weekly-goals/' + goalId, { completed: !currentCompleted }, { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } });
      setWeeklyGoals(prev => prev.map(g => g.id === goalId ? { ...g, completed: !currentCompleted, completed_at: !currentCompleted ? new Date().toISOString() : null } : g));
    } catch (err) {
      console.error('Error updating goal:', err);
    } finally {
      setGoalUpdating(prev => { const s = new Set(prev); s.delete(goalId); return s; });
    }
  };

  const loadPrograms = async () => {
    const token = getAuthToken();
    if (!token) {
      console.warn('No token found for loading training programs');
      setLoading(false);
      return;
    }

    try {
      console.log('Loading training programs...');
      const config = getAxiosConfig();
      console.log('Request config:', { hasAuth: !!config.headers?.Authorization });
      const response = await axios.get('http://localhost:5000/api/training-programs', config);
      console.log('Training programs response status:', response.status);
      console.log('Training programs response data:', response.data);
      console.log('Number of programs:', response.data?.length || 0);
      if (response.data && Array.isArray(response.data)) {
        setPrograms(response.data);
      } else {
        console.warn('Response data is not an array:', response.data);
        setPrograms([]);
      }
    } catch (error) {
      console.error('Error loading training programs:', error);
      console.error('Error message:', error.message);
      console.error('Error response status:', error.response?.status);
      console.error('Error response data:', error.response?.data);
      if (error.response?.status === 401 || error.response?.status === 422) {
        console.warn('Authentication error loading training programs');
      }
      setPrograms([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSession = (programId, sessionIdx) => {
    const sessionKey = `${programId}-${sessionIdx}`;
    setExpandedSessions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sessionKey)) {
        newSet.delete(sessionKey);
      } else {
        newSet.add(sessionKey);
      }
      return newSet;
    });
  };

  const isSessionExpanded = (programId, sessionIdx) => {
    return expandedSessions.has(`${programId}-${sessionIdx}`);
  };

  if (loading) {
    return <div className="training-program-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  return (
    <div className="training-program-tab" dir="ltr">
      <div className="training-program-header">
        <h2>{i18n.language === 'fa' ? 'برنامه تمرینی' : 'Training Program'}</h2>
      </div>

      <div className="training-program-content">
        {weeklyGoals.length > 0 && (
          <div className="weekly-goals-section">
            <h3>{i18n.language === 'fa' ? 'اهداف هفتگی' : 'Weekly Goals'}</h3>
            <p className="weekly-goals-desc">{i18n.language === 'fa' ? 'اهداف کوچک هر هفته برنامه خود را علامت بزنید.' : 'Check off your mini goals for each week.'}</p>
            <ul className="weekly-goals-list">
              {weeklyGoals.map((goal) => (
                <li key={goal.id} className={`weekly-goal-item ${goal.completed ? 'completed' : ''}`}>
                  <button
                    type="button"
                    className="weekly-goal-check"
                    onClick={() => !goalUpdating.has(goal.id) && toggleGoalComplete(goal.id, goal.completed)}
                    disabled={goalUpdating.has(goal.id)}
                    aria-label={goal.completed ? (i18n.language === 'fa' ? 'علامت انجام' : 'Mark incomplete') : (i18n.language === 'fa' ? 'انجام شد' : 'Mark complete')}
                  >
                    {goalUpdating.has(goal.id) ? '…' : (goal.completed ? '✓' : '○')}
                  </button>
                  <div className="weekly-goal-body">
                    <span className="weekly-goal-title">{goal.goal_title}</span>
                    {goal.training_program_name && (
                      <span className="weekly-goal-program">{goal.training_program_name}</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
        {programs.length === 0 ? (
          <div className="no-programs">
            <p>{i18n.language === 'fa' ? 'هنوز برنامه تمرینی برای شما ایجاد نشده است.' : 'No training program has been created for you yet.'}</p>
            <p>{i18n.language === 'fa' ? 'لطفاً با مربی خود تماس بگیرید یا از چت با AI استفاده کنید.' : 'Please contact your trainer or use the AI chat.'}</p>
          </div>
        ) : (
          <div className="programs-list">
            {programs.map((program, index) => (
              <div key={program.id || index} className="program-card">
                <h3>{program.name || program.name_fa || program.name_en || (i18n.language === 'fa' ? 'برنامه تمرینی' : 'Training Program')}</h3>
                {(program.description || program.description_fa || program.description_en) && (
                  <p className="program-description">
                    {program.description || (i18n.language === 'fa' ? program.description_fa : program.description_en)}
                  </p>
                )}
                {program.duration_weeks && (
                  <p className="program-duration">
                    {i18n.language === 'fa' ? 'مدت زمان' : 'Duration'}: {program.duration_weeks} {i18n.language === 'fa' ? 'هفته (یک ماه)' : 'weeks (1 month)'}
                  </p>
                )}
                {program.training_level && (
                  <p className="program-level">
                    {i18n.language === 'fa' ? 'سطح' : 'Level'}: {
                      program.training_level === 'beginner' ? (i18n.language === 'fa' ? 'مبتدی' : 'Beginner') :
                      program.training_level === 'intermediate' ? (i18n.language === 'fa' ? 'متوسط' : 'Intermediate') :
                      program.training_level === 'advanced' ? (i18n.language === 'fa' ? 'پیشرفته' : 'Advanced') :
                      program.training_level
                    }
                  </p>
                )}
                {program.sessions && program.sessions.length > 0 && (
                  <div className="program-sessions">
                    <h4>{i18n.language === 'fa' ? 'جلسات تمرینی' : 'Training Sessions'}:</h4>
                    <div className="sessions-list">
                      {program.sessions.map((session, sessionIdx) => {
                        const sessionKey = `${program.id || index}-${sessionIdx}`;
                        const isExpanded = isSessionExpanded(program.id || index, sessionIdx);
                        return (
                          <div 
                            key={sessionIdx} 
                            className={`session-card ${isExpanded ? 'expanded' : ''}`}
                            dir="ltr"
                          >
                            <div 
                              className="session-header" 
                              onClick={() => toggleSession(program.id || index, sessionIdx)}
                            >
                              <div className="session-header-content">
                                <h5>{session.name || (i18n.language === 'fa' ? session.name_fa : session.name_en) || `${i18n.language === 'fa' ? 'جلسه' : 'Session'} ${sessionIdx + 1}`}</h5>
                                {session.week && session.day && (
                                  <p className="session-info">
                                    {i18n.language === 'fa' ? 'هفته' : 'Week'} {session.week}, {i18n.language === 'fa' ? 'روز' : 'Day'} {session.day}
                                  </p>
                                )}
                              </div>
                              <span className={`session-toggle-icon ${isExpanded ? 'expanded' : ''}`}>
                                {i18n.language === 'fa' ? (isExpanded ? '▼' : '◄') : (isExpanded ? '▼' : '▶')}
                              </span>
                            </div>
                            {isExpanded && session.exercises && session.exercises.length > 0 && (
                              <div className="session-exercises">
                                <h6>{i18n.language === 'fa' ? 'تمرینات' : 'Exercises'}:</h6>
                                <ul>
                                  {session.exercises.map((exercise, exIdx) => (
                                    <li key={exIdx} className="exercise-item">
                                      <strong>{exercise.name || (i18n.language === 'fa' ? exercise.name_fa : exercise.name_en)}</strong>
                                      {exercise.sets && (
                                        <span> - {exercise.sets} {i18n.language === 'fa' ? 'ست' : 'sets'}</span>
                                      )}
                                      {exercise.reps && (
                                        <span> × {exercise.reps} {i18n.language === 'fa' ? 'تکرار' : 'reps'}</span>
                                      )}
                                      {exercise.rest && (
                                        <span> ({i18n.language === 'fa' ? 'استراحت' : 'rest'}: {exercise.rest})</span>
                                      )}
                                      {exercise.instructions && (
                                        <p className="exercise-instructions">
                                          {exercise.instructions || (i18n.language === 'fa' ? exercise.instructions_fa : exercise.instructions_en)}
                                        </p>
                                      )}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainingProgramTab;

