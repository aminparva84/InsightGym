import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import './AdminPage.css';

const AdminPage = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('assistants');
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Assistants state
  const [assistants, setAssistants] = useState([]);
  const [showAssistantForm, setShowAssistantForm] = useState(false);
  const [assistantFormData, setAssistantFormData] = useState({
    username: '',
    email: '',
    password: '',
    language: 'fa',
    fillProfileNow: false,
    // Profile fields (optional)
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
  
  // Members state
  const [members, setMembers] = useState([]);
  const [editingMember, setEditingMember] = useState(null);
  const [memberFormData, setMemberFormData] = useState({});
  
  // Training level and injury configuration
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

  useEffect(() => {
    checkAdmin();
  }, []);

  useEffect(() => {
    if (isAdmin) {
      if (activeTab === 'assistants') {
        fetchAssistants();
      } else if (activeTab === 'members') {
        fetchAssistants(); // Load assistants first for the dropdown
        fetchMembers();
      }
    }
  }, [isAdmin, activeTab]);

  const checkAdmin = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/admin/check-admin`);
      setIsAdmin(response.data.is_admin);
      if (!response.data.is_admin) {
        alert(i18n.language === 'fa' ? 'شما مجاز به دسترسی به این صفحه نیستید' : 'You are not authorized to access this page');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
      setIsAdmin(false);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssistants = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/admin/assistants`);
      setAssistants(response.data);
    } catch (error) {
      console.error('Error fetching assistants:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست دستیاران' : 'Error fetching assistants');
    }
  };

  const fetchMembers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/admin/members`);
      setMembers(response.data);
    } catch (error) {
      console.error('Error fetching members:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست اعضا' : 'Error fetching members');
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
          thigh_circumference: assistantFormData.thigh_circumference ? parseFloat(assistantFormData.thigh_circumference) : null
        };
      }
      
      await axios.post(`${API_BASE}/api/admin/assistants`, data);
      alert(i18n.language === 'fa' ? 'دستیار با موفقیت ایجاد شد' : 'Assistant created successfully');
      setShowAssistantForm(false);
      resetAssistantForm();
      fetchAssistants();
    } catch (error) {
      console.error('Error creating assistant:', error);
      alert(i18n.language === 'fa' 
        ? `خطا در ایجاد دستیار: ${error.response?.data?.error || error.message}`
        : `Error creating assistant: ${error.response?.data?.error || error.message}`);
    }
  };

  const handleAssignMember = async (memberId, assistantId) => {
    try {
      await axios.post(`${API_BASE}/api/admin/members/${memberId}/assign`, {
        assigned_to_id: assistantId || null
      });
      alert(i18n.language === 'fa' ? 'تخصیص با موفقیت انجام شد' : 'Assignment successful');
      fetchMembers();
    } catch (error) {
      console.error('Error assigning member:', error);
      alert(i18n.language === 'fa' ? 'خطا در تخصیص عضو' : 'Error assigning member');
    }
  };

  const handleEditMember = (member) => {
    setEditingMember(member);
    // Load member profile data
    setMemberFormData(member.profile || {});
  };

  const handleSaveMemberProfile = async () => {
    try {
      await axios.put(`${API_BASE}/api/admin/members/${editingMember.id}/profile`, memberFormData);
      alert(i18n.language === 'fa' ? 'پروفایل عضو به‌روزرسانی شد' : 'Member profile updated');
      setEditingMember(null);
      fetchMembers();
    } catch (error) {
      console.error('Error updating member profile:', error);
      alert(i18n.language === 'fa' ? 'خطا در به‌روزرسانی پروفایل' : 'Error updating profile');
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
      thigh_circumference: ''
    });
  };

  if (loading) {
    return <div className="admin-page-loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>;
  }

  if (!isAdmin) {
    return <div className="admin-page-loading">{i18n.language === 'fa' ? 'بررسی مجوزها...' : 'Checking authorization...'}</div>;
  }

  const tabs = [
    { id: 'assistants', label: i18n.language === 'fa' ? 'مدیریت دستیاران' : 'Manage Assistants', icon: '👥' },
    { id: 'members', label: i18n.language === 'fa' ? 'مدیریت اعضا' : 'Manage Members', icon: '👤' },
    { id: 'config', label: i18n.language === 'fa' ? 'تنظیمات' : 'Configuration', icon: '⚙️' }
  ];

  return (
    <div className="admin-page" dir="ltr">
      <div className="admin-header">
        <h1>{i18n.language === 'fa' ? 'پنل مدیریت' : 'Admin Dashboard'}</h1>
        <button className="admin-back-btn" onClick={() => navigate('/dashboard')}>
          {i18n.language === 'fa' ? 'بازگشت به داشبورد' : 'Back to Dashboard'}
        </button>
      </div>

      <div className="admin-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`admin-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span> {tab.label}
          </button>
        ))}
      </div>

      <div className="admin-content">
        {/* Assistants Tab */}
        {activeTab === 'assistants' && (
          <div className="admin-section">
            <div className="section-header">
              <h2>{i18n.language === 'fa' ? 'مدیریت دستیاران' : 'Assistants Management'}</h2>
              <button className="btn-primary" onClick={() => setShowAssistantForm(true)}>
                {i18n.language === 'fa' ? '+ افزودن دستیار' : '+ Add Assistant'}
              </button>
            </div>

            {showAssistantForm && (
              <div className="admin-form-overlay">
                <div className="admin-form-container">
                  <h3>{i18n.language === 'fa' ? 'ایجاد دستیار جدید' : 'Create New Assistant'}</h3>
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
                    <div className="form-group">
                      <label>
                        <input
                          type="checkbox"
                          checked={assistantFormData.fillProfileNow}
                          onChange={(e) => setAssistantFormData({...assistantFormData, fillProfileNow: e.target.checked})}
                        />
                        {i18n.language === 'fa' 
                          ? 'تکمیل پروفایل اکنون (در غیر این صورت دستیار باید بعد از اولین ورود تکمیل کند)'
                          : 'Fill profile now (otherwise assistant must complete after first login)'}
                      </label>
                    </div>

                    {assistantFormData.fillProfileNow && (
                      <>
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
                        <div className="form-row">
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
                            <input
                              type="number"
                              value={assistantFormData.weight}
                              onChange={(e) => setAssistantFormData({...assistantFormData, weight: e.target.value})}
                              step="0.1"
                            />
                          </div>
                          <div className="form-group">
                            <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                            <input
                              type="number"
                              value={assistantFormData.height}
                              onChange={(e) => setAssistantFormData({...assistantFormData, height: e.target.value})}
                              step="0.1"
                            />
                          </div>
                        </div>
                        <div className="form-group">
                          <label>{i18n.language === 'fa' ? 'سطح تمرین' : 'Training Level'}</label>
                          <select
                            value={assistantFormData.training_level}
                            onChange={(e) => setAssistantFormData({...assistantFormData, training_level: e.target.value})}
                          >
                            <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                            <option value="beginner">{i18n.language === 'fa' ? 'مبتدی' : 'Beginner'}</option>
                            <option value="intermediate">{i18n.language === 'fa' ? 'متوسط' : 'Intermediate'}</option>
                            <option value="advanced">{i18n.language === 'fa' ? 'پیشرفته' : 'Advanced'}</option>
                          </select>
                        </div>
                        <h4>{i18n.language === 'fa' ? 'اندازه‌گیری بدن (سانتی‌متر)' : 'Body Measurements (cm)'}</h4>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Members Tab */}
        {activeTab === 'members' && (
          <div className="admin-section">
            <div className="section-header">
              <h2>{i18n.language === 'fa' ? 'مدیریت اعضا' : 'Members Management'}</h2>
            </div>

            <div className="members-list">
              <table>
                <thead>
                  <tr>
                    <th>{i18n.language === 'fa' ? 'نام کاربری' : 'Username'}</th>
                    <th>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</th>
                    <th>{i18n.language === 'fa' ? 'تخصیص یافته به' : 'Assigned To'}</th>
                    <th>{i18n.language === 'fa' ? 'سطح تمرین' : 'Training Level'}</th>
                    <th>{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                  </tr>
                </thead>
                <tbody>
                  {members.map(member => (
                    <tr key={member.id}>
                      <td>{member.username}</td>
                      <td>{member.email}</td>
                      <td>
                        <select
                          value={member.assigned_to?.id || ''}
                          onChange={(e) => handleAssignMember(member.id, e.target.value ? parseInt(e.target.value) : null)}
                        >
                          <option value="">{i18n.language === 'fa' ? 'تخصیص نشده' : 'Unassigned'}</option>
                          <option value={user?.id}>{i18n.language === 'fa' ? 'مدیر' : 'Admin'}</option>
                          {assistants.map(assistant => (
                            <option key={assistant.id} value={assistant.id}>
                              {assistant.username} ({i18n.language === 'fa' ? 'دستیار' : 'Assistant'})
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>{member.profile?.training_level || '-'}</td>
                      <td>
                        <button 
                          className="btn-edit"
                          onClick={() => handleEditMember(member)}
                        >
                          {i18n.language === 'fa' ? 'ویرایش' : 'Edit'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {editingMember && (
              <div className="admin-form-overlay">
                <div className="admin-form-container" style={{ maxHeight: '90vh', overflowY: 'auto' }}>
                  <h3>{i18n.language === 'fa' ? `ویرایش پروفایل: ${editingMember.username}` : `Edit Profile: ${editingMember.username}`}</h3>
                  
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سن' : 'Age'}</label>
                    <input
                      type="number"
                      value={memberFormData.age || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, age: e.target.value ? parseInt(e.target.value) : null})}
                      min="1"
                      max="120"
                    />
                  </div>

                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'جنسیت' : 'Gender'}</label>
                    <select
                      value={memberFormData.gender || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, gender: e.target.value})}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="male">{i18n.language === 'fa' ? 'مرد' : 'Male'}</option>
                      <option value="female">{i18n.language === 'fa' ? 'زن' : 'Female'}</option>
                      <option value="other">{i18n.language === 'fa' ? 'سایر' : 'Other'}</option>
                    </select>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم)' : 'Weight (kg)'}</label>
                      <input
                        type="number"
                        value={memberFormData.weight || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, weight: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر)' : 'Height (cm)'}</label>
                      <input
                        type="number"
                        value={memberFormData.height || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, height: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سطح تمرین' : 'Training Level'}</label>
                    <select
                      value={memberFormData.training_level || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, training_level: e.target.value})}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="beginner">{i18n.language === 'fa' ? 'مبتدی' : 'Beginner'}</option>
                      <option value="intermediate">{i18n.language === 'fa' ? 'متوسط' : 'Intermediate'}</option>
                      <option value="advanced">{i18n.language === 'fa' ? 'پیشرفته' : 'Advanced'}</option>
                    </select>
                  </div>

                  <h4>{i18n.language === 'fa' ? 'اندازه‌گیری بدن (سانتی‌متر)' : 'Body Measurements (cm)'}</h4>
                  <div className="form-row">
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'دور سینه' : 'Chest'}</label>
                      <input
                        type="number"
                        value={memberFormData.chest_circumference || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, chest_circumference: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'دور کمر' : 'Waist'}</label>
                      <input
                        type="number"
                        value={memberFormData.waist_circumference || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, waist_circumference: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'دور شکم' : 'Abdomen'}</label>
                      <input
                        type="number"
                        value={memberFormData.abdomen_circumference || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, abdomen_circumference: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'دور بازو' : 'Arm'}</label>
                      <input
                        type="number"
                        value={memberFormData.arm_circumference || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, arm_circumference: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'دور باسن' : 'Hip'}</label>
                      <input
                        type="number"
                        value={memberFormData.hip_circumference || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, hip_circumference: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'دور ران' : 'Thigh'}</label>
                      <input
                        type="number"
                        value={memberFormData.thigh_circumference || ''}
                        onChange={(e) => setMemberFormData({...memberFormData, thigh_circumference: e.target.value ? parseFloat(e.target.value) : null})}
                        step="0.1"
                      />
                    </div>
                  </div>

                  <div className="form-actions">
                    <button type="button" className="btn-primary" onClick={handleSaveMemberProfile}>
                      {i18n.language === 'fa' ? 'ذخیره' : 'Save'}
                    </button>
                    <button type="button" className="btn-secondary" onClick={() => setEditingMember(null)}>
                      {i18n.language === 'fa' ? 'لغو' : 'Cancel'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="admin-section">
            <div className="section-header">
              <h2>{i18n.language === 'fa' ? 'تنظیمات' : 'Configuration'}</h2>
            </div>

            <div className="config-section">
              <h3>{i18n.language === 'fa' ? 'سطح‌های تمرین' : 'Training Levels'}</h3>
              {Object.keys(trainingLevels).map(level => (
                <div key={level} className="config-item">
                  <h4>{level.charAt(0).toUpperCase() + level.slice(1)}</h4>
                  <div className="form-row">
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'توضیحات (فارسی)' : 'Description (Persian)'}</label>
                      <textarea
                        value={trainingLevels[level].description_fa}
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
                        value={trainingLevels[level].description_en}
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
                  <h4>{injury.replace('_', ' ').charAt(0).toUpperCase() + injury.replace('_', ' ').slice(1)}</h4>
                  <div className="form-row">
                    <div className="form-group">
                      <label>{i18n.language === 'fa' ? 'توضیحات (فارسی)' : 'Description (Persian)'}</label>
                      <textarea
                        value={injuries[injury].description_fa}
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
                        value={injuries[injury].description_en}
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
                        value={injuries[injury].prevention_fa}
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
                        value={injuries[injury].prevention_en}
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
              <button className="btn-primary" style={{ marginTop: '1rem' }}>
                {i18n.language === 'fa' ? 'ذخیره تنظیمات' : 'Save Configuration'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPage;
