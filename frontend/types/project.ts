export interface Project {
  id: string;
  name: string;
  category: string;
  goal: number;
  duration: number;
  state: 'successful' | 'failed';
}

export interface Pagination {
  total_pages: number;
  total_items: number;
  current_page: number;
}

export interface ProjectsResponse {
  success: boolean;
  data: Project[];
  pagination: Pagination;
}

export interface CategoryStat {
  category: string;
  total_projects: number;
  successful_count: number;
  success_rate: number;
  avg_goal_usd: number;
  median_goal_usd: number;
  avg_duration_days: number;
}