# ============================================
# bot/tracking.py
# ============================================

import asyncio
import re

from datetime import datetime

import discord

from discord.ext import tasks
from textblob import TextBlob

from bot.database import (
    add_word,
    ensure_user,
    is_message_scanned,
    log_game,
    mark_message_scanned,
    save_message,
    update_user_stats,
)

# ============================================
# TRACKED USERS CACHE
# ============================================

tracked_users = set()

# ============================================
# WORD EXTRACTION
# ============================================


def extract_words(text):

    return re.findall(r"\b[a-zA-Z']+\b", text.lower())


# ============================================
# MESSAGE PROCESSING
# ============================================


async def process_message_data(message):

    # ========================================
    # IGNORE BOTS
    # ========================================

    if message.author.bot:
        return

    # ========================================
    # IGNORE DMS
    # ========================================

    if not message.guild:
        return

    # ========================================
    # IGNORE EMPTY
    # ========================================

    if not message.content:
        return

    # ========================================
    # DUPLICATE CHECK
    # ========================================

    already_scanned = await is_message_scanned(message.id)

    if already_scanned:
        return

    # ========================================
    # ENSURE USER EXISTS
    # ========================================

    await ensure_user(message.author)

    tracked_users.add(message.author.id)

    content = message.content or ""

    # ========================================
    # WORD ANALYSIS
    # ========================================

    words = extract_words(content)

    word_count = len(words)

    # ========================================
    # SENTIMENT
    # ========================================

    try:
        sentiment = TextBlob(content).sentiment.polarity

    except Exception:
        sentiment = 0

    # ========================================
    # EMOJIS / QUESTIONS / REPLIES
    # ========================================

    emojis = len(re.findall(r":[a-zA-Z0-9_]+:", content))

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

    try:
        await save_message(message)

    except Exception as e:
        print(f"save_message error: {e}")

    # ========================================
    # UPDATE USER STATS
    # ========================================

    try:
        await update_user_stats(
            user=message.author,
            word_count=word_count,
            sentiment=sentiment,
            morning=morning,
            afternoon=afternoon,
            night=night,
            emojis=emojis,
            questions=questions,
            replies=replies,
        )

    except Exception as e:
        print(f"update_user_stats error: {e}")

    # ========================================
    # SAVE WORDS
    # ========================================

    try:
        for word in words:
            await add_word(message.author.id, word)

    except Exception as e:
        print(f"add_word error: {e}")

    # ========================================
    # MARK SCANNED
    # ========================================

    try:
        await mark_message_scanned(message.id)

    except Exception as e:
        print(f"mark_message_scanned error: {e}")


# ============================================
# GAME TRACKER
# ============================================


async def track_games(member):

    if member.bot:
        return

    if not member.activities:
        return

    for activity in member.activities:
        try:
            if isinstance(activity, discord.Game):
                if activity.name:
                    await log_game(member.id, activity.name)

        except Exception as e:
            print(f"Game tracking error: {e}")


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
                if guild is None:
                    continue

                for member in guild.members:
                    try:
                        await track_games(member)

                    except Exception as e:
                        print(f"Game tracking error: {e}")

        except Exception as e:
            print(f"Game loop crashed: {e}")

    game_tracker_loop.start()

    print("Game tracker loop started.")


# ============================================
# HISTORY SCANNER
# ============================================


async def scan_history(ctx):

    scanned = 0

    skipped = 0

    await ctx.send("Starting history scan...")

    for guild in ctx.bot.guilds:
        if guild is None:
            continue

        try:
            channels = guild.text_channels

        except Exception as e:
            print(f"Guild channel error: {e}")

            continue

        for channel in channels:
            try:
                async for message in channel.history(limit=None, oldest_first=True):
                    if message.author.bot:
                        continue

                    exists = await is_message_scanned(message.id)

                    if exists:
                        skipped += 1

                        continue

                    await process_message_data(message)

                    scanned += 1

                    # ============================
                    # PREVENT LOCKUPS
                    # ============================

                    if scanned % 50 == 0:
                        print(f"Scanned {scanned} messages...")

                        await asyncio.sleep(0)

            except Exception as e:
                print(f"Failed scanning #{channel}: {e}")

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
    # MESSAGE LISTENER
    # ========================================

    @bot.listen()
    async def on_message(message):

        try:
            await process_message_data(message)

        except Exception as e:
            print(f"Message tracking error: {e}")

    # ========================================
    # READY EVENT
    # ========================================

    @bot.event
    async def on_ready():

        print("tracking.py ready.")

        start_game_tracker(bot)
