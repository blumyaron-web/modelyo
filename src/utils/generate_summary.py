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
from dataclasses import dataclass, field
from pathlib import Path


# ── Constants ─────────────────────────────────────────────────────────────────

STATUS_ICON: dict[str, str] = {
    "passed":  "[PASS]",
    "failed":  "[FAIL]",
    "broken":  "[BROKEN]",
    "skipped": "[SKIP]",
    "unknown": "[?]",
}

# Render order for test-group sections (most critical first)
STATUS_ORDER = ["failed", "broken", "skipped", "passed", "unknown"]

# Statuses whose detail sections start expanded
STATUS_EXPANDED = {"failed", "broken"}


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class SuiteStats:
    total:      int
    passed:     int
    failed:     int
    flaky:      int
    retries:    int
    duration:   str          # human-readable, e.g. "3.18s"
    overall:    str          # "passed" | "failed" | …
    suite_name: str
    sha:        str
    groups:     dict[str, list[dict]] = field(default_factory=dict)


@dataclass
class ReportLinks:
    report_url: str
    run_url:    str


# ── Loading ───────────────────────────────────────────────────────────────────

def load_results(results_dir: Path) -> list[dict]:
    tests: list[dict] = []
    for f in sorted(results_dir.glob("*-result.json")):
        try:
            tests.append(json.loads(f.read_text()))
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


# ── Aggregation ───────────────────────────────────────────────────────────────

def ms_to_human(ms: int | float) -> str:
    s = ms / 1000
    if s < 60:
        return f"{s:.2f}s"
    m, s = divmod(s, 60)
    return f"{int(m)}m {s:.0f}s"


def aggregate(tests: list[dict], summary: dict, sha: str) -> SuiteStats:
    stats  = summary.get("stats", {})
    total  = stats.get("total", len(tests))
    passed = stats.get("passed", sum(1 for t in tests if t.get("status") == "passed"))

    groups: dict[str, list[dict]] = {s: [] for s in STATUS_ORDER}
    for t in tests:
        groups.setdefault(t.get("status", "unknown"), []).append(t)

    return SuiteStats(
        total      = total,
        passed     = passed,
        failed     = total - passed,
        flaky      = len(summary.get("flakyTests", [])),
        retries    = stats.get("retries", 0),
        duration   = ms_to_human(summary.get("duration", 0)),
        overall    = summary.get("status", "unknown"),
        suite_name = summary.get("name", "QA Automation Suite"),
        sha        = sha,
        groups     = groups,
    )


# ── Rendering ─────────────────────────────────────────────────────────────────

def _icon(status: str) -> str:
    return STATUS_ICON.get(status, "[?]")


def _render_steps(steps: list[dict], depth: int = 0) -> str:
    if not steps:
        return ""
    indent = "&nbsp;" * (depth * 4)
    rows = []
    for step in steps:
        s   = step.get("status", "unknown")
        dur = ms_to_human(step.get("duration", 0))
        rows.append(
            f"<tr><td>{indent}{_icon(s)}</td>"
            f"<td><code>{step.get('name', '—')}</code></td>"
            f"<td align='right'>{dur}</td></tr>"
        )
        rows.append(_render_steps(step.get("steps", []), depth + 1))
    return "\n".join(rows)


def _render_test_row(test: dict) -> str:
    status   = test.get("status", "unknown")
    name     = test.get("name", "unknown")
    full     = test.get("fullName", "")
    duration = ms_to_human(test.get("duration", 0))
    details  = test.get("statusDetails") or {}
    msg      = details.get("message", "")
    trace    = details.get("trace", "")
    steps    = test.get("steps", [])
    flaky    = "[FLAKY] " if test.get("flaky") else ""

    steps_block = (
        "<table>"
        "<thead><tr><th></th><th>Step</th><th>Duration</th></tr></thead>"
        "<tbody>" + _render_steps(steps) + "</tbody></table>"
    ) if steps else ""

    trace_block = (
        f"<pre style='background:#161b22;color:#e6edf3;padding:8px;"
        f"border-radius:6px;overflow:auto;font-size:12px'>"
        + f"{msg}\n{trace}".strip() + "</pre>"
    ) if (msg or trace) else ""

    body = steps_block + trace_block or "<em>No details available.</em>"
    summary_line = (
        f"{_icon(status)} &nbsp;<strong>{name}</strong> &nbsp;{flaky}"
        f"<code style='float:right;color:#6e7781'>{duration}</code>"
    )
    open_attr = "  open" if status != "passed" else ""

    return (
        f"<tr><td colspan='3'>"
        f"<details{open_attr}><summary>{summary_line}</summary>"
        f"<blockquote><small><code>{full}</code></small><br/>{body}</blockquote>"
        f"</details></td></tr>\n"
    )


def _render_stat_table(s: SuiteStats) -> str:
    return (
        f"| Passed | Failed | Total | Flaky | Retries | Time |\n"
        f"|--------|--------|-------|-------|---------|------|\n"
        f"| ✅ {s.passed}"
        f" | {'❌' if s.failed else '✅'} {s.failed}"
        f" | {s.total}"
        f" | {'⚠️' if s.flaky else '✅'} {s.flaky}"
        f" | {s.retries}"
        f" | ⏱️ {s.duration} |"
    )


def _render_test_sections(groups: dict[str, list[dict]]) -> str:
    sections = ""
    for status in STATUS_ORDER:
        bucket = groups.get(status, [])
        if not bucket:
            continue
        open_attr = " open" if status in STATUS_EXPANDED else ""
        rows = "".join(_render_test_row(t) for t in bucket)
        sections += (
            f"<details{open_attr}>"
            f"<summary><strong>{_icon(status)} {status.capitalize()} ({len(bucket)})</strong></summary>"
            f"<table><tbody>{rows}</tbody></table>"
            f"</details>\n"
        )
    return sections


def _render_links(links: ReportLinks) -> str:
    return (
        f'<a href="{links.report_url}">Latest report</a>'
        f" &nbsp;|&nbsp; "
        f'<a href="{links.report_url}#/history">Per-test history</a>'
        f" &nbsp;|&nbsp; "
        f'<a href="{links.run_url}">Download artifacts</a>'
    )


def render(stats: SuiteStats, links: ReportLinks) -> str:
    headline = "All tests passed" if stats.overall == "passed" else "Some tests failed"
    return (
        f"## {headline}\n\n"
        f"> **{stats.suite_name}** &nbsp;·&nbsp; commit `{stats.sha[:7]}`"
        f" &nbsp;·&nbsp; {_render_links(links)}\n\n"
        f"{_render_stat_table(stats)}\n\n"
        f"---\n\n"
        f"{_render_test_sections(stats.groups)}\n"
    )


# ── Output ────────────────────────────────────────────────────────────────────

def write_summary(html: str) -> None:
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as f:
            f.write(html)
        print("Job summary written.")
    else:
        print(html)  # local dev fallback


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results",    default="reports/allure-results")
    parser.add_argument("--summary",    default="reports/allure-report/summary.json")
    parser.add_argument("--report-url", default="")
    parser.add_argument("--run-url",    default="")
    parser.add_argument("--sha",        default="")
    args = parser.parse_args()

    tests   = load_results(Path(args.results))
    summary = load_summary(Path(args.summary))
    stats   = aggregate(tests, summary, sha=args.sha or "unknown")
    links   = ReportLinks(report_url=args.report_url, run_url=args.run_url)

    write_summary(render(stats, links))


if __name__ == "__main__":
    main()
