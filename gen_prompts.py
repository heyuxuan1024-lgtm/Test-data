r"""Generate ready-to-paste prompt files for the A/B experiment.

    .venv\Scripts\python.exe gen_prompts.py

Condition A ("underspecified", the prompt already used) and condition B
("specified") differ ONLY by the extra specification lines. Everything else --
including the "return only code, no inline comments" clause -- is kept
byte-identical between the two, so the A/B comparison isolates one variable:
how much the prompt says about the module.

Output: prompts/A/<id>.md and prompts/B/<id>.md, plus prompts/INDEX.md.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPTS = ROOT / "prompts"

BASE_TEMPLATE = """Please write a complete, fully executable pytest unit test suite for the following Python source code. Ensure high statement and branch coverage, and explicitly include tests for edge cases and potential exceptions. Return only the python code without any inline comments.
{extra}
Source Code:
{code}"""

SPECIFIED_EXTRA = """
Additional requirements:
- The module under test is importable as `{import_path}` and is already installed on sys.path.
- Your test file must access it exactly this way: `{import_stmt}`. Do NOT copy, restate, or re-implement any part of the source code inside the test file; every assertion must go through the imported module.
- Name the test file `{test_filename}`.
- Use only the Python standard library and pytest. Do not import any other third-party package.
- Do not add an `if __name__ == "__main__"` block.
"""


def import_stmt(import_path: str) -> str:
    if "." in import_path:
        pkg, name = import_path.split(".", 1)
        return f"from {pkg} import {name}"
    return f"import {import_path}"


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    (PROMPTS / "A").mkdir(parents=True, exist_ok=True)
    (PROMPTS / "B").mkdir(parents=True, exist_ok=True)

    index_rows = []
    for target in manifest["targets"]:
        tid = target["id"]
        code = (ROOT / target["source_file"]).read_text(encoding="utf-8")
        slug = tid.replace(".", "_")
        test_filename = f"test_{slug}.py"

        prompt_a = BASE_TEMPLATE.format(code=code, extra="")
        prompt_b = BASE_TEMPLATE.format(
            code=code,
            extra=SPECIFIED_EXTRA.format(
                import_path=tid,
                import_stmt=import_stmt(tid),
                test_filename=test_filename,
            ),
        )

        (PROMPTS / "A" / f"{slug}.md").write_text(prompt_a, encoding="utf-8")
        (PROMPTS / "B" / f"{slug}.md").write_text(prompt_b, encoding="utf-8")
        index_rows.append(
            f"| {tid} | {target['lines']} | `{test_filename}` | "
            f"`{import_stmt(tid)}` | `generated/<模型>/<条件>/{slug}.py` |"
        )

    index = [
        "# Prompt index",
        "",
        "Condition A = underspecified (only the source code is given).",
        "Condition B = A plus module name, exact import statement, no-reimplementation",
        "rule and a fixed test filename.",
        "",
        "| module | lines | expected test file | import used in condition B | 粘贴保存到 |",
        "|---|---|---|---|---|",
        *index_rows,
        "",
        f"Total: {len(manifest['targets'])} modules x 2 conditions = "
        f"{len(manifest['targets']) * 2} prompt files.",
        "",
        "`generated/` 下已建好全部 placeholder（3 模型 × 2 条件 × 15 模块 = 90 个空文件），",
        "把模型返回的代码直接粘进对应文件保存即可，不要改动代码内容。",
    ]
    (PROMPTS / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    print(f"generated {len(manifest['targets']) * 2} prompts -> {PROMPTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
