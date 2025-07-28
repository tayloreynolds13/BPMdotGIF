FROM python:3.9-slim

# Install system dependencies for pygame and display
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual display for pygame
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY railway_requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Start command with virtual display
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & python gif_bpm_sync_tool_v2.py"] 