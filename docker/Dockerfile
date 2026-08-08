# ==============================================================================
# Production Dockerfile for AI Subtitle Generator Application
# Contains Debian Linux + System FFmpeg + PyTorch + OpenAI Whisper + FastAPI
# ==============================================================================

# Base image: Official lightweight Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk and disable stdout buffering
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set container working directory
WORKDIR /app

# Install system dependencies (FFmpeg for audio extraction and Git for Whisper download)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml configuration file
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir git+https://github.com/openai/whisper.git && \
    pip install --no-cache-dir fastapi uvicorn[standard] python-multipart ffmpeg-python pysrt

# Copy source code into the container
COPY src/ /app/src/

# Install the local python package
RUN pip install --no-cache-dir -e /app/src/video_captioning

# Expose port 8000 for incoming HTTP web traffic
EXPOSE 8000

# Start production Uvicorn web server
CMD ["uvicorn", "video_captioning.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
