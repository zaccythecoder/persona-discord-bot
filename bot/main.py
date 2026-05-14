# ============================================
# bot/main.py
# ============================================

import asyncio
import discord

from discord.ext import commands

from bot.config import (
    TOKEN,
    PREFIX
)

from bot.database import (
    init_db
)

from bot.ai_commands import (
    setup as setup_ai
)

from bot.utility_commands import (
    setup as setup_utility
)

from bot.voice.voice_logging import (
    setup_voice
)

# ============================================
# INTENTS
# ============================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.presences = True
intents.guilds = True
intents.messages = True
intents.voice_states = True

# ============================================
# BOT SETUP
# ============================================

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# ============================================
# REMOVE DEFAULT HELP
# ============================================

bot.remove_command(
    "help"
)

# ============================================
# READY EVENT
# ============================================

@bot.event
async def on_ready():

    print("\n====================================")
    print("BOT ONLINE")
    print(f"Logged in as: {bot.user}")
    print("====================================\n")

    print(
        f"Connected to "
        f"{len(bot.guilds)} guild(s)"
    )

# ============================================
# ERROR HANDLER
# ============================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        return

    print(
        f"\nCOMMAND ERROR:\n{error}\n"
    )

    await ctx.send(

        f"Error:\n```{error}```"

    )

# ============================================
# STARTUP
# ============================================

async def startup():

    print(
        "\nInitializing database..."
    )

    await init_db()

    print(
        "Database initialized."
    )

# ============================================
# MAIN
# ============================================

async def main():

    await startup()

    # ========================================
    # LOAD AI COMMANDS
    # ========================================

    setup_ai(bot)

    print(
        "Loaded ai_commands.py"
    )

    # ========================================
    # LOAD UTILITY COMMANDS
    # ========================================

    setup_utility(bot)

    print(
        "Loaded utility_commands.py"
    )

    # ========================================
    # LOAD VOICE SYSTEM
    # ========================================

    setup_voice(bot)

    print(
        "Loaded voice system"
    )

    # ========================================
    # START BOT
    # ========================================

    print(
        "\nStarting Discord bot...\n"
    )

    await bot.start(
        TOKEN
    )

# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )