export interface CampaignPayload {
  name:            string;
  category:        string;
  main_category:   string;
  goal_usd:        number;
  duration_days:   number;
  launch_year:     number;
  launch_month:    number;
  launch_day:      number;
  launch_hour:     number;
  deadline_year:   number;
  deadline_month:  number;
  deadline_day:    number;
  deadline_hour:   number;
  deadline_minute: number;
}

export interface ShapFactor {
  feature:   string;
  direction: 'up' | 'down';
  impact:    number;
}

export interface PredictResponse {
  success: boolean;
  prediction: {
    probability_percentage: number;
    is_viable:              boolean;
  };
  category_stats: {
    success_rate:    number;
    median_goal_usd: number;
    total_projects:  number;
    goal_rank_pct:   number;
  };
  competition: {
    n_competitors: number;
    percentile:    number;
    tier:          'low' | 'medium' | 'high';
  };
  shap_factors: ShapFactor[];
}

export interface SimilarProject {
  project_id:       string;
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
