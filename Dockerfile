FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent/ ./agent/
COPY mcp_server/ ./mcp_server/

# Create data directory for persistence
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set DOCKER_HOST to avoid SDK initialization issues
ENV DOCKER_HOST=unix:///var/run/docker.sock

# Run the application
CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
