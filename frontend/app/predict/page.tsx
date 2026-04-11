'use client';

import { Rocket } from 'lucide-react';
import Link from 'next/link';
import PredictForm     from '@/components/predict/PredictForm';
import PredictResult   from '@/components/predict/PredictResult';
import SimilarProjects from '@/components/predict/SimilarProjects';
import { usePredict }  from '@/hooks/usePredict';

export default function PredictPage() {
  const { submit, loading, error, prediction, recommend } = usePredict();

  return (
    <div className="min-h-screen bg-slate-50 text-[#061E47]">

      {/* Header */}
      <header className="bg-gradient-to-b from-[#2B6AD0] to-[#1F4591] pt-16 pb-20 px-6 text-center">
        <Link href="/" className="text-[#68A4F1] text-sm hover:underline mb-4 inline-block">
          ← กลับหน้าหลัก
        </Link>
        <div className="flex items-center justify-center gap-3 mb-3">
          <Rocket className="w-8 h-8 text-[#68A4F1]" />
          <h1 className="text-3xl md:text-4xl font-bold text-white">วิเคราะห์แคมเปญ</h1>
        </div>
        <p className="text-[#68A4F1] max-w-lg mx-auto">
          กรอกข้อมูลแคมเปญเพื่อประเมินโอกาสสำเร็จและหาโปรเจคต้นแบบ
        </p>
      </header>

      <main className="max-w-6xl mx-auto px-6 -mt-8 pb-20 space-y-8">

        {/* Row 1: Form 50% | Result 50% */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">

          {/* ซ้าย: Form */}
          <div className="space-y-4">
            <PredictForm onSubmit={submit} loading={loading} />
            {error && (
              <p className="text-red-500 text-sm text-center bg-red-50 rounded-xl px-4 py-3 border border-red-200">
                {error}
              </p>
            )}
          </div>

          {/* ขวา: ผลลัพธ์ */}
          <div>
            {!prediction && !loading && (
              <div className="bg-white rounded-2xl border border-[#68A4F1]/20 p-12 text-center text-slate-400 h-full flex flex-col items-center justify-center min-h-[300px]">
                <Rocket className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>กรอกข้อมูลแล้วกด "วิเคราะห์แคมเปญ"<br />เพื่อดูผลการประเมิน</p>
              </div>
            )}

            {loading && (
              <div className="bg-white rounded-2xl border border-[#68A4F1]/20 p-12 text-center text-[#2B6AD0] h-full flex flex-col items-center justify-center min-h-[300px]">
                <div className="w-12 h-12 border-4 border-[#2B6AD0] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="font-medium">กำลังวิเคราะห์...</p>
              </div>
            )}

            {prediction && <PredictResult result={prediction} />}
          </div>
        </div>

        {/* Row 2: Similar Projects 100% */}
        {recommend && (
          <div className="w-full">
            <SimilarProjects data={recommend} />
          </div>
        )}

      </main>
    </div>
  );
}