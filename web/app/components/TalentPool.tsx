"use client";

import { useEffect, useState } from "react";
import { FileText, LoaderCircle, Search, Trash2, UserRound } from "lucide-react";
import { deleteTalent, getTalent, openResume } from "../lib/api";
import type { TalentCandidate } from "../lib/types";

export function TalentPool({ apiKey }: { apiKey: string }) {
  const [items, setItems] = useState<TalentCandidate[]>([]); const [total, setTotal] = useState(0); const [search, setSearch] = useState(""); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = async (term = search) => { setLoading(true); setError(""); try { const result = await getTalent(term, apiKey); setItems(result.results); setTotal(result.total); } catch (cause) { setError(cause instanceof Error ? cause.message : "Could not load talent."); } finally { setLoading(false); } };
  useEffect(() => { getTalent("", apiKey).then((result) => { setItems(result.results); setTotal(result.total); }).catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "Could not load talent.")).finally(() => setLoading(false)); }, [apiKey]);
  const remove = async (item: TalentCandidate) => { if (!window.confirm(`Remove ${item.filename} from the talent pool?`)) return; await deleteTalent(item.resume_id, apiKey); await load(); };
  return <section className="content-view"><div className="view-heading"><div><span className="eyebrow">Talent database</span><h1>Talent pool</h1><p>Review every indexed profile and manage candidate availability.</p></div><div className="metric-pill"><strong>{total}</strong><span>profiles</span></div></div>
    <form onSubmit={(e) => { e.preventDefault(); void load(); }} className="toolbar"><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search candidates by file name…" /><button className="button-secondary">Search</button></form>
    {error && <p className="error-banner">{error}</p>}{loading ? <div className="empty-state"><LoaderCircle className="animate-spin" /> Loading talent pool…</div> : items.length === 0 ? <div className="empty-state"><UserRound /> No candidates found.</div> : <div className="table-shell"><div className="table-row table-head"><span>Candidate</span><span>Profile coverage</span><span>Resume ID</span><span /></div>{items.map((item) => <div className="table-row" key={item.resume_id}><div className="flex min-w-0 items-center gap-3"><span className="avatar"><UserRound size={17} /></span><div className="min-w-0"><p className="truncate font-semibold">{item.filename}</p><p className="text-xs text-slate-400">Indexed candidate</p></div></div><div className="flex flex-wrap gap-1">{item.sections.map((section) => <span key={section} className="tag">{section}</span>)}</div><code className="truncate text-xs text-slate-400">{item.resume_id.slice(0, 12)}…</code><div className="flex justify-end gap-1"><button onClick={() => void openResume(item.resume_url, apiKey)} className="icon-button" aria-label="View resume"><FileText size={16} /></button><button onClick={() => void remove(item)} className="icon-button danger" aria-label="Remove candidate"><Trash2 size={16} /></button></div></div>)}</div>}
  </section>;
}
