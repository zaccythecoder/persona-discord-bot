FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ffmpeg git build-essential libffi-dev libnacl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 1. Copy requirements first
COPY misc/requirements.txt /app/misc/requirements.txt

# 2. Install dependencies safely
RUN pip install --no-cache-dir --timeout 120 --retries 20 -r misc/requirements.txt

# 3. Copy source code last
COPY . /app
RUN mkdir -p data data/recordings data/transcripts data/summaries data/profiles

CMD ["python", "-m", "bot.main"]
