"""Configuration settings for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Firebase Configuration
from pathlib import Path

# Firebase credentials file
BASE_DIR = Path(__file__).resolve().parent

FIREBASE_CREDENTIALS = BASE_DIR / "pharmaquery-4710d-firebase-adminsdk-fbsvc-74a0db554b.json"
'''
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
}
'''
# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
IQVIA_API_KEY = os.getenv("IQVIA_API_KEY", "mock-key")
EXIM_API_KEY = os.getenv("EXIM_API_KEY", "mock-key")
USPTO_API_KEY = os.getenv("USPTO_API_KEY", "mock-key")
CLINICAL_TRIALS_API_KEY = os.getenv("CLINICAL_TRIALS_API_KEY", "mock-key")

# Scoring Weights
SCORING_WEIGHTS = {
    "market": 0.3,
    "patent": 0.25,
    "clinical": 0.25,
    "literature": 0.2
}

# Server Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
# Default CORS origins - include common Vite dev server ports
default_origins = [
    "http://localhost:5173",  # Default Vite port
    "http://localhost:8080",  # Custom Vite port
    "http://localhost:3000",  # Common React port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:3000",
]
CORS_ORIGINS = os.getenv("CORS_ORIGINS", ",".join(default_origins)).split(",")

# Paths
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

