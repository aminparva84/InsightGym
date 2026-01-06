import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import RegistrationForm from './RegistrationForm';
import './AuthModal.css';

const AuthModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const [activeTab, setActiveTab] = useState('login'); // 'login' or 'signup'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    setLoading(false);
    if (!result.success) {
      setError(result.error);
    } else {
      // Login successful, close modal
      onClose();
      setUsername('');
      setPassword('');
      setError('');
    }
  };

  const handleRegistrationComplete = () => {
    // Registration successful, user is automatically logged in
    onClose();
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setError('');
    if (tab === 'login') {
      setUsername('');
      setPassword('');
    }
  };

  const handleClose = () => {
    onClose();
    setError('');
    setUsername('');
    setPassword('');
    setActiveTab('login');
  };

  return (
    <div className="auth-modal-overlay" onClick={handleClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="auth-modal-close" onClick={handleClose}>
          ×
        </button>

        <div className="auth-modal-header">
          <h2 className="auth-modal-title">
            {i18n.language === 'fa' ? 'شروع کنید' : "Let's Start"}
          </h2>
        </div>

        <div className="auth-modal-tabs">
          <button
            className={`auth-modal-tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => handleTabChange('login')}
          >
            {t('login')}
          </button>
          <button
            className={`auth-modal-tab ${activeTab === 'signup' ? 'active' : ''}`}
            onClick={() => handleTabChange('signup')}
          >
            {t('register')}
          </button>
        </div>

        <div className="auth-modal-content">
          {activeTab === 'login' ? (
            <form className="auth-modal-form" onSubmit={handleLoginSubmit}>
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-group">
                <label>{t('username')}</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>{t('password')}</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? t('loading') : t('login')}
              </button>
            </form>
          ) : (
            <div className="auth-modal-signup">
              <RegistrationForm onComplete={handleRegistrationComplete} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;

