import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './TrainingLevelsInfoTab.css';

const TrainingLevelsInfoTab = () => {
  const { t, i18n } = useTranslation();
  const [trainingLevels, setTrainingLevels] = useState({
    beginner: { description_fa: '', description_en: '' },
    intermediate: { description_fa: '', description_en: '' },
    advanced: { description_fa: '', description_en: '' }
  });
  const [injuries, setInjuries] = useState({
    knee: { description_fa: '', description_en: '', prevention_fa: '', prevention_en: '' },
    shoulder: { description_fa: '', description_en: '', prevention_fa: '', prevention_en: '' },
    lower_back: { description_fa: '', description_en: '', prevention_fa: '', prevention_en: '' },
    neck: { description_fa: '', description_en: '', prevention_fa: '', prevention_en: '' },
    wrist: { description_fa: '', description_en: '', prevention_fa: '', prevention_en: '' },
    ankle: { description_fa: '', description_en: '', prevention_fa: '', prevention_en: '' }
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
      const response = await axios.get('http://localhost:5000/api/admin/config', getAxiosConfig());
      if (response.data.training_levels) {
        setTrainingLevels(response.data.training_levels);
      }
      if (response.data.injuries) {
        setInjuries(response.data.injuries);
      }
    } catch (error) {
      console.error('Error fetching configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfiguration = async () => {
    try {
      await axios.post('http://localhost:5000/api/admin/config', {
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
          <div className="config-section">
            <h3>{i18n.language === 'fa' ? 'سطح‌های تمرین' : 'Training Levels'}</h3>
            {Object.keys(trainingLevels).map(level => (
              <div key={level} className="config-item">
                <h4>{i18n.language === 'fa' 
                  ? (level === 'beginner' ? 'مبتدی' : level === 'intermediate' ? 'متوسط' : 'پیشرفته')
                  : level.charAt(0).toUpperCase() + level.slice(1)}
                </h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'توضیحات (فارسی)' : 'Description (Persian)'}</label>
                    <textarea
                      value={trainingLevels[level].description_fa || ''}
                      onChange={(e) => setTrainingLevels({
                        ...trainingLevels,
                        [level]: {...trainingLevels[level], description_fa: e.target.value}
                      })}
                      rows="3"
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'توضیحات (انگلیسی)' : 'Description (English)'}</label>
                    <textarea
                      value={trainingLevels[level].description_en || ''}
                      onChange={(e) => setTrainingLevels({
                        ...trainingLevels,
                        [level]: {...trainingLevels[level], description_en: e.target.value}
                      })}
                      rows="3"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="config-section">
            <h3>{i18n.language === 'fa' ? 'آسیب‌ها' : 'Injuries'}</h3>
            {Object.keys(injuries).map(injury => (
              <div key={injury} className="config-item">
                <h4>{i18n.language === 'fa' 
                  ? (injury === 'knee' ? 'زانو' : injury === 'shoulder' ? 'شانه' : injury === 'lower_back' ? 'کمر' : injury === 'neck' ? 'گردن' : injury === 'wrist' ? 'مچ دست' : 'مچ پا')
                  : injury.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'توضیحات (فارسی)' : 'Description (Persian)'}</label>
                    <textarea
                      value={injuries[injury].description_fa || ''}
                      onChange={(e) => setInjuries({
                        ...injuries,
                        [injury]: {...injuries[injury], description_fa: e.target.value}
                      })}
                      rows="2"
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'توضیحات (انگلیسی)' : 'Description (English)'}</label>
                    <textarea
                      value={injuries[injury].description_en || ''}
                      onChange={(e) => setInjuries({
                        ...injuries,
                        [injury]: {...injuries[injury], description_en: e.target.value}
                      })}
                      rows="2"
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'پیشگیری (فارسی)' : 'Prevention (Persian)'}</label>
                    <textarea
                      value={injuries[injury].prevention_fa || ''}
                      onChange={(e) => setInjuries({
                        ...injuries,
                        [injury]: {...injuries[injury], prevention_fa: e.target.value}
                      })}
                      rows="2"
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'پیشگیری (انگلیسی)' : 'Prevention (English)'}</label>
                    <textarea
                      value={injuries[injury].prevention_en || ''}
                      onChange={(e) => setInjuries({
                        ...injuries,
                        [injury]: {...injuries[injury], prevention_en: e.target.value}
                      })}
                      rows="2"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingLevelsInfoTab;
