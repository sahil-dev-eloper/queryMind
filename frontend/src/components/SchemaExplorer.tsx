import { useState } from "react";
import { ChevronDown, ChevronRight, Columns3, GitBranch, KeyRound, Table2 } from "lucide-react";

type Column = { name: string; type: string; nullable: boolean; primary_key: boolean; foreign_key?: string | null };
type Table = { name: string; type: string; description?: string | null; columns: Column[] };
type Schema = { name: string; tables: Table[] };
type Props = { schemas: Schema[]; selectedTable: Table | null; onSelectTable: (table: Table) => void };

export function SchemaExplorer({ schemas, selectedTable, onSelectTable }: Props) {
  const [openSchemas, setOpenSchemas] = useState<Record<string, boolean>>({});
  const [openTables, setOpenTables] = useState<Record<string, boolean>>({});
   return <div className="schema-layout"><div className="schema-tree"><div className="tree-label">SCHEMAS</div>{schemas.map((schema) => { const schemaOpen = openSchemas[schema.name] ?? true; return <div key={schema.name}><button className="tree-row schema-row" onClick={() => setOpenSchemas({ ...openSchemas, [schema.name]: !schemaOpen })}>{schemaOpen ? <ChevronDown size={15} /> : <ChevronRight size={15} />}<span>{schema.name}</span><small>{schema.tables.length}</small></button>{schemaOpen && schema.tables.map((table) => { const tableOpen = openTables[table.name] ?? false; return <div key={table.name}><button className={`tree-row table-row ${selectedTable?.name === table.name ? "selected" : ""}`} onClick={() => { onSelectTable(table); setOpenTables({ ...openTables, [table.name]: !tableOpen }); }}><Table2 size={15} />{table.name}<span className="tree-spacer" />{tableOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}</button>{tableOpen && <div className="column-list">{table.columns.map((column) => <div className="column-row" key={column.name}>{column.primary_key ? <KeyRound size={13} /> : column.foreign_key ? <GitBranch size={13} /> : <Columns3 size={13} />}<span>{column.name}</span><small>{column.foreign_key ?? column.type}</small></div>)}</div>}</div>})}</div>})}</div><TableDetails table={selectedTable} /></div>;
}

function TableDetails({ table }: { table: Table | null }) {
  if (!table) return <div className="details-empty">Select a table to inspect its columns and relationships.</div>;
  const primaryKeys = table.columns.filter((column) => column.primary_key);
  const foreignKeys = table.columns.filter((column) => column.foreign_key);
  return <div className="table-details"><div className="detail-heading"><Table2 size={20} /><div><h3>{table.name}</h3><span>{table.type}</span></div></div><h4>Columns</h4><div className="column-table"><div className="column-head"><span>Column</span><span>Type</span><span>Nullable</span></div>{table.columns.map((column) => <div className="column-line" key={column.name}><strong>{column.primary_key && <KeyRound size={13} />}{column.name}</strong><span>{column.type}</span><span>{column.nullable ? "Yes" : "No"}</span></div>)}</div><div className="key-summary"><div><b>Primary key</b><span>{primaryKeys.map((column) => column.name).join(", ") || "None"}</span></div><div><b>Foreign keys</b><span>{foreignKeys.map((column) => `${column.name} -> ${column.foreign_key}`).join(", ") || "None"}</span></div></div></div>;
}
