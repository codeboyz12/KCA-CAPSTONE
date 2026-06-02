import { useState, useEffect } from 'react';
import { fetchProjects, searchProjects } from '@/lib/api';
import type { Project } from '@/types/project';

export function useProjects(search = '') {
  const [projects, setProjects]       = useState<Project[]>([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages]   = useState(1);
  const [totalItems, setTotalItems]   = useState(0);

  // Reset to page 1 whenever the search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [search]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const req = search
      ? searchProjects(search, currentPage)
      : fetchProjects(currentPage);

    req.then((data) => {
        if (cancelled) return;
        if (data.success) {
          setProjects(data.data);
          setTotalPages(data.pagination.total_pages);
          setTotalItems(data.pagination.total_items);
        }
      })
      .catch((err: Error) => { if (!cancelled) setError(err.message ?? 'เกิดข้อผิดพลาด กรุณาลองใหม่'); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [currentPage, search]);

  const nextPage = () => setCurrentPage((p) => Math.min(p + 1, totalPages));
  const prevPage = () => setCurrentPage((p) => Math.max(p - 1, 1));

  return { projects, loading, error, currentPage, totalPages, totalItems, nextPage, prevPage };
}