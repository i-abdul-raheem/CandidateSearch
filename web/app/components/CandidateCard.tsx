"use client";

import { ArrowUpRight, CheckCircle2, ChevronRight, FileText, LoaderCircle, Sparkles } from "lucide-react";
import type { Candidate, Explanation } from "../lib/types";
import { openResume } from "../lib/api";

function scoreTone(score: number) {
  if (score >= 0.78) return { label: "Strong match", text: "text-emerald-700", ring: "#16805c" };
  if (score >= 0.58) return { label: "Good match", text: "text-amber-700", ring: "#c5872c" };
  return { label: "Potential match", text: "text-slate-600", ring: "#64748b" };
}

export function CandidateCard({ candidate, index, explanation, explaining, onExplain, apiKey }: { candidate: Candidate; index: number; explanation?: Explanation; explaining: boolean; onExplain: () => void; apiKey: string }) {
  const percent = Math.round(candidate.score * 100); const tone = scoreTone(candidate.score);
  const evidence = candidate.evidence.find((item) => item.section === "experience") ?? candidate.evidence[0];
  return <article className="candidate-card"><div className="flex items-start gap-4"><div className="grid size-11 shrink-0 place-items-center rounded-xl bg-[#E8EEE9] text-sm font-semibold text-[#173F35]">{String(index + 1).padStart(2, "0")}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Candidate {candidate.resume_id.slice(0, 7)}</p><h3 className="mt-1 text-[17px] font-semibold tracking-tight">Relevant profile</h3></div><div className="flex items-center gap-2"><span className={`text-xs font-semibold ${tone.text}`}>{tone.label}</span><div className="grid size-12 place-items-center rounded-full text-xs font-bold" style={{ background: `conic-gradient(${tone.ring} ${percent}%, #e9ece9 0)`, padding: 3 }}><span className="grid size-full place-items-center rounded-full bg-white">{percent}</span></div></div></div>{evidence && <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-500">{evidence.text.replace(/^[A-Z ]+:/, "").trim()}</p>}<div className="mt-5 flex flex-wrap items-center gap-2"><button onClick={() => void openResume(candidate.id, apiKey)} className="button-secondary"><FileText size={14} /> View CV <ArrowUpRight size={13} /></button><button onClick={onExplain} disabled={explaining} className="button-ghost">{explaining ? <LoaderCircle size={14} className="animate-spin" /> : <Sparkles size={14} />} Explain match <ChevronRight size={14} /></button></div></div></div>
    {explanation && <div className="mt-5 rounded-2xl bg-[#F3F6F3] p-5"><div className="flex items-center justify-between gap-3"><p className="text-xs font-bold uppercase tracking-[0.13em] text-[#173F35]">AI match brief</p><span className="rounded-full bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-600">{explanation.verdict}</span></div><p className="mt-3 text-sm leading-6 text-slate-600">{explanation.summary}</p><div className="mt-4 grid gap-4 sm:grid-cols-2"><div><p className="text-xs font-semibold text-slate-800">Why they fit</p><ul className="mt-2 space-y-2">{explanation.strengths.slice(0, 3).map((item) => <li key={item} className="flex gap-2 text-xs leading-5 text-slate-500"><CheckCircle2 size={14} className="mt-0.5 shrink-0 text-emerald-600" />{item}</li>)}</ul></div><div><p className="text-xs font-semibold text-slate-800">Points to verify</p><ul className="mt-2 space-y-2">{explanation.gaps.map((item) => <li key={item} className="flex gap-2 text-xs leading-5 text-slate-500"><span className="mt-2 size-1 shrink-0 rounded-full bg-amber-500" />{item}</li>)}</ul></div></div></div>}
  </article>;
}
