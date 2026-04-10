import { useState, useEffect } from 'react';
import { fetchProjects } from '@/lib/api';
import type { Project } from '@/types/project';

export function useProjects() {
  const [projects, setProjects]     = useState<Project[]>([]);
  const [loading, setLoading]       = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    fetchProjects(currentPage)
      .then((data) => {
        if (cancelled) return;
        if (data.success) {
          setProjects(data.data);
          setTotalPages(data.pagination.total_pages);
          setTotalItems(data.pagination.total_items);
        }
      })
      .catch(console.error)
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [currentPage]);

  const nextPage = () => setCurrentPage((p) => Math.min(p + 1, totalPages));
  const prevPage = () => setCurrentPage((p) => Math.max(p - 1, 1));

  return { projects, loading, currentPage, totalPages, totalItems, nextPage, prevPage };
}