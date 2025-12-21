"""
Batch script to generate embeddings for 200 exercises per category (600 total)
This script can be used to populate a larger exercise database
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
from app import app, db
from models import Exercise
from generate_embeddings import get_exercise_text, get_exercise_metadata, generate_embedding

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
EMBEDDING_DIMENSIONS = int(os.getenv('EMBEDDING_DIMENSIONS', '1536'))

def generate_embeddings_for_category(
    category: str,
    language: str = 'fa',
    limit: int = 200
):
    """Generate embeddings for exercises in a specific category"""
    exercises = Exercise.query.filter_by(category=category).limit(limit).all()
    total = len(exercises)
    
    print(f"\nGenerating embeddings for {total} exercises in category: {category} ({language})...")
    
    embeddings_data = []
    
    for i, exercise in enumerate(exercises, 1):
        print(f"  [{i}/{total}] {exercise.name_fa}")
        
        try:
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
        except Exception as e:
            print(f"    Error: {e}")
            continue
    
    return embeddings_data

def generate_all_embeddings(language: str = 'fa'):
    """Generate embeddings for all categories"""
    from models import (
        EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
        EXERCISE_CATEGORY_FUNCTIONAL_HOME,
        EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE
    )
    
    categories = [
        EXERCISE_CATEGORY_BODYBUILDING_MACHINE,
        EXERCISE_CATEGORY_FUNCTIONAL_HOME,
        EXERCISE_CATEGORY_HYBRID_HIIT_MACHINE
    ]
    
    all_embeddings = []
    
    for category in categories:
        embeddings = generate_embeddings_for_category(category, language, limit=200)
        all_embeddings.extend(embeddings)
        print(f"  ✓ Generated {len(embeddings)} embeddings for {category}")
    
    return all_embeddings

if __name__ == '__main__':
    import sys
    
    language = sys.argv[1] if len(sys.argv) > 1 else 'fa'
    output_file = sys.argv[2] if len(sys.argv) > 2 else f'embeddings_all_{language}.json'
    
    print(f"Starting batch embedding generation for language: {language}")
    print(f"Target: 200 exercises per category (600 total)")
    
    with app.app_context():
        all_embeddings = generate_all_embeddings(language=language)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_embeddings, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Completed!")
        print(f"  Total embeddings: {len(all_embeddings)}")
        print(f"  Saved to: {output_file}")
        print(f"\nNext steps:")
        print(f"  1. Upload to Pinecone: python vector_db_setup.py pinecone {output_file}")
        print(f"  2. Upload to Supabase: python vector_db_setup.py supabase {output_file}")

