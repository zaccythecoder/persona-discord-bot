# ============================================
# bot/config.py
# ============================================

import os
from dotenv import load_dotenv
from groq import Groq

# ============================================
# LOAD .ENV
# ============================================

load_dotenv()

# ============================================
# DISCORD SETTINGS
# ============================================

TOKEN = os.getenv(
    "TOKEN"
)

PREFIX = os.getenv(
    "PREFIX",
    "!"
)

OWNER_ID = 1449536595060330588

# ============================================
# DATABASE SETTINGS
# ============================================

DATABASE = os.getenv(
    "DATABASE",
    "data/persona.db"
)

# ============================================
# AI SETTINGS
# ============================================

MODEL = os.getenv(
    "MODEL",
    "llama-3.3-70b-versatile"
)

# ============================================
# GROQ
# ============================================

GROQ_KEY = os.getenv(
    "GROQ_KEY"
)

if not GROQ_KEY:

    raise Exception(
        "Missing GROQ_KEY in .env"
    )

groq_client = Groq(
    api_key=GROQ_KEY
)

# ============================================
# TOKEN CHECK
# ============================================

if not TOKEN:

    raise Exception(
        "Missing TOKEN in .env"
    )

print(
    "config.py loaded successfully"
)