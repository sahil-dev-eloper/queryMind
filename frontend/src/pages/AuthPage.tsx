import { FormEvent, useState } from "react";
import { LogIn, Sparkles, UserPlus } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

export function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(email, name, password);
      } else {
        await login(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="brand-mark">Q</span>
          <span>QueryMind</span>
        </div>
        <h1>{mode === "login" ? "Welcome back" : "Create account"}</h1>
        <p className="auth-subtitle">
          {mode === "login"
            ? "Sign in to access your analytics workspace."
            : "Get started with your own analytics workspace."}
        </p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={submit}>
          <label>
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </label>

          {mode === "register" && (
            <label>
              Full Name
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                autoComplete="name"
              />
            </label>
          )}

          <label>
            Password
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={mode === "register" ? "Min 6 characters" : "Your password"}
              autoComplete={mode === "register" ? "new-password" : "current-password"}
            />
          </label>

          <button className="auth-submit" type="submit" disabled={loading}>
            {loading ? (
              "Please wait…"
            ) : mode === "login" ? (
              <><LogIn size={16} /> Sign In</>
            ) : (
              <><UserPlus size={16} /> Create Account</>
            )}
          </button>
        </form>

        <div className="auth-switch">
          {mode === "login" ? (
            <>Don't have an account? <button onClick={() => { setMode("register"); setError(""); }}>Sign up</button></>
          ) : (
            <>Already have an account? <button onClick={() => { setMode("login"); setError(""); }}>Sign in</button></>
          )}
        </div>

        <div className="auth-footer">
          <Sparkles size={13} /> Powered by AI analytics
        </div>
      </div>
    </div>
  );
}
