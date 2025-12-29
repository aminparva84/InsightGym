/**
 * Example React component demonstrating vector search usage
 */

import React, { useState, useEffect } from 'react';
import { 
  searchExercisesWithProfile, 
  getExerciseRecommendations,
  getSafeExercisesForUser,
  searchExercisesByMuscle
} from '../services/vectorSearchHelpers';
import { SearchResult } from '../services/vectorSearch';

interface VectorSearchExampleProps {
  userId: number;
  language?: 'fa' | 'en';
}

const VectorSearchExample: React.FC<VectorSearchExampleProps> = ({ 
  userId, 
  language = 'fa' 
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchType, setSearchType] = useState<'search' | 'recommendations' | 'safe' | 'muscle'>('search');

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      let searchResults: SearchResult[];
      
      switch (searchType) {
        case 'search':
          searchResults = await searchExercisesWithProfile(query, userId, {
            language,
            maxResults: 20
          });
          break;
        case 'recommendations':
          searchResults = await getExerciseRecommendations(userId, {
            language,
            maxResults: 20
          });
          break;
        case 'safe':
          searchResults = await getSafeExercisesForUser(userId, {
            language,
            maxResults: 20
          });
          break;
        case 'muscle':
          searchResults = await searchExercisesByMuscle(query, userId, {
            language,
            maxResults: 20
          });
          break;
        default:
          searchResults = [];
      }
      
      setResults(searchResults);
    } catch (err: any) {
      setError(err.message || 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGetRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const recommendations = await getExerciseRecommendations(userId, {
        language,
        maxResults: 20
      });
      setResults(recommendations);
    } catch (err: any) {
      setError(err.message || 'Failed to get recommendations');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGetSafeExercises = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const safeExercises = await getSafeExercisesForUser(userId, {
        language,
        maxResults: 50
      });
      setResults(safeExercises);
    } catch (err: any) {
      setError(err.message || 'Failed to get safe exercises');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vector-search-example">
      <h2>{language === 'fa' ? 'جستجوی هوشمند تمرینات' : 'Smart Exercise Search'}</h2>
      
      {/* Search Type Selector */}
      <div className="search-type-selector">
        <button 
          className={searchType === 'search' ? 'active' : ''}
          onClick={() => setSearchType('search')}
        >
          {language === 'fa' ? 'جستجو' : 'Search'}
        </button>
        <button 
          className={searchType === 'recommendations' ? 'active' : ''}
          onClick={() => setSearchType('recommendations')}
        >
          {language === 'fa' ? 'پیشنهادات' : 'Recommendations'}
        </button>
        <button 
          className={searchType === 'safe' ? 'active' : ''}
          onClick={() => setSearchType('safe')}
        >
          {language === 'fa' ? 'تمرینات ایمن' : 'Safe Exercises'}
        </button>
        <button 
          className={searchType === 'muscle' ? 'active' : ''}
          onClick={() => setSearchType('muscle')}
        >
          {language === 'fa' ? 'بر اساس عضله' : 'By Muscle'}
        </button>
      </div>

      {/* Search Input */}
      {searchType !== 'recommendations' && searchType !== 'safe' && (
        <div className="search-input">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={language === 'fa' 
              ? 'جستجوی تمرینات... (مثال: تمرینات سینه)' 
              : 'Search exercises... (e.g., chest exercises)'}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading 
              ? (language === 'fa' ? 'در حال جستجو...' : 'Searching...')
              : (language === 'fa' ? 'جستجو' : 'Search')}
          </button>
        </div>
      )}

      {/* Quick Actions */}
      {searchType === 'recommendations' && (
        <button onClick={handleGetRecommendations} disabled={loading} className="action-btn">
          {loading 
            ? (language === 'fa' ? 'در حال بارگذاری...' : 'Loading...')
            : (language === 'fa' ? 'دریافت پیشنهادات' : 'Get Recommendations')}
        </button>
      )}

      {searchType === 'safe' && (
        <button onClick={handleGetSafeExercises} disabled={loading} className="action-btn">
          {loading 
            ? (language === 'fa' ? 'در حال بارگذاری...' : 'Loading...')
            : (language === 'fa' ? 'نمایش تمرینات ایمن' : 'Show Safe Exercises')}
        </button>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="search-results">
          <h3>
            {language === 'fa' 
              ? `نتایج (${results.length})` 
              : `Results (${results.length})`}
          </h3>
          <div className="results-list">
            {results.map((result, index) => (
              <div key={result.exercise_id} className="result-item">
                <div className="result-header">
                  <h4>{language === 'fa' ? result.name_fa : result.name_en}</h4>
                  <span className="similarity-score">
                    {Math.round(result.score * 100)}% {language === 'fa' ? 'شباهت' : 'similarity'}
                  </span>
                </div>
                <div className="result-metadata">
                  <span className="badge">{result.metadata.level}</span>
                  <span className="badge">{result.metadata.intensity}</span>
                  <span className="badge">{result.metadata.equipment}</span>
                  <span className="badge">
                    {language === 'fa' ? result.metadata.muscle_fa : result.metadata.muscle}
                  </span>
                </div>
                {result.metadata.injury_tags && result.metadata.injury_tags.length > 0 && (
                  <div className="injury-warning">
                    {language === 'fa' ? 'هشدار آسیب:' : 'Injury Warning:'} {result.metadata.injury_tags.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div className="no-results">
          {language === 'fa' 
            ? 'نتیجه‌ای یافت نشد' 
            : 'No results found'}
        </div>
      )}
    </div>
  );
};

export default VectorSearchExample;



