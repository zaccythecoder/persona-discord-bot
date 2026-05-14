# ============================================
# bot/utility_commands.py
# ============================================

import os
import discord
from discord.ext import commands

from bot.config import (
    OWNER_ID
)

from bot.database import (
    get_user_stats,
    get_top_words,
    get_games,
    add_note,
    get_notes,
    clear_notes
)

from bot.tracking import (
    scan_history
)

# ============================================
# OWNER CHECK
# ============================================

def owner_only():

    async def predicate(ctx):

        return ctx.author.id == OWNER_ID

    return commands.check(predicate)

# ============================================
# SETUP
# ============================================

def setup(bot):

    # ========================================
    # PING
    # ========================================

    @bot.command()
    async def ping(ctx):

        latency = round(
            bot.latency * 1000
        )

        await ctx.send(
            f"Pong! {latency}ms"
        )

    # ========================================
    # HELP
    # ========================================

    @bot.command()
    @owner_only()
    async def help(ctx):

        commands_text = """

=== PERSONA BOT COMMANDS ===

GENERAL:
!ping
!help

AI:
!persona @user
!ask @user <question>
!askall <question>

STATS:
!stats @user
!topwords @user
!games @user

NOTES:
!note @user <note>
!notes @user
!clearnotes @user

TRACKING:
!scanhistory

UTILITY:
!reset

"""

        await ctx.send(
            f"```{commands_text}```"
        )

    # ========================================
    # STATS
    # ========================================

    @bot.command()
    @owner_only()
    async def stats(
        ctx,
        member: discord.Member
    ):

        stats = await get_user_stats(
            member.id
        )

        if not stats:

            await ctx.send(
                "No stats found."
            )

            return

        text = f"""

Username: {stats[1]}

Messages: {stats[2]}

Words: {stats[3]}

Sentiment: {round(stats[4], 2)}

Morning msgs: {stats[5]}
Afternoon msgs: {stats[6]}
Night msgs: {stats[7]}

Emojis: {stats[8]}
Questions: {stats[9]}
Replies: {stats[10]}

"""

        await ctx.send(
            f"```{text}```"
        )

    # ========================================
    # TOP WORDS
    # ========================================

    @bot.command()
    @owner_only()
    async def topwords(
        ctx,
        member: discord.Member
    ):

        words = await get_top_words(
            member.id,
            10
        )

        if not words:

            await ctx.send(
                "No word data found."
            )

            return

        text = "\n".join(

            [
                f"{word} — {count}"

                for word, count in words
            ]

        )

        await ctx.send(
            f"```Top Words for {member}:\n\n{text}```"
        )

    # ========================================
    # GAMES
    # ========================================

    @bot.command()
    @owner_only()
    async def games(
        ctx,
        member: discord.Member
    ):

        games_list = await get_games(
            member.id
        )

        if not games_list:

            await ctx.send(
                "No games tracked."
            )

            return

        text = "\n".join(

            [
                f"{game} — {count}"

                for game, count in games_list
            ]

        )

        await ctx.send(
            f"```Games for {member}:\n\n{text}```"
        )

    # ========================================
    # ADD NOTE
    # ========================================

    @bot.command()
    @owner_only()
    async def note(
        ctx,
        member: discord.Member,
        *,
        note_text
    ):

        await add_note(
            member.id,
            note_text
        )

        await ctx.send(
            "Note added."
        )

    # ========================================
    # GET NOTES
    # ========================================

    @bot.command()
    @owner_only()
    async def notes(
        ctx,
        member: discord.Member
    ):

        notes_text = await get_notes(
            member.id
        )

        if not notes_text:

            notes_text = (
                "No notes."
            )

        await ctx.send(
            f"```{notes_text}```"
        )

    # ========================================
    # CLEAR NOTES
    # ========================================

    @bot.command()
    @owner_only()
    async def clearnotes(
        ctx,
        member: discord.Member
    ):

        await clear_notes(
            member.id
        )

        await ctx.send(
            "Notes cleared."
        )

    # ========================================
    # SCAN HISTORY
    # ========================================

    @bot.command()
    @owner_only()
    async def scanhistory(ctx):

        await scan_history(
            ctx
        )

    # ========================================
    # RESET
    # ========================================

    @bot.command()
    @owner_only()
    async def reset(ctx):

        await ctx.send(
            "Restarting bot..."
        )

        print(
            "\nRestart command received.\n"
        )

        os._exit(0)