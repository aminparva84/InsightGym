import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import './ProfileTab.css';

// BMI Calculator Component
const BMICalculator = ({ weight, height, gender, language }) => {
  const bmi = useMemo(() => {
    if (!weight || !height || height <= 0) return null;
    // BMI = weight (kg) / (height (m))^2
    const heightInMeters = height / 100;
    return (weight / (heightInMeters * heightInMeters)).toFixed(1);
  }, [weight, height]);

  const getBMICategory = (bmiValue) => {
    if (!bmiValue) return null;
    const bmiNum = parseFloat(bmiValue);
    
    // Slightly different ranges for males and females
    if (gender === 'female') {
      if (bmiNum < 18.5) return { category: 'underweight', color: '#ff9800', label: language === 'fa' ? 'کم‌وزن' : 'Underweight' };
      if (bmiNum < 24.9) return { category: 'normal', color: '#4caf50', label: language === 'fa' ? 'طبیعی' : 'Normal' };
      if (bmiNum < 29.9) return { category: 'overweight', color: '#ff9800', label: language === 'fa' ? 'اضافه وزن' : 'Overweight' };
      return { category: 'obese', color: '#f44336', label: language === 'fa' ? 'چاق' : 'Obese' };
    } else {
      // Male or other
      if (bmiNum < 18.5) return { category: 'underweight', color: '#ff9800', label: language === 'fa' ? 'کم‌وزن' : 'Underweight' };
      if (bmiNum < 25) return { category: 'normal', color: '#4caf50', label: language === 'fa' ? 'طبیعی' : 'Normal' };
      if (bmiNum < 30) return { category: 'overweight', color: '#ff9800', label: language === 'fa' ? 'اضافه وزن' : 'Overweight' };
      return { category: 'obese', color: '#f44336', label: language === 'fa' ? 'چاق' : 'Obese' };
    }
  };

  const getBMIRange = () => {
    if (gender === 'female') {
      return [
        { min: 0, max: 18.5, color: '#ff9800', label: language === 'fa' ? 'کم‌وزن' : 'Underweight' },
        { min: 18.5, max: 24.9, color: '#4caf50', label: language === 'fa' ? 'طبیعی' : 'Normal' },
        { min: 24.9, max: 29.9, color: '#ff9800', label: language === 'fa' ? 'اضافه وزن' : 'Overweight' },
        { min: 29.9, max: 50, color: '#f44336', label: language === 'fa' ? 'چاق' : 'Obese' }
      ];
    } else {
      return [
        { min: 0, max: 18.5, color: '#ff9800', label: language === 'fa' ? 'کم‌وزن' : 'Underweight' },
        { min: 18.5, max: 25, color: '#4caf50', label: language === 'fa' ? 'طبیعی' : 'Normal' },
        { min: 25, max: 30, color: '#ff9800', label: language === 'fa' ? 'اضافه وزن' : 'Overweight' },
        { min: 30, max: 50, color: '#f44336', label: language === 'fa' ? 'چاق' : 'Obese' }
      ];
    }
  };

  if (!bmi) return null;

  const category = getBMICategory(bmi);
  const ranges = getBMIRange();
  const maxBMI = 40;
  const currentPosition = Math.min((parseFloat(bmi) / maxBMI) * 100, 100);

  return (
    <div className="bmi-calculator">
      <h4>{language === 'fa' ? 'محاسبه BMI' : 'BMI Calculator'}</h4>
      <div className="bmi-display">
        <div className="bmi-value">
          <span className="bmi-number">{bmi}</span>
          <span className="bmi-unit">BMI</span>
        </div>
        {category && (
          <div className="bmi-category" style={{ color: category.color }}>
            {category.label}
          </div>
        )}
      </div>
      
      <div className="bmi-range-container">
        <div className="bmi-range-bar">
          {ranges.map((range, index) => {
            const width = ((range.max - range.min) / maxBMI) * 100;
            const left = (range.min / maxBMI) * 100;
            return (
              <div
                key={index}
                className="bmi-range-segment"
                style={{
                  left: `${left}%`,
                  width: `${width}%`,
                  backgroundColor: range.color,
                  opacity: 0.3
                }}
              />
            );
          })}
          <div
            className="bmi-indicator"
            style={{
              left: `${currentPosition}%`,
              backgroundColor: category?.color || '#666'
            }}
          />
        </div>
        <div className="bmi-labels">
          {ranges.map((range, index) => (
            <div key={index} className="bmi-label-item">
              <div 
                className="bmi-label-color" 
                style={{ backgroundColor: range.color }}
              />
              <span className="bmi-label-text">
                {range.label}: {range.min.toFixed(1)} - {range.max === 50 ? '∞' : range.max.toFixed(1)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const ProfileTab = () => {
  const { t, i18n } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');

  // Get auth token
  const getAuthToken = () => {
    // First try localStorage (most reliable)
    const localToken = localStorage.getItem('token');
    if (localToken && localToken.trim() !== '') {
      return localToken.trim();
    }
    // Fallback to axios defaults
    const authHeader = axios.defaults.headers.common['Authorization'];
    if (authHeader && typeof authHeader === 'string' && authHeader.startsWith('Bearer ')) {
      return authHeader.replace('Bearer ', '').trim();
    }
    return null;
  };

  const getAxiosConfig = () => {
    // Always get fresh token from localStorage first (source of truth)
    let token = localStorage.getItem('token');
    
    if (!token || token.trim() === '') {
      console.error('No auth token found in localStorage!');
      alert(i18n.language === 'fa' 
        ? 'خطا: توکن احراز هویت یافت نشد. لطفاً دوباره وارد شوید.'
        : 'Error: Authentication token not found. Please log in again.');
      return {};
    }
    
    // Clean the token
    token = token.trim();
    
    // Remove any accidental "Bearer " prefix
    if (token.startsWith('Bearer ')) {
      token = token.replace(/^Bearer\s+/i, '').trim();
    }
    
    // Ensure token is valid JWT format (starts with eyJ)
    if (!token.startsWith('eyJ')) {
      console.error('Invalid token format! Token should start with "eyJ"');
      console.error('Token (first 50 chars):', token.substring(0, 50));
      console.error('Token length:', token.length);
      return {};
    }
    
    // Check token structure (JWT should have 3 parts separated by dots)
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Invalid JWT structure! Token should have 3 parts separated by dots');
      console.error('Token parts count:', parts.length);
      console.error('Token:', token.substring(0, 100));
      return {};
    }
    
    // Always update axios defaults when we have a valid token
    const authHeader = `Bearer ${token}`;
    axios.defaults.headers.common['Authorization'] = authHeader;
    
    console.log('getAxiosConfig - Token validated and config created');
    console.log('Token length:', token.length);
    console.log('Token format check - starts with eyJ:', token.startsWith('eyJ'));
    console.log('Token parts count:', parts.length);
    console.log('Auth header (first 30 chars):', authHeader.substring(0, 30) + '...');
    
    return { 
      headers: { 
        'Authorization': authHeader
      } 
    };
  };

  useEffect(() => {
    // Wait for auth to finish loading before loading profile
    // Use a ref to prevent multiple simultaneous loads
    let isMounted = true;
    
    if (!authLoading && user) {
      // Small delay to ensure token is fully set in axios defaults
      const timer = setTimeout(() => {
        if (isMounted) {
          loadProfile();
        }
      }, 100);
      
      return () => {
        isMounted = false;
        clearTimeout(timer);
      };
      } else if (!authLoading && !user) {
      setLoading(false);
    }
    
    // Set username and email when user is available
    if (user && !authLoading) {
      setUsername(user.username || '');
      setEmail(user.email || '');
    }
    
    return () => {
      isMounted = false;
    };
  }, [authLoading, user]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadProfile = async () => {
    setLoading(true);
    const token = getAuthToken();
    if (!token) {
      console.warn('No token available for loading profile');
      // Set empty profile so user can still see the form
      setProfile({
        age: null,
        weight: null,
        height: null,
        gender: '',
        training_level: '',
        exercise_history_years: null,
        exercise_history_description: '',
        fitness_goals: [],
        injuries: [],
        injury_details: '',
        medical_conditions: [],
        medical_condition_details: '',
        equipment_access: [],
        gym_access: false,
        home_equipment: [],
        preferred_workout_time: '',
        workout_days_per_week: 3,
        preferred_intensity: ''
      });
      setLoading(false);
      return;
    }

    try {
      // Clean and validate token
      let cleanToken = token.trim();
      if (cleanToken.startsWith('Bearer ')) {
        cleanToken = cleanToken.replace(/^Bearer\s+/i, '').trim();
      }
      
      if (!cleanToken.startsWith('eyJ')) {
        console.error('Invalid token format - token should start with "eyJ"');
        throw new Error('Invalid token format');
      }
      
      // Ensure token is set in axios defaults
      const authHeader = `Bearer ${cleanToken}`;
      axios.defaults.headers.common['Authorization'] = authHeader;
      
      console.log('Loading profile with token:', cleanToken.substring(0, 20) + '...');
      console.log('Token length:', cleanToken.length);
      console.log('Token format valid:', cleanToken.startsWith('eyJ'));
      
      const config = getAxiosConfig();
      if (!config.headers || !config.headers['Authorization']) {
        throw new Error('Authorization header not set');
      }
      
      // Verify the header format
      const configHeader = config.headers['Authorization'];
      if (!configHeader.startsWith('Bearer ') || !configHeader.substring(7).startsWith('eyJ')) {
        console.error('Invalid Authorization header format:', configHeader.substring(0, 30));
        throw new Error('Invalid Authorization header format');
      }
      
      console.log('Loading profile with config:', { 
        hasAuthHeader: !!config.headers['Authorization'],
        headerFormat: config.headers['Authorization'].substring(0, 30) + '...',
        fullHeader: config.headers['Authorization']
      });
      console.log('Full token being sent:', cleanToken);
      
      const response = await axios.get('http://localhost:5000/api/user/profile', config);
      console.log('Profile loaded successfully - RAW response:', JSON.stringify(response.data, null, 2));
      
      // Ensure all fields are properly formatted and not null/undefined
      // Handle both direct response and nested profile structure
      const rawData = response.data;
      const profileData = {
        age: (rawData.age !== undefined && rawData.age !== null) ? rawData.age : null,
        weight: (rawData.weight !== undefined && rawData.weight !== null) ? rawData.weight : null,
        height: (rawData.height !== undefined && rawData.height !== null) ? rawData.height : null,
        gender: rawData.gender || '',
        training_level: rawData.training_level || '',
        exercise_history_years: (rawData.exercise_history_years !== undefined && rawData.exercise_history_years !== null) ? rawData.exercise_history_years : null,
        exercise_history_description: rawData.exercise_history_description || '',
        fitness_goals: (() => {
          if (Array.isArray(rawData.fitness_goals)) return rawData.fitness_goals;
          if (typeof rawData.fitness_goals === 'string' && rawData.fitness_goals.trim()) {
            try { return JSON.parse(rawData.fitness_goals); } catch { return []; }
          }
          return [];
        })(),
        injuries: (() => {
          if (Array.isArray(rawData.injuries)) return rawData.injuries;
          if (typeof rawData.injuries === 'string' && rawData.injuries.trim()) {
            try { return JSON.parse(rawData.injuries); } catch { return []; }
          }
          return [];
        })(),
        injury_details: rawData.injury_details || '',
        medical_conditions: (() => {
          if (Array.isArray(rawData.medical_conditions)) return rawData.medical_conditions;
          if (typeof rawData.medical_conditions === 'string' && rawData.medical_conditions.trim()) {
            try { return JSON.parse(rawData.medical_conditions); } catch { return []; }
          }
          return [];
        })(),
        medical_condition_details: rawData.medical_condition_details || '',
        equipment_access: (() => {
          if (Array.isArray(rawData.equipment_access)) return rawData.equipment_access;
          if (typeof rawData.equipment_access === 'string' && rawData.equipment_access.trim()) {
            try { return JSON.parse(rawData.equipment_access); } catch { return []; }
          }
          return [];
        })(),
        gym_access: rawData.gym_access ?? false,
        home_equipment: (() => {
          if (Array.isArray(rawData.home_equipment)) return rawData.home_equipment;
          if (typeof rawData.home_equipment === 'string' && rawData.home_equipment.trim()) {
            try { return JSON.parse(rawData.home_equipment); } catch { return []; }
          }
          return [];
        })(),
        preferred_workout_time: rawData.preferred_workout_time || '',
        workout_days_per_week: (rawData.workout_days_per_week !== undefined && rawData.workout_days_per_week !== null) ? rawData.workout_days_per_week : 3,
        preferred_intensity: rawData.preferred_intensity || '',
        profile_image: rawData.profile_image || null
      };
      
      console.log('Formatted profile data:', JSON.stringify(profileData, null, 2));
      console.log('Profile data summary:', {
        age: profileData.age,
        weight: profileData.weight,
        height: profileData.height,
        gender: profileData.gender,
        training_level: profileData.training_level,
        fitness_goals_count: profileData.fitness_goals.length,
        injuries_count: profileData.injuries.length,
        medical_conditions_count: profileData.medical_conditions.length
      });
      setProfile(profileData);
      
      // Load user info (username and email)
      if (user) {
        setUsername(user.username || '');
        setEmail(user.email || '');
      }
      
      // Load profile image if exists
      if (profileData.profile_image) {
        const imageUrl = `http://localhost:5000/api/user/profile/image/${profileData.profile_image}`;
        setImagePreview(imageUrl);
      } else {
        setImagePreview(null);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      console.error('Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        config: error.config?.url
      });
      
      if (error.response?.status === 404) {
        // Profile doesn't exist - create empty profile
        console.log('Profile not found (404), creating empty profile');
        console.log('This means the user has not created a profile yet. They can fill it out now.');
        setProfile({
          age: null,
          weight: null,
          height: null,
          gender: '',
          training_level: '',
          exercise_history_years: null,
          exercise_history_description: '',
          fitness_goals: [],
          injuries: [],
          injury_details: '',
          medical_conditions: [],
          medical_condition_details: '',
          equipment_access: [],
          gym_access: false,
          home_equipment: [],
          preferred_workout_time: '',
          workout_days_per_week: 3,
          preferred_intensity: ''
        });
      } else if (error.response?.status === 401 || error.response?.status === 422) {
        // Authentication error - check if it's a token error
        const errorData = error.response?.data || {};
        const errorMessage = (errorData.error || errorData.message || '').toLowerCase();
        const isTokenError = errorMessage.includes('token') && (
          errorMessage.includes('expired') || 
          errorMessage.includes('invalid') || 
          errorMessage.includes('missing') ||
          errorMessage.includes('format')
        );
        
        console.error('Authentication error loading profile');
        console.error('Auth error message:', errorMessage);
        console.error('Is token error:', isTokenError);
        
        if (isTokenError) {
          // Token is invalid - don't clear user state here, let auth context handle it
          console.warn('Token error detected, but keeping user state. Auth context will handle logout if needed.');
        }
        
        // Still set empty profile so form is visible
        setProfile({
          age: null,
          weight: null,
          height: null,
          gender: '',
          training_level: '',
          exercise_history_years: null,
          exercise_history_description: '',
          fitness_goals: [],
          injuries: [],
          injury_details: '',
          medical_conditions: [],
          medical_condition_details: '',
          equipment_access: [],
          gym_access: false,
          home_equipment: [],
          preferred_workout_time: '',
          workout_days_per_week: 3,
          preferred_intensity: ''
        });
      } else {
        // Other errors - still set empty profile so user can see the form
        console.log('Other error loading profile, creating empty profile');
        console.error('Full error:', error);
        setProfile({
          age: null,
          weight: null,
          height: null,
          gender: '',
          training_level: '',
          exercise_history_years: null,
          exercise_history_description: '',
          fitness_goals: [],
          injuries: [],
          injury_details: '',
          medical_conditions: [],
          medical_condition_details: '',
          equipment_access: [],
          gym_access: false,
          home_equipment: [],
          preferred_workout_time: '',
          workout_days_per_week: 3,
          preferred_intensity: ''
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        alert(i18n.language === 'fa' ? 'حجم فایل باید کمتر از 5 مگابایت باشد' : 'File size must be less than 5MB');
        return;
      }
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImage(reader.result);
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProfile(prev => {
      const baseProfile = prev || {
        age: null,
        weight: null,
        height: null,
        gender: '',
        training_level: '',
        exercise_history_years: null,
        exercise_history_description: '',
        fitness_goals: [],
        injuries: [],
        injury_details: '',
        medical_conditions: [],
        medical_condition_details: '',
        equipment_access: [],
        gym_access: false,
        home_equipment: [],
        preferred_workout_time: '',
        workout_days_per_week: 3,
        preferred_intensity: ''
      };
      return {
        ...baseProfile,
        [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) || null : value)
      };
    });
  };

  const handleArrayChange = (field, value, checked) => {
    setProfile(prev => {
      const baseProfile = prev || {
        age: null,
        weight: null,
        height: null,
        gender: '',
        training_level: '',
        exercise_history_years: null,
        exercise_history_description: '',
        fitness_goals: [],
        injuries: [],
        injury_details: '',
        medical_conditions: [],
        medical_condition_details: '',
        equipment_access: [],
        gym_access: false,
        home_equipment: [],
        preferred_workout_time: '',
        workout_days_per_week: 3,
        preferred_intensity: ''
      };
      const currentArray = baseProfile[field] || [];
      if (checked) {
        return { ...baseProfile, [field]: [...currentArray, value] };
      } else {
        return { ...baseProfile, [field]: currentArray.filter(item => item !== value) };
      }
    });
  };

  const handleSave = async () => {
    if (!profile) {
      alert(i18n.language === 'fa' ? 'پروفایل یافت نشد' : 'Profile not found');
      return;
    }
    
    // Ensure token is set in axios defaults before saving
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.trim()}`;
    }
    
    // Check for token before attempting to save
    const authToken = getAuthToken();
    if (!authToken) {
      alert(i18n.language === 'fa' 
        ? 'خطا: توکن احراز هویت یافت نشد. لطفاً دوباره وارد شوید.'
        : 'Error: Authentication token not found. Please log in again.');
      return;
    }
    
    setSaving(true);
    try {
      const profileData = {
        ...profile
      };
      
      // Only include profile_image if it's actually set (not null)
      if (profileImage) {
        profileData.profile_image = profileImage;
      }
      
      console.log('Saving profile data:', { ...profileData, profile_image: profileImage ? '[base64 image]' : null });
      console.log('Using token:', authToken.substring(0, 20) + '...');
      
      const config = getAxiosConfig();
      if (!config.headers || !config.headers['Authorization']) {
        console.error('Config:', config);
        throw new Error('Authorization header not set');
      }
      
      console.log('Axios config headers present:', !!config.headers['Authorization']);
      console.log('Authorization header:', config.headers['Authorization'].substring(0, 30) + '...');
      
      // Save profile data
      await axios.put('http://localhost:5000/api/user/profile', profileData, config);
      
      // Save user data (username and email) if changed
      if (username !== user?.username || email !== user?.email) {
        try {
          await axios.put('http://localhost:5000/api/user', {
            username: username,
            email: email
          }, config);
        } catch (userError) {
          console.error('Error updating user info:', userError);
          // Don't fail the whole save if user update fails, but show a warning
          alert(i18n.language === 'fa' 
            ? 'پروفایل به‌روزرسانی شد اما به‌روزرسانی اطلاعات کاربری با خطا مواجه شد'
            : 'Profile updated but user info update failed');
        }
      }
      
      setEditing(false);
      setProfileImage(null);
      await loadProfile();
      alert(i18n.language === 'fa' ? 'پروفایل با موفقیت به‌روزرسانی شد' : 'Profile updated successfully');
    } catch (error) {
      console.error('Error saving profile:', error);
      console.error('Error response:', error.response);
      const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message || 'Unknown error';
      console.error('Full error details:', error.response?.data);
      alert(i18n.language === 'fa' 
        ? `خطا در به‌روزرسانی پروفایل: ${errorMessage}`
        : `Error updating profile: ${errorMessage}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="profile-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  if (!profile) {
    return <div className="profile-loading">{i18n.language === 'fa' ? 'در حال بارگذاری پروفایل...' : 'Loading profile...'}</div>;
  }

  const fitnessGoalsOptions = [
    { value: 'weight_loss', label_fa: 'کاهش وزن', label_en: 'Weight Loss' },
    { value: 'muscle_gain', label_fa: 'افزایش عضله', label_en: 'Muscle Gain' },
    { value: 'strength', label_fa: 'قدرت', label_en: 'Strength' },
    { value: 'endurance', label_fa: 'استقامت', label_en: 'Endurance' },
    { value: 'flexibility', label_fa: 'انعطاف‌پذیری', label_en: 'Flexibility' }
  ];

  const injuryOptions = [
    { value: 'knee', label_fa: 'زانو', label_en: 'Knee' },
    { value: 'shoulder', label_fa: 'شانه', label_en: 'Shoulder' },
    { value: 'lower_back', label_fa: 'کمر', label_en: 'Lower Back' },
    { value: 'ankle', label_fa: 'مچ پا', label_en: 'Ankle' },
    { value: 'wrist', label_fa: 'مچ دست', label_en: 'Wrist' }
  ];

  return (
    <div className="profile-tab" dir={i18n.language === 'fa' ? 'rtl' : 'ltr'}>
      <div className="profile-header">
        <h2>{i18n.language === 'fa' ? 'پروفایل کاربری' : 'User Profile'}</h2>
        {!editing && (
          <button className="edit-btn" onClick={() => {
            // Ensure profile data is loaded before entering edit mode
            if (!profile) {
              loadProfile();
            }
            setEditing(true);
          }}>
            {i18n.language === 'fa' ? 'ویرایش' : 'Edit'}
          </button>
        )}
      </div>

      <div className="profile-content">
        {/* Profile Image Section */}
        <div className="profile-image-section">
          <div className="image-container">
            {imagePreview ? (
              <img src={imagePreview} alt="Profile" className="profile-image" />
            ) : (
              <div className="profile-image-placeholder">
                {i18n.language === 'fa' ? 'تصویر پروفایل' : 'Profile Image'}
              </div>
            )}
            {editing && (
              <div className="image-upload-overlay">
                <label className="image-upload-btn">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                  />
                  {i18n.language === 'fa' ? 'انتخاب تصویر' : 'Choose Image'}
                </label>
              </div>
            )}
          </div>
        </div>

        {/* Basic Information */}
        <div className="profile-section">
          <h3>{i18n.language === 'fa' ? 'اطلاعات پایه' : 'Basic Information'}</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'نام کاربری' : 'Username'}</label>
              <input 
                type="text" 
                name="username"
                value={username || ''} 
                onChange={(e) => setUsername(e.target.value)}
                disabled={!editing}
              />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</label>
              <input 
                type="email" 
                name="email"
                value={email || ''} 
                onChange={(e) => setEmail(e.target.value)}
                disabled={!editing}
              />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
              <input
                type="number"
                name="age"
                value={profile?.age ?? ''}
                onChange={handleInputChange}
                disabled={!editing}
                min="1"
                max="120"
              />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
              <select
                name="gender"
                value={profile?.gender || ''}
                onChange={handleInputChange}
                disabled={!editing}
              >
                {editing && <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>}
                {!editing && !profile?.gender && <option value=""></option>}
                <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                <option value="other">{i18n.language === 'fa' ? 'سایر' : 'Other'}</option>
              </select>
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
              <input
                type="number"
                name="weight"
                value={profile?.weight ?? ''}
                onChange={handleInputChange}
                disabled={!editing}
                min="1"
                step="0.1"
              />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
              <input
                type="number"
                name="height"
                value={profile?.height ?? ''}
                onChange={handleInputChange}
                disabled={!editing}
                min="1"
                step="0.1"
              />
            </div>
          </div>
          
          {/* BMI Calculator */}
          {profile?.weight && profile?.height && parseFloat(profile.weight) > 0 && parseFloat(profile.height) > 0 && (
            <BMICalculator 
              weight={parseFloat(profile.weight)} 
              height={parseFloat(profile.height)} 
              gender={profile.gender}
              language={i18n.language}
            />
          )}
        </div>

        {/* Training Information */}
        <div className="profile-section">
          <h3>{i18n.language === 'fa' ? 'اطلاعات تمرینی' : 'Training Information'}</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'سطح تمرین' : 'Training Level'}</label>
              <select
                name="training_level"
                value={profile?.training_level || ''}
                onChange={handleInputChange}
                disabled={!editing}
              >
                {editing && <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>}
                {!editing && !profile?.training_level && <option value=""></option>}
                <option value="beginner">{i18n.language === 'fa' ? 'مبتدی' : 'Beginner'}</option>
                <option value="intermediate">{i18n.language === 'fa' ? 'متوسط' : 'Intermediate'}</option>
                <option value="advanced">{i18n.language === 'fa' ? 'پیشرفته' : 'Advanced'}</option>
              </select>
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'روزهای تمرین در هفته' : 'Workout Days Per Week'}</label>
              <input
                type="number"
                name="workout_days_per_week"
                value={profile?.workout_days_per_week ?? ''}
                onChange={handleInputChange}
                disabled={!editing}
                min="1"
                max="7"
              />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'زمان ترجیحی تمرین' : 'Preferred Workout Time'}</label>
              <select
                name="preferred_workout_time"
                value={profile?.preferred_workout_time || ''}
                onChange={handleInputChange}
                disabled={!editing}
              >
                {editing && <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>}
                {!editing && !profile?.preferred_workout_time && <option value=""></option>}
                <option value="morning">{i18n.language === 'fa' ? 'صبح' : 'Morning'}</option>
                <option value="afternoon">{i18n.language === 'fa' ? 'ظهر' : 'Afternoon'}</option>
                <option value="evening">{i18n.language === 'fa' ? 'عصر' : 'Evening'}</option>
              </select>
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'شدت ترجیحی' : 'Preferred Intensity'}</label>
              <select
                name="preferred_intensity"
                value={profile?.preferred_intensity || ''}
                onChange={handleInputChange}
                disabled={!editing}
              >
                {editing && <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>}
                {!editing && !profile?.preferred_intensity && <option value=""></option>}
                <option value="light">{i18n.language === 'fa' ? 'سبک' : 'Light'}</option>
                <option value="medium">{i18n.language === 'fa' ? 'متوسط' : 'Medium'}</option>
                <option value="heavy">{i18n.language === 'fa' ? 'سنگین' : 'Heavy'}</option>
              </select>
            </div>
          </div>

          <div className="form-group full-width">
            <label>{i18n.language === 'fa' ? 'اهداف تناسب اندام' : 'Fitness Goals'}</label>
            <div className="checkbox-group">
              {fitnessGoalsOptions.map(option => (
                <label key={option.value} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.fitness_goals || []).includes(option.value)}
                    onChange={(e) => handleArrayChange('fitness_goals', option.value, e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? option.label_fa : option.label_en}
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Health Information */}
        <div className="profile-section">
          <h3>{i18n.language === 'fa' ? 'اطلاعات سلامتی' : 'Health Information'}</h3>
          <div className="form-group full-width">
            <label>{i18n.language === 'fa' ? 'آسیب‌ها' : 'Injuries'}</label>
            <div className="checkbox-group">
              {injuryOptions.map(option => (
                <label key={option.value} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.injuries || []).includes(option.value)}
                    onChange={(e) => handleArrayChange('injuries', option.value, e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? option.label_fa : option.label_en}
                </label>
              ))}
            </div>
          </div>
          <div className="form-group full-width">
            <label>{i18n.language === 'fa' ? 'جزئیات آسیب‌ها' : 'Injury Details'}</label>
            <textarea
              name="injury_details"
              value={profile?.injury_details || ''}
              onChange={handleInputChange}
              disabled={!editing}
              rows="3"
            />
          </div>
        </div>

        {/* Exercise History */}
        <div className="profile-section">
          <h3>{i18n.language === 'fa' ? 'سابقه تمرینی' : 'Exercise History'}</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'سال‌های سابقه تمرین' : 'Years of Exercise History'}</label>
              <input
                type="number"
                name="exercise_history_years"
                value={profile?.exercise_history_years ?? ''}
                onChange={handleInputChange}
                disabled={!editing}
                min="0"
                max="50"
              />
            </div>
          </div>
          <div className="form-group full-width">
            <label>{i18n.language === 'fa' ? 'توضیحات سابقه تمرینی' : 'Exercise History Description'}</label>
            <textarea
              name="exercise_history_description"
              value={profile?.exercise_history_description || ''}
              onChange={handleInputChange}
              disabled={!editing}
              rows="3"
              placeholder={i18n.language === 'fa' ? 'سابقه تمرینات قبلی خود را شرح دهید...' : 'Describe your previous exercise experience...'}
            />
          </div>
        </div>

        {/* Medical Conditions */}
        <div className="profile-section">
          <h3>{i18n.language === 'fa' ? 'شرایط پزشکی' : 'Medical Conditions'}</h3>
          <div className="form-group full-width">
            <label>{i18n.language === 'fa' ? 'بیماری‌ها و شرایط پزشکی' : 'Medical Conditions'}</label>
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={(profile?.medical_conditions || []).includes('heart_disease')}
                  onChange={(e) => handleArrayChange('medical_conditions', 'heart_disease', e.target.checked)}
                  disabled={!editing}
                />
                {i18n.language === 'fa' ? 'بیماری قلبی' : 'Heart Disease'}
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={(profile?.medical_conditions || []).includes('high_blood_pressure')}
                  onChange={(e) => handleArrayChange('medical_conditions', 'high_blood_pressure', e.target.checked)}
                  disabled={!editing}
                />
                {i18n.language === 'fa' ? 'فشار خون بالا' : 'High Blood Pressure'}
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={(profile?.medical_conditions || []).includes('pregnancy')}
                  onChange={(e) => handleArrayChange('medical_conditions', 'pregnancy', e.target.checked)}
                  disabled={!editing}
                />
                {i18n.language === 'fa' ? 'بارداری' : 'Pregnancy'}
              </label>
            </div>
          </div>
          <div className="form-group full-width">
            <label>{i18n.language === 'fa' ? 'توضیحات شرایط پزشکی' : 'Medical Condition Details'}</label>
            <textarea
              name="medical_condition_details"
              value={profile?.medical_condition_details || ''}
              onChange={handleInputChange}
              disabled={!editing}
              rows="3"
              placeholder={i18n.language === 'fa' ? 'جزئیات شرایط پزشکی خود را شرح دهید...' : 'Describe your medical conditions in detail...'}
            />
          </div>
        </div>

        {/* Equipment Access */}
        <div className="profile-section">
          <h3>{i18n.language === 'fa' ? 'دسترسی به تجهیزات' : 'Equipment Access'}</h3>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="gym_access"
                checked={profile?.gym_access || false}
                onChange={handleInputChange}
                disabled={!editing}
              />
              {i18n.language === 'fa' ? 'دسترسی به باشگاه' : 'Gym Access'}
            </label>
          </div>
          
          {profile?.gym_access && (
            <div className="form-group full-width">
              <label>{i18n.language === 'fa' ? 'تجهیزات باشگاه' : 'Gym Equipment'}</label>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.equipment_access || []).includes('machine')}
                    onChange={(e) => handleArrayChange('equipment_access', 'machine', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'دستگاه' : 'Machines'}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.equipment_access || []).includes('dumbbells')}
                    onChange={(e) => handleArrayChange('equipment_access', 'dumbbells', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'دمبل' : 'Dumbbells'}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.equipment_access || []).includes('barbell')}
                    onChange={(e) => handleArrayChange('equipment_access', 'barbell', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'هالتر' : 'Barbell'}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.equipment_access || []).includes('cable')}
                    onChange={(e) => handleArrayChange('equipment_access', 'cable', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'کابل' : 'Cable Machine'}
                </label>
              </div>
            </div>
          )}

          {!profile?.gym_access && (
            <div className="form-group full-width">
              <label>{i18n.language === 'fa' ? 'تجهیزات خانگی' : 'Home Equipment'}</label>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.home_equipment || []).includes('dumbbells')}
                    onChange={(e) => handleArrayChange('home_equipment', 'dumbbells', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'دمبل' : 'Dumbbells'}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.home_equipment || []).includes('resistance_bands')}
                    onChange={(e) => handleArrayChange('home_equipment', 'resistance_bands', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'باند مقاومتی' : 'Resistance Bands'}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.home_equipment || []).includes('yoga_mat')}
                    onChange={(e) => handleArrayChange('home_equipment', 'yoga_mat', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'تشک یوگا' : 'Yoga Mat'}
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={(profile?.home_equipment || []).includes('body_weight_only')}
                    onChange={(e) => handleArrayChange('home_equipment', 'body_weight_only', e.target.checked)}
                    disabled={!editing}
                  />
                  {i18n.language === 'fa' ? 'فقط وزن بدن' : 'Body Weight Only'}
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {editing && (
          <div className="profile-actions">
            <button className="save-btn" onClick={handleSave} disabled={saving}>
              {saving ? (i18n.language === 'fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language === 'fa' ? 'ذخیره' : 'Save')}
            </button>
            <button className="cancel-btn" onClick={() => { 
              setEditing(false); 
              setProfileImage(null); 
              // Reset username and email to original values
              if (user) {
                setUsername(user.username || '');
                setEmail(user.email || '');
              }
              loadProfile(); 
            }}>
              {i18n.language === 'fa' ? 'لغو' : 'Cancel'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileTab;

