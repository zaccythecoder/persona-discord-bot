# ============================================
# bot/config.py
# ============================================

import os

from dotenv import load_dotenv

# ============================================
# LOAD ENV
# ============================================

load_dotenv()

print(
    "config.py loaded successfully"
)

# ============================================
# BOT SETTINGS
# ============================================

PREFIX = "!"

# ============================================
# DATABASE
# ============================================

DATABASE = "data/persona.db"

# ============================================
# TOKENS
# ============================================

TOKEN = os.getenv(
    "TOKEN"
)

GROQ_KEY = (
    os.getenv("GROQ_KEY")
    or
    os.getenv("GROQ_API_KEY")
)

# ============================================
# OPTIONAL SETTINGS
# ============================================

OWNER_ID = int(
    os.getenv(
        "OWNER_ID",
        "0"
    )
)

# ============================================
# VALIDATION
# ============================================

if not TOKEN:

    raise Exception(
        "Missing TOKEN environment variable"
    )

if not GROQ_KEY:

    raise Exception(
        "Missing GROQ_KEY / GROQ_API_KEY environment variable"
    )

# ============================================
# VOICE SETTINGS
# ============================================

VOICE_LOGGING_ENABLED = True

WHISPER_MODEL = "base"

VOICE_SAVE_PATH = "voice_recordings"

# ============================================
# AI SETTINGS
# ============================================

AI_MODEL = "llama3-70b-8192"

MAX_HISTORY_MESSAGES = 100

MAX_ANALYSIS_MESSAGES = 500