APP_ERROR = 'حدث خطأ في التطبيق'
AUTHENTICATION_REQUIRED = 'يجب تسجيل الدخول'
ACTIVE_ACCOUNT_REQUIRED = 'يتطلب هذا الإجراء حسابًا نشطًا'
ADMIN_ACCESS_REQUIRED = 'يتطلب هذا الإجراء صلاحية المدير'
AUTHORIZATION_REQUIRED = 'لا تملك صلاحية تنفيذ هذا الإجراء'
NOT_FOUND = 'لم يتم العثور على السجل المطلوب'
VALIDATION_FAILED = 'تعذر التحقق من صحة البيانات'


def missing_permission_message(permission_key: str) -> str:
  return f'الصلاحية المطلوبة غير متاحة: {permission_key}'

