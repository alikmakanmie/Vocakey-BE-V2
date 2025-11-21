"""
Test Client untuk VocaKey API
Script untuk testing endpoint API
"""

import requests
import json
import sys
import os

# ===== KONFIGURASI =====
API_BASE_URL = "http://localhost:5000"
TEST_AUDIO_PATH = "test_audio.mp3"  # Ganti dengan path audio Anda

# ===== COLORS FOR TERMINAL =====
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ===== TEST FUNCTIONS =====

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/api/health")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {data['status']}")
            print_success(f"Message: {data['message']}")
            print_info(f"Version: {data['version']}")
            print_info(f"Algorithms: {', '.join(data['algorithms'])}")
            return True
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        print_info("Run: python app.py")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_analyze_vocal(audio_path, get_recommendations=True, max_recommendations=5):
    """Test vocal analysis endpoint"""
    print_header("TEST 2: Analyze Vocal")

    # Check if file exists
    if not os.path.exists(audio_path):
        print_error(f"Audio file not found: {audio_path}")
        print_info("Please provide a valid audio file path")
        return False

    print_info(f"Audio file: {audio_path}")
    print_info(f"File size: {os.path.getsize(audio_path) / 1024:.2f} KB")

    try:
        # Prepare request
        with open(audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {
                'get_recommendations': str(get_recommendations).lower(),
                'max_recommendations': str(max_recommendations)
            }

            print_info("Sending request to API...")
            response = requests.post(f"{API_BASE_URL}/api/analyze", files=files, data=data)

        if response.status_code == 200:
            result = response.json()

            if result['success']:
                print_success("Analysis successful!\n")

                # Print vocal analysis
                va = result['vocal_analysis']

                print(f"{Colors.BOLD}📊 VOCAL ANALYSIS:{Colors.ENDC}")
                print(f"   Pitch Range: {va['pitch_range']['notes']['min']} - {va['pitch_range']['notes']['max']}")
                print(f"   Range (Hz): {va['pitch_range']['hz']['min']:.1f} - {va['pitch_range']['hz']['max']:.1f} Hz")
                print(f"   Range (Semitones): {va['pitch_range']['midi']['range_semitones']:.1f}")
                print(f"   Detected Key: {va['key']['key']} {va['key']['scale']}")
                print(f"   Key Confidence: {va['key']['confidence']:.2%}")
                print(f"   Vocal Type: {va['vocal_classification']['primary']}")
                print(f"   Classification Confidence: {va['vocal_classification']['confidence']:.1f}%")

                # Print metadata
                print(f"\n{Colors.BOLD}📁 METADATA:{Colors.ENDC}")
                meta = result['metadata']
                print(f"   Duration: {meta['audio_duration']:.2f} seconds")
                print(f"   Sample Rate: {meta['sample_rate']} Hz")
                print(f"   Algorithm: {meta['algorithm']}")

                # Print recommendations
                if result['recommended_songs']:
                    print(f"\n{Colors.BOLD}🎵 TOP RECOMMENDATIONS:{Colors.ENDC}\n")

                    for i, song in enumerate(result['recommended_songs'], 1):
                        score = song['compatibility_score']['total']

                        # Color based on score
                        if score >= 80:
                            color = Colors.OKGREEN
                        elif score >= 60:
                            color = Colors.OKCYAN
                        else:
                            color = Colors.WARNING

                        print(f"{color}{i}. {song['title']} - {song['artist']}{Colors.ENDC}")
                        print(f"   Score: {score}/100")
                        print(f"   Original Key: {song['original_key']}")

                        if song['transpose_semitones'] != 0:
                            direction = song['transpose_direction']
                            semitones = abs(song['transpose_semitones'])
                            print(f"   Recommended: Transpose {semitones} semitones {direction} → {song['recommended_key']}")
                        else:
                            print(f"   Recommended: Sing in original key")

                        print(f"   Genre: {song['genre']} | Difficulty: {song['difficulty']}")
                        print()

                return True
            else:
                print_error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                return False

        else:
            print_error(f"HTTP {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print_error(response.text)
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests(audio_path=None):
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          VocaKey API - Test Suite                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    results = []

    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))

    # Test 2: Analyze Vocal (if audio provided)
    if audio_path and os.path.exists(audio_path):
        results.append(("Analyze Vocal", test_analyze_vocal(audio_path)))
    else:
        print_header("TEST 2: Analyze Vocal")
        print_error("No audio file provided. Skipping analysis test.")
        print_info(f"Usage: python test_client.py <path_to_audio_file>")
        results.append(("Analyze Vocal", None))

    # Summary
    print_header("TEST SUMMARY")

    for test_name, result in results:
        if result is True:
            print_success(f"{test_name}: PASSED")
        elif result is False:
            print_error(f"{test_name}: FAILED")
        else:
            print_info(f"{test_name}: SKIPPED")

    print()

# ===== MAIN =====

if __name__ == "__main__":
    # Get audio path from command line argument
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not audio_path:
        print_info("No audio file specified. Running health check only.")
        print_info("Usage: python test_client.py <path_to_audio_file>")
        print()

    run_all_tests(audio_path)
