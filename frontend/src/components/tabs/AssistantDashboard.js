import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './AssistantDashboard.css';

const AssistantDashboard = () => {
  const { t, i18n } = useTranslation();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);
  const [memberDetails, setMemberDetails] = useState(null);

  useEffect(() => {
    fetchAssignedMembers();
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

  const fetchAssignedMembers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/admin/members', getAxiosConfig());
      setMembers(response.data);
    } catch (error) {
      console.error('Error fetching assigned members:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت لیست اعضا' : 'Error fetching members');
    } finally {
      setLoading(false);
    }
  };

  const fetchMemberDetails = async (memberId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/admin/members/${memberId}`, getAxiosConfig());
      setMemberDetails(response.data);
      setSelectedMember(memberId);
    } catch (error) {
      console.error('Error fetching member details:', error);
      alert(i18n.language === 'fa' ? 'خطا در دریافت جزئیات عضو' : 'Error fetching member details');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString(i18n.language === 'fa' ? 'fa-IR' : 'en-US');
  };

  return (
    <div className="assistant-dashboard" dir="ltr">
      <div className="assistant-dashboard-header">
        <h2>{i18n.language === 'fa' ? 'داشبورد دستیار' : 'Assistant Dashboard'}</h2>
        <p>{i18n.language === 'fa' ? 'اعضای تخصیص یافته به شما' : 'Members Assigned to You'}</p>
      </div>

      <div className="assistant-dashboard-content">
        <div className="members-list-panel">
          <h3>{i18n.language === 'fa' ? 'لیست اعضا' : 'Members List'}</h3>
          {loading ? (
            <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
          ) : members.length === 0 ? (
            <div className="no-members">
              {i18n.language === 'fa' ? 'هیچ عضوی به شما تخصیص داده نشده است' : 'No members assigned to you'}
            </div>
          ) : (
            <div className="members-list">
              {members.map(member => (
                <div
                  key={member.id}
                  className={`member-card ${selectedMember === member.id ? 'selected' : ''}`}
                  onClick={() => fetchMemberDetails(member.id)}
                >
                  <div className="member-card-header">
                    <h4>{member.username}</h4>
                    <span className="member-email">{member.email}</span>
                  </div>
                  <div className="member-card-info">
                    <div className="info-item">
                      <span className="info-label">{i18n.language === 'fa' ? 'سطح تمرین:' : 'Training Level:'}</span>
                      <span className="info-value">{member.profile?.training_level || '-'}</span>
                    </div>
                    {member.profile?.age && (
                      <div className="info-item">
                        <span className="info-label">{i18n.language === 'fa' ? 'سن:' : 'Age:'}</span>
                        <span className="info-value">{member.profile.age}</span>
                      </div>
                    )}
                    {member.profile?.weight && member.profile?.height && (
                      <div className="info-item">
                        <span className="info-label">{i18n.language === 'fa' ? 'BMI:' : 'BMI:'}</span>
                        <span className="info-value">
                          {(() => {
                            const heightInMeters = member.profile.height / 100;
                            const bmi = (member.profile.weight / (heightInMeters * heightInMeters)).toFixed(1);
                            return bmi;
                          })()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedMember && memberDetails && (
          <div className="member-details-panel">
            <div className="member-details-header">
              <h3>{i18n.language === 'fa' ? 'جزئیات عضو' : 'Member Details'}</h3>
              <button className="close-btn" onClick={() => {
                setSelectedMember(null);
                setMemberDetails(null);
              }}>
                {i18n.language === 'fa' ? 'بستن' : 'Close'}
              </button>
            </div>

            <div className="member-details-content">
              <div className="details-section">
                <h4>{i18n.language === 'fa' ? 'اطلاعات پایه' : 'Basic Information'}</h4>
                <div className="details-grid">
                  <div className="detail-item">
                    <label>{i18n.language === 'fa' ? 'نام کاربری:' : 'Username:'}</label>
                    <span>{memberDetails.username}</span>
                  </div>
                  <div className="detail-item">
                    <label>{i18n.language === 'fa' ? 'ایمیل:' : 'Email:'}</label>
                    <span>{memberDetails.email}</span>
                  </div>
                  {memberDetails.profile?.age && (
                    <div className="detail-item">
                      <label>{i18n.language === 'fa' ? 'سن:' : 'Age:'}</label>
                      <span>{memberDetails.profile.age}</span>
                    </div>
                  )}
                  {memberDetails.profile?.gender && (
                    <div className="detail-item">
                      <label>{i18n.language === 'fa' ? 'جنسیت:' : 'Gender:'}</label>
                      <span>
                        {memberDetails.profile.gender === 'male' 
                          ? (i18n.language === 'fa' ? 'مرد' : 'Male')
                          : memberDetails.profile.gender === 'female'
                          ? (i18n.language === 'fa' ? 'زن' : 'Female')
                          : (i18n.language === 'fa' ? 'سایر' : 'Other')}
                      </span>
                    </div>
                  )}
                  {memberDetails.profile?.weight && (
                    <div className="detail-item">
                      <label>{i18n.language === 'fa' ? 'وزن (کیلوگرم):' : 'Weight (kg):'}</label>
                      <span>{memberDetails.profile.weight}</span>
                    </div>
                  )}
                  {memberDetails.profile?.height && (
                    <div className="detail-item">
                      <label>{i18n.language === 'fa' ? 'قد (سانتی‌متر):' : 'Height (cm):'}</label>
                      <span>{memberDetails.profile.height}</span>
                    </div>
                  )}
                  {memberDetails.profile?.training_level && (
                    <div className="detail-item">
                      <label>{i18n.language === 'fa' ? 'سطح تمرین:' : 'Training Level:'}</label>
                      <span>
                        {memberDetails.profile.training_level === 'beginner'
                          ? (i18n.language === 'fa' ? 'مبتدی' : 'Beginner')
                          : memberDetails.profile.training_level === 'intermediate'
                          ? (i18n.language === 'fa' ? 'متوسط' : 'Intermediate')
                          : (i18n.language === 'fa' ? 'پیشرفته' : 'Advanced')}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {memberDetails.profile && (
                <>
                  {(memberDetails.profile.chest_circumference || 
                    memberDetails.profile.waist_circumference || 
                    memberDetails.profile.abdomen_circumference ||
                    memberDetails.profile.arm_circumference ||
                    memberDetails.profile.hip_circumference ||
                    memberDetails.profile.thigh_circumference) && (
                    <div className="details-section">
                      <h4>{i18n.language === 'fa' ? 'اندازه‌گیری بدن (سانتی‌متر)' : 'Body Measurements (cm)'}</h4>
                      <div className="details-grid">
                        {memberDetails.profile.chest_circumference && (
                          <div className="detail-item">
                            <label>{i18n.language === 'fa' ? 'دور سینه:' : 'Chest:'}</label>
                            <span>{memberDetails.profile.chest_circumference}</span>
                          </div>
                        )}
                        {memberDetails.profile.waist_circumference && (
                          <div className="detail-item">
                            <label>{i18n.language === 'fa' ? 'دور کمر:' : 'Waist:'}</label>
                            <span>{memberDetails.profile.waist_circumference}</span>
                          </div>
                        )}
                        {memberDetails.profile.abdomen_circumference && (
                          <div className="detail-item">
                            <label>{i18n.language === 'fa' ? 'دور شکم:' : 'Abdomen:'}</label>
                            <span>{memberDetails.profile.abdomen_circumference}</span>
                          </div>
                        )}
                        {memberDetails.profile.arm_circumference && (
                          <div className="detail-item">
                            <label>{i18n.language === 'fa' ? 'دور بازو:' : 'Arm:'}</label>
                            <span>{memberDetails.profile.arm_circumference}</span>
                          </div>
                        )}
                        {memberDetails.profile.hip_circumference && (
                          <div className="detail-item">
                            <label>{i18n.language === 'fa' ? 'دور باسن:' : 'Hip:'}</label>
                            <span>{memberDetails.profile.hip_circumference}</span>
                          </div>
                        )}
                        {memberDetails.profile.thigh_circumference && (
                          <div className="detail-item">
                            <label>{i18n.language === 'fa' ? 'دور ران:' : 'Thigh:'}</label>
                            <span>{memberDetails.profile.thigh_circumference}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {memberDetails.profile.injuries && memberDetails.profile.injuries.length > 0 && (
                    <div className="details-section">
                      <h4>{i18n.language === 'fa' ? 'آسیب‌ها' : 'Injuries'}</h4>
                      <div className="injuries-list">
                        {memberDetails.profile.injuries.map((injury, index) => (
                          <div key={index} className="injury-item">
                            <span className="injury-name">{injury}</span>
                          </div>
                        ))}
                      </div>
                      {memberDetails.profile.injury_details && (
                        <div className="injury-details">
                          <p>{memberDetails.profile.injury_details}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {memberDetails.profile.fitness_goals && memberDetails.profile.fitness_goals.length > 0 && (
                    <div className="details-section">
                      <h4>{i18n.language === 'fa' ? 'اهداف تناسب اندام' : 'Fitness Goals'}</h4>
                      <div className="goals-list">
                        {memberDetails.profile.fitness_goals.map((goal, index) => (
                          <div key={index} className="goal-item">
                            <span>{goal}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {memberDetails.profile.medical_conditions && memberDetails.profile.medical_conditions.length > 0 && (
                    <div className="details-section">
                      <h4>{i18n.language === 'fa' ? 'شرایط پزشکی' : 'Medical Conditions'}</h4>
                      <div className="conditions-list">
                        {memberDetails.profile.medical_conditions.map((condition, index) => (
                          <div key={index} className="condition-item">
                            <span>{condition}</span>
                          </div>
                        ))}
                      </div>
                      {memberDetails.profile.medical_condition_details && (
                        <div className="condition-details">
                          <p>{memberDetails.profile.medical_condition_details}</p>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssistantDashboard;



