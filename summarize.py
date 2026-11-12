r"""Aggregate out/results.json into thesis-ready summary tables.

    .venv\Scripts\python.exe summarize.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"


def pct(x, n):
    return f"{100 * x / n:.1f}%" if n else "n/a"


def main() -> int:
    data = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    rows = data["results"]

    # Full statement count per module, taken from any run that did import it,
    # so artifacts that failed to import still contribute their denominator.
    module_statements: dict[str, int] = {}
    for r in rows:
        if r.get("statements"):
            module_statements.setdefault(r["module"], r["statements"])

    groups = defaultdict(list)
    for r in rows:
        groups[(r["model"], r["condition"])].append(r)

    print("=" * 78)
    print("PER MODEL x CONDITION")
    print("=" * 78)
    header = (
        f"{'model':<9}{'cond':<6}{'n':>3}{'exec':>6}{'tests':>7}{'pass':>7}"
        f"{'pass%':>8}{'import':>8}{'cov%':>8}{'yield%':>8}{'timeout':>9}{'collerr':>9}"
    )
    print(header)
    print("-" * 86)
    for (model, cond), rs in sorted(groups.items()):
        n = len(rs)
        executed = sum(1 for r in rs if (r["collected"] or 0) > 0)
        tests = sum(r["collected"] or 0 for r in rs)
        passed = sum(r["passed"] or 0 for r in rs)
        imported = sum(1 for r in rs if r["target_imported"])
        covered = [r for r in rs if r["target_imported"]]
        cov = sum(r["coverage_pct"] for r in covered) / len(covered) if covered else None
        # Coverage yield: aggregate over ALL artifacts, non-imported counts as 0.
        # Unlike the mean over imported-only, this cannot be inflated by
        # artefacts that failed to import and were therefore excluded.
        tot_stmt = sum(
            (r["statements"] or module_statements.get(r["module"], 0)) for r in rs
        )
        tot_cov = sum(r["covered_lines"] or 0 for r in rs)
        yield_pct = 100 * tot_cov / tot_stmt if tot_stmt else None
        timeout = sum(1 for r in rs if r["failure_kind"] == "timeout")
        collerr = sum(1 for r in rs if r["failure_kind"] == "collection_error")
        print(
            f"{model:<9}{cond:<6}{n:>3}{executed:>6}{tests:>7}{passed:>7}"
            f"{pct(passed, tests):>8}{pct(imported, n):>8}"
            f"{(f'{cov:.1f}' if cov is not None else 'n/a'):>8}"
            f"{(f'{yield_pct:.1f}' if yield_pct is not None else 'n/a'):>8}"
            f"{timeout:>9}{collerr:>9}"
        )

    print()
    print("=" * 78)
    print("FAILURE MODE COUNTS")
    print("=" * 78)
    kinds = Counter()
    for r in rows:
        kinds[(r["model"], r["condition"], r["failure_kind"])] += 1
    for (model, cond, kind), c in sorted(kinds.items()):
        print(f"{model:<9}{cond:<6}{kind:<20}{c:>3}")

    print()
    print("=" * 78)
    print("ARTIFACTS WITHOUT TARGET COVERAGE")
    print("=" * 78)
    for r in rows:
        if not r["target_imported"]:
            print(
                f"{r['model']:<9}{r['condition']:<6}{r['module']:<24}"
                f"{r['failure_kind']:<18}{r['failure_detail'][:70]}"
            )

    print()
    print("=" * 78)
    print("COVERAGE DETAIL (target imported)")
    print("=" * 78)
    for r in sorted(rows, key=lambda x: (x["model"], x["condition"], x["module"])):
        if not r["target_imported"]:
            continue
        b = (
            f"{r['covered_branches']}/{r['num_branches']}"
            if r["num_branches"] is not None else "-"
        )
        print(
            f"{r['model']:<9}{r['condition']:<6}{r['module']:<24}"
            f"stmt {r['covered_lines']:>4}/{r['statements']:<4}"
            f"branch {b:<8} pass {r['passed']:>3}/{r['collected']:<4}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
