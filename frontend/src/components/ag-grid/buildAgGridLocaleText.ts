import type { LocaleText } from 'ag-grid-community';

export function buildAgGridLocaleText(language: 'ar' | 'en'): LocaleText {
  if (language === 'ar') {
    return {
      noRowsToShow: 'لا توجد بيانات',
      loadingOoo: 'جار التحميل...',
      page: 'صفحة',
      more: 'المزيد',
      to: 'إلى',
      of: 'من',
      next: 'التالي',
      last: 'الأخير',
      first: 'الأول',
      previous: 'السابق',
      selectAll: 'تحديد الكل',
      searchOoo: 'بحث...',
      blanks: 'فارغ',
      filterOoo: 'فلترة...',
      equals: 'يساوي',
      notEqual: 'لا يساوي',
      lessThan: 'أقل من',
      greaterThan: 'أكبر من',
      contains: 'يحتوي',
      notContains: 'لا يحتوي',
      startsWith: 'يبدأ بـ',
      endsWith: 'ينتهي بـ',
      andCondition: 'و',
      orCondition: 'أو',
      applyFilter: 'تطبيق',
      resetFilter: 'إعادة ضبط',
      clearFilter: 'مسح',
      cancelFilter: 'إلغاء',
      pinColumn: 'تثبيت العمود',
      pinLeft: 'تثبيت يسار',
      pinRight: 'تثبيت يمين',
      noPin: 'بدون تثبيت',
      autosizeThiscolumn: 'احتواء العمود',
      autosizeAllColumns: 'احتواء كل الأعمدة',
      resetColumns: 'إعادة ضبط الأعمدة',
      expandAll: 'توسيع الكل',
      collapseAll: 'طي الكل',
    };
  }

  return {
    noRowsToShow: 'No rows',
    loadingOoo: 'Loading...',
  };
}
