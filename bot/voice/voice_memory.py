# ============================================
# bot/voice/voice_memory.py
# ============================================

import os
from datetime import datetime

from bot.database import db, db_lock

# ============================================
# TRANSCRIPT FOLDER
# ============================================

TRANSCRIPT_FOLDER = "data/transcripts"

os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

# ============================================
# SAVE TRANSCRIPT TO DATABASE
# ============================================


async def save_transcript(user_id, username, transcript):

    try:
        if not db:
            print("Database not initialized.")

            return False

        async with db_lock:
            await db.execute(
                """
                INSERT INTO voice_transcripts (

                    user_id,
                    username,
                    transcript,
                    timestamp

                )

                VALUES (?, ?, ?, ?)
                """,
                (user_id, username, transcript, str(datetime.utcnow())),
            )

            await db.commit()

        print(f"Saved transcript for {username}")

        return True

    except Exception as e:
        print(f"save_transcript error: {e}")

        return False


# ============================================
# SAVE TRANSCRIPT TO FILE
# ============================================


async def save_transcript_file(username, transcript):

    try:
        safe_name = "".join(c for c in username if c.isalnum() or c in "_- ").strip()

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        filename = f"{safe_name}_{timestamp}.txt"

        path = os.path.join(TRANSCRIPT_FOLDER, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"Saved transcript file: {filename}")

        return path

    except Exception as e:
        print(f"save_transcript_file error: {e}")

        return None


# ============================================
# GET USER TRANSCRIPTS
# ============================================


async def get_user_transcripts(user_id, limit=10):

    try:
        if not db:
            return []

        async with db_lock:
            cursor = await db.execute(
                """
                SELECT

                    transcript,
                    timestamp

                FROM voice_transcripts
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            )

            rows = await cursor.fetchall()

            return rows

    except Exception as e:
        print(f"get_user_transcripts error: {e}")

        return []


# ============================================
# GET ALL TRANSCRIPTS
# ============================================


async def get_all_transcripts(limit=50):

    try:
        if not db:
            return []

        async with db_lock:
            cursor = await db.execute(
                """
                SELECT

                    username,
                    transcript,
                    timestamp

                FROM voice_transcripts
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )

            rows = await cursor.fetchall()

            return rows

    except Exception as e:
        print(f"get_all_transcripts error: {e}")

        return []


# ============================================
# DELETE USER TRANSCRIPTS
# ============================================


async def clear_user_transcripts(user_id):

    try:
        if not db:
            return False

        async with db_lock:
            await db.execute(
                """
                DELETE FROM voice_transcripts
                WHERE user_id=?
                """,
                (user_id,),
            )

            await db.commit()

        print(f"Cleared transcripts for user {user_id}")

        return True

    except Exception as e:
        print(f"clear_user_transcripts error: {e}")

        return False


# ============================================
# TRANSCRIPT COUNT
# ============================================


async def get_transcript_count():

    try:
        if not db:
            return 0

        async with db_lock:
            cursor = await db.execute(
                """
                SELECT COUNT(*)
                FROM voice_transcripts
                """
            )

            result = await cursor.fetchone()

            if not result:
                return 0

            return result[0]

    except Exception as e:
        print(f"get_transcript_count error: {e}")

        return 0
