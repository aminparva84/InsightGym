import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import './TrainingProgramsModal.css';

const BASE_PROGRAMS = [
  { id: 1, nameKey: 'trainingProgram1', descriptionKey: 'trainingProgram1Desc', price: 99, icon: '💪', features: ['feature1', 'feature2', 'feature3'] },
  { id: 2, nameKey: 'trainingProgram2', descriptionKey: 'trainingProgram2Desc', price: 149, icon: '🔥', features: ['feature1', 'feature2', 'feature3', 'feature4'] },
  { id: 3, nameKey: 'trainingProgram3', descriptionKey: 'trainingProgram3Desc', price: 199, icon: '⭐', features: ['feature1', 'feature2', 'feature3', 'feature4', 'feature5'] },
  { id: 4, nameKey: 'trainingProgramEms', descriptionKey: 'trainingProgramEmsDesc', price: 249, icon: '⚡', features: [], isEms: true }
];

const PACKAGE_OPTIONS = [
  { id: 'vip', nameKey: 'packageVip', price: 80 },
  { id: 'weeklyPlan', nameKey: 'packageWeeklyPlan', price: 25 },
  { id: 'nutrition', nameKey: 'packageNutrition', price: 30 },
  { id: 'onlineSupport', nameKey: 'packageOnlineSupport', price: 25 },
  { id: 'progressTracking', nameKey: 'packageProgressTracking', price: 20 },
  { id: 'personalCoaching', nameKey: 'packagePersonalCoaching', price: 50 },
  { id: 'lifetimeAccess', nameKey: 'packageLifetimeAccess', price: 100 },
  { id: 'assessment', nameKey: 'packageAssessment', price: 40 },
  { id: 'months3', nameKey: 'packageMonths3', price: 60 }
];

const EMS_FORM_DEFAULTS = {
  pregnancy: false, pacemaker: false, epilepsy: false, thrombosis: false, hernia: false,
  infection: false, bleeding: false, medications: '', areasFocus: '', otherLimits: '', fitnessLevel: '', goals: ''
};

const TrainingProgramsModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [selectedProgramId, setSelectedProgramId] = useState(1);
  const [selectedPackages, setSelectedPackages] = useState({});
  const [emsStep, setEmsStep] = useState(0);
  const [emsForm, setEmsForm] = useState(EMS_FORM_DEFAULTS);

  const isEmsSelected = selectedProgramId === 4;
  const basePrice = useMemo(() => {
    const program = BASE_PROGRAMS.find((p) => p.id === selectedProgramId);
    return program ? program.price : 0;
  }, [selectedProgramId]);

  const packagesTotal = useMemo(() => {
    return PACKAGE_OPTIONS.reduce((sum, pkg) => {
      return sum + (selectedPackages[pkg.id] ? pkg.price : 0);
    }, 0);
  }, [selectedPackages]);

  const totalPrice = basePrice + packagesTotal;

  const handleClose = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const togglePackage = (id) => {
    setSelectedPackages((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleSelectProgram = (id) => {
    setSelectedProgramId(id);
    setEmsStep(id === 4 ? 1 : 0);
  };

  const handleBuyNow = () => {
    const program = BASE_PROGRAMS.find((p) => p.id === selectedProgramId);
    const packages = PACKAGE_OPTIONS.filter((pkg) => selectedPackages[pkg.id]).map((pkg) => ({
      id: pkg.id,
      nameKey: pkg.nameKey,
      price: pkg.price,
    }));
    const payload = {
      program: program || null,
      packages,
      emsForm: isEmsSelected ? emsForm : null,
    };
    try {
      localStorage.setItem('pendingPurchase', JSON.stringify(payload));
    } catch (err) {
      console.error('Could not save pending purchase:', err);
    }
    onClose();
    navigate('/purchase', { state: payload });
  };

  if (!isOpen) return null;

  const isRtl = i18n.language === 'fa';

  return (
    <div className="training-programs-modal-overlay" onClick={handleClose}>
      <div className="training-programs-modal" onClick={(e) => e.stopPropagation()} dir={isRtl ? 'rtl' : 'ltr'}>
        <button className="training-programs-modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className="training-programs-modal-header">
          <h2 className="training-programs-modal-title">
            {t('buyTrainingProgramme')}
          </h2>
          <p className="training-programs-modal-subtitle">
            {isRtl ? 'برنامه پایه و بسته‌های مورد نظر را انتخاب کنید' : 'Choose your base program and the packages you want'}
          </p>
        </div>

        {isEmsSelected && emsStep === 1 ? (
          <div className="training-programs-modal-body training-programs-ems-intro">
            <div className="ems-intro-image">
              <div className="ems-intro-image-placeholder">⚡ EMS</div>
            </div>
            <h3 className="ems-intro-title">EMS – {i18n.language === 'fa' ? 'تحریک الکتریکی عضله' : 'Electrical Muscle Stimulation'}</h3>
            <p className="ems-intro-text">{t('emsWhatIs')}</p>
            <div className="training-programs-footer">
              <button type="button" className="program-buy-btn secondary" onClick={() => setEmsStep(0)}>
                {t('emsBackToPlans')}
              </button>
              <button type="button" className="program-buy-btn" onClick={() => setEmsStep(2)}>
                {t('emsNextStep')}
              </button>
            </div>
          </div>
        ) : isEmsSelected && emsStep === 2 ? (
          <div className="training-programs-modal-body training-programs-ems-form">
            <h3 className="training-programs-section-title">{t('emsFormTitle')}</h3>
            <div className="ems-form-grid">
              {['pregnancy', 'pacemaker', 'epilepsy', 'thrombosis', 'hernia', 'infection', 'bleeding'].map((key) => (
                <label key={key} className="ems-form-check">
                  <input type="checkbox" checked={!!emsForm[key]} onChange={(e) => setEmsForm(prev => ({ ...prev, [key]: e.target.checked }))} />
                  <span>{t('ems' + key.charAt(0).toUpperCase() + key.slice(1))}</span>
                </label>
              ))}
            </div>
            <div className="ems-form-fields">
              <div className="form-group">
                <label>{t('emsMedications')}</label>
                <input type="text" value={emsForm.medications} onChange={(e) => setEmsForm(prev => ({ ...prev, medications: e.target.value }))} placeholder={isRtl ? 'داروهای فعلی' : 'Current medications'} />
              </div>
              <div className="form-group">
                <label>{t('emsAreasFocus')}</label>
                <input type="text" value={emsForm.areasFocus} onChange={(e) => setEmsForm(prev => ({ ...prev, areasFocus: e.target.value }))} placeholder={isRtl ? 'مناطق تمرین' : 'Body areas'} />
              </div>
              <div className="form-group">
                <label>{t('emsFitnessLevel')}</label>
                <input type="text" value={emsForm.fitnessLevel} onChange={(e) => setEmsForm(prev => ({ ...prev, fitnessLevel: e.target.value }))} placeholder={isRtl ? 'مبتدی / متوسط / پیشرفته' : 'Beginner / Intermediate / Advanced'} />
              </div>
              <div className="form-group">
                <label>{t('emsGoals')}</label>
                <input type="text" value={emsForm.goals} onChange={(e) => setEmsForm(prev => ({ ...prev, goals: e.target.value }))} placeholder={isRtl ? 'اهداف' : 'Goals'} />
              </div>
              <div className="form-group full-width">
                <label>{t('emsOtherLimits')}</label>
                <textarea rows={2} value={emsForm.otherLimits} onChange={(e) => setEmsForm(prev => ({ ...prev, otherLimits: e.target.value }))} placeholder={isRtl ? 'سایر محدودیت‌ها' : 'Other limitations'} />
              </div>
            </div>
            <div className="training-programs-footer">
              <button type="button" className="program-buy-btn secondary" onClick={() => setEmsStep(0)}>
                {t('emsBackToPlans')}
              </button>
              <div className="training-programs-total">
                <span className="training-programs-total-label">{t('totalPrice')}</span>
                <span className="training-programs-total-value">${basePrice}</span>
              </div>
              <button type="button" className="program-buy-btn training-programs-buy-btn" onClick={handleBuyNow}>
                {t('buyNow')}
              </button>
            </div>
          </div>
        ) : (
          <div className="training-programs-modal-body">
            <section className="training-programs-base-section">
              <h3 className="training-programs-section-title">
                {isRtl ? 'برنامه پایه' : 'Base program'}
              </h3>
              <div className="training-programs-grid training-programs-grid-base">
                {BASE_PROGRAMS.map((program) => (
                  <button
                    key={program.id}
                    type="button"
                    className={`training-program-card ${selectedProgramId === program.id ? 'selected' : ''}`}
                    onClick={() => handleSelectProgram(program.id)}
                  >
                    <div className="program-icon">{program.icon}</div>
                    <h4 className="program-name">{t(program.nameKey)}</h4>
                    <p className="program-description">{t(program.descriptionKey)}</p>
                    {program.features && program.features.length > 0 && (
                      <ul className="program-features">
                        {program.features.map((featureKey, index) => (
                          <li key={index}>{t(featureKey)}</li>
                        ))}
                      </ul>
                    )}
                    <div className="program-price">${program.price}</div>
                  </button>
                ))}
              </div>
            </section>

            <section className="training-programs-packages-section">
              <h3 className="training-programs-section-title">{t('selectPackages')}</h3>
              <ul className="training-programs-packages-list">
                {PACKAGE_OPTIONS.map((pkg) => (
                  <li key={pkg.id} className="training-programs-package-item">
                    <label className="training-programs-package-label">
                      <input
                        type="checkbox"
                        checked={!!selectedPackages[pkg.id]}
                        onChange={() => togglePackage(pkg.id)}
                        className="training-programs-package-checkbox"
                      />
                      <span className="training-programs-package-name">{t(pkg.nameKey)}</span>
                      <span className="training-programs-package-price">+${pkg.price}</span>
                    </label>
                  </li>
                ))}
              </ul>
            </section>

            <div className="training-programs-footer">
              <div className="training-programs-total">
                <span className="training-programs-total-label">{t('totalPrice')}</span>
                <span className="training-programs-total-value">${totalPrice}</span>
              </div>
              <button
                type="button"
                className="program-buy-btn training-programs-buy-btn"
                onClick={handleBuyNow}
              >
                {t('buyNow')}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainingProgramsModal;
