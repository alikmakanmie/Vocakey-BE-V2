"""
Pitch Detector using pYIN algorithm
"""

import librosa
import numpy as np

class PitchDetector:
    def __init__(self, sample_rate=16000, fmin=65.4, fmax=2093.0):
        """
        Initialize PitchDetector
        
        Args:
            sample_rate: Target sample rate (default: 16000 Hz)
            fmin: Minimum frequency (default: 65.4 Hz = C2)
            fmax: Maximum frequency (default: 2093.0 Hz = C7)
        """
        self.sample_rate = sample_rate
        self.fmin = fmin
        self.fmax = fmax
        self.frame_length = 2048
        
        print("✅ PitchDetector initialized")
        print(f"   - Algorithm: pYIN")
        print(f"   - Frequency range: {fmin} Hz - {fmax} Hz")
        print(f"   - Sample rate: {sample_rate} Hz")
    
    def detect_pitch(self, audio_path):
        """
        Detect pitch from audio file using pYIN algorithm
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            dict with pitch detection results
        """
        try:
            # Load audio
            try:
                y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to load audio file: {str(e)}'
                }
            
            # Check if audio is too short
            duration = len(y) / sr
            if duration < 0.5:
                return {
                    'success': False,
                    'error': f'Audio too short: {duration:.2f}s (minimum 0.5s required)'
                }
            
            # Detect pitch using pYIN
            try:
                pitches, voiced_flags, voiced_probs = librosa.pyin(
                    y,
                    fmin=self.fmin,
                    fmax=self.fmax,
                    sr=sr,
                    frame_length=self.frame_length
                )
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Pitch detection failed: {str(e)}'
                }
            
            # Remove NaN values
            valid_pitches = pitches[~np.isnan(pitches)]
            
            if len(valid_pitches) == 0:
                return {
                    'success': False,
                    'error': 'No pitch detected (audio might be noise or instrumental)'
                }
            
            # Calculate timestamps
            hop_length = self.frame_length // 4
            timestamps = librosa.frames_to_time(
                np.arange(len(pitches)),
                sr=sr,
                hop_length=hop_length
            )
            
            # Success
            return {
                'success': True,
                'pitches': pitches.tolist(),
                'timestamps': timestamps.tolist(),
                'voiced_flags': voiced_flags.tolist() if voiced_flags is not None else [],
                'voiced_probs': voiced_probs.tolist() if voiced_probs is not None else [],
                'metadata': {
                    'duration': duration,
                    'sample_rate': sr,
                    'total_frames': len(pitches),
                    'valid_frames': len(valid_pitches),
                    'voiced_percentage': (len(valid_pitches) / len(pitches)) * 100
                }
            }
        
        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'traceback': traceback.format_exc()
            }
