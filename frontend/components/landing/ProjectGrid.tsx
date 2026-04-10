import { Loader2 } from 'lucide-react';
import ProjectRow from './ProjectRow';
import type { Project } from '@/types/project';

interface Props {
  projects: Project[];
  loading: boolean;
  totalItems: number;
}

const COLUMNS = ['ชื่อโปรเจกต์', 'หมวดหมู่', 'เป้าหมาย', 'ระยะเวลา', 'สถานะ', ''];

export default function ProjectGrid({ projects, loading, totalItems }: Props) {
  return (
    <div>
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-2xl font-bold text-[#061E47]">โปรเจกต์ทั้งหมดในระบบ</h2>
          <p className="text-[#1F4591] text-sm mt-1">
            แสดงข้อมูลจริงจาก {totalItems.toLocaleString()} แคมเปญ
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-[#2B6AD0]">
          <Loader2 className="w-12 h-12 animate-spin mb-4" />
          <p className="font-medium">กำลังโหลดข้อมูล...</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-[#68A4F1]/20 shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#1F4591] text-white">
                {COLUMNS.map((col) => (
                  <th key={col} className="px-4 py-3 text-sm font-bold tracking-wide">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#68A4F1]/10">
              {projects.map((project, idx) => (
                <ProjectRow key={idx} project={project} index={idx} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}