"use client";

import { Clock3, Search, Trash2 } from "lucide-react";
import { clearRecentSearches, deleteRecentSearch } from "../lib/api";
import type { RecentSearch } from "../lib/types";

export function RecentSearches({ items, apiKey, onRefresh, onRun }: { items: RecentSearch[]; apiKey: string; onRefresh: () => Promise<void>; onRun: (query: string) => void }) {
  const remove = async (id: string) => { await deleteRecentSearch(id, apiKey); await onRefresh(); };
  const clear = async () => { if (!window.confirm("Clear all recent searches?")) return; await clearRecentSearches(apiKey); await onRefresh(); };
  return <section className="content-view"><div className="view-heading"><div><span className="eyebrow">Search memory</span><h1>Recent searches</h1><p>Return to previous briefs without rebuilding your search.</p></div>{items.length > 0 && <button onClick={() => void clear()} className="button-secondary"><Trash2 size={14} /> Clear history</button>}</div>
    {items.length === 0 ? <div className="empty-state"><Clock3 /><strong>No searches yet</strong><span>Your candidate searches will appear here automatically.</span></div> : <div className="space-y-3">{items.map((item) => <article key={item.id} className="history-card"><span className="grid size-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-500"><Search size={17} /></span><div className="min-w-0 flex-1"><p className="line-clamp-2 text-sm font-semibold leading-6">{item.query}</p><p className="mt-1 text-xs text-slate-400">{item.result_count} results · {new Date(item.created_at).toLocaleString()}</p></div><button onClick={() => onRun(item.query)} className="button-primary">Run again</button><button onClick={() => void remove(item.id)} className="icon-button danger"><Trash2 size={15} /></button></article>)}</div>}
  </section>;
}
