FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential

RUN pip install --no-cache-dir -r misc/requirements.txt

CMD ["python", "-m", "bot.main"]