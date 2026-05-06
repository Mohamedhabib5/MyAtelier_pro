APP_ERROR = 'حدث خطأ في التطبيق'
AUTHENTICATION_REQUIRED = 'يجب تسجيل الدخول'
ACTIVE_ACCOUNT_REQUIRED = 'يتطلب هذا الإجراء حسابًا نشطًا'
ADMIN_ACCESS_REQUIRED = 'يتطلب هذا الإجراء صلاحية المدير'
AUTHORIZATION_REQUIRED = 'لا تملك صلاحية تنفيذ هذا الإجراء'
NOT_FOUND = 'لم يتم العثور على السجل المطلوب'
VALIDATION_FAILED = 'تعذر التحقق من صحة البيانات'


def missing_permission_message(permission_key: str) -> str:
    return f'الصلاحية المطلوبة غير متاحة: {permission_key}'


# Booking & Lifecycle Messages
BOOKING_NOT_FOUND = 'لم يتم العثور على وثيقة الحجز'
BOOKING_LINE_NOT_FOUND = 'لم يتم العثور على سطر الحجز'
BOOKING_CANCELLED_NO_EDIT = 'لا يمكن تعديل وثيقة حجز ملغاة'
BOOKING_LINE_CANCELLED_NO_COMPLETE = 'لا يمكن إكمال السطور الملغاة'
BOOKING_DELETE_PAID_ERROR = 'لا يمكن حذف الحجز لوجود مبالغ مدفوعة. يجب حذف سندات القبض أولاً'
BOOKING_DELETE_RECOGNIZED_ERROR = 'لا يمكن حذف الحجز لوجود قيود إيرادات معترف بها'
BOOKING_LINE_RECOGNIZED_DELETE_ERROR = 'لا يمكن حذف السطور المكتملة بعد الاعتراف بالإيراد'
BOOKING_LINE_PAID_DELETE_ERROR = 'لا يمكن حذف السطور التي لها مدفوعات محصلة'

# Payment & Financial Messages
PAYMENT_NOT_FOUND = 'لم يتم العثور على سند الدفع'
PAYMENT_VOIDED_NO_EDIT = 'لا يمكن تعديل سندات الدفع المبطلة'
PAYMENT_READ_ONLY_TYPE = 'هذا النوع من السندات للقراءة فقط في هذه المرحلة'
PAYMENT_DELETE_PAID_RESTRICTION = 'لا يمكن حذف السند لوجود مبالغ مدفوعة مرتبطة به'
PAYMENT_REFUND_EXCEEDS_PAID = 'مجموع الرد والتحويل يتجاوز إجمالي المقبوض'
PAYMENT_METHOD_REQUIRED = 'طريقة الدفع مطلوبة'

