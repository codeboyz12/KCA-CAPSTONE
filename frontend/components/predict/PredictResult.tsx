import { TrendingUp, TrendingDown, Users, BarChart2, Zap } from 'lucide-react';
import type { PredictResponse, ShapFactor } from '@/types/predict';

const FEATURE_LABELS: Record<string, string> = {
  cat_success_rate:          'อัตราสำเร็จในหมวด',
  lag1_sr:                   'อัตราสำเร็จเดือนก่อน',
  category:                  'หมวดหมู่',
  deadline_minute:           'นาทีสิ้นสุด',
  goal_rank_in_cat:          'อันดับเป้าหมายในหมวด',
  goal_x_duration:           'เป้าหมาย × ระยะเวลา',
  goal_usd:                  'เป้าหมายระดมทุน',
  goal_vs_cat_median:        'เป้าหมายเทียบค่ากลางหมวด',
  log_goal_ratio:            'อัตราส่วนเป้าหมาย',
  name_has_colon:            'ชื่อมี ":"',
  duration_days:             'ระยะเวลาแคมเปญ',
  goal_usd_log:              'ระดับเป้าหมาย',
  launch_deadline_hour_diff: 'ช่วงเวลาเปิด–ปิด',
  goal_vs_cat_mean:          'เป้าหมายเทียบค่าเฉลี่ยหมวด',
  launch_year:               'ปีที่เปิดตัว',
};

const TIER_CONFIG = {
  low:    { label: 'ต่ำ',    bg: 'bg-emerald-100', text: 'text-emerald-700' },
  medium: { label: 'ปานกลาง', bg: 'bg-amber-100',   text: 'text-amber-700'   },
  high:   { label: 'สูง',    bg: 'bg-red-100',      text: 'text-red-700'     },
};

function MiniBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div className="w-full bg-slate-100 rounded-full h-1.5">
      <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function ShapRow({ factor, maxImpact }: { factor: ShapFactor; maxImpact: number }) {
  const isUp   = factor.direction === 'up';
  const pct    = maxImpact > 0 ? (factor.impact / maxImpact) * 100 : 0;
  const label  = FEATURE_LABELS[factor.feature] ?? factor.feature;

  return (
    <div className="flex items-center gap-3">
      <div className={`shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
        isUp ? 'bg-emerald-100' : 'bg-red-100'
      }`}>
        {isUp
          ? <TrendingUp  className="w-3.5 h-3.5 text-emerald-600" />
          : <TrendingDown className="w-3.5 h-3.5 text-red-500"    />}
      </div>
      <span className="text-xs text-[#1F4591] w-36 shrink-0">{label}</span>
      <div className="flex-1 bg-slate-100 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            isUp ? 'bg-emerald-400' : 'bg-red-400'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`text-xs font-bold w-10 text-right ${
        isUp ? 'text-emerald-600' : 'text-red-500'
      }`}>
        {isUp ? '+' : '−'}{factor.impact.toFixed(2)}
      </span>
    </div>
  );
}

interface Props {
  result: PredictResponse;
}

export default function PredictResult({ result }: Props) {
  const { probability_percentage, is_viable } = result.prediction;
  const stats  = result.category_stats;
  const comp   = result.competition;
  const shap   = result.shap_factors ?? [];

  const scoreColor = probability_percentage >= 70
    ? 'text-emerald-600'
    : probability_percentage >= 40 ? 'text-amber-500' : 'text-red-500';

  const bgColor = probability_percentage >= 70
    ? 'bg-emerald-50 border-emerald-200'
    : probability_percentage >= 40 ? 'bg-amber-50 border-amber-200' : 'bg-red-50 border-red-200';

  const barColor = is_viable ? 'bg-emerald-500' : 'bg-red-400';

  const tierCfg  = TIER_CONFIG[comp.tier];
  const maxImpact = shap.length > 0 ? Math.max(...shap.map((f) => f.impact)) : 1;

  return (
    <div className={`rounded-2xl border-2 p-8 space-y-6 ${bgColor}`}>

      {/* ── Probability ── */}
      <div>
        <p className="text-sm font-bold text-[#1F4591] mb-2 uppercase tracking-wider">
          ผลการวิเคราะห์
        </p>
        <div className="flex items-end gap-2 mb-3">
          <span className={`text-7xl font-bold ${scoreColor}`}>
            {probability_percentage.toFixed(1)}
          </span>
          <span className={`text-3xl font-bold mb-2 ${scoreColor}`}>%</span>
        </div>
        <p className="text-[#1F4591] font-medium mb-4">โอกาสที่แคมเปญจะสำเร็จ</p>
        <div className="w-full bg-white/60 rounded-full h-3 mb-4">
          <div
            className={`h-3 rounded-full transition-all duration-700 ${barColor}`}
            style={{ width: `${probability_percentage}%` }}
          />
        </div>
        <div className="text-center">
          {is_viable ? (
            <span className="text-emerald-700 font-bold text-sm bg-emerald-100 px-4 py-2 rounded-full">
              ✓ แคมเปญนี้มีศักยภาพสูง
            </span>
          ) : (
            <span className="text-red-700 font-bold text-sm bg-red-100 px-4 py-2 rounded-full">
              ✗ ควรปรับกลยุทธ์ก่อนเปิดตัว
            </span>
          )}
        </div>
      </div>

      <hr className="border-white/60" />

      {/* ── Category Stats ── */}
      <div>
        <p className="text-xs font-bold text-[#1F4591] uppercase tracking-wider mb-4 flex items-center gap-2">
          <BarChart2 className="w-3.5 h-3.5" /> สถิติหมวดหมู่
        </p>
        <div className="space-y-3">

          <div>
            <div className="flex justify-between text-xs text-[#1F4591] mb-1">
              <span>อัตราสำเร็จในหมวด</span>
              <span className="font-bold">{(stats.success_rate * 100).toFixed(1)}%</span>
            </div>
            <MiniBar value={stats.success_rate} max={1} color="bg-[#2B6AD0]" />
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs text-[#1F4591]">
            <div className="bg-white/50 rounded-xl p-3">
              <p className="text-[10px] uppercase tracking-wide opacity-60 mb-1">เป้าหมายมัธยฐาน</p>
              <p className="font-bold text-sm">${stats.median_goal_usd.toLocaleString()}</p>
            </div>
            <div className="bg-white/50 rounded-xl p-3">
              <p className="text-[10px] uppercase tracking-wide opacity-60 mb-1">จำนวนโปรเจค</p>
              <p className="font-bold text-sm">{stats.total_projects.toLocaleString()}</p>
            </div>
          </div>

          <div className="bg-white/50 rounded-xl p-3 text-xs text-[#1F4591]">
            <div className="flex justify-between mb-1">
              <span>เป้าหมายของคุณสูงกว่า</span>
              <span className="font-bold">{(stats.goal_rank_pct * 100).toFixed(0)}%</span>
            </div>
            <MiniBar value={stats.goal_rank_pct} max={1} color="bg-amber-400" />
            <p className="text-[10px] opacity-60 mt-1">ของโปรเจคในหมวดเดียวกัน</p>
          </div>

        </div>
      </div>

      <hr className="border-white/60" />

      {/* ── Competition ── */}
      <div>
        <p className="text-xs font-bold text-[#1F4591] uppercase tracking-wider mb-3 flex items-center gap-2">
          <Users className="w-3.5 h-3.5" /> การแข่งขัน
        </p>
        <div className="flex items-center justify-between bg-white/50 rounded-xl p-3">
          <div className="text-xs text-[#1F4591]">
            <p className="font-bold text-base">{comp.n_competitors.toLocaleString()}</p>
            <p className="opacity-60">คู่แข่งในเดือนนี้</p>
          </div>
          <div className="text-right">
            <span className={`text-xs font-bold px-3 py-1.5 rounded-full ${tierCfg.bg} ${tierCfg.text}`}>
              ระดับ {tierCfg.label}
            </span>
            <p className="text-[10px] text-[#1F4591] opacity-60 mt-1">
              เปอร์เซ็นไทล์ {(comp.percentile * 100).toFixed(0)}
            </p>
          </div>
        </div>
      </div>

      {shap.length > 0 && (
        <>
          <hr className="border-white/60" />

          {/* ── SHAP Factors ── */}
          <div>
            <p className="text-xs font-bold text-[#1F4591] uppercase tracking-wider mb-4 flex items-center gap-2">
              <Zap className="w-3.5 h-3.5" /> ปัจจัยที่มีผลต่อคะแนน
            </p>
            <div className="space-y-2.5">
              {shap.map((f) => (
                <ShapRow key={f.feature} factor={f} maxImpact={maxImpact} />
              ))}
            </div>
            <p className="text-[10px] text-[#1F4591] opacity-50 mt-3">
              ↑ ช่วยเพิ่มโอกาส · ↓ ลดโอกาส · ค่าแสดงผลกระทบสัมพัทธ์ (SHAP)
            </p>
          </div>
        </>
      )}

    </div>
  );
}
