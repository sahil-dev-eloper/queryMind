import { FormEvent, useEffect, useState } from "react";
import { ArrowUpRight, Database, MessageSquare, Send, Sparkles } from "lucide-react";
import { ResultTable } from "../components/ResultTable";
import { SQLViewer } from "../components/SQLViewer";
import { ClarificationCard } from "../components/ClarificationCard";
import { ResultVisualization } from "../components/ResultVisualization";
import { apiRequest } from "../services/api";
import { useNavigate } from "react-router-dom";

type DatabaseConnection = { id: string; name: string; host: string; port: number; connection_status: string };
type Clarification = { id: string; question: string; options: { label: string; value: string }[] };
type QueryResponse = { status: string; conversation_id?: string; clarification?: Clarification; rejection_reason?: string; analysis?: { intent?: string; is_ambiguous: boolean; ambiguities?: { field: string; reason: string }[] }; sql?: string; explanation?: string; result_analysis?: { visualization: { type: string; x?: string; y?: string }; summary: string }; repair_attempts?: number; results?: { columns: string[]; rows: unknown[][]; row_count: number; execution_time_ms: number } };

export function Dashboard() {
  const navigate = useNavigate();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]); const [databaseId, setDatabaseId] = useState(""); const [query, setQuery] = useState(""); const [result, setResult] = useState<QueryResponse | null>(null); const [conversationId, setConversationId] = useState(""); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  useEffect(() => { apiRequest<DatabaseConnection[]>("/databases").then((items) => { setDatabases(items.filter((item) => item.connection_status === "connected")); if (items[0]) setDatabaseId(items[0].id); }).catch(() => setError("Unable to load connected databases.")); }, []);
  const submit = async (event: FormEvent) => { event.preventDefault(); if (!databaseId || !query.trim()) return; setLoading(true); setError(""); setResult(null); setConversationId(""); try { const response = await apiRequest<QueryResponse>(`/databases/${databaseId}/query`, { method: "POST", body: JSON.stringify({ query }) }); if (response.status === "rejected") { setError(response.rejection_reason || "This question doesn't appear to be related to your database. Please ask a data-related question."); setResult(null); } else { setResult(response); if (response.conversation_id) setConversationId(response.conversation_id); } } catch { setError("The query could not be completed safely."); } finally { setLoading(false); } };
  const answerClarification = async (answer: string) => { if (!result?.conversation_id || !result.clarification) return; setLoading(true); setError(""); try { const response = await apiRequest<QueryResponse>(`/conversations/${result.conversation_id}/clarification`, { method: "POST", body: JSON.stringify({ clarification_id: result.clarification.id, answer }) }); setResult(response); setConversationId(response.conversation_id ?? result.conversation_id); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "That answer could not be applied."); } finally { setLoading(false); } };
  return (
    <div className="dashboard-page">
      <div className="eyebrow"><Sparkles size={15} /> WORKSPACE OVERVIEW</div>
      <h1>Ask better questions<br /><em>of your data.</em></h1>
      <p className="lede">QueryMind turns natural language into a clearer path through your analytics.</p>
      <button className="primary-action" onClick={() => navigate("/databases")}><Database size={18} /> Connect Database <ArrowUpRight size={17} /></button>
      <section className="query-workspace"><div className="query-heading"><div><div className="eyebrow"><Sparkles size={14} /> ASK YOUR DATA</div><h2>What would you like to know?</h2></div><select value={databaseId} onChange={(event) => setDatabaseId(event.target.value)} disabled={!databases.length}><option value="">Select database</option>{databases.map((database) => <option key={database.id} value={database.id}>{database.name}</option>)}</select></div><form className="query-form" onSubmit={submit}><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Show the top 10 customers by revenue this year" /><button className="primary-action compact" disabled={loading || !databaseId || !query.trim()}>{loading ? "Running..." : <><Send size={16} /> Ask</>}</button></form>{error && <div className="query-error">{error}</div>}{loading && <ResultTable loading />}{result?.status === "clarification_required" && result.clarification && <ClarificationCard question={result.clarification.question} options={result.clarification.options} loading={loading} onAnswer={answerClarification} />}{result?.status === "completed" && result.sql && <><div className="query-success">Query generated and executed · {result.results?.execution_time_ms} ms · {result.results?.row_count} rows</div><SQLViewer sql={result.sql} /><ResultVisualization columns={result.results?.columns ?? []} rows={result.results?.rows ?? []} analysis={result.result_analysis} /><ResultTable columns={result.results?.columns} rows={result.results?.rows} /></>}</section>
      <section className="dashboard-grid">
        <div className="panel conversations-panel"><div className="panel-heading"><span><MessageSquare size={18} /> Recent Conversations</span><span className="muted">0 total</span></div><div className="empty-state">Your recent questions will appear here.</div></div>
        <div className="quick-start"><div className="number">01</div><h2>Quick Start</h2><p>Ask questions about your data using natural language. Your workspace is ready when you are.</p></div>
      </section>
    </div>
  );
}
