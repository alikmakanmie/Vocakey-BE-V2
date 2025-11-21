"""
Song Recommender Module
Merekomendasikan lagu berdasarkan analisis vokal user
"""

import numpy as np
import json
import os

class SongRecommender:
    def __init__(self, songs_db_path='songs_database.json'):
        """
        Initialize Song Recommender

        Args:
            songs_db_path: Path to songs database JSON file
        """
        self.songs_db_path = songs_db_path
        self.songs_database = self._load_database()

        print(f"✅ SongRecommender initialized")
        print(f"   - Database: {len(self.songs_database)} songs loaded")

    def _load_database(self):
        """Load songs database from JSON file"""
        if not os.path.exists(self.songs_db_path):
            print(f"   ⚠️  Database not found, creating sample database...")
            self._create_sample_database()

        try:
            with open(self.songs_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"   ❌ Error loading database: {e}")
            return []

    def _create_sample_database(self):
        """Create sample songs database"""
        sample_songs = [
            {
                "id": "1",
                "title": "Perfect",
                "artist": "Ed Sheeran",
                "key": "G",
                "scale": "major",
                "tempo": 95,
                "vocal_range_midi": {"min": 57, "max": 76},  # A3-E5
                "genre": "Pop",
                "difficulty": "Medium",
                "year": 2017
            },
            {
                "id": "2",
                "title": "Someone Like You",
                "artist": "Adele",
                "key": "A",
                "scale": "major",
                "tempo": 67,
                "vocal_range_midi": {"min": 57, "max": 77},  # A3-F5
                "genre": "Pop Ballad",
                "difficulty": "Medium",
                "year": 2011
            },
            {
                "id": "3",
                "title": "Shape of You",
                "artist": "Ed Sheeran",
                "key": "C#",
                "scale": "minor",
                "tempo": 96,
                "vocal_range_midi": {"min": 52, "max": 69},  # E3-A4
                "genre": "Pop",
                "difficulty": "Easy",
                "year": 2017
            },
            {
                "id": "4",
                "title": "All of Me",
                "artist": "John Legend",
                "key": "Ab",
                "scale": "major",
                "tempo": 120,
                "vocal_range_midi": {"min": 53, "max": 72},  # F3-C5
                "genre": "R&B/Soul",
                "difficulty": "Medium",
                "year": 2013
            },
            {
                "id": "5",
                "title": "Thinking Out Loud",
                "artist": "Ed Sheeran",
                "key": "D",
                "scale": "major",
                "tempo": 79,
                "vocal_range_midi": {"min": 55, "max": 74},  # G3-D5
                "genre": "Pop/Soul",
                "difficulty": "Medium",
                "year": 2014
            },
            {
                "id": "6",
                "title": "Let It Be",
                "artist": "The Beatles",
                "key": "C",
                "scale": "major",
                "tempo": 72,
                "vocal_range_midi": {"min": 60, "max": 76},  # C4-E5
                "genre": "Rock/Pop",
                "difficulty": "Easy",
                "year": 1970
            },
            {
                "id": "7",
                "title": "Hallelujah",
                "artist": "Leonard Cohen",
                "key": "C",
                "scale": "major",
                "tempo": 60,
                "vocal_range_midi": {"min": 48, "max": 72},  # C3-C5
                "genre": "Folk/Pop",
                "difficulty": "Medium",
                "year": 1984
            },
            {
                "id": "8",
                "title": "Shallow",
                "artist": "Lady Gaga & Bradley Cooper",
                "key": "G",
                "scale": "minor",
                "tempo": 96,
                "vocal_range_midi": {"min": 55, "max": 79},  # G3-G5
                "genre": "Pop/Rock",
                "difficulty": "Hard",
                "year": 2018
            }
        ]

        with open(self.songs_db_path, 'w', encoding='utf-8') as f:
            json.dump(sample_songs, f, indent=2, ensure_ascii=False)

        return sample_songs

    def recommend(self, vocal_analysis, max_results=10):
        """
        Recommend songs based on vocal analysis

        Args:
            vocal_analysis: Output from VocalAnalyzer.analyze()
            max_results: Maximum number of recommendations

        Returns:
            List of recommended songs with compatibility scores
        """
        if not self.songs_database:
            return []

        user_key = vocal_analysis['key']['key']
        user_scale = vocal_analysis['key']['scale']
        user_range_min = vocal_analysis['pitch_range']['midi']['min']
        user_range_max = vocal_analysis['pitch_range']['midi']['max']

        recommendations = []

        for song in self.songs_database:
            # Calculate compatibility score
            score = self._calculate_compatibility_score(
                vocal_analysis, song
            )

            # Calculate transpose if needed
            transpose_info = self._calculate_transpose(
                user_range_min, user_range_max,
                song['vocal_range_midi']['min'],
                song['vocal_range_midi']['max']
            )

            recommendations.append({
                'song_id': song['id'],
                'title': song['title'],
                'artist': song['artist'],
                'original_key': f"{song['key']} {song['scale']}",
                'recommended_key': self._transpose_key(song['key'], transpose_info['semitones']),
                'transpose_semitones': transpose_info['semitones'],
                'transpose_direction': transpose_info['direction'],
                'compatibility_score': score,
                'score_breakdown': score['breakdown'],
                'genre': song['genre'],
                'difficulty': song['difficulty'],
                'tempo': song['tempo'],
                'year': song.get('year', 'Unknown')
            })

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x['compatibility_score']['total'], reverse=True)

        return recommendations[:max_results]

    def _calculate_compatibility_score(self, vocal_analysis, song):
        """
        Calculate compatibility score between user vocal and song
        Components:
        1. Key compatibility (30%)
        2. Vocal range compatibility (40%)
        3. Vocal type match (30%)
        """
        scores = {}

        # 1. Key Compatibility (30 points)
        user_key = vocal_analysis['key']['key']
        user_scale = vocal_analysis['key']['scale']
        song_key = song['key']
        song_scale = song['scale']

        key_score = self._calculate_key_compatibility(user_key, user_scale, song_key, song_scale)
        scores['key'] = key_score * 30

        # 2. Range Compatibility (40 points)
        user_min = vocal_analysis['pitch_range']['midi']['min']
        user_max = vocal_analysis['pitch_range']['midi']['max']
        song_min = song['vocal_range_midi']['min']
        song_max = song['vocal_range_midi']['max']

        range_score = self._calculate_range_compatibility(user_min, user_max, song_min, song_max)
        scores['range'] = range_score * 40

        # 3. Vocal Type Match (30 points)
        vocal_type_score = self._calculate_vocal_type_match(
            vocal_analysis['vocal_classification'],
            song['vocal_range_midi']
        )
        scores['vocal_type'] = vocal_type_score * 30

        total_score = sum(scores.values())

        return {
            'total': round(total_score, 2),
            'breakdown': {
                'key_compatibility': round(scores['key'], 2),
                'range_compatibility': round(scores['range'], 2),
                'vocal_type_match': round(scores['vocal_type'], 2)
            }
        }

    def _calculate_key_compatibility(self, user_key, user_scale, song_key, song_scale):
        """Calculate key compatibility (0-1)"""
        # Perfect match
        if user_key == song_key and user_scale == song_scale:
            return 1.0

        # Same key, different scale (relative major/minor)
        if user_key == song_key:
            return 0.8

        # Calculate semitone distance
        key_to_number = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                         'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
                         'Db': 1, 'Eb': 3, 'Gb': 6, 'Ab': 8, 'Bb': 10}

        user_num = key_to_number.get(user_key, 0)
        song_num = key_to_number.get(song_key, 0)

        distance = min(abs(user_num - song_num), 12 - abs(user_num - song_num))

        # Score based on circle of fifths distance
        if distance == 0:
            return 1.0
        elif distance <= 1:  # Adjacent keys
            return 0.9
        elif distance <= 2:  # Close keys
            return 0.7
        elif distance <= 5:  # Related keys
            return 0.5
        else:  # Distant keys
            return 0.3

    def _calculate_range_compatibility(self, user_min, user_max, song_min, song_max):
        """Calculate range compatibility (0-1)"""
        # Check if user can sing the song without transpose
        if user_min <= song_min and user_max >= song_max:
            return 1.0  # Perfect fit

        # Calculate overlap
        overlap_min = max(user_min, song_min)
        overlap_max = min(user_max, song_max)
        overlap = max(0, overlap_max - overlap_min)

        song_range = song_max - song_min
        user_range = user_max - user_min

        # Overlap percentage
        overlap_ratio = overlap / song_range if song_range > 0 else 0

        # Additional penalty if ranges are very different
        range_diff = abs(user_range - song_range)
        range_penalty = min(range_diff / 12, 0.3)  # Max 30% penalty

        score = overlap_ratio - range_penalty

        return max(0, min(1, score))

    def _calculate_vocal_type_match(self, vocal_classification, song_range):
        """Calculate how well vocal type matches song requirements"""
        # This is a simplified version
        # In production, you'd have vocal type tags for each song

        confidence = vocal_classification['confidence'] / 100

        # Bonus if it's a definite classification
        if vocal_classification['type'] == 'definite':
            return confidence * 1.0
        else:
            return confidence * 0.8

    def _calculate_transpose(self, user_min, user_max, song_min, song_max):
        """
        Calculate optimal transpose (in semitones)
        """
        # Calculate center of ranges
        user_center = (user_min + user_max) / 2
        song_center = (song_min + song_max) / 2

        # Transpose suggestion (round to nearest semitone)
        transpose = round(user_center - song_center)

        # Limit transpose to reasonable range (-6 to +6 semitones)
        transpose = max(-6, min(6, transpose))

        if transpose > 0:
            direction = "up"
        elif transpose < 0:
            direction = "down"
        else:
            direction = "none"

        return {
            'semitones': int(transpose),
            'direction': direction
        }

    def _transpose_key(self, original_key, semitones):
        """Transpose key by semitones"""
        if semitones == 0:
            return original_key

        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        try:
            original_index = keys.index(original_key)
            new_index = (original_index + semitones) % 12
            return keys[new_index]
        except ValueError:
            # Handle alternative notations (Db, Eb, etc.)
            alt_keys = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
            if original_key in alt_keys:
                original_key = alt_keys[original_key]
                original_index = keys.index(original_key)
                new_index = (original_index + semitones) % 12
                return keys[new_index]
            return original_key
