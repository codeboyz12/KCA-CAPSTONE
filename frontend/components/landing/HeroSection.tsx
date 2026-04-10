'use client';

import { Search } from 'lucide-react';

interface Props {
  searchTerm: string;
  onSearch: (value: string) => void;
}

export default function HeroSection({ searchTerm, onSearch }: Props) {
  return (
    <header className="bg-gradient-to-b from-[#2B6AD0] to-[#1F4591] pt-24 pb-32 px-6 text-center relative overflow-hidden">
      <div className="relative z-10 max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 drop-shadow-sm">
          Kickstarter Campaign Advisor
        </h1>
        <p className="text-lg md:text-xl text-[#68A4F1] mb-12 max-w-2xl mx-auto">
          เปลี่ยนไอเดียระดมทุนให้เป็นความจริง ด้วย AI วิเคราะห์และประเมินโอกาสสำเร็จของโปรเจกต์
        </p>

        <div className="max-w-3xl mx-auto relative shadow-2xl rounded-full">
          <div className="bg-white rounded-full p-2 flex items-center border-4 border-[#68A4F1]/30">
            <Search className="text-[#061E47] w-6 h-6 ml-4" />
            <input
              type="text"
              placeholder="ค้นหาโปรเจกต์ต้นแบบ (Similarity Search)..."
              className="w-full p-4 outline-none text-[#061E47] bg-transparent font-medium placeholder:text-slate-400"
              value={searchTerm}
              onChange={(e) => onSearch(e.target.value)}
            />
            <button className="bg-[#2B6AD0] text-white px-8 py-3 rounded-full font-bold hover:bg-[#1F4591] transition-colors shadow-md">
              ค้นหา
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}