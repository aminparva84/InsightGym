/**
 * Helper functions for vector search integration
 */

import { vectorSearchService, UserProfile, SearchResult } from './vectorSearch';

/**
 * Map user profile from API to vector search format
 */
export function mapUserProfileToSearchProfile(
  apiUserProfile: any
): UserProfile {
  // Parse JSON fields if they're strings
  const equipmentAccess = typeof apiUserProfile.equipment_access === 'string'
    ? JSON.parse(apiUserProfile.equipment_access)
    : apiUserProfile.equipment_access || [];

  const injuries = typeof apiUserProfile.injuries === 'string'
    ? JSON.parse(apiUserProfile.injuries)
    : apiUserProfile.injuries || [];

  return {
    gym_access: apiUserProfile.gym_access || false,
    equipment_access: equipmentAccess,
    injuries: injuries,
    training_level: apiUserProfile.training_level,
    preferred_intensity: apiUserProfile.preferred_intensity
  };
}

/**
 * Search exercises with automatic user profile fetching
 */
export async function searchExercisesWithProfile(
  query: string,
  userId: number,
  options: {
    level?: string;
    intensity?: string;
    targetMuscle?: string;
    maxResults?: number;
    language?: 'fa' | 'en';
  } = {}
): Promise<SearchResult[]> {
  try {
    // Fetch user profile from API
    const response = await fetch(`http://localhost:5000/api/user/profile`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user profile');
    }

    const apiProfile = await response.json();
    const userProfile = mapUserProfileToSearchProfile(apiProfile);

    // Perform search
    return await vectorSearchService.searchExercises(query, userProfile, options);
  } catch (error) {
    console.error('Error searching exercises:', error);
    throw error;
  }
}

/**
 * Get safe exercises for user (filtered by injuries and equipment)
 */
export async function getSafeExercisesForUser(
  userId: number,
  options: {
    category?: string;
    level?: string;
    intensity?: string;
    maxResults?: number;
    language?: 'fa' | 'en';
  } = {}
): Promise<SearchResult[]> {
  // Use a broad query to get all exercises, then filter
  const query = options.language === 'en' 
    ? 'fitness exercises workout training'
    : 'تمرینات ورزشی تناسب اندام';

  return searchExercisesWithProfile(query, userId, {
    level: options.level,
    intensity: options.intensity,
    maxResults: options.maxResults || 50,
    language: options.language
  });
}

/**
 * Search exercises by target muscle
 */
export async function searchExercisesByMuscle(
  muscleQuery: string,
  userId: number,
  options: {
    level?: string;
    intensity?: string;
    maxResults?: number;
    language?: 'fa' | 'en';
  } = {}
): Promise<SearchResult[]> {
  return searchExercisesWithProfile(muscleQuery, userId, {
    targetMuscle: muscleQuery,
    ...options
  });
}

/**
 * Get exercise recommendations based on user profile
 */
export async function getExerciseRecommendations(
  userId: number,
  options: {
    level?: string;
    intensity?: string;
    maxResults?: number;
    language?: 'fa' | 'en';
  } = {}
): Promise<SearchResult[]> {
  // Fetch user profile to determine query
  const response = await fetch(`http://localhost:5000/api/user/profile`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }

  const apiProfile = await response.json();
  const userProfile = mapUserProfileToSearchProfile(apiProfile);

  // Build query based on user's training level and goals
  const fitnessGoals = typeof apiProfile.fitness_goals === 'string'
    ? JSON.parse(apiProfile.fitness_goals)
    : apiProfile.fitness_goals || [];

  let query = '';
  if (options.language === 'en') {
    if (fitnessGoals.includes('weight_loss')) {
      query = 'cardio exercises for weight loss';
    } else if (fitnessGoals.includes('muscle_gain')) {
      query = 'strength training muscle building exercises';
    } else {
      query = 'fitness exercises workout';
    }
  } else {
    if (fitnessGoals.includes('weight_loss')) {
      query = 'تمرینات کاردیو برای کاهش وزن';
    } else if (fitnessGoals.includes('muscle_gain')) {
      query = 'تمرینات قدرتی برای عضله سازی';
    } else {
      query = 'تمرینات تناسب اندام';
    }
  }

  return searchExercisesWithProfile(query, userId, {
    level: options.level || userProfile.training_level,
    intensity: options.intensity || userProfile.preferred_intensity,
    maxResults: options.maxResults || 20,
    language: options.language
  });
}



