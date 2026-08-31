FROM python:3.12-slim

# Security: run as non-root
RUN groupadd -r procurex && useradd -r -g procurex procurex

WORKDIR /app

# System dependencies for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for temp processing (never store secrets here)
RUN mkdir -p /tmp/procurex && chown -R procurex:procurex /tmp/procurex /app

# Switch to non-root user
USER procurex

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entry point
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
