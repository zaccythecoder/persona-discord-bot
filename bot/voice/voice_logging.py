# ============================================
# bot/voice/voice_logging.py
# ============================================

import os
import discord

from discord.ext import commands

from bot.voice.voice_memory import (
    add_transcript,
    load_memory
)

from bot.voice.voice_analysis import (
    detect_emotion
)

from bot.voice.voice_profiles import (
    generate_profile
)

from bot.voice.voice_summary import (
    summarize_text
)

# ============================================
# SETUP
# ============================================

def setup_voice(bot):

    # ========================================
    # FAKE TRANSCRIPT EVENT
    # ========================================

    @bot.command()
    async def fakevc(ctx, *, text):

        username = str(
            ctx.author
        )

        emotion = detect_emotion(
            text
        )

        add_transcript(
            username,
            text,
            emotion
        )

        await ctx.send(

            f"Saved transcript.\n"
            f"Emotion: {emotion}"

        )

    # ========================================
    # PROFILE
    # ========================================

    @bot.command()
    async def vcprofile(ctx, member: discord.Member=None):

        if not member:

            member = ctx.author

        profile = generate_profile(
            str(member)
        )

        if not profile:

            await ctx.send(
                "No profile found."
            )

            return

        await ctx.send(

            f"Messages: {profile['messages']}\n"
            f"Relationship Score: "
            f"{profile['relationship']}%\n"
            f"Emotions: {profile['emotions']}"

        )

    # ========================================
    # SUMMARY
    # ========================================

    @bot.command()
    async def vcsummary(ctx):

        memory = load_memory()

        combined = ""

        for user in memory:

            for msg in memory[user]:

                combined += (
                    f"{user}: "
                    f"{msg['text']}\n"
                )

        if not combined:

            await ctx.send(
                "No transcripts found."
            )

            return

        await ctx.send(
            "Generating AI summary..."
        )

        summary = summarize_text(
            combined[:12000]
        )

        await ctx.send(

            f"```{summary[:1900]}```"

        )