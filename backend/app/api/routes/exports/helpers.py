from __future__ import annotations

from urllib.parse import quote
from fastapi import Response


def _csv_response(filename: str, content: bytes | str) -> Response:
    if isinstance(content, str):
        content_bytes = content.encode('utf-8-sig')
    else:
        content_bytes = content

    basename = filename.split('.')[0]
    ext = filename.split('.')[-1] if '.' in filename else 'csv'
    ascii_basename = basename.encode('ascii', 'ignore').decode('ascii')
    if not ascii_basename:
        ascii_basename = 'download'
    ascii_filename = f"{ascii_basename}.{ext}"
    
    encoded_filename = quote(filename)
    headers = {
        'Content-Disposition': f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    return Response(content=content_bytes, media_type='text/csv; charset=utf-8', headers=headers)


def _pdf_response(filename: str, content: bytes) -> Response:
    ascii_filename = filename.encode('ascii', 'ignore').decode('ascii') or 'download.pdf'
    encoded_filename = quote(filename)
    disposition = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    headers = {
        'Content-Disposition': disposition,
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    return Response(content=content, media_type='application/pdf', headers=headers)


def _xlsx_response(filename: str, content: bytes) -> Response:
    basename = filename.split('.')[0]
    ext = filename.split('.')[-1] if '.' in filename else 'xlsx'
    ascii_basename = basename.encode('ascii', 'ignore').decode('ascii')
    if not ascii_basename:
        ascii_basename = 'download'
    ascii_filename = f"{ascii_basename}.{ext}"
    
    encoded_filename = quote(filename)
    headers = {
        'Content-Disposition': f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}',
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    return Response(content=content, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)
