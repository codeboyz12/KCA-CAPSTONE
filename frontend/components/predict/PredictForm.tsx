'use client';

import { useState, useEffect } from 'react';
import { fetchMetadata } from '@/lib/api';
import type { CampaignPayload } from '@/types/predict';

const MONTHS = [
  'มกราคม','กุมภาพันธ์','มีนาคม','เมษายน',
  'พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม',
  'กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม',
];

interface Props {
  onSubmit: (payload: CampaignPayload) => void;
  loading:  boolean;
}

export default function PredictForm({ onSubmit, loading }: Props) {
  const [categories, setCategories] = useState<string[]>([]);
  const [form, setForm] = useState<CampaignPayload>({
    category:      '',
    goal_usd:      0,
    duration_days: 30,
    launch_month:  1,
  });

  useEffect(() => {
    fetchMetadata().then((d) => {
      setCategories(d.available_categories);
      setForm((prev) => ({ ...prev, category: d.available_categories[0] ?? '' }));
    });
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === 'category' ? value : Number(value),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  const inputClass =
    'w-full border border-[#68A4F1]/40 rounded-xl px-4 py-3 text-[#061E47] outline-none focus:border-[#2B6AD0] focus:ring-2 focus:ring-[#2B6AD0]/20 transition-all bg-white';

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-[#68A4F1]/20 p-8 space-y-6">
      <div>
        <label className="block text-sm font-bold text-[#061E47] mb-2">หมวดหมู่</label>
        <select name="category" value={form.category} onChange={handleChange} className={inputClass}>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-bold text-[#061E47] mb-2">เป้าหมายระดมทุน (USD)</label>
        <input
          type="number" name="goal_usd" min={1}
          value={form.goal_usd} onChange={handleChange}
          placeholder="เช่น 5000"
          className={inputClass}
        />
      </div>

      <div>
        <label className="block text-sm font-bold text-[#061E47] mb-2">
          ระยะเวลาแคมเปญ — <span className="text-[#2B6AD0]">{form.duration_days} วัน</span>
        </label>
        <input
          type="range" name="duration_days"
          min={1} max={60} value={form.duration_days}
          onChange={handleChange}
          className="w-full accent-[#2B6AD0]"
        />
        <div className="flex justify-between text-xs text-[#1F4591] mt-1">
          <span>1 วัน</span><span>60 วัน</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-bold text-[#061E47] mb-2">เดือนที่เปิดตัว</label>
        <select name="launch_month" value={form.launch_month} onChange={handleChange} className={inputClass}>
          {MONTHS.map((m, i) => (
            <option key={i + 1} value={i + 1}>{m}</option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={loading || !form.category || form.goal_usd <= 0}
        className="w-full bg-[#1F4591] hover:bg-[#061E47] text-white py-4 rounded-xl font-bold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'กำลังวิเคราะห์...' : 'วิเคราะห์แคมเปญ'}
      </button>
    </form>
  );
}