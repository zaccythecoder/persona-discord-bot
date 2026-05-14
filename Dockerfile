FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r misc/requirements.txt

CMD ["python", "-m", "bot.main"]