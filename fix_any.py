import os

files = [
  '/home/mohamed/MyAtelier_pro/frontend/src/features/accounting/api.ts',
  '/home/mohamed/MyAtelier_pro/frontend/src/features/accounting/AddAccountDialog.tsx',
  '/home/mohamed/MyAtelier_pro/frontend/src/features/accounting/JournalEntryDialog.tsx',
  '/home/mohamed/MyAtelier_pro/frontend/src/features/custody/api.ts',
  '/home/mohamed/MyAtelier_pro/frontend/src/features/custody/CustodyCompensationSection.tsx'
]

for file in files:
  if not os.path.exists(file): continue
  with open(file, 'r', encoding='utf-8') as f:
    content = f.read()
  
  if 'accounting/api.ts' in file:
    content = content.replace('export function createChartAccount(payload: any)', 'export function createChartAccount(payload: Record<string, any>)')
    content = content.replace('export function createJournalEntry(payload: any)', 'export function createJournalEntry(payload: Record<string, any>)')
    content = content.replace('export function updateJournalEntry(id: string, payload: any)', 'export function updateJournalEntry(id: string, payload: Record<string, any>)')
    content = content.replace('export function reverseJournalEntry(id: string, payload: any)', 'export function reverseJournalEntry(id: string, payload: Record<string, any>)')
    content = content.replace('export function updateChartAccount(id: string, payload: any)', 'export function updateChartAccount(id: string, payload: Record<string, any>)')
  
  if 'accounting/AddAccountDialog.tsx' in file:
    content = content.replace('mutationFn: (payload: any) =>', 'mutationFn: (payload: Record<string, any>) =>')
    content = content.replace('const payload: any =', 'const payload: Record<string, any> =')
    content = content.replace('onError: (err: any) =>', 'onError: (err: Error | any) =>')

  if 'accounting/JournalEntryDialog.tsx' in file:
    content = content.replace('onError: (err: any) =>', 'onError: (err: Error | any) =>')

  if 'custody/api.ts' in file:
    content = content.replace('Promise<any>', 'Promise<{ items: CustodyCaseRecord[]; total: number; page: number; size: number; pages: number }>')
    content = content.replace('apiRequest<any>', 'apiRequest<{ items: CustodyCaseRecord[]; total: number; page: number; size: number; pages: number }>')

  if 'custody/CustodyCompensationSection.tsx' in file:
    content = content.replace('(t: any)', '(t: { id: string; name: string })')
    content = content.replace('(item: any)', '(item: { id: string; name: string })')

  with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
