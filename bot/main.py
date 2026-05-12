# ============================================
# bot/main.py
# ============================================

import discord
from discord.ext import commands
import asyncio
import traceback

from bot.config import (
    TOKEN,
    PREFIX
)

from bot.database import (
    init_db
)

# ============================================
# BOT SETUP
# ============================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# ============================================
# IMPORT MODULES
# ============================================

try:

    from bot import tracking

    print(
        "tracking.py loaded"
    )

except Exception as e:

    print(
        "FAILED TO LOAD tracking.py"
    )

    print(e)

    traceback.print_exc()

    raise

try:

    from bot import ai_commands

    print(
        "ai_commands.py loaded"
    )

except Exception as e:

    print(
        "FAILED TO LOAD ai_commands.py"
    )

    print(e)

    traceback.print_exc()

    raise

try:

    from bot import utility_commands

    print(
        "utility_commands.py loaded"
    )

except Exception as e:

    print(
        "FAILED TO LOAD utility_commands.py"
    )

    print(e)

    traceback.print_exc()

    raise

# ============================================
# REGISTER BOT OBJECT
# ============================================

tracking.setup(bot)
ai_commands.setup(bot)
utility_commands.setup(bot)

# ============================================
# READY EVENT
# ============================================

@bot.event
async def on_ready():

    print("\n==============================")
    print("BOT ONLINE")
    print("==============================")

    print(
        f"Logged in as: {bot.user}"
    )

    print(
        f"Bot ID: {bot.user.id}"
    )

    print("==============================\n")

# ============================================
# MAIN STARTUP
# ============================================

async def main():

    try:

        print(
            "\nInitializing database...\n"
        )

        await init_db()

        print(
            "Database initialized.\n"
        )

        print(
            "Starting Discord bot...\n"
        )

        await bot.start(
            TOKEN
        )

    except Exception as e:

        print(
            "\nBOT CRASHED\n"
        )

        print(e)

        traceback.print_exc()

        raise

# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "\nBot stopped manually."
        )