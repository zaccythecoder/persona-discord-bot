# ============================================
# bot/utility_commands.py
# ============================================

import os
import sys
import platform

import discord
import psutil

from discord.ext import commands

from bot.config import OWNER_ID, PREFIX

from bot.database import (
    add_note,
    clear_notes,
    get_notes,
    get_games,
    get_top_words,
    get_user_stats,
    get_all_users,
)

from bot.tracking import scan_history

# ============================================
# OWNER CHECK
# ============================================


def owner_only():

    async def predicate(ctx):

        # ====================================
        # DM ONLY
        # ====================================

        if ctx.guild is not None:
            await ctx.send("Commands only work in DMs.")

            return False

        # ====================================
        # OWNER LOCK
        # ====================================

        if OWNER_ID != 0:
            if ctx.author.id != OWNER_ID:
                await ctx.send("You are not authorized.")

                return False

        return True

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

        latency = round(bot.latency * 1000)

        await ctx.send(f"Pong! `{latency}ms`")

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
            color=discord.Color.blue(),
        )

        await ctx.send(embed=embed)

    # ========================================
    # INFO
    # ========================================

    @bot.command()
    async def info(ctx):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        embed = discord.Embed(
            title="Persona Bot",
            description="AI-powered Discord personality bot.",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Python",
            value=platform.python_version(),
            inline=True,
        )

        embed.add_field(
            name="Discord.py",
            value=discord.__version__,
            inline=True,
        )

        embed.add_field(
            name="Servers",
            value=len(bot.guilds),
            inline=True,
        )

        embed.add_field(
            name="CPU Usage",
            value=f"{cpu}%",
            inline=True,
        )

        embed.add_field(
            name="RAM Usage",
            value=f"{ram}%",
            inline=True,
        )

        await ctx.send(embed=embed)

    # ========================================
    # NOTE
    # ========================================

    @bot.command()
    @owner_only()
    async def note(ctx, member: discord.Member, *, note_text):

        try:
            await add_note(member.id, note_text)

            await ctx.send(f"Added note for {member.name}")

        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    # ========================================
    # NOTES
    # ========================================

    @bot.command()
    @owner_only()
    async def notes(ctx, member: discord.Member):

        try:
            notes_text = await get_notes(member.id)

            if not notes_text:
                await ctx.send("No notes found.")

                return

            await ctx.send(f"Notes for {member.name}:\n```{notes_text[:1900]}```")

        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    # ========================================
    # CLEAR NOTES
    # ========================================

    @bot.command()
    @owner_only()
    async def clearnotes(ctx, member: discord.Member):

        try:
            await clear_notes(member.id)

            await ctx.send(f"Cleared notes for {member.name}")

        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    # ========================================
    # GAMES
    # ========================================

    @bot.command()
    async def games(ctx, member: discord.Member):

        try:
            games_list = await get_games(member.id)

            if not games_list:
                await ctx.send("No tracked games.")

                return

            text = "\n".join([f"{game} ({count})" for game, count in games_list])

            await ctx.send(f"Tracked games for {member.name}:\n```{text[:1900]}```")

        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    # ========================================
    # TOP WORDS
    # ========================================

    @bot.command()
    async def topwords(ctx, member: discord.Member):

        try:
            words = await get_top_words(member.id, 10)

            if not words:
                await ctx.send("No tracked words.")

                return

            output = "\n".join([f"{word} ({count})" for word, count in words])

            await ctx.send(f"Top words for {member.name}:\n```{output}```")

        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    # ========================================
    # STATS
    # ========================================

    @bot.command()
    async def stats(ctx, member: discord.Member = None):

        try:
            # ====================================
            # BOT STATS
            # ====================================

            if member is None:
                embed = discord.Embed(
                    title="System Stats",
                    color=discord.Color.orange(),
                )

                embed.add_field(
                    name="Guilds",
                    value=len(bot.guilds),
                    inline=True,
                )

                embed.add_field(
                    name="Users",
                    value=len(await get_all_users()),
                    inline=True,
                )

                embed.add_field(
                    name="Latency",
                    value=f"{round(bot.latency * 1000)}ms",
                    inline=True,
                )

                await ctx.send(embed=embed)

                return

            # ====================================
            # USER STATS
            # ====================================

            stats_data = await get_user_stats(member.id)

            if not stats_data:
                await ctx.send("No tracked data.")

                return

            embed = discord.Embed(
                title=f"{member.name} Stats",
                color=discord.Color.blurple(),
            )

            embed.add_field(
                name="Messages",
                value=stats_data[2],
                inline=True,
            )

            embed.add_field(
                name="Words",
                value=stats_data[3],
                inline=True,
            )

            embed.add_field(
                name="Sentiment",
                value=round(stats_data[4], 2),
                inline=True,
            )

            embed.add_field(
                name="Questions",
                value=stats_data[9],
                inline=True,
            )

            embed.add_field(
                name="Replies",
                value=stats_data[10],
                inline=True,
            )

            embed.add_field(
                name="Emojis",
                value=stats_data[8],
                inline=True,
            )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error:\n```{e}```")

    # ========================================
    # SCAN HISTORY
    # ========================================

    @bot.command()
    @owner_only()
    async def scanhistory(ctx):

        try:
            await scan_history(ctx)

        except Exception as e:
            await ctx.send(f"Scan failed:\n```{e}```")

    # ========================================
    # RESET
    # ========================================

    @bot.command()
    @owner_only()
    async def reset(ctx):

        await ctx.send("Restarting bot...")

        print("\nRestart requested.\n")

        await bot.close()

        os._exit(0)

    # ========================================
    # SHUTDOWN
    # ========================================

    @bot.command()
    @owner_only()
    async def shutdown(ctx):

        await ctx.send("Shutting down bot...")

        print("\nShutdown requested.\n")

        await bot.close()

        sys.exit(0)
