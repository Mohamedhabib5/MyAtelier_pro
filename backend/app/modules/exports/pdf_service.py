from __future__ import annotations

from datetime import datetime


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


def finance_pdf_lines(payload: dict) -> list[str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        f"Generated at: {now}",
        f"Total income: {payload.get('total_income', 0)}",
        f"Total remaining: {payload.get('total_remaining', 0)}",
        f"Total bookings: {payload.get('total_bookings', 0)}",
        f"Daily income items: {len(payload.get('daily_income', []))}",
        f"Department income items: {len(payload.get('department_income', []))}",
        f"Top services items: {len(payload.get('top_services', []))}",
    ]


def reports_pdf_lines(payload: dict) -> list[str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        f"Generated at: {now}",
        f"Active customers: {payload.get('active_customers', 0)}",
        f"Active services: {payload.get('active_services', 0)}",
        f"Available dresses: {payload.get('available_dresses', 0)}",
        f"Upcoming bookings: {payload.get('upcoming_bookings', 0)}",
        f"Booking status items: {len(payload.get('booking_status_counts', []))}",
        f"Payment type items: {len(payload.get('payment_type_totals', []))}",
        f"Dress status items: {len(payload.get('dress_status_counts', []))}",
    ]


def _pdf_text(value: str) -> str:
    text = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"({text})"
