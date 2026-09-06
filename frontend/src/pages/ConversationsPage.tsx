import { useEffect, useState } from "react";
import { Clock3, MessageSquare } from "lucide-react";
import { apiRequest } from "../services/api";

type Conversation = { id: string; database_id: string; title: string; state: string; created_at: string; updated_at: string };

export function ConversationsPage() {
  const [items, setItems] = useState<Conversation[]>([]);
  useEffect(() => { apiRequest<Conversation[]>("/conversations").then(setItems).catch(() => setItems([])); }, []);
  return <div className="placeholder-page history-page"><div className="eyebrow"><MessageSquare size={15} /> WORKSPACE HISTORY</div><h1>Conversations</h1><p>Return to a saved question and its resolved intent whenever you need it.</p><div className="history-list">{items.length ? items.map((item) => <article key={item.id}><MessageSquare size={17} /><div><h3>{item.title}</h3><span>{item.state.replace(/_/g, " ")} · <Clock3 size={12} /> {new Date(item.updated_at).toLocaleString()}</span></div></article>) : <div className="details-empty">No conversations yet.</div>}</div></div>;
}
