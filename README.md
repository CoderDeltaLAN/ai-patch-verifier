[![CI](https://github.com/CoderDeltaLAN/ai-patch-verifier/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CoderDeltaLAN/ai-patch-verifier/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](#)
[![Donate](https://img.shields.io/badge/Donate-PayPal-0070ba.svg?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Release](https://img.shields.io/github/v/release/CoderDeltaLAN/ai-patch-verifier)

AI PATCH VERIFIER
=================
(Project: ai-patch-verifier)

Compatibility: Python >= 3.11  
Lint: Ruff | Format: Black | Tests: Pytest + **100% coverage**  
CI: GitHub Actions (lint + format + tests + header gate + build)

*AI code review for AI-generated patches. Trust Score + mandatory header gate. Python CLI, CI/CD-ready.*

<!--
SEO keywords: ai patch verifier, trust score, ai code review, ai-generated code patches,
license header checker, header gate, plagiarism guard, github actions, ci/cd, python cli,
ruff black pytest 100 coverage, poetry twine wheel sdist, secure software supply chain
-->

---

Table of Contents
-----------------
1) Introduction  
2) Features  
3) How it works (ASCII diagram)  
4) Installation  
5) Quick start  
6) CLI Reference  
7) Practical examples  
8) CI Integration (GitHub Actions)  
9) Release Notes  
10) Troubleshooting Guide  
11) FAQ  
12) Contributing  
13) **Donations & Sponsorship**  

14) License  
15) Author  

1) Introduction
---------------
AI models accelerate development but can introduce subtle risks: unexpected binary
patches, TODO/FIXME markers, or changes without tests. This project provides a
reproducible, objective, and easy-to-automate verifier that scores diffs and blocks
changes lacking proper headers.

**Why use it (at a glance):**
- Catch risky AI edits before merge (objective scoring).
- Enforce repository headers for license + URL (traceability/compliance).
- Deterministic CLI, same behavior in local and CI.
- Zero-config defaults; integrates in minutes.

**Use cases:**
- Guardrails for AI pair-programming and code assistants.
- PR gate in regulated or compliance-sensitive repos.
- Classroom / OSS projects to prevent header omissions and plagiarism.

2) Features
-----------
- Trust Score for diffs (0–100).
- Penalizes risky patterns: "TODO", "FIXME", binary diffs.
- Rewards changes in tests (test-driven development).
- Validation of mandatory headers in every source file.
- Human- and machine-readable JSON output.
- CI-ready (GitHub Actions).

3) How it works (ASCII diagram)
-------------------------------
                 ┌───────────────────┐
                 │     Diff source   │
                 │ (git diff / file) │
                 └─────────┬─────────┘
                           │
                ┌──────────▼───────────┐
                │     aipatch score    │
                │     (heuristics)     │
                └───────┬──────────────┘
                        │  JSON {"score":N, "reasons":[...]}
                        ▼
         ┌─────────────────────────────────┐
         │  CI Gate / Merge Policy         │
         │   - minimum threshold (e.g., 70)│
         │   - mandatory header gate       │
         └─────────────────────────────────┘

Heuristics (ASCII visual)
> The Trust Score starts at **70** and is clamped to **0..100**.

| Signal                     | Effect on Trust Score | Visual hint    |
|---------------------------|-----------------------|----------------|
| Changes in **test files** | **+10**               | `[##########]` |
| **TODO/FIXME** detected   | **−10**               | `[######....]` |
| **Binary patches**        | **−10**               | `[######....]` |

*Final score = clamp( 70 + bonuses − penalties, 0, 100 ).*

4) Installation
---------------
With Poetry (recommended for development):
```bash
git clone https://github.com/CoderDeltaLAN/ai-patch-verifier.git
cd ai-patch-verifier
poetry install --no-interaction
```

From local package (wheel/sdist):
```bash
poetry build -q
python -m venv .venv && . .venv/bin/activate
pip install dist/*.whl
```

5) Quick start
--------------
Compute Trust Score from a diff file:
```bash
poetry run aipatch score --diff-file changes.diff
```

Or from git (piped):
```bash
git diff HEAD~1 | poetry run aipatch score
```

Verify headers in source code:
```bash
poetry run aipatch check-headers        # default root: src
poetry run aipatch check-headers path_to_scan
```

6) CLI Reference
----------------
`aipatch --help`  
Shows general help and subcommands.

`aipatch score --diff-file PATH`  
Reads a diff from PATH; if omitted, reads from STDIN.  
Output: JSON with `"score"` and `"reasons"`.

`aipatch check-headers [PATH=src]`  
Scans `.py` files (excludes site-packages and `__init__.py`) validating mandatory
headers. Returns a list of missing ones and exit code 1 if it fails.

7) Practical examples
---------------------
**Example 1: changes in tests (higher confidence)**  
Input (diff):
```diff
+ def test_addition():
+     assert 1 + 1 == 2
```
Output:
```json
{ "score": 80, "reasons": ["test changes detected"] }
```

**Example 2: TODO and binary diff (lower confidence)**  
Input (diff):
```
Binary files /dev/null and b/src/pkg/mod.bin differ
+ # TODO: implement
```
Output:
```json
{ "score": 50, "reasons": ["TODO/FIXME markers detected", "binary patches"] }
```

8) CI Integration (GitHub Actions)
----------------------------------
Job summary:
- Install Poetry
- Install dependencies
- Ruff (lint + format check) + Black
- Pytest with **100% minimum coverage**
- Header gate (`aipatch check-headers`)
- Build wheel + smoke install

CI flow (ASCII):
```
[Push/PR] -> [Ruff/Black] -> [Pytest 100%] -> [Header gate] -> [Build+Smoke] -> ✓ Green
```

Suggested thresholds:
- Coverage: 100%
- Minimum Trust Score to merge: >= 70
- Header gate: mandatory (no exceptions)

9) Release Notes
----------------
**v0.1.0**
- Stable CLI: `score`, `check-headers`
- Initial Trust Score heuristics
- JSON output, examples, and 100% tests
- CI workflow with smoke install
- Compatibility verified on Python 3.12 (runtime) and 3.11 (CI)

10) Troubleshooting Guide
-------------------------
- **ModuleNotFoundError: typer** (sdist)
  - Install built package (pip pulls deps) and verify virtualenv/pip version.
- **Header gate** fails with temp/generated files
  - Exclude build/venv dirs or point to correct root.
- **Unexpected Trust Score**
  - Inspect the diff fed to the tool; TODO/FIXME or “Binary files differ” reduce score;
    changes in tests increase confidence.

11) FAQ
-------
**Can I tweak scoring rules?**  
Roadmap: project-configurable rules.

**Does it work with other languages?**  
Current heuristic is diff-generic; language-specific analyzers (JS, Go, Rust) are on the roadmap.

**Why enforce headers?**  
Traceability, license compliance, and anti-plagiarism.

12) Contributing
----------------
1. Branch:
   ```bash
   git checkout -b feat/my-improvement
   ```
2. Lint + tests + 100% coverage:
   ```bash
   poetry run ruff check . --fix
   poetry run ruff format .
   poetry run black .
   PYTHONPATH=src poetry run pytest -q --cov=ai_patch_verifier --cov-fail-under=100
   ```
3. Open a PR with clear description and tests.

Conventions:
- Conventional Commits (feat, fix, chore, …).
- Nothing red gets pushed: **all checks must be green**.

13) Donations & Sponsorship
**CoderDeltaLAN OSS Projects**  
*Apoya el software libre: tus donativos aseguran proyectos limpios, seguros y en evolución constante para la comunidad global.*

- **PayPal:**  
  👉 **[Donate via PayPal](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)**

- **Badge (para otros repos):**
```md
[![Donate](https://img.shields.io/badge/Donate-PayPal-0070ba.svg?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)
```

Funds help with:
- CI minutes & runners, packaging releases, docs & examples
- Issue triage, security updates, roadmap features

**Gracias por apoyar el ecosistema open-source.**

14) License
-----------
MIT. See [LICENSE](LICENSE). Every source file must include a header with copyright and URL:  
https://github.com/CoderDeltaLAN/ai-patch-verifier

15) Author
----------
CoderDeltaLAN (Yosvel)  
Contact: coderdeltalan.cargo784@8alias.com  
Repository: https://github.com/CoderDeltaLAN/ai-patch-verifier
