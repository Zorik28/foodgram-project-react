FROM python:3.9.6-slim

WORKDIR /app
COPY . .
RUN apt update && \
    apt upgrade -y && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
