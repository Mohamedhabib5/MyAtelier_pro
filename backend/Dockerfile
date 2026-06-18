# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final image
FROM python:3.13-slim

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies and copy installed python packages
# tech-debt: add git for test_no_sensitive_files_in_repo.py guardrail test
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client git && \
    rm -rf /var/lib/apt/lists/*


COPY --from=builder /install /usr/local
COPY . .

# Ensure storage directories exist and are owned by appuser
RUN mkdir -p storage/attachments storage/backups && \
    chown -R appuser:appuser /app

# Configure git system-wide to avoid "dubious ownership" errors in tests
RUN git config --system --add safe.directory /app

# Switch to non-root user
USER appuser

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"]
