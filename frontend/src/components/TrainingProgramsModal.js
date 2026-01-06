import React from 'react';
import { useTranslation } from 'react-i18next';
import './TrainingProgramsModal.css';

const TrainingProgramsModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();

  if (!isOpen) return null;

  const trainingPrograms = [
    {
      id: 1,
      nameKey: 'trainingProgram1',
      descriptionKey: 'trainingProgram1Desc',
      priceKey: 'trainingProgram1Price',
      icon: '💪',
      features: ['feature1', 'feature2', 'feature3']
    },
    {
      id: 2,
      nameKey: 'trainingProgram2',
      descriptionKey: 'trainingProgram2Desc',
      priceKey: 'trainingProgram2Price',
      icon: '🔥',
      features: ['feature1', 'feature2', 'feature3', 'feature4']
    },
    {
      id: 3,
      nameKey: 'trainingProgram3',
      descriptionKey: 'trainingProgram3Desc',
      priceKey: 'trainingProgram3Price',
      icon: '⭐',
      features: ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
    },
    {
      id: 4,
      nameKey: 'trainingProgram4',
      descriptionKey: 'trainingProgram4Desc',
      priceKey: 'trainingProgram4Price',
      icon: '👑',
      features: ['feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6']
    }
  ];

  const handleClose = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleBuyClick = (programId) => {
    // Handle purchase logic here
    console.log(`Purchasing program ${programId}`);
    // You can add navigation or payment processing here
  };

  return (
    <div className="training-programs-modal-overlay" onClick={handleClose}>
      <div className="training-programs-modal" onClick={(e) => e.stopPropagation()}>
        <button className="training-programs-modal-close" onClick={onClose}>
          ×
        </button>

        <div className="training-programs-modal-header">
          <h2 className="training-programs-modal-title">
            {i18n.language === 'fa' ? 'خرید برنامه تمرینی' : 'Buy a Training Programme'}
          </h2>
          <p className="training-programs-modal-subtitle">
            {i18n.language === 'fa' 
              ? 'برنامه تمرینی مناسب خود را انتخاب کنید' 
              : 'Choose the training programme that suits you'}
          </p>
        </div>

        <div className="training-programs-grid">
          {trainingPrograms.map((program) => (
            <div key={program.id} className="training-program-card">
              <div className="program-icon">{program.icon}</div>
              <h3 className="program-name">{t(program.nameKey)}</h3>
              <p className="program-description">{t(program.descriptionKey)}</p>
              <div className="program-features">
                <ul>
                  {program.features.map((feature, index) => (
                    <li key={index}>{t(feature)}</li>
                  ))}
                </ul>
              </div>
              <div className="program-price">{t(program.priceKey)}</div>
              <button 
                className="program-buy-btn"
                onClick={() => handleBuyClick(program.id)}
              >
                {i18n.language === 'fa' ? 'خرید' : 'Buy Now'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TrainingProgramsModal;

