import { useEffect, useState } from "react";
import { AlertCircle, ArrowLeft, CheckCircle2, Clock3, Code2, DatabaseZap, LoaderCircle, MessageSquare, Search, Table2, XCircle } from "lucide-react";
import { apiRequest } from "../services/api";
import { SQLViewer } from "../components/SQLViewer";
import { ResultTable } from "../components/ResultTable";

type Conversation = { id: string; database_id: string; title: string; state: string; created_at: string; updated_at: string };
type Message = { role: string; content: string; created_at: string };
type QueryExecution = {
  id: string;
  natural_language_query: string;
  generated_sql: string | null;
  status: string;
  error: string | null;
  execution_time_ms: number | null;
  row_count: number | null;
  result_analysis: { visualization?: { type: string; x?: string; y?: string }; summary?: string } | null;
  repair_attempts: number;
  repaired_sql: string | null;
  created_at: string;
};
type ConversationDetail = {
  id: string;
  database_id: string;
  title: string;
  state: string;
  messages: Message[];
  query_executions: QueryExecution[];
  intent: Record<string, unknown> | null;
};

export function ConversationsPage() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setListLoading(true);
    apiRequest<Conversation[]>("/conversations")
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setListLoading(false));
  }, []);

  const openConversation = async (conversation: Conversation) => {
    setLoading(true);
    try {
      const detail = await apiRequest<ConversationDetail>(`/conversations/${conversation.id}`);
      setSelected(detail);
    } catch {
      setSelected(null);
    } finally {
      setLoading(false);
    }
  };

  const filtered = items.filter((item) =>
    item.title.toLowerCase().includes(search.toLowerCase())
  );

  const stateLabel = (state: string) => state.replace(/_/g, " ");

  const stateIcon = (state: string) => {
    if (state === "completed") return <CheckCircle2 size={13} className="state-icon completed" />;
    if (state === "failed") return <XCircle size={13} className="state-icon failed" />;
    return <Clock3 size={13} className="state-icon pending" />;
  };

  return (
    <div className="conversations-layout">
      {/* ─── Sidebar list ─── */}
      <aside className="conversations-sidebar">
        <div className="conv-sidebar-header">
          <div className="eyebrow"><MessageSquare size={14} /> CONVERSATIONS</div>
          <h2>History</h2>
        </div>

        <div className="conv-search-wrap">
          <Search size={14} />
          <input
            placeholder="Search conversations…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="conv-list">
          {listLoading ? (
            <div className="conv-list-empty"><LoaderCircle className="spin" size={18} /> Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="conv-list-empty">
              {search ? "No matches found." : "No conversations yet."}
            </div>
          ) : (
            filtered.map((item) => (
              <button
                key={item.id}
                className={`conv-item ${selected?.id === item.id ? "active" : ""}`}
                onClick={() => openConversation(item)}
              >
                <MessageSquare size={15} className="conv-item-icon" />
                <div className="conv-item-body">
                  <span className="conv-item-title">{item.title}</span>
                  <span className="conv-item-meta">
                    {stateIcon(item.state)}
                    {stateLabel(item.state)} · {new Date(item.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* ─── Detail panel ─── */}
      <section className="conversation-detail">
        {loading ? (
          <div className="conv-detail-empty"><LoaderCircle className="spin" size={22} /> Loading conversation…</div>
        ) : !selected ? (
          <div className="conv-detail-empty">
            <MessageSquare size={32} className="conv-detail-placeholder-icon" />
            <h3>Select a conversation</h3>
            <p>Choose a conversation from the list to view its full query history, generated SQL, and results.</p>
          </div>
        ) : (
          <>
            <div className="conv-detail-header">
              <button className="conv-back-btn" onClick={() => setSelected(null)}>
                <ArrowLeft size={16} />
              </button>
              <div>
                <h2>{selected.title}</h2>
                <span className="conv-detail-meta">
                  {stateIcon(selected.state)}
                  {stateLabel(selected.state)}
                  {selected.query_executions.length > 0 && (
                    <> · {selected.query_executions.length} {selected.query_executions.length === 1 ? "query" : "queries"}</>
                  )}
                </span>
              </div>
            </div>

            <div className="conv-thread">
              {/* Messages thread */}
              {selected.messages.map((msg, i) => (
                <div key={i} className={`conv-message conv-message-${msg.role}`}>
                  <div className="conv-message-avatar">
                    {msg.role === "user" ? "U" : "Q"}
                  </div>
                  <div className="conv-message-body">
                    <span className="conv-message-role">
                      {msg.role === "user" ? "You" : "QueryMind"}
                      {msg.created_at && <time> · {new Date(msg.created_at).toLocaleTimeString()}</time>}
                    </span>
                    <p>{msg.content}</p>
                  </div>
                </div>
              ))}

              {/* Query Executions */}
              {selected.query_executions.map((execution) => (
                <div key={execution.id} className="conv-execution">
                  <div className="conv-execution-header">
                    <DatabaseZap size={16} />
                    <span className="conv-execution-title">Query Execution</span>
                    <span className={`conv-execution-status status-${execution.status}`}>
                      {execution.status === "completed" ? <CheckCircle2 size={12} /> : execution.status === "failed" || execution.status === "rejected" ? <XCircle size={12} /> : <Clock3 size={12} />}
                      {execution.status}
                    </span>
                  </div>

                  {/* Natural language query */}
                  <div className="conv-execution-query">
                    <Search size={13} />
                    <span>{execution.natural_language_query}</span>
                  </div>

                  {/* Generated SQL */}
                  {execution.generated_sql && (
                    <div className="conv-execution-sql">
                      <SQLViewer sql={execution.generated_sql} />
                    </div>
                  )}

                  {/* Repaired SQL notice */}
                  {execution.repaired_sql && (
                    <div className="conv-execution-repair">
                      <AlertCircle size={13} />
                      SQL was auto-repaired ({execution.repair_attempts} {execution.repair_attempts === 1 ? "attempt" : "attempts"})
                    </div>
                  )}

                  {/* Execution stats */}
                  {execution.status === "completed" && (
                    <div className="conv-execution-stats">
                      {execution.execution_time_ms != null && (
                        <span className="conv-stat"><Clock3 size={12} /> {execution.execution_time_ms} ms</span>
                      )}
                      {execution.row_count != null && (
                        <span className="conv-stat"><Table2 size={12} /> {execution.row_count} rows</span>
                      )}
                      {execution.result_analysis?.summary && (
                        <span className="conv-stat-summary">{execution.result_analysis.summary}</span>
                      )}
                    </div>
                  )}

                  {/* Error */}
                  {execution.error && (execution.status === "failed" || execution.status === "rejected") && (
                    <div className="conv-execution-error">
                      <XCircle size={13} />
                      <span>{execution.error}</span>
                    </div>
                  )}
                </div>
              ))}

              {selected.messages.length === 0 && selected.query_executions.length === 0 && (
                <div className="conv-detail-empty" style={{ padding: "48px 0" }}>
                  <Code2 size={24} />
                  <p>This conversation has no recorded activity.</p>
                </div>
              )}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
