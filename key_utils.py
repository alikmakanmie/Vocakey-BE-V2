"""
Key Utilities - Music Theory Helpers
Support Mayor notation: C C# D D# E E# F F# G G# A A# B B#
"""

from typing import List

# Major Keys Mapping (semitone 0-11)
MAJOR_KEYS = {
    # Standard Mayor notes
    'C': 0,
    'C#': 1,
    'D': 2,
    'D#': 3,
    'E': 4,
    'F': 5,    # Also E# enharmonic
    'F#': 6,
    'G': 7,
    'G#': 8,
    'A': 9,
    'A#': 10,
    'B': 11,
    
    # Flat keys for input compatibility (convert to sharp)
    'Db': 1,   # Convert to C#
    'Eb': 3,   # Convert to D#
    'Fb': 4,   # Convert to E
    'Gb': 6,   # Convert to F#
    'Ab': 8,   # Convert to G#
    'Bb': 10,  # Convert to A#
    'Cb': 11,  # Convert to B
}

# Preferred output notation (sharp only, Mayor format)
SEMITONE_TO_KEY = {
    0: 'C',
    1: 'C#',
    2: 'D',
    3: 'D#',
    4: 'E',
    5: 'F',
    6: 'F#',
    7: 'G',
    8: 'G#',
    9: 'A',
    10: 'A#',
    11: 'B'
}

def normalize_key_name(key_input: str) -> str:
    """
    Normalize key to Mayor notation (sharp only)
    
    Args:
        key_input: Input key (e.g., 'Bb major', 'F#', 'Eb')
    
    Returns:
        Normalized key in Mayor notation (e.g., 'A#', 'F#', 'D#')
    """
    # Remove 'major', 'minor', whitespace
    key = key_input.strip()
    key = key.replace(' major', '').replace(' Major', '')
    key = key.replace(' minor', '').replace(' Minor', '')
    key = key.strip()
    
    # Capitalize properly
    if len(key) > 1:
        key = key[0].upper() + key[1].lower()
    else:
        key = key.upper()
    
    # Convert flat to sharp (Mayor notation)
    flat_to_sharp = {
        'Db': 'C#',
        'Eb': 'D#',
        'Fb': 'E',
        'Gb': 'F#',
        'Ab': 'G#',
        'Bb': 'A#',
        'Cb': 'B'
    }
    
    if key in flat_to_sharp:
        key = flat_to_sharp[key]
    
    return key

def get_key_semitone(key_str: str) -> int:
    """
    Get semitone value (0-11) for a key
    
    Args:
        key_str: Key name (e.g., 'C', 'F#', 'Bb')
    
    Returns:
        Semitone value (0-11)
    """
    normalized = normalize_key_name(key_str)
    
    if normalized not in MAJOR_KEYS:
        raise ValueError(f"Invalid key: {key_str} (normalized: {normalized})")
    
    return MAJOR_KEYS[normalized]

def get_nearby_keys(detected_note: str, semitone_range: int = 1) -> List[str]:
    """
    Get keys within ±semitone_range
    Returns in Mayor notation (sharp only)
    
    Args:
        detected_note: Detected note (e.g., 'G', 'Bb')
        semitone_range: Range in semitones (default: 1)
    
    Returns:
        List of nearby keys in Mayor notation
    """
    try:
        base_semitone = get_key_semitone(detected_note)
    except ValueError:
        # Fallback to C if invalid key
        print(f"[key_utils WARNING] Invalid key '{detected_note}', using 'C' as fallback")
        base_semitone = 0
    
    # Calculate range
    nearby_semitones = []
    for offset in range(-semitone_range, semitone_range + 1):
        semitone = (base_semitone + offset) % 12
        nearby_semitones.append(semitone)
    
    # Convert to Mayor notation
    nearby_keys = [SEMITONE_TO_KEY[s] for s in nearby_semitones]
    
    return nearby_keys

def calculate_semitone_distance(key1: str, key2: str) -> int:
    """
    Calculate shortest distance in semitones between two keys
    
    Args:
        key1: First key (e.g., 'C', 'F#')
        key2: Second key (e.g., 'G', 'Bb')
    
    Returns:
        Shortest distance in semitones (0-6)
    
    Example:
        >>> calculate_semitone_distance('C', 'G')
        5
        >>> calculate_semitone_distance('C', 'F')
        5  # Shortest path: C -> B -> Bb -> A -> Ab -> G -> F (5 steps)
    """
    try:
        semitone1 = get_key_semitone(key1)
        semitone2 = get_key_semitone(key2)
        
        # Calculate distance (circular)
        distance = abs(semitone2 - semitone1)
        
        # Get shortest path (max distance is 6 semitones in chromatic circle)
        if distance > 6:
            distance = 12 - distance
        
        return distance
    
    except ValueError as e:
        print(f"[key_utils ERROR] calculate_semitone_distance: {str(e)}")
        return 6  # Return max distance on error

def semitone_to_mayor_note(semitone: int) -> str:
    """
    Convert semitone (0-11) to Mayor notation
    
    Args:
        semitone: Semitone value (0-11)
    
    Returns:
        Note in Mayor format (e.g., 'C#', 'F#')
    """
    return SEMITONE_TO_KEY.get(semitone % 12, 'C')

def get_all_major_keys() -> List[str]:
    """
    Get all major keys in Mayor notation
    
    Returns:
        List of all 12 major keys
    """
    return [SEMITONE_TO_KEY[i] for i in range(12)]
