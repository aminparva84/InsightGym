-- Supabase pgvector setup for Raha Fitness
-- Run this in Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create exercises_embeddings table
CREATE TABLE IF NOT EXISTS exercises_embeddings (
    id BIGSERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    language VARCHAR(10) NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(exercise_id, language)
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS exercises_embeddings_embedding_idx 
ON exercises_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for metadata filtering
CREATE INDEX IF NOT EXISTS exercises_embeddings_metadata_idx 
ON exercises_embeddings 
USING gin (metadata);

-- Create index for exercise_id lookups
CREATE INDEX IF NOT EXISTS exercises_embeddings_exercise_id_idx 
ON exercises_embeddings (exercise_id);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_exercises(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 20,
    language_filter text DEFAULT NULL
)
RETURNS TABLE (
    exercise_id integer,
    language text,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.exercise_id,
        e.language,
        1 - (e.embedding <=> query_embedding) as similarity,
        e.metadata
    FROM exercises_embeddings e
    WHERE 
        (language_filter IS NULL OR e.language = language_filter)
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create function to filter by metadata
CREATE OR REPLACE FUNCTION filter_exercises_by_metadata(
    query_embedding vector(1536),
    equipment_filter text DEFAULT NULL,
    level_filter text DEFAULT NULL,
    intensity_filter text DEFAULT NULL,
    exclude_injuries text[] DEFAULT NULL,
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 20,
    language_filter text DEFAULT 'fa'
)
RETURNS TABLE (
    exercise_id integer,
    language text,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.exercise_id,
        e.language,
        1 - (e.embedding <=> query_embedding) as similarity,
        e.metadata
    FROM exercises_embeddings e
    WHERE 
        (language_filter IS NULL OR e.language = language_filter)
        AND (equipment_filter IS NULL OR e.metadata->>'equipment' = equipment_filter)
        AND (level_filter IS NULL OR e.metadata->>'level' = level_filter)
        AND (intensity_filter IS NULL OR e.metadata->>'intensity' = intensity_filter)
        AND (
            exclude_injuries IS NULL OR 
            NOT EXISTS (
                SELECT 1 
                FROM jsonb_array_elements_text(e.metadata->'injury_tags') AS tag
                WHERE tag = ANY(exclude_injuries)
            )
        )
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON exercises_embeddings TO authenticated;
-- GRANT EXECUTE ON FUNCTION match_exercises TO authenticated;
-- GRANT EXECUTE ON FUNCTION filter_exercises_by_metadata TO authenticated;



