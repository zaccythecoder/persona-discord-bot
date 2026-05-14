# ============================================
# bot/voice_logging.py
# ============================================

import os
import discord

from discord.ext import commands

# ============================================
# SETUP
# ============================================

def setup_voice(bot):

    # ========================================
    # JOIN VC
    # ========================================

    @bot.command()
    async def joinvc(ctx):

        if not ctx.author.voice:

            await ctx.send(
                "Join a VC first."
            )

            return

        channel = ctx.author.voice.channel

        if ctx.voice_client:

            await ctx.voice_client.move_to(
                channel
            )

        else:

            await channel.connect()

        await ctx.send(
            f"Joined {channel.name}"
        )

    # ========================================
    # LEAVE VC
    # ========================================

    @bot.command()
    async def leavevc(ctx):

        if ctx.voice_client:

            await ctx.voice_client.disconnect()

            await ctx.send(
                "Disconnected."
            )

    # ========================================
    # TEST SUMMARY
    # ========================================

    @bot.command()
    async def vcsummary(ctx):

        fake_transcript = """

Zac talked about deployment problems,
Discord bot hosting,
and GitHub setup.

Another user discussed Minecraft mods
and server performance.

The overall tone was casual and technical.

"""

        await ctx.send(

            f"```{fake_transcript}```"

        )