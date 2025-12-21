"""
Script to generate embeddings for exercises and store in vector database
Supports Pinecone and Supabase pgvector
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
from app import app, db
from models import Exercise, EXERCISE_CATEGORY_BODYBUILDING_MACHINE, EXERCISE_CATEGORY_FUNCTIONAL_HOME, EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')  # or 'text-embedding-3-large'
EMBEDDING_DIMENSIONS = int(os.getenv('EMBEDDING_DIMENSIONS', '1536'))

def get_exercise_text(exercise: Exercise, language: str = 'fa') -> str:
    """Generate searchable text from exercise for embedding"""
    if language == 'fa':
        text_parts = [
            exercise.name_fa,
            exercise.target_muscle_fa,
            exercise.execution_tips_fa or '',
            exercise.breathing_guide_fa or '',
            exercise.equipment_needed_fa or ''
        ]
    else:
        text_parts = [
            exercise.name_en,
            exercise.target_muscle_en,
            exercise.execution_tips_en or '',
            exercise.breathing_guide_en or '',
            exercise.equipment_needed_en or ''
        ]
    
    return ' '.join(filter(None, text_parts))

def get_exercise_metadata(exercise: Exercise) -> Dict[str, Any]:
    """Extract metadata from exercise for vector storage"""
    # Get injury contraindications
    injury_contraindications = []
    if hasattr(exercise, 'get_injury_contraindications'):
        injury_contraindications = exercise.get_injury_contraindications()
    elif exercise.injury_contraindications:
        if isinstance(exercise.injury_contraindications, str):
            try:
                injury_contraindications = json.loads(exercise.injury_contraindications)
            except:
                injury_contraindications = []
        elif isinstance(exercise.injury_contraindications, list):
            injury_contraindications = exercise.injury_contraindications
    
    # Determine equipment type from category
    equipment_type = 'machine'
    if exercise.category == EXERCISE_CATEGORY_FUNCTIONAL_HOME:
        equipment_type = 'home'
    elif exercise.category == EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE:
        equipment_type = 'hybrid'
    
    # Extract muscle groups for filtering
    muscle_groups = []
    if exercise.target_muscle_en:
        # Split by comma and clean
        muscle_groups = [m.strip().lower() for m in exercise.target_muscle_en.split(',')]
    
    return {
        'muscle': exercise.target_muscle_en,  # Use English for consistent filtering
        'muscle_fa': exercise.target_muscle_fa,
        'muscle_groups': muscle_groups,  # Array for easier filtering
        'level': exercise.level,
        'equipment': equipment_type,
        'equipment_needed': exercise.equipment_needed_en or '',
        'equipment_needed_fa': exercise.equipment_needed_fa or '',
        'injury_tags': injury_contraindications,  # Array of injury types
        'category': exercise.category,
        'intensity': exercise.intensity,
        'gender_suitability': exercise.gender_suitability,
        'exercise_id': exercise.id,
        'name_fa': exercise.name_fa,
        'name_en': exercise.name_en
    }

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI"""
    try:
        response = openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=EMBEDDING_DIMENSIONS
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise

def generate_exercise_embeddings(language: str = 'fa', batch_size: int = 100):
    """Generate embeddings for all exercises"""
    exercises = Exercise.query.all()
    total = len(exercises)
    
    print(f"Generating embeddings for {total} exercises in {language}...")
    
    embeddings_data = []
    
    for i, exercise in enumerate(exercises, 1):
        print(f"Processing exercise {i}/{total}: {exercise.name_fa}")
        
        # Generate text for embedding
        exercise_text = get_exercise_text(exercise, language)
        
        # Generate embedding
        embedding = generate_embedding(exercise_text)
        
        # Get metadata
        metadata = get_exercise_metadata(exercise)
        
        # Create vector data
        vector_id = f"exercise_{exercise.id}_{language}"
        embeddings_data.append({
            'id': vector_id,
            'values': embedding,
            'metadata': metadata
        })
        
        # Batch upload to Pinecone if needed
        if len(embeddings_data) >= batch_size:
            yield embeddings_data
            embeddings_data = []
    
    # Yield remaining
    if embeddings_data:
        yield embeddings_data
    
    print(f"Completed generating embeddings for {total} exercises")

def save_embeddings_to_file(embeddings_data: List[Dict], filename: str):
    """Save embeddings to JSON file for backup/verification"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(embeddings_data)} embeddings to {filename}")

if __name__ == '__main__':
    import sys
    
    language = sys.argv[1] if len(sys.argv) > 1 else 'fa'
    output_file = sys.argv[2] if len(sys.argv) > 2 else f'embeddings_{language}.json'
    
    with app.app_context():
        all_embeddings = []
        for batch in generate_exercise_embeddings(language=language):
            all_embeddings.extend(batch)
        
        save_embeddings_to_file(all_embeddings, output_file)
        print(f"\nTotal embeddings generated: {len(all_embeddings)}")
        print(f"Saved to: {output_file}")

