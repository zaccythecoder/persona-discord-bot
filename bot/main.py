# ============================================
# bot/main.py
# ============================================

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

from bot.voice_logging import (
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
# BOT
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

    print("\n================================")
    print("BOT ONLINE")
    print(f"Logged in as: {bot.user}")
    print("================================\n")

# ============================================
# STARTUP
# ============================================

async def startup():

    print(
        "\nInitializing database...\n"
    )

    await init_db()

    print(
        "Database initialized.\n"
    )

# ============================================
# MAIN
# ============================================

async def main():

    await startup()

    # ================================
    # LOAD COMMAND MODULES
    # ================================

    setup_ai(bot)

    print(
        "ai_commands.py loaded"
    )

    setup_utility(bot)

    print(
        "utility_commands.py loaded"
    )

    setup_voice(bot)

    print(
        "voice_logging.py loaded"
    )

    # ================================
    # START BOT
    # ================================

    print(
        "Starting Discord bot..."
    )

    await bot.start(
        TOKEN
    )

# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    import asyncio

    asyncio.run(
        main()
    )