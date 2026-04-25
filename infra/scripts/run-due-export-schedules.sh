#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin123}"
DRY_RUN="${DRY_RUN:-false}"
LIMIT="${LIMIT:-50}"

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

run_payload=$(cat <<JSON
{"dry_run":$DRY_RUN,"limit":$LIMIT,"trigger_source":"automation"}
JSON
)

result=$(curl -sS -f \
  -H "Content-Type: application/json" \
  -b "$COOKIE_FILE" \
  -X POST "$BASE_URL/api/exports/schedules/run-due" \
  -d "$run_payload")

echo "Run due export schedules result: $result"

curl -sS -b "$COOKIE_FILE" -X POST "$BASE_URL/api/auth/logout" > /dev/null || true
exit 0
