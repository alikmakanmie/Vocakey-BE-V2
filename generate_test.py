# generate_test.py
import numpy as np
import soundfile as sf

# Generate simple humming-like audio (C4 = 261.63 Hz)
duration = 3
sr = 16000
freq = 261.63  # C4

t = np.linspace(0, duration, int(sr * duration))
audio = 0.5 * np.sin(2 * np.pi * freq * t)

# Add some variation (vibrato)
vibrato = 0.05 * np.sin(2 * np.pi * 5 * t)
audio = audio * (1 + vibrato)

sf.write('test_humming.wav', audio, sr)
print("✅ Generated: test_humming.wav")
