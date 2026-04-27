"""
generate_summary.py — reads Allure 3 result JSON files and writes a rich
GitHub Actions Job Summary (GITHUB_STEP_SUMMARY) that looks like an embedded
report: status badge, stat counters, collapsible per-test detail rows.

Usage:
    python utils/generate_summary.py \
        --results  reports/allure-results \
        --summary  reports/allure-report/summary.json \
        --report-url https://owner.github.io/repo/awesome/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


# ── Status helpers ────────────────────────────────────────────────────────────

STATUS_ICON = {
    "passed":  "[PASS]",
    "failed":  "[FAIL]",
    "broken":  "[BROKEN]",
    "skipped": "[SKIP]",
    "unknown": "[?]",
}
STATUS_COLOUR = {
    "passed":  "#2ea44f",
    "failed":  "#cf222e",
    "broken":  "#bf8700",
    "skipped": "#6e7781",
    "unknown": "#6e7781",
}

def icon(status: str) -> str:
    return STATUS_ICON.get(status, "[?]")

def ms_to_human(ms: int | float) -> str:
    s = ms / 1000
    if s < 60:
        return f"{s:.2f}s"
    m, s = divmod(s, 60)
    return f"{int(m)}m {s:.0f}s"


# ── Parse allure result files ─────────────────────────────────────────────────

def load_results(results_dir: Path) -> list[dict]:
    tests: list[dict] = []
    for f in sorted(results_dir.glob("*-result.json")):
        try:
            data = json.loads(f.read_text())
            tests.append(data)
        except Exception:
            pass
    return tests


def load_summary(summary_path: Path) -> dict:
    if summary_path.exists():
        try:
            return json.loads(summary_path.read_text())
        except Exception:
            pass
    return {}


# ── HTML builders ─────────────────────────────────────────────────────────────

def stat_badge(label: str, value: int | str, colour: str) -> str:
    return (
        f'<span style="display:inline-block;padding:4px 10px;margin:2px;'
        f'border-radius:6px;background:{colour};color:#fff;font-weight:bold;'
        f'font-size:14px">{label}&nbsp;{value}</span>'
    )

def steps_html(steps: list[dict], depth: int = 0) -> str:
    if not steps:
        return ""
    indent = "&nbsp;" * (depth * 4)
    rows = []
    for step in steps:
        s = step.get("status", "unknown")
        name = step.get("name", "—")
        dur = ms_to_human(step.get("duration", 0))
        rows.append(
            f"<tr><td>{indent}{icon(s)}</td>"
            f"<td><code>{name}</code></td>"
            f"<td align='right'>{dur}</td></tr>"
        )
        rows.append(steps_html(step.get("steps", []), depth + 1))
    return "\n".join(rows)

def test_row_html(test: dict) -> str:
    status   = test.get("status", "unknown")
    name     = test.get("name", "unknown")
    full     = test.get("fullName", "")
    duration = ms_to_human(test.get("duration", 0))
    msg      = (test.get("statusDetails") or {}).get("message", "")
    trace    = (test.get("statusDetails") or {}).get("trace", "")
    steps    = test.get("steps", [])
    flaky    = "[FLAKY] " if test.get("flaky") else ""

    # Steps sub-table
    steps_section = ""
    if steps:
        steps_section = (
            "<table>"
            "<thead><tr><th></th><th>Step</th><th>Duration</th></tr></thead>"
            "<tbody>"
            + steps_html(steps) +
            "</tbody></table>"
        )

    # Error trace
    trace_section = ""
    if msg or trace:
        trace_section = (
            f"<pre style='background:#161b22;color:#e6edf3;padding:8px;"
            f"border-radius:6px;overflow:auto;font-size:12px'>"
            f"{msg}\n{trace}".strip() +
            "</pre>"
        )

    detail_body = steps_section + trace_section or "<em>No details available.</em>"

    summary_line = (
        f"{icon(status)} &nbsp;<strong>{name}</strong> &nbsp;{flaky}"
        f"<code style='float:right;color:#6e7781'>{duration}</code>"
    )

    return (
        f"<tr><td colspan='3'>"
        f"<details{'  open' if status != 'passed' else ''}>"
        f"<summary>{summary_line}</summary>"
        f"<blockquote><small><code>{full}</code></small><br/>{detail_body}</blockquote>"
        f"</details></td></tr>\n"
    )

def build_summary(
    tests: list[dict],
    summary: dict,
    report_url: str,
    run_url: str,
    sha: str,
) -> str:
    stats      = summary.get("stats", {})
    total      = stats.get("total", len(tests))
    passed     = stats.get("passed", sum(1 for t in tests if t.get("status") == "passed"))
    failed     = total - passed
    flaky_cnt  = len(summary.get("flakyTests", []))
    retries    = stats.get("retries", 0)
    duration   = ms_to_human(summary.get("duration", 0))
    overall    = summary.get("status", "unknown")
    suite_name = summary.get("name", "QA Automation Suite")

    headline = "All tests passed" if overall == "passed" else "Some tests failed"

    # Stat table
    badges = (
        f"| Passed | Failed | Total | Flaky | Retries | Time |\n"
        f"|--------|--------|-------|-------|---------|------|\n"
        f"| ✅ {passed} | {'❌' if failed else '✅'} {failed} | {total} | {'⚠️' if flaky_cnt else '✅'} {flaky_cnt} | {retries} | ⏱️ {duration} |"
    )

    # Group tests
    groups: dict[str, list[dict]] = {"failed": [], "broken": [], "passed": [], "skipped": [], "unknown": []}
    for t in tests:
        groups.setdefault(t.get("status", "unknown"), []).append(t)

    sections = ""
    for status in ["failed", "broken", "skipped", "passed", "unknown"]:
        bucket = groups[status]
        if not bucket:
            continue
        open_attr = " open" if status in ("failed", "broken") else ""
        rows = "".join(test_row_html(t) for t in bucket)
        sections += (
            f"<details{open_attr}>"
            f"<summary><strong>{icon(status)} {status.capitalize()} ({len(bucket)})</strong></summary>"
            f"<table><tbody>{rows}</tbody></table>"
            f"</details>\n"
        )

    links = (
        f'<a href="{report_url}">Latest report</a>'
        f" &nbsp;|&nbsp; "
        f'<a href="{report_url}#/history">Per-test history</a>'
        f" &nbsp;|&nbsp; "
        f'<a href="{run_url}">Download artifacts</a>'
    )

    return f"""## {headline}

> **{suite_name}** &nbsp;·&nbsp; commit `{sha[:7]}` &nbsp;·&nbsp; {links}

{badges}

---

{sections}
"""


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results",    default="reports/allure-results")
    parser.add_argument("--summary",    default="reports/allure-report/summary.json")
    parser.add_argument("--report-url", default="")
    parser.add_argument("--run-url",    default="")
    parser.add_argument("--sha",        default="")
    args = parser.parse_args()

    results_dir  = Path(args.results)
    summary_path = Path(args.summary)

    tests   = load_results(results_dir)
    summary = load_summary(summary_path)

    html = build_summary(
        tests      = tests,
        summary    = summary,
        report_url = args.report_url,
        run_url    = args.run_url,
        sha        = args.sha or "unknown",
    )

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(html)
        print("Job summary written.")
    else:
        # Local dev: just print it
        print(html)


if __name__ == "__main__":
    main()
