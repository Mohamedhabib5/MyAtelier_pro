#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin123}"
DRY_RUN="${DRY_RUN:-false}"
FORCE="${FORCE:-false}"

COOKIE_FILE="$(mktemp)"
trap 'rm -f "$COOKIE_FILE"' EXIT

login_payload=$(cat <<JSON
{"username":"$USERNAME","password":"$PASSWORD"}
JSON
)

curl -sS -f \
  -H "Content-Type: application/json" \
  -c "$COOKIE_FILE" \
  -X POST "$BASE_URL/api/auth/login" \
  -d "$login_payload" > /dev/null

check_payload=$(cat <<JSON
{"dry_run":$DRY_RUN,"force":$FORCE,"trigger_source":"automation"}
JSON
)

result=$(curl -sS -f \
  -H "Content-Type: application/json" \
  -b "$COOKIE_FILE" \
  -X POST "$BASE_URL/api/settings/ops/alerts/run-backup-check" \
  -d "$check_payload")

echo "Backup stale check result: $result"

stale=$(echo "$result" | python -c "import json,sys; print(str(json.load(sys.stdin)['stale']).lower())")
sent=$(echo "$result" | python -c "import json,sys; print(str(json.load(sys.stdin)['sent']).lower())")

if [[ "$stale" == "false" && "$sent" == "false" ]]; then
  curl -sS -b "$COOKIE_FILE" -X POST "$BASE_URL/api/auth/logout" > /dev/null || true
  exit 0
fi

if [[ "$stale" == "true" && "$sent" == "false" && "$DRY_RUN" != "true" ]]; then
  curl -sS -b "$COOKIE_FILE" -X POST "$BASE_URL/api/auth/logout" > /dev/null || true
  echo "Stale backup detected but alert was not sent." >&2
  exit 2
fi

curl -sS -b "$COOKIE_FILE" -X POST "$BASE_URL/api/auth/logout" > /dev/null || true
exit 0
