import { Sparkles } from "lucide-react";

export function BrandMark({ compact = false }: { compact?: boolean }) {
  return <div className="flex items-center gap-3">
    <div className="grid size-9 place-items-center rounded-xl bg-[#173F35] text-white shadow-sm"><Sparkles size={17} strokeWidth={2.2} /></div>
    {!compact && <div><div className="text-[15px] font-semibold tracking-[-0.02em] text-slate-950">Shortlist</div><div className="text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">Talent intelligence</div></div>}
  </div>;
}
