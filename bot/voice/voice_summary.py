# ============================================
# bot/voice/voice_summary.py
# ============================================

import os

from discord.ext import commands

from bot.config import (
    OWNER_ID,
    groq_client,
    MODEL,
    VOICE_SAVE_PATH,
)

from bot.voice.voice_analysis import (
    transcribe_all_recordings,
    cleanup_recordings,
)

from bot.voice.voice_memory import (
    save_transcript,
    save_transcript_file,
)

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
# ASK GROQ
# ============================================


async def ask_groq(prompt):

    try:
        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that summarizes "
                        "Discord voice conversations."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Groq error: {e}")

        return f"AI Error: {e}"


# ============================================
# SETUP
# ============================================


def setup(bot):

    # ========================================
    # VC SUMMARY
    # ========================================

    @bot.command(name="vcsummary")
    @owner_only()
    async def vc_summary(ctx):

        try:
            await ctx.send("Transcribing voice recordings...")

            transcripts = await transcribe_all_recordings()

            if not transcripts:
                await ctx.send("No transcripts available.")

                return

            # ====================================
            # SAVE TRANSCRIPTS
            # ====================================

            combined_text = ""

            for item in transcripts:
                filename = item["file"]

                text = item["text"]

                user_id = filename.replace(".wav", "")

                combined_text += f"\n[{user_id}]\n{text}\n"

                await save_transcript(
                    user_id=user_id, username=user_id, transcript=text
                )

                await save_transcript_file(username=user_id, transcript=text)

            # ====================================
            # AI SUMMARY
            # ====================================

            await ctx.send("Generating AI summary...")

            prompt = f"""

Summarize this Discord voice conversation.

Include:

- major topics
- jokes/memes
- emotional tone
- notable moments
- participant behavior
- overall vibe

VOICE CHAT:

{combined_text}

"""

            response = await ask_groq(prompt)

            # ====================================
            # SEND RESPONSE
            # ====================================

            if len(response) > 1900:
                chunks = [response[i : i + 1900] for i in range(0, len(response), 1900)]

                for chunk in chunks:
                    await ctx.send(f"```{chunk}```")

            else:
                await ctx.send(f"```{response}```")

        except Exception as e:
            print(f"vcsummary error: {e}")

            await ctx.send(f"VC Summary Error:\n```py\n{e}\n```")

    # ========================================
    # DELETE RECORDINGS
    # ========================================

    @bot.command(name="clearrecordings")
    @owner_only()
    async def clear_recordings(ctx):

        try:
            count = 0

            if os.path.exists(VOICE_SAVE_PATH):
                count = len(
                    [f for f in os.listdir(VOICE_SAVE_PATH) if f.endswith(".wav")]
                )

            await cleanup_recordings()

            await ctx.send(f"Deleted {count} recording(s).")

        except Exception as e:
            await ctx.send(f"Clear recordings error:\n```py\n{e}\n```")

    print("voice_summary.py loaded.")
