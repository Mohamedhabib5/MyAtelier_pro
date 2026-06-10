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
from app.modules.core_platform.security_service import encrypt_secret, decrypt_secret
from app.core.exceptions import ValidationAppError

logger = logging.getLogger("daily_report")

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


def generate_daily_report_html(db: Session, company: Company, report_date: date) -> str:
    # 1. Fetch Bookings created on report_date
    bookings = db.query(Booking).filter(
        Booking.company_id == company.id,
        func.cast(Booking.created_at, Date) == report_date
    ).all()

    # 2. Fetch Payments received on report_date (not voided)
    payments = db.query(PaymentDocument).filter(
        PaymentDocument.company_id == company.id,
        PaymentDocument.payment_date == report_date,
        PaymentDocument.status != 'voided'
    ).all()

    # 3. Fetch Audit Logs for booking modifications on report_date
    audit_logs = db.query(AuditLog).filter(
        func.cast(AuditLog.occurred_at, Date) == report_date,
        AuditLog.target_type == 'booking'
    ).order_by(AuditLog.occurred_at.asc()).all()

    # Calculate Summaries
    total_bookings_val = Decimal("0.00")
    total_paid_val = Decimal("0.00")
    total_remaining_val = Decimal("0.00")
    for b in bookings:
        total_bookings_val += booking_total_amount(b)
        total_paid_val += booking_paid_total(b)
        total_remaining_val += booking_remaining_amount(b)

    total_collections = Decimal("0.00")
    total_refunds = Decimal("0.00")
    payment_method_totals: dict[str, Decimal] = {}

    for p in payments:
        p_total = document_total(p)
        method_name = p.payment_method.name if p.payment_method else "غير محدد"
        payment_method_totals[method_name] = payment_method_totals.get(method_name, Decimal("0.00")) + p_total
        
        if p.document_kind == "refund":
            total_refunds += p_total
        else:
            total_collections += p_total

    net_collections = total_collections - total_refunds

    # HTML/CSS Premium Template in RTL
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير المبيعات والتحصيلات اليومي</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
        body {{
            font-family: 'Cairo', Arial, sans-serif;
            background-color: #f4f6f8;
            color: #333333;
            margin: 0;
            padding: 20px;
            direction: rtl;
            text-align: right;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 30px;
            border-top: 6px solid #6366f1;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #edf2f7;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .header h1 {{
            font-size: 24px;
            color: #1e293b;
            margin: 0;
            font-weight: 700;
        }}
        .header p {{
            font-size: 14px;
            color: #64748b;
            margin: 5px 0 0 0;
        }}
        .grid-cards {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .card {{
            flex: 1;
            min-width: 200px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px 20px;
            text-align: center;
        }}
        .card-title {{
            font-size: 13px;
            color: #64748b;
            margin: 0 0 8px 0;
            font-weight: 600;
        }}
        .card-value {{
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
        }}
        .card.primary {{
            border-top: 4px solid #6366f1;
        }}
        .card.success {{
            border-top: 4px solid #10b981;
        }}
        .card.warning {{
            border-top: 4px solid #f59e0b;
        }}
        .section-title {{
            font-size: 17px;
            color: #1e293b;
            border-right: 4px solid #6366f1;
            padding-right: 10px;
            margin: 30px 0 15px 0;
            font-weight: 700;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            font-size: 13px;
        }}
        th {{
            background-color: #f1f5f9;
            color: #475569;
            text-align: right;
            padding: 10px 12px;
            border-bottom: 2px solid #e2e8f0;
            font-weight: 700;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #edf2f7;
            color: #334155;
            vertical-align: middle;
        }}
        tr:hover td {{
            background-color: #f8fafc;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
        }}
        .badge.confirmed {{ background-color: #dcfce7; color: #15803d; }}
        .badge.completed {{ background-color: #dbeafe; color: #1d4ed8; }}
        .badge.draft {{ background-color: #f1f5f9; color: #475569; }}
        .badge.cancelled {{ background-color: #fee2e2; color: #b91c1c; }}
        .badge.refund {{ background-color: #fef3c7; color: #d97706; }}
        .badge.collection {{ background-color: #e0f2fe; color: #0369a1; }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            margin-top: 40px;
            border-top: 1px solid #edf2f7;
            padding-top: 15px;
        }}
        .no-data {{
            text-align: center;
            color: #94a3b8;
            padding: 20px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{company.name}</h1>
            <p>تقرير المبيعات والتحصيلات اليومي ليوم {report_date.strftime('%Y-%m-%d')}</p>
        </div>

        <div class="grid-cards">
            <div class="card primary">
                <div class="card-title">إجمالي الحجوزات الجديدة</div>
                <div class="card-value">{float(total_bookings_val):,.2f} {company.default_currency}</div>
                <div style="font-size:11px; color:#94a3b8; margin-top:5px;">العدد: {len(bookings)}</div>
            </div>
            <div class="card success">
                <div class="card-title">إجمالي التحصيلات (المقبوضات)</div>
                <div class="card-value">{float(total_collections):,.2f} {company.default_currency}</div>
            </div>
            <div class="card warning">
                <div class="card-title">إجمالي المبالغ المستردة</div>
                <div class="card-value">{float(total_refunds):,.2f} {company.default_currency}</div>
            </div>
            <div class="card success">
                <div class="card-title">صافي التدفق النقدي اليومي</div>
                <div class="card-value">{float(net_collections):,.2f} {company.default_currency}</div>
            </div>
        </div>

        <!-- Bookings Section -->
        <div class="section-title">الحجوزات الجديدة المصممة اليوم</div>
        """

    if not bookings:
        html += '<div class="no-data">لم يتم إدخال حجوزات جديدة اليوم.</div>'
    else:
        html += """<table>
            <thead>
                <tr>
                    <th>رقم الحجز</th>
                    <th>العميل</th>
                    <th>الخدمات والأقسام والفساتين</th>
                    <th>الإجمالي</th>
                    <th>المدفوع</th>
                    <th>المتبقي</th>
                    <th>بواسطة</th>
                    <th>الحالة</th>
                    <th>الملاحظات</th>
                </tr>
            </thead>
            <tbody>"""
        for b in bookings:
            # Format lines info
            lines_desc = []
            for line in b.lines:
                dress_info = f" (فستان: {line.dress.code})" if line.dress else ""
                lines_desc.append(f"{line.service.name} - {line.department.name}{dress_info}")
            lines_summary = "<br/>".join(lines_desc)

            status_badge_map = {
                "confirmed": "confirmed",
                "completed": "completed",
                "draft": "draft",
                "cancelled": "cancelled"
            }
            badge_class = status_badge_map.get(b.status, "draft")

            html += f"""
                <tr>
                    <td><b>{b.booking_number}</b></td>
                    <td>{b.customer.full_name}<br/><span style="font-size:11px; color:#64748b;">{b.customer.phone}</span></td>
                    <td>{lines_summary}</td>
                    <td>{float(booking_total_amount(b)):,.2f}</td>
                    <td>{float(booking_paid_total(b)):,.2f}</td>
                    <td>{float(booking_remaining_amount(b)):,.2f}</td>
                    <td>{b.created_by.full_name if b.created_by else 'غير محدد'}</td>
                    <td><span class="badge {badge_class}">{b.status}</span></td>
                    <td>{b.notes or '-'}</td>
                </tr>"""
        html += "</tbody></table>"

    # Payments Section
    html += '<div class="section-title">تفاصيل التحصيل وحركة الصندوق اليومية</div>'
    if not payments:
        html += '<div class="no-data">لم يتم تسجيل أي عمليات تحصيل أو استرداد اليوم.</div>'
    else:
        html += """<table>
            <thead>
                <tr>
                    <th>رقم السند</th>
                    <th>العميل</th>
                    <th>نوع السند</th>
                    <th>طريقة الدفع</th>
                    <th>القيمة</th>
                    <th>الملاحظات</th>
                </tr>
            </thead>
            <tbody>"""
        for p in payments:
            kind_lbl = "تحصيل" if p.document_kind != "refund" else "مسترد"
            kind_badge = "collection" if p.document_kind != "refund" else "refund"
            html += f"""
                <tr>
                    <td><b>{p.payment_number}</b></td>
                    <td>{p.customer.full_name}</td>
                    <td><span class="badge {kind_badge}">{kind_lbl}</span></td>
                    <td>{p.payment_method.name if p.payment_method else 'غير محدد'}</td>
                    <td><b>{float(document_total(p)):,.2f} {company.default_currency}</b></td>
                    <td>{p.notes or '-'}</td>
                </tr>"""
        html += "</tbody></table>"

        # Payment methods breakdown
        html += '<div class="section-title">ملخص التحصيل حسب طريقة الدفع</div>'
        html += """<table style="max-width: 400px;">
            <thead>
                <tr>
                    <th>طريقة الدفع</th>
                    <th>إجمالي التحصيلات</th>
                </tr>
            </thead>
            <tbody>"""
        for method, amt in payment_method_totals.items():
            html += f"""
                <tr>
                    <td>{method}</td>
                    <td><b>{float(amt):,.2f} {company.default_currency}</b></td>
                </tr>"""
        html += "</tbody></table>"

    # Audit Logs Section
    html += '<div class="section-title">سجل تعديلات وإجراءات الحجوزات اليومية</div>'
    if not audit_logs:
        html += '<div class="no-data">لم يتم رصد أي تعديلات على الحجوزات اليوم.</div>'
    else:
        html += """<table>
            <thead>
                <tr>
                    <th>الوقت</th>
                    <th>المستخدم</th>
                    <th>العملية</th>
                    <th>التفاصيل المحدثة (قبل / بعد)</th>
                </tr>
            </thead>
            <tbody>"""
        for log in audit_logs:
            # Format diff JSON
            diff_html = "-"
            if log.diff_json:
                try:
                    diff_data = json.loads(log.diff_json)
                    if isinstance(diff_data, dict):
                        diff_items = []
                        for k, v in diff_data.items():
                            key_ar = {
                                "status": "الحالة",
                                "line_count": "عدد السطور",
                                "entity_version": "إصدار البيانات",
                                "amount": "المبلغ",
                                "notes": "الملاحظات",
                                "booking_date": "تاريخ الحجز",
                                "customer_id": "معرف العميل",
                                "booking_number": "رقم الحجز"
                            }.get(k, k)
                            diff_items.append(f"<b>{key_ar}</b>: {v}")
                        diff_html = ", ".join(diff_items)
                    else:
                        diff_html = str(diff_data)
                except Exception:
                    diff_html = log.diff_json

            # occurred_at display in local time format
            time_str = log.occurred_at.strftime('%I:%M %p') if log.occurred_at else "-"
            actor_name = log.actor.full_name if log.actor else (log.actor_user_id or "النظام")

            html += f"""
                <tr>
                    <td>{time_str}</td>
                    <td>{actor_name}</td>
                    <td>{log.summary}</td>
                    <td>{diff_html}</td>
                </tr>"""
        html += "</tbody></table>"

    html += f"""
        <div class="footer">
            <p>صدر هذا التقرير تلقائياً بواسطة نظام MyAtelier Pro المالي في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>
        </div>
    </div>
</body>
</html>"""
    return html


# CRUD Settings Helpers
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


def run_test_report_for_config(db: Session, config_id: str, company_id: str) -> dict:
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

    today = date.today()
    try:
        html_content = generate_daily_report_html(db, company, today)
        subject = f"بريد تجريبي: التقرير اليومي لحجوزات وحصيلة يوم {today.strftime('%Y-%m-%d')} - {config.name}"
        
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


def check_and_run_due_reports(db: Session):
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
