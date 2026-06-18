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

from app.modules.exports.daily_report_templates import generate_daily_report_html

def send_email_report(
    sender_email: str,
    sender_password: str,
    recipient_emails: str,
    subject: str,
    html_content: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587
):
    recipients = [email.strip() for email in recipient_emails.split(",") if email.strip()]
    if not recipients:
        raise ValueError("لا يوجد مستلمون محددون لإرسال التقرير البريدي.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Gmail requires STARTTLS and login authentication
    server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipients, msg.as_string())
    server.quit()

def run_test_report_for_config(db: Session, config_id: str, company_id: str, report_date: date | None = None) -> dict:
    company = get_company_settings(db)
    config = db.query(DailyEmailReportConfig).filter(
        DailyEmailReportConfig.id == config_id,
        DailyEmailReportConfig.company_id == company_id
    ).first()
    if not config:
        raise ValidationAppError("تكوين البريد غير موجود")

    try:
        decrypted_password = decrypt_secret(config.sender_password)
    except Exception as e:
        return {"success": False, "error": f"فشل فك تشفير كلمة المرور: {str(e)}"}

    target_date = report_date or date.today()
    try:
        html_content = generate_daily_report_html(db, company, target_date)
        subject = f"بريد تجريبي: التقرير اليومي لحجوزات وحصيلة يوم {target_date.strftime('%Y-%m-%d')} - {config.name}"
        
        send_email_report(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=subject,
            html_content=html_content,
            smtp_server=config.smtp_server or "smtp.gmail.com",
            smtp_port=config.smtp_port or 587
        )
        return {"success": True, "message": "تم إرسال البريد التجريبي بنجاح"}
    except Exception as e:
        return {"success": False, "error": str(e)}

