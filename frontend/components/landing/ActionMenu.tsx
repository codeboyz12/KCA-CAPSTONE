import { Rocket } from 'lucide-react';

export default function ActionMenu() {
  return (
    <div className="max-w-5xl mx-auto px-6 -mt-12 relative z-20 mb-16">
      <div className="bg-white rounded-2xl shadow-lg p-6 flex flex-col md:flex-row items-center justify-between border border-[#68A4F1]/20">
        <div className="mb-4 md:mb-0">
          <h2 className="text-xl font-bold text-[#061E47]">เริ่มต้นใช้งาน AI Predictor</h2>
          <p className="text-[#1F4591] text-sm">ประเมินโครงสร้างแคมเปญของคุณก่อนลงสนามจริง</p>
        </div>
        <button className="bg-[#1F4591] text-white hover:bg-[#061E47] px-8 py-4 rounded-xl font-bold text-lg transition-all flex items-center gap-3 shadow-md hover:shadow-lg">
          <Rocket className="w-6 h-6 text-[#68A4F1]" />
          ประเมินความน่าจะเป็นของงาน
        </button>
      </div>
    </div>
  );
}