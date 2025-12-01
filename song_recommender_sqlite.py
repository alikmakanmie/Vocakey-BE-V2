import numpy as np
from typing import List, Dict, Optional
from database_manager import DatabaseManager

class SongRecommenderSQLite:
    """
    Song recommender using SQLite database
    (No SQLAlchemy, pure SQLite)
    """
    
    def __init__(self, db_path: str = "songs.db"):
        self.db_manager = DatabaseManager(db_path)
        print("✅ SongRecommenderSQLite initialized (SQLite)")
    
    def recommend(
        self,
        vocal_analysis: Dict,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Recommend songs based on vocal analysis
        
        Args:
            vocal_analysis: Dict containing key, pitch_range, etc.
            max_results: Maximum number of recommendations
        
        Returns:
            List of recommended songs with compatibility scores
        """
        try:
            # Extract key info
            key_info = vocal_analysis.get('key', {})
            
            if isinstance(key_info, dict):
                detected_key = key_info.get('key', 'C')
                confidence = key_info.get('confidence', 0.0)
            else:
                detected_key = 'C'
                confidence = 0.0
            
            print(f"[Recommender] Detected key: {detected_key}, Confidence: {confidence}")
            
            # Find compatible keys (same key + neighbors)
            matched_keys = self._get_compatible_keys(detected_key)
            print(f"[Recommender] Matched keys: {matched_keys}")
            
            # Query database
            print(f"[Recommender] Querying database...")
            songs = self.db_manager.get_songs_by_keys(matched_keys)
            
            print(f"[Recommender] SQL Filter: key_note IN {matched_keys}")
            print(f"[Recommender] Found {len(songs)} matches before sorting")
            
            if not songs:
                print("[Recommender] No songs found in database")
                return []
            
            # Calculate compatibility scores
            scored_songs = []
            for song in songs:
                score = self._calculate_compatibility(song, vocal_analysis)
                song['compatibility_score'] = score
                scored_songs.append(song)
            
            # Sort by total score
            scored_songs.sort(
                key=lambda x: x['compatibility_score'].get('total', 0),
                reverse=True
            )
            
            # Return top results
            results = scored_songs[:max_results]
            print(f"[Recommender] Returning {len(results)} recommendations")
            
            return results
            
        except Exception as e:
            print(f"[Recommender] Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def _get_compatible_keys(self, key: str) -> List[str]:
        """Get compatible keys including neighbors"""
        key_circle = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        try:
            idx = key_circle.index(key)
            # Return same key + neighbors (±1 semitone)
            compatible = [
                key_circle[(idx - 1) % 12],
                key_circle[idx],
                key_circle[(idx + 1) % 12]
            ]
            return compatible
        except ValueError:
            # If key not found, return just the key itself
            return [key]
    
    def _calculate_compatibility(
        self,
        song: Dict,
        vocal_analysis: Dict
    ) -> Dict:
        """
        Calculate compatibility score between song and user's voice
        
        Returns:
            Dict with breakdown: {
                'key_match': 0.0-1.0,
                'range_match': 0.0-1.0,
                'total': 0.0-1.0
            }
        """
        scores = {
            'key_match': 0.0,
            'range_match': 0.0,
            'total': 0.0
        }
        
        # 1. Key matching (50% weight)
        key_info = vocal_analysis.get('key', {})
        if isinstance(key_info, dict):
            user_key = key_info.get('key', 'C')
        else:
            user_key = 'C'
        
        song_key = song.get('key_note', 'C')
        
        if user_key == song_key:
            scores['key_match'] = 1.0
        elif self._are_keys_close(user_key, song_key):
            scores['key_match'] = 0.7
        else:
            scores['key_match'] = 0.3
        
        # 2. Range matching (50% weight)
        # Simple heuristic - can be improved
        scores['range_match'] = 0.8
        
        # Calculate total
        scores['total'] = (scores['key_match'] * 0.5 + scores['range_match'] * 0.5)
        
        return scores
    
    def _are_keys_close(self, key1: str, key2: str) -> bool:
        """Check if two keys are within 2 semitones"""
        key_circle = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        try:
            idx1 = key_circle.index(key1)
            idx2 = key_circle.index(key2)
            
            # Calculate distance (considering circle)
            distance = min(
                abs(idx1 - idx2),
                12 - abs(idx1 - idx2)
            )
            
            return distance <= 2
        except ValueError:
            return False
