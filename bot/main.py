# ============================================
# bot/main.py
# ============================================

import asyncio
import discord

from discord.ext import commands

from bot.config import (
    TOKEN,
    PREFIX,
    OWNER_ID
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

from bot.tracking import (
    setup as setup_tracking
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
# OWNER CHECK
# ============================================

def owner_only():

    async def predicate(ctx):

        # ====================================
        # ONLY DMS
        # ====================================

        if ctx.guild is not None:

            await ctx.send(
                "Commands only work in DMs."
            )

            return False

        # ====================================
        # OPTIONAL OWNER LOCK
        # ====================================

        if OWNER_ID != 0:

            if ctx.author.id != OWNER_ID:

                await ctx.send(
                    "You are not authorized."
                )

                return False

        return True

    return commands.check(
        predicate
    )

# ============================================
# READY EVENT
# ============================================

@bot.event
async def on_ready():

    print(
        "\n===================================="
    )

    print(
        "BOT ONLINE"
    )

    print(
        f"Logged in as: {bot.user}"
    )

    print(
        "====================================\n"
    )

    print(
        f"Connected to "
        f"{len(bot.guilds)} guild(s)"
    )

# ============================================
# GLOBAL COMMAND CHECK
# ============================================

@bot.check
async def globally_block_guild_commands(
    ctx
):

    # ========================================
    # ALLOW DMS
    # ========================================

    if ctx.guild is None:
        return True

    # ========================================
    # BLOCK SERVER COMMANDS
    # ========================================

    return False

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

    if isinstance(
        error,
        commands.CheckFailure
    ):

        return

    print(
        f"\nCOMMAND ERROR:\n{error}\n"
    )

    try:

        await ctx.send(

            f"Error:\n```{error}```"

        )

    except:

        pass

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

    # ========================================
    # DATABASE
    # ========================================

    await startup()

    # ========================================
    # TRACKING SYSTEM
    # ========================================

    setup_tracking(bot)

    print(
        "Loaded tracking.py"
    )

    # ========================================
    # AI COMMANDS
    # ========================================

    setup_ai(bot)

    print(
        "Loaded ai_commands.py"
    )

    # ========================================
    # UTILITY COMMANDS
    # ========================================

    setup_utility(bot)

    print(
        "Loaded utility_commands.py"
    )

    # ========================================
    # VOICE SYSTEM
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