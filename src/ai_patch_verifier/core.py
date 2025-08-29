# ai-patch-verifier — AI Patch Verifier
# Copyright (c) 2025 CoderDeltaLAN
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path

REPO_HEADER_LINES = [
    "ai-patch-verifier — AI Patch Verifier",
    "Source: https://github.com/CoderDeltaLAN/ai-patch-verifier",
    "License: MIT",
]


def has_required_header(text: str) -> bool:
    head = "\n".join(REPO_HEADER_LINES)
    return all(line in text for line in REPO_HEADER_LINES) or head in text


def iter_python_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        if "site-packages" in p.parts:
            continue
        if p.name == "__init__.py" and "src" not in p.parts:
            continue
        yield p


def assert_header_compliance(src_root: Path) -> list[Path]:
    missing: list[Path] = []
    for p in iter_python_files(src_root):
        text = p.read_text(encoding="utf-8")
        if not has_required_header(text):
            missing.append(p)
    return missing


def compute_trust_score(diff_text: str | None) -> dict:
    """
    Heurística inicial y transparente.
    - Penaliza TODO/FIXME.
    - Sube si hay cambios en tests.
    - Penaliza archivos binarios.
    - Devuelve score en [0,100] y desglose.
    """
    score = 70
    reasons: list[str] = []

    text = diff_text or ""
    if "TODO" in text or "FIXME" in text:
        score -= 10
        reasons.append("marcadores TODO/FIXME detectados")

    pattern = r"(?m)^\+\s*(def |class |from |import ).*test"
    touches_tests = len(re.findall(pattern, text)) > 0
    test_changes = touches_tests or ("tests/" in text)
    if test_changes:
        score += 10
        reasons.append("cambios en tests detectados")

    binary = re.findall(r"Binary files .* differ", text)
    if binary:
        score -= 10
        reasons.append("parches binarios")

    score = max(0, min(100, score))
    return {"score": score, "reasons": reasons}


def format_score_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)
