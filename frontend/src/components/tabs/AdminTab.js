import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import './AdminTab.css';

const AdminTab = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  
  // Members state
  const [members, setMembers] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [editingMember, setEditingMember] = useState(null);
  const [memberFormData, setMemberFormData] = useState({});
  const [showAssistantForm, setShowAssistantForm] = useState(false);
  const [showCredentialsModal, setShowCredentialsModal] = useState(false);
  const [createdCredentials, setCreatedCredentials] = useState(null);
  const [assistantFormData, setAssistantFormData] = useState({
    username: '',
    email: '',
    password: '',
    language: 'fa',
    fillProfileNow: false,
    age: '',
    weight: '',
    height: '',
    gender: '',
    training_level: '',
    chest_circumference: '',
    waist_circumference: '',
    abdomen_circumference: '',
    arm_circumference: '',
    hip_circumference: '',
    thigh_circumference: ''
  });


  useEffect(() => {
    fetchAssistants();
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

  const fetchAssistants = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/admin/assistants', getAxiosConfig());
      setAssistants(response.data);
    } catch (error) {
      console.error('Error fetching assistants:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست دستیاران' : 'Error fetching assistants');
    }
  };


  const handleCreateAssistant = async (e) => {
    e.preventDefault();
    try {
      const data = {
        username: assistantFormData.username,
        email: assistantFormData.email,
        password: assistantFormData.password,
        language: assistantFormData.language
      };
      
      if (assistantFormData.fillProfileNow) {
        data.profile = {
          age: assistantFormData.age ? parseInt(assistantFormData.age) : null,
          weight: assistantFormData.weight ? parseFloat(assistantFormData.weight) : null,
          height: assistantFormData.height ? parseFloat(assistantFormData.height) : null,
          gender: assistantFormData.gender || '',
          training_level: assistantFormData.training_level || '',
          chest_circumference: assistantFormData.chest_circumference ? parseFloat(assistantFormData.chest_circumference) : null,
          waist_circumference: assistantFormData.waist_circumference ? parseFloat(assistantFormData.waist_circumference) : null,
          abdomen_circumference: assistantFormData.abdomen_circumference ? parseFloat(assistantFormData.abdomen_circumference) : null,
          arm_circumference: assistantFormData.arm_circumference ? parseFloat(assistantFormData.arm_circumference) : null,
          hip_circumference: assistantFormData.hip_circumference ? parseFloat(assistantFormData.hip_circumference) : null,
          thigh_circumference: assistantFormData.thigh_circumference ? parseFloat(assistantFormData.thigh_circumference) : null,
          // Trainer Professional Details
          certifications: assistantFormData.certifications || '',
          qualifications: assistantFormData.qualifications || '',
          years_of_experience: assistantFormData.years_of_experience ? parseInt(assistantFormData.years_of_experience) : null,
          specialization: assistantFormData.specialization || '',
          education: assistantFormData.education || '',
          bio: assistantFormData.bio || ''
        };
      }
      
      const response = await axios.post('http://localhost:5000/api/admin/assistants', data, getAxiosConfig());
      
      // Show credentials modal
      setCreatedCredentials({
        username: assistantFormData.username,
        password: assistantFormData.password,
        email: assistantFormData.email
      });
      setShowAssistantForm(false);
      resetAssistantForm();
      fetchAssistants();
      setShowCredentialsModal(true);
    } catch (error) {
      console.error('Error creating assistant:', error);
      alert(i18n.language === 'fa' 
        ? `خطا در ایجاد دستیار: ${error.response?.data?.error || error.message}`
        : `Error creating assistant: ${error.response?.data?.error || error.message}`);
    }
  };

  const handleDeleteAssistant = async (assistantId) => {
    try {
      await axios.delete(`http://localhost:5000/api/admin/assistants/${assistantId}`, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'دستیار با موفقیت حذف شد' : 'Assistant deleted successfully');
      fetchAssistants();
    } catch (error) {
      console.error('Error deleting assistant:', error);
      alert(i18n.language === 'fa' 
        ? `خطا در حذف دستیار: ${error.response?.data?.error || error.message}`
        : `Error deleting assistant: ${error.response?.data?.error || error.message}`);
    }
  };


  const resetAssistantForm = () => {
    setAssistantFormData({
      username: '',
      email: '',
      password: '',
      language: 'fa',
      fillProfileNow: false,
      age: '',
      weight: '',
      height: '',
      gender: '',
      training_level: '',
      chest_circumference: '',
      waist_circumference: '',
      abdomen_circumference: '',
      arm_circumference: '',
      hip_circumference: '',
      thigh_circumference: '',
      certifications: '',
      qualifications: '',
      years_of_experience: '',
      specialization: '',
      education: '',
      bio: ''
    });
  };

  return (
    <div className="admin-tab" dir="ltr">
      <div className="admin-tab-header">
        <h2>{i18n.language === 'fa' ? 'مدیریت دستیاران' : 'Assistants Management'}</h2>
      </div>

      <div className="admin-tab-content">
        <div className="admin-section-content">
          <div className="section-header">
            <button className="btn-primary" onClick={() => setShowAssistantForm(true)}>
              {i18n.language === 'fa' ? '+ افزودن دستیار' : '+ Add Assistant'}
            </button>
          </div>

            {showAssistantForm && (
              <div className="admin-form-overlay">
                <div className="admin-form-container">
                  <div className="form-header-with-close">
                    <h3>{i18n.language === 'fa' ? 'ایجاد دستیار جدید' : 'Create New Assistant'}</h3>
                    <button 
                      type="button" 
                      className="close-form-btn"
                      onClick={() => {
                        setShowAssistantForm(false);
                        resetAssistantForm();
                      }}
                      aria-label={i18n.language === 'fa' ? 'بستن' : 'Close'}
                    >
                      ×
                    </button>
                  </div>
                  <form onSubmit={handleCreateAssistant}>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'نام کاربری *' : 'Username *'}</label>
                      <input
                        type="text"
                        value={assistantFormData.username}
                        onChange={(e) => setAssistantFormData({...assistantFormData, username: e.target.value})}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'ایمیل *' : 'Email *'}</label>
                      <input
                        type="email"
                        value={assistantFormData.email}
                        onChange={(e) => setAssistantFormData({...assistantFormData, email: e.target.value})}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'رمز عبور *' : 'Password *'}</label>
                      <input
                        type="password"
                        value={assistantFormData.password}
                        onChange={(e) => setAssistantFormData({...assistantFormData, password: e.target.value})}
                        required
                        minLength={6}
                      />
                    </div>
                    <div className="form-group checkbox-group">
                      <label className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={assistantFormData.fillProfileNow}
                          onChange={(e) => setAssistantFormData({...assistantFormData, fillProfileNow: e.target.checked})}
                        />
                        <span>{i18n.language === 'fa' 
                          ? 'تکمیل پروفایل اکنون (در غیر این صورت دستیار باید بعد از اولین ورود تکمیل کند)'
                          : 'Fill profile now (otherwise assistant must complete after first login)'}
                        </span>
                      </label>
                    </div>

                    {assistantFormData.fillProfileNow && (
                      <>
                        <h4 style={{ marginTop: '1.5rem', marginBottom: '1rem', color: 'var(--color-primary-800)', fontSize: '1.1rem', fontWeight: '600' }}>
                          {i18n.language === 'fa' ? 'اطلاعات شخصی' : 'Personal Information'}
                        </h4>
                        <div className="form-row">
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
                            <input
                              type="number"
                              value={assistantFormData.age}
                              onChange={(e) => setAssistantFormData({...assistantFormData, age: e.target.value})}
                              min="1"
                              max="120"
                            />
                          </div>
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
                            <select
                              value={assistantFormData.gender}
                              onChange={(e) => setAssistantFormData({...assistantFormData, gender: e.target.value})}
                            >
                              <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                              <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                              <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                              <option value="other">{i18n.language === 'fa' ? 'سایر' : 'Other'}</option>
                            </select>
                          </div>
                        </div>
                        
                        <h4 style={{ marginTop: '2rem', marginBottom: '1rem', color: 'var(--color-primary-800)', fontSize: '1.1rem', fontWeight: '600' }}>
                          {i18n.language === 'fa' ? 'اطلاعات حرفه‌ای مربی' : 'Trainer Professional Details'}
                        </h4>
                        <div className="form-group">
                          <label>{i18n.language === 'fa' ? 'گواهینامه‌ها' : 'Certifications'}</label>
                          <textarea
                            value={assistantFormData.certifications}
                            onChange={(e) => setAssistantFormData({...assistantFormData, certifications: e.target.value})}
                            placeholder={i18n.language === 'fa' ? 'مثال: NASM-CPT, ACE-CPT, ISSA...' : 'Example: NASM-CPT, ACE-CPT, ISSA...'}
                            rows="2"
                          />
                        </div>
                        <div className="form-group">
                          <label>{i18n.language === 'fa' ? 'مدارک و صلاحیت‌ها' : 'Qualifications'}</label>
                          <textarea
                            value={assistantFormData.qualifications}
                            onChange={(e) => setAssistantFormData({...assistantFormData, qualifications: e.target.value})}
                            placeholder={i18n.language === 'fa' ? 'مثال: کارشناسی تربیت بدنی، کارشناسی ارشد فیزیولوژی ورزش...' : 'Example: BS in Physical Education, MS in Exercise Physiology...'}
                            rows="2"
                          />
                        </div>
                        <div className="form-row">
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'سال‌های تجربه' : 'Years of Experience'}</label>
                            <input
                              type="number"
                              value={assistantFormData.years_of_experience}
                              onChange={(e) => setAssistantFormData({...assistantFormData, years_of_experience: e.target.value})}
                              min="0"
                              max="50"
                            />
                          </div>
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'تخصص' : 'Specialization'}</label>
                            <input
                              type="text"
                              value={assistantFormData.specialization}
                              onChange={(e) => setAssistantFormData({...assistantFormData, specialization: e.target.value})}
                              placeholder={i18n.language === 'fa' ? 'مثال: بدنسازی، کاهش وزن، قدرت...' : 'Example: Bodybuilding, Weight Loss, Strength...'}
                            />
                          </div>
                        </div>
                        <div className="form-group">
                          <label>{i18n.language === 'fa' ? 'تحصیلات' : 'Education'}</label>
                          <input
                            type="text"
                            value={assistantFormData.education}
                            onChange={(e) => setAssistantFormData({...assistantFormData, education: e.target.value})}
                            placeholder={i18n.language === 'fa' ? 'مثال: کارشناسی ارشد فیزیولوژی ورزش از دانشگاه تهران' : 'Example: MS in Exercise Physiology from University of Tehran'}
                          />
                        </div>
                        <div className="form-group">
                          <label>{i18n.language === 'fa' ? 'بیوگرافی' : 'Bio'}</label>
                          <textarea
                            value={assistantFormData.bio}
                            onChange={(e) => setAssistantFormData({...assistantFormData, bio: e.target.value})}
                            placeholder={i18n.language === 'fa' ? 'توضیحات درباره مربی...' : 'Description about the trainer...'}
                            rows="4"
                          />
                        </div>
                        
                        <h4 style={{ marginTop: '2rem', marginBottom: '1rem', color: 'var(--color-primary-800)', fontSize: '1.1rem', fontWeight: '600' }}>
                          {i18n.language === 'fa' ? 'اندازه‌گیری بدن (سانتی‌متر)' : 'Body Measurements (cm)'}
                        </h4>
                        <div className="form-row">
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'دور سینه' : 'Chest'}</label>
                            <input
                              type="number"
                              value={assistantFormData.chest_circumference}
                              onChange={(e) => setAssistantFormData({...assistantFormData, chest_circumference: e.target.value})}
                              step="0.1"
                            />
                          </div>
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'دور کمر' : 'Waist'}</label>
                            <input
                              type="number"
                              value={assistantFormData.waist_circumference}
                              onChange={(e) => setAssistantFormData({...assistantFormData, waist_circumference: e.target.value})}
                              step="0.1"
                            />
                          </div>
                        </div>
                        <div className="form-row">
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'دور شکم' : 'Abdomen'}</label>
                            <input
                              type="number"
                              value={assistantFormData.abdomen_circumference}
                              onChange={(e) => setAssistantFormData({...assistantFormData, abdomen_circumference: e.target.value})}
                              step="0.1"
                            />
                          </div>
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'دور بازو' : 'Arm'}</label>
                            <input
                              type="number"
                              value={assistantFormData.arm_circumference}
                              onChange={(e) => setAssistantFormData({...assistantFormData, arm_circumference: e.target.value})}
                              step="0.1"
                            />
                          </div>
                        </div>
                        <div className="form-row">
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'دور باسن' : 'Hip'}</label>
                            <input
                              type="number"
                              value={assistantFormData.hip_circumference}
                              onChange={(e) => setAssistantFormData({...assistantFormData, hip_circumference: e.target.value})}
                              step="0.1"
                            />
                          </div>
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'دور ران' : 'Thigh'}</label>
                            <input
                              type="number"
                              value={assistantFormData.thigh_circumference}
                              onChange={(e) => setAssistantFormData({...assistantFormData, thigh_circumference: e.target.value})}
                              step="0.1"
                            />
                          </div>
                        </div>
                      </>
                    )}

                    <div className="form-actions">
                      <button type="submit" className="btn-primary">
                        {i18n.language === 'fa' ? 'ایجاد دستیار' : 'Create Assistant'}
                      </button>
                      <button type="button" className="btn-secondary" onClick={() => {
                        setShowAssistantForm(false);
                        resetAssistantForm();
                      }}>
                        {i18n.language === 'fa' ? 'لغو' : 'Cancel'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <div className="assistants-list">
              <table>
                <thead>
                  <tr>
                    <th>{i18n.language === 'fa' ? 'نام کاربری' : 'Username'}</th>
                    <th>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</th>
                    <th>{i18n.language === 'fa' ? 'تعداد اعضای تخصیص یافته' : 'Assigned Members'}</th>
                    <th>{i18n.language === 'fa' ? 'وضعیت پروفایل' : 'Profile Status'}</th>
                    <th>{i18n.language === 'fa' ? 'حذف' : 'Delete'}</th>
                  </tr>
                </thead>
                <tbody>
                  {assistants.map(assistant => (
                    <tr key={assistant.id}>
                      <td>{assistant.username}</td>
                      <td>{assistant.email}</td>
                      <td>{assistant.assigned_members_count || 0}</td>
                      <td>{assistant.profile_complete 
                        ? (i18n.language === 'fa' ? 'تکمیل شده' : 'Complete')
                        : (i18n.language === 'fa' ? 'ناقص' : 'Incomplete')}
                      </td>
                      <td>
                        <button 
                          className="btn-delete"
                          onClick={() => {
                            if (window.confirm(
                              i18n.language === 'fa' 
                                ? `آیا مطمئن هستید که می‌خواهید دستیار "${assistant.username}" را حذف کنید؟ این عمل غیرقابل بازگشت است.`
                                : `Are you sure you want to delete assistant "${assistant.username}"? This action cannot be undone.`
                            )) {
                              handleDeleteAssistant(assistant.id);
                            }
                          }}
                        >
                          {i18n.language === 'fa' ? 'حذف' : 'Delete'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Credentials Modal */}
            {showCredentialsModal && createdCredentials && (
              <div className="admin-form-overlay">
                <div className="admin-form-container" style={{ maxWidth: '500px' }}>
                  <h3>{i18n.language === 'fa' ? 'اطلاعات ورود دستیار' : 'Assistant Login Credentials'}</h3>
                  <div className="credentials-display">
                    <div className="credential-item">
                      <label>{i18n.language === 'fa' ? 'نام کاربری:' : 'Username:'}</label>
                      <div className="credential-value">
                        <code>{createdCredentials.username}</code>
                        <button 
                          className="copy-btn"
                          onClick={() => {
                            navigator.clipboard.writeText(createdCredentials.username);
                            alert(i18n.language === 'fa' ? 'کپی شد' : 'Copied!');
                          }}
                        >
                          {i18n.language === 'fa' ? 'کپی' : 'Copy'}
                        </button>
                      </div>
                    </div>
                    <div className="credential-item">
                      <label>{i18n.language === 'fa' ? 'رمز عبور:' : 'Password:'}</label>
                      <div className="credential-value">
                        <code>{createdCredentials.password}</code>
                        <button 
                          className="copy-btn"
                          onClick={() => {
                            navigator.clipboard.writeText(createdCredentials.password);
                            alert(i18n.language === 'fa' ? 'کپی شد' : 'Copied!');
                          }}
                        >
                          {i18n.language === 'fa' ? 'کپی' : 'Copy'}
                        </button>
                      </div>
                    </div>
                    <div className="credential-warning">
                      <p>{i18n.language === 'fa' 
                        ? '⚠️ لطفاً این اطلاعات را ذخیره کنید. این اطلاعات فقط یک بار نمایش داده می‌شود.'
                        : '⚠️ Please save these credentials. They will only be shown once.'}
                      </p>
                    </div>
                  </div>
                  <div className="form-actions">
                    <button 
                      type="button" 
                      className="btn-primary" 
                      onClick={() => {
                        setShowCredentialsModal(false);
                        setCreatedCredentials(null);
                      }}
                    >
                      {i18n.language === 'fa' ? 'بستن' : 'Close'}
                    </button>
                  </div>
                </div>
              </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default AdminTab;

