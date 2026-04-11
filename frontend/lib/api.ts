import type { ProjectsResponse } from '@/types/project';
import type { CampaignPayload, PredictResponse, RecommendResponse } from '@/types/predict';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function fetchProjects(page: number, limit = 12): Promise<ProjectsResponse> {
  const res = await fetch(`${API_BASE}/api/v1/projects?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchMetadata(): Promise<{ available_categories: string[] }> {
  const res = await fetch(`${API_BASE}/api/v1/metadata`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function predictCampaign(payload: CampaignPayload): Promise<PredictResponse> {
  const res = await fetch(`${API_BASE}/api/v1/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getRecommendations(
  payload: CampaignPayload,
  top_k = 6
): Promise<RecommendResponse> {
  const res = await fetch(`${API_BASE}/api/v1/recommend?top_k=${top_k}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}