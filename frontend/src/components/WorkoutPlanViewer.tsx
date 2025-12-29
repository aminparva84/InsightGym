/**
 * React component for viewing 6-month workout plan
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { workoutPlanService, WorkoutPlan, WeeklyTable } from '../services/workoutPlanService';
import './WorkoutPlanViewer.css';

const WorkoutPlanViewer: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [plan, setPlan] = useState<WorkoutPlan | null>(null);
  const [weeklyTable, setWeeklyTable] = useState<{ [key: string]: WeeklyTable } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [selectedWeek, setSelectedWeek] = useState(1);
  const [viewMode, setViewMode] = useState<'plan' | 'table'>('table');

  useEffect(() => {
    loadWorkoutPlan();
  }, []);

  const loadWorkoutPlan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await workoutPlanService.generate6MonthPlan(i18n.language as 'fa' | 'en');
      setPlan(result.plan);
      setWeeklyTable(result.weekly_table);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentWeekData = (): WeeklyTable | null => {
    if (!weeklyTable) return null;
    const key = `month_${selectedMonth}_week_${selectedWeek}`;
    return weeklyTable[key] || null;
  };

  if (loading) {
    return (
      <div className="workout-plan-loading">
        <p>{i18n.language === 'fa' ? 'در حال تولید برنامه...' : 'Generating plan...'}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workout-plan-error">
        <p>{error}</p>
        <button onClick={loadWorkoutPlan}>
          {i18n.language === 'fa' ? 'تلاش مجدد' : 'Retry'}
        </button>
      </div>
    );
  }

  if (!plan || !weeklyTable) {
    return null;
  }

  const weekData = getCurrentWeekData();
  const monthData = plan.months[`month_${selectedMonth}`];

  return (
    <div className="workout-plan-viewer">
      <div className="plan-header">
        <h2>{i18n.language === 'fa' ? 'برنامه ۶ ماهه تمرین' : '6-Month Workout Plan'}</h2>
        <div className="view-controls">
          <button
            className={viewMode === 'table' ? 'active' : ''}
            onClick={() => setViewMode('table')}
          >
            {i18n.language === 'fa' ? 'نمایش جدولی' : 'Table View'}
          </button>
          <button
            className={viewMode === 'plan' ? 'active' : ''}
            onClick={() => setViewMode('plan')}
          >
            {i18n.language === 'fa' ? 'نمایش برنامه' : 'Plan View'}
          </button>
        </div>
      </div>

      <div className="month-selector">
        {[1, 2, 3, 4, 5, 6].map(month => {
          const monthInfo = plan.months[`month_${month}`];
          return (
            <button
              key={month}
              className={selectedMonth === month ? 'active' : ''}
              onClick={() => {
                setSelectedMonth(month);
                setSelectedWeek(1);
              }}
            >
              {i18n.language === 'fa' ? `ماه ${month}` : `Month ${month}`}
              <br />
              <small>{i18n.language === 'fa' ? monthInfo.month_name_fa : monthInfo.month_name_en}</small>
            </button>
          );
        })}
      </div>

      <div className="week-selector">
        {[1, 2, 3, 4].map(week => (
          <button
            key={week}
            className={selectedWeek === week ? 'active' : ''}
            onClick={() => setSelectedWeek(week)}
          >
            {i18n.language === 'fa' ? `هفته ${week}` : `Week ${week}`}
          </button>
        ))}
      </div>

      {viewMode === 'table' && weekData && (
        <div className="weekly-table-view">
          <h3>
            {i18n.language === 'fa' 
              ? `ماه ${selectedMonth} - هفته ${selectedWeek}: ${weekData.month_focus_fa}`
              : `Month ${selectedMonth} - Week ${selectedWeek}: ${weekData.month_focus_en}`}
          </h3>
          
          <table className="workout-table">
            <thead>
              <tr>
                <th>{i18n.language === 'fa' ? 'روز' : 'Day'}</th>
                <th>{i18n.language === 'fa' ? 'نوع تمرین' : 'Workout Type'}</th>
                <th>{i18n.language === 'fa' ? 'تمرین' : 'Exercise'}</th>
                <th>{i18n.language === 'fa' ? 'عضله هدف' : 'Target Muscle'}</th>
                <th>{i18n.language === 'fa' ? 'ست' : 'Sets'}</th>
                <th>{i18n.language === 'fa' ? 'تکرار' : 'Reps'}</th>
                <th>{i18n.language === 'fa' ? 'استراحت (ثانیه)' : 'Rest (sec)'}</th>
                <th>{i18n.language === 'fa' ? 'نکات تنفس' : 'Breathing'}</th>
                <th>{i18n.language === 'fa' ? 'نکات فرم' : 'Form Tips'}</th>
              </tr>
            </thead>
            <tbody>
              {weekData.workouts.map((workout, workoutIdx) => (
                <React.Fragment key={workoutIdx}>
                  {workout.exercises.map((exercise, exIdx) => (
                    <tr key={exIdx}>
                      {exIdx === 0 && (
                        <td rowSpan={workout.exercises.length}>
                          {i18n.language === 'fa' ? `روز ${workout.day}` : `Day ${workout.day}`}
                        </td>
                      )}
                      {exIdx === 0 && (
                        <td rowSpan={workout.exercises.length}>
                          {workout.workout_type_fa}
                        </td>
                      )}
                      <td>{exercise.exercise_name_fa}</td>
                      <td>{exercise.target_muscle_fa}</td>
                      <td>{exercise.sets}</td>
                      <td>{exercise.reps}</td>
                      <td>{exercise.rest_seconds}</td>
                      <td className="breathing-note">{exercise.breathing_note_fa}</td>
                      <td className="form-tips">{exercise.form_tips_fa}</td>
                    </tr>
                  ))}
                  {workout.supersets && workout.supersets.map((superset, ssIdx) => (
                    <tr key={`superset-${ssIdx}`} className="superset-row">
                      <td colSpan={2}>
                        <strong>{i18n.language === 'fa' ? 'سوپرست:' : 'Superset:'}</strong>
                      </td>
                      {superset.map((ex, exIdx) => (
                        <React.Fragment key={exIdx}>
                          <td>{ex.exercise_name_fa}</td>
                          <td>-</td>
                          <td>{ex.sets}</td>
                          <td>{ex.reps}</td>
                          <td>-</td>
                          <td className="breathing-note">{ex.breathing_note_fa}</td>
                          <td>-</td>
                        </React.Fragment>
                      ))}
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {viewMode === 'plan' && monthData && (
        <div className="plan-view">
          <h3>
            {i18n.language === 'fa' 
              ? `ماه ${selectedMonth}: ${monthData.month_name_fa}`
              : `Month ${selectedMonth}: ${monthData.month_name_en}`}
          </h3>
          
          {Object.values(monthData.weeks).map((week, weekIdx) => (
            <div key={weekIdx} className="week-plan">
              <h4>
                {i18n.language === 'fa' ? `هفته ${week.week_number}` : `Week ${week.week_number}`}
              </h4>
              
              {Object.values(week.days).map((day, dayIdx) => (
                <div key={dayIdx} className="day-workout">
                  <h5>
                    {i18n.language === 'fa' ? `روز ${day.day}` : `Day ${day.day}`}
                  </h5>
                  
                  <div className="exercises-list">
                    {day.exercises.map((exercise, exIdx) => (
                      <div key={exIdx} className="exercise-card">
                        <h6>{exercise.name_fa}</h6>
                        <div className="exercise-details">
                          <span>{exercise.sets} {i18n.language === 'fa' ? 'ست' : 'sets'}</span>
                          <span>{exercise.reps} {i18n.language === 'fa' ? 'تکرار' : 'reps'}</span>
                          <span>{exercise.rest_seconds}s {i18n.language === 'fa' ? 'استراحت' : 'rest'}</span>
                        </div>
                        <p className="breathing">{exercise.breathing_note_fa}</p>
                        <p className="form-tips">{exercise.form_tips_fa}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkoutPlanViewer;



