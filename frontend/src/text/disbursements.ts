import { useLocalizedText } from './useText';

const disbursementsText = {
  ar: {
    page: {
      title: 'سندات الصرف',
      subtitle: 'تسجيل وإدارة عمليات الصرف النقدي والبنكي للموردين والموظفين والمصاريف التشغيلية ورد العربون.',
      addDisbursement: 'إضافة سند صرف جديد',
      edit: 'تعديل سند',
      void: 'إبطال',
      delete: 'حذف نهائي',
      voidedState: 'ملغى (Voided)',
      searchLabel: 'ابحث برقم السند أو اسم المستلم أو الملاحظات',
      searchHint: 'اكتب حرفين على الأقل للبحث',
      loading: 'جاري تحميل سندات الصرف...',
      noResults: 'لم يتم العثور على أي سند صرف مطابق.',
      payeeType: 'نوع المستلم',
      amount: 'المبلغ',
      date: 'التاريخ',
      safe: 'الخزنة / طريقة الصرف',
      notes: 'الملاحظات',
      status: 'الحالة',
      journal: 'القيد المحاسبي',
      actions: 'الإجراءات',
      confirmDelete: 'هل أنت متأكد من حذف السند {number} نهائياً؟ سيتم عكس أو حذف القيود المحاسبية التلقائية المرتبطة به أيضاً.',
      types: {
        customer: 'رد عربون لعميلة',
        supplier: 'دفع لمورد',
        employee: 'سلفة / عهدة موظف',
        expense: 'مصروف تشغيلي',
      }
    },
    editor: {
      createTitle: 'سند صرف جديد',
      editTitle: 'تعديل سند الصرف {number}',
      save: 'حفظ السند',
      cancel: 'إلغاء',
      amount: 'مبلغ الصرف',
      payeeType: 'نوع الصرف المستهدف',
      payeeName: 'اسم المستلم (المورد/الموظف/العميل)',
      expenseAccount: 'حساب المصروف التشغيلي',
      paymentMethod: 'الخزنة / الحساب الصادر منه المبلغ',
      date: 'تاريخ الصرف',
      notes: 'ملاحظات وتفاصيل السند',
      required: 'هذا الحقل مطلوب',
      amountError: 'يجب أن يكون المبلغ أكبر من صفر',
      editNotice: 'تنبيه: أنت تقوم الآن بتعديل سند صرف تم ترحيله محاسبياً. سيقوم النظام بعكس القيد القديم وتوليد قيد جديد تلقائياً عند حفظ التعديلات.',
    },
    voidDialog: {
      title: 'إبطال سند صرف',
      confirm: 'تأكيد الإبطال المحاسبي',
      reason: 'سبب الإلغاء / الإبطال',
      date: 'تاريخ الإبطال',
    }
  },
  en: {
    page: {
      title: 'Payment Vouchers',
      subtitle: 'Record and manage outgoing cash and bank transactions for suppliers, employee advances, expenses, and customer refunds.',
      addDisbursement: 'Add Disbursement',
      edit: 'Edit',
      void: 'Void',
      delete: 'Delete',
      voidedState: 'Voided',
      searchLabel: 'Search by voucher number, payee, or notes',
      searchHint: 'Type at least 2 characters to search',
      loading: 'Loading disbursements...',
      noResults: 'No disbursements found.',
      payeeType: 'Payee Type',
      amount: 'Amount',
      date: 'Date',
      safe: 'Paid Through (Safe/Bank)',
      notes: 'Notes',
      status: 'Status',
      journal: 'Journal Entry',
      actions: 'Actions',
      confirmDelete: 'Are you sure you want to permanently delete voucher {number}? Its linked journal entry will also be deleted/reversed.',
      types: {
        customer: 'Customer Refund',
        supplier: 'Vendor Payment',
        employee: 'Employee Custody',
        expense: 'Direct Expense',
      }
    },
    editor: {
      createTitle: 'Create Disbursement Voucher',
      editTitle: 'Edit Disbursement Voucher {number}',
      save: 'Save Voucher',
      cancel: 'Cancel',
      amount: 'Amount',
      payeeType: 'Payee Type',
      payeeName: 'Payee Name (Supplier/Employee/Customer)',
      expenseAccount: 'Expense Account (CoA)',
      paymentMethod: 'Paid Through (Safe/Bank)',
      date: 'Voucher Date',
      notes: 'Voucher Notes & Description',
      required: 'Required field',
      amountError: 'Amount must be greater than zero',
      editNotice: 'Warning: You are editing an already posted disbursement. The previous journal entry will be automatically reversed and a new one generated on save.',
    },
    voidDialog: {
      title: 'Void Disbursement Voucher',
      confirm: 'Confirm Void',
      reason: 'Void Reason',
      date: 'Void Date',
    }
  }
} as const;

export function useDisbursementsText() {
  return useLocalizedText(disbursementsText);
}
