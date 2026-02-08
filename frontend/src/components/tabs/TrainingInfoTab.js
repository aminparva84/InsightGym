import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import TrainingLevelsInfoTab from './TrainingLevelsInfoTab';
import ExerciseLibraryTab from './ExerciseLibraryTab';
import TrainingMovementInfoTab from './TrainingMovementInfoTab';
import WarmingCooldownTab from './WarmingCooldownTab';
import DashboardIcon from '../DashboardIcon';
import './TrainingInfoTab.css';

const SUBTABS = [
  { id: 'training-levels', labelKeyFa: 'اطلاعات سطح‌های تمرینی', labelKeyEn: 'Training Levels Info', icon: 'bar_chart' },
  { id: 'exercise-library', labelKeyFa: 'کتابخانه تمرینات', labelKeyEn: 'Exercise Library', icon: 'menu_book' },
  { id: 'training-movement-info', labelKeyFa: 'اطلاعات حرکات تمرینی', labelKeyEn: 'Training Movement Info', icon: 'videocam' },
  { id: 'warming-cooldown', labelKeyFa: 'گرم کردن و سرد کردن', labelKeyEn: 'Warming & Cooldown', icon: 'ac_unit' }
];

const TrainingInfoTab = () => {
  const { i18n } = useTranslation();
  const [activeSubTab, setActiveSubTab] = useState('training-levels');
  const fa = i18n.language === 'fa';

  const renderSubTabContent = () => {
    switch (activeSubTab) {
      case 'training-levels':
        return <TrainingLevelsInfoTab />;
      case 'exercise-library':
        return <ExerciseLibraryTab />;
      case 'training-movement-info':
        return <TrainingMovementInfoTab />;
      case 'warming-cooldown':
        return <WarmingCooldownTab />;
      default:
        return <TrainingLevelsInfoTab />;
    }
  };

  return (
    <div className="training-info-tab" dir="ltr">
      <div className="training-info-subtabs">
        {SUBTABS.map((sub) => (
          <button
            key={sub.id}
            type="button"
            className={`training-info-subtab-btn ${activeSubTab === sub.id ? 'active' : ''}`}
            onClick={() => setActiveSubTab(sub.id)}
          >
            <span className="training-info-subtab-icon"><DashboardIcon name={sub.icon} /></span>
            {fa ? sub.labelKeyFa : sub.labelKeyEn}
          </button>
        ))}
      </div>
      <div className="training-info-content">
        {renderSubTabContent()}
      </div>
    </div>
  );
};

export default TrainingInfoTab;
