from __future__ import annotations

from pydantic import BaseModel


class MetricItem(BaseModel):
    label: str
    value: float


class CountMetricItem(BaseModel):
    label: str
    count: int


class FinanceDashboardResponse(BaseModel):
    total_income: float
    total_remaining: float
    total_bookings: int
    daily_income: list[MetricItem]
    department_income: list[MetricItem]
    top_services: list[CountMetricItem]
