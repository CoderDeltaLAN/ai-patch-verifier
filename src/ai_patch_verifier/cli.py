# ai-patch-verifier — AI Patch Verifier
# Copyright (c) 2025 CoderDeltaLAN
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich import print as rprint

from .core import assert_header_compliance, compute_trust_score, format_score_json

app = typer.Typer(
    add_completion=False,
    help="Verify AI-generated patches and compute trust score.",
)


@app.command("check-headers")
def check_headers(
    path: str = typer.Argument("src", help="Raíz de código fuente"),
) -> None:
    missing = assert_header_compliance(Path(path))
    if missing:
        rprint("[red]Faltan cabeceras obligatorias en:[/red]")
        for p in missing:
            rprint(f"- {p}")
        raise typer.Exit(code=1)
    rprint("[green]Cabeceras OK[/green]")


@app.command("score")
def score(
    diff_file: str = typer.Option(
        None,
        "--diff-file",
        help="Ruta al diff. Si no, STDIN",
    ),
) -> None:
    if diff_file:
        text = Path(diff_file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    result = compute_trust_score(text)
    rprint(format_score_json(result))


if __name__ == "__main__":  # pragma: no cover
    app()
