/**
 * Comprehensive Registration Form with Profile Data Collection
 * Collects all required information for personalized AI plans
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import './RegistrationForm.css';

const RegistrationForm = ({ onComplete }) => {
  const { t, i18n } = useTranslation();
  const { register } = useAuth();
  const [step, setStep] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const stepContainerRef = useRef(null);

  // Step 0: Account Type Selection
  const [accountType, setAccountType] = useState('');

  // Step 1: Basic Account Info
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Step 2: Basic Information
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [trainingLevel, setTrainingLevel] = useState('');
  const [exerciseHistoryYears, setExerciseHistoryYears] = useState('');
  const [exerciseHistoryDescription, setExerciseHistoryDescription] = useState('');

  // Step 3: Training Goals
  const [fitnessGoals, setFitnessGoals] = useState([]);

  // Step 4: Limitations & Injuries
  const [injuries, setInjuries] = useState([]);
  const [injuryDetails, setInjuryDetails] = useState('');
  const [medicalConditions, setMedicalConditions] = useState([]);
  const [medicalConditionDetails, setMedicalConditionDetails] = useState('');

  // Step 5: Training Conditions
  const [gymAccess, setGymAccess] = useState(false);
  const [equipmentAccess, setEquipmentAccess] = useState([]);
  const [homeEquipment, setHomeEquipment] = useState([]);
  const [workoutDaysPerWeek, setWorkoutDaysPerWeek] = useState(3);
  const [preferredWorkoutTime, setPreferredWorkoutTime] = useState('');

  const toggleArrayItem = (array, setArray, item) => {
    if (array.includes(item)) {
      setArray(array.filter(i => i !== item));
    } else {
      setArray([...array, item]);
    }
  };

  // Scroll to top when step changes
  useEffect(() => {
    if (stepContainerRef.current) {
      stepContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    // Also scroll the modal content to top
    const modalContent = document.querySelector('.auth-modal-content');
    if (modalContent) {
      modalContent.scrollTop = 0;
    }
  }, [step]);

  const handleStepChange = (newStep) => {
    setStep(newStep);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Step 0: Account type selection
    if (step === 0) {
      if (!accountType) {
        setError(i18n.language === 'fa' ? 'لطفاً نوع حساب کاربری خود را انتخاب کنید' : 'Please select your account type');
        return;
      }
      handleStepChange(step + 1);
      return;
    }
    
    if (step < 6) {
      handleStepChange(step + 1);
      return;
    }

    // Final step - submit registration
    if (password !== confirmPassword) {
      setError(i18n.language === 'fa' ? 'رمز عبور و تأیید رمز عبور مطابقت ندارند' : 'Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    const profileData = {
      account_type: accountType,
      age: age ? parseInt(age) : null,
      gender: gender,
      height: height ? parseFloat(height) : null,
      weight: weight ? parseFloat(weight) : null,
      training_level: trainingLevel,
      exercise_history_years: exerciseHistoryYears ? parseInt(exerciseHistoryYears) : null,
      exercise_history_description: exerciseHistoryDescription,
      fitness_goals: fitnessGoals,
      injuries: injuries,
      injury_details: injuryDetails,
      medical_conditions: medicalConditions,
      medical_condition_details: medicalConditionDetails,
      gym_access: gymAccess,
      equipment_access: equipmentAccess,
      home_equipment: homeEquipment,
      workout_days_per_week: workoutDaysPerWeek,
      preferred_workout_time: preferredWorkoutTime
    };

    const result = await register(username, email, password, i18n.language, profileData);
    
    setLoading(false);
    if (!result.success) {
      setError(result.error);
    } else if (onComplete) {
      onComplete();
    }
  };

  const renderStep0 = () => (
    <div className="registration-step">
      <h3>{i18n.language === 'fa' ? 'نوع حساب کاربری' : 'Account Type'}</h3>
      <p className="step-description">
        {i18n.language === 'fa' 
          ? 'لطفاً نوع حساب کاربری خود را انتخاب کنید'
          : 'Please select your account type'}
      </p>
      <div className="account-type-selection">
        <label className={`account-type-option ${accountType === 'trainer' ? 'selected' : ''}`}>
          <input
            type="radio"
            name="accountType"
            value="trainer"
            checked={accountType === 'trainer'}
            onChange={(e) => setAccountType(e.target.value)}
            required
          />
          <div className="account-type-content">
            <span className="account-type-title">{i18n.language === 'fa' ? 'مربی' : 'Trainer'}</span>
            <span className="account-type-description">
              {i18n.language === 'fa' 
                ? 'من یک مربی هستم و می‌خواهم برنامه‌های تمرینی برای دیگران ایجاد کنم'
                : 'I am a trainer and want to create training programs for others'}
            </span>
          </div>
        </label>
        <label className={`account-type-option ${accountType === 'member' ? 'selected' : ''}`}>
          <input
            type="radio"
            name="accountType"
            value="member"
            checked={accountType === 'member'}
            onChange={(e) => setAccountType(e.target.value)}
            required
          />
          <div className="account-type-content">
            <span className="account-type-title">{i18n.language === 'fa' ? 'عضو' : 'Member'}</span>
            <span className="account-type-description">
              {i18n.language === 'fa' 
                ? 'من می‌خواهم تمرین کنم و برنامه‌های تمرینی دریافت کنم'
                : 'I want to train and receive training programs'}
            </span>
          </div>
        </label>
      </div>
    </div>
  );

  const renderStep1 = () => (
    <div className="registration-step">
      <h3>{i18n.language === 'fa' ? 'اطلاعات حساب کاربری' : 'Account Information'}</h3>
      <div className="form-group">
        <label>{t('username')}</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label>{t('email')}</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label>{t('password')}</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
        />
      </div>
      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'تأیید رمز عبور' : 'Confirm Password'}</label>
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="registration-step">
      <h3>{i18n.language === 'fa' ? 'اطلاعات پایه' : 'Basic Information'}</h3>
      <div className="form-row">
        <div className="form-group">
          <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            min="10"
            max="100"
          />
        </div>
        <div className="form-group">
          <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
          <select value={gender} onChange={(e) => setGender(e.target.value)}>
            <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
            <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
            <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
            <option value="other">{i18n.language === 'fa' ? 'سایر' : 'Other'}</option>
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
          <input
            type="number"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            min="100"
            max="250"
          />
        </div>
        <div className="form-group">
          <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
          <input
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            min="30"
            max="300"
            step="0.1"
          />
        </div>
      </div>
      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'سطح آمادگی' : 'Fitness Level'}</label>
        <select value={trainingLevel} onChange={(e) => setTrainingLevel(e.target.value)}>
          <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
          <option value="beginner">{i18n.language === 'fa' ? 'مبتدی' : 'Beginner'}</option>
          <option value="intermediate">{i18n.language === 'fa' ? 'متوسط' : 'Intermediate'}</option>
          <option value="advanced">{i18n.language === 'fa' ? 'حرفه‌ای' : 'Advanced'}</option>
        </select>
      </div>
      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'سابقه ورزشی (سال)' : 'Exercise History (Years)'}</label>
        <input
          type="number"
          value={exerciseHistoryYears}
          onChange={(e) => setExerciseHistoryYears(e.target.value)}
          min="0"
          max="50"
        />
      </div>
      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'توضیح سابقه ورزشی' : 'Exercise History Description'}</label>
        <textarea
          value={exerciseHistoryDescription}
          onChange={(e) => setExerciseHistoryDescription(e.target.value)}
          rows={3}
          placeholder={i18n.language === 'fa' ? 'سابقه تمرینات قبلی خود را شرح دهید...' : 'Describe your previous exercise experience...'}
        />
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="registration-step">
      <h3>{i18n.language === 'fa' ? 'هدف تمرینی' : 'Training Goals'}</h3>
      <p className="step-description">
        {i18n.language === 'fa' 
          ? 'لطفاً اهداف خود را انتخاب کنید (می‌توانید چند مورد را انتخاب کنید)'
          : 'Please select your goals (you can select multiple)'}
      </p>
      <div className="checkbox-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={fitnessGoals.includes('lose_weight')}
            onChange={() => toggleArrayItem(fitnessGoals, setFitnessGoals, 'lose_weight')}
          />
          <span>{i18n.language === 'fa' ? 'کاهش وزن' : 'Lose Weight'}</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={fitnessGoals.includes('gain_weight')}
            onChange={() => toggleArrayItem(fitnessGoals, setFitnessGoals, 'gain_weight')}
          />
          <span>{i18n.language === 'fa' ? 'افزایش وزن' : 'Gain Weight'}</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={fitnessGoals.includes('gain_muscle')}
            onChange={() => toggleArrayItem(fitnessGoals, setFitnessGoals, 'gain_muscle')}
          />
          <span>{i18n.language === 'fa' ? 'افزایش عضله' : 'Gain Muscle'}</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={fitnessGoals.includes('shape_fitting')}
            onChange={() => toggleArrayItem(fitnessGoals, setFitnessGoals, 'shape_fitting')}
          />
          <span>{i18n.language === 'fa' ? 'تناسب اندام' : 'Shape Fitting'}</span>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={fitnessGoals.includes('healthy_diet')}
            onChange={() => toggleArrayItem(fitnessGoals, setFitnessGoals, 'healthy_diet')}
          />
          <span>{i18n.language === 'fa' ? 'رژیم غذایی سالم' : 'Healthy Diet'}</span>
        </label>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="registration-step">
      <h3>{i18n.language === 'fa' ? 'محدودیت‌ها و آسیب‌ها' : 'Limitations & Injuries'}</h3>
      <p className="step-description">
        {i18n.language === 'fa' 
          ? 'لطفاً آسیب‌ها و محدودیت‌های خود را مشخص کنید تا برنامه‌های ایمن برای شما طراحی شود'
          : 'Please specify your injuries and limitations so we can create safe programs for you'}
      </p>
      
      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'آسیب‌ها' : 'Injuries'}</label>
        <div className="checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={injuries.includes('knee')}
              onChange={() => toggleArrayItem(injuries, setInjuries, 'knee')}
            />
            <span>{i18n.language === 'fa' ? 'زانو' : 'Knee'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={injuries.includes('shoulder')}
              onChange={() => toggleArrayItem(injuries, setInjuries, 'shoulder')}
            />
            <span>{i18n.language === 'fa' ? 'شانه' : 'Shoulder'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={injuries.includes('lower_back')}
              onChange={() => toggleArrayItem(injuries, setInjuries, 'lower_back')}
            />
            <span>{i18n.language === 'fa' ? 'کمر' : 'Lower Back'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={injuries.includes('neck')}
              onChange={() => toggleArrayItem(injuries, setInjuries, 'neck')}
            />
            <span>{i18n.language === 'fa' ? 'گردن' : 'Neck'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={injuries.includes('wrist')}
              onChange={() => toggleArrayItem(injuries, setInjuries, 'wrist')}
            />
            <span>{i18n.language === 'fa' ? 'مچ دست' : 'Wrist'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={injuries.includes('ankle')}
              onChange={() => toggleArrayItem(injuries, setInjuries, 'ankle')}
            />
            <span>{i18n.language === 'fa' ? 'مچ پا' : 'Ankle'}</span>
          </label>
        </div>
      </div>

      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'توضیحات آسیب' : 'Injury Details'}</label>
        <textarea
          value={injuryDetails}
          onChange={(e) => setInjuryDetails(e.target.value)}
          rows={3}
          placeholder={i18n.language === 'fa' ? 'جزئیات آسیب‌های خود را شرح دهید...' : 'Describe your injuries in detail...'}
        />
      </div>

      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'بیماری‌ها و شرایط پزشکی' : 'Medical Conditions'}</label>
        <div className="checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={medicalConditions.includes('heart_disease')}
              onChange={() => toggleArrayItem(medicalConditions, setMedicalConditions, 'heart_disease')}
            />
            <span>{i18n.language === 'fa' ? 'بیماری قلبی' : 'Heart Disease'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={medicalConditions.includes('high_blood_pressure')}
              onChange={() => toggleArrayItem(medicalConditions, setMedicalConditions, 'high_blood_pressure')}
            />
            <span>{i18n.language === 'fa' ? 'فشار خون بالا' : 'High Blood Pressure'}</span>
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={medicalConditions.includes('pregnancy')}
              onChange={() => toggleArrayItem(medicalConditions, setMedicalConditions, 'pregnancy')}
            />
            <span>{i18n.language === 'fa' ? 'بارداری' : 'Pregnancy'}</span>
          </label>
        </div>
      </div>

      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'توضیحات شرایط پزشکی' : 'Medical Condition Details'}</label>
        <textarea
          value={medicalConditionDetails}
          onChange={(e) => setMedicalConditionDetails(e.target.value)}
          rows={3}
          placeholder={i18n.language === 'fa' ? 'جزئیات شرایط پزشکی خود را شرح دهید...' : 'Describe your medical conditions in detail...'}
        />
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="registration-step">
      <h3>{i18n.language === 'fa' ? 'شرایط تمرینی' : 'Training Conditions'}</h3>
      
      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={gymAccess}
            onChange={(e) => setGymAccess(e.target.checked)}
          />
          <span>{i18n.language === 'fa' ? 'دسترسی به باشگاه' : 'Gym Access'}</span>
        </label>
      </div>

      {gymAccess && (
        <div className="form-group">
          <label>{i18n.language === 'fa' ? 'تجهیزات باشگاه' : 'Gym Equipment'}</label>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={equipmentAccess.includes('machine')}
                onChange={() => toggleArrayItem(equipmentAccess, setEquipmentAccess, 'machine')}
              />
              <span>{i18n.language === 'fa' ? 'دستگاه' : 'Machines'}</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={equipmentAccess.includes('dumbbells')}
                onChange={() => toggleArrayItem(equipmentAccess, setEquipmentAccess, 'dumbbells')}
              />
              <span>{i18n.language === 'fa' ? 'دمبل' : 'Dumbbells'}</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={equipmentAccess.includes('barbell')}
                onChange={() => toggleArrayItem(equipmentAccess, setEquipmentAccess, 'barbell')}
              />
              <span>{i18n.language === 'fa' ? 'هالتر' : 'Barbell'}</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={equipmentAccess.includes('cable')}
                onChange={() => toggleArrayItem(equipmentAccess, setEquipmentAccess, 'cable')}
              />
              <span>{i18n.language === 'fa' ? 'کابل' : 'Cable Machine'}</span>
            </label>
          </div>
        </div>
      )}

      {!gymAccess && (
        <div className="form-group">
          <label>{i18n.language === 'fa' ? 'تجهیزات خانگی' : 'Home Equipment'}</label>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={homeEquipment.includes('dumbbells')}
                onChange={() => toggleArrayItem(homeEquipment, setHomeEquipment, 'dumbbells')}
              />
              <span>{i18n.language === 'fa' ? 'دمبل' : 'Dumbbells'}</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={homeEquipment.includes('resistance_bands')}
                onChange={() => toggleArrayItem(homeEquipment, setHomeEquipment, 'resistance_bands')}
              />
              <span>{i18n.language === 'fa' ? 'باند مقاومتی' : 'Resistance Bands'}</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={homeEquipment.includes('yoga_mat')}
                onChange={() => toggleArrayItem(homeEquipment, setHomeEquipment, 'yoga_mat')}
              />
              <span>{i18n.language === 'fa' ? 'تشک یوگا' : 'Yoga Mat'}</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={homeEquipment.includes('body_weight_only')}
                onChange={() => toggleArrayItem(homeEquipment, setHomeEquipment, 'body_weight_only')}
              />
              <span>{i18n.language === 'fa' ? 'فقط وزن بدن' : 'Body Weight Only'}</span>
            </label>
          </div>
        </div>
      )}

      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'روزهای تمرین در هفته' : 'Workout Days Per Week'}</label>
        <select value={workoutDaysPerWeek} onChange={(e) => setWorkoutDaysPerWeek(parseInt(e.target.value))}>
          {[1, 2, 3, 4, 5, 6, 7].map(days => (
            <option key={days} value={days}>{days}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>{i18n.language === 'fa' ? 'زمان ترجیحی تمرین' : 'Preferred Workout Time'}</label>
        <select value={preferredWorkoutTime} onChange={(e) => setPreferredWorkoutTime(e.target.value)}>
          <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
          <option value="morning">{i18n.language === 'fa' ? 'صبح' : 'Morning'}</option>
          <option value="afternoon">{i18n.language === 'fa' ? 'بعد از ظهر' : 'Afternoon'}</option>
          <option value="evening">{i18n.language === 'fa' ? 'عصر' : 'Evening'}</option>
        </select>
      </div>
    </div>
  );

  return (
    <div className="registration-form-container">
      <div className="registration-progress">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${((step + 1) / 6) * 100}%` }}></div>
        </div>
        <div className="progress-steps">
          {[0, 1, 2, 3, 4, 5].map(s => (
            <div
              key={s}
              className={`progress-step ${s <= step ? 'active' : ''} ${s < step ? 'clickable' : ''}`}
              onClick={() => {
                // Only allow clicking on steps that have been reached (previous steps)
                if (s < step) {
                  handleStepChange(s);
                }
              }}
              style={{
                cursor: s < step ? 'pointer' : 'default',
                opacity: s > step ? 0.5 : 1
              }}
            >
              {s + 1}
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="registration-form">
        {error && <div className="error-message">{error}</div>}

        <div ref={stepContainerRef}>
          {step === 0 && renderStep0()}
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
          {step === 5 && renderStep5()}
        </div>

        <div className="form-actions">
          {step > 0 && (
            <button type="button" className="btn-secondary" onClick={() => handleStepChange(step - 1)}>
              {i18n.language === 'fa' ? 'قبلی' : 'Previous'}
            </button>
          )}
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading
              ? t('loading')
              : step === 5
              ? (i18n.language === 'fa' ? 'ثبت نام و تکمیل' : 'Register & Complete')
              : (i18n.language === 'fa' ? 'بعدی' : 'Next')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RegistrationForm;



