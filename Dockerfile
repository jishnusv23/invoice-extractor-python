FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libssl-dev \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security (ensure ownership of /app)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Set Prisma cache path to a writable directory
ENV PRISMA_HOME=/app/.prisma
RUN mkdir -p /app/.prisma && chown -R appuser:appuser /app/.prisma

# Switch to non-root user
USER appuser

# Generate Prisma client (Python client code only)
RUN python -m prisma generate

# Expose port (Render will override this, but good practice)
EXPOSE 8000

# Health check (requires curl installed)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
