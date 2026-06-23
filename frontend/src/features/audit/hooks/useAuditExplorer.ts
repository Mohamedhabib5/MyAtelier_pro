import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listAuditEvents, listDestructiveActions, listNightlyOpsEvents, verifyAuditIntegrity, type IntegrityVerifyResponse, buildNightlyOpsCsvUrl } from '../api';
import { useAuditText } from '../../../text/audit';
import { useLanguage } from '../../language/LanguageProvider';

import { useDateRangeFilter } from '../../../components/inputs/useDateRangeFilter';

export type AuditFilterMode = 'all' | 'destructive' | 'nightly_ops';

export function useAuditExplorer() {
  const auditText = useAuditText();
  const { language } = useLanguage();
  const [search, setSearch] = useState('');
  const [actorUserId, setActorUserId] = useState('');
  const [action, setAction] = useState('');
  const [targetType, setTargetType] = useState('');
  const [targetId, setTargetId] = useState('');
  const [branchId, setBranchId] = useState('');

  const {
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
  } = useDateRangeFilter('all');

  const [mode, setMode] = useState<AuditFilterMode>('all');
  const [filtersVersion, setFiltersVersion] = useState(0);
  const [verifying, setVerifying] = useState(false);
  const [integrityResult, setIntegrityResult] = useState<IntegrityVerifyResponse | null>(null);
  const [showIntegrityDialog, setShowIntegrityDialog] = useState(false);

  const auditQuery = useQuery({
    queryKey: ['audit', 'events', filtersVersion, search, actorUserId, action, targetType, targetId, branchId, dateFrom, dateTo],
    queryFn: () => {
      const query = {
        search: search || undefined,
        actorUserId: actorUserId || undefined,
        action: action || undefined,
        targetType: targetType || undefined,
        targetId: targetId || undefined,
        branchId: branchId || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
      };
      if (mode === 'destructive') {
        return listDestructiveActions(query);
      }
      if (mode === 'nightly_ops') {
        return listNightlyOpsEvents(query);
      }
      return listAuditEvents(query);
    },
  });

  const labels =
    language === 'ar'
      ? {
          search: 'بحث',
          searchPlaceholder: 'بحث داخل نتائج السجل',
          filters: 'الفلاتر',
          columns: 'الأعمدة',
          export: 'تصدير',
          reset: 'إعادة الضبط',
          noRows: auditText.page.noRows,
          rowsPerPage: 'عدد الصفوف',
          close: 'إغلاق',
        }
      : {
          search: 'Search',
          searchPlaceholder: 'Search in audit rows',
          filters: 'Filters',
          columns: 'Columns',
          export: 'Export',
          reset: 'Reset',
          noRows: auditText.page.noRows,
          rowsPerPage: 'Rows per page',
          close: 'Close',
        };



  function exportNightlyOpsCsv() {
    const exportReason = window.prompt(auditText.page.exportReasonPrompt, '')?.trim() ?? '';
    const url = buildNightlyOpsCsvUrl({
      search: search || undefined,
      actorUserId: actorUserId || undefined,
      targetType: targetType || undefined,
      targetId: targetId || undefined,
      branchId: branchId || undefined,
      dateFrom: dateFrom || undefined,
      dateTo: dateTo || undefined,
    }, 1000, exportReason || undefined);
    window.location.assign(url);
  }

  async function handleVerifyIntegrity() {
    setVerifying(true);
    try {
      const result = await verifyAuditIntegrity();
      setIntegrityResult(result);
      setShowIntegrityDialog(true);
    } catch (err: unknown) {
      alert(`فشل التحقق: ${(err as any).message}`);
    } finally {
      setVerifying(false);
    }
  }

  const activeFilterPairs: string[] = [
    search ? `search=${search}` : '',
    actorUserId ? `actor_user_id=${actorUserId}` : '',
    targetType ? `target_type=${targetType}` : '',
    targetId ? `target_id=${targetId}` : '',
    branchId ? `branch_id=${branchId}` : '',
    dateFrom ? `date_from=${dateFrom}` : '',
    dateTo ? `date_to=${dateTo}` : '',
  ].filter(Boolean);

  return {
    search, setSearch,
    actorUserId, setActorUserId,
    action, setAction,
    targetType, setTargetType,
    targetId, setTargetId,
    branchId, setBranchId,
    dateFrom,
    dateTo,
    activePreset,
    customFrom,
    customTo,
    selectPreset,
    setCustomFrom,
    setCustomTo,
    mode, setMode,
    filtersVersion, setFiltersVersion,
    verifying,
    integrityResult,
    showIntegrityDialog, setShowIntegrityDialog,
    auditQuery,
    labels,
    exportNightlyOpsCsv,
    handleVerifyIntegrity,
    activeFilterPairs,
    auditText,
    language,
  };
}
