FROM python:3.11-slim

# ============================================
# SYSTEM PACKAGES
# ============================================

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# WORKDIR
# ============================================

WORKDIR /app

# ============================================
# COPY FILES
# ============================================

COPY . .

# ============================================
# INSTALL PYTHON PACKAGES
# ============================================

RUN pip install --upgrade pip

RUN pip install -r misc/requirements.txt

# ============================================
# CREATE DATA FOLDERS
# ============================================

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir \
    discord.py==2.4.0 \
    python-dotenv==1.0.1 \
    aiosqlite==0.20.0 \
    textblob==0.18.0.post0 \
    psutil==5.9.8 \
    groq==0.9.0

RUN pip install --no-cache-dir \
    numpy<2.0 \
    av==12.2.0 \
    ctranslate2==4.3.1 \
    faster-whisper==1.0.2

# ============================================
# START BOT
# ============================================

CMD ["python", "-m", "bot.main"]
