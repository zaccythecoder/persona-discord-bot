# ============================================
# bot/utility_commands.py
# ============================================

import os
import sys
import discord
import platform
import psutil

from discord.ext import commands

from bot.config import (
    OWNER_ID,
    PREFIX
)

from bot.tracking import (
    tracked_users,
    user_messages,
    user_notes,
    user_games,
    add_note
)

# ============================================
# OWNER CHECK
# ============================================

def owner_only():

    async def predicate(ctx):

        return ctx.author.id == OWNER_ID

    return commands.check(
        predicate
    )

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

            f"Pong! `{latency}ms`"

        )

    # ========================================
    # HELP
    # ========================================

    @bot.command()
    async def help(ctx):

        commands_text = f"""
AI COMMANDS
------------
{PREFIX}persona @user
{PREFIX}ask @user question
{PREFIX}askall question

NOTES
------------
{PREFIX}note @user text
{PREFIX}notes @user
{PREFIX}clearnotes @user

TRACKING
------------
{PREFIX}games @user
{PREFIX}topwords @user
{PREFIX}stats @user
{PREFIX}scanhistory

VOICE
------------
{PREFIX}joinvc
{PREFIX}leavevc
{PREFIX}record
{PREFIX}stoprecord
{PREFIX}vcsummary
{PREFIX}vcprofile
{PREFIX}fakevc

UTILITY
------------
{PREFIX}ping
{PREFIX}info
{PREFIX}reset
{PREFIX}shutdown
"""

        embed = discord.Embed(

            title="Persona Bot Commands",

            description=f"```{commands_text}```",

            color=discord.Color.blue()

        )

        await ctx.send(
            embed=embed
        )

    # ========================================
    # INFO
    # ========================================

    @bot.command()
    async def info(ctx):

        embed = discord.Embed(

            title="Persona Bot",

            description=
                "AI-powered Discord personality bot.",

            color=discord.Color.green()

        )

        embed.add_field(

            name="Python",

            value=platform.python_version(),

            inline=True

        )

        embed.add_field(

            name="Discord.py",

            value=discord.__version__,

            inline=True

        )

        embed.add_field(

            name="Servers",

            value=len(bot.guilds),

            inline=True

        )

        await ctx.send(
            embed=embed
        )

    # ========================================
    # PERSONA NOTE
    # ========================================

    @bot.command()
    async def note(
        ctx,
        member: discord.Member,
        *,
        note_text
    ):

        add_note(
            member.id,
            note_text
        )

        await ctx.send(

            f"Added note for "
            f"{member.name}"

        )

    # ========================================
    # VIEW NOTES
    # ========================================

    @bot.command()
    async def notes(
        ctx,
        member: discord.Member
    ):

        notes_list = user_notes.get(
            member.id,
            []
        )

        if not notes_list:

            await ctx.send(
                "No notes found."
            )

            return

        output = "\n".join(
            notes_list[-20:]
        )

        await ctx.send(

            f"Notes for {member.name}:\n"
            f"```{output}```"

        )

    # ========================================
    # CLEAR NOTES
    # ========================================

    @bot.command()
    async def clearnotes(
        ctx,
        member: discord.Member
    ):

        user_notes[
            member.id
        ] = []

        await ctx.send(

            f"Cleared notes for "
            f"{member.name}"

        )

    # ========================================
    # GAMES
    # ========================================

    @bot.command()
    async def games(
        ctx,
        member: discord.Member
    ):

        games_list = user_games.get(
            member.id,
            []
        )

        if not games_list:

            await ctx.send(
                "No tracked games."
            )

            return

        text = "\n".join(
            list(set(games_list))
        )

        await ctx.send(

            f"Tracked games for "
            f"{member.name}:\n```{text}```"

        )

    # ========================================
    # TOP WORDS
    # ========================================

    @bot.command()
    async def topwords(
        ctx,
        member: discord.Member
    ):

        messages = user_messages.get(
            member.id,
            []
        )

        if not messages:

            await ctx.send(
                "No messages tracked."
            )

            return

        words = {}

        for msg in messages:

            for word in msg.lower().split():

                if len(word) < 4:

                    continue

                words[word] = (
                    words.get(word, 0)
                    + 1
                )

        top = sorted(

            words.items(),

            key=lambda x: x[1],

            reverse=True

        )[:5]

        output = "\n".join(

            f"{w} ({c})"

            for w, c in top

        )

        await ctx.send(

            f"Top words for "
            f"{member.name}:\n```{output}```"

        )

    # ========================================
    # STATS
    # ========================================

    @bot.command()
    async def stats(
        ctx,
        member: discord.Member=None
    ):

        # ====================================
        # BOT STATS
        # ====================================

        if member is None:

            cpu = psutil.cpu_percent()

            ram = psutil.virtual_memory().percent

            embed = discord.Embed(

                title="System Stats",

                color=discord.Color.orange()

            )

            embed.add_field(

                name="CPU Usage",

                value=f"{cpu}%",

                inline=True

            )

            embed.add_field(

                name="RAM Usage",

                value=f"{ram}%",

                inline=True

            )

            embed.add_field(

                name="Guilds",

                value=len(bot.guilds),

                inline=True

            )

            await ctx.send(
                embed=embed
            )

            return

        # ====================================
        # USER STATS
        # ====================================

        messages = len(

            user_messages.get(
                member.id,
                []
            )

        )

        games = len(

            set(

                user_games.get(
                    member.id,
                    []
                )

            )

        )

        notes_count = len(

            user_notes.get(
                member.id,
                []
            )

        )

        embed = discord.Embed(

            title=f"{member.name} Stats",

            color=discord.Color.blurple()

        )

        embed.add_field(

            name="Messages",

            value=messages,

            inline=True

        )

        embed.add_field(

            name="Tracked Games",

            value=games,

            inline=True

        )

        embed.add_field(

            name="Notes",

            value=notes_count,

            inline=True

        )

        await ctx.send(
            embed=embed
        )

    # ========================================
    # SCAN HISTORY
    # ========================================

    @bot.command()
    @owner_only()
    async def scanhistory(ctx):

        await ctx.send(
            "Scanning ALL server history..."
        )

        scanned = 0

        skipped = 0

        # ====================================
        # LOOP THROUGH ALL GUILDS
        # ====================================

        for guild in bot.guilds:

            await ctx.send(
                f"Scanning: {guild.name}"
            )

            for channel in guild.text_channels:

                try:

                    async for msg in channel.history(
                        limit=500
                    ):

                        if msg.author.bot:
                            continue

                        tracked_users.add(
                            msg.author.id
                        )

                        user_messages.setdefault(
                            msg.author.id,
                            []
                        ).append(
                            msg.content
                        )

                        scanned += 1

                except Exception as e:

                    print(

                        f"Failed scanning "
                        f"{channel.name}: {e}"

                    )

        await ctx.send(

            f"Finished scanning.\n\n"

            f"Messages scanned: {scanned}\n"

            f"Skipped: {skipped}"

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
            "\nRestart requested.\n"
        )

        await bot.close()

        os._exit(0)

    # ========================================
    # SHUTDOWN
    # ========================================

    @bot.command()
    @owner_only()
    async def shutdown(ctx):

        await ctx.send(
            "Shutting down bot..."
        )

        print(
            "\nShutdown requested.\n"
        )

        await bot.close()

        sys.exit(0)