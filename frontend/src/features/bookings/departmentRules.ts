import type { DepartmentRecord } from '../catalog/api';

export function departmentUsesDressCode(department?: Pick<DepartmentRecord, 'code' | 'is_dress_department'> | null) {
  if (!department) {
    return false;
  }

  // Use explicit flag only (managed via operational settings)
  return department.is_dress_department === true;
}

