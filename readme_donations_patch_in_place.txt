# === README donations/SEO: patch-in-place (NO reemplaza tu README) ===
# Crea rama, actualiza solo la sección de donaciones + badge + SEO, valida en local
# y abre PR con merge automático cuando todo esté VERDE.

set -euo pipefail

# --- Config ---
REPO_DIR="/home/user/Proyectos/ai-patch-verifier"
REPO_SLUG="CoderDeltaLAN/ai-patch-verifier"
BRANCH="docs/readme-donations-append-$(date +%Y%m%d%H%M%S)"

DONATE_BADGE='[![Donate](https://img.shields.io/badge/Donate-PayPal-0070ba.svg?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW)'
SEO_BLOCK='<!--
SEO keywords: ai patch verifier, trust score, ai code review, ai-generated code patches,
license header checker, header gate, plagiarism guard, github actions, ci/cd, python cli,
ruff black pytest 100 coverage, poetry twine wheel sdist, secure software supply chain
-->'

# --- 0) Entrar al repo y crear rama ---
cd "$REPO_DIR"
git switch -c "$BRANCH"

# --- 1) Preparar el bloque de donaciones (contenido nuevo) ---
cat > /tmp/donations_section.md <<'DONO'
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
DONO

# --- 2) Añadir badge de DONATE (si falta) en la cabecera del README ---
if ! grep -q 'hosted_button_id=YVENCBNCZWVPW' README.md; then
  sed -i "1i $DONATE_BADGE" README.md
fi

# --- 3) Añadir bloque SEO (si falta) debajo de la línea 'CI:' ---
if ! grep -q 'SEO keywords:' README.md; then
  # Inserta después de la primera línea que empieza por 'CI:'
  awk -v block="$SEO_BLOCK" '
    BEGIN{printed=0}
    /^CI: / && !printed { print; print ""; print block; print ""; printed=1; next }
    { print }
  ' README.md > README.md.tmp && mv README.md.tmp README.md
fi

# --- 4) Reemplazar SOLO el contenido de la sección "13) Donations & Sponsorship" ---
if grep -q '^13) Donations & Sponsorship' README.md; then
  awk -v f="/tmp/donations_section.md" '
    BEGIN{inreplace=0}
    # Imprime el título de la sección tal cual
    /^13\) Donations & Sponsorship/ { print; system("cat " f); inreplace=1; next }
    # Cuando llegue a la siguiente sección (14) License), desactiva recorte y sigue
    inreplace && /^14\) License/ { inreplace=0 }
    # Saltar todas las líneas dentro del bloque a reemplazar
    inreplace { next }
    # El resto se imprime normal
    { print }
  ' README.md > README.md.new && mv README.md.new README.md
else
  # Si no existe la sección, la añadimos antes de "14) License" si está, o al final.
  if grep -q '^14\) License' README.md; then
    awk -v f="/tmp/donations_section.md" '
      /^14\) License/ { print ""; print "13) Donations & Sponsorship"; system("cat " f); print ""; }
      { print }
    ' README.md > README.md.new && mv README.md.new README.md
  else
    {
      echo ""
      echo "13) Donations & Sponsorship"
      cat /tmp/donations_section.md
      echo ""
    } >> README.md
  fi
  # Asegura que el ToC tenga la entrada (si no la tiene)
  if ! grep -q '13) \*\*Donations & Sponsorship\*\*' README.md; then
    sed -i 's/^12) Contributing.*/12) Contributing  \n13) **Donations & Sponsorship**  \n14) License  \n15) Author  /' README.md || true
  fi
fi

# --- 5) FUNDING.yml (Sponsor button) ---
mkdir -p .github
if [ ! -f .github/FUNDING.yml ]; then
  cat > .github/FUNDING.yml <<'YAML'
custom: ["https://www.paypal.com/donate/?hosted_button_id=YVENCBNCZWVPW"]
YAML
fi

# --- 6) Preflight idéntico al CI (todo debe pasar en VERDE) ---
rm -rf dist build .tox .venv_smoke /tmp/aipatch_* 2>/dev/null || true
poetry install --no-interaction

poetry run ruff check .
poetry run ruff format --check .
poetry run black --check .

PYTHONPATH=src poetry run pytest -q --cov=ai_patch_verifier --cov-report=term-missing --cov-fail-under=100
poetry run aipatch check-headers

poetry build -q && poetry run twine check dist/*

python -m venv /tmp/aipatch_whl && /tmp/aipatch_whl/bin/pip -q install -U pip && /tmp/aipatch_whl/bin/pip -q install dist/*.whl && /tmp/aipatch_whl/bin/aipatch --help >/dev/null
python -m venv /tmp/aipatch_sdist && /tmp/aipatch_sdist/bin/pip -q install -U pip && /tmp/aipatch_sdist/bin/pip -q install dist/*.tar.gz && /tmp/aipatch_sdist/bin/python -m ai_patch_verifier.cli --help >/dev/null

poetry run tox -q

# --- 7) Commit + PR + merge (solo si todo lo anterior pasó en VERDE) ---
git add README.md .github/FUNDING.yml || true
git commit -m "docs: README — donations section refresh (badge+SEO, non-destructive)"
git push -u origin "$BRANCH"

gh pr create --fill --title "docs: README — donations section refresh (non-destructive)"
gh pr checks --watch
gh pr merge --squash --delete-branch

# --- 8) Confirmar verde en main ---
RUN_ID=$(gh run list -R "$REPO_SLUG" --branch main -L 1 --json databaseId -q '.[0].databaseId')
gh run watch "$RUN_ID" -R "$REPO_SLUG" --exit-status

echo "✓ Todo en verde y README actualizado SIN reemplazar el contenido original."
