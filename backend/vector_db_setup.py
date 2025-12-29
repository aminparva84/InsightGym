"""
Setup script for vector database (Pinecone or Supabase pgvector)
"""

import os
from dotenv import load_dotenv
import json

load_dotenv()

# Pinecone setup
def setup_pinecone():
    """Setup Pinecone vector database"""
    try:
        import pinecone
        from pinecone import Pinecone, ServerlessSpec
        
        api_key = os.getenv('PINECONE_API_KEY')
        environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
        index_name = os.getenv('PINECONE_INDEX_NAME', 'raha-fitness-exercises')
        
        if not api_key:
            print("PINECONE_API_KEY not found in environment variables")
            return None
        
        pc = Pinecone(api_key=api_key)
        
        # Check if index exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"Creating Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI text-embedding-3-small dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=environment
                )
            )
            print(f"Index {index_name} created successfully")
        else:
            print(f"Index {index_name} already exists")
        
        return pc.Index(index_name)
    
    except ImportError:
        print("Pinecone not installed. Install with: pip install pinecone-client")
        return None
    except Exception as e:
        print(f"Error setting up Pinecone: {e}")
        return None

def upload_to_pinecone(embeddings_file: str):
    """Upload embeddings from JSON file to Pinecone"""
    index = setup_pinecone()
    if not index:
        return
    
    # Load embeddings
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        embeddings_data = json.load(f)
    
    print(f"Uploading {len(embeddings_data)} vectors to Pinecone...")
    
    # Upload in batches
    batch_size = 100
    for i in range(0, len(embeddings_data), batch_size):
        batch = embeddings_data[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i//batch_size + 1}/{(len(embeddings_data) + batch_size - 1)//batch_size}")
    
    print("Upload complete!")

# Supabase pgvector setup
def setup_supabase_pgvector():
    """Setup Supabase with pgvector extension"""
    try:
        from supabase import create_client, Client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
            return None
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Enable pgvector extension (run this in Supabase SQL editor)
        sql = """
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
            UNIQUE(exercise_id, language)
        );
        
        -- Create index for vector similarity search
        CREATE INDEX IF NOT EXISTS exercises_embeddings_embedding_idx 
        ON exercises_embeddings 
        USING ivfflat (embedding vector_cosine_ops);
        
        -- Create index for metadata filtering
        CREATE INDEX IF NOT EXISTS exercises_embeddings_metadata_idx 
        ON exercises_embeddings 
        USING gin (metadata);
        """
        
        print("Run the following SQL in Supabase SQL editor:")
        print(sql)
        
        return supabase
    
    except ImportError:
        print("Supabase not installed. Install with: pip install supabase")
        return None
    except Exception as e:
        print(f"Error setting up Supabase: {e}")
        return None

def upload_to_supabase(embeddings_file: str):
    """Upload embeddings to Supabase pgvector"""
    supabase = setup_supabase_pgvector()
    if not supabase:
        return
    
    # Load embeddings
    with open(embeddings_file, 'r', encoding='utf-8') as f:
        embeddings_data = json.load(f)
    
    print(f"Uploading {len(embeddings_data)} vectors to Supabase...")
    
    # Transform data for Supabase
    records = []
    for item in embeddings_data:
        # Extract exercise_id and language from vector_id
        parts = item['id'].split('_')
        exercise_id = int(parts[1])
        language = parts[2]
        
        records.append({
            'exercise_id': exercise_id,
            'language': language,
            'embedding': item['values'],
            'metadata': item['metadata']
        })
    
    # Upload in batches
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        supabase.table('exercises_embeddings').upsert(batch).execute()
        print(f"Uploaded batch {i//batch_size + 1}/{(len(records) + batch_size - 1)//batch_size}")
    
    print("Upload complete!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vector_db_setup.py <pinecone|supabase> [embeddings_file.json]")
        sys.exit(1)
    
    provider = sys.argv[1].lower()
    embeddings_file = sys.argv[2] if len(sys.argv) > 2 else 'embeddings_fa.json'
    
    if provider == 'pinecone':
        if os.path.exists(embeddings_file):
            upload_to_pinecone(embeddings_file)
        else:
            setup_pinecone()
    elif provider == 'supabase':
        if os.path.exists(embeddings_file):
            upload_to_supabase(embeddings_file)
        else:
            setup_supabase_pgvector()
    else:
        print("Invalid provider. Use 'pinecone' or 'supabase'")



