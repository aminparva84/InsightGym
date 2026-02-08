/**
 * Workout Log Service - Client-side service for logging workouts and tracking progress
 */

import axios from 'axios';
import { getApiBase } from './apiBase';

const BASE_URL = `${getApiBase()}/api/workout-log`;

export interface WorkoutLogEntry {
  id?: number;
  exercise_id: number;
  sets_completed: number;
  reps_completed: number;
  weight_kg?: number;
  duration_minutes?: number;
  distance_km?: number;
  difficulty_rating?: 'too_easy' | 'just_right' | 'too_difficult';
  pain_reported?: boolean;
  pain_location?: string;
  form_rating?: number; // 1-5
  notes?: string;
  language?: 'fa' | 'en';
}

export interface AlternativeExercise {
  id: number;
  name_fa: string;
  name_en: string;
  target_muscle_fa: string;
  target_muscle_en: string;
  intensity: string;
  level: string;
  reason_fa: string;
  reason_en: string;
}

export interface WorkoutLogResponse {
  workout_log_id: number;
  exercise_name_fa: string;
  exercise_name_en: string;
  sets_completed: number;
  reps_completed: number;
  alternative_suggested: boolean;
  alternative_exercise?: AlternativeExercise;
}

export interface ProgressEntry {
  weight_kg?: number;
  chest_cm?: number;
  waist_cm?: number;
  hips_cm?: number;
  arm_left_cm?: number;
  arm_right_cm?: number;
  thigh_left_cm?: number;
  thigh_right_cm?: number;
  form_level?: number; // 1-5
  form_notes_fa?: string;
  form_notes_en?: string;
  body_fat_percentage?: number;
  muscle_mass_kg?: number;
}

export interface WeeklyGoal {
  id?: number;
  week_start_date: string;
  workout_days_target: number;
  workout_days_completed?: number;
  exercise_goals?: Array<{
    exercise_id: number;
    sets: number;
    reps: number;
  }>;
  target_weight_kg?: number;
  target_measurements?: {
    [key: string]: number;
  };
  notes_fa?: string;
  notes_en?: string;
}

export interface WorkoutReminder {
  id?: number;
  reminder_time: string; // HH:MM format
  days_of_week: number[]; // 0=Monday, 6=Sunday
  enabled: boolean;
  message_fa?: string;
  message_en?: string;
  timezone?: string;
}

class WorkoutLogService {
  private getAuthHeaders() {
    return {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    };
  }

  /**
   * Log a completed workout with feedback
   */
  async logWorkout(entry: WorkoutLogEntry): Promise<WorkoutLogResponse> {
    try {
      const response = await axios.post(
        `${BASE_URL}/log`,
        entry,
        { headers: this.getAuthHeaders() }
      );
      return response.data.workout_log;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to log workout');
    }
  }

  /**
   * Get workout history
   */
  async getWorkoutHistory(params?: {
    start_date?: string;
    end_date?: string;
    exercise_id?: number;
    limit?: number;
  }) {
    try {
      const response = await axios.get(`${BASE_URL}/history`, {
        params,
        headers: this.getAuthHeaders()
      });
      return response.data.workout_logs;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch workout history');
    }
  }

  /**
   * Log progress entry
   */
  async logProgress(entry: ProgressEntry): Promise<{ success: boolean; progress_entry_id: number }> {
    try {
      const response = await axios.post(
        `${BASE_URL}/progress`,
        entry,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to log progress');
    }
  }

  /**
   * Get progress history
   */
  async getProgress(limit: number = 30) {
    try {
      const response = await axios.get(`${BASE_URL}/progress`, {
        params: { limit },
        headers: this.getAuthHeaders()
      });
      return response.data.progress_entries;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch progress');
    }
  }

  /**
   * Create weekly goal
   */
  async createWeeklyGoal(goal: WeeklyGoal): Promise<{ success: boolean; goal_id: number }> {
    try {
      const response = await axios.post(
        `${BASE_URL}/goals`,
        goal,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to create weekly goal');
    }
  }

  /**
   * Get weekly goals
   */
  async getWeeklyGoals(status?: 'active' | 'completed' | 'failed') {
    try {
      const response = await axios.get(`${BASE_URL}/goals`, {
        params: status ? { status } : {},
        headers: this.getAuthHeaders()
      });
      return response.data.goals;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch weekly goals');
    }
  }

  /**
   * Update weekly goal progress
   */
  async updateWeeklyGoal(goalId: number, workoutDaysCompleted: number) {
    try {
      const response = await axios.put(
        `${BASE_URL}/goals/${goalId}/update`,
        { workout_days_completed: workoutDaysCompleted },
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to update weekly goal');
    }
  }

  /**
   * Create workout reminder
   */
  async createReminder(reminder: WorkoutReminder): Promise<{ success: boolean; reminder_id: number }> {
    try {
      const response = await axios.post(
        `${BASE_URL}/reminders`,
        reminder,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to create reminder');
    }
  }

  /**
   * Get workout reminders
   */
  async getReminders() {
    try {
      const response = await axios.get(`${BASE_URL}/reminders`, {
        headers: this.getAuthHeaders()
      });
      return response.data.reminders;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch reminders');
    }
  }
}

export const workoutLogService = new WorkoutLogService();
export default WorkoutLogService;



