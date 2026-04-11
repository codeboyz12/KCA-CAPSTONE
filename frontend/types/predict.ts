export interface CampaignPayload {
  category:      string;
  goal_usd:      number;
  duration_days: number;
  launch_month:  number;
}

export interface PredictResponse {
  success: boolean;
  prediction: {
    probability_percentage: number;
    expected_pledged_usd:   number;
    is_viable:              boolean;
  };
}

export interface SimilarProject {
  project_id:       number;
  name:             string;
  category:         string;
  goal_usd:         number;
  duration_days:    number;
  state:            'Successful' | 'Failed';
  similarity_score: number;
}

export interface RecommendResponse {
  success:           boolean;
  target_category:   string;
  recommended_cases: SimilarProject[];
}