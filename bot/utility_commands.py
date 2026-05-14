# ============================================
# bot/utility_commands.py
# ============================================

import os
import sys
import discord
import platform
import psutil

from datetime import datetime

from discord.ext import commands

from bot.config import (
    OWNER_ID,
    PREFIX
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
{PREFIX}ping
{PREFIX}help
{PREFIX}info
{PREFIX}stats

{PREFIX}reset
{PREFIX}shutdown

VOICE:
{PREFIX}joinvc
{PREFIX}leavevc
{PREFIX}record
{PREFIX}stoprecord
{PREFIX}vcsummary
{PREFIX}vcprofile
{PREFIX}fakevc
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
    # STATS
    # ========================================

    @bot.command()
    async def stats(ctx):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        uptime = datetime.now()

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