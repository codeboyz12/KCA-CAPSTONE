import { Target, Clock, Award, XCircle } from 'lucide-react';
import type { RecommendResponse, SimilarProject } from '@/types/predict';

interface Props {
  data: RecommendResponse;
}

function ProjectCard({ project }: { project: SimilarProject }) {
  const isSuccess = project.state === 'Successful';
  return (
    <div className="bg-white rounded-xl border border-[#68A4F1]/20 p-4 hover:shadow-md transition-all">
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-sm font-bold text-[#061E47] line-clamp-2 flex-1 mr-2">
          {project.name}
        </h4>
        {isSuccess ? (
          <Award className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
        ) : (
          <XCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
        )}
      </div>

      <span className="text-xs font-bold text-[#2B6AD0] bg-[#68A4F1]/20 px-2 py-0.5 rounded-full">
        {project.category}
      </span>

      <div className="mt-3 space-y-1">
        <div className="flex items-center text-xs text-[#1F4591]">
          <Target className="w-3 h-3 mr-1.5 opacity-70" />
          ${project.goal_usd.toLocaleString()}
        </div>
        <div className="flex items-center text-xs text-[#1F4591]">
          <Clock className="w-3 h-3 mr-1.5 opacity-70" />
          {project.duration_days} วัน
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-[#68A4F1]/10 flex justify-between items-center">
        <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${
          isSuccess
            ? 'text-emerald-700 bg-emerald-50'
            : 'text-red-600 bg-red-50'
        }`}>
          {isSuccess ? 'สำเร็จ' : 'ล้มเหลว'}
        </span>
        <span className="text-xs text-[#1F4591]">
          คล้าย {(project.similarity_score * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

export default function SimilarProjects({ data }: Props) {
  const successful = data.recommended_cases.filter((p) => p.state === 'Successful');
  const failed     = data.recommended_cases.filter((p) => p.state === 'Failed');

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-[#68A4F1]/20 p-8">
      <h3 className="text-lg font-bold text-[#061E47] mb-6">โปรเจคที่คล้ายกัน</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        {/* Successful */}
        <div>
          <p className="text-sm font-bold text-emerald-600 mb-4 flex items-center gap-2">
            <Award className="w-4 h-4" /> ที่สำเร็จ ({successful.length})
          </p>
          {successful.length > 0 ? (
            <div className="grid grid-cols-1 gap-3">
              {successful.map((p) => (
                <ProjectCard key={p.project_id} project={p} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 italic">ไม่พบโปรเจคที่คล้ายกันในกลุ่มนี้</p>
          )}
        </div>

        {/* Failed */}
        <div>
          <p className="text-sm font-bold text-red-500 mb-4 flex items-center gap-2">
            <XCircle className="w-4 h-4" /> ที่ล้มเหลว ({failed.length})
          </p>
          {failed.length > 0 ? (
            <div className="grid grid-cols-1 gap-3">
              {failed.map((p) => (
                <ProjectCard key={p.project_id} project={p} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400 italic">ไม่พบโปรเจคที่คล้ายกันในกลุ่มนี้</p>
          )}
        </div>

      </div>
    </div>
  );
}