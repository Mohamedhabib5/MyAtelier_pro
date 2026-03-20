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
