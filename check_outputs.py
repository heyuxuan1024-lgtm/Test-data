r"""Sanity-check the manually collected model outputs before measurement.

    .venv\Scripts\python.exe check_outputs.py

For every non-empty file under generated/ this reports:
  * whether it parses as Python (catches truncated pastes),
  * whether markdown code fences were pasted by mistake,
  * which modules it imports (catches the "no import at all" case).

It never modifies the files: a broken artifact is data, not a mistake to repair.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    by_slug = {
        t["id"].replace(".", "_"): t["id"] for t in manifest["targets"]
    }

    total = 0
    problems = 0
    for path in sorted(GENERATED.rglob("*.py")):
        # Directories starting with "_" hold audit copies, never measured.
        if any(part.startswith("_") for part in path.relative_to(GENERATED).parts):
            continue
        size = path.stat().st_size
        if size == 0:
            continue
        total += 1
        rel = path.relative_to(GENERATED)
        text = path.read_text(encoding="utf-8", errors="replace")
        notes: list[str] = []

        if "```" in text:
            notes.append("MARKDOWN_FENCE")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            notes.append(f"SYNTAX_ERROR line {exc.lineno}: {exc.msg}")
            tree = None

        imports: list[str] = []
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)

        target = by_slug.get(path.stem)
        if target and imports:
            short = target.split(".")[0]
            if not any(i == target or i.startswith(short) for i in imports):
                notes.append(f"DOES_NOT_IMPORT_{target}")

        if notes:
            problems += 1
        flag = ", ".join(notes) if notes else "OK"
        print(f"{str(rel):<44} {len(text.splitlines()):>5} lines  {flag}")

    print(f"\n非空产物: {total} 个，有问题: {problems} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
