import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './TrainingMovementInfoTab.css';

const API_BASE = getApiBase();

const TrainingMovementInfoTab = () => {
  const { i18n } = useTranslation();
  const [exercises, setExercises] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [propagating, setPropagating] = useState(false);
  const [videoUploading, setVideoUploading] = useState(false);
  const [voiceUploading, setVoiceUploading] = useState(false);
  const [form, setForm] = useState({
    video_url: '',
    voice_url: '',
    trainer_notes_fa: '',
    trainer_notes_en: '',
    note_notify_at_seconds: '',
    ask_post_set_questions: false,
  });
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const getAuthToken = () => {
    const t = localStorage.getItem('token');
    return t && t.trim() ? t.trim() : null;
  };

  const getAxiosConfig = () => ({
    headers: {
      Authorization: `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    },
  });

  useEffect(() => {
    loadExercises();
  }, [page, search]);

  useEffect(() => {
    if (selectedExercise) {
      const notifyAt = selectedExercise.note_notify_at_seconds;
      setForm({
        video_url: selectedExercise.video_url || '',
        voice_url: selectedExercise.voice_url || '',
        trainer_notes_fa: selectedExercise.trainer_notes_fa || '',
        trainer_notes_en: selectedExercise.trainer_notes_en || '',
        note_notify_at_seconds: notifyAt != null && notifyAt !== '' ? String(notifyAt) : '',
        ask_post_set_questions: !!selectedExercise.ask_post_set_questions,
      });
    } else {
      setForm({ video_url: '', voice_url: '', trainer_notes_fa: '', trainer_notes_en: '', note_notify_at_seconds: '', ask_post_set_questions: false });
    }
  }, [selectedExercise]);

  const loadExercises = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: String(page), per_page: '100' });
      const res = await axios.get(
        `${API_BASE}/api/admin/exercises?${params}`,
        getAxiosConfig()
      );
      const list = res.data?.exercises || [];
      const totalCount = res.data?.total ?? list.length;
      const pages = res.data?.pages ?? 1;
      setExercises(list);
      setTotal(totalCount);
      setTotalPages(pages);
      if (!selectedExercise && list.length) {
        setSelectedExercise(list[0]);
      }
    } catch (err) {
      console.error('Error loading exercises:', err);
      setExercises([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedExercise?.id) return;
    try {
      setSaving(true);
      const notifyAfterSet = form.note_notify_at_seconds !== '' && form.note_notify_at_seconds != null
        ? parseInt(form.note_notify_at_seconds, 10)
        : null;
      await axios.patch(
        `${API_BASE}/api/admin/exercises/${selectedExercise.id}/movement-info`,
        {
          video_url: form.video_url.trim() || null,
          voice_url: form.voice_url.trim() || null,
          trainer_notes_fa: form.trainer_notes_fa.trim() || null,
          trainer_notes_en: form.trainer_notes_en.trim() || null,
          note_notify_at_seconds: Number.isInteger(notifyAfterSet) && notifyAfterSet >= 1 && notifyAfterSet <= 10 ? notifyAfterSet : null,
          ask_post_set_questions: !!form.ask_post_set_questions,
        },
        getAxiosConfig()
      );
      setSelectedExercise((prev) => (prev ? { ...prev, ...form } : null));
      await loadExercises();
      alert(i18n.language === 'fa' ? 'ذخیره شد' : 'Saved');
    } catch (err) {
      console.error('Error saving:', err);
      alert(i18n.language === 'fa' ? 'خطا در ذخیره' : 'Error saving');
    } finally {
      setSaving(false);
    }
  };

  const handleVideoUpload = async (e) => {
    const file = e?.target?.files?.[0];
    if (!file) return;
    try {
      setVideoUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const token = getAuthToken();
      const res = await axios.post(
        `${API_BASE}/api/admin/exercises/video-upload`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const url = res.data?.video_url;
      if (url) setForm((f) => ({ ...f, video_url: url }));
      e.target.value = '';
    } catch (err) {
      console.error('Video upload failed:', err);
      alert(i18n.language === 'fa' ? 'آپلود ویدیو ناموفق بود' : 'Video upload failed');
    } finally {
      setVideoUploading(false);
    }
  };

  const handlePropagate = async () => {
    if (!selectedExercise?.id) return;
    try {
      setPropagating(true);
      const res = await axios.post(
        `${API_BASE}/api/admin/exercises/${selectedExercise.id}/propagate-notes`,
        {},
        getAxiosConfig()
      );
      const count = res.data?.updated_count ?? 0;
      alert(i18n.language === 'fa' ? `یادداشت‌ها به ${count} مورد در برنامه‌ها اضافه شد.` : `Notes added to ${count} program slot(s).`);
    } catch (err) {
      console.error('Error propagating notes:', err);
      alert(i18n.language === 'fa' ? 'خطا در اعمال به برنامه‌ها' : 'Error propagating to programs');
    } finally {
      setPropagating(false);
    }
  };

  const handleVoiceUpload = async (e) => {
    const file = e?.target?.files?.[0];
    if (!file) return;
    try {
      setVoiceUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      const token = getAuthToken();
      const res = await axios.post(
        `${API_BASE}/api/admin/exercises/voice-upload`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const url = res.data?.voice_url;
      if (url) setForm((f) => ({ ...f, voice_url: url }));
      e.target.value = '';
    } catch (err) {
      console.error('Voice upload failed:', err);
      alert(i18n.language === 'fa' ? 'آپلود صدا ناموفق بود' : 'Voice upload failed');
    } finally {
      setVoiceUploading(false);
    }
  };

  const filteredList = search.trim()
    ? exercises.filter(
        (ex) =>
          (ex.name_fa && ex.name_fa.toLowerCase().includes(search.toLowerCase())) ||
          (ex.name_en && ex.name_en.toLowerCase().includes(search.toLowerCase()))
      )
    : exercises;

  return (
    <div className="training-movement-info-tab" dir="ltr">
      <div className="movement-info-header">
        <h2>{i18n.language === 'fa' ? 'اطلاعات حرکات تمرینی' : 'Training Movement Info'}</h2>
        <p className="movement-info-desc">
          {i18n.language === 'fa'
            ? 'صدای مربی یا متن یادداشت را یک‌بار برای هر حرکت تنظیم کنید؛ سپس با «اضافه به برنامه‌های اعضا» آن را به برنامه تمرینی همه اعضا اضافه کنید. در چت با AI هم می‌توانید بگویید: «یادداشت برای حرکت [نام حرکت]: [متن]» تا یادداشت ذخیره شود.'
            : 'Set trainer voice or text once per movement; then use «Add to members\' programs» to add it to all members\' training programs. In Chat with AI you can also say: «Add note to movement [name]: [text]» to save a note.'}
        </p>
      </div>

      <div className="movement-info-content">
        <div className="movement-info-sidebar">
          <div className="movement-info-search">
            <input
              type="text"
              placeholder={i18n.language === 'fa' ? 'جستجو حرکت...' : 'Search movement...'}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          {loading ? (
            <div className="movement-info-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
          ) : (
            <div className="movement-info-list">
              {filteredList.map((ex) => (
                <div
                  key={ex.id}
                  className={`movement-info-item ${selectedExercise?.id === ex.id ? 'active' : ''}`}
                  onClick={() => setSelectedExercise(ex)}
                >
                  <span className="movement-name">{ex.name_fa || ex.name_en || ex.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="movement-info-main">
          {!selectedExercise ? (
            <div className="movement-info-empty">
              <p>{i18n.language === 'fa' ? 'یک حرکت را انتخاب کنید' : 'Select a movement'}</p>
            </div>
          ) : (
            <>
              <div className="movement-info-form-header">
                <h3>{selectedExercise.name_fa || selectedExercise.name_en || selectedExercise.name}</h3>
                <div className="movement-info-form-actions">
                  <button
                    type="button"
                    className="movement-info-save-btn"
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? '…' : i18n.language === 'fa' ? 'ذخیره' : 'Save'}
                  </button>
                  <button
                    type="button"
                    className="movement-info-propagate-btn"
                    onClick={handlePropagate}
                    disabled={propagating || saving}
                    title={i18n.language === 'fa' ? 'این یادداشت و صدا را به همه برنامه‌هایی که این حرکت را دارند اضافه کن' : 'Add this note/voice to all programs that contain this movement'}
                  >
                    {propagating ? '…' : i18n.language === 'fa' ? 'اضافه به برنامه‌های اعضا' : 'Add to members\' programs'}
                  </button>
                </div>
              </div>

              <div className="movement-info-form">
                <div className="movement-info-field">
                  <label>{i18n.language === 'fa' ? 'ویدیو' : 'Video'}</label>
                  <div className="movement-info-media-row">
                    <input
                      type="text"
                      placeholder={i18n.language === 'fa' ? 'آدرس ویدیو یا آپلود' : 'Video URL or upload'}
                      value={form.video_url}
                      onChange={(e) => setForm((f) => ({ ...f, video_url: e.target.value }))}
                    />
                    <label className="movement-info-upload-btn">
                      <input
                        type="file"
                        accept=".mp4,.webm,.mov,.avi,.mkv,video/*"
                        onChange={handleVideoUpload}
                        disabled={videoUploading}
                      />
                      {videoUploading ? '…' : i18n.language === 'fa' ? 'آپلود' : 'Upload'}
                    </label>
                  </div>
                  {form.video_url && (
                    <div className="movement-info-preview">
                      {form.video_url.match(/\.(mp4|webm|mov|avi|mkv)(\?|$)/i) ? (
                        <video controls src={`${API_BASE}${form.video_url}`} preload="metadata" />
                      ) : (
                        <a href={form.video_url.startsWith('/') ? `${API_BASE}${form.video_url}` : form.video_url} target="_blank" rel="noopener noreferrer">
                          {i18n.language === 'fa' ? 'باز کردن ویدیو' : 'Open video'}
                        </a>
                      )}
                    </div>
                  )}
                </div>

                <div className="movement-info-field">
                  <label>{i18n.language === 'fa' ? 'صدای مربی' : 'Trainer voice'}</label>
                  <div className="movement-info-media-row">
                    <label className="movement-info-upload-btn">
                      <input
                        type="file"
                        accept=".webm,.mp3,.ogg,.wav,.m4a,audio/*"
                        onChange={handleVoiceUpload}
                        disabled={voiceUploading}
                      />
                      {voiceUploading ? '…' : i18n.language === 'fa' ? 'آپلود صدا' : 'Upload voice'}
                    </label>
                  </div>
                  {form.voice_url && (
                    <div className="movement-info-preview">
                      <audio controls src={`${API_BASE}${form.voice_url}`} preload="metadata" />
                    </div>
                  )}
                </div>

                <div className="movement-info-field">
                  <label>{i18n.language === 'fa' ? 'یادداشت مربی (فارسی)' : 'Trainer note (Persian)'}</label>
                  <textarea
                    rows={4}
                    value={form.trainer_notes_fa}
                    onChange={(e) => setForm((f) => ({ ...f, trainer_notes_fa: e.target.value }))}
                    placeholder={i18n.language === 'fa' ? 'متن یادداشت برای این حرکت' : 'Note text for this movement'}
                  />
                </div>

                <div className="movement-info-field">
                  <label>{i18n.language === 'fa' ? 'یادداشت مربی (انگلیسی)' : 'Trainer note (English)'}</label>
                  <textarea
                    rows={4}
                    value={form.trainer_notes_en}
                    onChange={(e) => setForm((f) => ({ ...f, trainer_notes_en: e.target.value }))}
                    placeholder={i18n.language === 'fa' ? 'متن یادداشت انگلیسی' : 'English note text'}
                  />
                </div>

                <div className="movement-info-field">
                  <label>{i18n.language === 'fa' ? 'اعلان یادداشت/صدا بعد از کدام ست' : 'Notify note/voice after which set'}</label>
                  <select
                    value={form.note_notify_at_seconds}
                    onChange={(e) => setForm((f) => ({ ...f, note_notify_at_seconds: e.target.value }))}
                  >
                    <option value="">{i18n.language === 'fa' ? 'در شروع حرکت (قبل از ست‌ها)' : 'At start of movement (before sets)'}</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                      <option key={n} value={String(n)}>
                        {i18n.language === 'fa' ? `بعد از ست ${n}` : `After set ${n}`}
                      </option>
                    ))}
                  </select>
                  <p className="movement-info-hint">
                    {i18n.language === 'fa' ? 'یادداشت یا صدای مربی در زمان انتخاب‌شده به عضو نشان داده می‌شود.' : 'Note or trainer voice is shown to the member at the chosen point.'}
                  </p>
                </div>

                <div className="movement-info-field">
                  <label className="movement-info-checkbox-label">
                    <input
                      type="checkbox"
                      checked={!!form.ask_post_set_questions}
                      onChange={(e) => setForm((f) => ({ ...f, ask_post_set_questions: e.target.checked }))}
                    />
                    <span>{i18n.language === 'fa' ? 'بعد از هر ست از عضو سوال بپرس (احساس ست، عضله درگیر) و بازخورد AI بده' : 'Ask member questions after each set (how it felt, which muscle) and show AI feedback'}</span>
                  </label>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainingMovementInfoTab;
