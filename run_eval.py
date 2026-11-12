r"""Measure every collected artifact and produce results.json / results.csv.

    .venv\Scripts\python.exe run_eval.py
    .venv\Scripts\python.exe run_eval.py --models chatgpt gemini
    .venv\Scripts\python.exe run_eval.py --conditions A

Protocol guarantees:
  * The artifact file is never modified. It is copied byte-for-byte into an
    isolated temp directory under a pytest-legal name; its SHA256 is recorded.
  * Each artifact runs in a fresh subprocess with its own cwd, so tests cannot
    leak state into each other.
  * Coverage is pinned to the exact installed file recorded in manifest.json,
    which doubles as the "did the test execute the real source?" detector:
    zero covered lines means the artifact never imported the module under test.

Nothing here repairs a failing artifact. A failure is a datapoint.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
OUT = ROOT / "out"
TIMEOUT_S = 60


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def top_level_names(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    return {
        n.name for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def run_one(path: Path, target: dict) -> dict:
    import_path = target["import_path"]
    installed = Path(target["installed_file"])
    target_names = top_level_names((ROOT / target["source_file"]).read_text(encoding="utf-8"))

    source = path.read_text(encoding="utf-8", errors="replace")
    import_mods: list[str] = []
    test_names: set[str] = set()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                import_mods.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                import_mods.append(node.module)
        test_names = {
            n.name for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
    except SyntaxError:
        pass

    imports_target = any(
        m == import_path or m.startswith(import_path + ".") or import_path.startswith(m + ".")
        for m in import_mods
    )
    reimplemented = len(test_names & target_names)

    tmp = Path(tempfile.mkdtemp(prefix="eval_"))
    try:
        test_copy = tmp / f"test_{path.stem}.py"
        shutil.copyfile(path, test_copy)
        cov_json = tmp / "coverage.json"

        env = dict(os.environ)
        env["PYTHONPATH"] = ""
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [
            sys.executable, "-m", "pytest", test_copy.name,
            "-v", "--tb=short", "-p", "no:cacheprovider",
            f"--cov={import_path}", "--cov-branch",
            f"--cov-report=json:{cov_json}",
        ]
        started = time.time()
        try:
            proc = subprocess.run(
                cmd, cwd=str(tmp), env=env, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S,
            )
            stdout, stderr, rc, timed_out = proc.stdout, proc.stderr, proc.returncode, False
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            stdout = stdout.decode("utf-8", "replace") if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode("utf-8", "replace") if isinstance(stderr, bytes) else stderr
            rc, timed_out = None, True
        elapsed = round(time.time() - started, 3)

        counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        tail = "\n".join(stdout.strip().splitlines()[-8:])
        for key, pat in (
            ("passed", r"(\d+) passed"),
            ("failed", r"(\d+) failed"),
            ("errors", r"(\d+) error"),
            ("skipped", r"(\d+) skipped"),
        ):
            m = re.search(pat, tail)
            if m:
                counts[key] = int(m.group(1))

        collected = counts["passed"] + counts["failed"] + counts["errors"]

        if timed_out:
            kind = "timeout"
            # ``-v`` prints each test before it runs, so the last one is the
            # test that never returned. Keep it: a hang is a real defect.
            hung = re.findall(r"::(\w+)", stdout)
            ran = len(re.findall(r"\b(PASSED|FAILED)\b", stdout))
            detail = (
                f"hung in {hung[-1] if hung else 'unknown'} "
                f"after {ran} completed tests (killed at {TIMEOUT_S}s)"
            )
            # a hang means the suite never finished: report what did run
            counts["passed"] = len(re.findall(r"\bPASSED\b", stdout))
            counts["failed"] = len(re.findall(r"\bFAILED\b", stdout))
            collected = counts["passed"] + counts["failed"]
        elif "error during collection" in stdout or "ERROR collecting" in stdout:
            kind = "collection_error"
            m = re.search(r"E\s+([A-Za-z_]*Error[^\n]*)", stdout)
            detail = (m.group(1) if m else "collection error")[:220]
            # pytest reports the error itself as one "item"; no test executed.
            counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
            collected = 0
        elif counts["errors"] and not collected:
            kind = "collection_error"
            m = re.search(r"E\s+([A-Za-z_]*Error[^\n]*)", stdout)
            detail = (m.group(1) if m else "error")[:220]
            counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
            collected = 0
        elif counts["failed"]:
            kind = "assertion_failure"
            m = re.search(r"^FAILED\s+(\S+?)(?:\s+-\s+(.*))?$", stdout, re.MULTILINE)
            detail = f"{m.group(1)}: {(m.group(2) or '').strip()}"[:220] if m else "failed"
        elif collected == 0:
            kind, detail = "no_tests", "pytest collected 0 tests"
        else:
            kind, detail = "none", ""

        pass_rate = round(counts["passed"] / collected, 4) if collected else None

        coverage = {"target_imported": False, "coverage_pct": None,
                    "statements": None, "covered_lines": None,
                    "num_branches": None, "covered_branches": None}
        if cov_json.exists():
            try:
                data = json.loads(cov_json.read_text(encoding="utf-8"))
                want = os.path.normcase(str(installed))
                for key, payload in (data.get("files") or {}).items():
                    if os.path.normcase(str(Path(key))) != want:
                        continue
                    s = payload.get("summary", {})
                    covered = int(s.get("covered_lines", 0) or 0)
                    coverage = {
                        "target_imported": covered > 0,
                        "coverage_pct": s.get("percent_covered"),
                        "statements": s.get("num_statements"),
                        "covered_lines": covered,
                        "num_branches": s.get("num_branches"),
                        "covered_branches": s.get("covered_branches"),
                    }
                    break
            except (json.JSONDecodeError, OSError):
                pass

        return {
            **coverage,
            "model": path.parent.parent.name,
            "condition": path.parent.name,
            "module": target["id"],
            "file": str(path.relative_to(GENERATED)),
            "lines": len(source.splitlines()),
            "collected": collected,
            "passed": counts["passed"],
            "failed": counts["failed"],
            "errors": counts["errors"],
            "pass_rate": pass_rate,
            "imports_target": imports_target,
            "reimplemented_names": reimplemented,
            "imports": ";".join(sorted(set(import_mods))[:8]),
            "failure_kind": kind,
            "failure_detail": detail,
            "exit_code": rc,
            "duration_s": elapsed,
            "sha256": sha256(path),
            "stdout_tail": "\n".join(stdout.strip().splitlines()[-6:]),
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--conditions", nargs="*", default=None)
    args = ap.parse_args()

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    by_slug = {t["id"].replace(".", "_"): t for t in manifest["targets"]}

    artifacts = []
    for path in sorted(GENERATED.glob("*/*/*.py")):
        if any(part.startswith("_") for part in path.relative_to(GENERATED).parts):
            continue
        if path.stat().st_size == 0:
            continue
        model, condition = path.parent.parent.name, path.parent.name
        if args.models and model not in args.models:
            continue
        if args.conditions and condition not in args.conditions:
            continue
        target = by_slug.get(path.stem)
        if not target:
            print(f"[skip] unknown module slug: {path.relative_to(GENERATED)}")
            continue
        artifacts.append((path, target))

    print(f"measuring {len(artifacts)} artifacts\n")
    rows = []
    for i, (path, target) in enumerate(artifacts, 1):
        row = run_one(path, target)
        rows.append(row)
        print(
            f"[{i:>2}/{len(artifacts)}] {row['model']:>7}/{row['condition']} "
            f"{row['module']:<22} collected={row['collected']:>3} "
            f"passed={row['passed']:>3} fail={row['failed']:>3} "
            f"cov={row['coverage_pct']} target={row['target_imported']} {row['failure_kind']}"
        )

    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(
        json.dumps({"manifest": manifest, "results": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    cols = [
        "model", "condition", "module", "lines", "collected", "passed", "failed",
        "errors", "pass_rate", "target_imported", "coverage_pct", "statements",
        "covered_lines", "num_branches", "covered_branches", "imports_target",
        "reimplemented_names", "failure_kind", "failure_detail", "duration_s",
        "sha256", "file",
    ]
    with (OUT / "results.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nwrote {OUT/'results.json'} and {OUT/'results.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
