# 🎵 VocaKey Backend API v2.0

VocaKey Backend adalah REST API untuk analisis vokal dan rekomendasi lagu berdasarkan pitch detection menggunakan algoritma pYIN. API ini dapat menganalisis audio humming dan memberikan rekomendasi lagu yang sesuai dengan karakteristik vokal pengguna.

---

## 🚀 Features

- ✅ **Pitch Detection** - Deteksi pitch menggunakan algoritma pYIN (librosa)
- ✅ **Vocal Analysis** - Analisis karakteristik vokal (range, key, vocal type)
- ✅ **Song Recommendation** - Rekomendasi lagu berdasarkan key dan confidence
- ✅ **Audio Transpose** - Transpose audio ke key yang berbeda
- ✅ **Mayor Notation** - Support notasi Mayor (C C# D D# E F F# G G# A A# B)
- ✅ **SQLite Database** - Penyimpanan data lagu lokal
- ✅ **CORS Enabled** - Siap digunakan dengan frontend

---

## 📋 Tech Stack

- **Python 3.13**
- **Flask** - Web framework
- **Librosa** - Audio analysis & pitch detection
- **SQLAlchemy** - ORM untuk database
- **SQLite** - Database
- **NumPy** - Numerical processing
- **SoundFile** - Audio file I/O

---

## 📦 Installation

### **1. Clone Repository**

git clone https://github.com/alikmakanmie/Vocakey-BE-V2.git
cd Vocakey-BE-V2


### **2. Create Virtual Environment (Optional)**

Windows
python -m venv venv
venv\Scripts\activate

Linux/Mac
python3 -m venv venv
source venv/bin/activate


### **3. Install Dependencies**

pip install -r requirements.txt



**requirements.txt:**
Flask==3.0.0
flask-cors==4.0.0
Werkzeug==3.0.1
SQLAlchemy>=2.0.0
librosa==0.10.1
soundfile==0.12.1
scipy==1.11.4
numpy==1.26.2
audioread==3.0.1
python-dotenv==1.0.0


### **4. Initialize Database**

python seed_database.py


Expected output:
✅ Successfully seeded 8 songs to database


---

## 🎯 Running the Server

### **Development Mode**

python app.py


Server akan berjalan di:
- **Local:** http://localhost:5000
- **Network:** http://192.168.x.x:5000

Expected output:
✅ Database initialized: songs.db
✅ PitchDetector initialized

Algorithm: pYIN

Frequency range: 65.4 Hz - 2093.0 Hz

Sample rate: 16000 Hz
✅ VocalAnalyzer initialized
✅ SongRecommenderSQLite initialized (SQLite)

============================================================
🎵 VocaKey Backend - Starting Server...
🌐 Server URL: http://localhost:5000
📡 API Endpoints:

GET /api/health → Health check

POST /api/analyze → Analyze vocal & get recommendations

POST /api/transpose/audio → Transpose audio file

GET /api/test → Test endpoint
============================================================

---

## 📡 API Endpoints

### **1. Health Check**

Check server status.

**Endpoint:** `GET /api/health`

**Response:**
{
"status": "healthy",
"service": "VocaKey API",
"version": "1.0.0"
}


---

### **2. Analyze Vocal + Recommendations**

Upload audio untuk analisis vokal dan mendapatkan rekomendasi lagu.

**Endpoint:** `POST /api/analyze`

**Request (multipart/form-data):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio` | File | ✅ Yes | Audio file (mp3, wav, m4a, ogg, flac, aac, webm) |
| `get_recommendations` | String | ❌ Optional | Enable recommendations (`"true"` / `"false"`, default: `"true"`) |
| `max_recommendations` | Integer | ❌ Optional | Max number of songs (1-20, default: 10) |

**Example Request (cURL):**
curl -X POST http://localhost:5000/api/analyze
-F "audio=@test_humming.wav"
-F "get_recommendations=true"
-F "max_recommendations=10"


**Response (200 OK):**
{
"success": true,
"data": {
"note": "G# major",
"vocal_range": "D#4 - A#4",
"accuracy": 85.5,
"vocal_type": "Tenor"
},
"recommendations": [
{
"title": "Perfect",
"artist": "Ed Sheeran",
"original_note": "G#",
"match_score": 95.8
},
{
"title": "Shape of You",
"artist": "Ed Sheeran",
"original_note": "G",
"match_score": 88.3
}
],
"metadata": {
"audio_duration": 3.5,
"sample_rate": 16000,
"algorithm": "pYIN",
"num_samples": 512
}
}


**Error Response (400 Bad Request):**
{
"success": false,
"error": "No pitch detected in audio"
}


---

### **3. Recommend by Humming (Direct)**

Mendapatkan rekomendasi lagu berdasarkan detected note (tanpa upload audio).

**Endpoint:** `POST /api/recommendation/by_humming`

**Request (application/json):**
{
"detected_note": "G# Major",
"humming_confidence": 0.85,
"limit": 10
}


**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `detected_note` | String | ✅ Yes | Detected key (Mayor notation: C, C#, D, D#, E, F, F#, G, G#, A, A#, B) |
| `humming_confidence` | Float | ❌ Optional | Confidence level (0.0-1.0, default: 0.5) |
| `limit` | Integer | ❌ Optional | Max number of songs (1-50, default: 10) |

**Response (200 OK):**
{
"success": true,
"detected_note": "G#",
"humming_confidence": 0.85,
"matched_keys": ["G", "G#", "A"],
"total_results": 3,
"recommendations": [
{
"id": 1,
"title": "Perfect",
"artist": "Ed Sheeran",
"key_note": "G#",
"pitch_range_acc": 0.68,
"link_youtube": "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
"genre": "Pop",
"tempo": 95,
"popularity_score": 0.98,
"match_score": 1.53,
"semitone_distance": 0
}
]
}


---

### **4. Transpose Audio**

Transpose audio file dari key asli ke key target.

**Endpoint:** `POST /api/transpose/audio`

**Request (multipart/form-data):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio` | File | ✅ Yes | Audio file to transpose |
| `original_key` | String | ✅ Yes | Original key (e.g., "C", "G#") |
| `target_key` | String | ✅ Yes | Target key (e.g., "D", "A#") |
| `preserve_formant` | String | ❌ Optional | Preserve formant (`"true"` / `"false"`, default: `"true"`) |

**Example Request (cURL):**
curl -X POST http://localhost:5000/api/transpose/audio
-F "audio=@song.wav"
-F "original_key=C"
-F "target_key=D"
-F "preserve_formant=true"

**Response (200 OK):**
{
"success": true,
"original_key": "C",
"target_key": "D",
"semitone_shift": 2,
"direction": "up",
"transposed_audio_url": "/uploads/audio_transposed_D.wav",
"quality": {
"is_optimal": true,
"is_acceptable": true,
"warning": null,
"suggestion": "Optimal transpose range (±2 semitones). Audio quality will be excellent."
},
"audio_info": {
"duration_seconds": 5.2,
"sample_rate": 16000,
"original_file": "uploads/audio.wav",
"output_file": "uploads/audio_transposed_D.wav"
}
}


---

## 🎵 Supported Audio Formats

- **MP3** (.mp3)
- **WAV** (.wav) ← Recommended
- **M4A** (.m4a)
- **OGG** (.ogg)
- **FLAC** (.flac)
- **AAC** (.aac)
- **WebM** (.webm)

**Maximum file size:** 10 MB

---

## 📊 Database Schema

### **Song Table**

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `title` | String | Song title |
| `artist` | String | Artist name |
| `key_note` | String | Musical key (Mayor notation: C, C#, D, etc.) |
| `pitch_range_acc` | Float | Pitch range accuracy (0.0-1.0) |
| `link_youtube` | String | YouTube URL |
| `genre` | String | Music genre |
| `tempo` | Integer | Tempo (BPM) |
| `popularity_score` | Float | Popularity score (0.0-1.0) |

---

## 🧪 Testing with Postman

### **Import Postman Collection**

1. Copy JSON collection dari `postman_collection.json`
2. Open Postman
3. Click **Import** → Paste JSON
4. Collection **VocaKey API** akan muncul

### **Quick Test Steps**

1. **Health Check:**
   - Method: GET
   - URL: `http://localhost:5000/api/health`
   - Expected: 200 OK

2. **Analyze Audio:**
   - Method: POST
   - URL: `http://localhost:5000/api/analyze`
   - Body: form-data
     - `audio`: Select file `test_humming.wav`
     - `get_recommendations`: `true`
     - `max_recommendations`: `10`
   - Expected: 200 OK with recommendations

3. **Direct Recommendation:**
   - Method: POST
   - URL: `http://localhost:5000/api/recommendation/by_humming`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```
     {
       "detected_note": "G#",
       "humming_confidence": 0.85,
       "limit": 10
     }
     ```
   - Expected: 200 OK with recommendations

---

## 🔧 Troubleshooting

### **1. Error: "No pitch detected"**

**Cause:** Audio terlalu pendek atau noise

**Solution:**
- Gunakan audio minimal 0.5 detik
- Pastikan audio adalah vokal/humming, bukan instrumental
- Convert ke WAV format: `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`

### **2. Error: "No recommendations found"**

**Cause:** Database kosong atau tidak ada lagu yang match

**Solution:**
Check database
python check_db.py

Populate database
python seed_database.py

Fix database keys to Mayor notation
python fix_database_keys.py


### **3. Error: "ImportError: cannot import name..."**

**Cause:** Missing dependencies

**Solution:**
pip install -r requirements.txt


### **4. Error: Port 5000 already in use**

**Solution:**
Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

Linux/Mac
lsof -ti:5000 | xargs kill -9


---

## 📁 Project Structure

Vocakey-BE-V2/
│
├── app.py # Main Flask application
├── pitch_detector.py # Pitch detection module (pYIN)
├── vocal_analyzer.py # Vocal analysis module
├── song_recommender_sqlite.py # Song recommendation engine
├── database_manager.py # Database connection manager
├── database_models.py # SQLAlchemy models
├── key_utils.py # Music theory utilities
├── seed_database.py # Database seeding script
├── requirements.txt # Python dependencies
├── README.md # Documentation
│
├── uploads/ # Temporary audio uploads
├── songs.db # SQLite database
│
└── tests/ # Test files (optional)
├── test_humming.wav
└── check_db.py


---

## 🎯 Algorithm Details

### **Pitch Detection (pYIN)**

- **Algorithm:** Probabilistic YIN (pYIN) dari librosa
- **Frequency Range:** 65.4 Hz - 2093.0 Hz (C2 - C7)
- **Sample Rate:** 16000 Hz
- **Frame Length:** 2048 samples

### **Key Detection**

- **Method:** Krumhansl-Schmuckler algorithm
- **Profiles:** Major & Minor key profiles
- **Output:** Key name + scale + confidence

### **Vocal Classification**

Vocal range categories:
- **Bass:** E2 - E4 (MIDI 40-64)
- **Baritone:** A2 - A4 (MIDI 45-69)
- **Tenor:** C3 - C5 (MIDI 48-72)
- **Alto:** F3 - F5 (MIDI 53-77)
- **Mezzo-Soprano:** A3 - A5 (MIDI 57-81)
- **Soprano:** C4 - C6 (MIDI 60-84)

### **Recommendation Algorithm**

Match score calculation:
total_score = (
key_match_score * 0.6 + # Key proximity
confidence * 0.2 + # Detection confidence
popularity_score * 0.2 # Song popularity
)


Key matching:
- **Perfect match** (0 semitones): 100% score
- **±1 semitone:** 80% score
- **±2 semitones:** 50% score

---

## 🎨 Mayor Notation

API ini menggunakan **Mayor notation (sharp only)**:

C → C# → D → D# → E → F → F# → G → G# → A → A# → B


**Flat notation** akan otomatis diconvert:
- Db → C#
- Eb → D#
- Gb → F#
- Ab → G#
- Bb → A#

---

## 🚀 Production Deployment

### **Using Gunicorn (Linux/Mac)**

pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app


### **Using Waitress (Windows)**

pip install waitress

waitress-serve --host=0.0.0.0 --port=5000 app:app


### **Docker (Optional)**

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]


Build & Run:
docker build -t vocakey-backend .
docker run -p 5000:5000 vocakey-backend

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**VocaKey Team**
- GitHub: [@alikmakanmie](https://github.com/alikmakanmie)
- Repository: [Vocakey-BE-V2](https://github.com/alikmakanmie/Vocakey-BE-V2)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📞 Support

If you have any questions or issues:
- Open an issue on [GitHub Issues](https://github.com/alikmakanmie/Vocakey-BE-V2/issues)
- Contact: [Your Email/Contact]

---

## 🎉 Acknowledgments

- **Librosa** - Audio analysis library
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **pYIN Algorithm** - Pitch detection method

---

**Happy Coding! 🎵🚀**
📋 Bonus: Postman Collection JSON
Buat file postman_collection.json:

json
{
  "info": {
    "name": "VocaKey API v2.0",
    "description": "Complete API collection for VocaKey Backend",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5000/api/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "health"]
        }
      }
    },
    {
      "name": "Analyze Vocal + Recommendations",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "audio",
              "type": "file",
              "src": ""
            },
            {
              "key": "get_recommendations",
              "value": "true",
              "type": "text"
            },
            {
              "key": "max_recommendations",
              "value": "10",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:5000/api/analyze",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "analyze"]
        }
      }
    },
    {
      "name": "Recommend by Humming",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"detected_note\": \"G# Major\",\n  \"humming_confidence\": 0.85,\n  \"limit\": 10\n}"
        },
        "url": {
          "raw": "http://localhost:5000/api/recommendation/by_humming",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "recommendation", "by_humming"]
        }
      }
    },
    {
      "name": "Transpose Audio",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "audio",
              "type": "file",
              "src": ""
            },
            {
              "key": "original_key",
              "value": "C",
              "type": "text"
            },
            {
              "key": "target_key",
              "value": "D",
              "type": "text"
            },
            {
              "key": "preserve_formant",
              "value": "true",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:5000/api/transpose/audio",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "transpose", "audio"]
        }
      }
    }
  ]
}