# ============================================
# bot/voice_logging.py
# ============================================

import os
import wave
import discord
import asyncio

from discord.ext import commands

from faster_whisper import WhisperModel

# ============================================
# WHISPER MODEL
# ============================================

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# ============================================
# RECORDING STORAGE
# ============================================

recording_active = False

audio_chunks = []

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
    # START RECORDING
    # ========================================

    @bot.command()
    async def record(ctx):

        global recording_active

        if not ctx.voice_client:

            await ctx.send(
                "Bot is not in VC."
            )

            return

        recording_active = True

        await ctx.send(
            "Recording started."
        )

    # ========================================
    # STOP RECORDING
    # ========================================

    @bot.command()
    async def stoprecord(ctx):

        global recording_active

        recording_active = False

        await ctx.send(
            "Recording stopped."
        )

        # fake placeholder audio path
        audio_path = "data/recordings/test.wav"

        # ====================================
        # TRANSCRIBE
        # ====================================

        await ctx.send(
            "Transcribing..."
        )

        segments, info = model.transcribe(
            audio_path
        )

        transcript = ""

        for segment in segments:

            transcript += (
                segment.text + "\n"
            )

        # ====================================
        # SAVE TRANSCRIPT
        # ====================================

        with open(
            "data/transcripts/latest.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                transcript
            )

        await ctx.send(
            "Transcript saved."
        )

    # ========================================
    # VIEW SUMMARY
    # ========================================

    @bot.command()
    async def vcsummary(ctx):

        transcript_path = (
            "data/transcripts/latest.txt"
        )

        if not os.path.exists(
            transcript_path
        ):

            await ctx.send(
                "No transcript found."
            )

            return

        with open(
            transcript_path,
            "r",
            encoding="utf-8"
        ) as f:

            transcript = f.read()

        # shorten for Discord limit
        transcript = transcript[:1800]

        await ctx.send(

            f"```{transcript}```"

        )