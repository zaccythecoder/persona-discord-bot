# ============================================
# bot/config.py
# ============================================

import os

from dotenv import load_dotenv
from groq import Groq

# ============================================
# LOAD ENV
# ============================================

load_dotenv()

print("config.py loaded successfully")

# ============================================
# BASE PATH
# ============================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# BOT SETTINGS
# ============================================

PREFIX = "!"

# ============================================
# DATABASE
# ============================================

DATABASE = "data/persona.db"

DATABASE_PATH = os.path.join(BASE_DIR, DATABASE)

# ============================================
# DATA DIRECTORIES
# ============================================

DATA_FOLDER = os.path.join(BASE_DIR, "data")

RECORDINGS_FOLDER = os.path.join(DATA_FOLDER, "recordings")

TRANSCRIPTS_FOLDER = os.path.join(DATA_FOLDER, "transcripts")

VOICE_SAVE_PATH = RECORDINGS_FOLDER

# ============================================
# CREATE REQUIRED FOLDERS
# ============================================

os.makedirs(DATA_FOLDER, exist_ok=True)

os.makedirs(RECORDINGS_FOLDER, exist_ok=True)

os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

# ============================================
# TOKENS
# ============================================

TOKEN = os.getenv("TOKEN")

GROQ_KEY = os.getenv("GROQ_KEY") or os.getenv("GROQ_API_KEY")

# ============================================
# OPTIONAL SETTINGS
# ============================================

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ============================================
# VALIDATION
# ============================================

if not TOKEN:
    raise Exception("Missing TOKEN")

if not GROQ_KEY:
    raise Exception("Missing GROQ_KEY")

# ============================================
# GROQ CLIENT
# ============================================

groq_client = Groq(api_key=GROQ_KEY)

# ============================================
# AI SETTINGS
# ============================================

AI_MODEL = "llama3-70b-8192"

# backward compatibility
MODEL = AI_MODEL

MAX_HISTORY_MESSAGES = 100

MAX_ANALYSIS_MESSAGES = 500

# ============================================
# VOICE SETTINGS
# ============================================

VOICE_LOGGING_ENABLED = True

WHISPER_MODEL = "base"

VOICE_SAMPLE_RATE = 48000

VOICE_CHANNELS = 2

# ============================================
# DEBUG
# ============================================

print("\n====================================")
print("CONFIG LOADED")
print("====================================")

print(f"Database Path: {DATABASE_PATH}")

print(f"Recordings Path: {RECORDINGS_FOLDER}")

print(f"Transcripts Path: {TRANSCRIPTS_FOLDER}")

print(f"Owner ID: {OWNER_ID}")

print("====================================\n")
