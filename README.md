# modelyo — QA Automation Suite

Python · Playwright · pytest · GitHub Actions · Allure 3

[![Tests](https://github.com/blumyaron-web/modelyo/actions/workflows/tests.yml/badge.svg)](https://github.com/blumyaron-web/modelyo/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure-live%20report-brightgreen)](https://blumyaron-web.github.io/modelyo/)

---

## What's covered

| Suite | Scenarios |
|---|---|
| **UI — Login** | Happy-path login; invalid-credential error message |
| **UI — Cart** | Add ≥2 items; badge count; cart contents and prices |
| **UI — Checkout** | End-to-end: add → cart → info → overview → confirmation |
| **UI — Bonus** | Price sort (low→high); badge increments and decrements |
| **API — GET /posts** | 200 + array schema; single item by id; 404 for unknown id |
| **API — CRUD /posts** | POST 201 + echo; PUT 200 + updated fields; DELETE 200/204 |

---

## Project structure

```
modelyo/
├── src/
│   ├── clients/        # HTTP client (httpx wrapper)
│   ├── config/         # Environment config (all values from env vars)
│   ├── flows/          # Business-logic flows + assertpy soft assertions
│   ├── pages/          # Page Object Model (Playwright)
│   └── utils/          # CI scripts (Allure summary, redirect)
├── tests/
│   ├── api/            # REST API tests
│   └── ui/             # Browser tests
├── conftest.py         # pytest fixtures (browser, page, api_client)
├── pytest.ini          # pytest config + marker registry
├── allurerc.mjs        # Allure 3 report config
├── Dockerfile
└── requirements.txt
```

**Key design choices:**
- `src/` on `pythonpath` — packages are importable without installation
- Tests are pure orchestration — all assertions live in `flows/`
- `assertpy` soft assertions — every check in a block runs before failing
- POM selectors use `data-test` attributes exclusively — stable across style changes
- Fresh `BrowserContext` per test — no shared cookies or session state

---

## Setup

**Requirements:** Python 3.11+, Node.js (for Allure CLI), Git

```bash
git clone https://github.com/blumyaron-web/modelyo.git && cd modelyo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
npm ci
mkdir -p reports/allure-results logs test-artifacts
```

---

## Running tests

```bash
# Full suite
pytest

# By layer
pytest tests/api
pytest tests/ui

# By marker
pytest -m smoke
pytest -m "api and crud"
pytest -m "ui and regression and not bonus"

# Parallel workers
pytest tests/api -n auto
pytest tests/ui -n 2

# Headed browser (local debugging)
HEADLESS=false pytest tests/ui -n 1 --tb=long
```

### Available markers

| Dimension | Markers |
|---|---|
| Business domain | `authentication` `catalog` `cart` `checkout` `posts` |
| Tech layer | `ui` `api` `playwright` `rest` |
| QA method | `smoke` `regression` `e2e` `schema_validation` `crud` `boundary` `bonus` |

---

## Reports

### Allure 3 — live on GitHub Pages
```
https://blumyaron-web.github.io/modelyo/
```
Published automatically on every CI run. Trend charts accumulate across runs via `gh-pages` history carry-forward.

### Allure 3 — generate locally
```bash
npx allure awesome reports/allure-results \
  --output reports/allure-report \
  --name "QA Automation Suite" \
  --lang en

open reports/allure-report/index.html

# Live watch during a run
npx allure watch reports/allure-results
```

### pytest-html (offline, single file)
```bash
open reports/report.html
```

---

## Failure artifacts

On any test failure, the following are written to `test-artifacts/` and uploaded to the CI run:

| File | Contents |
|---|---|
| `<test-id>.png` | Full-page screenshot at point of failure |
| `<test-id>.html` | Page DOM — inspect state without a browser |
| `<test-id>.zip` | Playwright trace — open with `playwright show-trace <file>.zip` |

---

## Configuration

All values are read from environment variables. Defaults work out of the box locally.

| Variable | Default | Description |
|---|---|---|
| `BASE_URL` | `https://www.saucedemo.com` | Swag Labs base URL |
| `API_BASE_URL` | `https://jsonplaceholder.typicode.com` | REST API base URL |
| `BROWSER` | `chromium` | `chromium` / `firefox` / `webkit` |
| `HEADLESS` | `true` | Set `false` for headed mode |
| `DEFAULT_TIMEOUT` | `10000` | Playwright action timeout (ms) |
| `NAVIGATION_TIMEOUT` | `15000` | Playwright navigation timeout (ms) |
| `ARTIFACT_DIR` | `test-artifacts` | Output path for failure artifacts |

---

## Docker

```bash
docker build -t modelyo-qa .
docker run --rm modelyo-qa

# Run a specific suite
docker run --rm modelyo-qa pytest tests/api -n auto --tb=short
```

---

## CI

GitHub Actions runs on every push and pull request to `main`.

**Pipeline steps:**
1. Install Python deps + Node deps (Allure CLI)
2. Install Chromium
3. Run API tests (`-n auto`)
4. Run UI tests (`-n 2`, headless)
5. Generate Allure 3 report with history carry-forward
6. Write GitHub Actions Job Summary
7. Publish report to GitHub Pages
8. Upload artifacts: `pytest-html-report`, `allure-report`, `allure-results`, `failure-artifacts`, `pytest-log`

See [`DESIGN.md`](DESIGN.md) for architectural decisions and trade-off rationale.

