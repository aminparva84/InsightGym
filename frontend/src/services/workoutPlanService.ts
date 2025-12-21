/**
 * Workout Plan Service - Client-side service for workout plan generation
 */

import axios from 'axios';

export interface ExerciseWorkout {
  exercise_id: number;
  name_fa: string;
  name_en: string;
  target_muscle_fa: string;
  target_muscle_en: string;
  sets: number;
  reps: number;
  rest_seconds: number;
  breathing_note_fa: string;
  breathing_note_en: string;
  form_tips_fa: string;
  form_tips_en: string;
  intensity: string;
  category: string;
}

export interface DayWorkout {
  day: number;
  month: number;
  week: number;
  workout_type_fa: string;
  workout_type_en: string;
  exercises: ExerciseWorkout[];
  supersets?: ExerciseWorkout[][];
  total_duration_minutes: number;
  focus_fa: string;
  focus_en: string;
}

export interface WeekPlan {
  week_number: number;
  days: { [key: string]: DayWorkout };
}

export interface MonthPlan {
  month_number: number;
  month_name_fa: string;
  month_name_en: string;
  focus_fa: string;
  focus_en: string;
  weeks: { [key: string]: WeekPlan };
}

export interface WorkoutPlan {
  user_id: number;
  generated_at: string;
  language: string;
  total_duration_months: number;
  workout_days_per_week: number;
  months: { [key: string]: MonthPlan };
}

export interface WeeklyTable {
  month: number;
  week: number;
  month_focus_fa: string;
  month_focus_en: string;
  workouts: {
    day: number;
    workout_type_fa: string;
    workout_type_en: string;
    exercises: {
      exercise_name_fa: string;
      exercise_name_en: string;
      target_muscle_fa: string;
      sets: number;
      reps: number;
      rest_seconds: number;
      breathing_note_fa: string;
      form_tips_fa: string;
    }[];
    supersets?: {
      exercise_name_fa: string;
      sets: number;
      reps: number;
      breathing_note_fa: string;
    }[][];
  }[];
}

class WorkoutPlanService {
  private baseURL = 'http://localhost:5000/api/workout-plan';

  /**
   * Generate complete 6-month workout plan
   */
  async generate6MonthPlan(language: 'fa' | 'en' = 'fa'): Promise<{
    plan: WorkoutPlan;
    weekly_table: { [key: string]: WeeklyTable };
  }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/generate`,
        { language },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.error || 'Failed to generate workout plan'
      );
    }
  }

  /**
   * Generate workout plan for a specific month
   */
  async generateMonthPlan(
    month: number,
    language: 'fa' | 'en' = 'fa'
  ): Promise<MonthPlan> {
    if (month < 1 || month > 6) {
      throw new Error('Month must be between 1 and 6');
    }

    try {
      const response = await axios.post(
        `${this.baseURL}/generate-month`,
        { month, language },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data.month_plan;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.error || 'Failed to generate month plan'
      );
    }
  }

  /**
   * Get monthly progression rules
   */
  async getProgressionRules(): Promise<{
    [key: number]: {
      name_fa: string;
      name_en: string;
      focus: string[];
      sets_range: [number, number];
      reps_range: [number, number];
      rest_seconds: number;
      intensity: string;
    };
  }> {
    try {
      const response = await axios.get(`${this.baseURL}/rules`);
      return response.data;
    } catch (error: any) {
      throw new Error('Failed to fetch progression rules');
    }
  }
}

export const workoutPlanService = new WorkoutPlanService();
export default WorkoutPlanService;

