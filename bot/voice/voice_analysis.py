# ============================================
# bot/voice/voice_analysis.py
# ============================================

from textblob import TextBlob

# ============================================
# EMOTION ANALYSIS
# ============================================

def detect_emotion(text):

    polarity = (
        TextBlob(text)
        .sentiment
        .polarity
    )

    if polarity > 0.3:

        return "positive"

    elif polarity < -0.3:

        return "negative"

    return "neutral"

# ============================================
# RELATIONSHIP SCORE
# ============================================

def relationship_score(messages):

    total = len(messages)

    positive = 0

    for msg in messages:

        if msg["emotion"] == "positive":

            positive += 1

    if total == 0:

        return 0

    return round(
        (positive / total) * 100,
        2
    )