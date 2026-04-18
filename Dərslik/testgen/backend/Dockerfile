FROM python:3.12-slim

WORKDIR /app

# System deps: build tools, postgres client, pandoc (for Word export),
# and Chromium runtime libs (for Playwright PDF export).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc pandoc \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0 \
    libx11-6 libxcb1 libxext6 libxrender1 \
    fonts-liberation fonts-noto-core fonts-noto-cjk && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's bundled Chromium browser
RUN python -m playwright install chromium

COPY . .

RUN chmod +x entrypoint.sh

CMD ["/bin/bash", "entrypoint.sh"]
