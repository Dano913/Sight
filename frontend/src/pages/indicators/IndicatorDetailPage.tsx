import { useState } from "react";

import { useParams } from "react-router-dom";

import type { Region, Mode } from "./types.ts";

import { useAsyncData } from "../../hooks/useAsyncData";

import {
  fetchIndicator,
  fetchRegions,
  fetchCycleAnalysis,
  fetchFeatureAnalysis,
  getInvestmentAnalysis,
  fetchInvestmentAssetRanking,
  resolveIndicatorCode,
} from "./api";

import ModeSelector from "../../components/selectors/ModeSelector.tsx";

import TimelineView from "./views/TimelineView";

import CompareView from "./views/CompareView";

import CycleAnalysis from "../../components/analysis/CycleAnalysis";

import { FeatureAnalysis } from "../../components/analysis/FutureAnalysis";

import InvestmentThesis from "../../components/analysis/InvestmentThesis";

import AssetRanking from "../../components/analysis/AssetRanking";

const EMPTY_REGIONS: Region[] = [];

export default function IndicatorDetailPage() {
  const { code } = useParams();

  const [mode, setMode] = useState<Mode>("timeline");

  // Región elegida por el usuario. Mientras sea null se usa la
  // primera región disponible (valor derivado, sin efectos).
  const [userRegion, setUserRegion] = useState<string | null>(null);

  // =====================================================
  // CARGAR INDICADOR + REGIONES
  // =====================================================

  const indicatorResult = useAsyncData(code ?? null, (signal) =>
    fetchIndicator(code!, signal),
  );

  const regionsResult = useAsyncData("regions", fetchRegions);

  const indicator = indicatorResult.data;
  const regions = regionsResult.data ?? EMPTY_REGIONS;
  const loading = indicatorResult.loading || regionsResult.loading;

  const selectedRegion = userRegion ?? regions[0]?.code ?? null;

  const effectiveCode =
    code && selectedRegion
      ? resolveIndicatorCode(code, selectedRegion)
      : null;

  // Clave compartida por los análisis que dependen de indicador efectivo + región.
  const analysisKey =
    effectiveCode && selectedRegion
      ? `${effectiveCode}|${selectedRegion}`
      : null;

  // =====================================================
  // FEATURE ANALYSIS
  // =====================================================

  const featureResult = useAsyncData(analysisKey, (signal) =>
    fetchFeatureAnalysis(effectiveCode!, selectedRegion!, signal),
  );

  // =====================================================
  // INVESTMENT ANALYSIS
  // =====================================================

  const investmentResult = useAsyncData(analysisKey, (signal) =>
    getInvestmentAnalysis(effectiveCode!, selectedRegion!, signal),
  );

  // =====================================================
  // INVESTMENT ASSET RANKING
  // =====================================================

  const assetRankingResult = useAsyncData(selectedRegion, (signal) =>
    fetchInvestmentAssetRanking(selectedRegion!, signal),
  );

  // =====================================================
  // CYCLE ANALYSIS
  // =====================================================

  const cycleResult = useAsyncData(analysisKey, (signal) =>
    fetchCycleAnalysis(effectiveCode!, selectedRegion!, signal),
  );

  const featureAnalysis = featureResult.data;
  const featureLoading = featureResult.loading;
  const investmentAnalysis = investmentResult.data;
  const investmentLoading = investmentResult.loading;
  const investmentAssetRanking = assetRankingResult.data;
  const investmentAssetLoading = assetRankingResult.loading;
  const cycleAnalysis = cycleResult.data;
  const cycleLoading = cycleResult.loading;

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#1b2a39] text-white">
        Loading...
      </div>
    );
  }

  // =====================================================
  // RENDER
  // =====================================================

  return (
    <div className="min-h-screen bg-[#1b2a39] p-4">
      {/* HEADER */}

      <section className="flex min-h-[70px] items-center justify-between rounded-xl border border-[#32485f] bg-[#223548] px-4 py-3">
        <div className="flex w-full items-center justify-between gap-6">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-400">
              <span>{indicator?.category?.name}</span>

              <span className="text-slate-600">•</span>

              <span>{indicator?.code}</span>

              <span className="text-slate-600">•</span>

              <span>{indicator?.frequency}</span>

              <span className="text-slate-600">•</span>

              <span>{indicator?.unit}</span>
            </div>
          </div>

          <ModeSelector
            mode={mode}
            onChange={setMode}
          />
        </div>
      </section>

      {/* CONTENIDO */}

      <div className="mt-6">
        {mode === "timeline" && code && (
          <div className="space-y-6">
            <TimelineView
              code={code}
              indicator={indicator}
              regions={regions}
              selectedRegion={selectedRegion}
              onRegionChange={setUserRegion}
            />

            {/* FEATURE ANALYSIS */}

            {featureLoading && (
              <div className="rounded-xl border border-[#32485f] bg-[#223548] p-5 text-sm text-slate-300">
                Cargando Feature Analysis...
              </div>
            )}

            {!featureLoading && !featureAnalysis && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-5 text-sm text-red-300">
                No se pudo cargar Feature Analysis.
              </div>
            )}

            {featureAnalysis && (
              <FeatureAnalysis data={featureAnalysis} />
            )}

            {/* CYCLE ANALYSIS */}

            <CycleAnalysis
              analysis={cycleAnalysis}
              loading={cycleLoading}
            />

            {/* INVESTMENT THESIS */}

            {investmentLoading && (
              <div className="rounded-xl border border-[#32485f] bg-[#223548] p-5 text-sm text-slate-300">
                Cargando tesis de inversión...
              </div>
            )}

            {!investmentLoading && !investmentAnalysis && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-5 text-sm text-red-300">
                No se pudo cargar la tesis de inversión.
              </div>
            )}

            {investmentAnalysis && (
              <InvestmentThesis
                analysis={investmentAnalysis}
              />
            )}

            {/* ASSET RANKING */}

            <AssetRanking
              assets={
                investmentAssetRanking?.asset_scores ?? []
              }
              loading={investmentAssetLoading}
            />
          </div>
        )}

        {mode === "compare" && code && (
          <CompareView
            key={code}
            code={code}
            indicator={indicator}
          />
        )}
      </div>
    </div>
  );
}