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
from app.modules.exports.daily_report_runner import send_email_report

def check_and_run_due_reports(db: Session):
    # 1. Trigger morning operations digest if not sent today yet
    from app.modules.core_platform.repository import CorePlatformRepository
    from app.modules.exports.notification_service import send_daily_operations_digest
    
    today_str = date.today().isoformat()
    core_repo = CorePlatformRepository(db)
    setting_key = "exports.last_ops_digest_sent_date"
    last_sent_setting = core_repo.get_setting(setting_key)
    
    if not last_sent_setting or last_sent_setting.value != today_str:
        logger.info("Operations digest not sent today yet. Triggering send_daily_operations_digest...")
        try:
            send_daily_operations_digest(db)
            core_repo.set_setting(setting_key, today_str)
            db.commit()
            logger.info("Successfully sent operations digest for today and updated setting.")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to send operations digest: {str(e)}")

    # 1.5 Trigger daily audit chain integrity check if not run today
    audit_setting_key = "audit.last_chain_integrity_check_date"
    last_audit_check = core_repo.get_setting(audit_setting_key)
    
    if not last_audit_check or last_audit_check.value != today_str:
        logger.info("Daily audit chain check not run today yet. Triggering verify_chain_integrity...")
        try:
            from app.modules.core_platform.audit import verify_chain_integrity
            res = verify_chain_integrity(db)
            if res["success"]:
                logger.info(f"Daily audit chain intact. Verified {res['total_verified']} logs.")
            else:
                logger.error(f"Daily audit chain broken! Issues: {res['issues']}")
                
            core_repo.set_setting(audit_setting_key, today_str)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to run daily audit chain check: {str(e)}")

    configs = db.query(DailyEmailReportConfig).filter(DailyEmailReportConfig.is_active == True).all()
    if not configs:
        logger.info("No active daily email report configurations found. Skipping run.")
        return {"status": "skipped", "reason": "no_configs"}

    company = get_company_settings(db)
    total_sent = 0
    failed_date = None
    last_error = None
    halted = False

    for config in configs:
        today = date.today()
        due_dates = []
        for i in range(7, -1, -1):
            d = today - timedelta(days=i)
            if d == today:
                current_hour = datetime.now().hour
                if current_hour < config.send_hour:
                    continue
            due_dates.append(d)

        due_dates.sort()

        try:
            decrypted_password = decrypt_secret(config.sender_password)
        except Exception as e:
            logger.error(f"Failed to decrypt password for config {config.name}: {str(e)}")
            continue

        for d in due_dates:
            log = db.query(DailyEmailReportLog).filter(
                DailyEmailReportLog.config_id == config.id,
                DailyEmailReportLog.report_date == d
            ).first()

            if not log:
                log = DailyEmailReportLog(config_id=config.id, report_date=d, status='pending', attempts=0)
                db.add(log)
                db.flush()

            if log.status == 'sent':
                continue

            log.attempts += 1
            log.last_attempt_at = datetime.now(timezone.utc)

            try:
                html_content = generate_daily_report_html(db, company, d)
                subject = f"التقرير اليومي لحجوزات وحصيلة يوم {d.strftime('%Y-%m-%d')} - {config.name}"
                
                send_email_report(
                    sender_email=config.sender_email,
                    sender_password=decrypted_password,
                    recipient_emails=config.recipient_email,
                    subject=subject,
                    html_content=html_content,
                    smtp_server=config.smtp_server or "smtp.gmail.com",
                    smtp_port=config.smtp_port or 587
                )

                log.status = 'sent'
                log.error_message = None
                db.commit()
                total_sent += 1
                logger.info(f"Successfully sent daily report for {d} using config {config.name}")
            except Exception as e:
                db.rollback()
                log.status = 'failed'
                log.error_message = str(e)
                db.commit()
                logger.error(f"Failed to send daily report for {d} using config {config.name}: {str(e)}")
                failed_date = d
                last_error = str(e)
                halted = True
                break

    return {
        "status": "completed" if not halted else "halted",
        "sent_count": total_sent,
        "failed_date": str(failed_date) if failed_date else None,
        "error": last_error
    }

