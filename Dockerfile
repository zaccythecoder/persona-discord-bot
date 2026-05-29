FROM python:3.11-slim

# ============================================
# ENVIRONMENT
# ============================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ============================================
# WORKDIR
# ============================================

WORKDIR /app

# ============================================
# SYSTEM PACKAGES
# ============================================

RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# COPY PROJECT
# ============================================

COPY . .

# ============================================
# UPGRADE PIP
# ============================================

RUN python -m pip install --upgrade pip setuptools wheel

# ============================================
# PIP SETTINGS
# ============================================

RUN pip config set global.progress_bar off

# ============================================
# INSTALL MAIN DEPENDENCIES
# ============================================

RUN pip install \
    --no-cache-dir \
    --retries 20 \
    --timeout 120 \
    --prefer-binary \
    discord.py==2.4.0 \
    python-dotenv==1.0.1 \
    aiosqlite==0.20.0 \
    textblob==0.18.0.post0 \
    psutil==5.9.8 \
    groq==0.9.0 \
    "numpy<2.0"

# ============================================
# OPTIONAL VOICE / WHISPER
# ============================================

RUN pip install \
    --no-cache-dir \
    --retries 20 \
    --timeout 120 \
    --prefer-binary \
    faster-whisper==1.0.2 \
    ctranslate2==4.3.1 \
    av==12.2.0

# ============================================
# DOWNLOAD NLTK DATA
# ============================================

RUN python -m textblob.download_corpora

# ============================================
# START BOT
# ============================================

CMD ["python", "-m", "bot.main"]