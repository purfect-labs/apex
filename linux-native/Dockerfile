# Optimized Docker image for APEX CI builds
# Layer ordering optimized for maximum cache efficiency
FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: Install system dependencies (rarely changes - good for caching)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    git \
    curl \
    build-essential \
    file \
    pkg-config \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    gir1.2-webkit2-4.0 \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: Set working directory
WORKDIR /app

# Layer 3: Copy Python requirements first (changes less frequently)
COPY requirements.txt .

# Layer 4: Install Python dependencies (expensive, cache when possible)
RUN pip3 install -r requirements.txt

# Layer 5: Copy build scripts (changes occasionally)
COPY linux-native/build.sh ./linux-native/
COPY linux-native/Dockerfile ./linux-native/
COPY linux-native/docker-compose.yml ./linux-native/

# Layer 6: Copy configuration files (changes occasionally) 
COPY config/ ./config/

# Layer 7: Copy web application (changes frequently)
COPY web/ ./web/

# Layer 8: Copy main application files (changes most frequently - last layer)
COPY apex_app.py .
COPY apex.py .

# Layer 9: Copy native app resources
COPY native/app/ ./native/app/

# Make build script executable
RUN chmod +x ./linux-native/build.sh

# Default command runs build script
CMD ["./linux-native/build.sh"]
