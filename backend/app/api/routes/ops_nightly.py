from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.deps import require_settings_manage
from app.core.exceptions import AuthorizationError
from app.db.session import get_db
from app.modules.core_platform.nightly_status import get_latest_nightly_snapshot, ingest_nightly_failure_report, is_valid_nightly_ingest_token
from app.modules.core_platform.schemas import NightlyFailureIngestResponse, NightlyFailureReportRequest, NightlyRunSnapshotResponse
from app.modules.identity.models import User

router = APIRouter(prefix="/settings/ops/nightly", tags=["settings"])


@router.post("/failure-report", response_model=NightlyFailureIngestResponse)
def ingest_nightly_failure_report_route(
    payload: NightlyFailureReportRequest,
    request: Request,
    db: Session = Depends(get_db),
    x_nightly_token: str | None = Header(default=None, alias="X-Nightly-Token"),
) -> NightlyFailureIngestResponse:
    expected_token = request.app.state.settings.nightly_failure_ingest_token
    if not is_valid_nightly_ingest_token(expected_token=expected_token, provided_token=x_nightly_token):
        raise AuthorizationError("Invalid nightly ingest token.")

    result = ingest_nightly_failure_report(
        db,
        payload=payload,
        source_ip=(request.client.host if request.client else None),
        user_agent=request.headers.get("user-agent"),
    )
    return NightlyFailureIngestResponse.model_validate(result)


@router.get("/latest", response_model=NightlyRunSnapshotResponse)
def get_latest_nightly_snapshot_route(
    db: Session = Depends(get_db),
    _: User = Depends(require_settings_manage),
) -> NightlyRunSnapshotResponse:
    payload = get_latest_nightly_snapshot(db)
    return NightlyRunSnapshotResponse.model_validate(payload)
