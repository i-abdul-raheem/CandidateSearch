"use client";

import { useRef, useState } from "react";
import { ArrowLeft, Check, FileText, LockKeyhole, UploadCloud, X } from "lucide-react";
import { uploadResume } from "../lib/api";
import { BrandMark } from "./BrandMark";

export function ApplicationPortal({ onBack }: { onBack: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [state, setState] = useState<"idle" | "uploading" | "success">("idle");
  const [error, setError] = useState("");
  const choose = (next?: File) => {
    setError("");
    if (!next) return;
    if (next.type !== "application/pdf") return setError("Please choose a PDF file.");
    if (next.size > 10 * 1024 * 1024) return setError("Your PDF must be smaller than 10 MB.");
    setFile(next);
  };
  const submit = async () => {
    if (!file) return;
    setState("uploading"); setError("");
    try { await uploadResume(file); setState("success"); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Upload failed. Please try again."); setState("idle"); }
  };
  return <main className="min-h-screen bg-[#F5F6F2] px-5 py-6 text-slate-950 sm:px-8">
    <header className="mx-auto flex max-w-6xl items-center justify-between"><BrandMark /><button onClick={onBack} className="button-quiet"><ArrowLeft size={15} /> Recruiter workspace</button></header>
    <section className="mx-auto grid max-w-6xl items-center gap-12 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:py-24">
      <div className="max-w-lg"><span className="eyebrow">Join our talent network</span><h1 className="mt-5 text-5xl font-semibold leading-[1.03] tracking-[-0.055em] sm:text-6xl">Your next chapter starts here.</h1><p className="mt-6 max-w-md text-lg leading-8 text-slate-500">Share your CV once. Our hiring team will match your experience with the right opportunities—present and future.</p><div className="mt-9 flex flex-wrap gap-x-7 gap-y-3 text-sm text-slate-600"><span className="flex items-center gap-2"><Check size={16} className="text-emerald-700" /> Takes under a minute</span><span className="flex items-center gap-2"><LockKeyhole size={15} className="text-emerald-700" /> Reviewed securely</span></div></div>
      <div className="rounded-[28px] border border-black/5 bg-white p-3 shadow-[0_24px_70px_rgba(29,48,42,0.10)] sm:p-5"><div className="rounded-[22px] border border-slate-100 p-6 sm:p-9">
        {state === "success" ? <div className="grid min-h-[360px] place-items-center text-center"><div><div className="mx-auto grid size-16 place-items-center rounded-full bg-emerald-50 text-emerald-700"><Check size={28} /></div><h2 className="mt-6 text-2xl font-semibold tracking-tight">Application received</h2><p className="mx-auto mt-3 max-w-sm leading-6 text-slate-500">Your profile is now available to our hiring team. We’ll be in touch when there’s a strong fit.</p><button onClick={() => { setFile(null); setState("idle"); }} className="button-primary mt-7">Submit another CV</button></div></div> : <>
          <div><p className="text-sm font-semibold text-[#173F35]">Application profile</p><h2 className="mt-1 text-2xl font-semibold tracking-[-0.025em]">Upload your CV</h2><p className="mt-2 text-sm leading-6 text-slate-500">PDF format · Maximum file size 10 MB</p></div>
          <button type="button" onClick={() => inputRef.current?.click()} onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); choose(e.dataTransfer.files[0]); }} className={`mt-7 flex min-h-56 w-full flex-col items-center justify-center rounded-2xl border border-dashed px-6 text-center transition ${dragging ? "border-emerald-600 bg-emerald-50/60" : "border-slate-300 bg-slate-50/60 hover:border-slate-400 hover:bg-slate-50"}`}><span className="grid size-12 place-items-center rounded-2xl border border-slate-200 bg-white text-[#173F35] shadow-sm"><UploadCloud size={21} /></span><span className="mt-4 text-sm font-semibold">Drop your CV here, or browse</span><span className="mt-1 text-xs text-slate-400">We only accept PDF documents</span></button>
          <input ref={inputRef} type="file" accept="application/pdf,.pdf" className="hidden" onChange={(e) => choose(e.target.files?.[0])} />
          {file && <div className="mt-4 flex items-center gap-3 rounded-xl border border-slate-200 p-3"><span className="grid size-10 place-items-center rounded-lg bg-rose-50 text-rose-600"><FileText size={18} /></span><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{file.name}</p><p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(1)} MB</p></div><button aria-label="Remove file" onClick={() => setFile(null)} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"><X size={16} /></button></div>}
          {error && <p role="alert" className="mt-3 text-sm text-rose-600">{error}</p>}<button disabled={!file || state === "uploading"} onClick={submit} className="button-primary mt-5 w-full disabled:cursor-not-allowed disabled:opacity-40">{state === "uploading" ? "Uploading securely…" : "Submit application"}</button><p className="mt-4 text-center text-[11px] leading-5 text-slate-400">By submitting, you agree that our hiring team may review your CV for relevant roles.</p>
        </>}
      </div></div>
    </section>
  </main>;
}
