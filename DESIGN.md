# Design Rationale

## Language and framework choice

**Python + Playwright + pytest.**  
Python was chosen for its concise syntax and the richest Playwright ecosystem (auto-waits, built-in tracing, first-class async support). pytest's fixture model maps naturally onto the assignment's isolation requirements, and `pytest-xdist` adds parallelism with a single flag.

Playwright over Selenium: Playwright ships with built-in auto-waiting on every action, a trace viewer for failure triage, and native network interception — all things we would have to bolt on manually with Selenium. Selenium remains the right choice when: (a) the target browser is IE/legacy Edge, (b) the organisation already owns a Selenium Grid and migration cost isn't justified, or (c) deep WebDriver-level control is required (e.g. Chrome DevTools Protocol via vendor-specific extensions).

For the API layer, `httpx` was chosen over `requests` for its cleaner type annotations and identical sync API — making a future async migration trivial.

## Anti-flakiness strategy

Concrete techniques used:
- **No `time.sleep` anywhere.** Every wait is condition-based (Playwright auto-waits on `.click()`, `.fill()`, `.wait_for()`).
- **`data-test` attributes first.** Swag Labs exposes them on every interactive element; they survive styling refactors. Implemented via a single `get_by_test_id()` override in `BasePage` using `[data-test="…"]` CSS — one place to change the attribute name globally.
- **Fresh browser context per test.** Each test gets isolated cookies, localStorage, and session state — no bleed between parallel workers.
- **Tracing enabled for every test**, saved only on failure — zero overhead in the green path.
- **`pytest-rerunfailures` (2 retries, 2s delay)** guards against transient network hiccups on CI without masking real failures — any test that fails all 3 attempts is a genuine bug. Tests that retry are flagged in the Allure report with a `flaky` indicator.

At scale (1000+ tests): add quarantine tagging (known-flaky tests run in a separate `flaky` job and never block the main gate), record retry counts in the report, and use a flakiness heatmap (test × failure count over rolling 30 days) to prioritise fixes.

## Parallelism and isolation

Tests are isolated by browser context: each `browser_context` fixture creates a fresh Playwright context (separate process equivalent). The `browser` fixture is session-scoped — one browser process shared across workers — which is safe because contexts are completely isolated.

`pytest-xdist` distributes test files across workers. What breaks first at higher parallelism: shared output directories (solved here by writing artifacts with a test-node-id-derived filename), and external rate limits on the target site (mitigated by not hammering the same login endpoint in tight loops).

## Reporting and triage

If a test fails at 3am the on-call engineer opens the GitHub Actions run, downloads `failure-artifacts`, and finds:
1. **Screenshot** (`<test-id>.png`) — first visual of what went wrong.
2. **DOM dump** (`<test-id>.html`) — inspect the exact page state, no browser needed.
3. **Playwright trace** (`<test-id>.zip`) — open with `playwright show-trace` for a step-by-step timeline with network, console, and DOM snapshots.
4. **pytest log** — structured DEBUG log covering every HTTP request/response and every page action.
5. **Allure 3 Awesome report** — `allure-html-report` artifact; `singleFile: true` in `allurerc.mjs` means a single `index.html` — no web server needed, works offline, readable by non-engineers. The Awesome UI shows pass/fail per step, retry history, and links directly to the attached screenshot. At scale, the Allure trend chart surfaces regression introductions across builds with no extra tooling. Allure 3 (Node.js CLI, `npx allure`) replaces the Java-based Allure 2 — no JDK required in CI.

The pytest-html report is self-contained (single file) and readable offline — useful for sharing with non-engineers.

## What I would build next

**Retry + quarantine infrastructure.** A `pytest-rerunfailures`-backed retry on CI (max 2 retries) with automatic tagging of tests that needed a retry. Anything that fails twice and only passes on retry enters the quarantine job automatically. This is the single highest-ROI investment once the suite grows past ~50 tests, because it separates genuine product bugs from environmental noise without any manual triage.

## AI tooling

GitHub Copilot was used to accelerate boilerplate (fixture scaffolding, type annotations). All architectural decisions, selector strategy, and test logic were authored and reviewed by hand.
