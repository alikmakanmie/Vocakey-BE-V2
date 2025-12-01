# transpose_audio.py
"""
Audio Transpose Module
Transpose audio file dari satu key ke key lain dengan preserving formant
"""

import librosa
import soundfile as sf
import numpy as np
from typing import Tuple, Optional
import warnings

# ===== MAJOR KEYS DICTIONARY =====
MAJOR_KEYS = {
    # Natural keys
    'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
    
    # Sharp keys
    'C#': 1, 'D#': 3, 'E#': 5, 'F#': 6, 'G#': 8, 'A#': 10, 'B#': 0,
    
    # Flat keys (enharmonic)
    'Db': 1, 'Eb': 3, 'Fb': 4, 'Gb': 6, 'Ab': 8, 'Bb': 10, 'Cb': 11,
}

SEMITONE_TO_KEY = {
    0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
    6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
}

OPTIMAL_TRANSPOSE_RANGE = 2  # ±2 semitones (optimal quality)
MAXIMUM_TRANSPOSE_RANGE = 6  # ±6 semitones (maximum acceptable)

# ===== HELPER FUNCTIONS =====

def normalize_key_name(key_input):
    """Normalize key name dari berbagai format"""
    key = key_input.strip().replace(' major', '').replace(' Major', '').replace('M', '')
    key = key.strip()
    
    if len(key) > 1:
        key = key[0].upper() + key[1].lower()
    else:
        key = key.upper()
    
    return key

def calculate_semitone_shift(original_key: str, target_key: str) -> int:
    """
    Hitung perbedaan semitone antara keys
    Formula: semitone_shift = MAJOR_KEYS[target] - MAJOR_KEYS[original]
    """
    orig_key = normalize_key_name(original_key)
    targ_key = normalize_key_name(target_key)
    
    if orig_key not in MAJOR_KEYS:
        raise ValueError(f"Invalid original key: {original_key}")
    if targ_key not in MAJOR_KEYS:
        raise ValueError(f"Invalid target key: {target_key}")
    
    semitone_shift = MAJOR_KEYS[targ_key] - MAJOR_KEYS[orig_key]
    
    # Shortest path (e.g., B to C = +1, not +11)
    if semitone_shift > 6:
        semitone_shift -= 12
    elif semitone_shift < -6:
        semitone_shift += 12
    
    return semitone_shift

def get_transpose_recommendation(semitone_shift: int) -> dict:
    """Generate quality recommendation"""
    recommendation = {
        'semitone_shift': semitone_shift,
        'is_optimal': abs(semitone_shift) <= OPTIMAL_TRANSPOSE_RANGE,
        'is_acceptable': abs(semitone_shift) <= MAXIMUM_TRANSPOSE_RANGE,
        'quality_warning': None,
        'suggestion': None
    }
    
    if abs(semitone_shift) == 0:
        recommendation['suggestion'] = "No transpose needed. Keys are identical."
    
    elif abs(semitone_shift) <= OPTIMAL_TRANSPOSE_RANGE:
        recommendation['suggestion'] = (
            f"Optimal transpose range (±{OPTIMAL_TRANSPOSE_RANGE} semitones). "
            f"Audio quality will be excellent."
        )
    
    elif abs(semitone_shift) <= MAXIMUM_TRANSPOSE_RANGE:
        recommendation['quality_warning'] = (
            f"Transpose of {abs(semitone_shift)} semitones may cause slight "
            f"audio degradation. Consider using ±{OPTIMAL_TRANSPOSE_RANGE} semitones."
        )
        recommendation['suggestion'] = "Acceptable but not optimal."
    
    else:
        recommendation['quality_warning'] = (
            f"EXTREME TRANSPOSE ({abs(semitone_shift)} semitones)! "
            f"Maximum recommended: ±{MAXIMUM_TRANSPOSE_RANGE} semitones."
        )
        recommendation['suggestion'] = "NOT RECOMMENDED."
    
    return recommendation

# ===== MAIN TRANSPOSE FUNCTION =====

def transpose_audio(
    audio_file: str,
    original_key: str,
    target_key: str,
    output_file: Optional[str] = None,
    method: str = 'librosa',
    preserve_formant: bool = True
) -> Tuple[str, dict]:
    """
    Transpose audio file dari original key ke target key
    
    Args:
        audio_file: Path ke file audio input
        original_key: Key asli (e.g., 'C', 'G#')
        target_key: Key target (e.g., 'D', 'A')
        output_file: Output path (auto-generate if None)
        method: 'librosa' atau 'pyrubberband'
        preserve_formant: Preserve formant untuk naturalness
    
    Returns:
        (output_filepath, transpose_info_dict)
    """
    
    # Calculate semitone shift
    semitone_shift = calculate_semitone_shift(original_key, target_key)
    
    # Get recommendation
    recommendation = get_transpose_recommendation(semitone_shift)
    
    # Validate range
    if not recommendation['is_acceptable']:
        raise ValueError(
            f"Transpose of {semitone_shift} semitones exceeds maximum "
            f"allowed range (±{MAXIMUM_TRANSPOSE_RANGE})."
        )
    
    # Warning untuk non-optimal
    if not recommendation['is_optimal']:
        warnings.warn(recommendation['quality_warning'], UserWarning)
    
    # Load audio
    print(f"[1/4] Loading audio: {audio_file}")
    y, sr = librosa.load(audio_file, sr=None, mono=True)
    duration = len(y) / sr
    
    # Transpose
    print(f"[2/4] Transposing by {semitone_shift} semitones...")
    
    if method == 'librosa':
        y_transposed = librosa.effects.pitch_shift(
            y=y,
            sr=sr,
            n_steps=semitone_shift,
            bins_per_octave=12 * 4 if preserve_formant else 12
        )
    
    elif method == 'pyrubberband':
        try:
            import pyrubberband as pyrb
            y_transposed = pyrb.pitch_shift(y, sr, semitone_shift)
        except ImportError:
            warnings.warn("pyrubberband not installed. Using librosa.", UserWarning)
            y_transposed = librosa.effects.pitch_shift(y, sr, n_steps=semitone_shift)
    
    else:
        raise ValueError(f"Invalid method: {method}")
    
    # Auto-generate output filename
    if output_file is None:
        import os
        base, ext = os.path.splitext(audio_file)
        output_file = f"{base}_transposed_{target_key.replace('#', 'sharp')}{ext}"
    
    # Save
    print(f"[3/4] Saving to: {output_file}")
    sf.write(output_file, y_transposed, sr)
    
    # Info
    transpose_info = {
        'success': True,
        'original_key': original_key,
        'target_key': target_key,
        'semitone_shift': semitone_shift,
        'direction': 'up' if semitone_shift > 0 else 'down' if semitone_shift < 0 else 'none',
        'method': method,
        'preserve_formant': preserve_formant,
        'audio_info': {
            'duration_seconds': float(duration),
            'sample_rate': int(sr),
            'original_file': audio_file,
            'output_file': output_file
        },
        'quality': {
            'is_optimal': recommendation['is_optimal'],
            'is_acceptable': recommendation['is_acceptable'],
            'warning': recommendation['quality_warning'],
            'suggestion': recommendation['suggestion']
        }
    }
    
    print(f"[4/4] Complete! Shift: {semitone_shift} semitones {transpose_info['direction']}")
    
    return output_file, transpose_info
