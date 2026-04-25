#!/usr/bin/env bash
set -euo pipefail

TASK_NAME="${TASK_NAME:-myatelier_backup_stale_alert_check}"
marker_start="# BEGIN $TASK_NAME"
marker_end="# END $TASK_NAME"

existing_cron="$(crontab -l 2>/dev/null || true)"
if [[ -z "$existing_cron" ]]; then
  echo "No crontab found. Nothing to remove."
  exit 0
fi

cleaned_cron="$(printf "%s\n" "$existing_cron" | awk "/$marker_start/{flag=1;next}/$marker_end/{flag=0;next}!flag")"

if [[ "$cleaned_cron" == "$existing_cron" ]]; then
  echo "Task marker not found: $TASK_NAME"
  exit 0
fi

printf "%s\n" "$cleaned_cron" | crontab -
echo "Cron task removed successfully: $TASK_NAME"
