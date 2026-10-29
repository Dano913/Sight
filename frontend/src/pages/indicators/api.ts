import client from "../../api/client";

import type {
  CycleAnalysisResult,
  FeatureAnalysisResult,
  InvestmentAnalysisResult,
  InvestmentAssetRankingResult,
} from "./types";

export async function fetchIndicator(code: string) {
  const { data } = await client.get(`/indicators/${code}`);

  return data;
}

export async function fetchRegions() {
  const { data } = await client.get("/regions");

  return data;
}

export async function fetchTimeline(
  regionCode: string,
  indicatorCode: string,
) {
  const { data } = await client.get(
    `/query/region/${regionCode}/indicator/${indicatorCode}`,
  );

  return data;
}

export async function fetchComparison(
  indicatorCode: string,
  regions: string[],
) {
  const { data } = await client.get("/query/compare", {
    params: {
      indicator: indicatorCode,
      regions: regions.join(","),
    },
  });

  return data;
}

export async function fetchCycleAnalysis(
  indicatorCode: string,
  regionCode: string,
): Promise<CycleAnalysisResult> {
  const { data } = await client.get<CycleAnalysisResult>(
    `/analysis/cycle/${indicatorCode}/${regionCode}`,
  );

  return data;
}

export async function fetchFeatures(
  indicatorCode: string,
  regionCode: string,
) {
  const { data } = await client.get(
    `/analysis/features/${indicatorCode}/${regionCode}`,
  );

  return data;
}

export async function fetchFeatureAnalysis(
  indicatorCode: string,
  regionCode: string,
): Promise<FeatureAnalysisResult> {
  const { data } = await client.get<FeatureAnalysisResult>(
    `/analysis/features/${indicatorCode}/${regionCode}`,
  );

  return data;
}

export async function getInvestmentAnalysis(
  indicatorCode: string,
  regionCode: string,
): Promise<InvestmentAnalysisResult> {
  const { data } = await client.get<InvestmentAnalysisResult>(
    `/analysis/investment/${indicatorCode}/${regionCode}`,
  );

  return data;
}

export async function fetchInvestmentAssetRanking(
  regionCode: string,
): Promise<InvestmentAssetRankingResult> {
  const { data } = await client.get<InvestmentAssetRankingResult>(
    `/investment/${regionCode}`,
  );

  return data;
}