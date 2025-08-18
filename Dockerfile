# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY create_user.py ./create_user.py
COPY import_users_csv.py ./import_users_csv.py

ENV PORT=8000
EXPOSE 8000

# NOTE: set SECRET_KEY and other env vars via compose
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
