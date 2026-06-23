from __future__ import annotations

from datetime import datetime
from typing import Any
from app.modules.dashboard.schemas import FinanceDashboardResponse
from app.modules.reports.schemas import ReportsOverviewResponse


def build_simple_pdf_report(*, title: str, lines: list[str]) -> bytes:
    content_lines = [
        "BT",
        "/F1 14 Tf",
        "50 800 Td",
        f"{_pdf_text(title)} Tj",
        "/F1 10 Tf",
    ]
    y = 780
    for line in lines[:35]:
        content_lines.append(f"50 {y} Td")
        content_lines.append(f"{_pdf_text(line)} Tj")
        y -= 18
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("utf-8")

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode("utf-8") + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    output = bytearray()
    output.extend(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def finance_pdf_lines(payload: Any) -> list[str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    def val(key: str) -> Any:
        return payload.get(key) if isinstance(payload, dict) else getattr(payload, key)
    return [
        f"Generated at: {now}",
        f"Total income: {val('total_income')}",
        f"Total remaining: {val('total_remaining')}",
        f"Total bookings: {val('total_bookings')}",
        f"Daily income items: {len(val('daily_income'))}",
        f"Department income items: {len(val('department_income'))}",
        f"Top services items: {len(val('top_services'))}",
    ]


def reports_pdf_lines(payload: Any) -> list[str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    def val(key: str) -> Any:
        return payload.get(key) if isinstance(payload, dict) else getattr(payload, key)
    return [
        f"Generated at: {now}",
        f"Active customers: {val('active_customers')}",
        f"Active services: {val('active_services')}",
        f"Available dresses: {val('available_dresses')}",
        f"Upcoming bookings: {val('upcoming_bookings')}",
        f"Booking status items: {len(val('booking_status_counts'))}",
        f"Payment type items: {len(val('payment_type_totals'))}",
        f"Dress status items: {len(val('dress_status_counts'))}",
    ]


def _pdf_text(value: str) -> str:
    text = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"({text})"
