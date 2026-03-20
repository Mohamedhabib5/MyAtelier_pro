import type { DepartmentRecord } from '../catalog/api';

const DRESS_CODE_PREFIXES = ['DR', 'DRESS', 'DRESSES'];

export function departmentUsesDressCode(department?: Pick<DepartmentRecord, 'code'> | null) {
  if (!department) {
    return false;
  }

  const code = department.code.trim().toUpperCase();
  return DRESS_CODE_PREFIXES.some((prefix) => code === prefix || code.startsWith(`${prefix}-`));
}

