# ================================
# main.py
# ================================

import asyncio
import traceback

print("Starting Discord bot...")

try:

    import bot
    print("bot.py imported successfully")

except Exception as e:

    print("FAILED TO IMPORT bot.py")
    print(e)
    traceback.print_exc()

    input("Press ENTER to exit...")
    raise

try:

    import bot2
    print("bot2.py imported successfully")

except Exception as e:

    print("FAILED TO IMPORT bot2.py")
    print(e)
    traceback.print_exc()

    input("Press ENTER to exit...")
    raise

async def main():

    try:

        await bot.init_db()

        print("Database initialized successfully")

        print(
            f"Logging in as bot..."
        )

        await bot.bot.start(
            bot.TOKEN
        )

    except Exception as e:

        print(
            "\nBOT CRASHED:\n"
        )

        print(e)

        traceback.print_exc()

        input(
            "\nPress ENTER to close..."
        )

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "\nBot stopped manually."
        )