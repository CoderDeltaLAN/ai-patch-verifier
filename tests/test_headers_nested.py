# ai-patch-verifier — AI Patch Verifier
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT
from pathlib import Path

from ai_patch_verifier.core import REPO_HEADER_LINES, assert_header_compliance


def test_missing_headers_in_nested_tree(tmp_path: Path):
    src = tmp_path / "src" / "pkg" / "sub"
    src.mkdir(parents=True)
    ok = src / "a.py"
    bad = src / "b.py"
    ok.write_text("\n".join(REPO_HEADER_LINES) + "\n", encoding="utf-8")
    bad.write_text("# falta header\n", encoding="utf-8")
    missing = assert_header_compliance(tmp_path / "src")
    assert bad in missing and ok not in missing
