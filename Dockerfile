FROM python:3.11-slim

WORKDIR /app

# Prevent .pyc + buffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (important for audio libs like av / whisper)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    libffi-dev \
    libnacl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Upgrade pip first (prevents broken downloads)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies safely (prevents broken pipe failures)
RUN pip install --no-cache-dir --timeout 120 --retries 20 \
    -r misc/requirements.txt

# Create required runtime dirs
RUN mkdir -p \
    data \
    data/recordings \
    data/transcripts \
    data/summaries \
    data/profiles

# Start bot
CMD ["python", "-m", "bot.main"]