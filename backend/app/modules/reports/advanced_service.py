from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.reports.detailed_service import get_detailed_lines_report

PRICE_QUANT = Decimal('0.01')
ZERO = Decimal('0.00')

def get_advanced_bi_report(
    db: Session,
    branch_id: str | None,
    date_from: date,
    date_to: date,
) -> dict:
    """
    Advanced BI Report service that provides flat records and summary KPIs
    for interactive dashboards and advanced table grids.
    """
    # 1. Reuse the detailed lines report logic for the flat records
    print(f"DEBUG: get_advanced_bi_report CALLED for period {date_from} to {date_to}")
    records = get_detailed_lines_report(db, branch_id, date_from, date_to)
    print(f"DEBUG: get_advanced_bi_report GOT {len(records)} records")
    
    # 2. Calculate global summary KPIs for the period
    total_sales = ZERO
    total_paid = ZERO
    total_remaining = ZERO
    
    # We can also track department and branch performance here for the summary
    dept_performance = {}
    
    for rec in records:
        line_price = Decimal(str(rec['line_price']))
        paid_amount = Decimal(str(rec['paid_amount']))
        remaining_amount = Decimal(str(rec['remaining_amount']))
        
        total_sales += line_price
        total_paid += paid_amount
        total_remaining += remaining_amount
        
        # Aggregate by department for a quick overview
        dept_name = rec['department_name']
        if dept_name not in dept_performance:
            dept_performance[dept_name] = {"sales": ZERO, "count": 0}
        
        dept_performance[dept_name]["sales"] += line_price
        dept_performance[dept_name]["count"] += 1

    return {
        "summary": {
            "total_sales": float(total_sales.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)),
            "total_paid": float(total_paid.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)),
            "total_remaining": float(total_remaining.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)),
            "record_count": len(records),
            "department_breakdown": [
                {"label": dept, "sales": float(data["sales"].quantize(PRICE_QUANT)), "count": data["count"]}
                for dept, data in dept_performance.items()
            ]
        },
        "records": records
    }
