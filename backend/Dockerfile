FROM python:3.9.6-slim

WORKDIR /app
COPY requirements.txt .
RUN apt update && \
    apt upgrade -y && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
