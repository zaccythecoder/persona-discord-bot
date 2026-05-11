# ================================
# bot.py
# ================================

import os
import discord
from discord.ext import commands
import aiosqlite
import asyncio
import re
from datetime import datetime
from textblob import TextBlob
from groq import Groq
from collections import Counter

# =========================================================
# CONFIG
# =========================================================

def load_config():

    config = {}

    with open(
        "bot.config",
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" in line:

                key, value = line.split(
                    "=",
                    1
                )

                config[
                    key.strip()
                ] = value.strip()

    return config

config = {}

if os.path.exists("bot.config"):
    config = load_config()

TOKEN = os.getenv(
    "TOKEN",
    config.get("TOKEN")
)

PREFIX = os.getenv(
    "PREFIX",
    config.get(
        "PREFIX",
        "!"
    )
)

GROQ_KEY = os.getenv(
    "GROQ_KEY",
    config.get("GROQ_KEY")
)

DB_NAME = os.getenv(
    "DATABASE",
    config.get(
        "DATABASE",
        "persona.db"
    )
)

MODEL_NAME = os.getenv(
    "MODEL",
    config.get(
        "MODEL",
        "llama-3.3-70b-versatile"
    )
)

OWNER_ID = 1449536595060330588

# =========================================================
# GROQ
# =========================================================

groq_client = Groq(
    api_key=GROQ_KEY
)

# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents
)

# =========================================================
# DATABASE
# =========================================================

db = None

db_lock = asyncio.Lock()

# =========================================================
# TABLES
# =========================================================

CREATE_USERS_TABLE = """
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

CREATE_WORDS_TABLE = """
CREATE TABLE IF NOT EXISTS words (
    user_id INTEGER,
    word TEXT,
    count INTEGER,
    PRIMARY KEY (user_id, word)
)
"""

CREATE_MESSAGE_TABLE = """
CREATE TABLE IF NOT EXISTS message_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER UNIQUE,
    user_id INTEGER,
    content TEXT
)
"""

CREATE_GAMES_TABLE = """
CREATE TABLE IF NOT EXISTS games (
    user_id INTEGER,
    game_name TEXT,
    first_seen TEXT,
    last_seen TEXT,
    times_seen INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, game_name)
)
"""

CREATE_SCANNED_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS scanned_messages (
    message_id INTEGER PRIMARY KEY
)
"""

# =========================================================
# HELPERS
# =========================================================

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "]+",
    flags=re.UNICODE,
)

def clean_words(text):

    return re.findall(
        r"\b[a-zA-Z']+\b",
        text.lower()
    )

def get_time_bucket(hour=None):

    if hour is None:
        hour = datetime.now().hour

    if 5 <= hour < 12:
        return "morning_msgs"

    elif 12 <= hour < 18:
        return "afternoon_msgs"

    else:
        return "night_msgs"

def calculate_sentiment(text):

    try:

        return TextBlob(
            text
        ).sentiment.polarity

    except:
        return 0

# =========================================================
# DATABASE INIT
# =========================================================

async def init_db():

    global db

    if db is not None:
        return

    db = await aiosqlite.connect(
        DB_NAME,
        timeout=60
    )

    await db.execute(
        "PRAGMA journal_mode=WAL;"
    )

    await db.execute(
        "PRAGMA synchronous=NORMAL;"
    )

    await db.execute(
        "PRAGMA temp_store=MEMORY;"
    )

    await db.execute(
        "PRAGMA busy_timeout=60000;"
    )

    await db.execute(
        CREATE_USERS_TABLE
    )

    await db.execute(
        CREATE_WORDS_TABLE
    )

    await db.execute(
        CREATE_MESSAGE_TABLE
    )

    await db.execute(
        CREATE_GAMES_TABLE
    )

    await db.execute(
        CREATE_SCANNED_MESSAGES_TABLE
    )

    await db.commit()

    print(
        "Database initialized."
    )

# =========================================================
# OWNER CHECK
# =========================================================

async def owner_dm_only(ctx):

    return (
        isinstance(
            ctx.channel,
            discord.DMChannel
        )
        and ctx.author.id == OWNER_ID
    )

# =========================================================
# USER ENSURE
# =========================================================

async def ensure_user(user):

    if db is None:
        return

    async with db_lock:

        await db.execute(
            """
            INSERT OR IGNORE INTO users(
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

# =========================================================
# GAME LOGGER
# =========================================================

async def log_game(
    user_id,
    game_name
):

    if db is None:
        return

    if not game_name:
        return

    now = datetime.utcnow().isoformat()

    async with db_lock:

        await db.execute(
            """
            INSERT INTO games(
                user_id,
                game_name,
                first_seen,
                last_seen,
                times_seen
            )
            VALUES (?, ?, ?, ?, 1)

            ON CONFLICT(user_id, game_name)
            DO UPDATE SET
                last_seen=excluded.last_seen,
                times_seen=times_seen+1
            """,
            (
                user_id,
                game_name,
                now,
                now
            )
        )

        await db.commit()

# =========================================================
# MESSAGE PROCESSOR
# =========================================================

async def process_message_data(message):

    if message.author.bot:
        return

    if db is None:
        return

    text = message.content

    if not text:
        return

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT message_id
            FROM scanned_messages
            WHERE message_id=?
            """,
            (
                message.id,
            )
        )

        exists = await cursor.fetchone()

    if exists:
        return

    await ensure_user(
        message.author
    )

    words = clean_words(text)

    sentiment = calculate_sentiment(
        text
    )

    emoji_count = len(
        EMOJI_PATTERN.findall(text)
    )

    questions = text.count("?")

    is_reply = (
        message.reference is not None
    )

    bucket = get_time_bucket(
        message.created_at.hour
    )

    word_counts = Counter([
        w for w in words
        if len(w) > 3
    ])

    async with db_lock:

        cursor = await db.execute(
            """
            SELECT total_messages,
                   avg_sentiment
            FROM users
            WHERE user_id=?
            """,
            (
                message.author.id,
            )
        )

        current = await cursor.fetchone()

        if not current:
            return

        total_msgs = current[0]
        old_sentiment = current[1]

        new_avg = (
            (
                old_sentiment
                * total_msgs
            )
            + sentiment
        ) / (total_msgs + 1)

        await db.execute(
            f"""
            UPDATE users
            SET
                username=?,
                total_messages=total_messages+1,
                total_words=total_words+?,
                avg_sentiment=?,
                emojis_used=emojis_used+?,
                questions_asked=questions_asked+?,
                replies_sent=replies_sent+?,
                {bucket}={bucket}+1
            WHERE user_id=?
            """,
            (
                str(message.author),
                len(words),
                new_avg,
                emoji_count,
                questions,
                int(is_reply),
                message.author.id
            )
        )

        await db.execute(
            """
            INSERT OR IGNORE INTO message_history(
                message_id,
                user_id,
                content
            )
            VALUES (?, ?, ?)
            """,
            (
                message.id,
                message.author.id,
                text[:1000]
            )
        )

        for word, count in word_counts.items():

            await db.execute(
                """
                INSERT INTO words(
                    user_id,
                    word,
                    count
                )
                VALUES (?, ?, ?)

                ON CONFLICT(user_id, word)
                DO UPDATE SET
                count=count+excluded.count
                """,
                (
                    message.author.id,
                    word,
                    count
                )
            )

        await db.execute(
            """
            INSERT OR IGNORE INTO scanned_messages(
                message_id
            )
            VALUES (?)
            """,
            (
                message.id,
            )
        )

        await db.commit()