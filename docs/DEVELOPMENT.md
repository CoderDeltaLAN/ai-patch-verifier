# Playbook: Añadir docs/DEVELOPMENT.md con Gate Verde

## 1) Crear archivo DEVELOPMENT.md
mkdir -p docs
cat > docs/DEVELOPMENT.md <<'EOFMD'
# Development Guide — Always Green

## Preflight (local)
```bash
poetry install --no-interaction
poetry run ruff check . --fix
poetry run ruff format .
poetry run black .
poetry run pytest -q
```

## CI Replica (local)
```bash
export PYTHONPATH=src
export PENDING_DIR="$(mktemp -d)"
export PENDING_STORAGE="$PENDING_DIR/pending.json"; [ -f "$PENDING_STORAGE" ] || echo "{}" > "$PENDING_STORAGE"
poetry run pytest -q
```

## Policy
- No push to `main`.
- Open PR only when local checks are green.
- Squash merge only with CI green.
EOFMD

## 2) Validar (Gate Verde)
poetry install --no-interaction
poetry run ruff check . --fix
poetry run ruff format .
poetry run black .
poetry run pytest -q

echo "[i] Si TODO está en verde, ejecutar Paso 3."

## 3) Commit + Push + PR (solo si Paso 2 está OK)
git add docs/DEVELOPMENT.md
git commit -m "docs: add DEVELOPMENT guide with Always Green workflow"
git push -u origin "$(git branch --show-current)"

REPO="CoderDeltaLAN/ai-patch-verifier"
gh pr create -R "$REPO"   -t "docs: add DEVELOPMENT guide with Always Green workflow"   -b "Adds a concise development guide: local preflight, CI replica, and merge policy. No code changes."

gh pr checks -R "$REPO" --watch
# merge squash solo cuando CI esté en verde
# gh pr merge -R "$REPO" --squash --auto
