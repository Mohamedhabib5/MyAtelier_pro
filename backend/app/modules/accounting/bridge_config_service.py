from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.modules.accounting.models import ChartOfAccount, AccountingBridgeConfig
from app.modules.accounting.repository import AccountingRepository

BRIDGE_KEYS = {
    "cash": ("1111001", "الصندوق الرئيسي", "Main Cash Account"),
    "customer_advances": ("2110", "عربون العملاء", "Customer Advances"),
    "customer_receivables": ("1121001", "ذمم العملاء التشغيلي", "Customer Receivables"),
    "supplier_payables": ("2121001", "ذمم الموردين التشغيلي", "Supplier Payables"),
    "service_revenue": ("4110", "إيرادات الخدمات", "Service Revenue"),
    "tax_payable": ("2200", "ضريبة المخرجات", "Output Tax/VAT"),
}


def ensure_accounting_bridge_configs(db: Session, company_id: str) -> None:
    """
    تتأكد من وجود كافة إعدادات الجسور المحاسبية الستة الأساسية للشركة.
    تُزرع القيم الافتراضية إذا لم تكن موجودة.
    """
    existing = db.query(AccountingBridgeConfig).filter(
        AccountingBridgeConfig.company_id == company_id
    ).all()
    existing_keys = {cfg.bridge_key for cfg in existing}

    created_any = False
    for key, (default_code, label_ar, label_en) in BRIDGE_KEYS.items():
        if key not in existing_keys:
            cfg = AccountingBridgeConfig(
                company_id=company_id,
                bridge_key=key,
                account_code=default_code,
                label_ar=label_ar,
                label_en=label_en,
                is_required=True,
            )
            db.add(cfg)
            created_any = True

    if created_any:
        db.flush()


def resolve_bridge_account(db: Session, company_id: str, bridge_key: str) -> ChartOfAccount:
    """
    تبحث عن كود الحساب المرتبط بمفتاح الجسر في جدول الإعدادات،
    ثم تتحقق من وجود الحساب وصلاحيته للترحيل.
    تحتوي على آلية Fallback آمنة للقيم القديمة مع تسجيل تحذير عند عدم وجود السجل.
    """
    # 1. البحث في جدول الإعدادات
    config = db.query(AccountingBridgeConfig).filter(
        AccountingBridgeConfig.company_id == company_id,
        AccountingBridgeConfig.bridge_key == bridge_key
    ).first()

    # 2. آلية Fallback مؤقتة
    if config is None:
        if bridge_key in BRIDGE_KEYS:
            default_code, label_ar, label_en = BRIDGE_KEYS[bridge_key]
            logging.warning(
                f"⚠️ [Fallback Warning] Missing bridge config for key '{bridge_key}'. "
                f"Using hardcoded default '{default_code}'."
            )
            code = default_code
            label = label_ar
        else:
            raise ValidationAppError(
                f"⚠️ الإعداد المحاسبي غير مكتمل: لم يتم تعيين حساب للجسر '{bridge_key}'."
            )
    else:
        code = config.account_code
        label = config.label_ar

    # 3. جلب الحساب والتحقق من صلاحيته
    repo = AccountingRepository(db)
    account = repo.get_chart_account_by_code(company_id, code)

    if account is None:
        raise ValidationAppError(
            f"⚠️ حساب الترحيل {code} ({label}) غير موجود في شجرة الحسابات. يرجى تحديث الإعدادات المحاسبية."
        )
    if not account.is_active:
        raise ValidationAppError(
            f"⚠️ حساب الترحيل {code} ({label}) معطل حالياً. يرجى تفعيله أو اختيار حساب بديل."
        )
    if not account.allows_posting:
        raise ValidationAppError(
            f"⚠️ حساب الترحيل {code} ({label}) حساب تجميعي ولا يقبل الترحيل المباشر."
        )

    return account


def list_bridge_configs(db: Session, company_id: str) -> list[dict]:
    """
    تستعرض جميع إعدادات الجسور للشركة الحالية مع دمج أسماء الحسابات المقابلة.
    """
    ensure_accounting_bridge_configs(db, company_id)
    configs = db.query(AccountingBridgeConfig).filter_by(company_id=company_id).all()
    repo = AccountingRepository(db)

    results = []
    for cfg in configs:
        account = repo.get_chart_account_by_code(company_id, cfg.account_code)
        results.append({
            "bridge_key": cfg.bridge_key,
            "account_code": cfg.account_code,
            "label_ar": cfg.label_ar,
            "label_en": cfg.label_en,
            "is_required": cfg.is_required,
            "account_name": account.name if account else None
        })
    return results


def update_bridge_config(
    db: Session,
    company_id: str,
    bridge_key: str,
    payload: AccountingBridgeConfigUpdateRequest,
    actor: User
) -> dict:
    """
    تحديث إعدادات جسر معين مع تفعيل الضوابط والتحقق من صلاحية الحساب ونشاطه وقابليته للترحيل.
    تسجيل كل عملية تغيير في سجلات التدقيق record_audit.
    """
    ensure_accounting_bridge_configs(db, company_id)
    config = db.query(AccountingBridgeConfig).filter_by(
        company_id=company_id,
        bridge_key=bridge_key
    ).first()

    if not config:
        raise ValidationAppError("لم يتم العثور على إعداد الجسر المطلوب")

    # Guardrails: التحقق من الحساب الجديد في شجرة الحسابات
    repo = AccountingRepository(db)
    account = repo.get_chart_account_by_code(company_id, payload.account_code)

    if account is None:
        raise ValidationAppError(
            f"⚠️ الحساب {payload.account_code} غير موجود في شجرة الحسابات."
        )
    if not account.is_active:
        raise ValidationAppError(
            f"⚠️ الحساب {payload.account_code} معطل حالياً. يرجى تفعيله أولاً."
        )
    if not account.allows_posting:
        raise ValidationAppError(
            f"⚠️ الحساب {payload.account_code} حساب تجميعي ولا يقبل الترحيل المباشر."
        )

    old_code = config.account_code

    # تحديث الحقول
    config.account_code = payload.account_code
    if payload.label_ar is not None:
        config.label_ar = payload.label_ar
    if payload.label_en is not None:
        config.label_en = payload.label_en

    db.flush()

    from app.modules.core_platform.service import record_audit
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.bridge_config_updated",
        target_type="accounting_bridge_config",
        target_id=config.id,
        summary=f"Updated accounting bridge '{bridge_key}' from {old_code} to {payload.account_code}",
        diff={
            "bridge_key": bridge_key,
            "old_value": old_code,
            "new_value": payload.account_code,
            "label_ar": config.label_ar,
        }
    )
    db.commit()

    return {
        "bridge_key": config.bridge_key,
        "account_code": config.account_code,
        "label_ar": config.label_ar,
        "label_en": config.label_en,
        "is_required": config.is_required,
        "account_name": account.name
    }


def reset_bridge_config(
    db: Session,
    company_id: str,
    bridge_key: str,
    actor: User
) -> dict:
    """
    إعادة تعيين الجسر المحدد إلى قيمته الافتراضية مع التحقق والتسجيل في سجل التدقيق.
    """
    if bridge_key not in BRIDGE_KEYS:
        raise ValidationAppError("مفتاح الجسر غير معروف لإعادة التعيين")

    ensure_accounting_bridge_configs(db, company_id)
    config = db.query(AccountingBridgeConfig).filter_by(
        company_id=company_id,
        bridge_key=bridge_key
    ).first()

    if not config:
        raise ValidationAppError("لم يتم العثور على إعداد الجسر المطلوب")

    default_code, label_ar, label_en = BRIDGE_KEYS[bridge_key]

    # Guardrails: التحقق من الحساب الافتراضي
    repo = AccountingRepository(db)
    account = repo.get_chart_account_by_code(company_id, default_code)

    if account is None:
        raise ValidationAppError(
            f"⚠️ الحساب الافتراضي {default_code} غير موجود في شجرة الحسابات."
        )
    if not account.is_active:
        raise ValidationAppError(
            f"⚠️ الحساب الافتراضي {default_code} معطل حالياً."
        )
    if not account.allows_posting:
        raise ValidationAppError(
            f"⚠️ الحساب الافتراضي {default_code} حساب تجميعي ولا يقبل الترحيل المباشر."
        )

    old_code = config.account_code

    config.account_code = default_code
    config.label_ar = label_ar
    config.label_en = label_en

    db.flush()

    from app.modules.core_platform.service import record_audit
    record_audit(
        db,
        actor_user_id=actor.id,
        action="accounting.bridge_config_reset",
        target_type="accounting_bridge_config",
        target_id=config.id,
        summary=f"Reset accounting bridge '{bridge_key}' to default {default_code}",
        diff={
            "bridge_key": bridge_key,
            "old_value": old_code,
            "new_value": default_code,
        }
    )
    db.commit()

    return {
        "bridge_key": config.bridge_key,
        "account_code": config.account_code,
        "label_ar": config.label_ar,
        "label_en": config.label_en,
        "is_required": config.is_required,
        "account_name": account.name
    }

