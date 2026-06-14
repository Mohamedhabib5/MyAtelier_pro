from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.organization.service import get_company_settings
from app.modules.exports.models import DailyEmailReportConfig
from app.modules.exports.daily_report_service import send_email_report
from app.modules.core_platform.security_service import decrypt_secret
from app.modules.bookings.calculations import booking_total_amount, booking_paid_total, booking_remaining_amount

logger = logging.getLogger("notifications")


def get_active_email_config(db: Session) -> DailyEmailReportConfig | None:
    return db.query(DailyEmailReportConfig).filter(DailyEmailReportConfig.is_active == True).first()


def send_email_async(sender_email: str, sender_password: str, recipient_emails: str, subject: str, html_content: str, smtp_server: str, smtp_port: int):
    threading.Thread(
        target=send_email_report,
        args=(sender_email, sender_password, recipient_emails, subject, html_content, smtp_server, smtp_port),
        daemon=True
    ).start()


def generate_booking_html(booking, template_type: str, is_new: bool) -> str:
    action_title = "إضافة حجز جديد" if is_new else "تعديل حجز قائم"
    status_ar = {
        "confirmed": "مؤكد",
        "completed": "مكتمل",
        "draft": "مسودة",
        "cancelled": "ملغي"
    }.get(booking.status, booking.status)

    lines_html = ""
    if template_type == "detailed":
        lines_html = """
        <div style="font-weight:700; margin-top:20px; margin-bottom:10px; color:#1e293b; border-bottom: 2px solid #edf2f7; padding-bottom:5px; text-align:right;">تفاصيل الخدمات المحجوزة:</div>
        <table style="width:100%; border-collapse:collapse; font-size:13px; margin-bottom:20px; direction:rtl;">
            <thead>
                <tr style="background:#f1f5f9; color:#475569; font-weight:700;">
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">الخدمة</th>
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">القسم</th>
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">تاريخ الخدمة</th>
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">رمز الفستان</th>
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">السعر</th>
                </tr>
            </thead>
            <tbody>
        """
        for line in booking.lines:
            dress_code = line.dress.code if line.dress else "-"
            line_status = " (ملغي)" if line.status == "cancelled" else ""
            lines_html += f"""
                <tr>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{line.service.name}{line_status}</td>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{line.department.name}</td>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{line.service_date.strftime('%Y-%m-%d') if line.service_date else '-'}</td>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{dress_code}</td>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{float(line.line_price):,.2f}</td>
                </tr>
            """
        lines_html += "</tbody></table>"

    html = f"""<!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f8; color: #333; direction: rtl; text-align: right; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); padding: 25px; border-top: 5px solid #6366f1; direction: rtl; }}
            .header {{ font-size: 20px; font-weight: bold; color: #1e293b; margin-bottom: 20px; border-bottom: 1px solid #edf2f7; padding-bottom: 10px; text-align: right; }}
            .info-row {{ margin-bottom: 10px; font-size: 14px; text-align: right; }}
            .info-label {{ font-weight: bold; color: #64748b; display: inline-block; width: 120px; text-align: right; }}
            .info-value {{ color: #0f172a; }}
            .financials {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; margin-top: 20px; direction: rtl; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">تنبيه حجز: {action_title}</div>
            
            <div class="info-row">
                <span class="info-label">رقم الحجز:</span>
                <span class="info-value"><b>{booking.booking_number}</b></span>
            </div>
            <div class="info-row">
                <span class="info-label">اسم العميلة:</span>
                <span class="info-value">{booking.customer.full_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">تاريخ الحجز:</span>
                <span class="info-value">{booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else '-'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">حالة الحجز:</span>
                <span class="info-value">{status_ar}</span>
            </div>
            
            {lines_html}

            <div class="financials">
                <div class="info-row"><span class="info-label">إجمالي الحجز:</span><span class="info-value"><b>{float(booking_total_amount(booking)):,.2f}</b></span></div>
                <div class="info-row"><span class="info-label">المدفوع:</span><span class="info-value">{float(booking_paid_total(booking)):,.2f}</span></div>
                <div class="info-row"><span class="info-label">المتبقي:</span><span class="info-value" style="color:#b91c1c;"><b>{float(booking_remaining_amount(booking)):,.2f}</b></span></div>
            </div>

            <div style="font-size: 11px; color: #94a3b8; text-align: center; margin-top: 30px; border-top: 1px solid #edf2f7; padding-top: 10px;">
                تم الإرسال تلقائياً بواسطة MyAtelier Pro في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
            </div>
        </div>
    </body>
    </html>"""
    return html


def generate_payment_html(payment, template_type: str, is_refund: bool) -> str:
    kind_title = "سند صرف / إرجاع" if is_refund else "سند قبض / تحصيل جديد"
    method_name = payment.payment_method.name if payment.payment_method else "غير محدد"
    
    allocations_html = ""
    if template_type == "detailed" and not is_refund:
        allocations_html = """
        <div style="font-weight:700; margin-top:20px; margin-bottom:10px; color:#1e293b; border-bottom: 2px solid #edf2f7; padding-bottom:5px; text-align:right;">التوزيع على الحجوزات:</div>
        <table style="width:100%; border-collapse:collapse; font-size:13px; margin-bottom:20px; direction:rtl;">
            <thead>
                <tr style="background:#f1f5f9; color:#475569; font-weight:700;">
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">رقم الحجز</th>
                    <th style="padding:10px; border:1px solid #cbd5e1; text-align:right;">المبلغ الموزع</th>
                </tr>
            </thead>
            <tbody>
        """
        for alloc in payment.allocations:
            allocations_html += f"""
                <tr>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{alloc.booking.booking_number}</td>
                    <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{float(alloc.amount):,.2f}</td>
                </tr>
            """
        allocations_html += "</tbody></table>"

    html = f"""<!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f8; color: #33; direction: rtl; text-align: right; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); padding: 25px; border-top: 5px solid #10b981; direction: rtl; }}
            .header {{ font-size: 20px; font-weight: bold; color: #1e293b; margin-bottom: 20px; border-bottom: 1px solid #edf2f7; padding-bottom: 10px; text-align: right; }}
            .info-row {{ margin-bottom: 10px; font-size: 14px; text-align: right; }}
            .info-label {{ font-weight: bold; color: #64748b; display: inline-block; width: 120px; text-align: right; }}
            .info-value {{ color: #0f172a; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">حركة مالية: {kind_title}</div>
            
            <div class="info-row">
                <span class="info-label">رقم السند:</span>
                <span class="info-value"><b>{payment.payment_number}</b></span>
            </div>
            <div class="info-row">
                <span class="info-label">العميل:</span>
                <span class="info-value">{payment.customer.full_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">القيمة:</span>
                <span class="info-value" style="font-size:16px; color:#15803d;"><b>{float(payment.amount):,.2f}</b></span>
            </div>
            <div class="info-row">
                <span class="info-label">طريقة الدفع:</span>
                <span class="info-value">{method_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">تاريخ الحركة:</span>
                <span class="info-value">{payment.payment_date.strftime('%Y-%m-%d') if payment.payment_date else '-'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">ملاحظات:</span>
                <span class="info-value">{payment.notes or '-'}</span>
            </div>

            {allocations_html}

            <div style="font-size: 11px; color: #94a3b8; text-align: center; margin-top: 30px; border-top: 1px solid #edf2f7; padding-top: 10px;">
                تم الإرسال تلقائياً بواسطة MyAtelier Pro في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
            </div>
        </div>
    </body>
    </html>"""
    return html


def dispatch_booking_notification(db: Session, booking, is_new: bool):
    config = get_active_email_config(db)
    if not config:
        return

    should_send = config.notify_booking_created if is_new else config.notify_booking_modified
    if not should_send:
        return

    try:
        decrypted_password = decrypt_secret(config.sender_password)
        template = config.booking_email_template or "detailed"
        html = generate_booking_html(booking, template, is_new)
        
        subject = f"تنبيه حجز جديد: {booking.booking_number} - {booking.customer.full_name}" if is_new else f"تعديل حجز: {booking.booking_number} - {booking.customer.full_name}"
        
        send_email_async(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=subject,
            html_content=html,
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port
        )
        logger.info(f"Notification email triggered asynchronously for booking {booking.booking_number}")
    except Exception as e:
        logger.error(f"Failed to dispatch booking notification: {str(e)}")


def dispatch_payment_notification(db: Session, payment, is_refund: bool):
    config = get_active_email_config(db)
    if not config:
        return

    should_send = config.notify_payment_refunded if is_refund else config.notify_payment_captured
    if not should_send:
        return

    try:
        decrypted_password = decrypt_secret(config.sender_password)
        template = config.payment_email_template or "detailed"
        html = generate_payment_html(payment, template, is_refund)
        
        subject = f"حركة صندوق: سند صرف {payment.payment_number}" if is_refund else f"حركة صندوق: سند قبض {payment.payment_number}"
        
        send_email_async(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=subject,
            html_content=html,
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port
        )
        logger.info(f"Notification email triggered asynchronously for payment {payment.payment_number}")
    except Exception as e:
        logger.error(f"Failed to dispatch payment notification: {str(e)}")


def dispatch_deletion_notification(db: Session, actor_username: str, entity_name: str, entity_ident: str, details: str):
    config = get_active_email_config(db)
    if not config or not config.notify_entity_deleted:
        return

    try:
        decrypted_password = decrypt_secret(config.sender_password)
        html = f"""<!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"></head>
        <body style="font-family:Arial; direction:rtl; text-align:right; padding:20px;">
            <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; padding:25px; border-top:5px solid #d32f2f; box-shadow:0 4px 6px rgba(0,0,0,0.05); direction:rtl;">
                <div style="font-size:20px; font-weight:bold; color:#b91c1c; margin-bottom:20px; border-bottom:1px solid #edf2f7; padding-bottom:10px; text-align:right;">🚨 تنبيه أمني: إجراء حذف / تعطيل في النظام</div>
                <p style="text-align:right;">تم رصد إجراء حذف أو تعطيل لعنصر مهم في النظام بالبيانات التالية:</p>
                <div style="margin-bottom:10px; text-align:right;"><b>المستخدم المنفذ:</b> {actor_username}</div>
                <div style="margin-bottom:10px; text-align:right;"><b>نوع العنصر:</b> {entity_name}</div>
                <div style="margin-bottom:10px; text-align:right;"><b>مُعرِّف العنصر:</b> {entity_ident}</div>
                <div style="margin-bottom:15px; padding:10px; background:#fef2f2; border:1px solid #fecaca; border-radius:6px; color:#991b1b; text-align:right;">
                    <b>تفاصيل العنصر المحذوف:</b> {details}
                </div>
                <div style="font-size:11px; color:#94a3b8; text-align:center; margin-top:30px; border-top:1px solid #edf2f7; padding-top:10px;">
                    تم الإرسال تلقائياً بواسطة MyAtelier Pro في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
                </div>
            </div>
        </body>
        </html>"""
        
        send_email_async(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=f"🚨 تنبيه أمني: إجراء حذف لعنصر ({entity_name}) بواسطة {actor_username}",
            html_content=html,
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port
        )
        logger.info(f"Deletion security notification triggered asynchronously")
    except Exception as e:
        logger.error(f"Failed to dispatch deletion notification: {str(e)}")


def dispatch_financial_critical_notification(db: Session, actor_username: str, action: str, details: str):
    config = get_active_email_config(db)
    if not config or not config.notify_financial_critical:
        return

    try:
        decrypted_password = decrypt_secret(config.sender_password)
        html = f"""<!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"></head>
        <body style="font-family:Arial; direction:rtl; text-align:right; padding:20px;">
            <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; padding:25px; border-top:5px solid #d97706; box-shadow:0 4px 6px rgba(0,0,0,0.05); direction:rtl;">
                <div style="font-size:20px; font-weight:bold; color:#d97706; margin-bottom:20px; border-bottom:1px solid #edf2f7; padding-bottom:10px; text-align:right;">⚠️ تنبيه مالي حرج</div>
                <p style="text-align:right;">تم رصد عملية حساسة تؤثر على الحسابات والقيود المالية:</p>
                <div style="margin-bottom:10px; text-align:right;"><b>المستخدم المنفذ:</b> {actor_username}</div>
                <div style="margin-bottom:10px; text-align:right;"><b>نوع الإجراء:</b> {action}</div>
                <div style="margin-bottom:15px; padding:10px; background:#fffbeb; border:1px solid #fef3c7; border-radius:6px; color:#92400e; text-align:right;">
                    <b>التفاصيل:</b> {details}
                </div>
                <div style="font-size:11px; color:#94a3b8; text-align:center; margin-top:30px; border-top:1px solid #edf2f7; padding-top:10px;">
                    تم الإرسال تلقائياً بواسطة MyAtelier Pro في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
                </div>
            </div>
        </body>
        </html>"""
        
        send_email_async(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=f"⚠️ تنبيه حركة مالية حساسة: {action}",
            html_content=html,
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port
        )
        logger.info(f"Financial critical notification triggered asynchronously")
    except Exception as e:
        logger.error(f"Failed to dispatch financial critical notification: {str(e)}")


def dispatch_backup_alert_notification(db: Session, is_stale: bool, error_msg: str | None = None):
    config = get_active_email_config(db)
    if not config or not config.notify_backup_warnings:
        return

    title = "تحذير: تأخر تحديث النسخ الاحتياطي" if is_stale else "عاجل: فشل إنشاء النسخة الاحتياطية"
    color = "#f59e0b" if is_stale else "#ef4444"
    details = f"مرت أكثر من 30 ساعة دون رصد نسخة احتياطية صحية جديدة للنظام." if is_stale else f"فشل النظام في إنشاء النسخة الاحتياطية المجدولة تلقائياً مع الخطأ التالي:<br/><b>{error_msg}</b>"

    try:
        decrypted_password = decrypt_secret(config.sender_password)
        html = f"""<!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head><meta charset="UTF-8"></head>
        <body style="font-family:Arial; direction:rtl; text-align:right; padding:20px;">
            <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; padding:25px; border-top:5px solid {color}; box-shadow:0 4px 6px rgba(0,0,0,0.05); direction:rtl;">
                <div style="font-size:20px; font-weight:bold; color:{color}; margin-bottom:20px; border-bottom:1px solid #edf2f7; padding-bottom:10px; text-align:right;">💾 {title}</div>
                <p style="font-size:14px; line-height:1.6; color:#1e293b; text-align:right;">{details}</p>
                <div style="font-size:11px; color:#94a3b8; text-align:center; margin-top:30px; border-top:1px solid #edf2f7; padding-top:10px;">
                    تم الإرسال تلقائياً بواسطة MyAtelier Pro في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
                </div>
            </div>
        </body>
        </html>"""
        
        send_email_async(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=f"💾 {title}",
            html_content=html,
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port
        )
        logger.info(f"Backup health alert triggered asynchronously")
    except Exception as e:
        logger.error(f"Failed to dispatch backup warning notification: {str(e)}")


def send_daily_operations_digest(db: Session):
    from datetime import date
    config = get_active_email_config(db)
    if not config or not config.notify_operations_daily:
        return

    company = get_company_settings(db)
    today_date = date.today()
    
    # Query all booking lines scheduled for today (service_date == today)
    # where the booking and line are not cancelled
    from app.modules.bookings.models import Booking, BookingLine
    
    lines = db.query(BookingLine).join(Booking).filter(
        Booking.company_id == company.id,
        Booking.status != 'cancelled',
        BookingLine.service_date == today_date,
        BookingLine.status != 'cancelled'
    ).order_by(BookingLine.line_number.asc()).all()
    
    if not lines:
        logger.info("No operations scheduled for today. Skipping digest email.")
        return

    lines_html = ""
    for line in lines:
        dress_code = line.dress.code if line.dress else "-"
        customer_name = line.booking.customer.full_name if line.booking.customer else "-"
        customer_phone = line.booking.customer.phone if line.booking.customer else "-"
        
        lines_html += f"""
            <tr>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{line.booking.booking_number}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{customer_name}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{customer_phone}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{line.service.name}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{line.department.name}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:right;">{dress_code}</td>
            </tr>
        """

    html = f"""<!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f8; color: #333; direction: rtl; text-align: right; padding: 20px; }}
            .container {{ max-width: 700px; margin: 0 auto; background: #fff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); padding: 25px; border-top: 5px solid #3b82f6; direction: rtl; }}
            .header {{ font-size: 20px; font-weight: bold; color: #1e293b; margin-bottom: 20px; border-bottom: 1px solid #edf2f7; padding-bottom: 10px; text-align: right; }}
            table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:20px; direction:rtl; }}
            th {{ background:#f1f5f9; color:#475569; font-weight:700; padding:10px; border:1px solid #cbd5e1; text-align:right; }}
            td {{ padding:10px; border:1px solid #e2e8f0; text-align:right; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">الملخص التشغيلي الصباحي ليوم {today_date.strftime('%Y-%m-%d')}</div>
            <p>فيما يلي قائمة بكافة المواعيد والخدمات المقررة اليوم في النظام:</p>
            
            <table>
                <thead>
                    <tr>
                        <th>رقم الحجز</th>
                        <th>العميلة</th>
                        <th>رقم الهاتف</th>
                        <th>الخدمة</th>
                        <th>القسم</th>
                        <th>كود الفستان</th>
                    </tr>
                </thead>
                <tbody>
                    {lines_html}
                </tbody>
            </table>

            <div style="font-size: 11px; color: #94a3b8; text-align: center; margin-top: 30px; border-top: 1px solid #edf2f7; padding-top: 10px;">
                تم الإرسال تلقائياً بواسطة MyAtelier Pro في {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
            </div>
        </div>
    </body>
    </html>"""

    try:
        decrypted_password = decrypt_secret(config.sender_password)
        subject = f"📋 الملخص التشغيلي اليومي - مواعيد يوم {today_date.strftime('%Y-%m-%d')}"
        
        send_email_async(
            sender_email=config.sender_email,
            sender_password=decrypted_password,
            recipient_emails=config.recipient_email,
            subject=subject,
            html_content=html,
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port
        )
        logger.info("Daily operations morning digest triggered asynchronously.")
    except Exception as e:
        logger.error(f"Failed to dispatch daily operations morning digest: {str(e)}")
