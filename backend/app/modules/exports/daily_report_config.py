from __future__ import annotations
import json
import logging
import smtplib
from datetime import date, datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decimal import Decimal
from sqlalchemy import func, Date
from sqlalchemy.orm import Session
from app.modules.organization.service import get_company_settings
from app.modules.organization.models import Company
from app.modules.bookings.models import Booking, BookingLine
from app.modules.payments.models import PaymentDocument
from app.modules.core_platform.models import AuditLog
from app.modules.exports.models import DailyEmailReportConfig, DailyEmailReportLog
from app.modules.bookings.calculations import booking_total_amount, booking_paid_total, booking_remaining_amount
from app.modules.payments.serializers import document_total
from app.core.security import encrypt_secret, decrypt_secret
from app.core.exceptions import ValidationAppError
logger = logging.getLogger("daily_report")

def list_daily_report_configs(db: Session, company_id: str) -> list[dict]:
    configs = db.query(DailyEmailReportConfig).filter(DailyEmailReportConfig.company_id == company_id).order_by(DailyEmailReportConfig.name.asc()).all()
    res = []
    for c in configs:
        res.append({
            "id": c.id,
            "company_id": c.company_id,
            "name": c.name,
            "sender_email": c.sender_email,
            "sender_password": "********" if c.sender_password else "",
            "smtp_server": c.smtp_server,
            "smtp_port": c.smtp_port,
            "recipient_email": c.recipient_email,
            "send_hour": c.send_hour,
            "is_active": c.is_active
        })
    return res

def create_daily_report_config(db: Session, company_id: str, payload) -> dict:
    encrypted_pass = encrypt_secret(payload.sender_password)
    config = DailyEmailReportConfig(
        company_id=company_id,
        name=payload.name.strip(),
        sender_email=payload.sender_email.strip(),
        sender_password=encrypted_pass,
        smtp_server=payload.smtp_server.strip() if payload.smtp_server else 'smtp.gmail.com',
        smtp_port=payload.smtp_port if payload.smtp_port is not None else 587,
        recipient_email=payload.recipient_email.strip(),
        send_hour=payload.send_hour,
        is_active=payload.is_active
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return {
        "id": config.id,
        "company_id": config.company_id,
        "name": config.name,
        "sender_email": config.sender_email,
        "sender_password": "********",
        "smtp_server": config.smtp_server,
        "smtp_port": config.smtp_port,
        "recipient_email": config.recipient_email,
        "send_hour": config.send_hour,
        "is_active": config.is_active
    }

def update_daily_report_config(db: Session, config_id: str, company_id: str, payload) -> dict:
    config = db.query(DailyEmailReportConfig).filter(
        DailyEmailReportConfig.id == config_id,
        DailyEmailReportConfig.company_id == company_id
    ).first()
    if not config:
        raise ValidationAppError("تكوين البريد غير موجود")

    if payload.name is not None:
        config.name = payload.name.strip()
    if payload.sender_email is not None:
        config.sender_email = payload.sender_email.strip()
    if payload.sender_password is not None and payload.sender_password.strip() not in ("", "********"):
        config.sender_password = encrypt_secret(payload.sender_password.strip())
    if payload.smtp_server is not None:
        config.smtp_server = payload.smtp_server.strip()
    if payload.smtp_port is not None:
        config.smtp_port = payload.smtp_port
    if payload.recipient_email is not None:
        config.recipient_email = payload.recipient_email.strip()
    if payload.send_hour is not None:
        config.send_hour = payload.send_hour
    if payload.is_active is not None:
        config.is_active = payload.is_active

    db.commit()
    db.refresh(config)
    return {
        "id": config.id,
        "company_id": config.company_id,
        "name": config.name,
        "sender_email": config.sender_email,
        "sender_password": "********",
        "smtp_server": config.smtp_server,
        "smtp_port": config.smtp_port,
        "recipient_email": config.recipient_email,
        "send_hour": config.send_hour,
        "is_active": config.is_active
    }

def delete_daily_report_config(db: Session, config_id: str, company_id: str) -> None:
    config = db.query(DailyEmailReportConfig).filter(
        DailyEmailReportConfig.id == config_id,
        DailyEmailReportConfig.company_id == company_id
    ).first()
    if config:
        db.delete(config)
        db.commit()

