"""
Song Recommender using SQLite Database
"""

from typing import List, Dict
from database_manager import db_manager
from database_models import Song
from sqlalchemy import and_, or_
from key_utils import get_nearby_keys, calculate_semitone_distance

class SongRecommenderSQLite:
    def __init__(self):
        self.db_manager = db_manager
        print("✅ SongRecommenderSQLite initialized (SQLite)")
    
    def recommend(self, vocal_analysis: dict, max_results: int = 10) -> List[Dict]:
        """
        Recommend songs based on vocal analysis
        
        Args:
            vocal_analysis: Dict from VocalAnalyzer
            max_results: Maximum number of recommendations
        
        Returns:
            List of recommended songs with compatibility scores
        """
        session = self.db_manager.get_session()
        
        try:
            # Extract detected key & confidence
            key_info = vocal_analysis.get('key', {})
            detected_key = key_info.get('key', 'C') if isinstance(key_info, dict) else 'C'
            confidence = key_info.get('confidence', 0.5) if isinstance(key_info, dict) else 0.5
            
            print(f"[Recommender] Detected key: {detected_key}, Confidence: {confidence}")
            
            # Get nearby keys (±1 semitone)
            try:
                matched_keys = get_nearby_keys(detected_key, semitone_range=1)
                print(f"[Recommender] Matched keys: {matched_keys}")
            except Exception as e:
                print(f"[Recommender ERROR] get_nearby_keys failed: {str(e)}")
                matched_keys = [detected_key]
            
            # Query database - FIXED: Remove confidence filter for debugging
            print(f"[Recommender] Querying database...")
            print(f"[Recommender] SQL Filter: key_note IN {matched_keys}")
            
            # Simple query without confidence filter first
            results = session.query(Song).filter(
                Song.key_note.in_(matched_keys)
            ).all()
            
            print(f"[Recommender] Found {len(results)} matches before sorting")
            
            if len(results) == 0:
                # Debug: Check what keys exist in database
                all_songs = session.query(Song).all()
                unique_keys = set([song.key_note for song in all_songs])
                print(f"[Recommender DEBUG] Available keys in database: {unique_keys}")
                print(f"[Recommender DEBUG] Looking for keys: {matched_keys}")
                print(f"[Recommender DEBUG] Total songs in DB: {len(all_songs)}")
                
                # Check if any key matches
                for key in matched_keys:
                    count = session.query(Song).filter(Song.key_note == key).count()
                    print(f"[Recommender DEBUG] Songs with key '{key}': {count}")
            
            # Calculate match scores
            recommendations = []
            for song in results:
                # Calculate semitone distance
                distance = calculate_semitone_distance(detected_key, song.key_note)
                
                # Calculate match score
                # - Perfect match (0 semitones): 100 points
                # - 1 semitone off: 80 points
                # - 2+ semitones: 50 points
                if distance == 0:
                    key_match_score = 1.0
                elif distance == 1:
                    key_match_score = 0.8
                else:
                    key_match_score = 0.5
                
                # Combine with confidence and popularity
                total_score = (
                    key_match_score * 0.6 +
                    confidence * 0.2 +
                    song.popularity_score * 0.2
                )
                
                recommendations.append({
                    'id': song.id,
                    'title': song.title,
                    'artist': song.artist,
                    'key_note': song.key_note,
                    'pitch_range_acc': song.pitch_range_acc,
                    'link_youtube': song.link_youtube,
                    'genre': song.genre,
                    'tempo': song.tempo,
                    'popularity_score': song.popularity_score,
                    'match_score': total_score,
                    'semitone_distance': distance
                })
            
            # Sort by match score (highest first)
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Limit results
            recommendations = recommendations[:max_results]
            
            print(f"[Recommender] Returning {len(recommendations)} recommendations")
            
            return recommendations
        
        except Exception as e:
            print(f"[Recommender ERROR] {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
        
        finally:
            session.close()
