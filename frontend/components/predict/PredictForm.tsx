'use client';

import { useState, useEffect } from 'react';
import { fetchMetadata, fetchMainCategories } from '@/lib/api';
import type { CampaignPayload } from '@/types/predict';

const MONTHS = [
  'มกราคม','กุมภาพันธ์','มีนาคม','เมษายน',
  'พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม',
  'กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม',
];

const CURRENT_YEAR = new Date().getFullYear();
const YEARS   = Array.from({ length: CURRENT_YEAR - 2008 }, (_, i) => 2009 + i).reverse();
const DAYS    = Array.from({ length: 31 }, (_, i) => i + 1);
const HOURS   = Array.from({ length: 24 }, (_, i) => i);
const MINUTES = Array.from({ length: 60 }, (_, i) => i);

const today = new Date();
const DEFAULT: CampaignPayload = {
  name:            '',
  category:        '',
  main_category:   '',
  goal_usd:        5000,
  duration_days:   30,
  launch_year:     today.getFullYear(),
  launch_month:    today.getMonth() + 1,
  launch_day:      today.getDate(),
  launch_hour:     12,
  deadline_year:   today.getFullYear(),
  deadline_month:  today.getMonth() + 1,
  deadline_day:    today.getDate(),
  deadline_hour:   12,
  deadline_minute: 0,
};

interface Props {
  onSubmit: (payload: CampaignPayload) => void;
  loading:  boolean;
}

export default function PredictForm({ onSubmit, loading }: Props) {
  const [categories,     setCategories]     = useState<string[]>([]);
  const [mainCategories, setMainCategories] = useState<string[]>([]);
  const [form, setForm] = useState<CampaignPayload>(DEFAULT);

  useEffect(() => {
    Promise.all([fetchMetadata(), fetchMainCategories()]).then(([meta, mainCats]) => {
      const cats = meta.available_categories ?? [];
      setCategories(cats);
      setMainCategories(mainCats);
      setForm((prev) => ({
        ...prev,
        category:      cats[0]      ?? '',
        main_category: mainCats[0]  ?? '',
      }));
    });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === 'name' ? value : Number(value),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  const inputClass =
    'w-full border border-[#68A4F1]/40 rounded-xl px-4 py-3 text-[#061E47] outline-none ' +
    'focus:border-[#2B6AD0] focus:ring-2 focus:ring-[#2B6AD0]/20 transition-all bg-white';
  const labelClass = 'block text-sm font-bold text-[#061E47] mb-2';
  const groupLabel = 'text-xs font-bold uppercase tracking-wider text-[#1F4591] mb-3 flex items-center gap-2';

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-[#68A4F1]/20 p-8 space-y-7">

      {/* ── Section 1: Campaign Info ── */}
      <div className="space-y-4">
        <p className={groupLabel}>
          <span className="w-5 h-5 rounded-full bg-[#2B6AD0] text-white text-[10px] flex items-center justify-center">1</span>
          ข้อมูลแคมเปญ
        </p>

        <div>
          <label className={labelClass}>ชื่อแคมเปญ</label>
          <input
            type="text" name="name"
            value={form.name} onChange={handleChange}
            placeholder="เช่น The Ultimate Board Game: A New Adventure"
            className={inputClass}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>หมวดหมู่หลัก</label>
            <select name="main_category" value={form.main_category} onChange={handleChange} className={inputClass}>
              {mainCategories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>หมวดหมู่ย่อย</label>
            <select name="category" value={form.category} onChange={handleChange} className={inputClass}>
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className={labelClass}>เป้าหมายระดมทุน (USD)</label>
          <input
            type="number" name="goal_usd" min={1}
            value={form.goal_usd} onChange={handleChange}
            placeholder="เช่น 5000"
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass}>
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
      </div>

      <hr className="border-[#68A4F1]/20" />

      {/* ── Section 2: Launch Date ── */}
      <div className="space-y-4">
        <p className={groupLabel}>
          <span className="w-5 h-5 rounded-full bg-[#2B6AD0] text-white text-[10px] flex items-center justify-center">2</span>
          วันที่เปิดตัว
        </p>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelClass}>วัน</label>
            <select name="launch_day" value={form.launch_day} onChange={handleChange} className={inputClass}>
              {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>เดือน</label>
            <select name="launch_month" value={form.launch_month} onChange={handleChange} className={inputClass}>
              {MONTHS.map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>ปี</label>
            <select name="launch_year" value={form.launch_year} onChange={handleChange} className={inputClass}>
              {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className={labelClass}>เวลาเปิดตัว</label>
          <select name="launch_hour" value={form.launch_hour} onChange={handleChange} className={inputClass}>
            {HOURS.map((h) => <option key={h} value={h}>{h}</option>)}
          </select>
        </div>
      </div>

      <hr className="border-[#68A4F1]/20" />

      {/* ── Section 3: End Date ── */}
      <div className="space-y-4">
        <p className={groupLabel}>
          <span className="w-5 h-5 rounded-full bg-[#2B6AD0] text-white text-[10px] flex items-center justify-center">3</span>
          วันที่สิ้นสุด
        </p>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelClass}>วัน</label>
            <select name="deadline_day" value={form.deadline_day} onChange={handleChange} className={inputClass}>
              {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>เดือน</label>
            <select name="deadline_month" value={form.deadline_month} onChange={handleChange} className={inputClass}>
              {MONTHS.map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>ปี</label>
            <select name="deadline_year" value={form.deadline_year} onChange={handleChange} className={inputClass}>
              {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>เวลาสิ้นสุด</label>
            <select name="deadline_hour" value={form.deadline_hour} onChange={handleChange} className={inputClass}>
              {HOURS.map((h) => <option key={h} value={h}>{h}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>นาที</label>
            <select name="deadline_minute" value={form.deadline_minute} onChange={handleChange} className={inputClass}>
              {MINUTES.map((m) => <option key={m} value={m}>:{String(m).padStart(2, '0')}</option>)}
            </select>
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !form.category || !form.main_category || form.goal_usd <= 0}
        className="w-full bg-[#1F4591] hover:bg-[#061E47] text-white py-4 rounded-xl font-bold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'กำลังวิเคราะห์...' : 'วิเคราะห์แคมเปญ'}
      </button>
    </form>
  );
}
