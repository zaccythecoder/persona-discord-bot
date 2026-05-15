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
    init_db,
    db
)

from bot.ai_commands import (
    setup as setup_ai
)

from bot.utility_commands import (
    setup as setup_utility
)

from bot.debug_commands import (
    setup as setup_debug
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

    for guild in bot.guilds:

        print(
            f"- {guild.name} ({guild.id})"
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

    if isinstance(
        error,
        commands.CheckFailure
    ):

        return

    print(
        "\n===================================="
    )

    print(
        "COMMAND ERROR"
    )

    print(
        "===================================="
    )

    print(error)

    print(
        "====================================\n"
    )

    try:

        await ctx.send(

            f"Error:\n```{str(error)[:1900]}```"

        )

    except Exception as e:

        print(
            f"Failed sending error: {e}"
        )

# ============================================
# STARTUP
# ============================================

async def startup():

    print(
        "\n===================================="
    )

    print(
        "STARTUP"
    )

    print(
        "===================================="
    )

    print(
        "\nInitializing database..."
    )

    try:

        await init_db()

        print(
            "Database initialized."
        )

    except Exception as e:

        print(
            "\nDATABASE INIT FAILED\n"
        )

        print(e)

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
    # DEBUG COMMANDS
    # ========================================

    setup_debug(bot)

    print(
        "Loaded debug_commands.py"
    )

    # ========================================
    # VOICE SYSTEM
    # ========================================

    setup_voice(bot)

    print(
        "Loaded voice system"
    )

    # ========================================
    # START BOT LOOP
    # ========================================

    print(
        "\n===================================="
    )

    print(
        "STARTING DISCORD BOT"
    )

    print(
        "====================================\n"
    )

    while True:

        try:

            await bot.start(
                TOKEN
            )

        except Exception as e:

            print(
                "\n===================================="
            )

            print(
                "BOT CRASHED"
            )

            print(
                "===================================="
            )

            print(e)

            print(
                "\nRestarting in 10 seconds...\n"
            )

            await asyncio.sleep(10)

# ============================================
# RUN
# ============================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "\nBot shutdown requested."
        )

    finally:

        try:

            if db:

                asyncio.run(
                    db.close()
                )

                print(
                    "Database connection closed."
                )

        except Exception as e:

            print(
                f"Failed closing DB: {e}"
            )