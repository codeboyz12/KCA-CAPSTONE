import { useState } from 'react';
import { predictCampaign, getRecommendations } from '@/lib/api';
import type {
  CampaignPayload,
  PredictResponse,
  RecommendResponse,
} from '@/types/predict';

export function usePredict() {
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const [prediction,  setPrediction]  = useState<PredictResponse | null>(null);
  const [recommend,   setRecommend]   = useState<RecommendResponse | null>(null);

  const submit = async (payload: CampaignPayload) => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    setRecommend(null);

    try {
      // เรียก 2 APIs พร้อมกัน
      const [predictRes, recommendRes] = await Promise.all([
        predictCampaign(payload),
        getRecommendations(payload, 6),
      ]);
      setPrediction(predictRes);
      setRecommend(recommendRes);
    } catch (e) {
      setError('เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง');
    } finally {
      setLoading(false);
    }
  };

  return { submit, loading, error, prediction, recommend };
}