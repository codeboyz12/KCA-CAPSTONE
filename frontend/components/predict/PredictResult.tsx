import type { PredictResponse } from '@/types/predict';

interface Props {
  result: PredictResponse;
}

export default function PredictResult({ result }: Props) {
  const { probability_percentage, expected_pledged_usd, is_viable } = result.prediction;

  const color = probability_percentage >= 70
    ? 'text-emerald-600'
    : probability_percentage >= 40
    ? 'text-amber-500'
    : 'text-red-500';

  const bgColor = probability_percentage >= 70
    ? 'bg-emerald-50 border-emerald-200'
    : probability_percentage >= 40
    ? 'bg-amber-50 border-amber-200'
    : 'bg-red-50 border-red-200';

  return (
    <div className={`rounded-2xl border-2 p-8 ${bgColor}`}>
      <p className="text-sm font-bold text-[#1F4591] mb-2 uppercase tracking-wider">
        ผลการวิเคราะห์
      </p>

      {/* โอกาสสำเร็จ */}
      <div className="mb-6">
        <div className="flex items-end gap-2 mb-3">
          <span className={`text-7xl font-bold ${color}`}>
            {probability_percentage.toFixed(1)}
          </span>
          <span className={`text-3xl font-bold mb-2 ${color}`}>%</span>
        </div>
        <p className="text-[#1F4591] font-medium">โอกาสที่แคมเปญจะสำเร็จ</p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-white/60 rounded-full h-3 mb-6">
        <div
          className={`h-3 rounded-full transition-all duration-700 ${
            is_viable ? 'bg-emerald-500' : 'bg-red-400'
          }`}
          style={{ width: `${probability_percentage}%` }}
        />
      </div>

      {/* Expected amount */}
      <div className="bg-white/60 rounded-xl p-4 flex justify-between items-center">
        <span className="text-sm text-[#1F4591] font-medium">คาดว่าจะระดมทุนได้</span>
        <span className="text-xl font-bold text-[#061E47]">
          ${expected_pledged_usd.toLocaleString()}
        </span>
      </div>

      {/* Verdict */}
      <div className="mt-4 text-center">
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
  );
}