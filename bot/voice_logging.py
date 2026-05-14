# ============================================
# bot/voice_logging.py
# ============================================

import os
import wave
import discord
import asyncio

from discord.ext import commands

import discord.ext.voice_recv as voice_recv

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
# PATHS
# ============================================

RECORDING_FILE = (
    "data/recordings/live.wav"
)

TRANSCRIPT_FILE = (
    "data/transcripts/latest.txt"
)

# ============================================
# AUDIO SINK
# ============================================

class VoiceSink(
    voice_recv.AudioSink
):

    def __init__(self):

        super().__init__()

        self.wav = wave.open(
            RECORDING_FILE,
            "wb"
        )

        self.wav.setnchannels(2)
        self.wav.setsampwidth(2)
        self.wav.setframerate(48000)

    def write(self, user, data):

        self.wav.writeframes(
            data.pcm
        )

    def cleanup(self):

        self.wav.close()

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

        vc = await channel.connect(
            cls=voice_recv.VoiceRecvClient
        )

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

        vc = ctx.voice_client

        if not vc:

            await ctx.send(
                "Bot is not in VC."
            )

            return

        sink = VoiceSink()

        vc.listen(
            sink
        )

        bot.current_sink = sink

        await ctx.send(
            "Live recording started."
        )

    # ========================================
    # STOP RECORDING
    # ========================================

    @bot.command()
    async def stoprecord(ctx):

        vc = ctx.voice_client

        if not vc:

            return

        vc.stop_listening()

        if hasattr(
            bot,
            "current_sink"
        ):

            bot.current_sink.cleanup()

        await ctx.send(
            "Recording stopped."
        )

        # ====================================
        # TRANSCRIBE
        # ====================================

        await ctx.send(
            "Transcribing audio..."
        )

        segments, info = model.transcribe(
            RECORDING_FILE
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
            TRANSCRIPT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                transcript
            )

        await ctx.send(
            "Transcript complete."
        )

    # ========================================
    # VIEW SUMMARY
    # ========================================

    @bot.command()
    async def vcsummary(ctx):

        if not os.path.exists(
            TRANSCRIPT_FILE
        ):

            await ctx.send(
                "No transcript found."
            )

            return

        with open(
            TRANSCRIPT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            transcript = f.read()

        transcript = transcript[:1800]

        await ctx.send(

            f"```{transcript}```"

        )