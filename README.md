# QA Automation Assignment

> Playwright + pytest · Python 3.12 · GitHub Actions CI · Allure Reports

## Prerequisites

- Python 3.11+
- Git
- (Optional) Docker

## Setup (< 5 minutes)

```bash
git clone <repo-url> && cd qa-automation-assignment-<name>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
mkdir -p reports/allure-results logs test-artifacts
```

## Run all tests

```bash
pytest
```

## Run suites separately

```bash
pytest tests/api              # API only
pytest tests/ui               # UI only (sequential)
pytest -m bonus               # bonus scenarios only
```

## Run UI tests in parallel (2 workers)

```bash
pytest tests/ui -n 2
```

## Run with visible browser (for debugging)

```bash
HEADLESS=false pytest tests/ui -n 1
```

## Run via Docker

```bash
docker build -t qa-tests .
docker run --rm qa-tests
# Override command:
docker run --rm qa-tests pytest tests/api -n auto
```

## Configuration via env vars

| Variable            | Default                                | Description                        |
|---------------------|----------------------------------------|------------------------------------|
| `BASE_URL`          | `https://www.saucedemo.com`            | Swag Labs base URL                 |
| `API_BASE_URL`      | `https://jsonplaceholder.typicode.com` | API base URL                       |
| `BROWSER`           | `chromium`                             | `chromium` / `firefox` / `webkit`  |
| `HEADLESS`          | `true`                                 | Set `false` for headed mode        |
| `WORKERS`           | `2`                                    | pytest-xdist worker count          |
| `DEFAULT_TIMEOUT`   | `10000`                                | Playwright default timeout (ms)    |

## View reports

### Allure 3 — live on GitHub Pages (always latest run)
```
https://blumyaron-web.github.io/modelyo/
```

### Allure 3 — generate locally
```bash
# Generate (reads allurerc.mjs → outputs to reports/allure-report/)
npx allure generate reports/allure-results

# Open the Awesome report in your browser
npx allure open reports/allure-report

# Live watch during a test run (updates in real time)
npx allure watch reports/allure-results

# Produce a portable single-file HTML (good for sharing)
npx allure generate reports/allure-results --single-file
```

### pytest-html (offline, single file)
```bash
open reports/report.html
```

## On failure

Artifacts written automatically to `test-artifacts/`:
- `<test-id>.png` — full-page screenshot
- `<test-id>.html` — page DOM at failure time
- `<test-id>.zip` — Playwright trace (open with `playwright show-trace <file>.zip`)

## CI

Latest green run: **<add Actions link after first push>**

**Live Allure report (GitHub Pages):** https://blumyaron-web.github.io/modelyo/

CI artifacts per run (downloadable from Actions):
- `pytest-html-report` — self-contained HTML report
- `allure-report` — full Allure 3 Awesome report (downloadable copy)
- `allure-results` — raw JSON (useful for local re-generation or trend debugging)
- `failure-artifacts` — screenshots + DOM + traces (only on failure)
- `pytest-log` — full DEBUG log
