# ============================================
# bot/voice/voice_profiles.py
# ============================================

import discord

from bot.config import (
    OWNER_ID,
    groq_client,
    MODEL,
)

from bot.voice.voice_memory import (
    get_user_transcripts,
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
                        "You are an advanced AI personality analysis assistant."
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
    # VOICE PROFILE
    # ========================================

    @bot.command(name="vcprofile")
    @owner_only()
    async def voice_profile(ctx, member: discord.Member):

        try:
            await ctx.send(f"Building voice profile for {member.name}...")

            transcripts = await get_user_transcripts(member.id, limit=25)

            if not transcripts:
                await ctx.send("No voice transcripts found.")

                return

            transcript_text = "\n\n".join([x[0] for x in transcripts if x[0]])

            prompt = f"""

Analyze this user's voice/chat behaviour.

Give:

- personality
- humor style
- emotional traits
- speaking style
- confidence level
- likely interests
- social behavior
- internet archetype

VOICE TRANSCRIPTS:

{transcript_text}

"""

            response = await ask_groq(prompt)

            if len(response) > 1900:
                chunks = [response[i : i + 1900] for i in range(0, len(response), 1900)]

                for chunk in chunks:
                    await ctx.send(f"```{chunk}```")

            else:
                await ctx.send(f"```{response}```")

        except Exception as e:
            print(f"vcprofile error: {e}")

            await ctx.send(f"VC Profile Error:\n```py\n{e}\n```")

    print("voice_profiles.py loaded.")
