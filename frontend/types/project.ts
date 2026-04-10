export interface Project {
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