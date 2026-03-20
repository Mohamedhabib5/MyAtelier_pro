import { useLocalizedText } from './useText';

const accountingText = {
  ar: {
    page: {
      description: 'عرض قراءة فقط لشجرة الحسابات والقيود اليومية وميزان المراجعة.',
      title: 'المحاسبة',
    },
    chart: {
      account: 'الحساب',
      code: 'الكود',
      subtitle: 'الحسابات الأساسية المجهزة حاليًا للنظام.',
      title: 'شجرة الحسابات',
      type: 'النوع',
    },
    journals: {
      credit: 'دائن',
      date: 'التاريخ',
      debit: 'مدين',
      number: 'رقم القيد',
      reference: 'المرجع',
      status: 'الحالة',
      subtitle: 'عرض سريع للقيود الحالية وحالتها المحاسبية.',
      title: 'القيود اليومية',
    },
    trialBalance: {
      account: 'الحساب',
      accountType: 'النوع',
      asOfDate: 'حتى تاريخ',
      balanceCredit: 'رصيد دائن',
      balanceDebit: 'رصيد مدين',
      code: 'الكود',
      includeZero: 'إظهار الحسابات الصفرية',
      movementCredit: 'حركة دائن',
      movementDebit: 'حركة مدين',
      subtitle: 'يعتمد فقط على القيود المرحلة والقيود المعكوسة ضمن النطاق المحدد.',
      summary: {
        balanceCredit: 'إجمالي الأرصدة الدائنة',
        balanceDebit: 'إجمالي الأرصدة المدينة',
        entries: 'القيود المحتسبة',
        movementCredit: 'إجمالي الحركة الدائنة',
        movementDebit: 'إجمالي الحركة المدينة',
      },
      title: 'ميزان المراجعة',
    },
  },
  en: {
    page: {
      description: 'A read-only view of the chart of accounts, journal entries, and trial balance.',
      title: 'Accounting',
    },
    chart: {
      account: 'Account',
      code: 'Code',
      subtitle: 'Core system accounts currently seeded.',
      title: 'Chart of accounts',
      type: 'Type',
    },
    journals: {
      credit: 'Credit',
      date: 'Date',
      debit: 'Debit',
      number: 'Entry #',
      reference: 'Reference',
      status: 'Status',
      subtitle: 'A quick view of current journal entries and their accounting status.',
      title: 'Journal entries',
    },
    trialBalance: {
      account: 'Account',
      accountType: 'Type',
      asOfDate: 'As of date',
      balanceCredit: 'Credit balance',
      balanceDebit: 'Debit balance',
      code: 'Code',
      includeZero: 'Include zero accounts',
      movementCredit: 'Credit movement',
      movementDebit: 'Debit movement',
      subtitle: 'Based only on posted and reversed entries within the selected scope.',
      summary: {
        balanceCredit: 'Total credit balances',
        balanceDebit: 'Total debit balances',
        entries: 'Included entries',
        movementCredit: 'Total credit movement',
        movementDebit: 'Total debit movement',
      },
      title: 'Trial balance',
    },
  },
} as const;

export function useAccountingText() {
  return useLocalizedText(accountingText);
}
