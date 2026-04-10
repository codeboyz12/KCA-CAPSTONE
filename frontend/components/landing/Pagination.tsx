import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Props {
  currentPage: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
}

export default function Pagination({ currentPage, totalPages, onPrev, onNext }: Props) {
  return (
    <div className="mt-12 flex items-center justify-between border-t border-[#68A4F1]/20 pt-6">
      <span className="text-sm text-[#1F4591]">
        หน้า {currentPage} จาก {totalPages.toLocaleString()}
      </span>
      <div className="flex items-center gap-2">
        <button
          onClick={onPrev}
          disabled={currentPage === 1}
          className={`p-2 rounded-lg flex items-center transition-colors ${
            currentPage === 1
              ? 'text-slate-300 cursor-not-allowed'
              : 'text-[#061E47] hover:bg-[#68A4F1]/20'
          }`}
        >
          <ChevronLeft className="w-5 h-5 mr-1" /> ย้อนกลับ
        </button>
        <button
          onClick={onNext}
          disabled={currentPage === totalPages}
          className={`p-2 rounded-lg flex items-center transition-colors ${
            currentPage === totalPages
              ? 'text-slate-300 cursor-not-allowed'
              : 'text-[#061E47] hover:bg-[#68A4F1]/20'
          }`}
        >
          ถัดไป <ChevronRight className="w-5 h-5 ml-1" />
        </button>
      </div>
    </div>
  );
}