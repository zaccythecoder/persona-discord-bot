# ============================================
# bot/voice/voice_profiles.py
# ============================================

from bot.voice.voice_memory import (
    load_memory
)

from bot.voice.voice_analysis import (
    relationship_score
)

# ============================================
# USER PROFILE
# ============================================

def generate_profile(username):

    memory = load_memory()

    if username not in memory:

        return None

    messages = memory[username]

    total_messages = len(messages)

    relationship = (
        relationship_score(messages)
    )

    emotions = {}

    for msg in messages:

        emotion = msg["emotion"]

        emotions[emotion] = (
            emotions.get(emotion, 0)
            + 1
        )

    return {

        "messages":
            total_messages,

        "relationship":
            relationship,

        "emotions":
            emotions

    }