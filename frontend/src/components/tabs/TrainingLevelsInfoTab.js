import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './TrainingLevelsInfoTab.css';

const PURPOSE_KEYS = ['lose_weight', 'gain_weight', 'gain_muscle', 'shape_fitting'];
const PURPOSE_LABELS = {
  lose_weight: { fa: 'کاهش وزن', en: 'Lose weight' },
  gain_weight: { fa: 'افزایش وزن', en: 'Gain weight' },
  gain_muscle: { fa: 'افزایش عضله', en: 'Gain muscle' },
  shape_fitting: { fa: 'تناسب اندام', en: 'Shape fitting' }
};

const defaultPurposes = () => ({
  lose_weight: { sessions_per_week: '', sets_per_action: '', reps_per_action: '', training_focus_fa: '', training_focus_en: '', break_between_sets: '' },
  gain_weight: { sessions_per_week: '', sets_per_action: '', reps_per_action: '', training_focus_fa: '', training_focus_en: '', break_between_sets: '' },
  gain_muscle: { sessions_per_week: '', sets_per_action: '', reps_per_action: '', training_focus_fa: '', training_focus_en: '', break_between_sets: '' },
  shape_fitting: { sessions_per_week: '', sets_per_action: '', reps_per_action: '', training_focus_fa: '', training_focus_en: '', break_between_sets: '' }
});

const defaultLevel = () => ({
  description_fa: '',
  description_en: '',
  goals: [],
  purposes: defaultPurposes()
});

const normalizeLevel = (stored) => {
  if (!stored) return defaultLevel();
  return {
    description_fa: stored.description_fa || '',
    description_en: stored.description_en || '',
    goals: Array.isArray(stored.goals) ? stored.goals : [],
    purposes: (() => {
      const p = defaultPurposes();
      const sp = stored.purposes || {};
      PURPOSE_KEYS.forEach(key => {
        if (sp[key] && typeof sp[key] === 'object') {
          p[key] = { ...p[key], ...sp[key] };
        }
      });
      return p;
    })()
  };
};

const INJURY_KEYS = ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle'];
const INJURY_LABELS = {
  knee: { fa: 'زانو', en: 'Knee' },
  shoulder: { fa: 'شانه', en: 'Shoulder' },
  lower_back: { fa: 'کمر', en: 'Lower back' },
  neck: { fa: 'گردن', en: 'Neck' },
  wrist: { fa: 'مچ دست', en: 'Wrist' },
  ankle: { fa: 'مچ پا', en: 'Ankle' }
};

const defaultInjury = () => ({
  purposes_fa: '',
  purposes_en: '',
  allowed_movements: [],
  forbidden_movements: [],
  important_notes_fa: '',
  important_notes_en: ''
});

const normalizeInjury = (stored) => {
  if (!stored) return defaultInjury();
  return {
    purposes_fa: stored.purposes_fa || (stored.description_fa ?? ''),
    purposes_en: stored.purposes_en || (stored.description_en ?? ''),
    allowed_movements: Array.isArray(stored.allowed_movements) ? stored.allowed_movements : [],
    forbidden_movements: Array.isArray(stored.forbidden_movements) ? stored.forbidden_movements : [],
    important_notes_fa: stored.important_notes_fa ?? '',
    important_notes_en: stored.important_notes_en ?? ''
  };
};

const TrainingLevelsInfoTab = () => {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'fa' ? 'fa' : 'en';
  const [trainingLevels, setTrainingLevels] = useState({
    beginner: defaultLevel(),
    intermediate: defaultLevel(),
    advanced: defaultLevel()
  });
  const [injuries, setInjuries] = useState(() => {
    const o = {};
    INJURY_KEYS.forEach(k => { o[k] = defaultInjury(); });
    o.common_injury_note_fa = '';
    o.common_injury_note_en = '';
    return o;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchConfiguration();
  }, []);

  const getAuthToken = () => {
    const localToken = localStorage.getItem('token');
    if (localToken && localToken.trim() !== '') {
      return localToken.trim();
    }
    return null;
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  };

  const fetchConfiguration = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${getApiBase()}/api/admin/config`, getAxiosConfig());
      if (response.data.training_levels) {
        const raw = response.data.training_levels;
        setTrainingLevels({
          beginner: normalizeLevel(raw.beginner),
          intermediate: normalizeLevel(raw.intermediate),
          advanced: normalizeLevel(raw.advanced)
        });
      }
      if (response.data.injuries) {
        const raw = response.data.injuries;
        const normalized = {};
        INJURY_KEYS.forEach(k => { normalized[k] = normalizeInjury(raw[k]); });
        normalized.common_injury_note_fa = raw.common_injury_note_fa ?? '';
        normalized.common_injury_note_en = raw.common_injury_note_en ?? '';
        setInjuries(normalized);
      }
    } catch (error) {
      console.error('Error fetching configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const addGoal = (level) => {
    const goals = Array.isArray(trainingLevels[level].goals) ? [...trainingLevels[level].goals] : [];
    goals.push({ fa: '', en: '' });
    setTrainingLevels({
      ...trainingLevels,
      [level]: { ...trainingLevels[level], goals }
    });
  };

  const removeGoal = (level, index) => {
    const goals = trainingLevels[level].goals.filter((_, i) => i !== index);
    setTrainingLevels({
      ...trainingLevels,
      [level]: { ...trainingLevels[level], goals }
    });
  };

  const updateGoal = (level, index, lang, value) => {
    const goals = [...(trainingLevels[level].goals || [])];
    if (!goals[index]) goals[index] = { fa: '', en: '' };
    goals[index] = { ...goals[index], [lang]: value };
    setTrainingLevels({
      ...trainingLevels,
      [level]: { ...trainingLevels[level], goals }
    });
  };

  const updatePurpose = (level, purposeKey, field, value) => {
    const purposes = { ...(trainingLevels[level].purposes || defaultPurposes()) };
    purposes[purposeKey] = { ...purposes[purposeKey], [field]: value };
    setTrainingLevels({
      ...trainingLevels,
      [level]: { ...trainingLevels[level], purposes }
    });
  };

  const addInjuryMovement = (injuryKey, listKey) => {
    const list = Array.isArray(injuries[injuryKey]?.[listKey]) ? [...injuries[injuryKey][listKey]] : [];
    list.push({ fa: '', en: '' });
    setInjuries({
      ...injuries,
      [injuryKey]: { ...injuries[injuryKey], [listKey]: list }
    });
  };

  const removeInjuryMovement = (injuryKey, listKey, index) => {
    const list = injuries[injuryKey][listKey].filter((_, i) => i !== index);
    setInjuries({
      ...injuries,
      [injuryKey]: { ...injuries[injuryKey], [listKey]: list }
    });
  };

  const updateInjuryMovement = (injuryKey, listKey, index, lang, value) => {
    const list = [...(injuries[injuryKey][listKey] || [])];
    if (!list[index]) list[index] = { fa: '', en: '' };
    list[index] = { ...list[index], [lang]: value };
    setInjuries({
      ...injuries,
      [injuryKey]: { ...injuries[injuryKey], [listKey]: list }
    });
  };

  const updateInjuryImportantNotes = (injuryKey, lang, value) => {
    const field = lang === 'fa' ? 'important_notes_fa' : 'important_notes_en';
    setInjuries({
      ...injuries,
      [injuryKey]: { ...injuries[injuryKey], [field]: value }
    });
  };

  const updateCommonInjuryNote = (lang, value) => {
    const field = lang === 'fa' ? 'common_injury_note_fa' : 'common_injury_note_en';
    setInjuries({ ...injuries, [field]: value });
  };

  const handleSaveConfiguration = async () => {
    try {
      await axios.post(`${getApiBase()}/api/admin/config`, {
        training_levels: trainingLevels,
        injuries: injuries
      }, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'تنظیمات ذخیره شد' : 'Configuration saved');
    } catch (error) {
      console.error('Error saving configuration:', error);
      alert(i18n.language === 'fa' ? 'خطا در ذخیره تنظیمات' : 'Error saving configuration');
    }
  };

  return (
    <div className="training-levels-info-tab" dir="ltr">
      <div className="levels-header">
        <h2>{i18n.language === 'fa' ? 'اطلاعات سطح‌های تمرینی' : 'Training Level Information'}</h2>
        <button className="btn-primary" onClick={handleSaveConfiguration}>
          {i18n.language === 'fa' ? 'ذخیره تنظیمات' : 'Save Configuration'}
        </button>
      </div>

      {loading ? (
        <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
      ) : (
        <div className="levels-content">
          <div className="config-section training-levels-section">
            <h3>{i18n.language === 'fa' ? 'سطح‌های تمرین' : 'Training Levels'}</h3>
            {Object.keys(trainingLevels).map(level => {
              const levelLabel = i18n.language === 'fa'
                ? (level === 'beginner' ? 'مبتدی' : level === 'intermediate' ? 'متوسط' : 'پیشرفته')
                : level.charAt(0).toUpperCase() + level.slice(1);
              const levelData = trainingLevels[level] || defaultLevel();
              const goals = Array.isArray(levelData.goals) ? levelData.goals : [];
              const purposes = levelData.purposes || defaultPurposes();
              return (
                <div key={level} className={`level-block level-block--${level}`}>
                  <h4 className="level-block-title">{levelLabel}</h4>

                  <div className="level-description">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'توضیحات' : 'Description'}</span>
                    <div className="form-group">
                      <textarea
                        value={lang === 'fa' ? (levelData.description_fa || '') : (levelData.description_en || '')}
                        onChange={(e) => setTrainingLevels({
                          ...trainingLevels,
                          [level]: { ...levelData, [lang === 'fa' ? 'description_fa' : 'description_en']: e.target.value }
                        })}
                        rows="3"
                        placeholder={i18n.language === 'fa' ? 'توضیحات به فارسی' : 'Description in English'}
                      />
                    </div>
                  </div>

                  <div className="level-goals">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'اهداف' : 'Goals'}</span>
                    <p className="level-hint">{i18n.language === 'fa' ? 'هر هدف را جداگانه اضافه کنید.' : 'Add each goal item separately.'}</p>
                    {goals.map((goal, idx) => (
                      <div key={idx} className="goal-row">
                        <div className="form-row goal-inputs">
                          <div className="form-group">
                            <input
                              type="text"
                              value={goal[lang] || ''}
                              onChange={(e) => updateGoal(level, idx, lang, e.target.value)}
                              placeholder={i18n.language === 'fa' ? 'هدف' : 'Goal'}
                            />
                          </div>
                        </div>
                        <button type="button" className="btn-remove-goal" onClick={() => removeGoal(level, idx)} aria-label={i18n.language === 'fa' ? 'حذف هدف' : 'Remove goal'}>
                          ×
                        </button>
                      </div>
                    ))}
                    <button type="button" className="btn-add-goal" onClick={() => addGoal(level)}>
                      {i18n.language === 'fa' ? '+ افزودن هدف' : '+ Add goal'}
                    </button>
                  </div>

                  <div className="level-purposes">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'ویژگی‌ها برای هر هدف تمرینی' : 'Features for each training purpose'}</span>
                    <div className="purposes-grid">
                      {PURPOSE_KEYS.map(purposeKey => {
                        const p = purposes[purposeKey] || {};
                        const label = PURPOSE_LABELS[purposeKey] ? (i18n.language === 'fa' ? PURPOSE_LABELS[purposeKey].fa : PURPOSE_LABELS[purposeKey].en) : purposeKey;
                        return (
                          <div key={purposeKey} className="purpose-card">
                            <h5 className="purpose-card-title">{label}</h5>
                            <div className="form-group">
                              <label>{i18n.language === 'fa' ? 'تعداد جلسات در هفته' : 'Sessions per week'}</label>
                              <input
                                type="text"
                                value={p.sessions_per_week || ''}
                                onChange={(e) => updatePurpose(level, purposeKey, 'sessions_per_week', e.target.value)}
                                placeholder="e.g. 3-4"
                              />
                            </div>
                            <div className="form-group">
                              <label>{i18n.language === 'fa' ? 'تعداد ست در هر حرکت' : 'Sets per action'}</label>
                              <input
                                type="text"
                                value={p.sets_per_action || ''}
                                onChange={(e) => updatePurpose(level, purposeKey, 'sets_per_action', e.target.value)}
                                placeholder="e.g. 3"
                              />
                            </div>
                            <div className="form-group">
                              <label>{i18n.language === 'fa' ? 'تعداد تکرار در هر حرکت' : 'Reps per action'}</label>
                              <input
                                type="text"
                                value={p.reps_per_action || ''}
                                onChange={(e) => updatePurpose(level, purposeKey, 'reps_per_action', e.target.value)}
                                placeholder="e.g. 10-12"
                              />
                            </div>
                            <div className="form-group">
                              <label>{i18n.language === 'fa' ? 'نحوه تمرین (مکان و ابزار)' : 'Training focus (where & tools)'}</label>
                              <input
                                type="text"
                                value={lang === 'fa' ? (p.training_focus_fa || '') : (p.training_focus_en || '')}
                                onChange={(e) => updatePurpose(level, purposeKey, lang === 'fa' ? 'training_focus_fa' : 'training_focus_en', e.target.value)}
                                placeholder={i18n.language === 'fa' ? 'مثال: خانه، باشگاه، با/بدون ابزار' : 'e.g. at home, gym, with/without tools'}
                              />
                            </div>
                            <div className="form-group">
                              <label>{i18n.language === 'fa' ? 'استراحت بین ست‌ها' : 'Break between sets'}</label>
                              <input
                                type="text"
                                value={p.break_between_sets || ''}
                                onChange={(e) => updatePurpose(level, purposeKey, 'break_between_sets', e.target.value)}
                                placeholder={i18n.language === 'fa' ? 'مثلاً ۶۰ ثانیه' : 'e.g. 60 seconds'}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="config-section injuries-section">
            <h3>{i18n.language === 'fa' ? 'حرکات اصلاحی برای هر آسیب' : 'Corrective movements for each injury'}</h3>
            {INJURY_KEYS.map(injuryKey => {
              const data = injuries[injuryKey] || defaultInjury();
              const label = INJURY_LABELS[injuryKey] ? (i18n.language === 'fa' ? INJURY_LABELS[injuryKey].fa : INJURY_LABELS[injuryKey].en) : injuryKey;
              const allowed = Array.isArray(data.allowed_movements) ? data.allowed_movements : [];
              const forbidden = Array.isArray(data.forbidden_movements) ? data.forbidden_movements : [];
              return (
                <div key={injuryKey} className="injury-card-block">
                  <h4 className="injury-card-title">{label}</h4>

                  <div className="injury-purposes">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'اهداف / کاربرد' : 'Purposes'}</span>
                    <div className="form-group">
                      <textarea
                        value={lang === 'fa' ? (data.purposes_fa || '') : (data.purposes_en || '')}
                        onChange={(e) => setInjuries({
                          ...injuries,
                          [injuryKey]: { ...data, [lang === 'fa' ? 'purposes_fa' : 'purposes_en']: e.target.value }
                        })}
                        rows="3"
                        placeholder={i18n.language === 'fa' ? 'توضیحات به فارسی' : 'Description in English'}
                      />
                    </div>
                  </div>

                  <div className="injury-allowed">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'حرکات مجاز' : 'Allowed movements'}</span>
                    {allowed.map((item, idx) => (
                      <div key={idx} className="goal-row">
                        <div className="form-row goal-inputs">
                          <div className="form-group">
                            <input
                              type="text"
                              value={item[lang] || ''}
                              onChange={(e) => updateInjuryMovement(injuryKey, 'allowed_movements', idx, lang, e.target.value)}
                              placeholder={i18n.language === 'fa' ? 'حرکت مجاز' : 'Allowed movement'}
                            />
                          </div>
                        </div>
                        <button type="button" className="btn-remove-goal" onClick={() => removeInjuryMovement(injuryKey, 'allowed_movements', idx)} aria-label={i18n.language === 'fa' ? 'حذف' : 'Remove'}>×</button>
                      </div>
                    ))}
                    <button type="button" className="btn-add-goal" onClick={() => addInjuryMovement(injuryKey, 'allowed_movements')}>
                      {i18n.language === 'fa' ? '+ افزودن حرکت مجاز' : '+ Add allowed movement'}
                    </button>
                  </div>

                  <div className="injury-forbidden">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'حرکات ممنوع' : 'Forbidden movements'}</span>
                    {forbidden.map((item, idx) => (
                      <div key={idx} className="goal-row">
                        <div className="form-row goal-inputs">
                          <div className="form-group">
                            <input
                              type="text"
                              value={item[lang] || ''}
                              onChange={(e) => updateInjuryMovement(injuryKey, 'forbidden_movements', idx, lang, e.target.value)}
                              placeholder={i18n.language === 'fa' ? 'حرکت ممنوع' : 'Forbidden movement'}
                            />
                          </div>
                        </div>
                        <button type="button" className="btn-remove-goal" onClick={() => removeInjuryMovement(injuryKey, 'forbidden_movements', idx)} aria-label={i18n.language === 'fa' ? 'حذف' : 'Remove'}>×</button>
                      </div>
                    ))}
                    <button type="button" className="btn-add-goal" onClick={() => addInjuryMovement(injuryKey, 'forbidden_movements')}>
                      {i18n.language === 'fa' ? '+ افزودن حرکت ممنوع' : '+ Add forbidden movement'}
                    </button>
                  </div>

                  <div className="injury-important-notes">
                    <span className="level-subtitle">{i18n.language === 'fa' ? 'نکات مهم' : 'Important notes'}</span>
                    <div className="form-group">
                      <textarea
                        value={lang === 'fa' ? (data.important_notes_fa || '') : (data.important_notes_en || '')}
                        onChange={(e) => updateInjuryImportantNotes(injuryKey, lang, e.target.value)}
                        rows="3"
                        placeholder={i18n.language === 'fa' ? 'نکات مهم به فارسی' : 'Important notes in English'}
                      />
                    </div>
                  </div>
                </div>
              );
            })}

            <div className="injury-common-note">
              <h4 className="injury-common-note-title">{i18n.language === 'fa' ? 'نکته مشترک برای تمام آسیب‌ها' : 'Common note for all injuries'}</h4>
              <div className="form-group">
                <textarea
                  value={lang === 'fa' ? (injuries.common_injury_note_fa || '') : (injuries.common_injury_note_en || '')}
                  onChange={(e) => updateCommonInjuryNote(lang, e.target.value)}
                  rows="4"
                  placeholder={i18n.language === 'fa' ? 'مثال: همیشه فرم صحیح + تنفس کنترل‌شده؛ اگر درد شدید بود توقف و جایگزینی' : 'e.g. Always correct form + controlled breathing; if severe pain, stop and substitute'}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingLevelsInfoTab;
