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

    let predictRes: PredictResponse;
    try {
      predictRes = await predictCampaign(payload);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(`วิเคราะห์แคมเปญไม่สำเร็จ (${msg})`);
      setLoading(false);
      return;
    }

    setPrediction(predictRes);

    // Recommendations are non-critical — failure doesn't hide the prediction result
    try {
      const recommendRes = await getRecommendations(payload, 6);
      setRecommend(recommendRes);
    } catch {
      // silently skip
    }

    setLoading(false);
  };

  return { submit, loading, error, prediction, recommend };
}
