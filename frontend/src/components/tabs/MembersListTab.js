import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import { getApiBase } from '../../services/apiBase';
import './MembersListTab.css';

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
  { value: 'neck', label_fa: 'گردن', label_en: 'Neck' },
  { value: 'wrist', label_fa: 'مچ دست', label_en: 'Wrist' },
  { value: 'ankle', label_fa: 'مچ پا', label_en: 'Ankle' }
];
const medicalConditionOptions = [
  { value: 'heart_disease', label_fa: 'بیماری قلبی', label_en: 'Heart Disease' },
  { value: 'high_blood_pressure', label_fa: 'فشار خون بالا', label_en: 'High Blood Pressure' },
  { value: 'pregnancy', label_fa: 'بارداری', label_en: 'Pregnancy' }
];
const equipmentAccessOptions = [
  { value: 'machine', label_fa: 'دستگاه', label_en: 'Machine' },
  { value: 'dumbbells', label_fa: 'دمبل', label_en: 'Dumbbells' },
  { value: 'barbell', label_fa: 'میله', label_en: 'Barbell' },
  { value: 'cable', label_fa: 'کابل', label_en: 'Cable' }
];
const homeEquipmentOptions = [
  { value: 'dumbbells', label_fa: 'دمبل', label_en: 'Dumbbells' },
  { value: 'resistance_bands', label_fa: 'بند مقاومتی', label_en: 'Resistance Bands' },
  { value: 'yoga_mat', label_fa: 'مت یوگا', label_en: 'Yoga Mat' },
  { value: 'body_weight_only', label_fa: 'فقط وزن بدن', label_en: 'Body Weight Only' }
];

const MembersListTab = () => {
  const { i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user } = useAuth();
  const [members, setMembers] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [memberFormData, setMemberFormData] = useState({});
  const [userRole, setUserRole] = useState(null);

  const getAuthToken = useCallback(() => {
    const localToken = localStorage.getItem('token');
    if (localToken && localToken.trim() !== '') {
      return localToken.trim();
    }
    return null;
  }, []);

  const getAxiosConfig = useCallback(() => {
    const token = getAuthToken();
    return {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };
  }, [getAuthToken]);

  const fetchMembers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/admin/members`, getAxiosConfig());
      setMembers(response.data);
    } catch (error) {
      console.error('Error fetching members:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست اعضا' : 'Error fetching members');
    } finally {
      setLoading(false);
    }
  }, [API_BASE, getAxiosConfig, i18n.language]);

  const fetchAssistants = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/admin/assistants`, getAxiosConfig());
      setAssistants(response.data);
    } catch (error) {
      console.error('Error fetching assistants:', error);
    }
  }, [API_BASE, getAxiosConfig]);

  const checkUserRole = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/admin/check-admin`, getAxiosConfig());
      setUserRole(response.data.role || 'member');
    } catch (error) {
      console.error('Error checking user role:', error);
      setUserRole('member');
    }
  }, [API_BASE, getAxiosConfig]);

  useEffect(() => {
    checkUserRole();
    fetchMembers();
    fetchAssistants();
  }, [checkUserRole, fetchMembers, fetchAssistants]);

  const handleAssignMember = async (memberId, assistantId) => {
    try {
      await axios.post(`${API_BASE}/api/admin/members/${memberId}/assign`, {
        assigned_to_id: assistantId || null
      }, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'تخصیص با موفقیت انجام شد' : 'Assignment successful');
      fetchMembers();
    } catch (error) {
      console.error('Error assigning member:', error);
      alert(i18n.language === 'fa' ? 'خطا در تخصیص عضو' : 'Error assigning member');
    }
  };

  const fetchMemberDetails = async (memberId) => {
    try {
      const response = await axios.get(`${API_BASE}/api/admin/members/${memberId}`, getAxiosConfig());
      return response.data;
    } catch (error) {
      console.error('Error fetching member details:', error);
      return null;
    }
  };

  const handleArrayChange = (field, value, checked) => {
    const arr = Array.isArray(memberFormData[field]) ? [...memberFormData[field]] : [];
    const next = checked ? (arr.includes(value) ? arr : [...arr, value]) : arr.filter(x => x !== value);
    setMemberFormData({ ...memberFormData, [field]: next });
  };

  const handleEditMember = async (member) => {
    setEditingMember(member);
    const full = await fetchMemberDetails(member.id);
    if (full) {
      const profile = full.profile || {};
      setMemberFormData({
        username: full.username || '',
        email: full.email || '',
        age: profile.age ?? '',
        weight: profile.weight ?? '',
        height: profile.height ?? '',
        gender: profile.gender || '',
        training_level: profile.training_level || '',
        chest_circumference: profile.chest_circumference ?? '',
        waist_circumference: profile.waist_circumference ?? '',
        abdomen_circumference: profile.abdomen_circumference ?? '',
        arm_circumference: profile.arm_circumference ?? '',
        hip_circumference: profile.hip_circumference ?? '',
        thigh_circumference: profile.thigh_circumference ?? '',
        fitness_goals: Array.isArray(profile.fitness_goals) ? profile.fitness_goals : [],
        injuries: Array.isArray(profile.injuries) ? profile.injuries : [],
        injury_details: profile.injury_details || '',
        medical_conditions: Array.isArray(profile.medical_conditions) ? profile.medical_conditions : [],
        medical_condition_details: profile.medical_condition_details || '',
        exercise_history_years: profile.exercise_history_years ?? '',
        exercise_history_description: profile.exercise_history_description || '',
        equipment_access: Array.isArray(profile.equipment_access) ? profile.equipment_access : [],
        gym_access: profile.gym_access || false,
        home_equipment: Array.isArray(profile.home_equipment) ? profile.home_equipment : [],
        preferred_workout_time: profile.preferred_workout_time || '',
        workout_days_per_week: profile.workout_days_per_week ?? '',
        preferred_intensity: profile.preferred_intensity || ''
      });
    } else {
      setMemberFormData({ ...member.profile, username: member.username, email: member.email });
    }
  };

  const handleSaveMemberProfile = async () => {
    try {
      const { username, email, ...profilePayload } = memberFormData;
      if (username !== editingMember.username || email !== editingMember.email) {
        await axios.put(`${API_BASE}/api/admin/members/${editingMember.id}`, { username, email }, getAxiosConfig());
      }
      await axios.put(`${API_BASE}/api/admin/members/${editingMember.id}/profile`, profilePayload, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'پروفایل عضو به‌روزرسانی شد' : 'Member profile updated');
      setEditingMember(null);
      fetchMembers();
    } catch (error) {
      console.error('Error updating member profile:', error);
      alert(i18n.language === 'fa' ? 'خطا در به‌روزرسانی پروفایل' : 'Error updating profile');
    }
  };

  const handleDeleteMember = async (memberId) => {
    try {
      await axios.delete(`${API_BASE}/api/admin/members/${memberId}`, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'عضو با موفقیت حذف شد' : 'Member deleted successfully');
      fetchMembers();
    } catch (error) {
      console.error('Error deleting member:', error);
      alert(i18n.language === 'fa' 
        ? `خطا در حذف عضو: ${error.response?.data?.error || error.message}`
        : `Error deleting member: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <div className="members-list-tab" dir="ltr">
      <div className="members-list-header">
        <h2>{i18n.language === 'fa' ? 'لیست اعضا' : 'Members List'}</h2>
      </div>

      {loading ? (
        <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
      ) : (
        <div className="members-list-container">
          <div className="members-table-wrapper">
            <table className="members-table">
              <thead>
                <tr>
                  <th>{i18n.language === 'fa' ? 'نام کاربری' : 'Username'}</th>
                  <th>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</th>
                  <th>{i18n.language === 'fa' ? 'تخصیص یافته به' : 'Assigned To'}</th>
                  <th>{i18n.language === 'fa' ? 'سطح تمرین' : 'Training Level'}</th>
                  {userRole === 'admin' && (
                    <>
                      <th>{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                      <th>{i18n.language === 'fa' ? 'حذف' : 'Delete'}</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {members.length === 0 ? (
                  <tr>
                    <td colSpan={userRole === 'admin' ? 6 : 4} className="no-data">
                      {i18n.language === 'fa' ? 'هیچ عضوی یافت نشد' : 'No members found'}
                    </td>
                  </tr>
                ) : (
                  members.map(member => (
                    <tr key={member.id}>
                      <td>{member.username}</td>
                      <td>{member.email}</td>
                      <td>
                        {userRole === 'admin' ? (
                          <select
                            value={
                              member.assigned_to?.id === user?.id 
                                ? 'admin' 
                                : (member.assigned_to?.id || '')
                            }
                            onChange={(e) => {
                              const value = e.target.value;
                              if (value === 'admin') {
                                handleAssignMember(member.id, user?.id || null);
                              } else {
                                handleAssignMember(member.id, value ? parseInt(value) : null);
                              }
                            }}
                          >
                            <option value="">{i18n.language === 'fa' ? 'تخصیص نشده' : 'Unassigned'}</option>
                            <option value="admin">{i18n.language === 'fa' ? 'مدیر' : 'Admin'}</option>
                            {assistants.map(assistant => (
                              <option key={assistant.id} value={assistant.id}>
                                {assistant.username} ({i18n.language === 'fa' ? 'دستیار' : 'Assistant'})
                              </option>
                            ))}
                          </select>
                        ) : (
                          <span>
                            {member.assigned_to 
                              ? (member.assigned_to.id === user?.id 
                                  ? (i18n.language === 'fa' ? 'مدیر' : 'Admin')
                                  : `${member.assigned_to.username} (${i18n.language === 'fa' ? 'دستیار' : 'Assistant'})`)
                              : (i18n.language === 'fa' ? 'تخصیص نشده' : 'Unassigned')
                            }
                          </span>
                        )}
                      </td>
                      <td>{member.profile?.training_level || '-'}</td>
                      <td>
                        {userRole === 'admin' && (
                          <button 
                            className="btn-edit"
                            onClick={() => handleEditMember(member)}
                          >
                            {i18n.language === 'fa' ? 'ویرایش' : 'Edit'}
                          </button>
                        )}
                      </td>
                      <td>
                        {userRole === 'admin' && (
                          <button 
                            className="btn-delete"
                            onClick={() => {
                              if (window.confirm(
                                i18n.language === 'fa' 
                                  ? `آیا مطمئن هستید که می‌خواهید عضو "${member.username}" را حذف کنید؟`
                                  : `Are you sure you want to delete member "${member.username}"?`
                              )) {
                                handleDeleteMember(member.id);
                              }
                            }}
                          >
                            {i18n.language === 'fa' ? 'حذف' : 'Delete'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {editingMember && (
            <div className="admin-form-overlay">
              <div className="admin-form-container" style={{ maxHeight: '90vh', overflowY: 'auto' }}>
                <h3>{i18n.language === 'fa' ? `ویرایش پروفایل: ${editingMember.username}` : `Edit Profile: ${editingMember.username}`}</h3>
                
                <h4>{i18n.language === 'fa' ? 'اطلاعات حساب' : 'Account'}</h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'نام کاربری' : 'Username'}</label>
                    <input
                      type="text"
                      value={memberFormData.username || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, username: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}</label>
                    <input
                      type="email"
                      value={memberFormData.email || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, email: e.target.value})}
                    />
                  </div>
                </div>

                <h4>{i18n.language === 'fa' ? 'اطلاعات پایه' : 'Basic Info'}</h4>
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

                <h4>{i18n.language === 'fa' ? 'اهداف تناسب اندام' : 'Fitness Goals'}</h4>
                <div className="form-group checkbox-group">
                  {fitnessGoalsOptions.map(opt => (
                    <label key={opt.value} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={(memberFormData.fitness_goals || []).includes(opt.value)}
                        onChange={(e) => handleArrayChange('fitness_goals', opt.value, e.target.checked)}
                      />
                      <span>{i18n.language === 'fa' ? opt.label_fa : opt.label_en}</span>
                    </label>
                  ))}
                </div>

                <h4>{i18n.language === 'fa' ? 'آسیب‌ها و شرایط پزشکی' : 'Injuries & Medical'}</h4>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'آسیب‌ها' : 'Injuries'}</label>
                  <div className="checkbox-group">
                    {injuryOptions.map(opt => (
                      <label key={opt.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={(memberFormData.injuries || []).includes(opt.value)}
                          onChange={(e) => handleArrayChange('injuries', opt.value, e.target.checked)}
                        />
                        <span>{i18n.language === 'fa' ? opt.label_fa : opt.label_en}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'جزئیات آسیب' : 'Injury Details'}</label>
                  <textarea
                    value={memberFormData.injury_details || ''}
                    onChange={(e) => setMemberFormData({...memberFormData, injury_details: e.target.value})}
                    rows="2"
                  />
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'شرایط پزشکی' : 'Medical Conditions'}</label>
                  <div className="checkbox-group">
                    {medicalConditionOptions.map(opt => (
                      <label key={opt.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={(memberFormData.medical_conditions || []).includes(opt.value)}
                          onChange={(e) => handleArrayChange('medical_conditions', opt.value, e.target.checked)}
                        />
                        <span>{i18n.language === 'fa' ? opt.label_fa : opt.label_en}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'جزئیات شرایط پزشکی' : 'Medical Condition Details'}</label>
                  <textarea
                    value={memberFormData.medical_condition_details || ''}
                    onChange={(e) => setMemberFormData({...memberFormData, medical_condition_details: e.target.value})}
                    rows="2"
                  />
                </div>

                <h4>{i18n.language === 'fa' ? 'تاریخچه تمرین' : 'Exercise History'}</h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'سال‌های تجربه' : 'Years of Experience'}</label>
                    <input
                      type="number"
                      value={memberFormData.exercise_history_years ?? ''}
                      onChange={(e) => setMemberFormData({...memberFormData, exercise_history_years: e.target.value ? parseInt(e.target.value) : null})}
                      min="0"
                      max="80"
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'توضیحات' : 'Description'}</label>
                    <input
                      type="text"
                      value={memberFormData.exercise_history_description || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, exercise_history_description: e.target.value})}
                    />
                  </div>
                </div>

                <h4>{i18n.language === 'fa' ? 'دسترسی به تجهیزات' : 'Equipment Access'}</h4>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'تجهیزات در دسترس' : 'Equipment Access'}</label>
                  <div className="checkbox-group">
                    {equipmentAccessOptions.map(opt => (
                      <label key={opt.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={(memberFormData.equipment_access || []).includes(opt.value)}
                          onChange={(e) => handleArrayChange('equipment_access', opt.value, e.target.checked)}
                        />
                        <span>{i18n.language === 'fa' ? opt.label_fa : opt.label_en}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={!!memberFormData.gym_access}
                      onChange={(e) => setMemberFormData({...memberFormData, gym_access: e.target.checked})}
                    />
                    <span>{i18n.language === 'fa' ? 'دسترسی به باشگاه' : 'Gym Access'}</span>
                  </label>
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'تجهیزات خانگی' : 'Home Equipment'}</label>
                  <div className="checkbox-group">
                    {homeEquipmentOptions.map(opt => (
                      <label key={opt.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={(memberFormData.home_equipment || []).includes(opt.value)}
                          onChange={(e) => handleArrayChange('home_equipment', opt.value, e.target.checked)}
                        />
                        <span>{i18n.language === 'fa' ? opt.label_fa : opt.label_en}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <h4>{i18n.language === 'fa' ? 'ترجیحات تمرین' : 'Workout Preferences'}</h4>
                <div className="form-row">
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'زمان ترجیحی' : 'Preferred Time'}</label>
                    <select
                      value={memberFormData.preferred_workout_time || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, preferred_workout_time: e.target.value})}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="morning">{i18n.language === 'fa' ? 'صبح' : 'Morning'}</option>
                      <option value="afternoon">{i18n.language === 'fa' ? 'عصر' : 'Afternoon'}</option>
                      <option value="evening">{i18n.language === 'fa' ? 'شب' : 'Evening'}</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'روزهای تمرین در هفته' : 'Days per Week'}</label>
                    <input
                      type="number"
                      value={memberFormData.workout_days_per_week ?? ''}
                      onChange={(e) => setMemberFormData({...memberFormData, workout_days_per_week: e.target.value ? parseInt(e.target.value) : null})}
                      min="1"
                      max="7"
                    />
                  </div>
                  <div className="form-group">
                    <label>{i18n.language === 'fa' ? 'شدت ترجیحی' : 'Preferred Intensity'}</label>
                    <select
                      value={memberFormData.preferred_intensity || ''}
                      onChange={(e) => setMemberFormData({...memberFormData, preferred_intensity: e.target.value})}
                    >
                      <option value="">{i18n.language === 'fa' ? 'انتخاب کنید' : 'Select'}</option>
                      <option value="light">{i18n.language === 'fa' ? 'سبک' : 'Light'}</option>
                      <option value="medium">{i18n.language === 'fa' ? 'متوسط' : 'Medium'}</option>
                      <option value="heavy">{i18n.language === 'fa' ? 'سنگین' : 'Heavy'}</option>
                    </select>
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
    </div>
  );
};

export default MembersListTab;
