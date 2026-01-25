import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import './MembersListTab.css';

const MembersListTab = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [members, setMembers] = useState([]);
  const [assistants, setAssistants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [memberFormData, setMemberFormData] = useState({});

  useEffect(() => {
    fetchMembers();
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

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/admin/members', getAxiosConfig());
      setMembers(response.data);
    } catch (error) {
      console.error('Error fetching members:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست اعضا' : 'Error fetching members');
    } finally {
      setLoading(false);
    }
  };

  const fetchAssistants = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/admin/assistants', getAxiosConfig());
      setAssistants(response.data);
    } catch (error) {
      console.error('Error fetching assistants:', error);
    }
  };

  const handleAssignMember = async (memberId, assistantId) => {
    try {
      await axios.post(`http://localhost:5000/api/admin/members/${memberId}/assign`, {
        assigned_to_id: assistantId || null
      }, getAxiosConfig());
      alert(i18n.language === 'fa' ? 'تخصیص با موفقیت انجام شد' : 'Assignment successful');
      fetchMembers();
    } catch (error) {
      console.error('Error assigning member:', error);
      alert(i18n.language === 'fa' ? 'خطا در تخصیص عضو' : 'Error assigning member');
    }
  };

  const handleEditMember = (member) => {
    setEditingMember(member);
    setMemberFormData(member.profile || {});
  };

  const handleSaveMemberProfile = async () => {
    try {
      await axios.put(`http://localhost:5000/api/admin/members/${editingMember.id}/profile`, memberFormData, getAxiosConfig());
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
      await axios.delete(`http://localhost:5000/api/admin/members/${memberId}`, getAxiosConfig());
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
                  <th>{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                  <th>{i18n.language === 'fa' ? 'حذف' : 'Delete'}</th>
                </tr>
              </thead>
              <tbody>
                {members.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="no-data">
                      {i18n.language === 'fa' ? 'هیچ عضوی یافت نشد' : 'No members found'}
                    </td>
                  </tr>
                ) : (
                  members.map(member => (
                    <tr key={member.id}>
                      <td>{member.username}</td>
                      <td>{member.email}</td>
                      <td>
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
                      <td>
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
    </div>
  );
};

export default MembersListTab;
