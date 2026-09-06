import { LoaderCircle } from "lucide-react";

type Props = { columns?: string[]; rows?: unknown[][]; loading?: boolean; error?: string };

export function ResultTable({ columns = [], rows = [], loading, error }: Props) {
  if (loading) return <div className="result-empty"><LoaderCircle className="spin" size={20} /> Running query...</div>;
  if (error) return <div className="result-empty error-text">{error}</div>;
  if (!columns.length) return <div className="result-empty">No rows returned.</div>;
  return <div className="result-table-wrap"><table><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{row.map((value, valueIndex) => <td key={valueIndex}>{value === null ? "NULL" : String(value)}</td>)}</tr>)}</tbody></table></div>;
}
