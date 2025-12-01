"""
Vocal Analyzer Module
Menganalisis karakteristik vokal dari pitch data:
- Vocal range (Hz dan notes)
- Key/nada dasar detection
- Pitch statistics
"""

import librosa
import numpy as np
from collections import Counter

class VocalAnalyzer:
    def __init__(self):
        """Initialize Vocal Analyzer"""
        # Key profiles (Krumhansl-Schmuckler algorithm)
        self.major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        self.minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

        # Vocal range classifications (in MIDI notes)
        self.vocal_ranges = {
            'Bass': (40, 64),           # E2-E4
            'Baritone': (45, 69),       # A2-A4
            'Tenor': (48, 72),          # C3-C5
            'Alto': (53, 77),           # F3-F5
            'Mezzo-Soprano': (57, 81),  # A3-A5
            'Soprano': (60, 84)         # C4-C6
        }

        print("✅ VocalAnalyzer initialized")

    def analyze(self, pitch_data):
        """
        Analyze vocal characteristics from pitch data

        Args:
            pitch_data: Output from PitchDetector.detect_pitch()

        Returns:
            dict with vocal analysis results
        """
        f0 = pitch_data['f0']
        voiced_flag = pitch_data['voiced_flag']

        # Filter only voiced frames
        f0_voiced = f0[voiced_flag]
        f0_voiced = f0_voiced[~np.isnan(f0_voiced)]

        if len(f0_voiced) == 0:
            return {
                'error': 'No valid pitch detected'
            }

        # 1. Pitch Range Analysis
        pitch_range = self._analyze_pitch_range(f0_voiced)

        # 2. Key Detection
        key_info = self._detect_key(f0_voiced)

        # 3. Pitch Statistics
        stats = self._calculate_statistics(f0_voiced)

        # 4. Vocal Range Classification
        vocal_type = self._classify_vocal_range(pitch_range['midi']['min'], pitch_range['midi']['max'])

        print(f"   📊 Vocal Analysis:")
        print(f"      - Range: {pitch_range['notes']['min']} - {pitch_range['notes']['max']}")
        print(f"      - Key: {key_info['key']} {key_info['scale']}")
        print(f"      - Vocal Type: {vocal_type}")

        return {
            'pitch_range': pitch_range,
            'key': key_info,
            'statistics': stats,
            'vocal_classification': vocal_type,
            'melody_contour': self._extract_melody_contour(f0_voiced)
        }

    def _analyze_pitch_range(self, f0_voiced):
        """Calculate pitch range in Hz, MIDI, and note names"""
        min_hz = float(np.min(f0_voiced))
        max_hz = float(np.max(f0_voiced))
        mean_hz = float(np.mean(f0_voiced))
        median_hz = float(np.median(f0_voiced))

        # Convert to MIDI
        min_midi = float(librosa.hz_to_midi(min_hz))
        max_midi = float(librosa.hz_to_midi(max_hz))
        mean_midi = float(librosa.hz_to_midi(mean_hz))

        # Convert to note names
        min_note = librosa.midi_to_note(int(np.round(min_midi)))
        max_note = librosa.midi_to_note(int(np.round(max_midi)))
        mean_note = librosa.midi_to_note(int(np.round(mean_midi)))

        # Range in semitones
        range_semitones = max_midi - min_midi

        return {
            'hz': {
                'min': min_hz,
                'max': max_hz,
                'mean': mean_hz,
                'median': median_hz
            },
            'midi': {
                'min': min_midi,
                'max': max_midi,
                'mean': mean_midi,
                'range_semitones': float(range_semitones)
            },
            'notes': {
                'min': min_note,
                'max': max_note,
                'mean': mean_note
            }
        }

    def _detect_key(self, f0_voiced):
        """
        Detect musical key using Krumhansl-Schmuckler algorithm
        """
        # Convert Hz to MIDI
        midi_notes = librosa.hz_to_midi(f0_voiced)

        # Get pitch classes (0-11, where 0=C, 1=C#, etc.)
        pitch_classes = np.mod(np.round(midi_notes), 12).astype(int)

        # Build pitch class histogram
        histogram = np.zeros(12)
        for pc in pitch_classes:
            histogram[pc] += 1

        # Normalize
        histogram = histogram / (np.sum(histogram) + 1e-8)

        # Correlate with key profiles
        best_correlation = -1
        best_key = None
        best_scale = None

        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        for shift in range(12):
            # Test major
            shifted_histogram = np.roll(histogram, shift)
            correlation_major = np.corrcoef(shifted_histogram, self.major_profile)[0, 1]

            if correlation_major > best_correlation:
                best_correlation = correlation_major
                best_key = key_names[shift]
                best_scale = 'major'

            # Test minor
            correlation_minor = np.corrcoef(shifted_histogram, self.minor_profile)[0, 1]

            if correlation_minor > best_correlation:
                best_correlation = correlation_minor
                best_key = key_names[shift]
                best_scale = 'minor'

        return {
            'key': best_key,
            'scale': best_scale,
            'confidence': float(best_correlation),
            'pitch_class_histogram': histogram.tolist()
        }

    def _calculate_statistics(self, f0_voiced):
        """Calculate various pitch statistics"""
        return {
            'mean_hz': float(np.mean(f0_voiced)),
            'median_hz': float(np.median(f0_voiced)),
            'std_hz': float(np.std(f0_voiced)),
            'min_hz': float(np.min(f0_voiced)),
            'max_hz': float(np.max(f0_voiced)),
            'pitch_variability': float(np.std(f0_voiced) / np.mean(f0_voiced)),  # Coefficient of variation
            'num_samples': int(len(f0_voiced))
        }

    def _classify_vocal_range(self, min_midi, max_midi):
        """
        Classify vocal range based on pitch range
        """
        # Calculate overlap with each vocal range type
        overlaps = {}

        for range_name, (range_min, range_max) in self.vocal_ranges.items():
            # Calculate overlap
            overlap_min = max(min_midi, range_min)
            overlap_max = min(max_midi, range_max)
            overlap = max(0, overlap_max - overlap_min)

            user_range = max_midi - min_midi
            overlap_percentage = (overlap / user_range) * 100 if user_range > 0 else 0

            overlaps[range_name] = overlap_percentage

        # Find best match
        best_match = max(overlaps, key=overlaps.get)
        confidence = overlaps[best_match]

        # Determine if intermediate range
        sorted_matches = sorted(overlaps.items(), key=lambda x: x[1], reverse=True)

        classification = {
            'primary': best_match,
            'confidence': float(confidence),
            'all_matches': overlaps
        }

        # If two ranges have similar overlap, it's intermediate
        if len(sorted_matches) > 1 and sorted_matches[1][1] > 30:
            classification['secondary'] = sorted_matches[1][0]
            classification['type'] = 'intermediate'
        else:
            classification['type'] = 'definite'

        return classification

    def _extract_melody_contour(self, f0_voiced, num_points=20):
        """
        Extract simplified melody contour (for song matching)
        Sample evenly across the humming
        """
        if len(f0_voiced) < num_points:
            indices = range(len(f0_voiced))
        else:
            indices = np.linspace(0, len(f0_voiced) - 1, num_points).astype(int)

        contour_hz = f0_voiced[indices]
        contour_midi = librosa.hz_to_midi(contour_hz)

        # Normalize to start at 0 (relative pitch)
        contour_relative = contour_midi - contour_midi[0]

        return {
            'absolute_midi': contour_midi.tolist(),
            'relative_semitones': contour_relative.tolist(),
            'num_points': int(len(contour_midi))
        }
