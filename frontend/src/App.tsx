import { NavLink, Route, Routes } from "react-router-dom";
import { BarChart3, Database, LayoutDashboard, MessageSquare } from "lucide-react";
import { Dashboard } from "./pages/Dashboard";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { DatabasePage } from "./pages/DatabasePage";
import { ConversationsPage } from "./pages/ConversationsPage";

export default function App() {
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><span className="brand-mark">Q</span><span>QueryMind</span></div><nav><NavLink to="/"><LayoutDashboard size={17} /> Dashboard</NavLink><NavLink to="/databases"><Database size={17} /> Databases</NavLink><NavLink to="/conversations"><MessageSquare size={17} /> Conversations</NavLink></nav><div className="sidebar-footer"><BarChart3 size={17} /><span>Analytics workspace</span></div></aside><main><header><span className="status-dot" /> Analytics workspace <span className="header-rule" /></header><Routes><Route path="/" element={<Dashboard />} /><Route path="/databases" element={<DatabasePage />} /><Route path="/conversations" element={<ConversationsPage />} /></Routes></main></div>;
}
