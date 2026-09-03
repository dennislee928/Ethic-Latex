import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8787";

interface Profile {
  id: string;
  name: string;
  riskThreshold: number;
  protectedTopics: string[];
  autoApproveTools: string[];
}

interface Decision {
  id: number;
  toolName: string;
  actionText: string;
  riskScore: number;
  ethicalValue: number;
  erhSatisfied: boolean | null;
  estimatedExponent: number | null;
  verdict: "auto_approved" | "human_approved" | "blocked";
  createdAt: number | string;
}

const VERDICT_LABEL: Record<Decision["verdict"], string> = {
  auto_approved: "auto-approved",
  human_approved: "human approved",
  blocked: "blocked",
};

function riskClass(score: number, threshold: number): string {
  if (score > threshold) return "risk high";
  if (score > threshold * 0.6) return "risk mid";
  return "risk low";
}

export default function App() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [rows, setRows] = useState<Decision[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const [p, d] = await Promise.all([
          fetch(`${API}/api/profile`).then((r) => r.json()),
          fetch(`${API}/api/decisions?limit=50`).then((r) => r.json()),
        ]);
        if (!alive) return;
        setProfile(p);
        setRows(Array.isArray(d) ? d : []);
        setError(null);
      } catch {
        if (alive) setError(`Cannot reach the guardian worker at ${API}`);
      }
    }
    load();
    const t = setInterval(load, 5000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const threshold = profile?.riskThreshold ?? 40;
  const blocked = rows.filter((r) => r.verdict === "blocked").length;

  return (
    <main>
      <header>
        <h1>ERH Guardian</h1>
        <p className="sub">
          Transparency panel — every consequential agent action, scored before it ran.
        </p>
      </header>

      {error && <div className="banner">{error}</div>}

      <section className="cards">
        <div className="card">
          <h2>Value profile</h2>
          {profile ? (
            <>
              <div className="stat">
                <span className="big">{threshold}</span>
                <span>/100 risk threshold</span>
              </div>
              <p className="muted">Protected topics</p>
              <ul>
                {profile.protectedTopics.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ul>
            </>
          ) : (
            <p className="muted">No profile stored yet.</p>
          )}
        </div>
        <div className="card">
          <h2>Session</h2>
          <div className="stat">
            <span className="big">{rows.length}</span>
            <span>gate decisions</span>
          </div>
          <div className="stat">
            <span className="big">{blocked}</span>
            <span>blocked pending human review</span>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Decision audit log</h2>
        {rows.length === 0 ? (
          <p className="muted">No decisions logged yet — run the agent.</p>
        ) : (
          <div className="tablewrap">
            <table>
              <thead>
                <tr>
                  <th>Tool</th>
                  <th>Action</th>
                  <th>Risk</th>
                  <th>ERH</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td className="mono">{r.toolName}</td>
                    <td className="action">{r.actionText}</td>
                    <td>
                      <div className={riskClass(r.riskScore, threshold)}>
                        <div
                          className="bar"
                          style={{ width: `${Math.min(100, r.riskScore)}%` }}
                        />
                        <span>{Math.round(r.riskScore)}</span>
                      </div>
                    </td>
                    <td>
                      {r.erhSatisfied == null
                        ? "—"
                        : r.erhSatisfied
                          ? `pass (α=${r.estimatedExponent?.toFixed(2) ?? "?"})`
                          : `FAIL (α=${r.estimatedExponent?.toFixed(2) ?? "?"})`}
                    </td>
                    <td>
                      <span className={`chip ${r.verdict}`}>{VERDICT_LABEL[r.verdict]}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
