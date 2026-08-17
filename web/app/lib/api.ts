import type { Explanation, RecentSearch, Role, RoleInput, SearchResponse, TalentPoolResponse, UploadResponse } from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) { super(message); }
}

function headers(apiKey?: string): HeadersInit { return apiKey ? { "X-API-Key": apiKey } : {}; }

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? "Something went wrong. Please try again.", response.status);
  }
  return response.json() as Promise<T>;
}

export async function searchCandidates(query: string, limit: number, apiKey?: string) {
  return parse<SearchResponse>(await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers(apiKey) },
    body: JSON.stringify({ query, top_k_people: limit }),
  }));
}

export async function explainCandidate(resumeId: string, jdText: string, apiKey?: string) {
  return parse<Explanation>(await fetch(`${API_URL}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers(apiKey) },
    body: JSON.stringify({ resume_id: resumeId, jd_text: jdText }),
  }));
}

export async function uploadResume(file: File) {
  const body = new FormData();
  body.append("file", file);
  return parse<UploadResponse>(await fetch(`${API_URL}/apply`, { method: "POST", body }));
}

export async function openResume(url: string, apiKey?: string) {
  const preview = window.open("", "_blank", "noopener,noreferrer");
  try {
    const response = await fetch(url, { headers: headers(apiKey) });
    if (!response.ok) throw new ApiError("Could not open this resume.", response.status);
    const objectUrl = URL.createObjectURL(await response.blob());
    if (preview) preview.location.href = objectUrl;
    window.setTimeout(() => URL.revokeObjectURL(objectUrl), 60_000);
  } catch (error) {
    preview?.close();
    throw error;
  }
}

export async function getTalent(search: string, apiKey?: string) {
  const params = new URLSearchParams({ search, limit: "200" });
  return parse<TalentPoolResponse>(await fetch(`${API_URL}/talent?${params}`, { headers: headers(apiKey), cache: "no-store" }));
}

export async function deleteTalent(resumeId: string, apiKey?: string) {
  const response = await fetch(`${API_URL}/talent/${resumeId}`, { method: "DELETE", headers: headers(apiKey) });
  if (!response.ok) throw new ApiError("Could not remove this candidate.", response.status);
}

export async function getRoles(apiKey?: string) {
  return parse<Role[]>(await fetch(`${API_URL}/roles`, { headers: headers(apiKey), cache: "no-store" }));
}

export async function saveRole(role: RoleInput, apiKey?: string, id?: string) {
  return parse<Role>(await fetch(`${API_URL}/roles${id ? `/${id}` : ""}`, {
    method: id ? "PUT" : "POST", headers: { "Content-Type": "application/json", ...headers(apiKey) }, body: JSON.stringify(role),
  }));
}

export async function deleteRole(id: string, apiKey?: string) {
  const response = await fetch(`${API_URL}/roles/${id}`, { method: "DELETE", headers: headers(apiKey) });
  if (!response.ok) throw new ApiError("Could not delete this role.", response.status);
}

export async function getRecentSearches(apiKey?: string) {
  return parse<RecentSearch[]>(await fetch(`${API_URL}/searches`, { headers: headers(apiKey), cache: "no-store" }));
}

export async function deleteRecentSearch(id: string, apiKey?: string) {
  const response = await fetch(`${API_URL}/searches/${id}`, { method: "DELETE", headers: headers(apiKey) });
  if (!response.ok) throw new ApiError("Could not delete this search.", response.status);
}

export async function clearRecentSearches(apiKey?: string) {
  const response = await fetch(`${API_URL}/searches`, { method: "DELETE", headers: headers(apiKey) });
  if (!response.ok) throw new ApiError("Could not clear search history.", response.status);
}
