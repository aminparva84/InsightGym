import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './NutritionTab.css';

const NutritionTab = () => {
  const { t, i18n } = useTranslation();
  const [planType, setPlanType] = useState('2week');
  const [nutritionPlans, setNutritionPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNutritionPlans();
  }, [planType]);

  const loadNutritionPlans = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/api/nutrition/plans?type=${planType}`);
      setNutritionPlans(response.data);
    } catch (error) {
      console.error('Error loading nutrition plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupByDay = (plans) => {
    const grouped = {};
    plans.forEach(plan => {
      if (!grouped[plan.day]) {
        grouped[plan.day] = [];
      }
      grouped[plan.day].push(plan);
    });
    return grouped;
  };

  const mealTypeLabels = {
    breakfast: t('breakfast'),
    lunch: t('lunch'),
    dinner: t('dinner'),
    snack: t('snack')
  };

  if (loading) {
    return <div className="loading">{t('loading')}...</div>;
  }

  const groupedPlans = groupByDay(nutritionPlans);
  const maxDays = planType === '2week' ? 14 : 28;

  return (
    <div className="nutrition-tab">
      <div className="nutrition-header">
        <h2>{t('nutrition')}</h2>
        <div className="plan-type-selector">
          <button
            className={`plan-type-btn ${planType === '2week' ? 'active' : ''}`}
            onClick={() => setPlanType('2week')}
          >
            {t('twoWeekPlan')}
          </button>
          <button
            className={`plan-type-btn ${planType === '4week' ? 'active' : ''}`}
            onClick={() => setPlanType('4week')}
          >
            {t('fourWeekPlan')}
          </button>
        </div>
      </div>

      {nutritionPlans.length === 0 ? (
        <p className="no-data">{t('noNutritionPlans')}</p>
      ) : (
        <div className="nutrition-plans">
          {Array.from({ length: maxDays }, (_, i) => i + 1).map(day => (
            <div key={day} className="nutrition-day">
              <h3 className="day-header">
                {t('day')} {day}
              </h3>
              {groupedPlans[day] ? (
                <div className="day-meals">
                  {groupedPlans[day].map(meal => (
                    <div key={meal.id} className="meal-item">
                      <div className="meal-header">
                        <span className="meal-type">{mealTypeLabels[meal.meal_type] || meal.meal_type}</span>
                        <span className="meal-food">{meal.food_item}</span>
                      </div>
                      <div className="meal-nutrition">
                        {meal.calories && (
                          <span className="nutrition-badge">
                            {t('calories')}: {meal.calories}
                          </span>
                        )}
                        {meal.protein && (
                          <span className="nutrition-badge">
                            {t('protein')}: {meal.protein}g
                          </span>
                        )}
                        {meal.carbs && (
                          <span className="nutrition-badge">
                            {t('carbs')}: {meal.carbs}g
                          </span>
                        )}
                        {meal.fats && (
                          <span className="nutrition-badge">
                            {t('fats')}: {meal.fats}g
                          </span>
                        )}
                      </div>
                      {meal.notes && (
                        <div className="meal-notes">{meal.notes}</div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-meals">{i18n.language === 'fa' ? 'بدون برنامه' : 'No plan for this day'}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NutritionTab;

