# Evaluating LLM-Generated Unit Tests

An empirical study of whether large language models produce **usable** pytest suites for Python
modules. Three models (Claude, ChatGPT, Gemini) generated tests for ten modules under two prompt
conditions; every generated file was executed unmodified, and failures were recorded as data
rather than repaired.

## Key findings

- **Prompt specification is a safety net, not an enhancement.** Explicitly naming the module and
  its import path raises ChatGPT's coverage yield from 48.5% to 91.2%, but adds only 0.6 points
  for Claude, which infers the module name unaided.
- **The dominant failure under an underspecified prompt is an invented module name**
  (`your_module`, `iban`, `string_convert`), which detaches the tests from the object under test
  entirely. Supplying one `import` statement eliminates this failure class.
- **Test count is a poor proxy for quality.** One model produced ~15× more tests than another
  while achieving only 1.2 points more coverage. Pass rate can likewise mislead through selection
  effects, which motivates the *coverage yield* metric below.

## Repository layout

```
.
├─ sources/          frozen source snapshots of the 10 modules under test
├─ prompts/
│  ├─ A/             condition A prompts (source only, underspecified)
│  └─ B/             condition B prompts (adds module name, import, no-reimplementation)
├─ generated/        the 60 collected artifacts, exactly as the models returned them
│  ├─ claude/{A,B}/
│  ├─ chatgpt/{A,B}/
│  ├─ gemini/{A,B}/
│  └─ _discarded/    artifacts voided by a documented collection error, kept for audit
├─ manifest.json     module metadata, pinned versions, SHA256 of every source snapshot
├─ freeze_sources.py snapshot the installed modules and record provenance
├─ gen_prompts.py    generate the 20 prompts from the manifest
├─ run_eval.py       run every artifact in isolation, measure pytest + coverage
├─ make_tables.py    aggregate results into Markdown tables (en / zh)
├─ make_figures.py   render the figures
├─ summarize.py      print per-model / per-condition summaries
└─ check_outputs.py  syntax and import sanity check on collected artifacts
```

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Python 3.12 is required; all versions are pinned in `requirements.txt`.

## Reproducing the measurement

```bash
# 1. Re-freeze the test subjects and rebuild manifest.json (hash-verified)
python freeze_sources.py

# 2. Regenerate the 20 prompt files
python gen_prompts.py

# 3. Sanity-check the collected artifacts
python check_outputs.py

# 4. Measure every artifact (isolated subprocess, pytest + coverage)
python run_eval.py

# 5. Aggregate
python make_tables.py --lang en
python make_figures.py
python summarize.py
```

`run_eval.py` writes `out/results.json` and `out/results.csv`. That directory is git-ignored
because it is regenerated on every run.

## Experiment design

Two conditions differ **only** by an "Additional requirements" block; everything else in the
prompt, including the instruction to return code without comments, is word-for-word identical.

| | Condition A | Condition B |
|---|---|---|
| Module name given | no | yes |
| Exact `import` statement given | no | yes |
| Re-implementation forbidden | no | yes |
| Test filename specified | no | yes |

Ten modules span five domains: encoding (`itsdangerous.encoding`, `base58`), number formatting
(`humanize.filesize`, `humanize.number`), string manipulation (`stringcase`, `inflection`),
checksums (`stdnum.iban`, `stdnum.isbn`), and version parsing (`semver.version`,
`packaging.version`).

### Model configurations

These were free-tier configurations and are **not capability-matched**; see the limitations
section of the paper.

| System | Configuration |
|---|---|
| Claude | Sonnet 5.5, reasoning level medium |
| ChatGPT | GPT-6 Instant, reasoning level low |
| Gemini | 3.5 Flash-Lite (Auto routing; all 20 responses labelled Flash-Lite) |

## Metrics

- **Execution rate** — share of artifacts that collected at least one test.
- **Pass rate** — pooled passed / collected tests, with a Wilson 95% interval.
- **Mean coverage** — averaged over artifacts that successfully imported the target only.
- **Coverage yield** — covered lines summed over *all* artifacts (non-imported count as zero)
  divided by the module's total statements. Unlike a mean over imported artifacts, it cannot be
  inflated by excluding failures, so it is used as the primary metric.

## Notes on the artifacts

- Files under `generated/` are byte-for-byte what the models returned; they were never edited to
  make them pass. A failing artifact is a datapoint.
- `generated/_discarded/` holds three artifacts voided because of collection errors (one
  duplicated input, two truncated pastes). They are retained so the audit trail is complete.
- Every source snapshot in `sources/` is verified against the installed file by SHA256 in
  `freeze_sources.py`, guaranteeing that the code shown to a model is the code that was executed.

## Third-party code and licenses

The modules under test are unmodified copies of third-party packages and remain under their
original licenses: itsdangerous (BSD-3-Clause), humanize (MIT), python-stdnum (LGPL-2.1),
base58 (MIT), stringcase (MIT), inflection (MIT), semver (BSD-3-Clause), packaging
(Apache-2.0 / BSD-2-Clause). They are included solely as test subjects.

The experiment code in this repository is provided for academic reproducibility.
