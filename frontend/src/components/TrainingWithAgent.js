import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { getApiBase } from '../services/apiBase';
import { useAuth } from '../context/AuthContext';
import './TrainingWithAgent.css';

const TrainingWithAgent = () => {
  const { t, i18n } = useTranslation();
  const API_BASE = getApiBase();
  const { user } = useAuth();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    duration: 60,
    notes: ''
  });
  const [editingMeeting, setEditingMeeting] = useState(null);

  const getAuthToken = () => {
    return localStorage.getItem('token') || axios.defaults.headers.common['Authorization']?.replace('Bearer ', '');
  };

  const getAxiosConfig = () => {
    const token = getAuthToken();
    return token ? { headers: { 'Authorization': `Bearer ${token}` } } : {};
  };

  useEffect(() => {
    if (user) {
      loadMeetings();
    }
  }, [user]);

  const loadMeetings = async () => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API_BASE}/api/meetings`, getAxiosConfig());
      setMeetings(response.data || []);
    } catch (error) {
      console.error('Error loading meetings:', error);
      setMeetings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = getAuthToken();
    if (!token) return;

    try {
      if (editingMeeting) {
        await axios.put(
          `${API_BASE}/api/meetings/${editingMeeting.id}`,
          formData,
          getAxiosConfig()
        );
      } else {
        await axios.post(
          `${API_BASE}/api/meetings`,
          formData,
          getAxiosConfig()
        );
      }
      setShowForm(false);
      setEditingMeeting(null);
      setFormData({ date: '', time: '', duration: 60, notes: '' });
      loadMeetings();
    } catch (error) {
      console.error('Error saving meeting:', error);
      alert(i18n.language === 'fa' 
        ? 'خطا در ذخیره جلسه. لطفاً دوباره تلاش کنید.'
        : 'Error saving meeting. Please try again.');
    }
  };

  const handleAccept = async (meetingId) => {
    try {
      await axios.put(
        `${API_BASE}/api/meetings/${meetingId}/accept`,
        {},
        getAxiosConfig()
      );
      loadMeetings();
    } catch (error) {
      console.error('Error accepting meeting:', error);
      alert(i18n.language === 'fa' 
        ? 'خطا در پذیرش جلسه.'
        : 'Error accepting meeting.');
    }
  };

  const handleDeny = async (meetingId) => {
    try {
      await axios.put(
        `${API_BASE}/api/meetings/${meetingId}/deny`,
        {},
        getAxiosConfig()
      );
      loadMeetings();
    } catch (error) {
      console.error('Error denying meeting:', error);
      alert(i18n.language === 'fa' 
        ? 'خطا در رد جلسه.'
        : 'Error denying meeting.');
    }
  };

  const handleEdit = (meeting) => {
    setEditingMeeting(meeting);
    setFormData({
      date: meeting.date || '',
      time: meeting.time || '',
      duration: meeting.duration || 60,
      notes: meeting.notes || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (meetingId) => {
    if (!window.confirm(i18n.language === 'fa' 
      ? 'آیا مطمئن هستید که می‌خواهید این جلسه را حذف کنید؟'
      : 'Are you sure you want to delete this meeting?')) {
      return;
    }

    try {
      await axios.delete(
        `${API_BASE}/api/meetings/${meetingId}`,
        getAxiosConfig()
      );
      loadMeetings();
    } catch (error) {
      console.error('Error deleting meeting:', error);
      alert(i18n.language === 'fa' 
        ? 'خطا در حذف جلسه.'
        : 'Error deleting meeting.');
    }
  };

  const getStatusLabel = (status) => {
    if (i18n.language === 'fa') {
      switch (status) {
        case 'pending': return 'در انتظار';
        case 'accepted': return 'پذیرفته شده';
        case 'denied': return 'رد شده';
        case 'completed': return 'تکمیل شده';
        default: return status;
      }
    } else {
      switch (status) {
        case 'pending': return 'Pending';
        case 'accepted': return 'Accepted';
        case 'denied': return 'Denied';
        case 'completed': return 'Completed';
        default: return status;
      }
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'status-pending';
      case 'accepted': return 'status-accepted';
      case 'denied': return 'status-denied';
      case 'completed': return 'status-completed';
      default: return '';
    }
  };

  return (
    <div className="training-with-agent" dir="ltr">
      <div className="training-with-agent-header">
        <h3>{i18n.language === 'fa' ? 'تمرین با مربی' : 'Training with Agent'}</h3>
        <button 
          className="new-meeting-btn"
          onClick={() => {
            setShowForm(true);
            setEditingMeeting(null);
            setFormData({ date: '', time: '', duration: 60, notes: '' });
          }}
        >
          {i18n.language === 'fa' ? '+ جلسه جدید' : '+ New Meeting'}
        </button>
      </div>

      {showForm && createPortal(
        <div className="meeting-modal-overlay" onClick={() => {
          setShowForm(false);
          setEditingMeeting(null);
          setFormData({ date: '', time: '', duration: 60, notes: '' });
        }}>
          <div className="meeting-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="meeting-modal-header">
              <h3>{editingMeeting 
                ? (i18n.language === 'fa' ? 'ویرایش جلسه' : 'Edit Meeting')
                : (i18n.language === 'fa' ? 'جلسه جدید' : 'New Meeting')}</h3>
              <button 
                className="modal-close-btn"
                onClick={() => {
                  setShowForm(false);
                  setEditingMeeting(null);
                  setFormData({ date: '', time: '', duration: 60, notes: '' });
                }}
              >
                ×
              </button>
            </div>
            <form className="meeting-form" onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'تاریخ' : 'Date'}</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{i18n.language === 'fa' ? 'زمان' : 'Time'}</label>
                  <input
                    type="time"
                    value={formData.time}
                    onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'مدت زمان (دقیقه)' : 'Duration (minutes)'}</label>
                <input
                  type="number"
                  value={formData.duration}
                  onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || 60 })}
                  min="15"
                  step="15"
                  required
                />
              </div>
              <div className="form-group">
                <label>{i18n.language === 'fa' ? 'یادداشت' : 'Notes'}</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows="3"
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="submit-btn">
                  {editingMeeting 
                    ? (i18n.language === 'fa' ? 'به‌روزرسانی' : 'Update')
                    : (i18n.language === 'fa' ? 'ایجاد' : 'Create')}
                </button>
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => {
                    setShowForm(false);
                    setEditingMeeting(null);
                    setFormData({ date: '', time: '', duration: 60, notes: '' });
                  }}
                >
                  {i18n.language === 'fa' ? 'لغو' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>,
        document.body
      )}

      <div className="meetings-list">
        {loading ? (
          <div className="loading">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
        ) : meetings.length === 0 ? (
          <div className="no-meetings">
            {i18n.language === 'fa' ? 'هیچ جلسه‌ای وجود ندارد.' : 'No meetings scheduled.'}
          </div>
        ) : (
          meetings.map((meeting) => (
            <div key={meeting.id} className="meeting-card">
              <div className="meeting-header">
                <div className="meeting-date-time">
                  <span className="meeting-date">{meeting.date}</span>
                  <span className="meeting-time">{meeting.time}</span>
                </div>
                <span className={`meeting-status ${getStatusClass(meeting.status)}`}>
                  {getStatusLabel(meeting.status)}
                </span>
              </div>
              {meeting.duration && (
                <div className="meeting-duration">
                  {i18n.language === 'fa' ? 'مدت زمان' : 'Duration'}: {meeting.duration} {i18n.language === 'fa' ? 'دقیقه' : 'minutes'}
                </div>
              )}
              {meeting.notes && (
                <div className="meeting-notes">{meeting.notes}</div>
              )}
              <div className="meeting-actions">
                {meeting.status === 'pending' && (
                  <>
                    <button 
                      className="accept-btn"
                      onClick={() => handleAccept(meeting.id)}
                    >
                      {i18n.language === 'fa' ? 'پذیرش' : 'Accept'}
                    </button>
                    <button 
                      className="deny-btn"
                      onClick={() => handleDeny(meeting.id)}
                    >
                      {i18n.language === 'fa' ? 'رد' : 'Deny'}
                    </button>
                  </>
                )}
                <button 
                  className="edit-btn"
                  onClick={() => handleEdit(meeting)}
                >
                  {i18n.language === 'fa' ? 'ویرایش' : 'Edit'}
                </button>
                <button 
                  className="delete-btn"
                  onClick={() => handleDelete(meeting.id)}
                >
                  {i18n.language === 'fa' ? 'حذف' : 'Delete'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TrainingWithAgent;

