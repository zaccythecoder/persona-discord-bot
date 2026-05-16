# ============================================
# bot/ai_commands.py
# ============================================

import discord

from discord.ext import commands

from bot.config import (
    groq_client,
    MODEL,
    OWNER_ID,
)

from bot.database import (
    db,
    get_all_users,
    get_games,
    get_notes,
    get_top_words,
    get_user_stats,
)

# ============================================
# OWNER CHECK
# ============================================


def owner_only():

    async def predicate(ctx):

        # ====================================
        # DM ONLY
        # ====================================

        if ctx.guild is not None:
            await ctx.send("Commands only work in DMs.")

            return False

        # ====================================
        # OWNER LOCK
        # ====================================

        if OWNER_ID != 0:
            if ctx.author.id != OWNER_ID:
                await ctx.send("You are not authorized.")

                return False

        return True

    return commands.check(predicate)


# ============================================
# FORMAT USER DATA
# ============================================


async def build_user_context(user):

    stats = await get_user_stats(user.id)

    top_words = await get_top_words(user.id, 10)

    games = await get_games(user.id)

    notes = await get_notes(user.id)

    # ========================================
    # RECENT MESSAGES
    # ========================================

    recent_messages = ""

    try:
        if db:
            cursor = await db.execute(
                """
                SELECT content
                FROM message_history
                WHERE user_id=?
                ORDER BY message_id DESC
                LIMIT 50
                """,
                (user.id,),
            )

            messages = await cursor.fetchall()

            recent_messages = "\n".join([x[0] for x in messages if x[0]])

    except Exception as e:
        print(f"Recent message fetch error: {e}")

    # ========================================
    # WORDS
    # ========================================

    top_words_text = "\n".join([f"{word} ({count})" for word, count in top_words])

    # ========================================
    # GAMES
    # ========================================

    games_text = "\n".join([f"{game} ({count})" for game, count in games])

    # ========================================
    # STATS TEXT
    # ========================================

    if stats:
        stats_text = f"""
Username: {stats[1]}
Messages: {stats[2]}
Words: {stats[3]}
Sentiment: {stats[4]}
Morning msgs: {stats[5]}
Afternoon msgs: {stats[6]}
Night msgs: {stats[7]}
Emojis: {stats[8]}
Questions: {stats[9]}
Replies: {stats[10]}
"""

    else:
        stats_text = "No stats found."

    return f"""

=== USER STATS ===
{stats_text}

=== TOP WORDS ===
{top_words_text}

=== GAMES ===
{games_text}

=== NOTES ===
{notes}

=== RECENT MESSAGES ===
{recent_messages}

"""


# ============================================
# AI REQUEST
# ============================================


async def ask_groq(prompt):

    completion = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": ("You are an advanced Discord personality analysis AI."),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return completion.choices[0].message.content


# ============================================
# SEND LONG RESPONSE
# ============================================


async def send_long_message(ctx, response):

    if not response:
        response = "No response."

    if len(response) > 1900:
        chunks = [response[i : i + 1900] for i in range(0, len(response), 1900)]

        for chunk in chunks:
            await ctx.send(f"```{chunk}```")

    else:
        await ctx.send(f"```{response}```")


# ============================================
# SETUP
# ============================================


def setup(bot):

    # ========================================
    # PERSONA
    # ========================================

    @bot.command()
    @owner_only()
    async def persona(ctx, member: discord.User):

        await ctx.send("Generating personality analysis...")

        context = await build_user_context(member)

        prompt = f"""

Analyze this Discord user.

Give:

- personality
- humor
- emotional patterns
- social style
- internet archetype
- strengths
- weaknesses
- likely interests
- communication style

USER DATA:

{context}

"""

        try:
            response = await ask_groq(prompt)

            await send_long_message(ctx, response)

        except Exception as e:
            await ctx.send(f"AI Error: {e}")

    # ========================================
    # ASK USER
    # ========================================

    @bot.command()
    @owner_only()
    async def ask(ctx, member: discord.User, *, question):

        await ctx.send("Thinking...")

        context = await build_user_context(member)

        prompt = f"""

Answer this question about the Discord user.

QUESTION:
{question}

USER DATA:
{context}

"""

        try:
            response = await ask_groq(prompt)

            await send_long_message(ctx, response)

        except Exception as e:
            await ctx.send(f"AI Error: {e}")

    # ========================================
    # ASK ALL
    # ========================================

    @bot.command()
    @owner_only()
    async def askall(ctx, *, question):

        await ctx.send("Analyzing all users...")

        users = await get_all_users()

        combined = ""

        for user in users:
            combined += f"""

Username: {user[1]}
Messages: {user[2]}
Words: {user[3]}

"""

        prompt = f"""

Answer this question about ALL Discord users.

QUESTION:
{question}

USER DATA:
{combined}

"""

        try:
            response = await ask_groq(prompt)

            await send_long_message(ctx, response)

        except Exception as e:
            await ctx.send(f"AI Error: {e}")
