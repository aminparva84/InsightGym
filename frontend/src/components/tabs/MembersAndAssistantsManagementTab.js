import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import MembersListTab from './MembersListTab';
import AdminTab from './AdminTab';
import HistoryTab from './HistoryTab';
import BreakRequestsTab from './BreakRequestsTab';
import './MembersAndAssistantsManagementTab.css';

const SUB_TABS = [
  { id: 'member-list', labelKey: 'memberList', icon: '👥' },
  { id: 'assistants', labelKey: 'assistants', icon: '👤' },
  { id: 'chat-history', labelKey: 'chatHistory', icon: '💬' },
  { id: 'break-request', labelKey: 'breakRequest', icon: '⏸️' }
];

const MembersAndAssistantsManagementTab = () => {
  const { i18n } = useTranslation();
  const [activeSubTab, setActiveSubTab] = useState('member-list');

  const getSubTabLabel = (labelKey) => {
    const labels = {
      memberList: i18n.language === 'fa' ? 'لیست اعضا' : 'Member List',
      assistants: i18n.language === 'fa' ? 'دستیاران' : 'Assistants',
      chatHistory: i18n.language === 'fa' ? 'تاریخچه پیام‌ها' : 'Chat History',
      breakRequest: i18n.language === 'fa' ? 'درخواست استراحت' : 'Break Request'
    };
    return labels[labelKey] || labelKey;
  };

  return (
    <div className="members-assistants-management">
      <div className="sub-tabs-container">
        {SUB_TABS.map(tab => (
          <button
            key={tab.id}
            type="button"
            className={`sub-tab-btn ${activeSubTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveSubTab(tab.id)}
          >
            <span className="sub-tab-icon">{tab.icon}</span>
            {getSubTabLabel(tab.labelKey)}
          </button>
        ))}
      </div>
      <div className="sub-tab-content">
        {activeSubTab === 'member-list' && <MembersListTab />}
        {activeSubTab === 'assistants' && <AdminTab />}
        {activeSubTab === 'chat-history' && <HistoryTab showOnlyMessages={true} />}
        {activeSubTab === 'break-request' && <BreakRequestsTab />}
      </div>
    </div>
  );
};

export default MembersAndAssistantsManagementTab;
