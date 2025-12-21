import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import './ProfileTab.css';

const ProfileTab = () => {
  const { t, i18n } = useTranslation();
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Get auth token
  const getAuthToken = () => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  useEffect(() => {
    // Wait for auth to finish loading before loading profile
    if (!authLoading && user) {
      loadProfile();
    } else if (!authLoading && !user) {
      setLoading(false);
    }
  }, [authLoading, user]);

  const loadProfile = async () => {
    const token = getAuthToken();
    if (!token) {
      console.warn('No token available for loading profile');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://localhost:5000/api/user/profile', getAxiosConfig());
      setProfile(response.data);
      
      // Load profile image if exists
      if (response.data.profile_image) {
        const imageUrl = `http://localhost:5000/api/user/profile/image/${response.data.profile_image}`;
        setImagePreview(imageUrl);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      if (error.response?.status === 404) {
        // Profile doesn't exist - create empty profile
        setProfile({
          age: null,
          weight: null,
          height: null,
          gender: '',
          training_level: '',
          fitness_goals: [],
          injuries: [],
          injury_details: '',
          medical_conditions: [],
          equipment_access: [],
          gym_access: false,
          home_equipment: [],
          preferred_workout_time: '',
          workout_days_per_week: 3,
          preferred_intensity: ''
        });
      } else if (error.response?.status === 401 || error.response?.status === 422) {
        // Authentication error - user needs to log in again
        console.error('Authentication error loading profile');
        alert(i18n.language === 'fa' 
          ? 'لطفاً دوباره وارد شوید'
          : 'Please log in again');
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
    setProfile(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) || null : value)
    }));
  };

  const handleArrayChange = (field, value, checked) => {
    setProfile(prev => {
      const currentArray = prev[field] || [];
      if (checked) {
        return { ...prev, [field]: [...currentArray, value] };
      } else {
        return { ...prev, [field]: currentArray.filter(item => item !== value) };
      }
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const profileData = {
        ...profile,
        profile_image: profileImage
      };
      
      await axios.put('http://localhost:5000/api/user/profile', profileData, getAxiosConfig());
      setEditing(false);
      setProfileImage(null);
      await loadProfile();
      alert(i18n.language === 'fa' ? 'پروفایل با موفقیت به‌روزرسانی شد' : 'Profile updated successfully');
    } catch (error) {
      console.error('Error saving profile:', error);
      alert(i18n.language === 'fa' ? 'خطا در به‌روزرسانی پروفایل' : 'Error updating profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="profile-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
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
          <button className="edit-btn" onClick={() => setEditing(true)}>
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
              <input type="text" value={user?.username || ''} disabled />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</label>
              <input type="email" value={user?.email || ''} disabled />
            </div>
            <div className="form-group">
              <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
              <input
                type="number"
                name="age"
                value={profile?.age || ''}
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
                <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
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
                value={profile?.weight || ''}
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
                value={profile?.height || ''}
                onChange={handleInputChange}
                disabled={!editing}
                min="1"
                step="0.1"
              />
            </div>
          </div>
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
                <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
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
                value={profile?.workout_days_per_week || ''}
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
                <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
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
                <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
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
        </div>

        {/* Action Buttons */}
        {editing && (
          <div className="profile-actions">
            <button className="save-btn" onClick={handleSave} disabled={saving}>
              {saving ? (i18n.language === 'fa' ? 'در حال ذخیره...' : 'Saving...') : (i18n.language === 'fa' ? 'ذخیره' : 'Save')}
            </button>
            <button className="cancel-btn" onClick={() => { setEditing(false); setProfileImage(null); loadProfile(); }}>
              {i18n.language === 'fa' ? 'لغو' : 'Cancel'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileTab;

