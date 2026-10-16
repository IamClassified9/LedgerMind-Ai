import type { ReactNode } from "react";

export default function StatCard({label, value, note, icon}: {label: string; value: string; note: string; icon: ReactNode}) {
  return <article className="stat-card">
    <div className="stat-top"><span className="stat-label">{label}</span><span className="stat-icon">{icon}</span></div>
    <strong className="stat-value">{value}</strong>
    <span className="stat-note">{note}</span>
  </article>;
}
