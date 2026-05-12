# ============================================
# bot/config.py
# ============================================

import os
from groq import Groq

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
# GROQ API KEY
# ============================================

GROQ_KEY = (
    os.getenv("GROQ_KEY")
    or
    os.getenv("GROQ_API_KEY")
)

if not GROQ_KEY:

    raise Exception(
        "Missing GROQ_KEY / GROQ_API_KEY environment variable"
    )

# ============================================
# GROQ CLIENT
# ============================================

groq_client = Groq(
    api_key=GROQ_KEY
)

# ============================================
# STARTUP CHECKS
# ============================================

if not TOKEN:

    raise Exception(
        "Missing TOKEN environment variable"
    )

print(
    "config.py loaded successfully"
)