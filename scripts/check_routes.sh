#!/usr/bin/env bash
# Simple route smoke test using curl against local Flask server

set -euo pipefail

BASE_URL=${BASE_URL:-"http://localhost:5002"}

routes=(
  "/"
  "/project/1"
  "/projects"
  "/work-items"
  "/work-item/1"
  "/tasks"
  "/task/1"
  "/contexts"
  "/contexts/1"
  "/context-files"
  "/agents"
  "/events"
  "/documents"
  "/evidence"
  "/sessions"
)

error=0
for route in "${routes[@]}"; do
  tmp=$(mktemp)
  code=$(curl -sS -o "$tmp" -w "%{http_code}" "$BASE_URL$route" || echo "000")
  if [[ "$code" != "200" ]]; then
    echo "[FAIL] $route -> HTTP $code"
    error=1
  else
    if grep -qiE "(UndefinedError|TemplateNotFound|Traceback|Exception)" "$tmp"; then
      echo "[FAIL] $route -> detected error content"
      error=1
    else
      echo "[OK]   $route"
    fi
  fi
  rm -f "$tmp"
  sleep 0.2

done

exit $error
