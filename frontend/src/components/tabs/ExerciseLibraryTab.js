import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import type1Groups from '../../data/exerciseLibraryType1.json';
import type2Groups from '../../data/exerciseLibraryType2.json';
import type3Groups from '../../data/exerciseLibraryType3.json';
import './ExerciseLibraryTab.css';

const API_BASE = getApiBase();

const CATEGORIES = [
  { value: 'bodybuilding_machine', label_fa: 'حرکات باشگاهی با دستگاه', label_en: 'Gym equipment exercises' },
  { value: 'functional_home', label_fa: 'حرکات فانکشنال بدون دستگاه', label_en: 'Functional exercises without equipment' },
  { value: 'hybrid_hiit_machine', label_fa: 'حرکات ترکیبی (دستگاه و فانکشنال)', label_en: 'Combined (equipment and functional)' }
];
const LEVELS = [
  { value: 'beginner', label_fa: 'مبتدی', label_en: 'Beginner' },
  { value: 'intermediate', label_fa: 'متوسط', label_en: 'Intermediate' },
  { value: 'advanced', label_fa: 'پیشرفته', label_en: 'Advanced' }
];
const INTENSITIES = [
  { value: 'light', label_fa: 'سبک', label_en: 'Light' },
  { value: 'medium', label_fa: 'متوسط', label_en: 'Medium' },
  { value: 'heavy', label_fa: 'سنگین', label_en: 'Heavy' }
];
const GENDER_SUITABILITY = [
  { value: 'male', label_fa: 'مرد', label_en: 'Male' },
  { value: 'female', label_fa: 'زن', label_en: 'Female' },
  { value: 'both', label_fa: 'هر دو', label_en: 'Both' }
];
const INJURY_OPTIONS = ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle'];

const EXERCISES_INFO = {
  title_en: 'Exercises',
  title_fa: 'تمرینات',
  intro_en: 'This section defines how exercises are added to the library so the AI and training plans can use them safely and consistently.',
  intro_fa: 'این بخش توضیح می‌دهد تمرین‌ها چگونه به کتابخانه اضافه شوند تا AI و برنامه‌های تمرینی با کیفیت و ایمنی استفاده کنند.',
  sections: [
    {
      title_en: 'Required fields',
      title_fa: 'فیلدهای ضروری',
      items_en: [
        'Name (FA/EN), Target muscle (FA/EN)',
        'Category, Level, Intensity, Gender suitability',
        'Execution tips & Breathing guide (recommended)',
      ],
      items_fa: [
        'نام (فارسی/انگلیسی)، عضله هدف (فارسی/انگلیسی)',
        'دسته‌بندی، سطح، شدت، مناسب‌بودن برای جنسیت',
        'نکات اجرا و راهنمای تنفس (ترجیحاً تکمیل شود)',
      ],
    },
    {
      title_en: 'Quality checklist',
      title_fa: 'چک‌لیست کیفیت',
      items_en: [
        'Write short, clear cues for form and breathing',
        'Match intensity to level; avoid advanced cues for beginners',
        'List injuries that should avoid this movement',
      ],
      items_fa: [
        'راهنمای کوتاه و واضح برای فرم و تنفس بنویسید',
        'شدت را با سطح تمرینی هماهنگ کنید؛ برای مبتدی‌ها پیشرفته ننویسید',
        'آسیب‌هایی که این حرکت برایشان ممنوع است را مشخص کنید',
      ],
    },
    {
      title_en: 'Media & notes',
      title_fa: 'رسانه و یادداشت',
      items_en: [
        'Optional video/image URLs help members perform correctly',
        'Trainer notes can be reused across programs',
      ],
      items_fa: [
        'ویدیو/تصویر اختیاری برای اجرای صحیح اعضا مفید است',
        'یادداشت مربی می‌تواند در برنامه‌ها استفاده مجدد شود',
      ],
    },
  ],
};

const defaultExerciseForm = () => ({
  category: 'bodybuilding_machine',
  name_fa: '',
  name_en: '',
  target_muscle_fa: '',
  target_muscle_en: '',
  level: 'beginner',
  intensity: 'medium',
  gender_suitability: 'both',
  execution_tips_fa: '',
  execution_tips_en: '',
  breathing_guide_fa: '',
  breathing_guide_en: '',
  injury_contraindications: [],
  equipment_needed_fa: '',
  equipment_needed_en: '',
  video_url: '',
  image_url: ''
});

const ExerciseLibraryTab = () => {
  const { i18n } = useTranslation();
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingExercise, setEditingExercise] = useState(null);
  const [formData, setFormData] = useState(defaultExerciseForm());

  const getAuthToken = useCallback(() => {
    const t = localStorage.getItem('token');
    return t && t.trim() ? t.trim() : null;
  }, []);
  const getAxiosConfig = useCallback(() => ({
    headers: {
      Authorization: `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    }
  }), [getAuthToken]);

  const fetchExercises = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: String(page), per_page: '20' });
      if (categoryFilter) params.set('category', categoryFilter);
      if (levelFilter) params.set('level', levelFilter);
      const response = await axios.get(
        `${API_BASE}/api/admin/exercises?${params}`,
        getAxiosConfig()
      );
      setExercises(response.data.exercises || []);
      setTotalPages(response.data.pages || 1);
      setTotal(response.data.total ?? 0);
    } catch (error) {
      console.error('Error fetching exercises:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست تمرینات' : 'Error fetching exercises');
    } finally {
      setLoading(false);
    }
  }, [categoryFilter, getAxiosConfig, i18n.language, levelFilter, page]);

  useEffect(() => {
    fetchExercises();
  }, [fetchExercises]);

  const handleArrayChange = (field, value, checked) => {
    const arr = Array.isArray(formData[field]) ? [...formData[field]] : [];
    const next = checked ? (arr.includes(value) ? arr : [...arr, value]) : arr.filter((x) => x !== value);
    setFormData({ ...formData, [field]: next });
  };

  const openCreate = () => {
    setEditingExercise(null);
    setFormData(defaultExerciseForm());
    setShowForm(true);
  };

  const openEdit = async (exercise) => {
    let ex = exercise;
    try {
      const response = await axios.get(
        `${API_BASE}/api/admin/exercises/${exercise.id}`,
        getAxiosConfig()
      );
      ex = response.data || exercise;
    } catch (error) {
      const status = error.response?.status;
      if (status === 404) {
        alert(i18n.language === 'fa' ? 'تمرین یافت نشد. لیست به‌روزرسانی می‌شود.' : 'Exercise not found. Refreshing list.');
        fetchExercises();
        return;
      }
      console.error('Error fetching exercise:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت تمرین' : 'Error fetching exercise');
      return;
    }
    setFormData({
      category: ex.category || 'bodybuilding_machine',
      name_fa: ex.name_fa || '',
      name_en: ex.name_en || '',
      target_muscle_fa: ex.target_muscle_fa || '',
      target_muscle_en: ex.target_muscle_en || '',
      level: ex.level || 'beginner',
      intensity: ex.intensity || 'medium',
      gender_suitability: ex.gender_suitability || 'both',
      execution_tips_fa: ex.execution_tips_fa || '',
      execution_tips_en: ex.execution_tips_en || '',
      breathing_guide_fa: ex.breathing_guide_fa || '',
      breathing_guide_en: ex.breathing_guide_en || '',
      injury_contraindications: Array.isArray(ex.injury_contraindications) ? ex.injury_contraindications : [],
      equipment_needed_fa: ex.equipment_needed_fa || '',
      equipment_needed_en: ex.equipment_needed_en || '',
      video_url: ex.video_url || '',
      image_url: ex.image_url || ''
    });
    setEditingExercise(exercise);
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      category: formData.category,
      name_fa: formData.name_fa.trim(),
      name_en: formData.name_en.trim(),
      target_muscle_fa: formData.target_muscle_fa.trim(),
      target_muscle_en: formData.target_muscle_en.trim(),
      level: formData.level,
      intensity: formData.intensity,
      gender_suitability: formData.gender_suitability,
      execution_tips_fa: formData.execution_tips_fa || null,
      execution_tips_en: formData.execution_tips_en || null,
      breathing_guide_fa: formData.breathing_guide_fa || null,
      breathing_guide_en: formData.breathing_guide_en || null,
      injury_contraindications: formData.injury_contraindications,
      equipment_needed_fa: formData.equipment_needed_fa || null,
      equipment_needed_en: formData.equipment_needed_en || null,
      video_url: formData.video_url || null,
      image_url: formData.image_url || null
    };
    try {
      if (editingExercise) {
        await axios.put(
          `${API_BASE}/api/admin/exercises/${editingExercise.id}`,
          payload,
          getAxiosConfig()
        );
        alert(i18n.language === 'fa' ? 'تمرین به‌روزرسانی شد' : 'Exercise updated');
      } else {
        await axios.post(`${API_BASE}/api/admin/exercises`, payload, getAxiosConfig());
        alert(i18n.language === 'fa' ? 'تمرین ایجاد شد' : 'Exercise created');
      }
      setShowForm(false);
      setEditingExercise(null);
      fetchExercises();
    } catch (error) {
      console.error('Error saving exercise:', error);
      alert(i18n.language === 'fa'
        ? `خطا: ${error.response?.data?.error || error.message}`
        : `Error: ${error.response?.data?.error || error.message}`);
    }
  };

  const handleDelete = async (exercise) => {
    if (!window.confirm(
      i18n.language === 'fa'
        ? `آیا از حذف "${exercise.name_fa || exercise.name_en}" مطمئن هستید؟`
        : `Delete "${exercise.name_fa || exercise.name_en}"?`
    )) return;
    const token = getAuthToken();
    if (!token) {
      alert(i18n.language === 'fa' ? 'ابتدا وارد شوید' : 'Please log in first');
      return;
    }
    try {
      const res = await axios.delete(
        `${API_BASE}/api/admin/exercises/${exercise.id}`,
        getAxiosConfig()
      );
      if (res.status === 200) {
        setExercises((prev) => prev.filter((ex) => ex.id !== exercise.id));
        alert(i18n.language === 'fa' ? 'تمرین حذف شد' : 'Exercise deleted');
        fetchExercises();
        return;
      }
      alert(i18n.language === 'fa' ? 'حذف انجام نشد' : 'Delete did not complete');
    } catch (error) {
      console.error('Error deleting exercise:', error);
      const msg = error.response?.data?.error || error.message || 'Error';
      alert(i18n.language === 'fa' ? `خطا در حذف تمرین: ${msg}` : `Error deleting exercise: ${msg}`);
    }
  };

  const nameLabel = (ex) => (i18n.language === 'fa' ? ex.name_fa : ex.name_en) || ex.name_fa || ex.name_en || '-';

  return (
    <div className="exercise-library-tab" dir="ltr">
      <div className="exercise-library-header">
        <h2>{i18n.language === 'fa' ? 'کتابخانه تمرینات' : 'Exercise Library'}</h2>
        <button type="button" className="btn-primary" onClick={openCreate}>
          {i18n.language === 'fa' ? '+ افزودن تمرین' : '+ Add Exercise'}
        </button>
      </div>

      <div className="exercise-library-info">
        <h3>{i18n.language === 'fa' ? EXERCISES_INFO.title_fa : EXERCISES_INFO.title_en}</h3>
        <p>{i18n.language === 'fa' ? EXERCISES_INFO.intro_fa : EXERCISES_INFO.intro_en}</p>
        <div className="exercise-library-info-grid">
          {EXERCISES_INFO.sections.map((sec, idx) => (
            <div key={idx} className="exercise-library-info-card">
              <h4>{i18n.language === 'fa' ? sec.title_fa : sec.title_en}</h4>
              <ul>
                {(i18n.language === 'fa' ? sec.items_fa : sec.items_en).map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="exercise-library-machine">
        <h3>{i18n.language === 'fa' ? 'حالت ۱ – دستگاهی' : 'Type 1 – Machine'}</h3>
        <p className="exercise-library-machine-desc">
          {i18n.language === 'fa'
            ? 'لیست استاندارد حرکات دستگاهی به تفکیک عضلات (ویرایش و بازبینی).'
            : 'Standard machine exercise list by muscle group (review/edit).'}
        </p>
        <div className="exercise-library-machine-groups">
          {type1Groups.map((group, idx) => (
            <div key={idx} className="exercise-library-machine-group">
              <h4>{group.title}</h4>
              <div className="exercise-library-machine-table-wrap">
                <table className="exercise-library-machine-table">
                  <thead>
                    <tr>
                      <th>{i18n.language === 'fa' ? 'نام حرکت' : 'Exercise name'}</th>
                      <th>{i18n.language === 'fa' ? 'عضله هدف' : 'Target muscle'}</th>
                      <th>{i18n.language === 'fa' ? 'سطح' : 'Level'}</th>
                      <th>{i18n.language === 'fa' ? 'نکات اجرا' : 'Tips'}</th>
                      <th>{i18n.language === 'fa' ? 'تنفس' : 'Breathing'}</th>
                      <th>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.items.map((item) => (
                      <tr key={`${item.name_en}-${item.index}`}>
                        <td>{item.name_en} / {item.name_fa}</td>
                        <td>{item.target_group_en} / {item.target_group_fa}</td>
                        <td>{item.level_fa}</td>
                        <td>{item.tips_fa}</td>
                        <td>{item.breathing_fa}</td>
                        <td>{item.gender_fa}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="exercise-library-machine">
        <h3>{i18n.language === 'fa' ? 'حالت ۲ – فانکشنال بدون دستگاه' : 'Type 2 – Functional (No Equipment)'}</h3>
        <p className="exercise-library-machine-desc">
          {i18n.language === 'fa'
            ? 'لیست استاندارد حرکات فانکشنال بدون دستگاه به تفکیک عضلات (ویرایش و بازبینی).'
            : 'Standard functional (no equipment) exercise list by muscle group (review/edit).'}
        </p>
        <div className="exercise-library-machine-groups">
          {type2Groups.map((group, idx) => (
            <div key={idx} className="exercise-library-machine-group">
              <h4>{group.title}</h4>
              <div className="exercise-library-machine-table-wrap">
                <table className="exercise-library-machine-table">
                  <thead>
                    <tr>
                      <th>{i18n.language === 'fa' ? 'نام حرکت' : 'Exercise name'}</th>
                      <th>{i18n.language === 'fa' ? 'عضله هدف' : 'Target muscle'}</th>
                      <th>{i18n.language === 'fa' ? 'سطح' : 'Level'}</th>
                      <th>{i18n.language === 'fa' ? 'نکات اجرا' : 'Tips'}</th>
                      <th>{i18n.language === 'fa' ? 'تنفس' : 'Breathing'}</th>
                      <th>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.items.map((item) => (
                      <tr key={`${item.name_en}-${item.index}`}>
                        <td>{item.name_en} / {item.name_fa}</td>
                        <td>{item.target_group_en} / {item.target_group_fa}</td>
                        <td>{item.level_fa}</td>
                        <td>{item.tips_fa}</td>
                        <td>{item.breathing_fa}</td>
                        <td>{item.gender_fa}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="exercise-library-machine">
        <h3>{i18n.language === 'fa' ? 'حالت ۳ – ترکیبی (دستگاه + فانکشنال)' : 'Type 3 – Hybrid (Machine + Functional)'}</h3>
        <p className="exercise-library-machine-desc">
          {i18n.language === 'fa'
            ? 'لیست استاندارد حرکات ترکیبی دستگاهی و فانکشنال به تفکیک عضلات (ویرایش و بازبینی).'
            : 'Standard hybrid (machine + functional) exercise list by muscle group (review/edit).'}
        </p>
        <div className="exercise-library-machine-groups">
          {type3Groups.map((group, idx) => (
            <div key={idx} className="exercise-library-machine-group">
              <h4>{group.title}</h4>
              <div className="exercise-library-machine-table-wrap">
                <table className="exercise-library-machine-table">
                  <thead>
                    <tr>
                      <th>{i18n.language === 'fa' ? 'نام حرکت' : 'Exercise name'}</th>
                      <th>{i18n.language === 'fa' ? 'عضله هدف' : 'Target muscle'}</th>
                      <th>{i18n.language === 'fa' ? 'سطح' : 'Level'}</th>
                      <th>{i18n.language === 'fa' ? 'نکات اجرا' : 'Tips'}</th>
                      <th>{i18n.language === 'fa' ? 'تنفس' : 'Breathing'}</th>
                      <th>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.items.map((item) => (
                      <tr key={`${item.name_en}-${item.index}`}>
                        <td>{item.name_en} / {item.name_fa}</td>
                        <td>{item.target_group_en} / {item.target_group_fa}</td>
                        <td>{item.level_fa}</td>
                        <td>{item.tips_fa}</td>
                        <td>{item.breathing_fa}</td>
                        <td>{item.gender_fa}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="exercise-library-filters">
        <select value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}>
          <option value="">{i18n.language === 'fa' ? 'همه دسته‌ها' : 'All categories'}</option>
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>{i18n.language === 'fa' ? c.label_fa : c.label_en}</option>
          ))}
        </select>
        <select value={levelFilter} onChange={(e) => { setLevelFilter(e.target.value); setPage(1); }}>
          <option value="">{i18n.language === 'fa' ? 'همه سطوح' : 'All levels'}</option>
          {LEVELS.map((l) => (
            <option key={l.value} value={l.value}>{i18n.language === 'fa' ? l.label_fa : l.label_en}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
      ) : (
        <>
          <div className="exercise-library-table-wrapper">
            <table className="exercise-library-table">
              <thead>
                <tr>
                  <th>{i18n.language === 'fa' ? 'نام' : 'Name'}</th>
                  <th>{i18n.language === 'fa' ? 'دسته' : 'Category'}</th>
                  <th>{i18n.language === 'fa' ? 'سطح' : 'Level'}</th>
                  <th>{i18n.language === 'fa' ? 'عضله هدف' : 'Target Muscle'}</th>
                  <th>{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {exercises.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="no-data">
                      {i18n.language === 'fa' ? 'تمرینی یافت نشد' : 'No exercises found'}
                    </td>
                  </tr>
                ) : (
                  exercises.map((ex) => (
                    <tr key={ex.id}>
                      <td>{nameLabel(ex)}</td>
                      <td>{CATEGORIES.find((c) => c.value === ex.category)?.[i18n.language === 'fa' ? 'label_fa' : 'label_en'] || ex.category}</td>
                      <td>{LEVELS.find((l) => l.value === ex.level)?.[i18n.language === 'fa' ? 'label_fa' : 'label_en'] || ex.level}</td>
                      <td>{(i18n.language === 'fa' ? ex.target_muscle_fa : ex.target_muscle_en) || ex.target_muscle_fa || ex.target_muscle_en || '-'}</td>
                      <td>
                        <button type="button" className="btn-edit" onClick={() => openEdit(ex)}>
                          {i18n.language === 'fa' ? 'ویرایش' : 'Edit'}
                        </button>
                        <button type="button" className="btn-delete" onClick={() => handleDelete(ex)}>
                          {i18n.language === 'fa' ? 'حذف' : 'Delete'}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="exercise-library-pagination">
              <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                {i18n.language === 'fa' ? 'قبلی' : 'Previous'}
              </button>
              <span>{i18n.language === 'fa' ? `صفحه ${page} از ${totalPages} (${total} مورد)` : `Page ${page} of ${totalPages} (${total} total)`}</span>
              <button type="button" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                {i18n.language === 'fa' ? 'بعدی' : 'Next'}
              </button>
            </div>
          )}
        </>
      )}

      {showForm && (
        <div className="admin-form-overlay exercise-form-overlay">
          <div className="admin-form-container exercise-form-container">
            <div className="form-header-with-close">
              <h3>
                {editingExercise
                  ? (i18n.language === 'fa' ? `ویرایش تمرین: ${formData.name_fa || formData.name_en}` : `Edit Exercise: ${formData.name_fa || formData.name_en}`)
                  : (i18n.language === 'fa' ? 'افزودن تمرین جدید' : 'Add New Exercise')}
              </h3>
              <button type="button" className="close-form-btn" onClick={() => { setShowForm(false); setEditingExercise(null); }} aria-label="Close">×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'دسته *' : 'Category *'}</label>
                  <select value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })} required>
                    {CATEGORIES.map((c) => (
                      <option key={c.value} value={c.value}>{i18n.language === 'fa' ? c.label_fa : c.label_en}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'سطح *' : 'Level *'}</label>
                  <select value={formData.level} onChange={(e) => setFormData({ ...formData, level: e.target.value })} required>
                    {LEVELS.map((l) => (
                      <option key={l.value} value={l.value}>{i18n.language === 'fa' ? l.label_fa : l.label_en}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'شدت *' : 'Intensity *'}</label>
                  <select value={formData.intensity} onChange={(e) => setFormData({ ...formData, intensity: e.target.value })} required>
                    {INTENSITIES.map((i) => (
                      <option key={i.value} value={i.value}>{i18n.language === 'fa' ? i.label_fa : i.label_en}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'مناسب برای *' : 'Gender Suitability *'}</label>
                  <select value={formData.gender_suitability} onChange={(e) => setFormData({ ...formData, gender_suitability: e.target.value })} required>
                    {GENDER_SUITABILITY.map((g) => (
                      <option key={g.value} value={g.value}>{i18n.language === 'fa' ? g.label_fa : g.label_en}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'نام (فارسی) *' : 'Name (FA) *'}</label>
                  <input type="text" value={formData.name_fa} onChange={(e) => setFormData({ ...formData, name_fa: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'نام (انگلیسی) *' : 'Name (EN) *'}</label>
                  <input type="text" value={formData.name_en} onChange={(e) => setFormData({ ...formData, name_en: e.target.value })} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'عضله هدف (فارسی) *' : 'Target Muscle (FA) *'}</label>
                  <input type="text" value={formData.target_muscle_fa} onChange={(e) => setFormData({ ...formData, target_muscle_fa: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'عضله هدف (انگلیسی) *' : 'Target Muscle (EN) *'}</label>
                  <input type="text" value={formData.target_muscle_en} onChange={(e) => setFormData({ ...formData, target_muscle_en: e.target.value })} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'تجهیزات (فارسی)' : 'Equipment (FA)'}</label>
                  <input type="text" value={formData.equipment_needed_fa} onChange={(e) => setFormData({ ...formData, equipment_needed_fa: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'تجهیزات (انگلیسی)' : 'Equipment (EN)'}</label>
                  <input type="text" value={formData.equipment_needed_en} onChange={(e) => setFormData({ ...formData, equipment_needed_en: e.target.value })} />
                </div>
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'ممنوعیت آسیب (انتخاب چندگانه)' : 'Injury Contraindications'}</label>
                <div className="checkbox-group">
                  {INJURY_OPTIONS.map((opt) => (
                    <label key={opt} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={(formData.injury_contraindications || []).includes(opt)}
                        onChange={(e) => handleArrayChange('injury_contraindications', opt, e.target.checked)}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'نکات اجرا (فارسی)' : 'Execution Tips (FA)'}</label>
                <textarea value={formData.execution_tips_fa} onChange={(e) => setFormData({ ...formData, execution_tips_fa: e.target.value })} rows="2" />
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'نکات اجرا (انگلیسی)' : 'Execution Tips (EN)'}</label>
                <textarea value={formData.execution_tips_en} onChange={(e) => setFormData({ ...formData, execution_tips_en: e.target.value })} rows="2" />
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'راهنمای تنفس (فارسی)' : 'Breathing Guide (FA)'}</label>
                <textarea value={formData.breathing_guide_fa} onChange={(e) => setFormData({ ...formData, breathing_guide_fa: e.target.value })} rows="2" />
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'راهنمای تنفس (انگلیسی)' : 'Breathing Guide (EN)'}</label>
                <textarea value={formData.breathing_guide_en} onChange={(e) => setFormData({ ...formData, breathing_guide_en: e.target.value })} rows="2" />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Video URL</label>
                  <input type="url" value={formData.video_url} onChange={(e) => setFormData({ ...formData, video_url: e.target.value })} />
                </div>
                <div className="form-group">
                  <label>Image URL</label>
                  <input type="url" value={formData.image_url} onChange={(e) => setFormData({ ...formData, image_url: e.target.value })} />
                </div>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary">{editingExercise ? (i18n.language === 'fa' ? 'ذخیره' : 'Save') : (i18n.language === 'fa' ? 'ایجاد' : 'Create')}</button>
                <button type="button" className="btn-secondary" onClick={() => { setShowForm(false); setEditingExercise(null); }}>{i18n.language === 'fa' ? 'لغو' : 'Cancel'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExerciseLibraryTab;
