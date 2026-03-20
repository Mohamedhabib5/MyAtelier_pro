export function userIsAdmin(roleNames: string[]): boolean {
  return roleNames.includes('admin');
}
