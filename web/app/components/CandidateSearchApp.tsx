"use client";
import { useState } from "react";
import { ApplicationPortal } from "./ApplicationPortal";
import { RecruiterWorkspace } from "./RecruiterWorkspace";
export function CandidateSearchApp() {
  const [view, setView] = useState<"recruiter" | "apply">("recruiter");
  return view === "apply" ? <ApplicationPortal onBack={() => setView("recruiter")} /> : <RecruiterWorkspace onApply={() => setView("apply")} />;
}
