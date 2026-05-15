# ============================================
# bot/database.py
# ============================================

import os
import aiosqlite
import asyncio

from datetime import datetime

from bot.config import DATABASE

# ============================================
# DATABASE PATH
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    DATABASE
)

# ============================================
# AUTO CREATE FOLDER
# ============================================

database_folder = os.path.dirname(
    DATABASE_PATH
)

if database_folder:

    os.makedirs(
        database_folder,
        exist_ok=True
    )

# ============================================
# DATABASE GLOBALS
# ============================================

db = None

db_lock = asyncio.Lock()

# ============================================
# INIT DATABASE
# ============================================

async def init_db():

    global db

    if db:
        return

    print(
        "\n===================================="
    )

    print(
        "INITIALIZING DATABASE"
    )

    print(
        "===================================="
    )

    print(
        f"Using database:\n{DATABASE_PATH}\n"
    )

    # ========================================
    # CONNECT
    # ========================================

    db = await aiosqlite.connect(
        DATABASE_PATH
    )

    print(
        "SQLite connected."
    )

    # ========================================
    # SQLITE SETTINGS
    # ========================================

    await db.execute(
        "PRAGMA journal_mode=WAL"
    )

    await db.execute(
        "PRAGMA synchronous=NORMAL"
    )

    # ========================================
    # USERS TABLE
    # ========================================

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            user_id INTEGER PRIMARY KEY,

            username TEXT,

            total_messages INTEGER DEFAULT 0,

            total_words INTEGER DEFAULT 0,

            avg_sentiment REAL DEFAULT 0,

            morning_msgs INTEGER DEFAULT 0,

            afternoon_msgs INTEGER DEFAULT 0,

            night_msgs INTEGER DEFAULT 0,

            emojis_used INTEGER DEFAULT 0,

            questions_asked INTEGER DEFAULT 0,

            replies_sent INTEGER DEFAULT 0,

            manual_notes TEXT DEFAULT ''
        )
        """
    )

    # ========================================
    # WORD TRACKING
    # ========================================

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS words (

            user_id INTEGER,

            word TEXT,

            count INTEGER DEFAULT 0,

            PRIMARY KEY (
                user_id,
                word
            )
        )
        """
    )

    # ========================================
    # MESSAGE HISTORY
    # ========================================

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS message_history (

            message_id INTEGER PRIMARY KEY,

            user_id INTEGER,

            username TEXT,

            content TEXT,

            timestamp TEXT,

            channel_id INTEGER,

            guild_id INTEGER
        )
        """
    )

    # ========================================
    # GAMES TABLE
    # ========================================

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS games (

            user_id INTEGER,

            game_name TEXT,

            first_seen TEXT,

            last_seen TEXT,

            times_seen INTEGER DEFAULT 1,

            PRIMARY KEY (
                user_id,
                game_name
            )
        )
        """
    )

    # ========================================
    # SCANNED MESSAGES
    # ========================================

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS scanned_messages (

            message_id INTEGER PRIMARY KEY
        )
        """
    )

    # ========================================
    # MIGRATIONS
    # ========================================

    try:

        await db.execute(
            """
            ALTER TABLE users
            ADD COLUMN manual_notes TEXT DEFAULT ''
            """
        )

        print(
            "Migration applied."
        )

    except:

        pass

    # ========================================
    # COMMIT
    # ========================================

    await db.commit()

    print(
        "Tables committed."
    )

    # ========================================
    # VERIFY FILE EXISTS
    # ========================================

    if os.path.exists(
        DATABASE_PATH
    ):

        print(
            "\nDatabase file created successfully."
        )

    else:

        print(
            "\nWARNING: Database file missing."
        )

    print(
        "Database initialized successfully."
    )

    print(
        "====================================\n"
    )

# ============================================
# ENSURE USER EXISTS
# ============================================

async def ensure_user(user):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id=?
            """,
            (
                user.id,
            )
        )

        exists = await cursor.fetchone()

        if not exists:

            await db.execute(
                """
                INSERT INTO users (

                    user_id,
                    username

                )

                VALUES (?, ?)
                """,
                (
                    user.id,
                    str(user)
                )
            )

            await db.commit()

# ============================================
# SAVE MESSAGE
# ============================================

async def save_message(
    message
):

    async with db_lock:

        await db.execute(
            """
            INSERT OR IGNORE INTO message_history (

                message_id,
                user_id,
                username,
                content,
                timestamp,
                channel_id,
                guild_id

            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message.id,
                message.author.id,
                str(message.author),
                message.content,
                str(message.created_at),
                message.channel.id,
                message.guild.id
                if message.guild
                else 0
            )
        )

        await db.commit()

# ============================================
# CHECK IF MESSAGE SCANNED
# ============================================

async def is_message_scanned(
    message_id
):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT message_id
            FROM scanned_messages
            WHERE message_id=?
            """,
            (
                message_id,
            )
        )

        exists = await cursor.fetchone()

        return bool(exists)

# ============================================
# MARK MESSAGE SCANNED
# ============================================

async def mark_message_scanned(
    message_id
):

    async with db_lock:

        await db.execute(
            """
            INSERT OR IGNORE INTO scanned_messages (

                message_id

            )

            VALUES (?)
            """,
            (
                message_id,
            )
        )

        await db.commit()

# ============================================
# UPDATE USER STATS
# ============================================

async def update_user_stats(

    user,
    word_count,
    sentiment,
    morning,
    afternoon,
    night,
    emojis,
    questions,
    replies

):

    async with db_lock:

        await db.execute(
            """
            UPDATE users
            SET

                username=?,

                total_messages=total_messages+1,

                total_words=total_words+?,

                avg_sentiment=
                    (
                        avg_sentiment
                        +
                        ?
                    ) / 2,

                morning_msgs=morning_msgs+?,

                afternoon_msgs=afternoon_msgs+?,

                night_msgs=night_msgs+?,

                emojis_used=emojis_used+?,

                questions_asked=questions_asked+?,

                replies_sent=replies_sent+?

            WHERE user_id=?
            """,
            (
                str(user),

                word_count,

                sentiment,

                morning,

                afternoon,

                night,

                emojis,

                questions,

                replies,

                user.id
            )
        )

        await db.commit()

# ============================================
# ADD WORD
# ============================================

async def add_word(
    user_id,
    word
):

    async with db_lock:

        await db.execute(
            """
            INSERT INTO words (

                user_id,
                word,
                count

            )

            VALUES (?, ?, 1)

            ON CONFLICT(user_id, word)

            DO UPDATE SET

                count=count+1
            """,
            (
                user_id,
                word
            )
        )

        await db.commit()

# ============================================
# LOG GAME
# ============================================

async def log_game(
    user_id,
    game_name
):

    if not game_name:
        return

    now = str(
        datetime.utcnow()
    )

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT times_seen
            FROM games
            WHERE user_id=?
            AND game_name=?
            """,
            (
                user_id,
                game_name
            )
        )

        existing = await cursor.fetchone()

        if existing:

            await db.execute(
                """
                UPDATE games
                SET

                    times_seen=times_seen+1,

                    last_seen=?

                WHERE user_id=?
                AND game_name=?
                """,
                (
                    now,
                    user_id,
                    game_name
                )
            )

        else:

            await db.execute(
                """
                INSERT INTO games (

                    user_id,
                    game_name,
                    first_seen,
                    last_seen,
                    times_seen

                )

                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    game_name,
                    now,
                    now,
                    1
                )
            )

        await db.commit()

# ============================================
# GET USER STATS
# ============================================

async def get_user_stats(
    user_id
):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT *
            FROM users
            WHERE user_id=?
            """,
            (
                user_id,
            )
        )

        return await cursor.fetchone()

# ============================================
# GET TOP WORDS
# ============================================

async def get_top_words(
    user_id,
    limit=5
):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT word, count
            FROM words
            WHERE user_id=?
            ORDER BY count DESC
            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        )

        return await cursor.fetchall()

# ============================================
# GET GAMES
# ============================================

async def get_games(
    user_id
):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT

                game_name,
                times_seen

            FROM games
            WHERE user_id=?
            ORDER BY times_seen DESC
            """,
            (
                user_id,
            )
        )

        return await cursor.fetchall()

# ============================================
# NOTES
# ============================================

async def add_note(
    user_id,
    note
):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT manual_notes
            FROM users
            WHERE user_id=?
            """,
            (
                user_id,
            )
        )

        existing = await cursor.fetchone()

        old_notes = ""

        if existing and existing[0]:
            old_notes = existing[0]

        new_notes = (
            old_notes
            + "\n"
            + note
        ).strip()

        await db.execute(
            """
            UPDATE users
            SET manual_notes=?
            WHERE user_id=?
            """,
            (
                new_notes,
                user_id
            )
        )

        await db.commit()

# ============================================
# GET NOTES
# ============================================

async def get_notes(
    user_id
):

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT manual_notes
            FROM users
            WHERE user_id=?
            """,
            (
                user_id,
            )
        )

        result = await cursor.fetchone()

        if not result:
            return ""

        return result[0] or ""

# ============================================
# CLEAR NOTES
# ============================================

async def clear_notes(
    user_id
):

    async with db_lock:

        await db.execute(
            """
            UPDATE users
            SET manual_notes=''
            WHERE user_id=?
            """,
            (
                user_id,
            )
        )

        await db.commit()

# ============================================
# GET ALL USERS
# ============================================

async def get_all_users():

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT

                user_id,
                username,
                total_messages,
                total_words

            FROM users
            ORDER BY total_messages DESC
            """
        )

        return await cursor.fetchall()