# ai-patch-verifier — AI Patch Verifier
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT
from pathlib import Path

from ai_patch_verifier.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_cli_help_commands():
    r = runner.invoke(app, ["--help"])
    assert r.exit_code == 0 and "Verify AI-generated patches" in r.stdout
    r2 = runner.invoke(app, ["score", "--help"])
    assert r2.exit_code == 0 and "diff" in r2.stdout
    r3 = runner.invoke(app, ["check-headers", "--help"])
    assert r3.exit_code == 0


def test_cli_score_from_file(tmp_path: Path):
    diff = tmp_path / "d.diff"
    diff.write_text("+ def test_x():\n+  assert True\n", encoding="utf-8")
    r = runner.invoke(app, ["score", "--diff-file", str(diff)])
    assert r.exit_code == 0 and '"score"' in r.stdout


def test_cli_score_from_stdin():
    r = runner.invoke(app, ["score"], input="TODO\n")
    assert r.exit_code == 0 and '"score"' in r.stdout


def test_cli_check_headers_ok():
    r = runner.invoke(app, ["check-headers", "src"])
    assert r.exit_code == 0 and "Cabeceras OK" in r.stdout


def test_cli_check_headers_fail(tmp_path: Path):
    bad = tmp_path / "x.py"
    bad.write_text("print('no header')\n", encoding="utf-8")
    r = runner.invoke(app, ["check-headers", str(tmp_path)])
    assert r.exit_code == 1 and "Faltan cabeceras" in r.stdout
