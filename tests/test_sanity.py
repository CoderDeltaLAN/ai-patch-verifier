# ai-patch-verifier — AI Patch Verifier
# Copyright (c) 2025 CoderDeltaLAN
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT

from pathlib import Path

from ai_patch_verifier.core import assert_header_compliance, compute_trust_score


def test_headers_present():
    missing = assert_header_compliance(Path("src"))
    assert not missing, f"Faltan cabeceras en: {missing}"


def test_score_fields():
    result = compute_trust_score(diff_text="+ def test_example():\n+    assert True")
    assert "score" in result and "reasons" in result
    assert 0 <= result["score"] <= 100
