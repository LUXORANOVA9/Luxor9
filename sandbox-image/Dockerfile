# sandbox-image/Dockerfile

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Languages
    python3 python3-pip python3-venv \
    nodejs npm \
    # Browser
    chromium-browser \
    # Display (for headed browser)
    xvfb \
    # Utilities
    curl wget git jq unzip zip tar \
    ripgrep fd-find bat \
    # Media
    ffmpeg imagemagick \
    # Documents
    pandoc \
    # Network
    dnsutils \
    # Build
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python packages
RUN pip3 install --break-system-packages \
    requests httpx beautifulsoup4 \
    pandas numpy matplotlib seaborn plotly \
    openpyxl python-docx PyPDF2 \
    flask fastapi uvicorn \
    Pillow \
    rich pydantic \
    lxml cssselect

# Node packages
RUN npm install -g \
    playwright \
    typescript ts-node \
    live-server

# Playwright browser
RUN npx playwright install chromium --with-deps

# Create user
RUN useradd -m -s /bin/bash -u 1000 agent
RUN echo "agent ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER agent
WORKDIR /home/agent/workspace

ENV DISPLAY=:99
ENV PATH="/home/agent/.local/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sleep", "infinity"]
