from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def send_export_delivery_webhook(*, webhook_url: str, payload: dict, dry_run: bool = True) -> tuple[bool, str]:
    cleaned_url = webhook_url.strip()
    if dry_run:
        return False, "Dry-run mode: delivery webhook not sent."
    if not cleaned_url:
        return False, "Delivery webhook URL is not configured."

    body = json.dumps(
        {
            "source": "myatelier_pro",
            "type": "export_schedule_batch",
            "sent_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(cleaned_url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=5) as response:
            status = getattr(response, "status", 200)
            if 200 <= status < 300:
                return True, f"Delivery webhook sent with status {status}."
            return False, f"Delivery webhook responded with status {status}."
    except URLError as exc:
        logger.warning("Export delivery webhook failed: %s", exc)
        reason = exc.reason if hasattr(exc, "reason") else str(exc)
        return False, f"Delivery webhook request failed: {reason}"
