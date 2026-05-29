# ============================================
# bot/voice/voice_analysis.py
# ============================================

import os

from faster_whisper import WhisperModel

from bot.config import (
    VOICE_SAVE_PATH,
)

# ============================================
# LOAD WHISPER MODEL
# ============================================

print("Loading faster-whisper model...")

model = WhisperModel("base", device="cpu", compute_type="int8")

print("faster-whisper model loaded.")

# ============================================
# TRANSCRIBE AUDIO
# ============================================


async def transcribe_audio(audio_path):

    try:
        if not os.path.exists(audio_path):
            print(f"Missing audio file: {audio_path}")

            return ""

        segments, info = model.transcribe(audio_path)

        text = " ".join(segment.text for segment in segments).strip()

        print(f"Transcribed: {audio_path}")

        return text

    except Exception as e:
        print(f"Transcription error: {e}")

        return ""


# ============================================
# TRANSCRIBE ALL RECORDINGS
# ============================================


async def transcribe_all_recordings():

    results = []

    try:
        os.makedirs(VOICE_SAVE_PATH, exist_ok=True)

        files = [f for f in os.listdir(VOICE_SAVE_PATH) if f.endswith(".wav")]

        if not files:
            print("No recordings found.")

            return results

        for file in files:
            path = os.path.join(VOICE_SAVE_PATH, file)

            try:
                text = await transcribe_audio(path)

                if text:
                    results.append(
                        {
                            "file": file,
                            "text": text,
                        }
                    )

            except Exception as e:
                print(f"Failed processing {file}: {e}")

        print(f"Finished transcribing {len(results)} file(s).")

        return results

    except Exception as e:
        print(f"transcribe_all_recordings error: {e}")

        return results


# ============================================
# CLEANUP RECORDINGS
# ============================================


async def cleanup_recordings():

    try:
        if not os.path.exists(VOICE_SAVE_PATH):
            return

        deleted = 0

        for file in os.listdir(VOICE_SAVE_PATH):
            if not file.endswith(".wav"):
                continue

            path = os.path.join(VOICE_SAVE_PATH, file)

            try:
                os.remove(path)

                deleted += 1

            except Exception as e:
                print(f"Failed deleting {file}: {e}")

        print(f"Deleted {deleted} recording(s).")

    except Exception as e:
        print(f"cleanup_recordings error: {e}")
