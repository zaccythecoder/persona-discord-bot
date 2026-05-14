# ============================================
# bot/voice/voice_summary.py
# ============================================

from groq import Groq

from bot.config import (
    GROQ_KEY
)

client = Groq(
    api_key=GROQ_KEY
)

# ============================================
# SUMMARIZE
# ============================================

def summarize_text(text):

    response = client.chat.completions.create(

        model="llama3-70b-8192",

        messages=[

            {
                "role": "system",
                "content":
                    "Summarize this voice chat conversation."
            },

            {
                "role": "user",
                "content":
                    text
            }

        ]

    )

    return (
        response
        .choices[0]
        .message
        .content
    )