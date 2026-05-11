# ================================
# bot2.py
# ================================

import discord
from discord.ext import commands, tasks
from datetime import datetime

import bot

# =========================================================
# REFERENCES
# =========================================================

bot_instance = bot.bot

db_lock = bot.db_lock
groq_client = bot.groq_client

MODEL_NAME = bot.MODEL_NAME

process_message_data = bot.process_message_data
ensure_user = bot.ensure_user
log_game = bot.log_game
owner_dm_only = bot.owner_dm_only
init_db = bot.init_db

# =========================================================
# PERSONA BUILDER
# =========================================================

async def build_persona(user_id):

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT *
            FROM users
            WHERE user_id=?
            """,
            (
                user_id,
            )
        )

        data = await cursor.fetchone()

        if not data:
            return "No data found."

        (
            uid,
            username,
            total_messages,
            total_words,
            avg_sentiment,
            morning_msgs,
            afternoon_msgs,
            night_msgs,
            emojis_used,
            questions_asked,
            replies_sent,
            manual_notes
        ) = data

        word_cursor = await bot.db.execute(
            """
            SELECT word, count
            FROM words
            WHERE user_id=?
            ORDER BY count DESC
            LIMIT 50
            """,
            (
                user_id,
            )
        )

        top_words = await word_cursor.fetchall()

        game_cursor = await bot.db.execute(
            """
            SELECT game_name,
                   times_seen
            FROM games
            WHERE user_id=?
            ORDER BY times_seen DESC
            LIMIT 50
            """,
            (
                user_id,
            )
        )

        games = await game_cursor.fetchall()

        msg_cursor = await bot.db.execute(
            """
            SELECT content
            FROM message_history
            WHERE user_id=?
            ORDER BY RANDOM()
            LIMIT 50
            """,
            (
                user_id,
            )
        )

        samples = await msg_cursor.fetchall()

    top_word_list = "\n".join([
        f"{w[0]} ({w[1]})"
        for w in top_words
    ])

    game_list = "\n".join([
        f"{g[0]} ({g[1]} times)"
        for g in games
    ])

    sample_text = "\n".join([
        x[0]
        for x in samples
    ])

    prompt = f"""
Analyze this Discord user deeply.

Username:
{username}

Messages:
{total_messages}

Words:
{total_words}

Average Sentiment:
{avg_sentiment}

Morning Messages:
{morning_msgs}

Afternoon Messages:
{afternoon_msgs}

Night Messages:
{night_msgs}

Emojis Used:
{emojis_used}

Questions Asked:
{questions_asked}

Replies Sent:
{replies_sent}

Games:
{game_list}

Manual Notes:
{manual_notes}

Top Words:
{top_word_list}

Message Samples:
{sample_text}

Include:
- Personality
- Humor
- Emotional patterns
- Social style
- Likely insecurities
- Likely strengths
- Internet archetype
- What kind of friend they are
- How they act socially
- Writing style
- Overall summary
"""

    try:

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a highly advanced "
                        "behavioral and personality analyst."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_tokens=3500
        )

        return (
            response
            .choices[0]
            .message.content
        )

    except Exception as e:

        return f"Groq Error: {e}"

# =========================================================
# READY
# =========================================================

@bot_instance.event
async def on_ready():

    try:

        print(
            f"Logged in as {bot_instance.user}"
        )

        await init_db()

        print(
            "Database initialized."
        )

        if not activity_tracker.is_running():

            activity_tracker.start()

            print(
                "Activity tracker started."
            )

    except Exception as e:

        print(
            f"READY ERROR: {e}"
        )

# =========================================================
# MESSAGE EVENT
# =========================================================

@bot_instance.event
async def on_message(message):

    try:

        await process_message_data(
            message
        )

        await bot_instance.process_commands(
            message
        )

    except Exception as e:

        print(
            f"Message Error: {e}"
        )

# =========================================================
# COMMAND ERROR
# =========================================================

@bot_instance.event
async def on_command_error(
    ctx,
    error
):

    await ctx.send(
        f"```{error}```"
    )

# =========================================================
# PRESENCE TRACKER
# =========================================================

@bot_instance.event
async def on_presence_update(
    before,
    after
):

    try:

        if after.bot:
            return

        if after.activities:

            for activity in after.activities:

                await log_game(
                    after.id,
                    str(activity)
                )

    except Exception as e:

        print(
            f"Presence Error: {e}"
        )

# =========================================================
# ACTIVITY LOOP
# =========================================================

@tasks.loop(minutes=2)
async def activity_tracker():

    for guild in bot_instance.guilds:

        for member in guild.members:

            try:

                if member.bot:
                    continue

                await ensure_user(
                    member
                )

                if member.activities:

                    for activity in member.activities:

                        await log_game(
                            member.id,
                            str(activity)
                        )

            except Exception as e:

                print(
                    f"Activity Error: {e}"
                )

# =========================================================
# PERSONA
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def persona(
    ctx,
    member: discord.User = None
):

    member = member or ctx.author

    loading = await ctx.send(
        "Generating persona..."
    )

    report = await build_persona(
        member.id
    )

    await loading.delete()

    chunks = []

    while len(report) > 1900:

        split = report.rfind(
            "\n",
            0,
            1900
        )

        if split == -1:
            split = 1900

        chunks.append(
            report[:split]
        )

        report = report[split:]

    chunks.append(report)

    for chunk in chunks:

        await ctx.send(
            f"```{chunk}```"
        )

# =========================================================
# ASK USER
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def ask(
    ctx,
    member: discord.User,
    *,
    question
):

    loading = await ctx.send(
        "Thinking..."
    )

    persona_text = await build_persona(
        member.id
    )

    prompt = f"""
Answer the question about this user.

QUESTION:
{question}

USER ANALYSIS:
{persona_text}
"""

    try:

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions "
                        "about Discord users."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_tokens=2500
        )

        answer = (
            response
            .choices[0]
            .message.content
        )

    except Exception as e:

        return await loading.edit(
            content=f"Groq Error: {e}"
        )

    await loading.delete()

    chunks = []

    while len(answer) > 1900:

        split = answer.rfind(
            "\n",
            0,
            1900
        )

        if split == -1:
            split = 1900

        chunks.append(
            answer[:split]
        )

        answer = answer[split:]

    chunks.append(answer)

    for chunk in chunks:

        await ctx.send(
            f"```{chunk}```"
        )

# =========================================================
# ASK EVERYONE
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def askall(
    ctx,
    *,
    question
):

    loading = await ctx.send(
        "Analyzing server..."
    )

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT user_id,
                   username,
                   total_messages,
                   total_words,
                   avg_sentiment,
                   manual_notes
            FROM users
            ORDER BY total_messages DESC
            LIMIT 200
            """
        )

        users = await cursor.fetchall()

    combined = []

    for user in users:

        uid = user[0]

        async with db_lock:

            word_cursor = await bot.db.execute(
                """
                SELECT word, count
                FROM words
                WHERE user_id=?
                ORDER BY count DESC
                LIMIT 30
                """,
                (
                    uid,
                )
            )

            words = await word_cursor.fetchall()

        word_text = ", ".join([
            f"{w[0]} ({w[1]})"
            for w in words
        ])

        combined.append(
            f"""
USERNAME: {user[1]}
MESSAGES: {user[2]}
WORDS: {user[3]}
SENTIMENT: {user[4]}

NOTES:
{user[5]}

TOP WORDS:
{word_text}
"""
        )

    full_text = "\n\n".join(combined)

    prompt = f"""
Analyze this Discord server.

QUESTION:
{question}

SERVER DATA:
{full_text}

You should:
- Compare users
- Rank users if needed
- Mention usernames often
- Infer patterns
- Answer confidently
"""

    try:

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert "
                        "server behavior analyst."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_tokens=3500
        )

        answer = (
            response
            .choices[0]
            .message.content
        )

    except Exception as e:

        return await loading.edit(
            content=f"Groq Error: {e}"
        )

    await loading.delete()

    chunks = []

    while len(answer) > 1900:

        split = answer.rfind(
            "\n",
            0,
            1900
        )

        if split == -1:
            split = 1900

        chunks.append(
            answer[:split]
        )

        answer = answer[split:]

    chunks.append(answer)

    for chunk in chunks:

        await ctx.send(
            f"```{chunk}```"
        )

# =========================================================
# NOTE
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def note(
    ctx,
    member: discord.User,
    *,
    note_text
):

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT manual_notes
            FROM users
            WHERE user_id=?
            """,
            (
                member.id,
            )
        )

        existing = await cursor.fetchone()

        old_notes = ""

        if existing and existing[0]:

            old_notes = existing[0]

        new_notes = (
            old_notes
            + "\n"
            + f"[{datetime.utcnow()}] "
            + note_text
        )

        await bot.db.execute(
            """
            UPDATE users
            SET manual_notes=?
            WHERE user_id=?
            """,
            (
                new_notes,
                member.id
            )
        )

        await bot.db.commit()

    await ctx.send(
        f"Added note for {member}"
    )

# =========================================================
# NOTES
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def notes(
    ctx,
    member: discord.User
):

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT manual_notes
            FROM users
            WHERE user_id=?
            """,
            (
                member.id,
            )
        )

        data = await cursor.fetchone()

    if not data:
        return await ctx.send("No notes found.")

    notes_text = data[0]

    if not notes_text:
        return await ctx.send("No notes found.")

    chunks = []

    while len(notes_text) > 1900:

        chunks.append(
            notes_text[:1900]
        )

        notes_text = notes_text[1900:]

    chunks.append(notes_text)

    for chunk in chunks:

        await ctx.send(
            f"```{chunk}```"
        )

# =========================================================
# CLEAR NOTES
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def clearnotes(
    ctx,
    member: discord.User
):

    async with db_lock:

        await bot.db.execute(
            """
            UPDATE users
            SET manual_notes=''
            WHERE user_id=?
            """,
            (
                member.id,
            )
        )

        await bot.db.commit()

    await ctx.send(
        f"Cleared notes for {member}"
    )

# =========================================================
# STATS
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def stats(
    ctx,
    member: discord.User = None
):

    member = member or ctx.author

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT *
            FROM users
            WHERE user_id=?
            """,
            (
                member.id,
            )
        )

        data = await cursor.fetchone()

    await ctx.send(
        f"```{data}```"
    )

# =========================================================
# GAMES
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def games(
    ctx,
    member: discord.User
):

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT game_name,
                   first_seen,
                   last_seen,
                   times_seen
            FROM games
            WHERE user_id=?
            ORDER BY times_seen DESC
            """,
            (
                member.id,
            )
        )

        games = await cursor.fetchall()

    if not games:
        return await ctx.send(
            "No games tracked."
        )

    text = ""

    for game in games:

        text += (
            f"{game[0]}\n"
            f"Seen: {game[3]} times\n"
            f"First: {game[1]}\n"
            f"Last: {game[2]}\n\n"
        )

    chunks = []

    while len(text) > 1900:

        chunks.append(
            text[:1900]
        )

        text = text[1900:]

    chunks.append(text)

    for chunk in chunks:

        await ctx.send(
            f"```{chunk}```"
        )

# =========================================================
# TOP WORDS
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def topwords(
    ctx,
    member: discord.User
):

    async with db_lock:

        cursor = await bot.db.execute(
            """
            SELECT word,
                   count
            FROM words
            WHERE user_id=?
            ORDER BY count DESC
            LIMIT 5
            """,
            (
                member.id,
            )
        )

        results = await cursor.fetchall()

    if not results:

        return await ctx.send(
            "No word data found."
        )

    text = f"Top words for {member}:\n\n"

    for i, (word, count) in enumerate(results, start=1):

        text += (
            f"{i}. {word} "
            f"({count} uses)\n"
        )

    await ctx.send(
        f"```{text}```"
    )

# =========================================================
# SCAN HISTORY
# =========================================================

@bot_instance.command()
@commands.check(owner_dm_only)
async def scanhistory(ctx):

    status = await ctx.send(
        "Starting full server history scan..."
    )

    total_scanned = 0
    skipped = 0

    for guild in bot_instance.guilds:

        for channel in guild.text_channels:

            try:

                await status.edit(
                    content=(
                        f"Scanning: "
                        f"{guild.name} / #{channel.name}"
                    )
                )

                async for message in channel.history(
                    limit=None,
                    oldest_first=True
                ):

                    try:

                        if message.author.bot:
                            continue

                        async with db_lock:

                            cursor = await bot.db.execute(
                                """
                                SELECT message_id
                                FROM scanned_messages
                                WHERE message_id=?
                                """,
                                (
                                    message.id,
                                )
                            )

                            exists = await cursor.fetchone()

                        if exists:

                            skipped += 1
                            continue

                        await process_message_data(
                            message
                        )

                        total_scanned += 1

                        if total_scanned % 500 == 0:

                            await status.edit(
                                content=(
                                    f"New Messages: "
                                    f"{total_scanned}\n"
                                    f"Skipped Existing: "
                                    f"{skipped}"
                                )
                            )

                    except Exception as e:

                        print(
                            f"Message Scan Error: {e}"
                        )

            except Exception as e:

                print(
                    f"Channel Scan Error: {e}"
                )

    await status.edit(
        content=(
            f"History scan complete.\n\n"
            f"New messages added: "
            f"{total_scanned}\n"
            f"Already scanned skipped: "
            f"{skipped}"
        )
    )