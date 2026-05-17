from __future__ import annotations

from app.core.enums import RoleKey

DEFAULT_PERMISSIONS = {
    # System & Security
    "audit.view": "عرض سجل التدقيق وتاريخ العمليات",
    "destructive.manage": "تنفيذ إجراءات الحذف النهائي المحمية",
    "period_lock.manage": "ضبط وتحرير أقفال الفترة المالية",
    "users.manage": "إدارة جميع المستخدمين والأدوار",
    "users.self_manage": "إدارة الملف الشخصي الخاص",
    "settings.manage": "إدارة الإعدادات والنسخ الاحتياطي",
    "security.manage": "إدارة إعدادات الأمان والتحقق الثنائي وتجميد الحسابات",
    
    # Financial & Ops
    "finance.view": "عرض مؤشرات لوحة القيادة المالية",
    "finance.reconcile_cash": "تسوية النقدية والعهد المالية",
    "reports.view": "عرض التقارير التشغيلية الواسعة",
    "exports.view": "تحميل وفتح الصادرات",
    "exports.manage": "إدارة جداول التصدير المحفوظة",
    "accounting.view": "عرض بيانات التأسيس المحاسبية",
    "accounting.manage": "إنشاء وترحيل وعكس قيود اليومية",
    
    # Core Data
    "customers.view": "عرض قائمة وتفاصيل العملاء",
    "customers.manage": "إنشاء وتحديث العملاء",
    "catalog.view": "عرض كتالوج الأقسام والخدمات",
    "catalog.manage": "إنشاء وتحديث الأقسام والخدمات",
    "dresses.view": "عرض موارد الفساتين",
    "dresses.manage": "إنشاء وتحديث موارد الفساتين",
    "branches.manage": "إدارة الفروع وصلاحياتها",
    
    # Atelier Module
    "atelier.view_reservations": "عرض حجوزات الأتيليه",
    "atelier.manage_reservations": "إدارة حجوزات الأتيليه (إنشاء/تعديل)",
    "atelier.view_fittings": "عرض مواعيد البروفة",
    "atelier.manage_fittings": "إدارة مواعيد البروفة",
    "atelier.view_deliveries": "عرض مواعيد التسليم",
    "atelier.manage_deliveries": "إدارة عمليات التسليم",
    "atelier.view_maintenance": "عرض سجلات صيانة الفساتين",
    "atelier.manage_maintenance": "إدارة صيانة الفساتين",

    # Salon Module
    "salon.view_appointments": "عرض مواعيد الصالون",
    "salon.manage_appointments": "إدارة مواعيد الصالون",
    "salon.view_services": "عرض خدمات التجميل",
    "salon.manage_services": "إدارة خدمات التجميل",

    # CRM Module
    "crm.view_leads": "عرض العملاء المحتملين",
    "crm.manage_leads": "إدارة العملاء المحتملين",
    "crm.view_marketing": "عرض حملات التسويق",
    "crm.manage_marketing": "إدارة حملات التسويق",

    # Inventory Module
    "inventory.view_stock": "عرض المخزون",
    "inventory.manage_stock": "إدارة المخزون (إضافة/تعديل)",
    "inventory.view_suppliers": "عرض الموردين",
    "inventory.manage_suppliers": "إدارة الموردين",
    "inventory.adjust_stock": "إجراء تسويات مخزنية",

    # Transactions
    "bookings.view": "عرض الحجوزات العامة",
    "bookings.manage": "إدارة الحجوزات العامة",
    "payments.view": "عرض المدفوعات",
    "payments.manage": "إنشاء وتحديث المدفوعات",
    "payments.void": "إلغاء مستندات الدفع",
    "custody.view": "عرض قضايا العهدة",
    "custody.manage": "إدارة تدفقات عمل العهدة",
}

ROLE_PERMISSION_MAP = {
    RoleKey.ADMIN.value: list(DEFAULT_PERMISSIONS.keys()),
    RoleKey.USER.value: [
        "users.self_manage",
        "customers.view",
        "customers.manage",
        "catalog.view",
        "dresses.view",
        "bookings.view",
        "bookings.manage",
        "payments.view",
        "payments.manage",
        "accounting.view",
        "atelier.view_reservations",
        "atelier.view_fittings",
        "salon.view_appointments",
    ],
}
