from __future__ import annotations

from pydantic import BaseModel


class SummaryMetric(BaseModel):
    key: str
    count: int


class ValueMetric(BaseModel):
    key: str
    value: float


class DepartmentCountMetric(BaseModel):
    label: str
    count: int


class UpcomingBookingItem(BaseModel):
    booking_number: str
    customer_name: str
    service_name: str
    service_date: str
    status: str


class ReportsOverviewResponse(BaseModel):
    active_customers: int
    active_services: int
    available_dresses: int
    upcoming_bookings: int
    booking_status_counts: list[SummaryMetric]
    payment_type_totals: list[ValueMetric]
    dress_status_counts: list[SummaryMetric]
    department_service_counts: list[DepartmentCountMetric]
    upcoming_booking_items: list[UpcomingBookingItem]


# ---------------------------------------------------------------------------
# Comprehensive report schemas (new — not related to overview above)
# ---------------------------------------------------------------------------

class DailyIncomeItem(BaseModel):
    date: str
    amount: float


class TopClientItem(BaseModel):
    customer_name: str
    total_paid: float
    booking_count: int


class ChartItem(BaseModel):
    label: str
    value: float


class CountItem(BaseModel):
    label: str
    count: int


class ComprehensiveReportResponse(BaseModel):
    date_from: str
    date_to: str
    total_collected: float
    total_recognized: float
    total_remaining: float
    total_bookings: int
    cancelled_bookings: int
    cancellation_rate: float
    daily_income: list[DailyIncomeItem]
    department_income: list[ChartItem]
    top_services: list[CountItem]
    top_clients: list[TopClientItem]
    booking_status_counts: list[SummaryMetric]


class DetailedReportRowResponse(BaseModel):
    booking_id: str
    booking_line_id: str
    booking_number: str
    external_code: str | None
    booking_date: str
    customer_name: str
    customer_phone: str | None
    customer_phone_2: str | None
    department_name: str
    service_name: str
    dress_code: str | None
    dress_name: str | None
    service_date: str
    line_price: float
    paid_amount: float
    remaining_amount: float
    payment_method: str | None
    payment_reference: str | None
    payment_type: str | None
    booking_status: str
    line_status: str
    custody_status: str | None
    notes: str | None
    created_by: str | None
