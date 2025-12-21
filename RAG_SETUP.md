# RAG System Setup Guide - Raha Fitness

## Overview

This guide explains how to set up the Retrieval-Augmented Generation (RAG) system for the fitness AI agent using vector databases (Pinecone or Supabase pgvector).

## Prerequisites

1. **OpenAI API Key** - For generating embeddings
2. **Vector Database** - Choose one:
   - Pinecone (cloud-based, managed)
   - Supabase pgvector (self-hosted or cloud)

## Setup Steps

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements-rag.txt

# Frontend (if using TypeScript directly)
cd frontend
npm install @pinecone-database/pinecone @supabase/supabase-js
```

### 2. Environment Variables

Create/update `.env` file:

```env
# OpenAI
OPENAI_API_KEY=your-openai-api-key
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Pinecone (if using)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=raha-fitness-exercises

# Supabase (if using)
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Frontend
REACT_APP_OPENAI_API_KEY=your-openai-api-key
REACT_APP_PINECONE_API_KEY=your-pinecone-api-key
REACT_APP_PINECONE_INDEX_NAME=raha-fitness-exercises
REACT_APP_SUPABASE_URL=your-supabase-url
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
REACT_APP_VECTOR_DB_PROVIDER=pinecone  # or 'supabase'
```

### 3. Generate Embeddings

```bash
cd backend

# Generate embeddings for Persian (Farsi)
python generate_embeddings.py fa embeddings_fa.json

# Generate embeddings for English
python generate_embeddings.py en embeddings_en.json
```

This will:
- Load all exercises from the database
- Generate embeddings using OpenAI
- Save to JSON files

### 4. Setup Vector Database

#### Option A: Pinecone

```bash
# Setup Pinecone index
python vector_db_setup.py pinecone

# Upload embeddings
python vector_db_setup.py pinecone embeddings_fa.json
```

#### Option B: Supabase pgvector

1. **Run SQL setup**:
   - Go to Supabase Dashboard → SQL Editor
   - Run `supabase_setup.sql`

2. **Upload embeddings**:
```bash
python vector_db_setup.py supabase embeddings_fa.json
```

### 5. Integrate with Backend

Update `app.py` to include vector search routes:

```python
from api.vector_search import vector_search_bp
app.register_blueprint(vector_search_bp)
```

### 6. Frontend Integration

The TypeScript search service is ready to use:

```typescript
import { searchExercisesWithProfile, getExerciseRecommendations } from './services/vectorSearchHelpers';

// Search exercises
const results = await searchExercisesWithProfile(
  'تمرینات سینه',  // Query in Persian
  userId,
  {
    level: 'intermediate',
    intensity: 'medium',
    maxResults: 20,
    language: 'fa'
  }
);

// Get recommendations
const recommendations = await getExerciseRecommendations(userId, {
  level: 'beginner',
  maxResults: 10
});
```

## How It Works

### 1. Embedding Generation

- Each exercise is converted to searchable text (name, target muscle, tips, etc.)
- OpenAI generates a 1536-dimensional vector embedding
- Metadata (muscle, level, equipment, injury tags) is stored with the vector

### 2. Search Process

1. **Query Embedding**: User's search query is converted to an embedding
2. **Vector Search**: Find similar exercises using cosine similarity
3. **Equipment Filter**: Filter by user's available equipment
4. **Injury Filter**: Strictly exclude exercises matching user's injuries
5. **Additional Filters**: Apply level, intensity, muscle filters
6. **Rank & Return**: Sort by similarity score and return top results

### 3. Filtering Logic

#### Equipment Filtering
- If user has `gym_access = true`: Show all exercises
- If `gym_access = false`: Only show `equipment = 'home'` exercises
- Check `equipment_access` array for specific equipment needs

#### Injury Filtering (Strict Exclusion)
- If exercise has injury tag matching user's injury → **EXCLUDE**
- Example: User has "knee" injury → Exclude "Squats", "Lunges", etc.

#### Semantic Search in Persian
- Embeddings work for both Persian and English
- Query can be in Persian: "تمرینات سینه" → Finds chest exercises
- Results maintain bilingual support

## Example Queries

### Persian Queries
```typescript
// Search for chest exercises
await searchExercisesWithProfile('تمرینات سینه', userId);

// Search for home exercises
await searchExercisesWithProfile('تمرینات بدون وسیله', userId);

// Search for weight loss exercises
await searchExercisesWithProfile('تمرینات کاهش وزن', userId);
```

### English Queries
```typescript
// Search for leg exercises
await searchExercisesWithProfile('leg exercises', userId, { language: 'en' });

// Search for cardio
await searchExercisesWithProfile('cardio workout', userId, { language: 'en' });
```

## Metadata Structure

Each vector includes metadata:

```json
{
  "muscle": "Chest, Shoulders, Triceps",
  "muscle_fa": "سینه، شانه، سه‌سر بازو",
  "level": "intermediate",
  "equipment": "machine",
  "equipment_needed": "Chest Press Machine",
  "equipment_needed_fa": "دستگاه پرس سینه",
  "injury_tags": ["shoulder", "lower_back"],
  "category": "bodybuilding_machine",
  "intensity": "medium",
  "gender_suitability": "both",
  "exercise_id": 1,
  "name_fa": "پرس سینه با دستگاه",
  "name_en": "Chest Press Machine"
}
```

## Performance Optimization

1. **Batch Processing**: Generate embeddings in batches
2. **Indexing**: Use proper indexes on metadata fields
3. **Caching**: Cache user profiles and common queries
4. **Filtering Order**: Apply strict filters (injuries) before semantic search when possible

## Troubleshooting

### Embedding Generation Fails
- Check OpenAI API key
- Verify API quota/limits
- Check network connection

### Vector Search Returns No Results
- Verify embeddings were uploaded
- Check filter criteria (might be too restrictive)
- Verify index exists and is accessible

### Persian Text Issues
- Ensure UTF-8 encoding throughout
- Verify database collation supports Persian
- Check embedding model supports multilingual text

## Next Steps

1. **Scale to 200 exercises per category** (600 total)
2. **Add more metadata fields** as needed
3. **Implement caching** for frequent queries
4. **Add query expansion** for better results
5. **Integrate with AI agent** for contextual recommendations

## Cost Estimation

- **OpenAI Embeddings**: ~$0.0001 per 1K tokens
- **Pinecone**: Free tier available, then ~$70/month for starter
- **Supabase**: Free tier available, then pay-as-you-go

For 600 exercises × 2 languages = 1200 embeddings:
- Generation cost: ~$0.50-1.00
- Storage: Minimal
- Query cost: ~$0.0001 per search

