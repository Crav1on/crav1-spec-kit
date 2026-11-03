// 1.110.0: parse every ```mermaid block in kit templates and goldens with mermaid 11.4.1.
// Usage: node scripts/mermaid/check-mermaid.mjs <file> ...   Exit 1 on any parse error.
import { JSDOM } from 'jsdom';
import fs from 'fs';
const dom = new JSDOM('<body></body>');
globalThis.window = dom.window; globalThis.document = dom.window.document;
const { default: mermaid } = await import('mermaid');
mermaid.initialize({ startOnLoad: false });
let bad = 0, n = 0;
for (const f of process.argv.slice(2)) {
  const src = fs.readFileSync(f, 'utf8');
  for (const m of src.matchAll(/^```mermaid[ \t]*\n([\s\S]*?)^```[ \t]*$/gm)) {
    n++;
    const line = src.slice(0, m.index).split('\n').length;
    try { await mermaid.parse(m[1]); }
    catch (e) { bad++; console.log(`${f}:${line}: ${String(e.message || e).split('\n').slice(0, 3).join(' | ')}`); }
  }
}
console.log(`mermaid 11.4.1: ${n} blocks, ${bad} failed`);
process.exit(bad ? 1 : 0);
