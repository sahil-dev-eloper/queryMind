import { useState } from "react";
import { Check, ChevronDown, ChevronRight, Copy } from "lucide-react";

export function SQLViewer({ sql }: { sql: string }) {
  const [open, setOpen] = useState(true); const [copied, setCopied] = useState(false);
  const copy = async () => { await navigator.clipboard.writeText(sql); setCopied(true); window.setTimeout(() => setCopied(false), 1600); };
  return <section className="sql-viewer"><div className="result-heading"><button className="icon-button" onClick={() => setOpen(!open)}>{open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}</button><span>Generated SQL</span><button className="copy-button" onClick={copy}>{copied ? <Check size={14} /> : <Copy size={14} />}{copied ? "Copied" : "Copy"}</button></div>{open && <pre><code>{sql}</code></pre>}</section>;
}
