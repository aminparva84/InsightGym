import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './OnlineLab.css';

const OnlineLab = () => {
  const { i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('bmi');
  const [loading, setLoading] = useState(true);

  // Form states for each calculator
  const [bmiData, setBmiData] = useState({ weight: '', height: '' });
  const [bfpData, setBfpData] = useState({ age: '', weight: '', height: '', gender: '', waist: '', neck: '', hip: '' });
  const [ibwData, setIbwData] = useState({ height: '', gender: '' });
  const [rhrData, setRhrData] = useState({ age: '', resting_hr: '' });
  const [waterData, setWaterData] = useState({ weight: '', activity_level: 'moderate' });
  const [rmData, setRmData] = useState({ weight: '', reps: '', exercise_type: 'strength' });
  const [frameData, setFrameData] = useState({ height: '', wrist: '', gender: '' });
  const [bmrData, setBmrData] = useState({ age: '', weight: '', height: '', gender: '', activity_level: 'sedentary' });

  const getAuthToken = useCallback(() => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  }, []);

  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  }, [getAuthToken]);

  const loadUserProfile = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/api/user/profile`, getAxiosConfig());
      
      // Pre-fill forms with user data
      if (response.data) {
        setBmiData({ weight: response.data.weight || '', height: response.data.height || '' });
        setBfpData(prev => ({ ...prev, weight: response.data.weight || '', height: response.data.height || '', gender: response.data.gender || '', age: response.data.age || '' }));
        setIbwData({ height: response.data.height || '', gender: response.data.gender || '' });
        setRhrData(prev => ({ ...prev, age: response.data.age || '' }));
        setWaterData(prev => ({ ...prev, weight: response.data.weight || '' }));
        setFrameData({ height: response.data.height || '', gender: response.data.gender || '' });
        setBmrData({ age: response.data.age || '', weight: response.data.weight || '', height: response.data.height || '', gender: response.data.gender || '' });
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    } finally {
      setLoading(false);
    }
  }, [API_BASE, getAuthToken, getAxiosConfig]);

  useEffect(() => {
    loadUserProfile();
  }, [user, loadUserProfile]);

  // 1. BMI Calculator
  const calculateBMI = () => {
    const weight = parseFloat(bmiData.weight);
    const height = parseFloat(bmiData.height);
    if (!weight || !height || height <= 0) return null;
    const heightInMeters = height / 100;
    return (weight / (heightInMeters * heightInMeters)).toFixed(1);
  };

  // 2. Body Fat Percentage (BFP) Calculator - Using Deurenberg formula
  const calculateBFP = () => {
    const age = parseFloat(bfpData.age);
    const weight = parseFloat(bfpData.weight);
    const height = parseFloat(bfpData.height);
    const gender = bfpData.gender;
    
    if (!age || !weight || !height || height <= 0) return null;
    
    const bmi = weight / Math.pow(height / 100, 2);
    // Deurenberg formula: BFP = (1.20 × BMI) + (0.23 × Age) - (10.8 × Gender) - 5.4
    // Gender: 1 for male, 0 for female
    const genderFactor = gender === 'male' ? 1 : 0;
    const bfp = (1.20 * bmi) + (0.23 * age) - (10.8 * genderFactor) - 5.4;
    return Math.max(0, Math.min(100, bfp.toFixed(1)));
  };

  // 3. Ideal Body Weight (IBW) Calculator - Using Robinson formula
  const calculateIBW = () => {
    const height = parseFloat(ibwData.height);
    const gender = ibwData.gender;
    
    if (!height || height <= 0) return null;
    
    const heightInInches = height / 2.54;
    let ibw;
    
    if (gender === 'male') {
      // Robinson formula for men: IBW = 52 + 1.9 × (height in inches - 60)
      ibw = 52 + 1.9 * (heightInInches - 60);
    } else {
      // Robinson formula for women: IBW = 49 + 1.7 × (height in inches - 60)
      ibw = 49 + 1.7 * (heightInInches - 60);
    }
    
    return ibw > 0 ? ibw.toFixed(1) : null;
  };

  // 4. Resting Heart Rate - Minimum heart rate when resting
  const calculateRHR = () => {
    const age = parseFloat(rhrData.age);
    const resting_hr = parseFloat(rhrData.resting_hr);
    
    if (resting_hr) {
      return resting_hr; // User provided their resting heart rate
    }
    
    if (!age) return null;
    
    // Average resting heart rate by age: 60-100 bpm for adults
    // Formula: 220 - age gives max HR, resting is typically 60-70% of max
    const maxHR = 220 - age;
    const avgRestingHR = Math.round(maxHR * 0.65);
    return avgRestingHR;
  };

  // 5. Daily Water Needs
  const calculateWaterNeeds = () => {
    const weight = parseFloat(waterData.weight);
    if (!weight || weight <= 0) return null;
    
    // Base: 30-35ml per kg body weight
    let baseWater = weight * 32.5; // Average of 30-35
    
    // Activity level multipliers
    const multipliers = {
      sedentary: 1.0,
      light: 1.2,
      moderate: 1.4,
      active: 1.6,
      very_active: 1.8
    };
    
    const multiplier = multipliers[waterData.activity_level] || 1.0;
    const totalWater = baseWater * multiplier;
    
    return Math.round(totalWater);
  };

  // 6. One Rep Max (1RM) Calculator - Using Brzycki formula
  const calculate1RM = () => {
    const weight = parseFloat(rmData.weight);
    const reps = parseFloat(rmData.reps);
    
    if (!weight || !reps || reps <= 0 || reps > 10) return null;
    
    // Brzycki formula: 1RM = weight / (1.0278 - 0.0278 × reps)
    const oneRM = weight / (1.0278 - 0.0278 * reps);
    return oneRM.toFixed(1);
  };

  // 7. Body Frame Type
  const calculateFrameType = () => {
    const height = parseFloat(frameData.height);
    const wrist = parseFloat(frameData.wrist);
    const gender = frameData.gender;
    
    if (!height || !wrist || height <= 0 || wrist <= 0) return null;
    
    const heightInInches = height / 2.54;
    let frameSize;
    
    if (gender === 'male') {
      // For men: height/wrist ratio
      const ratio = heightInInches / wrist;
      if (ratio > 10.9) frameSize = 'small';
      else if (ratio > 9.6) frameSize = 'medium';
      else frameSize = 'large';
    } else {
      // For women: height/wrist ratio
      const ratio = heightInInches / wrist;
      if (ratio > 11.0) frameSize = 'small';
      else if (ratio > 10.1) frameSize = 'medium';
      else frameSize = 'large';
    }
    
    return frameSize;
  };

  // 8. Basal Metabolic Rate (BMR) - Using Mifflin-St Jeor equation
  const calculateBMR = () => {
    const age = parseFloat(bmrData.age);
    const weight = parseFloat(bmrData.weight);
    const height = parseFloat(bmrData.height);
    const gender = bmrData.gender;
    
    if (!age || !weight || !height || height <= 0) return null;
    
    // Mifflin-St Jeor equation
    // Men: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
    // Women: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161
    let bmr;
    if (gender === 'male') {
      bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
      bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }
    
    // Activity level multipliers for TDEE (Total Daily Energy Expenditure)
    const multipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      very_active: 1.9
    };
    
    const multiplier = multipliers[bmrData.activity_level] || 1.2;
    const tdee = bmr * multiplier;
    
    return {
      bmr: Math.round(bmr),
      tdee: Math.round(tdee)
    };
  };

  const sections = [
    { id: 'bmi', label: i18n.language === 'fa' ? 'محاسبه BMI' : 'BMI Calculator' },
    { id: 'bfp', label: i18n.language === 'fa' ? 'محاسبه درصد چربی بدن' : 'Body Fat % Calculator' },
    { id: 'ibw', label: i18n.language === 'fa' ? 'محاسبه وزن ایده‌آل' : 'Ideal Weight Calculator' },
    { id: 'rhr', label: i18n.language === 'fa' ? 'محاسبه ضربان قلب پایه' : 'Resting Heart Rate' },
    { id: 'water', label: i18n.language === 'fa' ? 'محاسبه نیاز روزانه آب' : 'Daily Water Needs' },
    { id: 'rm', label: i18n.language === 'fa' ? 'محاسبه قدرت بیشینه (1RM)' : 'One Rep Max (1RM)' },
    { id: 'frame', label: i18n.language === 'fa' ? 'محاسبه نوع استخوان‌بندی' : 'Body Frame Type' },
    { id: 'bmr', label: i18n.language === 'fa' ? 'محاسبه متابولیسم پایه (BMR)' : 'Basal Metabolic Rate (BMR)' }
  ];

  if (loading) {
    return <div className="online-lab-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  return (
    <div className="online-lab" dir="ltr">
      <div className="online-lab-header">
        <h2>{i18n.language === 'fa' ? 'آزمایشگاه آنلاین' : 'Online Laboratory'}</h2>
      </div>

      <div className="online-lab-content">
        <div className="lab-sections-nav">
          {sections.map(section => (
            <button
              key={section.id}
              className={`lab-nav-btn ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              {section.label}
            </button>
          ))}
        </div>

        <div className="lab-calculator-content">
          {/* 1. BMI Calculator */}
          {activeSection === 'bmi' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه شاخص توده بدنی (BMI)' : 'Body Mass Index (BMI) Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
                  <input
                    type="number"
                    value={bmiData.weight}
                    onChange={(e) => setBmiData({ ...bmiData, weight: e.target.value })}
                    step="0.1"
                    placeholder={i18n.language === 'fa' ? 'مثال: 75' : 'e.g., 75'}
                  />
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                  <input
                    type="number"
                    value={bmiData.height}
                    onChange={(e) => setBmiData({ ...bmiData, height: e.target.value })}
                    step="0.1"
                    placeholder={i18n.language === 'fa' ? 'مثال: 175' : 'e.g., 175'}
                  />
                </div>
                {calculateBMI() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculateBMI()}</span>
                      <span className="result-unit">BMI</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'BMI شما: ' + calculateBMI() 
                        : 'Your BMI: ' + calculateBMI()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 2. Body Fat Percentage */}
          {activeSection === 'bfp' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه درصد چربی بدن (BFP)' : 'Body Fat Percentage (BFP) Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
                    <input
                      type="number"
                      value={bfpData.age}
                      onChange={(e) => setBfpData({ ...bfpData, age: e.target.value })}
                      placeholder={i18n.language === 'fa' ? 'مثال: 30' : 'e.g., 30'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
                    <input
                      type="number"
                      value={bfpData.weight}
                      onChange={(e) => setBfpData({ ...bfpData, weight: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 75' : 'e.g., 75'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                    <input
                      type="number"
                      value={bfpData.height}
                      onChange={(e) => setBfpData({ ...bfpData, height: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 175' : 'e.g., 175'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
                    <select
                      value={bfpData.gender}
                      onChange={(e) => setBfpData({ ...bfpData, gender: e.target.value })}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                      <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                    </select>
                  </div>
                </div>
                {calculateBFP() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculateBFP()}</span>
                      <span className="result-unit">%</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'درصد چربی بدن شما: ' + calculateBFP() + '%'
                        : 'Your Body Fat Percentage: ' + calculateBFP() + '%'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 3. Ideal Body Weight */}
          {activeSection === 'ibw' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه وزن ایده‌آل (IBW)' : 'Ideal Body Weight (IBW) Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                    <input
                      type="number"
                      value={ibwData.height}
                      onChange={(e) => setIbwData({ ...ibwData, height: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 175' : 'e.g., 175'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
                    <select
                      value={ibwData.gender}
                      onChange={(e) => setIbwData({ ...ibwData, gender: e.target.value })}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                      <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                    </select>
                  </div>
                </div>
                {calculateIBW() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculateIBW()}</span>
                      <span className="result-unit">kg</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'وزن ایده‌آل شما: ' + calculateIBW() + ' کیلوگرم'
                        : 'Your Ideal Body Weight: ' + calculateIBW() + ' kg'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 4. Resting Heart Rate */}
          {activeSection === 'rhr' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه ضربان قلب پایه' : 'Resting Heart Rate Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
                    <input
                      type="number"
                      value={rhrData.age}
                      onChange={(e) => setRhrData({ ...rhrData, age: e.target.value })}
                      placeholder={i18n.language === 'fa' ? 'مثال: 30' : 'e.g., 30'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'ضربان قلب در حالت استراحت (اختیاری)' : 'Resting Heart Rate (optional)'}</label>
                    <input
                      type="number"
                      value={rhrData.resting_hr}
                      onChange={(e) => setRhrData({ ...rhrData, resting_hr: e.target.value })}
                      placeholder={i18n.language === 'fa' ? 'مثال: 70' : 'e.g., 70'}
                    />
                  </div>
                </div>
                {calculateRHR() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculateRHR()}</span>
                      <span className="result-unit">bpm</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'ضربان قلب پایه شما: ' + calculateRHR() + ' ضربه در دقیقه'
                        : 'Your Resting Heart Rate: ' + calculateRHR() + ' beats per minute'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 5. Daily Water Needs */}
          {activeSection === 'water' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه نیاز روزانه آب بدن' : 'Daily Water Needs Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
                    <input
                      type="number"
                      value={waterData.weight}
                      onChange={(e) => setWaterData({ ...waterData, weight: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 75' : 'e.g., 75'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سطح فعالیت' : 'Activity Level'}</label>
                    <select
                      value={waterData.activity_level}
                      onChange={(e) => setWaterData({ ...waterData, activity_level: e.target.value })}
                    >
                      <option value="sedentary">{i18n.language === 'fa' ? 'بی‌تحرک' : 'Sedentary'}</option>
                      <option value="light">{i18n.language === 'fa' ? 'سبک' : 'Light'}</option>
                      <option value="moderate">{i18n.language === 'fa' ? 'متوسط' : 'Moderate'}</option>
                      <option value="active">{i18n.language === 'fa' ? 'فعال' : 'Active'}</option>
                      <option value="very_active">{i18n.language === 'fa' ? 'خیلی فعال' : 'Very Active'}</option>
                    </select>
                  </div>
                </div>
                {calculateWaterNeeds() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculateWaterNeeds()}</span>
                      <span className="result-unit">ml</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'نیاز روزانه آب شما: ' + calculateWaterNeeds() + ' میلی‌لیتر (' + (calculateWaterNeeds() / 1000).toFixed(1) + ' لیتر)'
                        : 'Your Daily Water Needs: ' + calculateWaterNeeds() + ' ml (' + (calculateWaterNeeds() / 1000).toFixed(1) + ' liters)'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 6. One Rep Max */}
          {activeSection === 'rm' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه قدرت بیشینه (1RM)' : 'One Rep Max (1RM) Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'وزن استفاده شده (کیلوگرم)' : 'Weight Used (kg)'}</label>
                    <input
                      type="number"
                      value={rmData.weight}
                      onChange={(e) => setRmData({ ...rmData, weight: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 80' : 'e.g., 80'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'تعداد تکرار' : 'Number of Reps'}</label>
                    <input
                      type="number"
                      value={rmData.reps}
                      onChange={(e) => setRmData({ ...rmData, reps: e.target.value })}
                      min="1"
                      max="10"
                      placeholder={i18n.language === 'fa' ? 'مثال: 5' : 'e.g., 5'}
                    />
                  </div>
                </div>
                {calculate1RM() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculate1RM()}</span>
                      <span className="result-unit">kg</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'قدرت بیشینه شما (1RM): ' + calculate1RM() + ' کیلوگرم'
                        : 'Your One Rep Max (1RM): ' + calculate1RM() + ' kg'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 7. Body Frame Type */}
          {activeSection === 'frame' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه نوع استخوان‌بندی' : 'Body Frame Type Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                    <input
                      type="number"
                      value={frameData.height}
                      onChange={(e) => setFrameData({ ...frameData, height: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 175' : 'e.g., 175'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'دور مچ دست (سانتی‌متر)' : 'Wrist Circumference (cm)'}</label>
                    <input
                      type="number"
                      value={frameData.wrist}
                      onChange={(e) => setFrameData({ ...frameData, wrist: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 17' : 'e.g., 17'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
                    <select
                      value={frameData.gender}
                      onChange={(e) => setFrameData({ ...frameData, gender: e.target.value })}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                      <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                    </select>
                  </div>
                </div>
                {calculateFrameType() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">
                        {calculateFrameType() === 'small' 
                          ? (i18n.language === 'fa' ? 'ریز' : 'Small')
                          : calculateFrameType() === 'medium'
                          ? (i18n.language === 'fa' ? 'متوسط' : 'Medium')
                          : (i18n.language === 'fa' ? 'درشت' : 'Large')}
                      </span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? 'نوع استخوان‌بندی شما: ' + (calculateFrameType() === 'small' ? 'ریز' : calculateFrameType() === 'medium' ? 'متوسط' : 'درشت')
                        : 'Your Body Frame Type: ' + calculateFrameType()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 8. BMR */}
          {activeSection === 'bmr' && (
            <div className="calculator-section">
              <h3>{i18n.language === 'fa' ? 'محاسبه متابولیسم پایه (BMR)' : 'Basal Metabolic Rate (BMR) Calculator'}</h3>
              <div className="calculator-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
                    <input
                      type="number"
                      value={bmrData.age}
                      onChange={(e) => setBmrData({ ...bmrData, age: e.target.value })}
                      placeholder={i18n.language === 'fa' ? 'مثال: 30' : 'e.g., 30'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
                    <input
                      type="number"
                      value={bmrData.weight}
                      onChange={(e) => setBmrData({ ...bmrData, weight: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 75' : 'e.g., 75'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                    <input
                      type="number"
                      value={bmrData.height}
                      onChange={(e) => setBmrData({ ...bmrData, height: e.target.value })}
                      step="0.1"
                      placeholder={i18n.language === 'fa' ? 'مثال: 175' : 'e.g., 175'}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
                    <select
                      value={bmrData.gender}
                      onChange={(e) => setBmrData({ ...bmrData, gender: e.target.value })}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                      <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سطح فعالیت' : 'Activity Level'}</label>
                    <select
                      value={bmrData.activity_level}
                      onChange={(e) => setBmrData({ ...bmrData, activity_level: e.target.value })}
                    >
                      <option value="sedentary">{i18n.language === 'fa' ? 'بی‌تحرک' : 'Sedentary'}</option>
                      <option value="light">{i18n.language === 'fa' ? 'سبک' : 'Light'}</option>
                      <option value="moderate">{i18n.language === 'fa' ? 'متوسط' : 'Moderate'}</option>
                      <option value="active">{i18n.language === 'fa' ? 'فعال' : 'Active'}</option>
                      <option value="very_active">{i18n.language === 'fa' ? 'خیلی فعال' : 'Very Active'}</option>
                    </select>
                  </div>
                </div>
                {calculateBMR() && (
                  <div className="calculator-result">
                    <div className="result-value">
                      <span className="result-number">{calculateBMR().bmr}</span>
                      <span className="result-unit">kcal/day</span>
                    </div>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? `متابولیسم پایه (BMR): ${calculateBMR().bmr} کیلوکالری در روز`
                        : `Basal Metabolic Rate (BMR): ${calculateBMR().bmr} kcal/day`}
                    </p>
                    <p className="result-description">
                      {i18n.language === 'fa' 
                        ? `مصرف انرژی روزانه (TDEE): ${calculateBMR().tdee} کیلوکالری در روز`
                        : `Total Daily Energy Expenditure (TDEE): ${calculateBMR().tdee} kcal/day`}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnlineLab;

