import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './MembersProgramsTab.css';

const MembersProgramsTab = () => {
  const { t, i18n } = useTranslation();
  const [members, setMembers] = useState([]);
  const [selectedMember, setSelectedMember] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMembers();
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
    } finally {
      setLoading(false);
    }
  };

  const fetchMemberPrograms = async (memberId) => {
    try {
      setLoading(true);
      setSelectedMember(memberId);
      // TODO: Replace with actual API endpoint when available
      // const response = await axios.get(`http://localhost:5000/api/members/${memberId}/programs`, getAxiosConfig());
      // setPrograms(response.data);
      setPrograms([]); // Placeholder
    } catch (error) {
      console.error('Error fetching programs:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="members-programs-tab" dir="ltr">
      <div className="programs-header">
        <h2>{i18n.language === 'fa' ? 'برنامه اعضا' : 'Members Programs'}</h2>
      </div>

      <div className="programs-content">
        <div className="members-sidebar">
          <h3>{i18n.language === 'fa' ? 'لیست اعضا' : 'Members List'}</h3>
          {loading ? (
            <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
          ) : (
            <div className="members-list">
              {members.map(member => (
                <div
                  key={member.id}
                  className={`member-item ${selectedMember === member.id ? 'active' : ''}`}
                  onClick={() => fetchMemberPrograms(member.id)}
                >
                  {member.username}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="programs-main">
          {selectedMember ? (
            programs.length === 0 ? (
              <div className="no-programs">
                <p>{i18n.language === 'fa' ? 'برنامه‌ای برای این عضو ثبت نشده است' : 'No programs found for this member'}</p>
              </div>
            ) : (
              <div className="programs-list">
                {programs.map(program => (
                  <div key={program.id} className="program-card">
                    <h3>{program.name}</h3>
                    <p>{program.description}</p>
                  </div>
                ))}
              </div>
            )
          ) : (
            <div className="select-member-prompt">
              <p>{i18n.language === 'fa' ? 'لطفاً یک عضو را انتخاب کنید' : 'Please select a member'}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MembersProgramsTab;


