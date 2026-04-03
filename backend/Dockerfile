FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the static logos directory exists at runtime
RUN mkdir -p /app/static/logos

EXPOSE 8000

# Run migrations and startup-safe seeding before launching the API server.
CMD ["sh", "-c", "alembic upgrade head && python seed.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
