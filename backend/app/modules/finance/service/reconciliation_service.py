from __future__ import annotations

from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.exceptions import ValidationAppError
from app.modules.core_platform.audit import record_audit
from app.modules.identity.models import User
from app.modules.organization.service import get_company_settings
from app.modules.payments.models import PaymentDocument, PaymentMethod
from app.modules.finance.models.reconciliation import CashReconciliation, ReconciliationItem


def list_reconciliations(db: Session, branch_id: str) -> list[CashReconciliation]:
    return (
        db.query(CashReconciliation)
        .filter(CashReconciliation.branch_id == branch_id)
        .order_by(CashReconciliation.end_date.desc(), CashReconciliation.created_at.desc())
        .all()
    )


def get_reconciliation(db: Session, reconciliation_id: str, branch_id: str) -> CashReconciliation:
    recon = db.query(CashReconciliation).filter(
        CashReconciliation.id == reconciliation_id,
        CashReconciliation.branch_id == branch_id
    ).first()
    if not recon:
        raise ValidationAppError("التسوية غير موجودة أو لا تنتمي لهذا الفرع")
    return recon


def get_pending_payments(
    db: Session, branch_id: str, payment_method_id: str, start_date: date, end_date: date
) -> list[PaymentDocument]:
    # Find payment documents that have been reconciled in this branch
    from sqlalchemy import select
    
    reconciled_ids = (
        select(ReconciliationItem.payment_document_id)
        .join(CashReconciliation)
        .filter(
            CashReconciliation.branch_id == branch_id,
            ReconciliationItem.is_reconciled == True
        )
    )

    payments = (
        db.query(PaymentDocument)
        .filter(
            PaymentDocument.branch_id == branch_id,
            PaymentDocument.payment_method_id == payment_method_id,
            PaymentDocument.payment_date >= start_date,
            PaymentDocument.payment_date <= end_date,
            PaymentDocument.status == "active",
            ~PaymentDocument.id.in_(reconciled_ids)
        )
        .order_by(PaymentDocument.payment_date.asc(), PaymentDocument.payment_number.asc())
        .all()
    )
    return payments


def get_latest_reconciliation_ids(db: Session, branch_id: str) -> set[str]:
    # Subquery to get max end_date grouped by payment method
    latest_sub = (
        db.query(
            CashReconciliation.payment_method_id,
            func.max(CashReconciliation.end_date).label("max_end")
        )
        .filter(CashReconciliation.branch_id == branch_id)
        .group_by(CashReconciliation.payment_method_id)
        .subquery()
    )
    
    # Query to fetch the IDs of reconciliations matching that max date
    latest_recons = (
        db.query(CashReconciliation.id)
        .join(
            latest_sub,
            (CashReconciliation.payment_method_id == latest_sub.c.payment_method_id) &
            (CashReconciliation.end_date == latest_sub.c.max_end)
        )
        .all()
    )
    return {r[0] for r in latest_recons}


def create_reconciliation(
    db: Session,
    actor: User,
    branch_id: str,
    payload: dict
) -> CashReconciliation:
    company = get_company_settings(db)
    
    # 1. Resolve payment method
    payment_method_id = payload.get("payment_method_id")
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id,
        PaymentMethod.company_id == company.id
    ).first()
    if not payment_method:
        raise ValidationAppError("طريقة الدفع المحددة غير صالحة")

    # 2. Parse date range
    start_date_str = payload.get("start_date")
    end_date_str = payload.get("end_date")
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except Exception:
        raise ValidationAppError("صيغة التاريخ غير صالحة")

    if start_date > end_date:
        raise ValidationAppError("تاريخ البدء لا يمكن أن يكون بعد تاريخ الانتهاء")

    # 3. Enforce sequential and non-overlapping constraint
    latest_recon = db.query(CashReconciliation).filter(
        CashReconciliation.payment_method_id == payment_method.id,
        CashReconciliation.branch_id == branch_id
    ).order_by(CashReconciliation.end_date.desc()).first()

    if latest_recon and latest_recon.end_date:
        if start_date <= latest_recon.end_date:
            raise ValidationAppError(f"التسوية الجديدة يجب أن تبدأ بعد انتهاء التسوية السابقة ({latest_recon.end_date})")

    # Double check all overlaps
    overlap = db.query(CashReconciliation).filter(
        CashReconciliation.payment_method_id == payment_method.id,
        CashReconciliation.branch_id == branch_id,
        CashReconciliation.start_date <= end_date,
        CashReconciliation.end_date >= start_date
    ).first()
    if overlap:
        raise ValidationAppError("تتقاطع هذه الفترة مع تسوية مسجلة بالفعل")

    # 4. Check for Cash and receiver_name
    is_cash = payment_method.code.lower() == "cash" or payment_method.name == "نقدي"
    receiver_name = payload.get("receiver_name")
    if is_cash:
        if not receiver_name or not receiver_name.strip():
            raise ValidationAppError("يجب تحديد اسم الشخص الذي استلم النقدية من الكاشير")
        receiver_name = receiver_name.strip()
    else:
        receiver_name = None

    # 5. Fetch pending payments specified
    item_payloads = payload.get("items", [])
    if not item_payloads:
        raise ValidationAppError("يجب اختيار دفعة واحدة على الأقل لإجراء التسوية")
        
    payment_ids = [item["payment_document_id"] for item in item_payloads]
    
    # Verify these payments actually exist, are active, belong to the branch/date/method
    pending_payments = get_pending_payments(db, branch_id, payment_method.id, start_date, end_date)
    pending_dict = {p.id: p for p in pending_payments}

    recon_items = []
    total_expected = Decimal("0.00")
    total_actual = Decimal("0.00")

    from app.modules.payments.serializers import document_total

    for item_pay in item_payloads:
        p_id = item_pay["payment_document_id"]
        if p_id not in pending_dict:
            raise ValidationAppError(f"المستند {p_id} غير متاح للتسوية")
        
        payment_doc = pending_dict[p_id]
        expected_amt = document_total(payment_doc)
        actual_amt = Decimal(str(item_pay.get("actual_amount", expected_amt)))
        
        total_expected += expected_amt
        total_actual += actual_amt

        recon_item = ReconciliationItem(
            payment_document_id=p_id,
            expected_amount=expected_amt,
            actual_amount=actual_amt,
            is_reconciled=True
        )
        recon_items.append(recon_item)

    difference = total_actual - total_expected

    # 6. Create CashReconciliation
    reconciliation = CashReconciliation(
        company_id=company.id,
        branch_id=branch_id,
        created_by_user_id=actor.id,
        updated_by_user_id=actor.id,
        reconciliation_date=end_date,
        start_date=start_date,
        end_date=end_date,
        payment_method_id=payment_method.id,
        receiver_name=receiver_name,
        total_expected_amount=total_expected,
        total_actual_amount=total_actual,
        difference_amount=difference,
        status="COMPLETED",
        notes=payload.get("notes"),
        items=recon_items
    )

    db.add(reconciliation)
    db.flush()

    record_audit(
        db,
        actor_user_id=actor.id,
        action="finance.reconcile_cash",
        target_type="cash_reconciliation",
        target_id=reconciliation.id,
        summary=f"Reconciled {payment_method.name} from {start_date} to {end_date}. Expected: {total_expected}, Actual: {total_actual}",
        diff={
            "start_date": str(start_date),
            "end_date": str(end_date),
            "payment_method_name": payment_method.name,
            "total_expected": float(total_expected),
            "total_actual": float(total_actual),
            "difference": float(difference),
            "receiver_name": receiver_name
        }
    )

    db.commit()
    return reconciliation


def delete_reconciliation(db: Session, user: User, reconciliation_id: str, branch_id: str) -> None:
    recon = get_reconciliation(db, reconciliation_id, branch_id)
    
    # Check if there is any newer reconciliation for the same method
    newer = db.query(CashReconciliation).filter(
        CashReconciliation.payment_method_id == recon.payment_method_id,
        CashReconciliation.branch_id == branch_id,
        CashReconciliation.end_date > recon.end_date,
        CashReconciliation.id != recon.id
    ).first()
    if newer:
        raise ValidationAppError("لا يمكن حذف هذه التسوية لأنها ليست التسوية الأحدث لهذه طريقة الدفع")
        
    db.delete(recon)
    db.flush()
    
    record_audit(
        db,
        actor_user_id=user.id,
        action="finance.reconcile_cash",
        target_type="cash_reconciliation",
        target_id=reconciliation_id,
        summary=f"Deleted cash reconciliation for {recon.payment_method.name} from {recon.start_date} to {recon.end_date}",
        diff={
            "id": reconciliation_id,
            "action": "deleted"
        }
    )
    db.commit()


def update_reconciliation(
    db: Session, user: User, reconciliation_id: str, branch_id: str, payload: dict
) -> CashReconciliation:
    recon = get_reconciliation(db, reconciliation_id, branch_id)
    
    # Check latest constraint
    newer = db.query(CashReconciliation).filter(
        CashReconciliation.payment_method_id == recon.payment_method_id,
        CashReconciliation.branch_id == branch_id,
        CashReconciliation.end_date > recon.end_date,
        CashReconciliation.id != recon.id
    ).first()
    if newer:
        raise ValidationAppError("لا يمكن تعديل هذه التسوية لأنها ليست التسوية الأحدث لهذه طريقة الدفع")
        
    is_cash = recon.payment_method.code.lower() == "cash" or recon.payment_method.name == "نقدي"
    
    if "receiver_name" in payload:
        receiver_name = payload["receiver_name"]
        if is_cash:
            if not receiver_name or not receiver_name.strip():
                raise ValidationAppError("يجب تحديد اسم الشخص الذي استلم النقدية من الكاشير")
            recon.receiver_name = receiver_name.strip()
        else:
            recon.receiver_name = None
            
    if "notes" in payload:
        recon.notes = payload["notes"]
        
    recon.updated_by_user_id = user.id
    db.flush()
    
    record_audit(
        db,
        actor_user_id=user.id,
        action="finance.reconcile_cash",
        target_type="cash_reconciliation",
        target_id=recon.id,
        summary=f"Updated cash reconciliation metadata for {recon.payment_method.name}",
        diff={
            "receiver_name": recon.receiver_name,
            "notes": recon.notes
        }
    )
    db.commit()
    return recon
