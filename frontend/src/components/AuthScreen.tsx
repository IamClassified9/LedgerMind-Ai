import { useState } from "react";
import { Activity, AlertCircle, ArrowRight, Eye, EyeOff, LoaderCircle, ShieldCheck } from "lucide-react";
import { api, setAuthToken, type UserProfile } from "../api/client";

type Props = { onAuthenticated: (user: UserProfile) => void };

export default function AuthScreen({ onAuthenticated }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const result = mode === "register"
        ? await api.register({ full_name: fullName.trim(), email: email.trim(), password })
        : await api.login({ email: email.trim(), password });
      setAuthToken(result.access_token);
      onAuthenticated(result.user);
    } catch (e) { setError(e instanceof Error ? e.message : "Authentication failed. Please try again."); }
    finally { setBusy(false); }
  }

  return <main className="auth-shell">
    <section className="auth-card">
      <div className="brand auth-brand"><div className="brand-mark"><Activity size={22}/></div><div><strong>LedgerMind<span> AI</span></strong><small>BUSINESS INTELLIGENCE</small></div></div>
      <div className="auth-eyebrow"><span className="eyebrow-dot"/> YOUR BUSINESS, IN FOCUS</div>
      <h1>{mode === "login" ? "Welcome back." : "Build with clarity."}</h1>
      <p className="auth-subtitle">{mode === "login" ? "Sign in to your secure business workspace." : "Create your account to start organizing your business records."}</p>
      <div className="auth-tabs"><button className={mode === "login" ? "selected" : ""} onClick={() => {setMode("login");setError("");}}>Sign in</button><button className={mode === "register" ? "selected" : ""} onClick={() => {setMode("register");setError("");}}>Create account</button></div>
      {error && <div className="alert error-alert"><AlertCircle size={17}/><span>{error}</span></div>}
      <form className="auth-form" onSubmit={submit}>
        {mode === "register" && <label>Full name<input autoComplete="name" required minLength={2} maxLength={120} value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Your name"/></label>}
        <label>Email address<input type="email" autoComplete="email" required maxLength={254} value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com"/></label>
        <label>Password<div className="password-input"><input type={showPassword ? "text" : "password"} autoComplete={mode === "register" ? "new-password" : "current-password"} required minLength={mode === "register" ? 10 : 1} maxLength={128} value={password} onChange={e => setPassword(e.target.value)} placeholder={mode === "register" ? "At least 10 characters" : "Your password"}/><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword(v => !v)}>{showPassword ? <EyeOff size={16}/> : <Eye size={16}/>}</button></div></label>
        {mode === "register" && <p className="auth-hint"><ShieldCheck size={15}/> Your password is securely hashed and never stored as plain text.</p>}
        <button className="primary-button auth-submit" type="submit" disabled={busy}>{busy ? <LoaderCircle size={17} className="spin"/> : <ArrowRight size={17}/>} {busy ? "Please wait…" : mode === "login" ? "Sign in securely" : "Create account"}</button>
      </form>
      <div className="auth-foot"><ShieldCheck size={15}/> Your business records are private to your authorized account.</div>
    </section>
    <aside className="auth-promo"><div className="graphic-glow"/><span className="eyebrow"><span className="eyebrow-dot"/> LEDGERMIND INTELLIGENCE</span><h2>Good records.<br/><em>Clearer decisions.</em></h2><p>Bring sales, expenses, stock and reports into one secure workspace — with evidence before assumptions.</p><div className="auth-feature"><ShieldCheck size={18}/><div><b>Private by design</b><span>Only authorized members can access a business workspace.</span></div></div><div className="auth-feature"><Activity size={18}/><div><b>Understand the numbers</b><span>Reporting and issue detection built around your saved records.</span></div></div><div className="auth-graphic-card"><div className="preview-top"><span>BUSINESS SNAPSHOT</span><span className="preview-dot"/></div><div className="preview-label">Sales revenue</div><div className="preview-number">₦ ———</div><div className="preview-chart">{Array.from({length:12},(_,i)=><span key={i}/>)}</div><div className="preview-line"><span/><span/><span/></div></div></aside>
  </main>;
}
