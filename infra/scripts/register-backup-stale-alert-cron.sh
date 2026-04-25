#!/usr/bin/env bash
set -euo pipefail

TASK_NAME="${TASK_NAME:-myatelier_backup_stale_alert_check}"
INTERVAL_MINUTES="${INTERVAL_MINUTES:-60}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin123}"
DRY_RUN="${DRY_RUN:-false}"
FORCE="${FORCE:-false}"

if (( INTERVAL_MINUTES <= 0 )); then
  echo "INTERVAL_MINUTES must be greater than zero." >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/run-backup-stale-alert-check.sh"

if [[ ! -f "$RUNNER" ]]; then
  echo "Runner script not found: $RUNNER" >&2
  exit 1
fi

chmod +x "$RUNNER"

minute_step="$INTERVAL_MINUTES"
if (( INTERVAL_MINUTES >= 60 && INTERVAL_MINUTES % 60 == 0 )); then
  hour_step=$((INTERVAL_MINUTES / 60))
  schedule="0 */$hour_step * * *"
else
  schedule="*/$minute_step * * * *"
fi

cron_cmd="BASE_URL=\"$BASE_URL\" USERNAME=\"$USERNAME\" PASSWORD=\"$PASSWORD\" DRY_RUN=\"$DRY_RUN\" FORCE=\"$FORCE\" \"$RUNNER\""
marker_start="# BEGIN $TASK_NAME"
marker_end="# END $TASK_NAME"
entry="$marker_start"$'\n'"$schedule $cron_cmd"$'\n'"$marker_end"

existing_cron="$(crontab -l 2>/dev/null || true)"
cleaned_cron="$(printf "%s\n" "$existing_cron" | awk "/$marker_start/{flag=1;next}/$marker_end/{flag=0;next}!flag")"

{
  printf "%s\n" "$cleaned_cron" | sed '/^[[:space:]]*$/d'
  printf "%s\n" "$entry"
} | crontab -

echo "Cron task registered successfully: $TASK_NAME"
echo "Schedule: $schedule"
