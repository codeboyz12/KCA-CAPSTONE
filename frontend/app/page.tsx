'use client';

import { useState } from 'react';
import HeroSection  from '@/components/landing/HeroSection';
import ActionMenu   from '@/components/landing/ActionMenu';
import ProjectGrid  from '@/components/landing/ProjectGrid';
import Pagination   from '@/components/landing/Pagination';
import { useProjects } from '@/hooks/useProjects';

export default function LandingPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const {
    projects, loading,
    currentPage, totalPages, totalItems,
    nextPage, prevPage,
  } = useProjects();

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-[#061E47]">
      <HeroSection searchTerm={searchTerm} onSearch={setSearchTerm} />
      <ActionMenu />
      <main className="max-w-7xl mx-auto px-6 pb-20">
        <ProjectGrid projects={projects} loading={loading} totalItems={totalItems} />
        {!loading && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPrev={prevPage}
            onNext={nextPage}
          />
        )}
      </main>
    </div>
  );
}