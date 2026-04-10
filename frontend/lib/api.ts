import type { ProjectsResponse } from '@/types/project';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function fetchProjects(
  page: number,
  limit = 12
): Promise<ProjectsResponse> {
  const res = await fetch(
    `${API_BASE}/api/v1/projects?page=${page}&limit=${limit}`
  );
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}