import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './MembersProgramsTab.css';

const API_BASE = getApiBase();

const MembersProgramsTab = () => {
  const { i18n } = useTranslation();
  const [programs, setPrograms] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [programDetail, setProgramDetail] = useState(null);
  const [actionNotes, setActionNotes] = useState([]);
  const [notesDirty, setNotesDirty] = useState({});
  const [expandedSessions, setExpandedSessions] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [voiceUploading, setVoiceUploading] = useState(null);

  const getAuthToken = useCallback(() => {
    const t = localStorage.getItem('token');
    return t && t.trim() ? t.trim() : null;
  }, []);

  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    return {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    };
  }, [getAuthToken]);

  const loadPrograms = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get(
        `${API_BASE}/api/admin/programs?language=${i18n.language || 'fa'}`,
        getAxiosConfig()
      );
      const list = Array.isArray(res.data) ? res.data : [];
      setPrograms(list);
      if (list.length) {
        setSelectedProgram((prev) => prev || list[0]);
      }
    } catch (err) {
      console.error('Error loading programs:', err);
      setPrograms([]);
    } finally {
      setLoading(false);
    }
  }, [getAxiosConfig, i18n.language]);

  const loadActionNotes = useCallback(async (programId) => {
    if (!programId) return;
    try {
      const res = await axios.get(
        `${API_BASE}/api/admin/programs/${programId}/action-notes?language=${i18n.language || 'fa'}`,
        getAxiosConfig()
      );
      const list = Array.isArray(res.data) ? res.data : [];
      const map = {};
      list.forEach((item) => {
        const key = `${item.session_index}-${item.exercise_index}`;
        map[key] = {
          note_fa: item.note_fa ?? '',
          note_en: item.note_en ?? '',
          voice_url: item.voice_url ?? '',
        };
      });
      setActionNotes(map);
      setNotesDirty({});
    } catch (err) {
      console.error('Error loading action notes:', err);
      setActionNotes([]);
    }
  }, [getAxiosConfig, i18n.language]);

  useEffect(() => {
    if (selectedProgram) {
      loadActionNotes(selectedProgram.id);
      setProgramDetail(selectedProgram);
    } else {
      setProgramDetail(null);
      setActionNotes([]);
      setNotesDirty({});
    }
  }, [selectedProgram, loadActionNotes]);

  useEffect(() => {
    loadPrograms();
  }, [loadPrograms]);

  const noteKey = (sessionIdx, exIdx) => `${sessionIdx}-${exIdx}`;

  const getNote = (sessionIdx, exIdx) => {
    const key = noteKey(sessionIdx, exIdx);
    if (notesDirty[key]) return notesDirty[key];
    return actionNotes[key] || { note_fa: '', note_en: '', voice_url: '' };
  };

  const setNote = (sessionIdx, exIdx, field, value) => {
    const key = noteKey(sessionIdx, exIdx);
    const prev = getNote(sessionIdx, exIdx);
    setNotesDirty((d) => ({
      ...d,
      [key]: { ...prev, [field]: value },
    }));
  };

  const toggleSession = (sessionIdx) => {
    setExpandedSessions((prev) => {
      const next = new Set(prev);
      if (next.has(sessionIdx)) next.delete(sessionIdx);
      else next.add(sessionIdx);
      return next;
    });
  };

  const saveNotes = async (notifyMembers = false) => {
    if (!selectedProgram || !programDetail?.sessions) return;
    const notes = [];
    programDetail.sessions.forEach((session, sessionIdx) => {
      (session.exercises || []).forEach((_, exIdx) => {
        const n = getNote(sessionIdx, exIdx);
        notes.push({
          session_index: sessionIdx,
          exercise_index: exIdx,
          note_fa: (n.note_fa || '').trim() || undefined,
          note_en: (n.note_en || '').trim() || undefined,
          voice_url: (n.voice_url || '').trim() || undefined,
        });
      });
    });
    try {
      setSaving(true);
      await axios.put(
        `${API_BASE}/api/admin/programs/${selectedProgram.id}/action-notes`,
        { notes, notify_members: notifyMembers },
        getAxiosConfig()
      );
      setNotesDirty({});
      await loadActionNotes(selectedProgram.id);
      if (notifyMembers) {
        alert(i18n.language === 'fa' ? 'یادداشت‌ها ذخیره و به اعضا اعلان شد.' : 'Notes saved and members notified.');
      } else {
        alert(i18n.language === 'fa' ? 'یادداشت‌ها ذخیره شد.' : 'Notes saved.');
      }
    } catch (err) {
      console.error('Error saving notes:', err);
      alert(i18n.language === 'fa' ? 'خطا در ذخیره' : 'Error saving');
    } finally {
      setSaving(false);
    }
  };

  const handleVoiceUpload = async (sessionIdx, exIdx, file) => {
    if (!file) return;
    const key = `${sessionIdx}-${exIdx}`;
    setVoiceUploading(key);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const token = getAuthToken();
      const res = await axios.post(
        `${API_BASE}/api/admin/action-notes/voice-upload`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const voice_url = res.data?.voice_url;
      if (voice_url) setNote(sessionIdx, exIdx, 'voice_url', voice_url);
    } catch (err) {
      console.error('Voice upload failed:', err);
      alert(i18n.language === 'fa' ? 'آپلود صدا ناموفق بود' : 'Voice upload failed');
    } finally {
      setVoiceUploading(null);
    }
  };

  const hasDirty = Object.keys(notesDirty).length > 0;

  return (
    <div className="members-programs-tab" dir="ltr">
      <div className="programs-header">
        <h2>{i18n.language === 'fa' ? 'برنامه اعضا و یادداشت‌های مربی' : 'Members Programs & Trainer Notes'}</h2>
        <p className="programs-subtitle">
          {i18n.language === 'fa'
            ? 'برنامه را انتخاب کنید و برای هر تمرین یادداشت یا صدای مربی اضافه کنید. با «اعلان به اعضا» یادداشت‌های جدید به اعضا ارسال می‌شود.'
            : 'Select a program and add trainer notes or voice notes per exercise. Use "Notify members" to send new notes to members.'}
        </p>
      </div>

      <div className="programs-content">
        <div className="members-sidebar">
          <h3>{i18n.language === 'fa' ? 'لیست برنامه‌ها' : 'Programs'}</h3>
          {loading ? (
            <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
          ) : (
            <div className="members-list">
              {programs.map((prog) => (
                <div
                  key={prog.id}
                  className={`member-item ${selectedProgram?.id === prog.id ? 'active' : ''}`}
                  onClick={() => setSelectedProgram(prog)}
                >
                  {prog.name || prog.name_fa || prog.name_en || `Program ${prog.id}`}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="programs-main">
          {!selectedProgram ? (
            <div className="select-member-prompt">
              <p>{i18n.language === 'fa' ? 'یک برنامه را انتخاب کنید' : 'Select a program'}</p>
            </div>
          ) : !programDetail?.sessions?.length ? (
            <div className="no-programs">
              <p>{i18n.language === 'fa' ? 'این برنامه جلسه یا تمرینی ندارد.' : 'This program has no sessions or exercises.'}</p>
            </div>
          ) : (
            <>
              <div className="action-notes-program-title">
                <h3>{programDetail.name || programDetail.name_fa || programDetail.name_en}</h3>
              </div>
              <div className="action-notes-actions">
                <button
                  type="button"
                  className="btn-save-notes"
                  onClick={() => saveNotes(false)}
                  disabled={saving || !hasDirty}
                >
                  {saving ? '…' : i18n.language === 'fa' ? 'ذخیره یادداشت‌ها' : 'Save notes'}
                </button>
                <button
                  type="button"
                  className="btn-notify-members"
                  onClick={() => saveNotes(true)}
                  disabled={saving || !hasDirty}
                >
                  {saving ? '…' : i18n.language === 'fa' ? 'ذخیره و اعلان به اعضا' : 'Save and notify members'}
                </button>
              </div>
              <div className="sessions-list-notes">
                {programDetail.sessions.map((session, sessionIdx) => {
                  const isExpanded = expandedSessions.has(sessionIdx);
                  return (
                    <div key={sessionIdx} className={`session-card-notes ${isExpanded ? 'expanded' : ''}`}>
                      <div
                        className="session-header-notes"
                        onClick={() => toggleSession(sessionIdx)}
                      >
                        <h5>
                          {session.name || session.name_fa || session.name_en || `Session ${sessionIdx + 1}`}
                        </h5>
                        <span className="session-toggle-icon">{isExpanded ? '▼' : '▶'}</span>
                      </div>
                      {isExpanded && (
                        <div className="session-exercises-notes">
                          {(session.exercises || []).map((exercise, exIdx) => {
                            const note = getNote(sessionIdx, exIdx);
                            const uploadKey = `${sessionIdx}-${exIdx}`;
                            return (
                              <div key={exIdx} className="exercise-note-row">
                                <div className="exercise-note-label">
                                  <strong>
                                    {exercise.name || exercise.name_fa || exercise.name_en || `Exercise ${exIdx + 1}`}
                                  </strong>
                                  {exercise.sets && <span> — {exercise.sets} sets</span>}
                                  {exercise.reps != null && <span> × {exercise.reps} reps</span>}
                                </div>
                                <div className="exercise-note-fields">
                                  <label>
                                    <span>{i18n.language === 'fa' ? 'یادداشت (فا)' : 'Note (FA)'}</span>
                                    <textarea
                                      value={note.note_fa}
                                      onChange={(e) => setNote(sessionIdx, exIdx, 'note_fa', e.target.value)}
                                      rows={2}
                                      placeholder={i18n.language === 'fa' ? 'یادداشت فارسی' : 'Persian note'}
                                    />
                                  </label>
                                  <label>
                                    <span>{i18n.language === 'fa' ? 'یادداشت (EN)' : 'Note (EN)'}</span>
                                    <textarea
                                      value={note.note_en}
                                      onChange={(e) => setNote(sessionIdx, exIdx, 'note_en', e.target.value)}
                                      rows={2}
                                      placeholder={i18n.language === 'fa' ? 'یادداشت انگلیسی' : 'English note'}
                                    />
                                  </label>
                                  <div className="voice-note-field">
                                    <span>{i18n.language === 'fa' ? 'صدای مربی' : 'Voice note'}</span>
                                    <input
                                      type="file"
                                      accept=".webm,.mp3,.ogg,.wav,.m4a,audio/*"
                                      onChange={(e) => {
                                        const f = e.target.files?.[0];
                                        if (f) handleVoiceUpload(sessionIdx, exIdx, f);
                                        e.target.value = '';
                                      }}
                                      disabled={!!voiceUploading}
                                    />
                                    {voiceUploading === uploadKey && <span className="uploading-label">…</span>}
                                    {note.voice_url && (
                                      <div className="current-voice">
                                        <audio controls src={`${API_BASE}${note.voice_url}`} preload="metadata" />
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MembersProgramsTab;
