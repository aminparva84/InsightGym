/**
 * Comprehensive Registration Form with Profile Data Collection
 * Collects all required information for personalized AI plans
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import './RegistrationForm.css';

// Injury types (all 6 body locations)
const INJURY_KEYS = ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle'];
const INJURY_LABELS = {
  knee: { fa: 'زانو', en: 'Knee' },
  shoulder: { fa: 'شانه', en: 'Shoulder' },
  lower_back: { fa: 'کمر', en: 'Lower Back' },
  neck: { fa: 'گردن', en: 'Neck' },
  wrist: { fa: 'مچ دست', en: 'Wrist' },
  ankle: { fa: 'مچ پا', en: 'Ankle' }
};

// Follow-up questions per injury (FA + EN)
const INJURY_QUESTIONS = {
  knee: {
    label: { fa: 'زانو', en: 'Knee' },
    questions: [
      { key: 'when_started', fa: 'از چه زمانی شروع شده؟', en: 'When did it start?', type: 'radio', options: [
        { value: 'last_month', fa: 'ماه گذشته', en: 'Last month' },
        { value: '3_6_months', fa: '۳ تا ۶ ماه پیش', en: '3–6 months ago' },
        { value: '6_12_months', fa: '۶ تا ۱۲ ماه پیش', en: '6–12 months ago' },
        { value: 'over_year', fa: 'بیش از یک سال', en: 'Over 1 year ago' }
      ]},
      { key: 'severity', fa: 'شدت درد یا محدودیت؟', en: 'Severity of pain or limitation?', type: 'radio', options: [
        { value: 'mild', fa: 'خفیف', en: 'Mild' },
        { value: 'moderate', fa: 'متوسط', en: 'Moderate' },
        { value: 'severe', fa: 'شدید', en: 'Severe' }
      ]},
      { key: 'location', fa: 'درد در کدام قسمت زانو؟', en: 'Where is the knee pain?', type: 'radio', options: [
        { value: 'front', fa: 'جلو', en: 'Front' },
        { value: 'back', fa: 'پشت', en: 'Back' },
        { value: 'inside', fa: 'داخل', en: 'Inside' },
        { value: 'outside', fa: 'خارج', en: 'Outside' }
      ]},
      { key: 'pain_squat', fa: 'هنگام اسکوات درد داری؟', en: 'Do you have pain during squat?', type: 'yesno' },
      { key: 'pain_stairs', fa: 'هنگام بالا رفتن از پله درد داری؟', en: 'Do you have pain when climbing stairs?', type: 'yesno' },
      { key: 'surgery', fa: 'جراحی داشتی؟', en: 'Have you had surgery?', type: 'yesno' },
      { key: 'clicking', fa: 'صدا یا قفل شدن زانو داری؟', en: 'Do you have clicking or locking of the knee?', type: 'yesno' }
    ]
  },
  shoulder: {
    label: { fa: 'شانه', en: 'Shoulder' },
    questions: [
      { key: 'when_started', fa: 'از چه زمانی شروع شده؟', en: 'When did it start?', type: 'radio', options: [
        { value: 'last_month', fa: 'ماه گذشته', en: 'Last month' },
        { value: '3_6_months', fa: '۳ تا ۶ ماه پیش', en: '3–6 months ago' },
        { value: '6_12_months', fa: '۶ تا ۱۲ ماه پیش', en: '6–12 months ago' },
        { value: 'over_year', fa: 'بیش از یک سال', en: 'Over 1 year ago' }
      ]},
      { key: 'severity', fa: 'شدت درد یا محدودیت؟', en: 'Severity?', type: 'radio', options: [
        { value: 'mild', fa: 'خفیف', en: 'Mild' },
        { value: 'moderate', fa: 'متوسط', en: 'Moderate' },
        { value: 'severe', fa: 'شدید', en: 'Severe' }
      ]},
      { key: 'pain_raise_arm', fa: 'درد هنگام بالا بردن دست؟', en: 'Pain when raising your arm?', type: 'yesno' },
      { key: 'pain_bench', fa: 'درد در پرس سینه یا سرشانه؟', en: 'Pain during bench press or overhead press?', type: 'yesno' },
      { key: 'dislocation', fa: 'دررفتگی سابقه دارد؟', en: 'History of dislocation?', type: 'yesno' }
    ]
  },
  lower_back: {
    label: { fa: 'کمر', en: 'Lower Back' },
    questions: [
      { key: 'when_started', fa: 'از چه زمانی شروع شده؟', en: 'When did it start?', type: 'radio', options: [
        { value: 'last_month', fa: 'ماه گذشته', en: 'Last month' },
        { value: '3_6_months', fa: '۳ تا ۶ ماه پیش', en: '3–6 months ago' },
        { value: '6_12_months', fa: '۶ تا ۱۲ ماه پیش', en: '6–12 months ago' },
        { value: 'over_year', fa: 'بیش از یک سال', en: 'Over 1 year ago' }
      ]},
      { key: 'severity', fa: 'شدت درد یا محدودیت؟', en: 'Severity?', type: 'radio', options: [
        { value: 'mild', fa: 'خفیف', en: 'Mild' },
        { value: 'moderate', fa: 'متوسط', en: 'Moderate' },
        { value: 'severe', fa: 'شدید', en: 'Severe' }
      ]},
      { key: 'disc', fa: 'دیسک داری؟', en: 'Do you have disc issue?', type: 'yesno' },
      { key: 'lordosis', fa: 'گودی کمر؟', en: 'Excessive lower back curve (lordosis)?', type: 'yesno' },
      { key: 'pain_bending', fa: 'درد هنگام خم شدن؟', en: 'Pain when bending?', type: 'yesno' },
      { key: 'radiating', fa: 'درد تیرکشنده به پا؟', en: 'Radiating pain to the leg?', type: 'yesno' }
    ]
  },
  neck: {
    label: { fa: 'گردن', en: 'Neck' },
    questions: [
      { key: 'when_started', fa: 'از چه زمانی شروع شده؟', en: 'When did it start?', type: 'radio', options: [
        { value: 'last_month', fa: 'ماه گذشته', en: 'Last month' },
        { value: '3_6_months', fa: '۳ تا ۶ ماه پیش', en: '3–6 months ago' },
        { value: '6_12_months', fa: '۶ تا ۱۲ ماه پیش', en: '6–12 months ago' },
        { value: 'over_year', fa: 'بیش از یک سال', en: 'Over 1 year ago' }
      ]},
      { key: 'severity', fa: 'شدت درد یا محدودیت؟', en: 'Severity?', type: 'radio', options: [
        { value: 'mild', fa: 'خفیف', en: 'Mild' },
        { value: 'moderate', fa: 'متوسط', en: 'Moderate' },
        { value: 'severe', fa: 'شدید', en: 'Severe' }
      ]},
      { key: 'pain_sitting', fa: 'درد هنگام نشستن طولانی؟', en: 'Pain during prolonged sitting?', type: 'yesno' },
      { key: 'numbness_hand', fa: 'بی‌حسی دست؟', en: 'Numbness in hand?', type: 'yesno' },
      { key: 'disc', fa: 'دیسک گردن؟', en: 'Neck disc issue?', type: 'yesno' }
    ]
  },
  wrist: {
    label: { fa: 'مچ دست', en: 'Wrist' },
    questions: [
      { key: 'when_started', fa: 'از چه زمانی شروع شده؟', en: 'When did it start?', type: 'radio', options: [
        { value: 'last_month', fa: 'ماه گذشته', en: 'Last month' },
        { value: '3_6_months', fa: '۳ تا ۶ ماه پیش', en: '3–6 months ago' },
        { value: '6_12_months', fa: '۶ تا ۱۲ ماه پیش', en: '6–12 months ago' },
        { value: 'over_year', fa: 'بیش از یک سال', en: 'Over 1 year ago' }
      ]},
      { key: 'severity', fa: 'شدت درد یا محدودیت؟', en: 'Severity?', type: 'radio', options: [
        { value: 'mild', fa: 'خفیف', en: 'Mild' },
        { value: 'moderate', fa: 'متوسط', en: 'Moderate' },
        { value: 'severe', fa: 'شدید', en: 'Severe' }
      ]},
      { key: 'pain_pushup', fa: 'درد هنگام شنا؟', en: 'Pain during push-ups?', type: 'yesno' },
      { key: 'weak_grip', fa: 'ضعف در گرفتن وزنه؟', en: 'Weakness when gripping weights?', type: 'yesno' }
    ]
  },
  ankle: {
    label: { fa: 'مچ پا', en: 'Ankle' },
    questions: [
      { key: 'when_started', fa: 'از چه زمانی شروع شده؟', en: 'When did it start?', type: 'radio', options: [
        { value: 'last_month', fa: 'ماه گذشته', en: 'Last month' },
        { value: '3_6_months', fa: '۳ تا ۶ ماه پیش', en: '3–6 months ago' },
        { value: '6_12_months', fa: '۶ تا ۱۲ ماه پیش', en: '6–12 months ago' },
        { value: 'over_year', fa: 'بیش از یک سال', en: 'Over 1 year ago' }
      ]},
      { key: 'severity', fa: 'شدت درد یا محدودیت؟', en: 'Severity?', type: 'radio', options: [
        { value: 'mild', fa: 'خفیف', en: 'Mild' },
        { value: 'moderate', fa: 'متوسط', en: 'Moderate' },
        { value: 'severe', fa: 'شدید', en: 'Severe' }
      ]},
      { key: 'sprain_history', fa: 'پیچ‌خوردگی قبلی؟', en: 'Previous sprain?', type: 'yesno' },
      { key: 'pain_running', fa: 'درد در دویدن؟', en: 'Pain when running?', type: 'yesno' },
      { key: 'instability', fa: 'ناپایداری؟', en: 'Instability?', type: 'yesno' }
    ]
  }
};

const RegistrationForm = ({ onComplete }) => {
  const { t, i18n } = useTranslation();
  const { register } = useAuth();
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const stepContainerRef = useRef(null);

  // Account type is always 'member' for registration
  const accountType = 'member';

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

  // Step 4: Body Measurements
  const [chestCircumference, setChestCircumference] = useState('');
  const [waistCircumference, setWaistCircumference] = useState('');
  const [abdomenCircumference, setAbdomenCircumference] = useState('');
  const [armCircumference, setArmCircumference] = useState('');
  const [hipCircumference, setHipCircumference] = useState('');
  const [thighCircumference, setThighCircumference] = useState('');

  // Step 5: Limitations & Injuries
  const [injuries, setInjuries] = useState([]);
  const [injuryDetails, setInjuryDetails] = useState('');
  const [injuryQuestionAnswers, setInjuryQuestionAnswers] = useState(() => {
    const o = {};
    INJURY_KEYS.forEach(k => { o[k] = {}; });
    return o;
  });
  const [medicalConditions, setMedicalConditions] = useState([]);
  const [medicalConditionDetails, setMedicalConditionDetails] = useState('');

  const setInjuryAnswer = (injuryKey, questionKey, value) => {
    setInjuryQuestionAnswers(prev => ({
      ...prev,
      [injuryKey]: { ...(prev[injuryKey] || {}), [questionKey]: value }
    }));
  };

  // Step 6: Training Conditions
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

    // Build injury_details: free text + summary of injury follow-up answers
    let injuryDetailsFinal = injuryDetails.trim();
    if (injuries.length > 0) {
      const fa = i18n.language === 'fa';
      const parts = [];
      injuries.forEach(injuryKey => {
        const config = INJURY_QUESTIONS[injuryKey];
        const answers = injuryQuestionAnswers[injuryKey] || {};
        if (!config || Object.keys(answers).length === 0) return;
        const label = config.label[fa ? 'fa' : 'en'];
        const lines = [];
        config.questions.forEach(q => {
          const v = answers[q.key];
          if (v === undefined || v === '') return;
          const qText = q[fa ? 'fa' : 'en'];
          let aText = v;
          if (q.type === 'yesno') aText = v === 'yes' ? (fa ? 'بله' : 'Yes') : (fa ? 'خیر' : 'No');
          else if (q.options) aText = (q.options.find(o => o.value === v) || {})[fa ? 'fa' : 'en'] || v;
          lines.push(`${qText}: ${aText}`);
        });
        if (lines.length) parts.push(`[${label}]\n${lines.join('\n')}`);
      });
      if (parts.length) {
        injuryDetailsFinal = (injuryDetailsFinal ? injuryDetailsFinal + '\n\n' : '') + parts.join('\n\n');
      }
    }

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
      chest_circumference: chestCircumference ? parseFloat(chestCircumference) : null,
      waist_circumference: waistCircumference ? parseFloat(waistCircumference) : null,
      abdomen_circumference: abdomenCircumference ? parseFloat(abdomenCircumference) : null,
      arm_circumference: armCircumference ? parseFloat(armCircumference) : null,
      hip_circumference: hipCircumference ? parseFloat(hipCircumference) : null,
      thigh_circumference: thighCircumference ? parseFloat(thighCircumference) : null,
      injuries: injuries,
      injury_details: injuryDetailsFinal,
      injury_question_answers: injuryQuestionAnswers,
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
      <h3>{i18n.language === 'fa' ? 'اندازه‌گیری بدن' : 'Body Measurements'}</h3>
      <p className="step-description">
        {i18n.language === 'fa' 
          ? 'لطفاً اندازه‌های بدن خود را وارد کنید (بر حسب سانتی‌متر)'
          : 'Please enter your body measurements (in centimeters)'}
      </p>
      
      <div className="form-group">
        <label>
          {i18n.language === 'fa' ? 'دور سینه (سانتی‌متر)' : 'Chest Circumference (cm)'}
        </label>
        <p className="measurement-description">
          {i18n.language === 'fa' 
            ? 'دور برجسته ترین قسمت سینه'
            : 'Circumference of the most prominent part of the chest'}
        </p>
        <input
          type="number"
          value={chestCircumference}
          onChange={(e) => setChestCircumference(e.target.value)}
          min="0"
          step="0.1"
          placeholder={i18n.language === 'fa' ? 'مثال: 95.5' : 'e.g., 95.5'}
        />
      </div>

      <div className="form-group">
        <label>
          {i18n.language === 'fa' ? 'دور کمر (سانتی‌متر)' : 'Waist Circumference (cm)'}
        </label>
        <p className="measurement-description">
          {i18n.language === 'fa' 
            ? 'دور باریک ترین قسمت کمر'
            : 'Circumference of the narrowest part of the waist'}
        </p>
        <input
          type="number"
          value={waistCircumference}
          onChange={(e) => setWaistCircumference(e.target.value)}
          min="0"
          step="0.1"
          placeholder={i18n.language === 'fa' ? 'مثال: 80.0' : 'e.g., 80.0'}
        />
      </div>

      <div className="form-group">
        <label>
          {i18n.language === 'fa' ? 'دور شکم (سانتی‌متر)' : 'Abdomen Circumference (cm)'}
        </label>
        <p className="measurement-description">
          {i18n.language === 'fa' 
            ? 'دور برجسته ترین قسمت شکم'
            : 'Circumference of the most prominent part of the abdomen'}
        </p>
        <input
          type="number"
          value={abdomenCircumference}
          onChange={(e) => setAbdomenCircumference(e.target.value)}
          min="0"
          step="0.1"
          placeholder={i18n.language === 'fa' ? 'مثال: 90.0' : 'e.g., 90.0'}
        />
      </div>

      <div className="form-group">
        <label>
          {i18n.language === 'fa' ? 'دور بازو (سانتی‌متر)' : 'Arm Circumference (cm)'}
        </label>
        <p className="measurement-description">
          {i18n.language === 'fa' 
            ? 'دور برجسته ترین قسمت بازو'
            : 'Circumference of the most prominent part of the arm'}
        </p>
        <input
          type="number"
          value={armCircumference}
          onChange={(e) => setArmCircumference(e.target.value)}
          min="0"
          step="0.1"
          placeholder={i18n.language === 'fa' ? 'مثال: 35.5' : 'e.g., 35.5'}
        />
      </div>

      <div className="form-group">
        <label>
          {i18n.language === 'fa' ? 'دور باسن (سانتی‌متر)' : 'Hip Circumference (cm)'}
        </label>
        <p className="measurement-description">
          {i18n.language === 'fa' 
            ? 'دور برجسته ترین قسمت باسن'
            : 'Circumference of the most prominent part of the hip'}
        </p>
        <input
          type="number"
          value={hipCircumference}
          onChange={(e) => setHipCircumference(e.target.value)}
          min="0"
          step="0.1"
          placeholder={i18n.language === 'fa' ? 'مثال: 100.0' : 'e.g., 100.0'}
        />
      </div>

      <div className="form-group">
        <label>
          {i18n.language === 'fa' ? 'دور ران (سانتی‌متر)' : 'Thigh Circumference (cm)'}
        </label>
        <p className="measurement-description">
          {i18n.language === 'fa' 
            ? 'دور برجسته ترین قسمت ران'
            : 'Circumference of the most prominent part of the thigh'}
        </p>
        <input
          type="number"
          value={thighCircumference}
          onChange={(e) => setThighCircumference(e.target.value)}
          min="0"
          step="0.1"
          placeholder={i18n.language === 'fa' ? 'مثال: 60.0' : 'e.g., 60.0'}
        />
      </div>
    </div>
  );

  const renderStep5 = () => {
    const fa = i18n.language === 'fa';
    return (
    <div className="registration-step">
      <h3>{fa ? 'محدودیت‌ها و آسیب‌ها' : 'Limitations & Injuries'}</h3>
      <p className="step-description">
        {fa 
          ? 'لطفاً آسیب‌ها و محدودیت‌های خود را مشخص کنید تا برنامه‌های ایمن برای شما طراحی شود'
          : 'Please specify your injuries and limitations so we can create safe programs for you'}
      </p>
      
      <div className="form-group">
        <label>{fa ? 'آسیب‌ها' : 'Injuries'}</label>
        <div className="checkbox-group">
          {INJURY_KEYS.map(key => (
            <label key={key} className="checkbox-label">
              <input
                type="checkbox"
                checked={injuries.includes(key)}
                onChange={() => toggleArrayItem(injuries, setInjuries, key)}
              />
              <span>{INJURY_LABELS[key] ? (fa ? INJURY_LABELS[key].fa : INJURY_LABELS[key].en) : key}</span>
            </label>
          ))}
        </div>
      </div>

      {injuries.length > 0 && (
        <div className="injury-questions-section">
          <p className="step-description">{fa ? 'سوال‌های زیر را برای هر آسیب انتخاب‌شده پاسخ دهید.' : 'Please answer the following questions for each selected injury.'}</p>
          {injuries.map(injuryKey => {
            const config = INJURY_QUESTIONS[injuryKey];
            if (!config) return null;
            const label = config.label[fa ? 'fa' : 'en'];
            const answers = injuryQuestionAnswers[injuryKey] || {};
            return (
              <div key={injuryKey} className="injury-question-block">
                <h4 className="injury-question-title">{label}</h4>
                {config.questions.map(q => {
                  const qText = q[fa ? 'fa' : 'en'];
                  const value = answers[q.key];
                  return (
                    <div key={q.key} className="form-group injury-question">
                      <label>{qText}</label>
                      {q.type === 'radio' && q.options && (
                        <div className="checkbox-group injury-options">
                          {q.options.map(opt => (
                            <label key={opt.value} className="checkbox-label">
                              <input
                                type="radio"
                                name={`${injuryKey}-${q.key}`}
                                checked={value === opt.value}
                                onChange={() => setInjuryAnswer(injuryKey, q.key, opt.value)}
                              />
                              <span>{fa ? opt.fa : opt.en}</span>
                            </label>
                          ))}
                        </div>
                      )}
                      {q.type === 'yesno' && (
                        <div className="checkbox-group injury-options">
                          <label className="checkbox-label">
                            <input
                              type="radio"
                              name={`${injuryKey}-${q.key}`}
                              checked={value === 'yes'}
                              onChange={() => setInjuryAnswer(injuryKey, q.key, 'yes')}
                            />
                            <span>{fa ? 'بله' : 'Yes'}</span>
                          </label>
                          <label className="checkbox-label">
                            <input
                              type="radio"
                              name={`${injuryKey}-${q.key}`}
                              checked={value === 'no'}
                              onChange={() => setInjuryAnswer(injuryKey, q.key, 'no')}
                            />
                            <span>{fa ? 'خیر' : 'No'}</span>
                          </label>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}

      <div className="form-group">
        <label>{fa ? 'توضیحات آسیب' : 'Injury Details'}</label>
        <textarea
          value={injuryDetails}
          onChange={(e) => setInjuryDetails(e.target.value)}
          rows={3}
          placeholder={fa ? 'جزئیات آسیب‌های خود را شرح دهید...' : 'Describe your injuries in detail...'}
        />
      </div>

      <div className="form-group">
        <label>{fa ? 'بیماری‌ها و شرایط پزشکی' : 'Medical Conditions'}</label>
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
  };

  const renderStep6 = () => (
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
          <div className="progress-fill" style={{ width: `${(step / 6) * 100}%` }}></div>
        </div>
        <div className="progress-steps">
          {[1, 2, 3, 4, 5, 6].map(s => (
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
              {s}
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="registration-form">
        {error && <div className="error-message">{error}</div>}

        <div ref={stepContainerRef}>
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
          {step === 5 && renderStep5()}
          {step === 6 && renderStep6()}
        </div>

        <div className="form-actions">
          {step > 1 && (
            <button type="button" className="btn-secondary" onClick={() => handleStepChange(step - 1)}>
              {i18n.language === 'fa' ? 'قبلی' : 'Previous'}
            </button>
          )}
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading
              ? t('loading')
              : step === 6
              ? (i18n.language === 'fa' ? 'ثبت نام و تکمیل' : 'Register & Complete')
              : (i18n.language === 'fa' ? 'بعدی' : 'Next')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RegistrationForm;



