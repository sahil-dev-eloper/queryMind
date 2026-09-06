import { BarChart3, LineChart as LineIcon } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Analysis = { visualization: { type: string; x?: string; y?: string }; summary: string };
type Props = { columns: string[]; rows: unknown[][]; analysis?: Analysis };

export function ResultVisualization({ columns, rows, analysis }: Props) {
  const recommendation = analysis?.visualization;
  if (!recommendation || recommendation.type === "TABLE" || !recommendation.x || !recommendation.y) return null;
  if (!columns.includes(recommendation.x) || !columns.includes(recommendation.y)) return null;
  const xIndex = columns.indexOf(recommendation.x);
  const yIndex = columns.indexOf(recommendation.y);
  const data = rows.map((row) => ({ [recommendation.x!]: row[xIndex], [recommendation.y!]: Number(row[yIndex]) })).filter((row) => Number.isFinite(row[recommendation.y!]));
  if (!data.length) return null;
  const chart = recommendation.type === "LINE" ? <LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#e1e9dc" /><XAxis dataKey={recommendation.x} stroke="#809087" fontSize={11} /><YAxis stroke="#809087" fontSize={11} /><Tooltip /><Line type="monotone" dataKey={recommendation.y} stroke="#71994a" strokeWidth={2} dot={{ r: 3 }} /></LineChart> : <BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#e1e9dc" /><XAxis dataKey={recommendation.x} stroke="#809087" fontSize={11} /><YAxis stroke="#809087" fontSize={11} /><Tooltip /><Bar dataKey={recommendation.y} fill="#98ba61" radius={[3, 3, 0, 0]} /></BarChart>;
  return <section className="visualization-panel"><div className="result-heading light"><span>{recommendation.type === "LINE" ? <LineIcon size={16} /> : <BarChart3 size={16} />} Visualization</span><small>{analysis?.summary}</small></div><div className="chart-container"><ResponsiveContainer width="100%" height={270}>{chart}</ResponsiveContainer></div></section>;
}
