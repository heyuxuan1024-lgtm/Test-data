r"""Generate the thesis figures from out/results.json.

    .venv\Scripts\python.exe make_figures.py

Writes PNGs to out/figures/. Labels are in English on purpose: CJK fonts are
not guaranteed to exist on the machine that renders the thesis.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
FIGS = OUT / "figures"

MODELS = ["claude", "chatgpt", "gemini"]
CONDS = ["A", "B"]
COLORS = {"A": "#9aa5b1", "B": "#2f6db3"}
MODEL_COLORS = {"claude": "#d97706", "chatgpt": "#10a37f", "gemini": "#4285f4"}


def classify(r: dict) -> str:
    kind = r["failure_kind"]
    detail = r.get("failure_detail") or ""
    if kind == "none":
        return "no failure"
    if kind == "timeout":
        return "hang / infinite loop"
    if kind == "collection_error":
        if "ModuleNotFoundError" in detail or "ImportError" in detail:
            return "import failure"
        if "SyntaxError" in detail or "IndentationError" in detail:
            return "syntax / truncation"
        return "other collection error"
    if kind == "assertion_failure":
        return "assertion failure"
    return kind


def aggregates(rows):
    module_statements = {}
    for r in rows:
        if r.get("statements"):
            module_statements.setdefault(r["module"], r["statements"])
    out = {}
    for m in MODELS:
        for c in CONDS:
            rs = [r for r in rows if r["model"] == m and r["condition"] == c]
            if not rs:
                continue
            tests = sum(r["collected"] or 0 for r in rs)
            passed = sum(r["passed"] or 0 for r in rs)
            stmt = sum((r["statements"] or module_statements.get(r["module"], 0)) for r in rs)
            cov = sum(r["covered_lines"] or 0 for r in rs)
            out[(m, c)] = {
                "yield": 100 * cov / stmt if stmt else 0,
                "pass": 100 * passed / tests if tests else 0,
                "tests": tests,
                "exec": sum(1 for r in rs if (r["collected"] or 0) > 0),
                "imported": sum(1 for r in rs if r["target_imported"]),
                "n": len(rs),
            }
    return out


def fig_yield(agg):
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.36
    x = range(len(MODELS))
    for i, c in enumerate(CONDS):
        vals = [agg[(m, c)]["yield"] for m in MODELS]
        bars = ax.bar([p + (i - 0.5) * width for p in x], vals, width, label=f"Condition {c}", color=COLORS[c])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}", ha="center", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([m.capitalize() for m in MODELS])
    ax.set_ylabel("Coverage yield (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Coverage yield by model and prompt condition")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig1_coverage_yield.png", dpi=160)
    plt.close(fig)


def fig_tests_vs_yield(rows):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for m in MODELS:
        for c in CONDS:
            pts = [r for r in rows if r["model"] == m and r["condition"] == c]
            xs = [r["collected"] or 0 for r in pts]
            ys = [r["coverage_pct"] if r["target_imported"] else 0 for r in pts]
            ax.scatter(xs, ys, s=34, alpha=0.75, color=MODEL_COLORS[m],
                       marker="o" if c == "A" else "s",
                       label=f"{m.capitalize()} {c}")
    ax.set_xlabel("Number of tests collected")
    ax.set_ylabel("Statement coverage (%)")
    ax.set_title("Test volume vs achieved coverage (one point per artifact)")
    ax.set_ylim(-3, 105)
    ax.legend(fontsize=7, frameon=False, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig2_volume_vs_coverage.png", dpi=160)
    plt.close(fig)


def fig_failure_modes(rows):
    tax = defaultdict(Counter)
    for r in rows:
        tax[(r["model"], r["condition"])][classify(r)] += 1
    kinds = ["no failure", "assertion failure", "import failure",
             "hang / infinite loop", "syntax / truncation", "other collection error"]
    kinds = [k for k in kinds if any(tax[key].get(k) for key in tax)]
    labels = [f"{m.capitalize()}-{c}" for m in MODELS for c in CONDS]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bottom = [0] * len(labels)
    cmap = plt.get_cmap("Set2")
    for i, k in enumerate(kinds):
        vals = [tax[(m, c)].get(k, 0) for m in MODELS for c in CONDS]
        ax.bar(labels, vals, bottom=bottom, label=k, color=cmap(i % 8))
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_ylabel("Artifacts")
    ax.set_title("Failure modes per model and condition")
    ax.legend(fontsize=7, frameon=False, ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig3_failure_modes.png", dpi=160)
    plt.close(fig)


def fig_pass_rate(agg):
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.36
    x = range(len(MODELS))
    for i, c in enumerate(CONDS):
        vals = [agg[(m, c)]["pass"] for m in MODELS]
        bars = ax.bar([p + (i - 0.5) * width for p in x], vals, width, label=f"Condition {c}", color=COLORS[c])
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.1f}", ha="center", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([m.capitalize() for m in MODELS])
    ax.set_ylabel("Test pass rate (%)")
    ax.set_ylim(70, 102)
    ax.set_title("Pass rate by model and prompt condition")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGS / "fig4_pass_rate.png", dpi=160)
    plt.close(fig)


def main() -> int:
    FIGS.mkdir(parents=True, exist_ok=True)
    rows = json.loads((OUT / "results.json").read_text(encoding="utf-8"))["results"]
    agg = aggregates(rows)
    fig_yield(agg)
    fig_tests_vs_yield(rows)
    fig_failure_modes(rows)
    fig_pass_rate(agg)
    print("figures ->", FIGS)
    for p in sorted(FIGS.glob("*.png")):
        print(" ", p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
