# ai-patch-verifier — AI Patch Verifier
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT
from pathlib import Path

from ai_patch_verifier.core import (
    REPO_HEADER_LINES,
    assert_header_compliance,
    compute_trust_score,
    format_score_json,
    has_required_header,
    iter_python_files,
)


def test_has_required_header_true_false(tmp_path: Path):
    ok = "\n".join(REPO_HEADER_LINES) + "\nprint('x')\n"
    bad = "# no header\n"
    assert has_required_header(ok)
    assert not has_required_header(bad)


def test_iter_python_files_filters(tmp_path: Path):
    sp = tmp_path / "site-packages" / "x.py"
    sp.parent.mkdir(parents=True)
    sp.write_text("print('x')\n", encoding="utf-8")
    init_out = tmp_path / "__init__.py"
    init_out.write_text("print('x')\n", encoding="utf-8")
    valid = tmp_path / "src" / "pkg" / "m.py"
    valid.parent.mkdir(parents=True)
    valid.write_text("\n".join(REPO_HEADER_LINES) + "\n", encoding="utf-8")
    files = list(iter_python_files(tmp_path))
    assert valid in files and sp not in files and init_out not in files


def test_assert_header_compliance(tmp_path: Path):
    src = tmp_path / "src"
    good = src / "ok.py"
    bad = src / "bad.py"
    good.parent.mkdir(parents=True)
    good.write_text("\n".join(REPO_HEADER_LINES) + "\n", encoding="utf-8")
    bad.write_text("# missing header\n", encoding="utf-8")
    missing = assert_header_compliance(src)
    assert bad in missing and good not in missing


def test_compute_trust_score_branches():
    base = compute_trust_score("")
    assert base["score"] == 70
    t = compute_trust_score("+ def test_example():\n+    assert True")
    assert t["score"] == 80 and any("tests" in r for r in t["reasons"])
    rb = compute_trust_score("TODO\nBinary files a/b differ\n")
    assert rb["score"] == 50
    j = format_score_json(t)
    assert j.strip().startswith("{") and '"score"' in j
