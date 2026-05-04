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

export interface PredictResponse {
  success: boolean;
  prediction: {
    probability_percentage: number;
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
