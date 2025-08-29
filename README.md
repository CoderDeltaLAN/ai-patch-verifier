[![CI](https://github.com/CoderDeltaLAN/ai-patch-verifier/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CoderDeltaLAN/ai-patch-verifier/actions/workflows/ci.yml)
AI PATCH VERIFIER
=================
(Project: ai-patch-verifier)

Compatibility: Python >= 3.11
Lint: Ruff | Format: Black | Tests: Pytest + 100% coverage
CI: GitHub Actions (lint + format + tests + header gate + build)

Brief description
-----------------
ai-patch-verifier is a command-line tool (CLI) and a set of CI checks that analyze
**AI-generated code patches** and assign a **Trust Score**. It also validates that all
source files carry a mandatory header (license + repository URL), acting as an
anti-plagiarism barrier and improving traceability.

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
13) License
14) Author

1) Introduction
---------------
AI models accelerate development but can introduce subtle risks: unexpected binary
patches, TODO/FIXME markers, or changes without tests. This project provides a
reproducible, objective, and easy-to-automate verifier that scores diffs and blocks
changes lacking proper headers.

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
-------------------------
+--------------+----------------------------+
| Signal       | Effect on Trust Score      |
+--------------+----------------------------+
| Changes in   | +10                        |
| test files   |                            |
|              |  [##########]              |
+--------------+----------------------------+
| TODO/FIXME   | -10                        |
| detected     |  [######....]              |
+--------------+----------------------------+
| Binary       | -10                        |
| patches      |  [######....]              |
+--------------+----------------------------+
Base score: 70. Result is clamped to [0, 100].

4) Installation
---------------
With Poetry (recommended for development):
    git clone https://github.com/CoderDeltaLAN/ai-patch-verifier.git
    cd ai-patch-verifier
    poetry install --no-interaction

From local package (wheel/sdist):
    # Build
    poetry build -q
    # Install produced wheel
    python -m venv .venv && . .venv/bin/activate
    pip install dist/*.whl

5) Quick start
--------------
Compute Trust Score from a diff file:
    poetry run aipatch score --diff-file changes.diff

Or from git (piped):
    git diff HEAD~1 | poetry run aipatch score

Verify headers in source code:
    poetry run aipatch check-headers        # default root: src
    poetry run aipatch check-headers path_to_scan

6) CLI Reference
----------------
aipatch --help
    Shows general help and subcommands.

aipatch score --diff-file PATH
    Reads a diff from PATH; if omitted, reads from STDIN.
    Output: JSON with "score" and "reasons".

aipatch check-headers [PATH=src]
    Scans .py files (excludes site-packages and __init__.py) validating mandatory
    headers. Returns a list of missing ones and exit code 1 if it fails.

7) Practical examples
---------------------
Example 1: changes in tests (higher confidence)
-----------------------------------------------
Input (diff):
    + def test_addition():
    +     assert 1 + 1 == 2

Output:
    {
      "score": 80,
      "reasons": ["test changes detected"]
    }

Example 2: TODO and binary diff (lower confidence)
--------------------------------------------------
Input (diff):
    Binary files /dev/null and b/src/pkg/mod.bin differ
    + # TODO: implement

Output:
    {
      "score": 50,
      "reasons": ["TODO/FIXME markers detected", "binary patches"]
    }

8) CI Integration (GitHub Actions)
----------------------------------
Job summary:
    - Install Poetry
    - Install dependencies
    - Ruff (lint + format check) + Black
    - Pytest with 100% minimum coverage
    - Header gate (aipatch check-headers)
    - Build wheel + smoke install

CI flow (ASCII):
    [Push/PR] -> [Ruff/Black] -> [Pytest 100%] -> [Header gate] -> [Build+Smoke] -> ✓ Green

Suggested thresholds:
    - Coverage: 100%
    - Minimum Trust Score to merge: >= 70
    - Header gate: mandatory (no exceptions)

9) Release Notes
----------------
v0.1.0
  - Stable CLI: `score`, `check-headers`
  - Initial Trust Score heuristics
  - JSON output, examples, and 100% tests
  - CI workflow with smoke install
  - Compatibility verified on Python 3.12 (runtime) and 3.11 (CI)

10) Troubleshooting Guide
-------------------------
• Error: "ModuleNotFoundError: typer" when running from sdist
  - Ensure you install the built package (pip installs dependencies).
  - Verify your virtual environment and pip version.

• Header gate fails with temporary/generated files
  - Exclude build/venv directories in your pipeline or point it to the correct root.

• Unexpected Trust Score
  - Review the diff being consumed (avoid noise) and confirm whether "TODO/FIXME" or
    "Binary files differ" appear. Changes in tests increase confidence.

11) FAQ
-------
Q: Can I tweak scoring rules?
A: Coming soon: project-configurable rules.

Q: Does it work with other languages?
A: The current heuristic is diff-generic; the roadmap includes language-specific
   analyzers (JS, Go, Rust).

Q: Why enforce headers?
A: Improves traceability, license compliance, and reduces plagiarism risks.

12) Contributing
----------------
1. Create a branch:
       git checkout -b feat/my-improvement
2. Lint + tests + 100% coverage:
       poetry run ruff check . --fix
       poetry run ruff format .
       poetry run black .
       PYTHONPATH=src poetry run pytest -q --cov=ai_patch_verifier --cov-fail-under=100
3. Open a PR with a clear description and test cases.

Conventions:
- Conventional Commits style (feat, fix, chore, etc.).
- Nothing red gets pushed: all checks must be green.

13) License
-----------
MIT. See LICENSE. Every source file must include a header with copyright and URL:
https://github.com/CoderDeltaLAN/ai-patch-verifier

14) Author
----------
CoderDeltaLAN (Yosvel)
Contact: coderdeltalan.cargo784@8alias.com
Repository: https://github.com/CoderDeltaLAN/ai-patch-verifier
