import { PlayCircle, Target, Clock, Award } from 'lucide-react';
import type { Project } from '@/types/project';

interface Props {
  project: Project;
}

export default function ProjectCard({ project }: Props) {
  return (
    <div className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all border border-[#68A4F1]/20 group cursor-pointer flex flex-col">
      <div className="bg-gradient-to-tr from-[#68A4F1]/20 to-[#2B6AD0]/10 h-32 flex items-center justify-center p-4 relative">
        <span className="text-xs font-bold text-white bg-[#2B6AD0] px-3 py-1 rounded-full absolute top-4 left-4 uppercase tracking-wider shadow-sm">
          {project.category}
        </span>
        <PlayCircle className="w-12 h-12 text-[#2B6AD0] opacity-50 group-hover:opacity-100 group-hover:scale-110 transition-all" />
      </div>

      <div className="p-5 flex-1 flex flex-col">
        <h3
          className="text-lg font-bold text-[#061E47] mb-3 line-clamp-2 group-hover:text-[#2B6AD0] transition-colors"
          title={project.name}
        >
          {project.name}
        </h3>

        <div className="space-y-2 mb-4 mt-auto">
          <div className="flex items-center text-[#1F4591] text-sm">
            <Target className="w-4 h-4 mr-2 opacity-70" />
            <span>เป้าหมาย: <strong>${project.goal.toLocaleString()}</strong></span>
          </div>
          <div className="flex items-center text-[#1F4591] text-sm">
            <Clock className="w-4 h-4 mr-2 opacity-70" />
            <span>ระยะเวลา: <strong>{project.duration} วัน</strong></span>
          </div>
        </div>

        <div className="pt-4 border-t border-[#68A4F1]/20 flex justify-between items-center">
          {project.state === 'successful' ? (
            <span className="text-xs font-bold text-[#061E47] bg-[#68A4F1]/30 px-2 py-1 rounded-md flex items-center gap-1">
              <Award className="w-3 h-3 text-[#1F4591]" /> สำเร็จ
            </span>
          ) : (
            <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
              ล้มเหลว
            </span>
          )}
          <span className="font-bold text-[#2B6AD0] text-sm hover:underline">ดูรายละเอียด</span>
        </div>
      </div>
    </div>
  );
}