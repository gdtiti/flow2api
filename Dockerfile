# Multi-stage build for better security and size optimization
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=app:app . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create necessary directories before switching to non-root user
RUN mkdir -p /app/data /app/tmp /app/logs && \
    chown -R app:app /app/data /app/tmp /app/logs

# Switch to non-root user
USER app

# Health check (simple port check)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

# Expose port
EXPOSE 8000

# Add labels for better metadata
LABEL org.opencontainers.image.title="Flow2API" \
      org.opencontainers.image.description="OpenAI compatible API for Google VideoFX (Veo)" \
      org.opencontainers.image.vendor="Flow2API Community" \
      org.opencontainers.image.license="MIT" \
      org.opencontainers.image.version="latest" \
      org.opencontainers.image.source="https://github.com/thesmallhancat/gdtiti_flow2api"

# Run the application
CMD ["python", "main.py"]
