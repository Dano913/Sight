import { useEffect, useState } from "react";

import { useParams } from "react-router-dom";

import type {
  Indicator,
  Region,
  Mode,
  CycleAnalysisResult,
  FeatureAnalysisResult,
  InvestmentAnalysisResult,
  InvestmentAssetRankingResult,
} from "./types.ts";

import {
  fetchIndicator,
  fetchRegions,
  fetchCycleAnalysis,
  fetchFeatureAnalysis,
  getInvestmentAnalysis,
  fetchInvestmentAssetRanking,
} from "./api";

import ModeSelector from "../../components/selectors/ModeSelector.tsx";

import TimelineView from "./views/TimelineView";

import CompareView from "./views/CompareView";

import CycleAnalysis from "../../components/analysis/CycleAnalysis";

import { FeatureAnalysis } from "../../components/analysis/FutureAnalysis";

import InvestmentThesis from "../../components/analysis/InvestmentThesis";

import AssetRanking from "../../components/analysis/AssetRanking";

export default function IndicatorDetailPage() {
  const { code } = useParams();

  const [indicator, setIndicator] = useState<Indicator | null>(null);

  const [regions, setRegions] = useState<Region[]>([]);

  const [mode, setMode] = useState<Mode>("timeline");

  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);

  const [cycleAnalysis, setCycleAnalysis] =
    useState<CycleAnalysisResult | null>(null);

  const [cycleLoading, setCycleLoading] = useState(false);

  const [featureAnalysis, setFeatureAnalysis] =
    useState<FeatureAnalysisResult | null>(null);

  const [featureLoading, setFeatureLoading] = useState(false);

  const [investmentAnalysis, setInvestmentAnalysis] =
    useState<InvestmentAnalysisResult | null>(null);

  const [investmentLoading, setInvestmentLoading] = useState(false);

  const [investmentAssetRanking, setInvestmentAssetRanking] =
    useState<InvestmentAssetRankingResult | null>(null);

  const [investmentAssetLoading, setInvestmentAssetLoading] =
    useState(false);

  // =====================================================
  // CARGAR INDICADOR + REGIONES
  // =====================================================

  useEffect(() => {
    loadPage();
  }, [code]);

  async function loadPage() {
    if (!code) return;

    try {
      setLoading(true);

      const [indicatorData, regionsData] = await Promise.all([
        fetchIndicator(code),
        fetchRegions(),
      ]);

      setIndicator(indicatorData);
      setRegions(regionsData);

      if (regionsData.length > 0) {
        setSelectedRegion(
          (current) => current ?? regionsData[0].code,
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // =====================================================
  // FEATURE ANALYSIS
  // =====================================================

  useEffect(() => {
    if (!code || !selectedRegion) {
      setFeatureAnalysis(null);
      return;
    }

    loadFeatureAnalysis(code, selectedRegion);
  }, [code, selectedRegion]);

  async function loadFeatureAnalysis(
    indicatorCode: string,
    regionCode: string,
  ) {
    try {
      setFeatureLoading(true);

      const data = await fetchFeatureAnalysis(
        indicatorCode,
        regionCode,
      );

      setFeatureAnalysis(data);
    } catch (error) {
      console.error(
        `Error cargando features para ${regionCode}:`,
        error,
      );

      setFeatureAnalysis(null);
    } finally {
      setFeatureLoading(false);
    }
  }

  // =====================================================
  // INVESTMENT ANALYSIS
  // =====================================================

  useEffect(() => {
    if (!code || !selectedRegion) {
      setInvestmentAnalysis(null);
      return;
    }

    loadInvestmentAnalysis(code, selectedRegion);
  }, [code, selectedRegion]);

  async function loadInvestmentAnalysis(
    indicatorCode: string,
    regionCode: string,
  ) {
    try {
      setInvestmentLoading(true);

      const data = await getInvestmentAnalysis(
        indicatorCode,
        regionCode,
      );

      setInvestmentAnalysis(data);
    } catch (error) {
      console.error(
        `Error cargando tesis de inversión para ${regionCode}:`,
        error,
      );

      setInvestmentAnalysis(null);
    } finally {
      setInvestmentLoading(false);
    }
  }

  // =====================================================
  // INVESTMENT ASSET RANKING
  // =====================================================

  useEffect(() => {
    if (!selectedRegion) {
      setInvestmentAssetRanking(null);
      return;
    }

    loadInvestmentAssetRanking(selectedRegion);
  }, [selectedRegion]);

  async function loadInvestmentAssetRanking(
    regionCode: string,
  ) {
    try {
      setInvestmentAssetLoading(true);

      const data = await fetchInvestmentAssetRanking(
        regionCode,
      );

      setInvestmentAssetRanking(data);
    } catch (error) {
      console.error(
        `Error cargando ranking de activos para ${regionCode}:`,
        error,
      );

      setInvestmentAssetRanking(null);
    } finally {
      setInvestmentAssetLoading(false);
    }
  }

  // =====================================================
  // CYCLE ANALYSIS
  // =====================================================

  useEffect(() => {
    if (!code || !selectedRegion) {
      setCycleAnalysis(null);
      return;
    }

    loadCycleAnalysis(code, selectedRegion);
  }, [code, selectedRegion]);

  async function loadCycleAnalysis(
    indicatorCode: string,
    regionCode: string,
  ) {
    try {
      setCycleLoading(true);

      const cycleData = await fetchCycleAnalysis(
        indicatorCode,
        regionCode,
      );

      setCycleAnalysis(cycleData);
    } catch (error) {
      console.error(
        `Error cargando análisis de ciclo para ${regionCode}:`,
        error,
      );

      setCycleAnalysis(null);
    } finally {
      setCycleLoading(false);
    }
  }

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
              onRegionChange={setSelectedRegion}
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
            code={code}
            indicator={indicator}
          />
        )}
      </div>
    </div>
  );
}