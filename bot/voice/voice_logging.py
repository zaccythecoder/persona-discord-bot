# ============================================
# bot/voice/voice_logging.py
# ============================================

import os
import discord

from discord.ext import commands

from bot.config import (
    OWNER_ID,
    VOICE_SAVE_PATH,
)

# ============================================
# GLOBALS
# ============================================

voice_clients = {}

recording_states = {}

# ============================================
# OWNER CHECK
# ============================================


def owner_only():

    async def predicate(ctx):

        if OWNER_ID == 0:
            return True

        return ctx.author.id == OWNER_ID

    return commands.check(predicate)


# ============================================
# ENSURE RECORDING FOLDER
# ============================================

os.makedirs(VOICE_SAVE_PATH, exist_ok=True)

# ============================================
# SAFE DISCORD SINK
# ============================================


class DummySink(discord.sinks.WaveSink):
    def __init__(self):

        super().__init__()

    async def on_finish(self):

        print("Recording finished.")


# ============================================
# SETUP
# ============================================


def setup_voice(bot):

    # ========================================
    # JOIN VC
    # ========================================

    @bot.command(name="joinvc")
    @owner_only()
    async def join_vc(ctx):

        try:
            if not ctx.author.voice:
                await ctx.send("You are not in a voice channel.")

                return

            channel = ctx.author.voice.channel

            # ====================================
            # ALREADY CONNECTED
            # ====================================

            if ctx.guild.voice_client:
                await ctx.guild.voice_client.move_to(channel)

                await ctx.send(f"Moved to: `{channel.name}`")

                return

            # ====================================
            # CONNECT
            # ====================================

            vc = await channel.connect()

            voice_clients[ctx.guild.id] = vc

            await ctx.send(f"Joined VC: `{channel.name}`")

            print(f"Connected to VC in guild: {ctx.guild.name}")

        except Exception as e:
            print(f"joinvc error: {e}")

            await ctx.send(f"Join VC error:\n```py\n{e}\n```")

    # ========================================
    # LEAVE VC
    # ========================================

    @bot.command(name="leavevc")
    @owner_only()
    async def leave_vc(ctx):

        try:
            vc = ctx.guild.voice_client

            if not vc:
                await ctx.send("Bot is not in a voice channel.")

                return

            await vc.disconnect()

            voice_clients.pop(ctx.guild.id, None)

            recording_states.pop(ctx.guild.id, None)

            await ctx.send("Disconnected from VC.")

            print(f"Disconnected from VC in guild: {ctx.guild.name}")

        except Exception as e:
            print(f"leavevc error: {e}")

            await ctx.send(f"Leave VC error:\n```py\n{e}\n```")

    # ========================================
    # START RECORDING
    # ========================================

    @bot.command(name="record")
    @owner_only()
    async def start_recording(ctx):

        try:
            vc = ctx.guild.voice_client

            if not vc:
                await ctx.send("Bot is not connected to VC.")

                return

            if recording_states.get(ctx.guild.id):
                await ctx.send("Already recording.")

                return

            sink = DummySink()

            recording_states[ctx.guild.id] = True

            vc.start_recording(sink, finished_callback, ctx)

            await ctx.send("Started recording voice chat.")

            print(f"Recording started in guild: {ctx.guild.name}")

        except Exception as e:
            print(f"record error: {e}")

            await ctx.send(f"Record error:\n```py\n{e}\n```")

    # ========================================
    # STOP RECORDING
    # ========================================

    @bot.command(name="stoprecord")
    @owner_only()
    async def stop_recording(ctx):

        try:
            vc = ctx.guild.voice_client

            if not vc:
                await ctx.send("Bot is not connected to VC.")

                return

            if not recording_states.get(ctx.guild.id):
                await ctx.send("Not currently recording.")

                return

            vc.stop_recording()

            recording_states[ctx.guild.id] = False

            await ctx.send("Stopped recording.")

            print(f"Recording stopped in guild: {ctx.guild.name}")

        except Exception as e:
            print(f"stoprecord error: {e}")

            await ctx.send(f"Stop recording error:\n```py\n{e}\n```")

    # ========================================
    # VC STATUS
    # ========================================

    @bot.command(name="vcstatus")
    async def vc_status(ctx):

        try:
            vc = ctx.guild.voice_client

            connected = vc is not None

            recording = recording_states.get(ctx.guild.id, False)

            embed = discord.Embed(title="Voice Status", color=discord.Color.blurple())

            embed.add_field(name="Connected", value=str(connected), inline=False)

            embed.add_field(name="Recording", value=str(recording), inline=False)

            if connected:
                embed.add_field(name="Channel", value=vc.channel.name, inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"VC status error:\n```py\n{e}\n```")

    print("voice_logging.py loaded.")


# ============================================
# RECORDING CALLBACK
# ============================================


async def finished_callback(sink, ctx):

    try:
        recordings_saved = 0

        for user_id, audio in sink.audio_data.items():
            filename = os.path.join(VOICE_SAVE_PATH, f"{user_id}.wav")

            with open(filename, "wb") as f:
                f.write(audio.file.read())

            recordings_saved += 1

        await ctx.send(f"Recording finished.\nSaved {recordings_saved} audio file(s).")

        print(f"Saved {recordings_saved} voice recordings.")

    except Exception as e:
        print(f"Recording callback error: {e}")

        try:
            await ctx.send(f"Recording save error:\n```py\n{e}\n```")

        except Exception:
            pass
