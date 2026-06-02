import { Award } from 'lucide-react';
import type { Project } from '@/types/project';

interface Props {
  project: Project;
  index: number;
  onViewDetail: (project: Project) => void;
}

export default function ProjectRow({ project, index, onViewDetail }: Props) {
  return (
    <tr className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
      <td className="px-4 py-3 text-sm font-medium text-[#061E47] max-w-xs truncate">
        {project.name}
      </td>
      <td className="px-4 py-3">
        <span className="text-xs font-bold text-[#2B6AD0] bg-[#68A4F1]/20 px-2 py-1 rounded-full uppercase tracking-wider">
          {project.category}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-[#1F4591] text-right">
        ${project.goal.toLocaleString()}
      </td>
      <td className="px-4 py-3 text-sm text-[#1F4591] text-center">
        {project.duration} วัน
      </td>
      <td className="px-4 py-3 text-center">
        {project.state === 'successful' ? (
          <span className="text-xs font-bold text-[#061E47] bg-[#68A4F1]/30 px-2 py-1 rounded-md inline-flex items-center gap-1">
            <Award className="w-3 h-3 text-[#1F4591]" /> สำเร็จ
          </span>
        ) : project.state === 'failed' ? (
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
            ล้มเหลว
          </span>
        ) : (
          <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-md">
            {project.state}
          </span>
        )}
      </td>
      <td className="px-4 py-3 text-center">
        <button
          onClick={() => onViewDetail(project)}
          className="text-sm font-bold text-[#2B6AD0] hover:underline"
        >
          ดูรายละเอียด
        </button>
      </td>
    </tr>
  );
}