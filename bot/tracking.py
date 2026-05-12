# ============================================
# bot/tracking.py
# ============================================

import re
import asyncio
from datetime import datetime

import discord
from textblob import TextBlob
from discord.ext import tasks

from bot.database import (
    ensure_user,
    save_message,
    is_message_scanned,
    mark_message_scanned,
    update_user_stats,
    add_word,
    log_game
)

# ============================================
# WORD EXTRACTION
# ============================================

def extract_words(text):

    return re.findall(
        r"\b[a-zA-Z']+\b",
        text.lower()
    )

# ============================================
# MESSAGE PROCESSING
# ============================================

async def process_message_data(
    message
):

    if message.author.bot:
        return

    # ========================================
    # DUPLICATE CHECK
    # ========================================

    already_scanned = await is_message_scanned(
        message.id
    )

    if already_scanned:
        return

    # ========================================
    # ENSURE USER EXISTS
    # ========================================

    await ensure_user(
        message.author
    )

    content = (
        message.content or ""
    )

    # ========================================
    # WORD ANALYSIS
    # ========================================

    words = extract_words(
        content
    )

    word_count = len(words)

    # ========================================
    # SENTIMENT
    # ========================================

    sentiment = (
        TextBlob(content)
        .sentiment
        .polarity
    )

    # ========================================
    # EMOJIS / QUESTIONS / REPLIES
    # ========================================

    emojis = len(
        re.findall(
            r":[a-zA-Z0-9_]+:",
            content
        )
    )

    questions = content.count("?")

    replies = 1 if message.reference else 0

    # ========================================
    # TIME OF DAY
    # ========================================

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

    # ========================================
    # SAVE MESSAGE
    # ========================================

    await save_message(
        message
    )

    # ========================================
    # UPDATE USER STATS
    # ========================================

    await update_user_stats(

        user=message.author,

        word_count=word_count,

        sentiment=sentiment,

        morning=morning,

        afternoon=afternoon,

        night=night,

        emojis=emojis,

        questions=questions,

        replies=replies

    )

    # ========================================
    # SAVE WORDS
    # ========================================

    for word in words:

        await add_word(
            message.author.id,
            word
        )

    # ========================================
    # MARK SCANNED
    # ========================================

    await mark_message_scanned(
        message.id
    )

# ============================================
# GAME TRACKER
# ============================================

async def track_games(
    member
):

    if not member.activities:
        return

    for activity in member.activities:

        if isinstance(
            activity,
            discord.Game
        ):

            await log_game(
                member.id,
                activity.name
            )

# ============================================
# AUTO GAME LOOP
# ============================================

game_loop_running = False

def start_game_tracker(bot):

    global game_loop_running

    if game_loop_running:
        return

    game_loop_running = True

    @tasks.loop(minutes=5)
    async def game_tracker_loop():

        try:

            for guild in bot.guilds:

                for member in guild.members:

                    try:

                        await track_games(
                            member
                        )

                    except Exception as e:

                        print(
                            f"Game tracking error: {e}"
                        )

        except Exception as e:

            print(
                f"Game loop crashed: {e}"
            )

    game_tracker_loop.start()

    print(
        "Game tracker loop started."
    )

# ============================================
# HISTORY SCANNER
# ============================================

async def scan_history(
    ctx
):

    scanned = 0

    skipped = 0

    await ctx.send(
        "Starting history scan..."
    )

    for guild in ctx.bot.guilds:

        for channel in guild.text_channels:

            try:

                async for message in channel.history(
                    limit=None,
                    oldest_first=True
                ):

                    if message.author.bot:
                        continue

                    exists = await is_message_scanned(
                        message.id
                    )

                    if exists:

                        skipped += 1

                        continue

                    await process_message_data(
                        message
                    )

                    scanned += 1

                    if scanned % 100 == 0:

                        print(
                            f"Scanned {scanned} messages..."
                        )

                        await asyncio.sleep(
                            0.2
                        )

            except Exception as e:

                print(
                    f"Failed scanning #{channel}: {e}"
                )

    await ctx.send(

        f"History scan complete.\n\n"

        f"New messages scanned: {scanned}\n"

        f"Skipped existing: {skipped}"

    )

# ============================================
# SETUP
# ============================================

def setup(bot):

    # ========================================
    # MESSAGE EVENT
    # ========================================

    @bot.event
    async def on_message(message):

        try:

            await process_message_data(
                message
            )

        except Exception as e:

            print(
                f"Message tracking error: {e}"
            )

        await bot.process_commands(
            message
        )

    # ========================================
    # READY EVENT
    # ========================================

    @bot.event
    async def on_ready():

        print(
            "tracking.py ready."
        )

        start_game_tracker(bot)