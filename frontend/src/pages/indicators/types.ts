export interface Category {
  id: number;
  name: string;
  description: string;
}

export interface Indicator {
  id: number;
  code: string;
  name: string;
  description: string;
  category: Category;
  frequency: string;
  unit: string;
}

export interface Region {
  code: string;
  name: string;
}

export interface Observation {
  region: Region;
  date: string;
  value: number;
  source?: {
    code: string;
    name: string;
  };
}

export interface ObservationResponse {
  date: string;
  value: number;
  source: string;
}

export interface RegionResponse {
  region: Region;
  indicators: Record<string, ObservationResponse[]>;
}


// ======================================================
// CYCLE ANALYSIS
// ======================================================

export interface CycleEvidence {
  method: string;
  period_years: number;
  power: number;
}

export interface RobustCycle {
  period_years: number;
  score: number;
  confidence: string;
  methods: string[];
  method_count: number;
  method_coverage: number;
  cycles_observable: number;
  period_dispersion: number;
  evidence: CycleEvidence[];
}

export interface CycleAnalysisResult {
  start_date: string;
  end_date: string;
  observations: number;
  growth_observations: number;

  growth: Record<string, unknown>;
  hp: Record<string, unknown>;
  linear_detrend: Record<string, unknown>;

  robust_cycles: RobustCycle[];
}

export interface FeatureValues {
  value: number;

  rolling_mean: number | null;
  rolling_median: number | null;
  rolling_min: number | null;
  rolling_max: number | null;
  rolling_percentile: number | null;
  rolling_zscore: number | null;

  distance_from_rolling_mean: number | null;
  distance_from_max: number | null;
  distance_from_min: number | null;

  log_difference?: number | null;
  percentage_change?: number | null;
  cumulative_growth?: number | null;
  change?: number | null;
  yoy_change?: number | null;
  momentum: number | null;
  yoy_growth?: number | null;
  yoy_log_growth?: number | null;

  rolling_slope_short: number | null;
  rolling_slope_medium: number | null;
  rolling_slope_long: number | null;
  acceleration: number | null;
  slope_change: number | null;
  trend_change: number | null;

  rolling_std: number | null;
  rolling_volatility: number | null;
  rolling_range: number | null;
  volatility_change: number | null;
  volatility_zscore: number | null;

  zscore: number | null;
  percentile: number | null;
  drawdown: number | null;
}

export type FeatureKey = keyof FeatureValues;

export interface FeatureObservation {
  date: string;
  features: FeatureValues;
}

export interface FeatureAnalysisResult {
  indicator_code: string;
  region_code: string;
  observations: FeatureObservation[];
}

export interface InvestmentAnalysisResult {
  indicator?: string;
  region?: string;
  date?: string;

  regime: string;

  overall: {
    assessment: string;
    score: number;
    macro_bias: string;
    direction?: string;
    conviction: string;
    environment: string;
    risk: string;
    opportunity: string;
    confidence: string;
  };

  environment: {
    state: string;
    score: number;
    reasons: string[];
  };

  risk: {
    state: string;
    score: number;
    reasons: string[];
  };

  opportunity: {
    state: string;
    score: number;
    reasons: string[];
  };

  macro_bias: {
    state: string;
    score: number;
    reasons: string[];
  };

  transition: {
    detected: boolean;
    direction: string;
    strength: string;
    score: number;
  };

  horizon: {
    short_term: string;
    medium_term: string;
    long_term: string;
  };

  conviction: {
    state: string;
    score: number;
    reasons: string[];
  };

  alerts: string[];

  signals: Record<string, boolean | number | string | null>;

  confidence: {
    state?: string;
    score: number;
    reasons?: string[];
  };
}

export interface AssetScore {
  asset: string;
  name: string;
  asset_class: string;
  asset_type: string;
  region: string | null;
  score: number;
  contributions: Record<string, number>;
}

export interface InvestmentAssetRankingResult {
  region: string;
  date: string;
  asset_scores: AssetScore[];
}

export type Mode = "timeline" | "compare";