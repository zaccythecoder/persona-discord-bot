# ================================
# bot.py
# ================================

import discord
from discord.ext import commands
import aiosqlite
import asyncio
import os
import re
from datetime import datetime
from textblob import TextBlob
from groq import Groq

# =========================================================
# ENV VARIABLES
# =========================================================

TOKEN = os.getenv("TOKEN")

PREFIX = os.getenv("PREFIX", "!")

DATABASE = os.getenv(
    "DATABASE",
    "persona.db"
)

MODEL_NAME = os.getenv(
    "MODEL",
    "llama-3.3-70b-versatile"
)

# =========================================================
# GROQ KEY FIX
# =========================================================

GROQ_KEY = (
    os.getenv("GROQ_KEY")
    or os.getenv("GROQ_API_KEY")
)

if not GROQ_KEY:

    raise Exception(
        "Missing GROQ_KEY / GROQ_API_KEY environment variable"
    )

groq_client = Groq(
    api_key=GROQ_KEY
)

# =========================================================
# DISCORD BOT
# =========================================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# =========================================================
# DATABASE
# =========================================================

db = None

db_lock = asyncio.Lock()

# =========================================================
# OWNER DM CHECK
# =========================================================

OWNER_ID = 1449536595060330588

async def owner_dm_only(ctx):

    if not isinstance(
        ctx.channel,
        discord.DMChannel
    ):
        return False

    return ctx.author.id == OWNER_ID

# =========================================================
# INIT DB
# =========================================================

async def init_db():

    global db

    if db:
        return

    db = await aiosqlite.connect(
        DATABASE
    )

    await db.execute(
        "PRAGMA journal_mode=WAL"
    )

    await db.execute(
        "PRAGMA synchronous=NORMAL"
    )

    # =====================================================
    # USERS
    # =====================================================

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

    # =====================================================
    # WORDS
    # =====================================================

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

    # =====================================================
    # MESSAGE HISTORY
    # =====================================================

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

    # =====================================================
    # GAMES
    # =====================================================

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

    # =====================================================
    # SCANNED MESSAGES
    # =====================================================

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS scanned_messages (

            message_id INTEGER PRIMARY KEY
        )
        """
    )

    # =====================================================
    # MIGRATIONS
    # =====================================================

    try:

        await db.execute(
            """
            ALTER TABLE users
            ADD COLUMN manual_notes TEXT DEFAULT ''
            """
        )

    except:
        pass

    await db.commit()

    print(
        "Database initialized."
    )

# =========================================================
# ENSURE USER
# =========================================================

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

# =========================================================
# LOG GAME
# =========================================================

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

# =========================================================
# WORD PARSER
# =========================================================

def extract_words(text):

    return re.findall(
        r"\b[a-zA-Z']+\b",
        text.lower()
    )

# =========================================================
# PROCESS MESSAGE
# =========================================================

async def process_message_data(message):

    if message.author.bot:
        return

    await ensure_user(
        message.author
    )

    content = (
        message.content or ""
    )

    words = extract_words(
        content
    )

    word_count = len(words)

    emojis = len(
        re.findall(
            r":[a-zA-Z0-9_]+:",
            content
        )
    )

    questions = content.count("?")

    replies = 1 if message.reference else 0

    sentiment = (
        TextBlob(content)
        .sentiment
        .polarity
    )

    hour = datetime.utcnow().hour

    morning = 0
    afternoon = 0
    night = 0

    if 5 <= hour < 12:
        morning = 1

    elif 12 <= hour < 18:
        afternoon = 1

    else:
        night = 1

    async with db_lock:

        # =================================================
        # DUPLICATE CHECK
        # =================================================

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

        # =================================================
        # MARK SCANNED
        # =================================================

        await db.execute(
            """
            INSERT OR IGNORE INTO scanned_messages (

                message_id

            )

            VALUES (?)
            """,
            (
                message.id,
            )
        )

        # =================================================
        # SAVE HISTORY
        # =================================================

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
                content,
                str(message.created_at),
                message.channel.id,
                message.guild.id
                if message.guild
                else 0
            )
        )

        # =================================================
        # UPDATE USER STATS
        # =================================================

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
                str(message.author),

                word_count,

                sentiment,

                morning,

                afternoon,

                night,

                emojis,

                questions,

                replies,

                message.author.id
            )
        )
        
        
@bot.command()
@commands.check(owner_dm_only)
async def reset(ctx):

    await ctx.send(
        "Restarting bot..."
    )

    print(
        "\nRestart command received.\n"
    )

    os._exit(0)
    
        # =================================================
        # WORD TRACKING
        # =================================================

        for word in words:

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
                    message.author.id,
                    word
                )
            )

        await db.commit()

# =========================================================
# BASIC COMMANDS
# =========================================================

@bot.command()
@commands.check(owner_dm_only)
async def ping(ctx):

    await ctx.send(
        "Pong!"
    )

# =========================================================
# HELP COMMAND
# =========================================================

@bot.command()
@commands.check(owner_dm_only)
async def help(ctx):

    commands_text = """
COMMANDS

!persona @user
Generate AI personality analysis

!ask @user question
Ask AI about a user

!askall question
Analyze whole server

!note @user text
Add manual note

!notes @user
View notes

!clearnotes @user
Clear notes

!games @user
Show tracked games

!topwords @user
Show top 5 words

!stats @user
Show raw stats

!scanhistory
Scan all channel history

!ping
Ping test
"""

    await ctx.send(
        f"```{commands_text}```"
    )