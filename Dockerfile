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

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip config set global.progress_bar off

RUN pip install \
    --no-cache-dir \
    --retries 20 \
    --timeout 120 \
    --prefer-binary \
    -r misc/requirements.txt

# ============================================
# START BOT
# ============================================

CMD ["python", "-m", "bot.main"]
