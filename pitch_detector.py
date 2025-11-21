"""
Pitch Detector Module
Menggunakan pYIN algorithm untuk deteksi pitch dari audio humming
"""

import librosa
import numpy as np
import soundfile as sf
import warnings
warnings.filterwarnings('ignore')

class PitchDetector:
    def __init__(self):
        """
        Initialize Pitch Detector dengan parameter optimal untuk humming
        """
        # Parameter pYIN
        self.fmin = librosa.note_to_hz('C2')  # 65.4 Hz (low male voice)
        self.fmax = librosa.note_to_hz('C7')  # 2093 Hz (high female voice)
        self.sr = 16000  # Sample rate (16kHz cukup untuk vokal)

        print("✅ PitchDetector initialized")
        print(f"   - Algorithm: pYIN")
        print(f"   - Frequency range: {self.fmin:.1f} Hz - {self.fmax:.1f} Hz")
        print(f"   - Sample rate: {self.sr} Hz")

    def detect_pitch(self, audio_path):
        """
        Deteksi pitch dari file audio

        Args:
            audio_path: Path ke file audio

        Returns:
            dict dengan keys:
                - success: bool
                - f0: numpy array of frequencies (Hz)
                - voiced_flag: numpy array of boolean (voiced/unvoiced)
                - voiced_probs: numpy array of probabilities
                - times: numpy array of time stamps
                - metadata: dict info audio
        """
        try:
            # Load audio
            y, sr_original = librosa.load(audio_path, sr=self.sr, mono=True)
            duration = len(y) / self.sr

            print(f"   📁 Audio loaded: {duration:.2f}s")

            # Preprocessing
            y_processed = self._preprocess(y)

            # Pitch detection dengan pYIN
            print(f"   🔍 Running pYIN algorithm...")
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y_processed,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sr,
                frame_length=2048,
                hop_length=512,
                center=True,
                pad_mode='constant'
            )

            # Generate time stamps
            times = librosa.times_like(f0, sr=self.sr, hop_length=512)

            # Post-processing
            f0_corrected = self._postprocess(f0, voiced_flag)

            # Statistics
            voiced_frames = np.sum(voiced_flag)
            total_frames = len(voiced_flag)
            voicing_rate = (voiced_frames / total_frames) * 100 if total_frames > 0 else 0

            print(f"   ✅ Detection complete:")
            print(f"      - Total frames: {total_frames}")
            print(f"      - Voiced frames: {voiced_frames} ({voicing_rate:.1f}%)")

            if voiced_frames == 0:
                return {
                    'success': False,
                    'error': 'No voice detected in audio. Please hum louder or reduce background noise.'
                }

            return {
                'success': True,
                'f0': f0_corrected,
                'f0_raw': f0,
                'voiced_flag': voiced_flag,
                'voiced_probs': voiced_probs,
                'times': times,
                'metadata': {
                    'duration': duration,
                    'sample_rate': self.sr,
                    'total_frames': int(total_frames),
                    'voiced_frames': int(voiced_frames),
                    'voicing_rate': float(voicing_rate)
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error detecting pitch: {str(e)}'
            }

    def _preprocess(self, y):
        """
        Preprocessing audio untuk meningkatkan akurasi deteksi pitch

        Steps:
        1. Normalization
        2. Pre-emphasis filter (boost high frequencies)
        3. Trimming silence
        """
        # 1. Normalization
        y = y / (np.max(np.abs(y)) + 1e-8)

        # 2. Pre-emphasis (optional, boost formants)
        y = librosa.effects.preemphasis(y, coef=0.95)

        # 3. Trim silence (top_db=20 untuk humming)
        y, _ = librosa.effects.trim(y, top_db=20)

        return y

    def _postprocess(self, f0, voiced_flag):
        """
        Post-processing untuk koreksi error

        Steps:
        1. Median filtering (smoothing)
        2. Octave error correction
        3. Outlier removal
        """
        f0_processed = f0.copy()

        # Apply only to voiced frames
        voiced_indices = np.where(voiced_flag)[0]

        if len(voiced_indices) == 0:
            return f0_processed

        voiced_f0 = f0_processed[voiced_indices]

        # 1. Median filtering (window size 3)
        from scipy.signal import medfilt
        voiced_f0_smoothed = medfilt(voiced_f0, kernel_size=3)

        # 2. Octave error correction
        voiced_f0_corrected = self._correct_octave_errors(voiced_f0_smoothed)

        # 3. Outlier removal (pitch jumps > 5 semitones)
        voiced_f0_final = self._remove_outliers(voiced_f0_corrected, max_jump_semitones=5)

        # Put back to original array
        f0_processed[voiced_indices] = voiced_f0_final

        return f0_processed

    def _correct_octave_errors(self, f0_sequence):
        """
        Koreksi octave doubling/halving errors
        """
        corrected = [f0_sequence[0]]

        for i in range(1, len(f0_sequence)):
            current_f0 = f0_sequence[i]
            prev_f0 = corrected[-1]

            if np.isnan(current_f0) or np.isnan(prev_f0):
                corrected.append(current_f0)
                continue

            # Check ratio
            ratio = current_f0 / prev_f0

            # Octave up error (ratio ~2)
            if 1.9 < ratio < 2.1:
                corrected.append(current_f0 / 2)
            # Octave down error (ratio ~0.5)
            elif 0.45 < ratio < 0.55:
                corrected.append(current_f0 * 2)
            else:
                corrected.append(current_f0)

        return np.array(corrected)

    def _remove_outliers(self, f0_sequence, max_jump_semitones=5):
        """
        Remove outliers based on maximum allowed pitch jump
        """
        cleaned = [f0_sequence[0]]

        for i in range(1, len(f0_sequence)):
            current_f0 = f0_sequence[i]
            prev_f0 = cleaned[-1]

            if np.isnan(current_f0) or np.isnan(prev_f0):
                cleaned.append(current_f0)
                continue

            # Calculate semitone distance
            semitone_distance = abs(12 * np.log2(current_f0 / prev_f0))

            if semitone_distance > max_jump_semitones:
                # Outlier detected, use previous value
                cleaned.append(prev_f0)
            else:
                cleaned.append(current_f0)

        return np.array(cleaned)
