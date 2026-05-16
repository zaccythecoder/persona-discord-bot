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

RUN mkdir -p data
RUN mkdir -p data/recordings
RUN mkdir -p data/transcripts

# ============================================
# START BOT
# ============================================

CMD ["python", "-m", "bot.main"]