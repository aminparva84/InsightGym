/**
 * Vector Search Service for Raha Fitness
 * Supports semantic search in Persian and English with filtering
 */

import { Pinecone } from '@pinecone-database/pinecone';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Types
export interface ExerciseMetadata {
  muscle: string;
  muscle_fa: string;
  level: string;
  equipment: 'machine' | 'home' | 'hybrid';
  equipment_needed: string;
  equipment_needed_fa: string;
  injury_tags: string[];
  category: string;
  intensity: string;
  gender_suitability: string;
  exercise_id: number;
  name_fa: string;
  name_en: string;
}

export interface UserProfile {
  gym_access: boolean;
  equipment_access: string[];
  injuries: string[];
  training_level?: string;
  preferred_intensity?: string;
}

export interface SearchFilters {
  userProfile: UserProfile;
  level?: string;
  intensity?: string;
  targetMuscle?: string;
  maxResults?: number;
  language?: 'fa' | 'en';
}

export interface SearchResult {
  exercise_id: number;
  name_fa: string;
  name_en: string;
  score: number;
  metadata: ExerciseMetadata;
}

// Vector Database Provider
export type VectorDBProvider = 'pinecone' | 'supabase';

class VectorSearchService {
  private provider: VectorDBProvider;
  private pineconeIndex: any = null;
  private supabaseClient: SupabaseClient | null = null;
  private openaiApiKey: string;

  constructor(provider: VectorDBProvider = 'pinecone') {
    this.provider = provider;
    this.openaiApiKey = process.env.REACT_APP_OPENAI_API_KEY || '';
    this.initialize();
  }

  private async initialize() {
    if (this.provider === 'pinecone') {
      await this.initializePinecone();
    } else if (this.provider === 'supabase') {
      this.initializeSupabase();
    }
  }

  private async initializePinecone() {
    try {
      const apiKey = process.env.REACT_APP_PINECONE_API_KEY || '';
      const indexName = process.env.REACT_APP_PINECONE_INDEX_NAME || 'raha-fitness-exercises';
      
      const pinecone = new Pinecone({ apiKey });
      this.pineconeIndex = pinecone.index(indexName);
    } catch (error) {
      console.error('Error initializing Pinecone:', error);
    }
  }

  private initializeSupabase() {
    try {
      const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || '';
      const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY || '';
      
      this.supabaseClient = createClient(supabaseUrl, supabaseKey);
    } catch (error) {
      console.error('Error initializing Supabase:', error);
    }
  }

  /**
   * Generate embedding for search query
   */
  private async generateEmbedding(text: string): Promise<number[]> {
    try {
      const response = await fetch('https://api.openai.com/v1/embeddings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.openaiApiKey}`
        },
        body: JSON.stringify({
          model: 'text-embedding-3-small',
          input: text,
          dimensions: 1536
        })
      });

      const data = await response.json();
      return data.data[0].embedding;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw error;
    }
  }

  /**
   * Filter exercises based on user equipment access
   */
  private filterByEquipment(
    exercises: SearchResult[],
    userProfile: UserProfile
  ): SearchResult[] {
    return exercises.filter(exercise => {
      const { equipment, equipment_needed } = exercise.metadata;
      
      // If user has gym access, show all exercises
      if (userProfile.gym_access) {
        return true;
      }
      
      // If no gym access, only show home exercises
      if (equipment === 'home') {
        return true;
      }
      
      // Check if user has required equipment
      if (equipment_needed && userProfile.equipment_access) {
        const needed = equipment_needed.toLowerCase();
        return userProfile.equipment_access.some(
          eq => needed.includes(eq.toLowerCase())
        );
      }
      
      return false;
    });
  }

  /**
   * Filter out exercises that match user's injuries
   */
  private filterByInjuries(
    exercises: SearchResult[],
    userProfile: UserProfile
  ): SearchResult[] {
    if (!userProfile.injuries || userProfile.injuries.length === 0) {
      return exercises;
    }

    return exercises.filter(exercise => {
      const injuryTags = exercise.metadata.injury_tags || [];
      
      // Strict exclusion: if any injury tag matches user's injuries, exclude
      const hasMatchingInjury = userProfile.injuries.some(userInjury => {
        const userInjuryLower = userInjury.toLowerCase();
        return injuryTags.some(tag => 
          tag.toLowerCase().includes(userInjuryLower) ||
          userInjuryLower.includes(tag.toLowerCase())
        );
      });
      
      return !hasMatchingInjury;
    });
  }

  /**
   * Apply additional filters (level, intensity, muscle)
   */
  private applyAdditionalFilters(
    exercises: SearchResult[],
    filters: SearchFilters
  ): SearchResult[] {
    let filtered = exercises;

    // Filter by level
    if (filters.level) {
      filtered = filtered.filter(
        ex => ex.metadata.level === filters.level
      );
    }

    // Filter by intensity
    if (filters.intensity) {
      filtered = filtered.filter(
        ex => ex.metadata.intensity === filters.intensity
      );
    }

    // Filter by target muscle
    if (filters.targetMuscle) {
      const targetLower = filters.targetMuscle.toLowerCase();
      filtered = filtered.filter(ex => {
        const muscle = ex.metadata.muscle.toLowerCase();
        const muscleFa = ex.metadata.muscle_fa.toLowerCase();
        return muscle.includes(targetLower) || muscleFa.includes(targetLower);
      });
    }

    return filtered;
  }

  /**
   * Search exercises using Pinecone
   */
  private async searchPinecone(
    query: string,
    filters: SearchFilters,
    topK: number = 50
  ): Promise<SearchResult[]> {
    if (!this.pineconeIndex) {
      throw new Error('Pinecone not initialized');
    }

    // Generate embedding for query
    const queryEmbedding = await this.generateEmbedding(query);

    // Build filter object for Pinecone
    const pineconeFilter: any = {};

    // Filter by equipment if user doesn't have gym access
    if (!filters.userProfile.gym_access) {
      pineconeFilter.equipment = 'home';
    }

    // Filter by level
    if (filters.level) {
      pineconeFilter.level = filters.level;
    }

    // Filter by intensity
    if (filters.intensity) {
      pineconeFilter.intensity = filters.intensity;
    }

    // Search
    const searchResponse = await this.pineconeIndex.query({
      vector: queryEmbedding,
      topK: topK * 2, // Get more results to filter
      includeMetadata: true,
      filter: Object.keys(pineconeFilter).length > 0 ? pineconeFilter : undefined
    });

    // Transform results
    const results: SearchResult[] = searchResponse.matches.map((match: any) => ({
      exercise_id: match.metadata.exercise_id,
      name_fa: match.metadata.name_fa,
      name_en: match.metadata.name_en,
      score: match.score,
      metadata: match.metadata as ExerciseMetadata
    }));

    return results;
  }

  /**
   * Search exercises using Supabase pgvector
   */
  private async searchSupabase(
    query: string,
    filters: SearchFilters,
    topK: number = 50
  ): Promise<SearchResult[]> {
    if (!this.supabaseClient) {
      throw new Error('Supabase not initialized');
    }

    // Generate embedding for query
    const queryEmbedding = await this.generateEmbedding(query);

    const language = filters.language || 'fa';

    // Build query
    let queryBuilder = this.supabaseClient
      .rpc('match_exercises', {
        query_embedding: queryEmbedding,
        match_threshold: 0.7,
        match_count: topK * 2,
        language_filter: language
      });

    // Apply metadata filters
    if (!filters.userProfile.gym_access) {
      queryBuilder = queryBuilder.eq('metadata->>equipment', 'home');
    }

    if (filters.level) {
      queryBuilder = queryBuilder.eq('metadata->>level', filters.level);
    }

    if (filters.intensity) {
      queryBuilder = queryBuilder.eq('metadata->>intensity', filters.intensity);
    }

    const { data, error } = await queryBuilder;

    if (error) {
      throw error;
    }

    // Transform results
    const results: SearchResult[] = (data || []).map((item: any) => ({
      exercise_id: item.exercise_id,
      name_fa: item.metadata.name_fa,
      name_en: item.metadata.name_en,
      score: item.similarity,
      metadata: item.metadata as ExerciseMetadata
    }));

    return results;
  }

  /**
   * Main search function with all filters applied
   */
  async search(
    query: string,
    filters: SearchFilters
  ): Promise<SearchResult[]> {
    const maxResults = filters.maxResults || 20;
    const topK = maxResults * 3; // Get more results to filter

    // Perform vector search
    let results: SearchResult[];
    
    if (this.provider === 'pinecone') {
      results = await this.searchPinecone(query, filters, topK);
    } else {
      results = await this.searchSupabase(query, filters, topK);
    }

    // Apply equipment filter
    results = this.filterByEquipment(results, filters.userProfile);

    // Apply injury filter (strict exclusion)
    results = this.filterByInjuries(results, filters.userProfile);

    // Apply additional filters
    results = this.applyAdditionalFilters(results, filters);

    // Sort by score and limit results
    results = results
      .sort((a, b) => b.score - a.score)
      .slice(0, maxResults);

    return results;
  }

  /**
   * Search exercises by user query in Persian or English
   */
  async searchExercises(
    query: string,
    userProfile: UserProfile,
    options: {
      level?: string;
      intensity?: string;
      targetMuscle?: string;
      maxResults?: number;
      language?: 'fa' | 'en';
    } = {}
  ): Promise<SearchResult[]> {
    const filters: SearchFilters = {
      userProfile,
      ...options
    };

    return this.search(query, filters);
  }
}

// Export singleton instance
export const vectorSearchService = new VectorSearchService(
  (process.env.REACT_APP_VECTOR_DB_PROVIDER as VectorDBProvider) || 'pinecone'
);

// Export class for custom instances
export default VectorSearchService;



