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

    # 4. Calculate MTD & YTD Totals (MTD = Month to Date, YTD = Year to Date)
    start_of_month = report_date.replace(day=1)
    start_of_year = report_date.replace(month=1, day=1)

    # Sum line prices of active bookings created in MTD
    mtd_bookings_total = db.query(func.coalesce(func.sum(BookingLine.line_price), 0)).join(Booking).filter(
        Booking.company_id == company.id,
        Booking.booking_date >= start_of_month,
        Booking.booking_date <= report_date,
        Booking.status != 'cancelled'
    ).scalar() or Decimal("0.00")

    # Sum line prices of active bookings created in YTD
    ytd_bookings_total = db.query(func.coalesce(func.sum(BookingLine.line_price), 0)).join(Booking).filter(
        Booking.company_id == company.id,
        Booking.booking_date >= start_of_year,
        Booking.booking_date <= report_date,
        Booking.status != 'cancelled'
    ).scalar() or Decimal("0.00")

    # Sum payments collected in MTD (excluding voided and refunds)
    payments_mtd = db.query(PaymentDocument).filter(
        PaymentDocument.company_id == company.id,
        PaymentDocument.payment_date >= start_of_month,
        PaymentDocument.payment_date <= report_date,
        PaymentDocument.status != 'voided'
    ).all()

    mtd_collections_total = Decimal("0.00")
    for p in payments_mtd:
        if p.document_kind != "refund":
            mtd_collections_total += document_total(p)

    # Sum payments collected in YTD (excluding voided and refunds)
    payments_ytd = db.query(PaymentDocument).filter(
        PaymentDocument.company_id == company.id,
        PaymentDocument.payment_date >= start_of_year,
        PaymentDocument.payment_date <= report_date,
        PaymentDocument.status != 'voided'
    ).all()

    ytd_collections_total = Decimal("0.00")
    for p in payments_ytd:
        if p.document_kind != "refund":
            ytd_collections_total += document_total(p)

    # 5. Retrieve bookings for the next two days
    next_day_1 = report_date + timedelta(days=1)
    next_day_2 = report_date + timedelta(days=2)

    bookings_day1 = db.query(Booking).join(BookingLine).filter(
        Booking.company_id == company.id,
        Booking.status != 'cancelled',
        BookingLine.service_date == next_day_1,
        BookingLine.status != 'cancelled'
    ).distinct().order_by(Booking.booking_number.asc()).all()

    bookings_day2 = db.query(Booking).join(BookingLine).filter(
        Booking.company_id == company.id,
        Booking.status != 'cancelled',
        BookingLine.service_date == next_day_2,
        BookingLine.status != 'cancelled'
    ).distinct().order_by(Booking.booking_number.asc()).all()

    # Build next two days bookings tables
    def format_bookings_day_table(day_date: date, day_bookings: list[Booking]) -> str:
        if not day_bookings:
            return f'<div class="no-data">لا توجد حجوزات مجدولة ليوم {day_date.strftime("%Y-%m-%d")}.</div>'
        
        table_html = f"""
        <div style="font-size:14px; font-weight:600; margin: 15px 0 10px 0; color:#475569;">
            مواعيد يوم {day_date.strftime("%Y-%m-%d")}
        </div>
        <table>
            <thead>
                <tr>
                    <th>رقم الحجز</th>
                    <th>العميل</th>
                    <th>العروسة / العريس</th>
                    <th>أرقام الهاتف</th>
                    <th>نوع الحجز والخدمات المجدولة</th>
                    <th>إجمالي الحجز</th>
                    <th>المدفوع</th>
                    <th>المتبقي</th>
                    <th>ملاحظات</th>
                </tr>
            </thead>
            <tbody>"""
        
        for b in day_bookings:
            # Lines scheduled for this day
            day_lines = [line for line in b.lines if line.service_date == day_date and line.status != 'cancelled']
            lines_desc = []
            for line in day_lines:
                dress_info = f" (فستان: {line.dress.code})" if line.dress else ""
                lines_desc.append(f"{line.service.name} - {line.department.name}{dress_info}")
            lines_summary = "<br/>".join(lines_desc) if lines_desc else "خدمات أخرى"
            
            # Bride & Groom names
            groom_bride = []
            if b.customer.bride_name:
                groom_bride.append(f"العروسة: {b.customer.bride_name}")
            if b.customer.groom_name:
                groom_bride.append(f"العريس: {b.customer.groom_name}")
            groom_bride_summary = "<br/>".join(groom_bride) if groom_bride else "غير مسجل"
            
            # Phones
            phones = []
            if b.customer.phone:
                phones.append(b.customer.phone)
            if b.customer.phone_2:
                phones.append(b.customer.phone_2)
            phones_summary = "<br/>".join(phones) if phones else "-"
            
            table_html += f"""
                <tr>
                    <td><b>{b.booking_number}</b></td>
                    <td>{b.customer.full_name}</td>
                    <td>{groom_bride_summary}</td>
                    <td>{phones_summary}</td>
                    <td>{lines_summary}</td>
                    <td>{float(booking_total_amount(b)):,.2f}</td>
                    <td>{float(booking_paid_total(b)):,.2f}</td>
                    <td>{float(booking_remaining_amount(b)):,.2f}</td>
                    <td>{b.notes or '-'}</td>
                </tr>"""
        
        table_html += "</tbody></table>"
        return table_html

    next_days_html = format_bookings_day_table(next_day_1, bookings_day1)
    next_days_html += format_bookings_day_table(next_day_2, bookings_day2)

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

        <!-- ملخصات الشهر والسنة (MTD & YTD Summary) -->
        <div class="section-title">ملخص مبيعات وتحصيلات الشهر والسنة</div>
        <table>
            <thead>
                <tr>
                    <th>الفترة</th>
                    <th>إجمالي الحجوزات (المبيعات)</th>
                    <th>إجمالي التحصيلات (المقبوضات)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>منذ بداية الشهر (MTD)</b></td>
                    <td><b>{float(mtd_bookings_total):,.2f} {company.default_currency}</b></td>
                    <td><b>{float(mtd_collections_total):,.2f} {company.default_currency}</b></td>
                </tr>
                <tr>
                    <td><b>منذ بداية السنة (YTD)</b></td>
                    <td><b>{float(ytd_bookings_total):,.2f} {company.default_currency}</b></td>
                    <td><b>{float(ytd_collections_total):,.2f} {company.default_currency}</b></td>
                </tr>
            </tbody>
        </table>

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

    # Next Two Days Appointments Section
    html += '<div class="section-title">حجوزات ومواعيد اليومين التاليين</div>'
    html += next_days_html

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

