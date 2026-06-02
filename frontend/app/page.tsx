'use client';

import { useState, useEffect } from 'react';
import HeroSection        from '@/components/landing/HeroSection';
import ActionMenu         from '@/components/landing/ActionMenu';
import ProjectGrid        from '@/components/landing/ProjectGrid';
import Pagination         from '@/components/landing/Pagination';
import ProjectDetailModal from '@/components/landing/ProjectDetailModal';
import { useProjects } from '@/hooks/useProjects';
import type { Project } from '@/types/project';

export default function LandingPage() {
  const [searchTerm, setSearchTerm]         = useState('');
  const [submittedSearch, setSubmittedSearch] = useState('');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // Debounce: auto-search 400 ms after the user stops typing
  useEffect(() => {
    const timer = setTimeout(() => setSubmittedSearch(searchTerm), 400);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleSearchSubmit = () => setSubmittedSearch(searchTerm);

  const {
    projects, loading, error,
    currentPage, totalPages, totalItems,
    nextPage, prevPage,
  } = useProjects(submittedSearch);

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-[#061E47]">
      <HeroSection
        searchTerm={searchTerm}
        onSearch={setSearchTerm}
        onSearchSubmit={handleSearchSubmit}
      />
      <ActionMenu />
      <main className="max-w-7xl mx-auto px-6 pb-20">
        {error && (
          <p className="mb-6 text-sm text-center text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
            {error}
          </p>
        )}
        <ProjectGrid
          projects={projects}
          loading={loading}
          totalItems={totalItems}
          onViewDetail={setSelectedProject}
        />
        {!loading && !error && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPrev={prevPage}
            onNext={nextPage}
          />
        )}
      </main>

      {selectedProject && (
        <ProjectDetailModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  );
}