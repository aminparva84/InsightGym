"""
API endpoints for vector search functionality
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import User, UserProfile, Exercise
import os
import openai
from typing import List, Dict, Any

vector_search_bp = Blueprint('vector_search', __name__, url_prefix='/api/vector-search')

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI"""
    try:
        response = openai.embeddings.create(
            model='text-embedding-3-small',
            input=text,
            dimensions=1536
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise

def get_user_profile_for_search(user_id: int) -> Dict[str, Any]:
    """Get user profile formatted for search"""
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)
    
    if not profile:
        return {
            'gym_access': False,
            'equipment_access': [],
            'injuries': [],
            'training_level': None,
            'preferred_intensity': None
        }
    
    # Parse JSON fields
    equipment_access = []
    if profile.equipment_access:
        try:
            import json
            equipment_access = json.loads(profile.equipment_access)
        except:
            equipment_access = []
    
    injuries = []
    if profile.injuries:
        try:
            import json
            injuries = json.loads(profile.injuries)
        except:
            injuries = []
    
    return {
        'gym_access': profile.gym_access or False,
        'equipment_access': equipment_access,
        'injuries': injuries,
        'training_level': profile.training_level,
        'preferred_intensity': profile.preferred_intensity
    }

@vector_search_bp.route('/search', methods=['POST'])
@jwt_required()
def search_exercises():
    """Search exercises using vector similarity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        query = data.get('query', '')
        language = data.get('language', 'fa')
        max_results = data.get('max_results', 20)
        level_filter = data.get('level')
        intensity_filter = data.get('intensity')
        target_muscle = data.get('target_muscle')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get user profile for filtering
        user_profile = get_user_profile_for_search(user_id)
        
        # Generate embedding for query
        query_embedding = generate_embedding(query)
        
        # TODO: Perform vector search using Pinecone or Supabase
        # For now, return a placeholder response
        # In production, integrate with your vector database
        
        return jsonify({
            'message': 'Vector search endpoint - integrate with Pinecone/Supabase',
            'query': query,
            'user_profile': user_profile,
            'embedding_dimension': len(query_embedding)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vector_search_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get exercise recommendations based on user profile"""
    try:
        user_id = get_jwt_identity()
        language = request.args.get('language', 'fa')
        max_results = int(request.args.get('max_results', 20))
        
        # Get user profile
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Build query based on user goals
        import json
        fitness_goals = []
        if profile.fitness_goals:
            try:
                fitness_goals = json.loads(profile.fitness_goals)
            except:
                pass
        
        # Generate query text
        if language == 'fa':
            if 'weight_loss' in fitness_goals:
                query = 'تمرینات کاردیو برای کاهش وزن'
            elif 'muscle_gain' in fitness_goals:
                query = 'تمرینات قدرتی برای عضله سازی'
            else:
                query = 'تمرینات تناسب اندام'
        else:
            if 'weight_loss' in fitness_goals:
                query = 'cardio exercises for weight loss'
            elif 'muscle_gain' in fitness_goals:
                query = 'strength training muscle building exercises'
            else:
                query = 'fitness exercises workout'
        
        # TODO: Perform vector search
        return jsonify({
            'message': 'Recommendations endpoint - integrate with vector search',
            'query': query,
            'user_profile': get_user_profile_for_search(user_id)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



