#!/usr/bin/env bash
#
# Growth Markets Research -- one-shot deploy to GitHub Pages.
# Idempotent: safe to re-run. It installs prerequisites, fixes Python's
# macOS SSL cert issue, rebuilds index.html, and pushes to GitHub.
#
#   bash deploy.sh
#
set -uo pipefail

BOLD="$(printf '\033[1m')"; DIM="$(printf '\033[2m')"; RED="$(printf '\033[31m')"
GRN="$(printf '\033[32m')"; YLW="$(printf '\033[33m')"; RST="$(printf '\033[0m')"
say(){ printf "%s\n" "${BOLD}$*${RST}"; }
warn(){ printf "%s\n" "${YLW}$*${RST}"; }
err(){ printf "%s\n" "${RED}$*${RST}" 1>&2; }
ok(){ printf "%s\n" "${GRN}$*${RST}"; }

cd "$(dirname "$0")"
ROOT="$(pwd)"

# ---------------------------------------------------------------------------
# 1. Xcode Command Line Tools (needed for git on a fresh Mac)
# ---------------------------------------------------------------------------
say "==> 1/6  Checking Xcode Command Line Tools"
if xcode-select -p >/dev/null 2>&1; then
  ok "    Command Line Tools present."
else
  warn "    Not found -- triggering the installer GUI. Accept the prompt, then this script will wait."
  xcode-select --install 2>/dev/null || true
  until xcode-select -p >/dev/null 2>&1; do
    printf "."
    sleep 5
  done
  echo
  ok "    Command Line Tools installed."
fi

# ---------------------------------------------------------------------------
# 2. git init + remote
# ---------------------------------------------------------------------------
say "==> 2/6  Git repository"
if [ ! -d .git ]; then
  git init -q
  git branch -M main 2>/dev/null || true
  ok "    Initialized a new git repo."
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  read -r -p "    GitHub username: " GH_USER
  read -r -p "    Repository name [GMR]: " GH_REPO
  GH_REPO="${GH_REPO:-GMR}"
  git remote add origin "https://github.com/${GH_USER}/${GH_REPO}.git"
  ok "    Added remote origin -> https://github.com/${GH_USER}/${GH_REPO}.git"
else
  REMOTE_URL="$(git remote get-url origin)"
  GH_USER="$(printf '%s' "$REMOTE_URL" | sed -E 's#.*github.com[:/]([^/]+)/.*#\1#')"
  GH_REPO="$(printf '%s' "$REMOTE_URL" | sed -E 's#.*/([^/]+)(\.git)?$#\1#' | sed 's/\.git$//')"
  ok "    Using existing remote -> ${REMOTE_URL}"
fi

# ---------------------------------------------------------------------------
# 3. Python HTTPS cert fix (macOS Python.org installers ship no CA bundle)
# ---------------------------------------------------------------------------
say "==> 3/6  Python SSL certificates"
python3 -m pip install --quiet --upgrade certifi >/dev/null 2>&1 && ok "    certifi installed/updated." || warn "    Could not pip install certifi (continuing anyway)."
PYVER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "")"
CERT_CMD="/Applications/Python ${PYVER}/Install Certificates.command"
if [ -f "$CERT_CMD" ]; then
  bash "$CERT_CMD" >/dev/null 2>&1 && ok "    Ran 'Install Certificates.command'." || warn "    'Install Certificates.command' returned non-zero (continuing)."
else
  warn "    'Install Certificates.command' not found for Python ${PYVER} -- the browser fetches live data anyway, so a synthetic build baseline is fine."
fi

# ---------------------------------------------------------------------------
# 4. Rebuild the static site
# ---------------------------------------------------------------------------
say "==> 4/6  Building index.html"
if python3 build_static_site.py; then
  ok "    Build complete."
else
  err "    Build failed -- fix the error above and re-run."
  exit 1
fi

# ---------------------------------------------------------------------------
# 5. Commit + push
# ---------------------------------------------------------------------------
say "==> 5/6  Commit + push"
git add -A
if git diff --cached --quiet; then
  warn "    Nothing new to commit."
else
  git commit -q -m "Deploy Growth Markets Research ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  ok "    Committed."
fi

say "    Pushing to origin/main..."
if git push -u origin main 2>/tmp/gmr_push_err; then
  ok "    Pushed."
else
  err "    Push failed. Most common cause: authentication."
  cat /tmp/gmr_push_err 1>&2 || true
  echo
  warn "    GitHub no longer accepts passwords over HTTPS. Create a Personal Access Token:"
  warn "      https://github.com/settings/tokens/new?scopes=repo,workflow&description=GMR"
  warn "    Give it the ${BOLD}repo${RST}${YLW} and ${BOLD}workflow${RST}${YLW} scopes, then use it as the password when git prompts you."
  exit 1
fi

# ---------------------------------------------------------------------------
# 6. Enable Pages + print URL
# ---------------------------------------------------------------------------
say "==> 6/6  GitHub Pages"
warn "    One manual step: enable Pages once at"
warn "      https://github.com/${GH_USER}/${GH_REPO}/settings/pages"
warn "    Set Source = 'Deploy from a branch', Branch = 'main', Folder = '/ (root)', then Save."
echo
ok "Done. Your site will be live in a minute or two at:"
printf "%s\n" "${BOLD}    https://${GH_USER}.github.io/${GH_REPO}/${RST}"
echo
say "Next steps to turn on email alerts:"
cat <<EOF
  1. In the site, open ${BOLD}Methodology -> Email digest schedule${RST}, paste your Gmail
     address + a GitHub token (repo + workflow scopes), click "Turn on scheduled emails".
  2. Add a repo secret named ${BOLD}GMAIL_APP_PASSWORD${RST} (a Gmail App Password) at:
       https://github.com/${GH_USER}/${GH_REPO}/settings/secrets/actions
  3. On the ${BOLD}Alerts${RST} tab, click "Send me a test alert NOW" to confirm the pipeline.
EOF
