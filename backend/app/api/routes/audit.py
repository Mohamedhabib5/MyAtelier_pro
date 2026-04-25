from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import require_audit_view
from app.db.session import get_db
from app.modules.core_platform.audit import record_audit
from app.modules.core_platform.audit_explorer import list_audit_events, list_destructive_actions, list_nightly_ops_events
from app.modules.core_platform.schemas import AuditEventPageResponse
from app.modules.identity.models import User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events", response_model=AuditEventPageResponse)
def list_audit_events_route(
    actor_user_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    target_id: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_audit_view),
) -> AuditEventPageResponse:
    return AuditEventPageResponse.model_validate(
        list_audit_events(
            db,
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/destructive-actions", response_model=AuditEventPageResponse)
def list_destructive_actions_route(
    actor_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    target_id: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_audit_view),
) -> AuditEventPageResponse:
    return AuditEventPageResponse.model_validate(
        list_destructive_actions(
            db,
            actor_user_id=actor_user_id,
            target_type=target_type,
            target_id=target_id,
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/nightly-ops", response_model=AuditEventPageResponse)
def list_nightly_ops_events_route(
    actor_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    target_id: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_audit_view),
) -> AuditEventPageResponse:
    return AuditEventPageResponse.model_validate(
        list_nightly_ops_events(
            db,
            actor_user_id=actor_user_id,
            target_type=target_type,
            target_id=target_id,
            branch_id=branch_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/nightly-ops.csv")
def export_nightly_ops_csv_route(
    actor_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    target_id: str | None = Query(default=None),
    branch_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    search: str | None = Query(default=None),
    export_reason: str | None = Query(default=None, max_length=500),
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_audit_view),
) -> Response:
    active_filters = {
        "actor_user_id": actor_user_id,
        "target_type": target_type,
        "target_id": target_id,
        "branch_id": branch_id,
        "date_from": date_from,
        "date_to": date_to,
        "search": search,
    }
    clean_filters = {key: value for key, value in active_filters.items() if value}
    payload = list_nightly_ops_events(
        db,
        actor_user_id=actor_user_id,
        target_type=target_type,
        target_id=target_id,
        branch_id=branch_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=1,
        page_size=limit,
    )
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["# exported_at_utc", datetime.now(UTC).isoformat()])
    writer.writerow(["# exported_rows", payload["total"]])
    writer.writerow(["# active_filters", json.dumps(clean_filters, ensure_ascii=False)])
    writer.writerow(["occurred_at", "action", "actor", "target_type", "target_id", "summary", "success", "error_code"])
    for row in payload["items"]:
        writer.writerow(
            [
                row.get("occurred_at"),
                row.get("action"),
                row.get("actor_name") or row.get("actor_user_id") or "",
                row.get("target_type"),
                row.get("target_id") or "",
                row.get("summary"),
                row.get("success"),
                row.get("error_code") or "",
            ]
        )
    record_audit(
        db,
        actor_user_id=current_user.id,
        action="audit.nightly_ops_exported",
        target_type="audit_export",
        target_id="nightly_ops_csv",
        summary=f"Exported nightly ops CSV with {payload['total']} rows",
        diff={"filters": clean_filters, "rows": payload["total"], "limit": limit},
        reason_text=(export_reason.strip() if export_reason else None),
    )
    db.commit()
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="nightly-ops-audit.csv"',
            "X-Exported-Rows": str(payload["total"]),
            "X-Active-Filters": json.dumps(clean_filters, ensure_ascii=False),
        },
    )
