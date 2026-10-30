import client from "../../api/client";

import type {
  Indicator,
  Region,
  RegionResponse,
  CycleAnalysisResult,
  FeatureAnalysisResult,
  InvestmentAnalysisResult,
  InvestmentAssetRankingResult,
} from "./types";

// Indicadores que tienen una variante "por país" en estados miembros UE
// distinta de su variante agregada EU27_2020 / US
const BY_COUNTRY_MAP: Record<string, string> = {
  EXPORTS: "EXPORTS_BY_COUNTRY",
  IMPORTS: "IMPORTS_BY_COUNTRY",
  TRADE: "TRADE_BALANCE_BY_COUNTRY",
};

export function resolveIndicatorCode(
  baseCode: string,
  regionCode: string,
): string {
  if (regionCode === "EU27_2020" || regionCode === "US") {
    return baseCode;
  }

  return BY_COUNTRY_MAP[baseCode] ?? baseCode;
}

export async function fetchIndicator(
  code: string,
  signal?: AbortSignal,
): Promise<Indicator> {
  const { data } = await client.get<Indicator>(`/indicators/${code}`, {
    signal,
  });

  return data;
}

export async function fetchRegions(
  signal?: AbortSignal,
): Promise<Region[]> {
  const { data } = await client.get<Region[]>("/regions", { signal });

  return data;
}

export async function fetchTimeline(
  regionCode: string,
  indicatorCode: string,
  signal?: AbortSignal,
): Promise<RegionResponse> {
  const { data } = await client.get<RegionResponse>(
    `/query/region/${regionCode}/indicator/${indicatorCode}`,
    { signal },
  );

  return data;
}

export async function fetchComparison(
  indicatorCode: string,
  regions: string[],
  signal?: AbortSignal,
): Promise<RegionResponse[]> {
  const { data } = await client.get<RegionResponse[]>("/query/compare", {
    params: {
      indicator: indicatorCode,
      regions: regions.join(","),
    },
    signal,
  });

  return data;
}

export async function fetchCycleAnalysis(
  indicatorCode: string,
  regionCode: string,
  signal?: AbortSignal,
): Promise<CycleAnalysisResult> {
  const { data } = await client.get<CycleAnalysisResult>(
    `/analysis/cycle/${indicatorCode}/${regionCode}`,
    { signal },
  );

  return data;
}

export async function fetchFeatures(
  indicatorCode: string,
  regionCode: string,
  signal?: AbortSignal,
): Promise<FeatureAnalysisResult> {
  return fetchFeatureAnalysis(indicatorCode, regionCode, signal);
}

export async function fetchFeatureAnalysis(
  indicatorCode: string,
  regionCode: string,
  signal?: AbortSignal,
): Promise<FeatureAnalysisResult> {
  const { data } = await client.get<FeatureAnalysisResult>(
    `/analysis/features/${indicatorCode}/${regionCode}`,
    { signal },
  );

  return data;
}

export async function getInvestmentAnalysis(
  indicatorCode: string,
  regionCode: string,
  signal?: AbortSignal,
): Promise<InvestmentAnalysisResult> {
  const { data } = await client.get<InvestmentAnalysisResult>(
    `/analysis/investment/${indicatorCode}/${regionCode}`,
    { signal },
  );

  return data;
}

export async function fetchInvestmentAssetRanking(
  regionCode: string,
  signal?: AbortSignal,
): Promise<InvestmentAssetRankingResult> {
  const { data } = await client.get<InvestmentAssetRankingResult>(
    `/investment/${regionCode}`,
    { signal },
  );

  return data;
}
