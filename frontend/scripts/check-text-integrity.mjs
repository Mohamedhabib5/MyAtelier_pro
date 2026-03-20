import { readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const targets = [path.join(root, 'src'), path.join(root, '..', 'backend', 'app')];
const extensions = new Set(['.ts', '.tsx', '.py', '.md']);
const brokenPatterns = [
  { label: 'lost-question-marks', matcher: (text) => text.includes('???') },
  { label: 'replacement-character', matcher: (text) => text.includes('\uFFFD') },
  { label: 'encoded-dash', matcher: (text) => text.includes('â€”') },
  { label: 'encoded-bullet', matcher: (text) => text.includes('â€¢') },
  { label: 'encoded-quotes', matcher: (text) => text.includes('â€œ') || text.includes('â€') },
  { label: 'mojibake-pattern', matcher: (text) => ((text.match(/(?:ط·.{0,1}ط¸|ط¸.{0,1}ط·)/gu) ?? []).length >= 3) },
  { label: 'english-date-message', matcher: (text) => text.includes('Date is required') || text.includes('Invalid date value') },
  {
    label: 'hardcoded-rtl-document',
    matcher: (text) =>
      text.includes("document.documentElement.dir = 'rtl'") ||
      text.includes('document.documentElement.dir = "rtl"') ||
      text.includes("document.body.dir = 'rtl'") ||
      text.includes('document.body.dir = "rtl"'),
  },
];

async function walk(dir) {
  try {
    const info = await stat(dir);
    if (!info.isDirectory()) {
      return [];
    }
  } catch {
    return [];
  }

  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const nextPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walk(nextPath)));
      continue;
    }
    if (extensions.has(path.extname(entry.name))) {
      files.push(nextPath);
    }
  }
  return files;
}

const findings = [];
for (const dir of targets) {
  const files = await walk(dir);
  for (const file of files) {
    const text = await readFile(file, 'utf8');
    for (const pattern of brokenPatterns) {
      if (pattern.matcher(text)) {
        findings.push(`${pattern.label}: ${path.relative(root, file)}`);
      }
    }
  }
}

if (findings.length) {
  console.error(`Found corrupted or banned text markers:\n${findings.join('\n')}`);
  process.exit(1);
}

console.log('Text integrity check passed.');
