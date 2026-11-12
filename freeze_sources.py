r"""Freeze the 15 benchmark modules: snapshot their source and record provenance.

Run with the project venv:
    .venv\Scripts\python.exe freeze_sources.py

For every target module this script:
  1. resolves the module file from the pinned venv installation,
  2. copies it verbatim into sources/<import_path>.py,
  3. verifies the copy is byte-identical to the installed file,
  4. records line count + sha256 for the manifest.

The snapshot is what the experimenter pastes into the LLM prompt; the
installed file is what the harness executes. Hash equality is what makes
"the model saw the code that actually ran" a checkable fact.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"

# (import path, distribution name, why it is a good test-generation target)
# 10 modules: 5 domains x 2 modules. Chosen to keep a complexity spread
# (54 -> 1252 lines) while fitting the free-tier budget (10 x 3 x 2 = 60 runs).
TARGETS = [
    ("itsdangerous.encoding", "itsdangerous", "base64url 与整数互转，负数/零/大整数边界"),
    ("humanize.filesize", "humanize", "人类可读文件大小，舍入与负数边界"),
    ("stdnum.iban", "python-stdnum", "IBAN 校验位算法，长度与校验和"),
    ("base58", "base58", "Base58 编解码，字符集与空输入"),
    ("stdnum.isbn", "python-stdnum", "ISBN-10/13 校验位与格式转换"),
    ("stringcase", "stringcase", "多种命名风格互转，空串与数字边界"),
    ("inflection", "inflection", "英文单复数与驼峰转换，不规则词"),
    ("humanize.number", "humanize", "数字格式化，序数、科学计数、负数"),
    ("semver.version", "semver", "语义化版本解析与比较，预发布版本优先级"),
    ("packaging.version", "packaging", "PEP 440 版本解析与比较，大量非法输入"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    SOURCES.mkdir(exist_ok=True)
    records = []

    for import_path, dist, note in TARGETS:
        module = importlib.import_module(import_path)
        origin = Path(module.__file__)
        text = origin.read_text(encoding="utf-8")
        lines = len(text.splitlines())

        out = SOURCES / f"{import_path}.py"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(origin.read_bytes())

        frozen = sha256(out)
        installed = sha256(origin)
        if frozen != installed:
            raise SystemExit(f"ERROR: snapshot mismatch for {import_path}")

        records.append({
            "id": import_path,
            "import_path": import_path,
            "distribution": dist,
            "distribution_version": version(dist),
            "source_file": f"sources/{import_path}.py",
            "installed_file": str(origin),
            "lines": lines,
            "sha256": frozen,
            "note": note,
        })
        print(f"{import_path:<24} {lines:>5} lines  {frozen[:12]}  OK")

    manifest = {
        "experiment": "genai_unit_test_generation",
        "created": "2026-11-11",
        "python": "3.12.4",
        "venv": ".venv",
        "tooling": {
            "pytest": version("pytest"),
            "coverage": version("coverage"),
            "pytest-cov": version("pytest-cov"),
        },
        "targets": records,
    }
    (ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{len(records)} modules frozen -> {SOURCES}")
    print(f"manifest -> {ROOT / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
