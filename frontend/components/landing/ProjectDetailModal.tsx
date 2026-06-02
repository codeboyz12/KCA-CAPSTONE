'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { X, Award, Target, Clock, TrendingUp, Users } from 'lucide-react';
import { fetchCategoryStats } from '@/lib/api';
import type { Project, CategoryStat } from '@/types/project';

interface Props {
  project: Project;
  onClose: () => void;
}

export default function ProjectDetailModal({ project, onClose }: Props) {
  const [stat, setStat] = useState<CategoryStat | null>(null);
  const [loadingStat, setLoadingStat] = useState(true);

  useEffect(() => {
    fetchCategoryStats()
      .then((stats) => setStat(stats.find((s) => s.category === project.category) ?? null))
      .catch(() => setStat(null))
      .finally(() => setLoadingStat(false));
  }, [project.category]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const templateUrl =
    `/predict?category=${encodeURIComponent(project.category)}` +
    `&goal_usd=${project.goal}&duration_days=${project.duration}`;

  const goalVsMedian = stat
    ? Math.round(((project.goal - stat.median_goal_usd) / stat.median_goal_usd) * 100)
    : null;
  const durationVsAvg = stat
    ? Math.round(project.duration - stat.avg_duration_days)
    : null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-[#2B6AD0] bg-[#68A4F1]/20 px-2 py-1 rounded-full uppercase tracking-wider">
              {project.category}
            </span>
            {project.state === 'successful' ? (
              <span className="text-xs font-bold text-[#061E47] bg-[#68A4F1]/30 px-2 py-1 rounded-md inline-flex items-center gap-1">
                <Award className="w-3 h-3" /> สำเร็จ
              </span>
            ) : (
              <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-md">
                ล้มเหลว
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-[#061E47] transition-colors flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <h2 className="text-xl font-bold text-[#061E47] leading-snug">{project.name}</h2>

        {/* Project stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-50 rounded-xl p-4 flex items-center gap-3">
            <Target className="w-5 h-5 text-[#2B6AD0] flex-shrink-0" />
            <div>
              <p className="text-xs text-[#1F4591] font-medium">เป้าหมาย</p>
              <p className="text-base font-bold text-[#061E47]">${project.goal.toLocaleString()}</p>
            </div>
          </div>
          <div className="bg-slate-50 rounded-xl p-4 flex items-center gap-3">
            <Clock className="w-5 h-5 text-[#2B6AD0] flex-shrink-0" />
            <div>
              <p className="text-xs text-[#1F4591] font-medium">ระยะเวลา</p>
              <p className="text-base font-bold text-[#061E47]">{project.duration} วัน</p>
            </div>
          </div>
        </div>

        {/* Category benchmarks */}
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-[#1F4591] mb-3">
            สถิติหมวดหมู่: {project.category}
          </p>

          {loadingStat ? (
            <div className="h-20 flex items-center justify-center text-[#2B6AD0] text-sm">
              กำลังโหลด...
            </div>
          ) : stat ? (
            <div className="space-y-3">
              {/* Success rate bar */}
              <div>
                <div className="flex justify-between text-xs text-[#1F4591] mb-1">
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" /> อัตราสำเร็จ
                  </span>
                  <span className="font-bold">{(stat.success_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#2B6AD0] rounded-full transition-all"
                    style={{ width: `${stat.success_rate * 100}%` }}
                  />
                </div>
              </div>

              {/* Goal vs median */}
              <div className="flex justify-between items-center text-sm">
                <span className="text-[#1F4591]">Median goal ในหมวดหมู่</span>
                <span className="font-bold text-[#061E47]">
                  ${stat.median_goal_usd.toLocaleString()}
                  {goalVsMedian !== null && (
                    <span className={`ml-1 text-xs font-normal ${goalVsMedian > 0 ? 'text-amber-600' : 'text-green-600'}`}>
                      ({goalVsMedian >= 0 ? '+' : ''}{goalVsMedian}%)
                    </span>
                  )}
                </span>
              </div>

              {/* Duration vs avg */}
              <div className="flex justify-between items-center text-sm">
                <span className="text-[#1F4591]">Avg duration ในหมวดหมู่</span>
                <span className="font-bold text-[#061E47]">
                  {Math.round(stat.avg_duration_days)} วัน
                  {durationVsAvg !== null && (
                    <span className={`ml-1 text-xs font-normal ${durationVsAvg > 0 ? 'text-amber-600' : 'text-green-600'}`}>
                      ({durationVsAvg >= 0 ? '+' : ''}{durationVsAvg} วัน)
                    </span>
                  )}
                </span>
              </div>

              {/* Total projects */}
              <div className="flex justify-between items-center text-sm">
                <span className="text-[#1F4591] flex items-center gap-1">
                  <Users className="w-3 h-3" /> โปรเจกต์ทั้งหมดในหมวดหมู่
                </span>
                <span className="font-bold text-[#061E47]">{stat.total_projects.toLocaleString()}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-4">ไม่พบสถิติหมวดหมู่</p>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl border border-slate-200 text-[#061E47] font-medium text-sm hover:bg-slate-50 transition-colors"
          >
            ปิด
          </button>
          <Link
            href={templateUrl}
            onClick={onClose}
            className="flex-1 py-3 rounded-xl bg-[#1F4591] text-white font-bold text-sm text-center hover:bg-[#061E47] transition-colors"
          >
            ใช้เป็นต้นแบบใน Predictor →
          </Link>
        </div>
      </div>
    </div>
  );
}
