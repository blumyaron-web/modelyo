# ── Stage 1: Python + Playwright + Node (for Allure 3 CLI) + tests ───────
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install Node.js LTS (needed for npx allure — Allure 3 is a pure Node CLI)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cached unless requirements change)
COPY requirements.txt package.json package-lock.json ./
RUN pip install --no-cache-dir -r requirements.txt && npm ci

# Install Chromium (already baked into the base image, but ensure it's current)
RUN playwright install chromium --with-deps

# Copy project (allurerc.mjs is included here)
COPY . .

# Pre-create output directories
RUN mkdir -p reports/allure-results reports/allure-report logs test-artifacts

# ── Default command: full suite + report generation ───────────────────────
# Tests run with 2 workers; report generated via Allure 3 CLI after.
# Override with:  docker run --rm qa-tests pytest tests/api
CMD ["sh", "-c", "pytest tests/ui tests/api -n 2 --tb=short && npx allure generate reports/allure-results"]
