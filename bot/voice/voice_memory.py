# ============================================
# bot/voice/voice_memory.py
# ============================================

import os
import json
from datetime import datetime

MEMORY_PATH = (
    "data/voice_memory.json"
)

# ============================================
# LOAD
# ============================================

def load_memory():

    if not os.path.exists(
        MEMORY_PATH
    ):

        return {}

    with open(
        MEMORY_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# ============================================
# SAVE
# ============================================

def save_memory(memory):

    with open(
        MEMORY_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=4
        )

# ============================================
# ADD MESSAGE
# ============================================

def add_transcript(
    username,
    text,
    emotion
):

    memory = load_memory()

    if username not in memory:

        memory[username] = []

    memory[username].append({

        "timestamp":
            str(datetime.utcnow()),

        "text":
            text,

        "emotion":
            emotion

    })

    save_memory(memory)