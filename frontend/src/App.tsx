import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import { BarChart3, Database, LayoutDashboard, LogOut, MessageSquare } from "lucide-react";
import { Dashboard } from "./pages/Dashboard";
import { DatabasePage } from "./pages/DatabasePage";
import { ConversationsPage } from "./pages/ConversationsPage";
import { AuthPage } from "./pages/AuthPage";
import { useAuth } from "./contexts/AuthContext";

function ProtectedLayout() {
  const { user, logout } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">Q</span>
          <span>QueryMind</span>
        </div>
        <nav>
          <NavLink to="/"><LayoutDashboard size={17} /> Dashboard</NavLink>
          <NavLink to="/databases"><Database size={17} /> Databases</NavLink>
          <NavLink to="/conversations"><MessageSquare size={17} /> Conversations</NavLink>
        </nav>
        <div className="sidebar-user">
          <div className="sidebar-user-info">
            <div className="sidebar-user-avatar">{user.name.charAt(0).toUpperCase()}</div>
            <div>
              <div className="sidebar-user-name">{user.name}</div>
              <div className="sidebar-user-email">{user.email}</div>
            </div>
          </div>
          <button className="sidebar-logout" onClick={logout}>
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </aside>
      <main>
        <header>
          <span className="status-dot" /> Analytics workspace <span className="header-rule" />
        </header>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/databases" element={<DatabasePage />} />
          <Route path="/conversations" element={<ConversationsPage />} />
        </Routes>
      </main>
    </div>
  );
}

function AuthGuard() {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (user) return <Navigate to="/" replace />;
  return <AuthPage />;
}

export default function App() {
  const { loading } = useAuth();

  if (loading) return null;

  return (
    <Routes>
      <Route path="/login" element={<AuthGuard />} />
      <Route path="/*" element={<ProtectedLayout />} />
    </Routes>
  );
}
