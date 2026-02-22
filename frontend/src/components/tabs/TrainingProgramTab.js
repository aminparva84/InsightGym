import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import { useAuth } from '../../context/AuthContext';
import './TrainingProgramTab.css';

const TrainingProgramTab = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const fa = i18n.language === 'fa';
  const { user, loading: authLoading } = useAuth();
  const [programs, setPrograms] = useState([]);
  const [weeklyGoals, setWeeklyGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedSessions, setExpandedSessions] = useState(new Set());
  const [goalUpdating, setGoalUpdating] = useState(new Set());
  const [progressSet, setProgressSet] = useState(new Set());
  const [actionNotesByProgram, setActionNotesByProgram] = useState({});
  const [actionToggling, setActionToggling] = useState(new Set());
  const [exerciseInfoCache, setExerciseInfoCache] = useState({});
  const [sessionPhases, setSessionPhases] = useState({ warming: { title_fa: '', title_en: '', steps: [] }, cooldown: { title_fa: '', title_en: '', steps: [] }, ending_message_fa: '', ending_message_en: '' });
  const [activeSessionStart, setActiveSessionStart] = useState(null);
  const [moodModal, setMoodModal] = useState({ open: false, programId: null, sessionIndex: null });
  const [completedSetsInSession, setCompletedSetsInSession] = useState({});
  const [endMessageModal, setEndMessageModal] = useState({ open: false, text: '' });
  const [postSetModal, setPostSetModal] = useState({ open: false, programId: null, sessionIdx: null, exIdx: null, exercise: null, setNumber: null, targetMuscle: '' });
  const [postSetAnswers, setPostSetAnswers] = useState({ how_was_it: '', which_muscle: '', was_hard: '' });
  const [postSetFeedback, setPostSetFeedback] = useState('');
  const [postSetLoading, setPostSetLoading] = useState(false);
  const [adaptingSession, setAdaptingSession] = useState(false);
  const [weeklyGoalsSectionOpen, setWeeklyGoalsSectionOpen] = useState(false);
  const [expandedGoalWeeks, setExpandedGoalWeeks] = useState(new Set());
  const [cancellingProgramId, setCancellingProgramId] = useState(null);
  const [showOtherDaysByProgram, setShowOtherDaysByProgram] = useState({});

  const getAuthToken = useCallback(() => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  }, []);

  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  }, [getAuthToken]);

  const loadSessionPhases = useCallback(async () => {
    const token = getAuthToken();
    if (!token) return;
    try {
      const config = getAxiosConfig();
      const res = await axios.get(`${API_BASE}/api/member/session-phases`, config);
      const d = res.data || {};
      setSessionPhases({
        warming: d.warming && typeof d.warming === 'object' ? d.warming : { title_fa: '', title_en: '', steps: [] },
        cooldown: d.cooldown && typeof d.cooldown === 'object' ? d.cooldown : { title_fa: '', title_en: '', steps: [] },
        ending_message_fa: d.ending_message_fa || '',
        ending_message_en: d.ending_message_en || ''
      });
    } catch (err) {
      console.error('Error loading session phases:', err);
    }
  }, [API_BASE, getAuthToken, getAxiosConfig]);

  const loadTrainingProgress = useCallback(async () => {
    const token = getAuthToken();
    if (!token) return;
    try {
      const config = getAxiosConfig();
      const response = await axios.get(`${API_BASE}/api/member/training-progress`, config);
      const list = Array.isArray(response.data) ? response.data : [];
      const set = new Set(list.map((r) => `${r.training_program_id}-${r.session_index}-${r.exercise_index}`));
      setProgressSet(set);
    } catch (err) {
      console.error('Error loading training progress:', err);
    }
  }, [API_BASE, getAuthToken, getAxiosConfig]);

  const loadActionNotes = useCallback(async (programId) => {
    const token = getAuthToken();
    if (!token) return;
    try {
      const config = getAxiosConfig();
      const response = await axios.get(`${API_BASE}/api/member/action-notes?program_id=${programId}&language=${i18n.language || 'fa'}`, config);
      const list = Array.isArray(response.data) ? response.data : [];
      const map = {};
      list.forEach((item) => {
        const key = `${item.session_index}-${item.exercise_index}`;
        map[key] = { note: item.note || '', voice_url: item.voice_url || '' };
      });
      setActionNotesByProgram((prev) => ({ ...prev, [programId]: map }));
    } catch (err) {
      console.error('Error loading action notes:', err);
    }
  }, [API_BASE, getAuthToken, getAxiosConfig, i18n.language]);

  const progressKey = (programId, sessionIdx, exIdx) => `${programId}-${sessionIdx}-${exIdx}`;

  const isActionCompleted = (programId, sessionIdx, exIdx) => progressSet.has(progressKey(programId, sessionIdx, exIdx));

  const toggleActionComplete = async (programId, sessionIdx, exIdx) => {
    const key = progressKey(programId, sessionIdx, exIdx);
    const completed = !isActionCompleted(programId, sessionIdx, exIdx);
    setActionToggling((prev) => new Set(prev).add(key));
    try {
      const config = getAxiosConfig();
      await axios.post(`${API_BASE}/api/member/training-progress`, {
        program_id: programId,
        session_index: sessionIdx,
        exercise_index: exIdx,
        completed,
      }, { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } });
      setProgressSet((prev) => {
        const next = new Set(prev);
        if (completed) next.add(key);
        else next.delete(key);
        return next;
      });
    } catch (err) {
      console.error('Error toggling action:', err);
    } finally {
      setActionToggling((prev) => { const s = new Set(prev); s.delete(key); return s; });
    }
  };

  const getActionNote = (programId, sessionIdx, exIdx) => {
    const map = actionNotesByProgram[programId];
    if (!map) return null;
    return map[`${sessionIdx}-${exIdx}`];
  };

  const exerciseInfoKey = (nameFa, nameEn) => `${nameFa || ''}|${nameEn || ''}`;

  const loadExerciseInfo = useCallback(async (nameFa, nameEn) => {
    const key = exerciseInfoKey(nameFa, nameEn);
    if (!key || key === '|' || exerciseInfoCache[key]) return;
    try {
      const config = getAxiosConfig();
      const params = new URLSearchParams({ language: i18n.language || 'fa' });
      if (nameFa) params.set('name_fa', nameFa);
      if (nameEn) params.set('name_en', nameEn);
      const res = await axios.get(`${API_BASE}/api/member/exercise-info?${params}`, config);
      const data = res.data || {};
      setExerciseInfoCache((prev) => ({ ...prev, [key]: { video_url: data.video_url || '', voice_url: data.voice_url || '', trainer_notes: data.trainer_notes || '', ask_post_set_questions: !!data.ask_post_set_questions, target_muscle: data.target_muscle || '' } }));
    } catch (err) {
      console.error('Error loading exercise info:', err);
    }
  }, [API_BASE, exerciseInfoCache, getAxiosConfig, i18n.language]);

  useEffect(() => {
    if (!programs.length) return;
    programs.forEach((program) => {
      (program.sessions || []).forEach((session, sessionIdx) => {
        const sessionKey = `${program.id}-${sessionIdx}`;
        if (!expandedSessions.has(sessionKey)) return;
        (session.exercises || []).forEach((exercise) => {
          const nameFa = exercise.name_fa || exercise.name || '';
          const nameEn = exercise.name_en || exercise.name || '';
          const key = exerciseInfoKey(nameFa, nameEn);
          if (key && key !== '|' && !exerciseInfoCache[key]) loadExerciseInfo(nameFa, nameEn);
        });
      });
    });
  }, [programs, expandedSessions, exerciseInfoCache, loadExerciseInfo]);

  useEffect(() => {
    if (!activeSessionStart?.session?.exercises?.length) return;
    activeSessionStart.session.exercises.forEach((exercise) => {
      const nameFa = exercise.name_fa || exercise.name || '';
      const nameEn = exercise.name_en || exercise.name || '';
      const key = exerciseInfoKey(nameFa, nameEn);
      if (key && key !== '|' && !exerciseInfoCache[key]) loadExerciseInfo(nameFa, nameEn);
    });
  }, [activeSessionStart, exerciseInfoCache, loadExerciseInfo]);

  const loadWeeklyGoals = useCallback(async () => {
    const token = getAuthToken();
    if (!token) return;
    try {
      const config = getAxiosConfig();
      const response = await axios.get(`${API_BASE}/api/member/weekly-goals?language=${i18n.language || 'fa'}`, config);
      const list = Array.isArray(response.data) ? response.data : [];
      setWeeklyGoals(list);
      if (list.length > 0) {
        const maxWeek = Math.max(...list.map((g) => g.week_number || 1));
        let currentWeek = 1;
        for (let w = 1; w <= maxWeek; w++) {
          const inWeek = list.filter((g) => (g.week_number || 1) === w);
          if (inWeek.some((g) => !g.completed)) {
            currentWeek = w;
            break;
          }
          currentWeek = w + 1;
        }
        if (currentWeek > maxWeek) currentWeek = maxWeek;
        setExpandedGoalWeeks((prev) => (prev.size === 0 ? new Set([currentWeek]) : prev));
      }
    } catch (err) {
      console.error('Error loading weekly goals:', err);
      setWeeklyGoals([]);
    }
  }, [API_BASE, getAuthToken, getAxiosConfig, i18n.language]);

  const toggleGoalWeek = (weekNum) => {
    setExpandedGoalWeeks((prev) => {
      const next = new Set(prev);
      if (next.has(weekNum)) next.delete(weekNum);
      else next.add(weekNum);
      return next;
    });
  };

  const toggleGoalComplete = async (goalId, currentCompleted) => {
    setGoalUpdating(prev => new Set(prev).add(goalId));
    try {
      const config = getAxiosConfig();
      await axios.patch(`${API_BASE}/api/member/weekly-goals/${goalId}`, { completed: !currentCompleted }, { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } });
      setWeeklyGoals(prev => prev.map(g => g.id === goalId ? { ...g, completed: !currentCompleted, completed_at: !currentCompleted ? new Date().toISOString() : null } : g));
    } catch (err) {
      console.error('Error updating goal:', err);
    } finally {
      setGoalUpdating(prev => { const s = new Set(prev); s.delete(goalId); return s; });
    }
  };

  const handleCancelPlan = async (programId) => {
    if (!window.confirm(t('tpCancelPlanConfirm'))) return;
    const id = parseInt(programId, 10);
    if (Number.isNaN(id)) return;
    setCancellingProgramId(id);
    try {
      const config = getAxiosConfig();
      const res = await axios.delete(`${API_BASE}/api/member/training-programs/${id}`, config);
      if (res.status === 200) {
        setPrograms((prev) => prev.filter((p) => p.id !== id));
        await loadWeeklyGoals();
        await loadTrainingProgress();
      }
      await loadPrograms();
    } catch (err) {
      console.error('Error cancelling plan:', err);
      const msg = err.response?.data?.error || err.message || (i18n.language === 'fa' ? 'خطا در لغو برنامه' : 'Error cancelling plan');
      alert(msg);
    } finally {
      setCancellingProgramId(null);
    }
  };

  const loadPrograms = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      console.warn('No token found for loading training programs');
      setLoading(false);
      return;
    }

    try {
      const config = getAxiosConfig();
      const response = await axios.get(`${API_BASE}/api/training-programs`, config);
      console.log('Training programs response status:', response.status);
      console.log('Training programs response data:', response.data);
      console.log('Number of programs:', response.data?.length || 0);
      if (response.data && Array.isArray(response.data)) {
        setPrograms(response.data);
        response.data.forEach((p) => { if (p.id) loadActionNotes(p.id); });
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
  }, [API_BASE, getAuthToken, getAxiosConfig, loadActionNotes]);

  useEffect(() => {
    if (!authLoading && user) {
      loadPrograms();
      loadWeeklyGoals();
      loadTrainingProgress();
      loadSessionPhases();
    } else if (!authLoading && !user) {
      setLoading(false);
    }
  }, [authLoading, user, loadPrograms, loadWeeklyGoals, loadTrainingProgress, loadSessionPhases]);

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

  const getSessionStatus = (programId, sessionIdx, program) => {
    const sessions = program?.sessions || [];
    if (sessionIdx < 0 || sessionIdx >= sessions.length) return { completed: false, next: false, locked: true };
    const session = sessions[sessionIdx];
    const exerciseCount = (session.exercises || []).length;
    let completedCount = 0;
    for (let exIdx = 0; exIdx < exerciseCount; exIdx++) {
      if (isActionCompleted(programId, sessionIdx, exIdx)) completedCount++;
    }
    const completed = exerciseCount > 0 && completedCount === exerciseCount;
    let nextSessionIdx = -1;
    for (let i = 0; i < sessions.length; i++) {
      const s = sessions[i];
      const n = (s.exercises || []).length;
      let c = 0;
      for (let j = 0; j < n; j++) {
        if (isActionCompleted(programId, i, j)) c++;
      }
      if (n > 0 && c < n) { nextSessionIdx = i; break; }
    }
    if (nextSessionIdx < 0) nextSessionIdx = sessions.length;
    const next = nextSessionIdx === sessionIdx;
    const locked = sessionIdx > nextSessionIdx;
    return { completed, next, locked };
  };

  const canStartSession = (programId, sessionIdx, program) => {
    const st = getSessionStatus(programId, sessionIdx, program);
    return st.next && !st.completed;
  };

  useEffect(() => {
    if (!programs.length) return;
    setExpandedSessions(new Set());
  }, [programs]);

  const toggleOtherDays = (programId) => {
    setShowOtherDaysByProgram((prev) => ({
      ...prev,
      [programId]: !prev[programId],
    }));
  };

  const handleStartSessionClick = (programId, sessionIndex) => {
    setMoodModal({ open: true, programId, sessionIndex });
  };

  const handleMoodSubmit = async (moodOrMessage) => {
    if (moodModal.programId == null || moodModal.sessionIndex == null) return;
    const programId = moodModal.programId;
    const sessionIndex = moodModal.sessionIndex;
    const program = programs.find(p => (p.id || 0) === programId);
    if (!program?.sessions?.[sessionIndex]) return;
    setAdaptingSession(true);
    try {
      const config = getAxiosConfig();
      const res = await axios.post(`${API_BASE}/api/member/adapt-session`, {
        program_id: programId,
        session_index: sessionIndex,
        mood_or_message: moodOrMessage,
        language: i18n.language || 'fa',
      }, { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } });
      const sessionObj = program.sessions[sessionIndex];
      setActiveSessionStart({
        programId,
        sessionIndex,
        session: { ...sessionObj, exercises: res.data?.session?.exercises ?? sessionObj.exercises },
        extraAdvice: res.data?.extra_advice || '',
      });
      setMoodModal({ open: false, programId: null, sessionIndex: null });
      setCompletedSetsInSession({});

      // Background: generate next session when user starts current one (for sessions after the first 2)
      if (program.user_id != null) {
        const sessions = program.sessions || [];
        const nextIdx = sessionIndex + 1;
        if (nextIdx === sessions.length) {
          axios.post(
            `${API_BASE}/api/member/programs/${programId}/generate-sessions`,
            { start_session_index: sessions.length, count: 1, language: i18n.language || 'fa' },
            { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } }
          ).then((r) => {
            if (r.data?.program) {
              setPrograms((prev) => prev.map((p) => (p.id === programId ? r.data.program : p)));
              if (programId) loadActionNotes(programId);
            }
          }).catch((err) => console.warn('Background session generation failed:', err?.response?.data?.error || err.message));
        }
      }
    } catch (err) {
      console.error('Adapt session error:', err);
      const sessionObj = program.sessions[sessionIndex];
      setActiveSessionStart({
        programId,
        sessionIndex,
        session: sessionObj,
        extraAdvice: '',
      });
      setMoodModal({ open: false, programId: null, sessionIndex: null });
      setCompletedSetsInSession({});
    } finally {
      setAdaptingSession(false);
    }
  };

  const setDoneKey = (programId, sessionIdx, exIdx) => `${programId}-${sessionIdx}-${exIdx}`;
  const getCompletedSets = (programId, sessionIdx, exIdx) => {
    const key = setDoneKey(programId, sessionIdx, exIdx);
    return completedSetsInSession[key] || new Set();
  };
  const submitPostSetAndMarkDone = async () => {
    if (!postSetModal.open || !postSetModal.exercise) return;
    setPostSetLoading(true);
    try {
      const config = getAxiosConfig();
      const res = await axios.post(`${API_BASE}/api/member/post-set-feedback`, {
        exercise_name_fa: postSetModal.exercise.name_fa || postSetModal.exercise.name,
        exercise_name_en: postSetModal.exercise.name_en || postSetModal.exercise.name,
        target_muscle: postSetModal.targetMuscle,
        answers: postSetAnswers,
        language: i18n.language || 'fa',
      }, { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } });
      setPostSetFeedback(res.data?.feedback || '');
      const { programId, sessionIdx, exIdx, setNumber } = postSetModal;
      const key = setDoneKey(programId, sessionIdx, exIdx);
      const completed = getCompletedSets(programId, sessionIdx, exIdx);
      const newSet = new Set([...completed, setNumber]);
      setCompletedSetsInSession(prev => ({ ...prev, [key]: newSet }));
      const session = activeSessionStart?.session;
      const exercises = session?.exercises || [];
      const ex = exercises[exIdx];
      const sets = ex?.sets || 1;
      if (newSet.size >= sets) {
        toggleActionComplete(programId, sessionIdx, exIdx);
      }
      closePostSetModal();
    } catch (err) {
      console.error('Post-set feedback error:', err);
      setPostSetFeedback(t('tpErrorFeedback'));
    } finally {
      setPostSetLoading(false);
    }
  };

  const closePostSetModal = () => {
    setPostSetModal({ open: false, programId: null, sessionIdx: null, exIdx: null, exercise: null, setNumber: null, targetMuscle: '' });
    setPostSetFeedback('');
  };

  const handleEndSessionClick = async () => {
    const session = activeSessionStart?.session;
    const name = session?.name || session?.name_fa || session?.name_en || '';
    try {
      const config = getAxiosConfig();
      const res = await axios.post(`${API_BASE}/api/member/session-end-message`, {
        language: i18n.language || 'fa',
        session_name: name,
      }, { ...config, headers: { ...config.headers, 'Content-Type': 'application/json' } });
      setEndMessageModal({ open: true, text: res.data?.message || '' });
    } catch (err) {
      console.error('Session end message error:', err);
      setEndMessageModal({ open: true, text: t('tpSessionFinishedFallback') });
    }
  };

  const closeEndMessageAndExitSession = () => {
    setEndMessageModal({ open: false, text: '' });
    setActiveSessionStart(null);
    loadTrainingProgress();
  };

  const isActiveSessionFullyCompleted = () => {
    if (!activeSessionStart?.session?.exercises?.length) return true;
    const { programId, sessionIndex } = activeSessionStart;
    return activeSessionStart.session.exercises.every((_, exIdx) =>
      isActionCompleted(programId, sessionIndex, exIdx)
    );
  };

  /** First movement (exercise) that is not fully completed; null if all done. One movement shown at a time. */
  const getCurrentExerciseIndex = () => {
    if (!activeSessionStart?.session?.exercises?.length) return null;
    const { programId, sessionIndex } = activeSessionStart;
    const exercises = activeSessionStart.session.exercises;
    for (let exIdx = 0; exIdx < exercises.length; exIdx++) {
      if (!isActionCompleted(programId, sessionIndex, exIdx)) return exIdx;
    }
    return null;
  };

  if (loading) {
    return <div className="training-program-loading">{t('tpLoading')}</div>;
  }

  if (activeSessionStart) {
    const { programId, sessionIndex, session, extraAdvice } = activeSessionStart;
    const fa = i18n.language === 'fa';
    // Prefer warming/cooldown from session (AI-generated), else from sessionPhases
    const warming = session?.warming && (session.warming.steps?.length > 0 || session.warming.title_fa || session.warming.title_en)
      ? session.warming : (sessionPhases.warming || {});
    const cooldown = session?.cooldown && (session.cooldown.steps?.length > 0 || session.cooldown.title_fa || session.cooldown.title_en)
      ? session.cooldown : (sessionPhases.cooldown || {});
    const warmingTitle = fa ? (warming.title_fa || 'گرم کردن') : (warming.title_en || 'Warming');
    const cooldownTitle = fa ? (cooldown.title_fa || 'سرد کردن و تنفس') : (cooldown.title_en || 'Cooldown & Breathing');
    const exercises = session?.exercises || [];
    const allDone = isActiveSessionFullyCompleted();

    return (
      <div className="training-program-tab session-in-progress-view" dir="ltr">
        <div className="session-in-progress-header">
          <button type="button" className="session-back-btn" onClick={() => setActiveSessionStart(null)}>
            {t('tpBackToSessions')}
          </button>
          <h2>{session?.name || session?.name_fa || session?.name_en || t('tpWorkoutSession')}</h2>
        </div>
        <div className="session-in-progress-content">
          {extraAdvice && <div className="session-extra-advice">{extraAdvice}</div>}
          <div className="session-step-block session-step-warming">
            <h6>1. {warmingTitle}</h6>
            {(warming.steps || []).length > 0 ? (
              <ul className="session-phase-steps">
                {(warming.steps || []).map((step, i) => (
                  <li key={i}><strong>{fa ? (step.title_fa || step.title_en) : (step.title_en || step.title_fa)}</strong>
                    {(fa ? step.body_fa : step.body_en) && <p>{(fa ? step.body_fa : step.body_en)}</p>}
                  </li>
                ))}
              </ul>
            ) : <p className="session-phase-placeholder">{t('tpWarming')}</p>}
          </div>
          <div className="session-step-block session-step-main">
            <h6>2. {t('tpMainTraining')}</h6>
            {(() => {
              const exIdx = getCurrentExerciseIndex();
              if (exIdx === null) {
                return (
                  <div className="current-set-complete-summary">
                    <p className="main-training-all-done">✓ {t('tpMainTraining')} {t('tpDone')}</p>
                  </div>
                );
              }
              const exercise = exercises[exIdx];
              const nameFa = exercise.name_fa || exercise.name || '';
              const nameEn = exercise.name_en || exercise.name || '';
              const movementKey = exerciseInfoKey(nameFa, nameEn);
              const movementInfo = movementKey ? exerciseInfoCache[movementKey] : null;
              const sets = exercise.sets || 1;
              const exerciseCompleted = isActionCompleted(programId, sessionIndex, exIdx);
              const videoUrl = movementInfo?.video_url;
              const videoSrc = videoUrl && videoUrl.startsWith('/') ? `${API_BASE}${videoUrl}` : videoUrl;
              return (
                <div className="current-movement-view">
                  <p className="current-movement-counter" aria-hidden="true">
                    {t('tpMovement')} {exIdx + 1} {t('tpOf')} {exercises.length}
                  </p>
                  <div className={`current-set-video-block ${!videoUrl ? 'current-set-video-placeholder' : ''}`}>
                    <span className="current-set-video-label">{videoUrl ? t('tpWatchVideo') : t('tpMovementVideoPlaceholder')}</span>
                    {videoUrl ? (
                      videoSrc && (videoUrl.match(/\.(mp4|webm|mov|avi|mkv)(\?|$)/i) ? (
                        <video controls src={videoSrc} preload="metadata" className="current-set-video" />
                      ) : (
                        <a href={videoSrc} target="_blank" rel="noopener noreferrer" className="current-set-video-link">{t('tpWatchVideo')}</a>
                      ))
                    ) : (
                      <div className="current-set-video-placeholder-inner" aria-hidden="true">
                        <span className="current-set-video-placeholder-icon">▶</span>
                        <span className="current-set-video-placeholder-text">{t('tpMovementVideoPlaceholder')}</span>
                      </div>
                    )}
                  </div>
                  <div className={`current-movement-info ${exerciseCompleted ? 'exercise-item-done' : ''}`}>
                    <h4 className="current-set-exercise-name">{exercise.name || (fa ? exercise.name_fa : exercise.name_en)}</h4>
                    <p className="current-set-meta">
                      {sets} {t('tpSets')} × {exercise.reps || '?'} {t('tpReps')}
                      {exercise.rest && ` (${t('tpRest')}: ${exercise.rest})`}
                    </p>
                    {!exerciseCompleted && (
                      <button
                        type="button"
                        className="next-movement-btn"
                        onClick={() => toggleActionComplete(programId, sessionIndex, exIdx)}
                      >
                        {t('tpNextMovement')}
                      </button>
                    )}
                    {movementInfo?.trainer_notes && <p className="movement-info-notes">{movementInfo.trainer_notes}</p>}
                  </div>
                </div>
              );
            })()}
          </div>
          <div className="session-step-block session-step-cooldown">
            <h6>3. {cooldownTitle}</h6>
            {(cooldown.steps || []).length > 0 ? (
              <ul className="session-phase-steps">
                {(cooldown.steps || []).map((step, i) => (
                  <li key={i}><strong>{fa ? (step.title_fa || step.title_en) : (step.title_en || step.title_fa)}</strong>
                    {(fa ? step.body_fa : step.body_en) && <p>{(fa ? step.body_fa : step.body_en)}</p>}
                  </li>
                ))}
              </ul>
            ) : <p className="session-phase-placeholder">{t('tpCooldownShort')}</p>}
          </div>
          {allDone && (
            <div className="session-end-row">
              <button type="button" className="session-end-btn" onClick={handleEndSessionClick}>
                {t('tpEndSessionEncouragement')}
              </button>
            </div>
          )}
        </div>

        {postSetModal.open && postSetModal.exercise && (
          <div className="training-modal-overlay" onClick={closePostSetModal}>
            <div className="training-modal post-set-modal" onClick={(e) => e.stopPropagation()}>
              <h3>{t('tpAfterSet')} {postSetModal.setNumber}</h3>
              <p>{postSetModal.exercise.name_fa || postSetModal.exercise.name_en || postSetModal.exercise.name}</p>
              <div className="post-set-form">
                <label>
                  <span>{t('tpHowWasIt')}</span>
                  <input type="text" value={postSetAnswers.how_was_it} onChange={(e) => setPostSetAnswers(a => ({ ...a, how_was_it: e.target.value }))} placeholder={t('tpPlaceholderHow')} />
                </label>
                <label>
                  <span>{t('tpWhichMuscle')}</span>
                  <input type="text" value={postSetAnswers.which_muscle} onChange={(e) => setPostSetAnswers(a => ({ ...a, which_muscle: e.target.value }))} placeholder={t('tpPlaceholderMuscle')} />
                </label>
                <label>
                  <span>{t('tpHardOrEasy')}</span>
                  <select value={postSetAnswers.was_hard} onChange={(e) => setPostSetAnswers(a => ({ ...a, was_hard: e.target.value }))}>
                    <option value="">{t('tpSelectOption')}</option>
                    <option value="hard">{t('tpHard')}</option>
                    <option value="medium">{t('tpMedium')}</option>
                    <option value="easy">{t('tpEasy')}</option>
                  </select>
                </label>
              </div>
              {postSetFeedback && <div className="post-set-feedback-text">{postSetFeedback}</div>}
              <div className="post-set-modal-actions">
                <button type="button" className="post-set-submit" onClick={submitPostSetAndMarkDone} disabled={postSetLoading}>
                  {postSetLoading ? '…' : t('tpSubmitContinue')}
                </button>
                <button type="button" className="post-set-close" onClick={closePostSetModal}>{t('tpClose')}</button>
              </div>
            </div>
          </div>
        )}

        {endMessageModal.open && (
          <div className="training-modal-overlay" onClick={closeEndMessageAndExitSession}>
            <div className="training-modal end-message-modal" onClick={(e) => e.stopPropagation()}>
              <h3>{t('tpWellDone')}</h3>
              <p className="end-message-text">{endMessageModal.text}</p>
              <button type="button" className="end-message-close" onClick={closeEndMessageAndExitSession}>
                {t('tpCloseAndBack')}
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="training-program-tab" dir="ltr">
      <div className="training-program-header">
        <h2>{t('tpTrainingProgram')}</h2>
      </div>

      <div className="training-program-content">
        {weeklyGoals.length > 0 && (
          <div className={`weekly-goals-section ${weeklyGoalsSectionOpen ? 'expanded' : 'collapsed'}`}>
            <div
              className="weekly-goals-section-header"
              onClick={() => setWeeklyGoalsSectionOpen((open) => !open)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setWeeklyGoalsSectionOpen((open) => !open); } }}
              aria-expanded={weeklyGoalsSectionOpen}
            >
              <h3>{t('tpWeeklyGoals')}</h3>
              <p className="weekly-goals-desc">{t('tpWeeklyGoalsDesc')}</p>
              <span className="weekly-goals-section-toggle" aria-hidden="true">
                {weeklyGoalsSectionOpen ? `▼ ${t('tpCollapse')}` : `▶ ${t('tpExpand')}`}
              </span>
            </div>
            {weeklyGoalsSectionOpen && (() => {
              const byWeek = {};
              weeklyGoals.forEach((g) => {
                const w = g.week_number || 1;
                if (!byWeek[w]) byWeek[w] = [];
                byWeek[w].push(g);
              });
              const weekNumbers = Object.keys(byWeek).map(Number).sort((a, b) => a - b);
              return (
                <div className="weekly-goals-weeks">
                  {weekNumbers.map((weekNum) => {
                    const goalsInWeek = byWeek[weekNum];
                    const isWeekExpanded = expandedGoalWeeks.has(weekNum);
                    const completedCount = goalsInWeek.filter((g) => g.completed).length;
                    const totalCount = goalsInWeek.length;
                    return (
                      <div key={weekNum} className={`weekly-goals-week-block ${isWeekExpanded ? 'expanded' : 'collapsed'}`}>
                        <div
                          className="weekly-goals-week-header"
                          onClick={() => toggleGoalWeek(weekNum)}
                          role="button"
                          tabIndex={0}
                          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleGoalWeek(weekNum); } }}
                          aria-expanded={isWeekExpanded}
                        >
                          <span className="weekly-goals-week-title">
                            {t('tpWeek')} {weekNum}
                            <span className="weekly-goals-week-summary"> ({completedCount}/{totalCount})</span>
                          </span>
                          <span className="weekly-goals-week-toggle" aria-hidden="true">
                            {isWeekExpanded ? '▼' : '▶'}
                          </span>
                        </div>
                        {isWeekExpanded && (
                          <ul className="weekly-goals-list">
                            {goalsInWeek.map((goal) => (
                              <li key={goal.id} className={`weekly-goal-item ${goal.completed ? 'completed' : ''}`}>
                                <button
                                  type="button"
                                  className="weekly-goal-check"
                                  onClick={() => !goalUpdating.has(goal.id) && toggleGoalComplete(goal.id, goal.completed)}
                                  disabled={goalUpdating.has(goal.id)}
                                  aria-label={goal.completed ? t('tpMarkIncomplete') : t('tpMarkComplete')}
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
                        )}
                      </div>
                    );
                  })}
                </div>
              );
            })()}
          </div>
        )}
        {programs.length === 0 ? (
          <div className="no-programs">
            <p>{t('tpNoProgramYet')}</p>
            <p>{t('tpContactTrainer')}</p>
          </div>
        ) : (
          <div className="programs-list">
            {programs.map((program, index) => (
              <div key={program.id || index} className="program-card">
                <h3>{program.name || program.name_fa || program.name_en || t('tpTrainingProgram')}</h3>
                {(program.description || program.description_fa || program.description_en) && (
                  <p className="program-description">
                    {program.description || (fa ? program.description_fa : program.description_en)}
                  </p>
                )}
                {program.duration_weeks && (
                  <p className="program-duration">
                    {t('tpDuration')}: {program.duration_weeks} {t('tpWeeksMonth')}
                  </p>
                )}
                {program.training_level && (
                  <p className="program-level">
                    {t('tpLevel')}: {
                      program.training_level === 'beginner' ? t('tpBeginner') :
                      program.training_level === 'intermediate' ? t('tpIntermediate') :
                      program.training_level === 'advanced' ? t('tpAdvanced') :
                      program.training_level
                    }
                  </p>
                )}
                {program.user_id != null && (
                  <div className="program-cancel-row">
                    <button
                      type="button"
                      className="program-cancel-btn"
                      onClick={() => handleCancelPlan(program.id)}
                      disabled={cancellingProgramId === program.id}
                    >
                      {cancellingProgramId === program.id ? '…' : t('tpCancelPlan')}
                    </button>
                  </div>
                )}
                {program.sessions && program.sessions.length > 0 && (
                  <div className="program-sessions">
                    <h4>{t('tpTrainingSessions')}:</h4>
                    <div className="sessions-list">
                      {(() => {
                        const pid = program.id || index;
                        const sessions = program.sessions || [];
                        const sessionsWithIndex = sessions.map((session, i) => ({ session, index: i }));
                        let nextIdx = -1;
                        for (let i = 0; i < sessions.length; i++) {
                          const st = getSessionStatus(pid, i, program);
                          if (st.next) { nextIdx = i; break; }
                        }
                        if (nextIdx < 0 && sessions.length > 0) nextIdx = 0;
                        const showOtherDays = !!showOtherDaysByProgram[pid];
                        const otherSessions = sessionsWithIndex.filter(({ index: i }) => i !== nextIdx);
                        const visibleSessions = sessionsWithIndex.filter(({ index: i }) => i === nextIdx);

                        const renderSessionCard = ({ session, index: sessionIdx }) => {
                          const sessionKey = `${pid}-${sessionIdx}`;
                          const isExpanded = isSessionExpanded(pid, sessionIdx);
                          const status = getSessionStatus(pid, sessionIdx, program);
                          const canStart = canStartSession(pid, sessionIdx, program);
                          return (
                            <div
                              key={sessionKey}
                              className={`session-card ${isExpanded ? 'expanded' : ''} ${status.completed ? 'session-completed' : ''} ${status.next ? 'session-next' : ''} ${status.locked ? 'session-locked' : ''}`}
                              dir="ltr"
                            >
                              <div
                                className="session-header"
                                onClick={() => toggleSession(pid, sessionIdx)}
                              >
                                <div className="session-header-text">
                                  <h5>{session.name || (fa ? session.name_fa : session.name_en) || `${t('tpSession')} ${sessionIdx + 1}`}</h5>
                                  {session.week && session.day && (
                                    <p className="session-info">
                                      {t('tpWeek')} {session.week}, {t('tpDay')} {session.day}
                                    </p>
                                  )}
                                </div>
                                <div className="session-header-actions">
                                  <button
                                    type="button"
                                    className="session-start-btn session-start-btn-inline"
                                    onClick={(e) => { e.stopPropagation(); if (canStart) handleStartSessionClick(pid, sessionIdx); }}
                                    disabled={!canStart}
                                  >
                                    {t('tpStartSession')}
                                  </button>
                                </div>
                              </div>
                              {isExpanded && (
                                <div className="session-exercises">
                                  {(() => {
                                    const fa = i18n.language === 'fa';
                                    const warming = session?.warming && (session.warming.steps?.length > 0 || session.warming.title_fa || session.warming.title_en)
                                      ? session.warming : (sessionPhases.warming || {});
                                    const cooldown = session?.cooldown && (session.cooldown.steps?.length > 0 || session.cooldown.title_fa || session.cooldown.title_en)
                                      ? session.cooldown : (sessionPhases.cooldown || {});
                                    const warmingTitle = fa ? (warming.title_fa || t('tpWarming')) : (warming.title_en || t('tpWarming'));
                                    const cooldownTitle = fa ? (cooldown.title_fa || t('tpCooldown')) : (cooldown.title_en || t('tpCooldown'));
                                    return (
                                      <>
                                        <div className="session-step-block session-step-warming">
                                          <h6>1. {warmingTitle}</h6>
                                          {(warming.steps || []).length > 0 ? (
                                            <ul className="session-phase-steps">
                                              {(warming.steps || []).map((step, i) => (
                                                <li key={i}>
                                                  <strong>{fa ? (step.title_fa || step.title_en) : (step.title_en || step.title_fa)}</strong>
                                                  {(fa ? step.body_fa : step.body_en) && <p>{(fa ? step.body_fa : step.body_en)}</p>}
                                                </li>
                                              ))}
                                            </ul>
                                          ) : (
                                            <p className="session-phase-placeholder">{t('tpWarmingContentAdmin')}</p>
                                          )}
                                        </div>
                                        <div className="session-step-block session-step-main">
                                          <h6>2. {t('tpMainTraining')}</h6>
                                          {session.exercises && session.exercises.length > 0 ? (
                                            <ul>
                                    {session.exercises.map((exercise, exIdx) => {
                                      const pid = program.id || index;
                                      const completed = isActionCompleted(pid, sessionIdx, exIdx);
                                      const toggleKey = progressKey(pid, sessionIdx, exIdx);
                                      const toggling = actionToggling.has(toggleKey);
                                      const trainerNote = getActionNote(pid, sessionIdx, exIdx);
                                      const nameFa = exercise.name_fa || exercise.name || '';
                                      const nameEn = exercise.name_en || exercise.name || '';
                                      const movementKey = exerciseInfoKey(nameFa, nameEn);
                                      const movementInfo = movementKey ? exerciseInfoCache[movementKey] : null;
                                      return (
                                        <li key={exIdx} className={`exercise-item ${completed ? 'exercise-item-done' : ''}`}>
                                          <div className="exercise-item-row">
                                            <button
                                              type="button"
                                              className="exercise-done-check"
                                              onClick={() => !toggling && !status.locked && toggleActionComplete(pid, sessionIdx, exIdx)}
                                              disabled={toggling || status.locked}
                                              aria-label={completed ? t('tpMarkNotDone') : t('tpMarkComplete')}
                                              title={status.locked ? t('tpThisSessionLocked') : (completed ? t('tpNotDone') : t('tpDone'))}
                                            >
                                              {toggling ? '…' : (completed ? '✓' : '○')}
                                            </button>
                                            <div className="exercise-item-body">
                                              <strong>{exercise.name || (fa ? exercise.name_fa : exercise.name_en)}</strong>
                                              {exercise.sets && (
                                                <span> - {exercise.sets} {t('tpSets')}</span>
                                              )}
                                              {exercise.reps && (
                                                <span> × {exercise.reps} {t('tpReps')}</span>
                                              )}
                                              {exercise.rest && (
                                                <span> ({t('tpRest')}: {exercise.rest})</span>
                                              )}
                                              {exercise.instructions && (
                                                <p className="exercise-instructions">
                                                  {exercise.instructions || (fa ? exercise.instructions_fa : exercise.instructions_en)}
                                                </p>
                                              )}
                                              {movementInfo && (movementInfo.video_url || movementInfo.voice_url || movementInfo.trainer_notes) && (
                                                <div className="movement-info-block">
                                                  <span className="movement-info-label">{t('tpMovementInfo')}:</span>
                                                  {movementInfo.video_url && (
                                                    <div className="movement-info-video">
                                                      {movementInfo.video_url.startsWith('/') ? (
                                                        <video controls src={`${API_BASE}${movementInfo.video_url}`} preload="metadata" />
                                                      ) : (
                                                        <a href={movementInfo.video_url} target="_blank" rel="noopener noreferrer">{t('tpWatchVideo')}</a>
                                                      )}
                                                    </div>
                                                  )}
                                                  {movementInfo.voice_url && (
                                                    <audio controls className="movement-voice-note" src={`${API_BASE}${movementInfo.voice_url}`} preload="metadata">
                                                      {t('tpTrainerVoice')}
                                                    </audio>
                                                  )}
                                                  {movementInfo.trainer_notes && <p className="movement-info-notes">{movementInfo.trainer_notes}</p>}
                                                </div>
                                              )}
                                              {trainerNote && (trainerNote.note || trainerNote.voice_url) && (
                                                <div className="trainer-note-block">
                                                  <span className="trainer-note-label">{t('tpTrainerNoteProgram')}:</span>
                                                  {trainerNote.note && <p className="trainer-note-text">{trainerNote.note}</p>}
                                                  {trainerNote.voice_url && (
                                                    <audio controls className="trainer-voice-note" src={`${API_BASE}${trainerNote.voice_url}`} preload="metadata">
                                                      {t('tpAudio')}
                                                    </audio>
                                                  )}
                                                </div>
                                              )}
                                            </div>
                                          </div>
                                        </li>
                                      );
                                    })}
                                            </ul>
                                          ) : (
                                            <p className="session-phase-placeholder">{t('tpNoExercisesSession')}</p>
                                          )}
                                        </div>
                                        <div className="session-step-block session-step-cooldown">
                                          <h6>3. {cooldownTitle}</h6>
                                          {(cooldown.steps || []).length > 0 ? (
                                            <ul className="session-phase-steps">
                                              {(cooldown.steps || []).map((step, i) => (
                                                <li key={i}>
                                                  <strong>{fa ? (step.title_fa || step.title_en) : (step.title_en || step.title_fa)}</strong>
                                                  {(fa ? step.body_fa : step.body_en) && <p>{(fa ? step.body_fa : step.body_en)}</p>}
                                                </li>
                                              ))}
                                            </ul>
                                          ) : (
                                            <p className="session-phase-placeholder">{t('tpCooldownContentAdmin')}</p>
                                          )}
                                        </div>
                                      </>
                                    );
                                  })()}
                                </div>
                              )}
                            </div>
                          );
                        };

                        return (
                          <>
                            {visibleSessions.map((entry) => renderSessionCard(entry))}
                            {otherSessions.length > 0 && (
                              <div className="other-days-toggle">
                                <button
                                  type="button"
                                  className="other-days-toggle-btn"
                                  onClick={() => toggleOtherDays(pid)}
                                >
                                  {showOtherDays ? (fa ? 'بستن روزهای دیگر' : 'Hide other days') : (fa ? 'مشاهده روزهای دیگر' : 'See other days')}
                                </button>
                              </div>
                            )}
                            {showOtherDays && otherSessions.length > 0 && (
                              <div className="other-days-list">
                                {otherSessions.map((entry) => renderSessionCard(entry))}
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {moodModal.open && (
        <div className="training-modal-overlay" onClick={() => !adaptingSession && setMoodModal({ open: false, programId: null, sessionIndex: null })}>
          <div className="training-modal mood-modal" onClick={(e) => e.stopPropagation()}>
            <h3>{t('tpMoodBodyToday')}</h3>
            <p className="mood-modal-hint">{t('tpMoodHint')}</p>
            <div className="mood-options">
              {[
                { id: 'tired', key: 'tpTired' },
                { id: 'exhausted', key: 'tpExhausted' },
                { id: 'depressed', key: 'tpDepressed' },
                { id: 'energy', key: 'tpEnergy' },
                { id: 'normal', key: 'tpNormal' },
              ].map((m) => (
                <button key={m.id} type="button" className="mood-option-btn" onClick={() => handleMoodSubmit(t(m.key))}>
                  {t(m.key)}
                </button>
              ))}
            </div>
            <div className="mood-custom-row">
              <input
                type="text"
                placeholder={t('tpOrWriteMessage')}
                id="mood-custom-input"
                onKeyDown={(e) => { if (e.key === 'Enter') handleMoodSubmit(e.target.value); }}
              />
              <button type="button" className="mood-submit-custom" onClick={() => handleMoodSubmit(document.getElementById('mood-custom-input')?.value || '')}>
                {t('tpSendAndStart')}
              </button>
            </div>
            {adaptingSession && <p className="mood-loading">{t('tpAdaptingSession')}</p>}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingProgramTab;

