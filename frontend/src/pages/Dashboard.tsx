import { useState } from "react";

import {
    getRegions,
    getRegion,
    getMacroRegime,
} from "../services/queryService";

import { useAsyncData } from "../hooks/useAsyncData";

import MacroLineChart from "../components/charts/MacroLineChart";

import MacroRegime, {
    type MacroRegimeData,
} from "../components/analysis/MacroRegime";


type Region = {
    id: number;
    code: string;
    name: string;
    region_type: string;
};


type Observation = {
    date: string;
    value: number;
    source: string;
};


type RegionData = {
    region: Region;
    indicators: {
        GDP?: Observation[];
        INFLATION?: Observation[];
        UNEMPLOYMENT?: Observation[];
    };
};

const EMPTY_REGIONS: Region[] = [];


export default function Dashboard() {

    const [selectedRegion, setSelectedRegion] =
        useState("EU27_2020");

    const regionsResult = useAsyncData<Region[]>(
        "dashboard-regions",
        getRegions
    );

    const dashboardDataResult = useAsyncData<{
        regionData: RegionData;
        macroRegime: MacroRegimeData | null;
    }>(
        selectedRegion || null,
        async (signal) => {
            const [regionData, macroRegime] = await Promise.all([
                getRegion(selectedRegion, signal),
                getMacroRegime(selectedRegion, signal),
            ]);

            return { regionData, macroRegime };
        }
    );

    const regions = regionsResult.data ?? EMPTY_REGIONS;
    const loadingRegions = regionsResult.loading;
    const loadingData = dashboardDataResult.loading;
    const regionData = dashboardDataResult.data?.regionData ?? null;
    const macroRegime = dashboardDataResult.data?.macroRegime ?? null;


    /*
     * LOADING REGIONS
     */

    if (loadingRegions) {

        return (
            <div
                style={{
                    padding: 24,
                    color: "#64748b",
                }}
            >
                Loading regions...
            </div>
        );

    }


    const region =
        regionData?.region;


    const gdp =
        regionData?.indicators?.GDP ?? [];


    const inflation =
        regionData?.indicators?.INFLATION ?? [];


    const unemployment =
        regionData?.indicators?.UNEMPLOYMENT ?? [];


    const latestGDP =
        gdp[gdp.length - 1];


    const latestInflation =
        inflation[inflation.length - 1];


    const latestUnemployment =
        unemployment[
            unemployment.length - 1
        ];


    return (

        <div>

            {/* HEADER */}

            <div
                style={{
                    marginBottom: 28,
                }}
            >

                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent:
                            "space-between",
                        gap: 20,
                        marginBottom: 8,
                    }}
                >

                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 10,
                        }}
                    >

                        <h1
                            style={{
                                margin: 0,
                                fontSize: 24,
                                fontWeight: 700,
                                color: "#0f172a",
                                letterSpacing:
                                    "-0.025em",
                            }}
                        >
                            Macroeconomic Dashboard
                        </h1>


                        <span
                            style={{
                                padding:
                                    "2px 10px",
                                background:
                                    "#eff6ff",
                                borderRadius: 20,
                                fontSize: 11,
                                fontWeight: 700,
                                color: "#2563eb",
                                letterSpacing:
                                    "0.04em",
                            }}
                        >
                            LIVE
                        </span>

                    </div>


                    {/* REGION SELECTOR */}

                    <select
                        value={selectedRegion}
                        onChange={(event) =>
                            setSelectedRegion(
                                event.target.value
                            )
                        }
                        style={{
                            minWidth: 190,
                            padding:
                                "8px 12px",
                            border:
                                "1px solid #cbd5e1",
                            borderRadius: 8,
                            background:
                                "#ffffff",
                            color: "#0f172a",
                            fontSize: 13,
                            fontWeight: 600,
                            cursor: "pointer",
                            outline: "none",
                        }}
                    >

                        {regions.map(
                            (item) => (

                                <option
                                    key={item.id}
                                    value={
                                        item.code
                                    }
                                >
                                    {item.name}
                                </option>

                            )
                        )}

                    </select>

                </div>


                <p
                    style={{
                        margin: 0,
                        fontSize: 14,
                        color: "#64748b",
                    }}
                >
                    Explore macroeconomic
                    indicators and the current
                    macro regime for{" "}

                    <strong>
                        {region?.name ??
                            "European Union"}
                    </strong>.
                </p>

            </div>


            {/* MACRO REGIME */}

            {loadingData ? (

                <div
                    style={{
                        background:
                            "#ffffff",
                        border:
                            "1px solid #e2e8f0",
                        borderRadius: 12,
                        padding: 24,
                        marginBottom: 24,
                        color: "#64748b",
                        fontSize: 13,
                    }}
                >
                    Loading Macro Regime...
                </div>

            ) : macroRegime ? (

                <div
                    style={{
                        marginBottom: 24,
                    }}
                >

                    <MacroRegime
                        data={macroRegime}
                    />

                </div>

            ) : null}


            {/* INDICATOR CARDS */}

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "repeat(3, minmax(0, 1fr))",
                    gap: 16,
                    marginBottom: 24,
                }}
            >


                {/* GDP */}

                <div
                    style={{
                        background:
                            "#ffffff",
                        border:
                            "1px solid #e2e8f0",
                        borderRadius: 12,
                        padding: 20,
                    }}
                >

                    <div
                        style={{
                            fontSize: 12,
                            color: "#64748b",
                            marginBottom: 8,
                        }}
                    >
                        GDP
                    </div>


                    <div
                        style={{
                            fontSize: 24,
                            fontWeight: 700,
                            color: "#0f172a",
                        }}
                    >

                        {loadingData
                            ? "Loading..."
                            : latestGDP
                                ? latestGDP.value
                                    .toLocaleString(
                                        undefined,
                                        {
                                            maximumFractionDigits:
                                                1,
                                        }
                                    )
                                : "—"}

                    </div>


                    <div
                        style={{
                            marginTop: 6,
                            fontSize: 11,
                            color: "#94a3b8",
                        }}
                    >

                        {loadingData
                            ? "Loading..."
                            : latestGDP
                                ? latestGDP.date
                                    .substring(
                                        0,
                                        4
                                    )
                                : "No data"}

                    </div>

                </div>


                {/* INFLATION */}

                <div
                    style={{
                        background:
                            "#ffffff",
                        border:
                            "1px solid #e2e8f0",
                        borderRadius: 12,
                        padding: 20,
                    }}
                >

                    <div
                        style={{
                            fontSize: 12,
                            color: "#64748b",
                            marginBottom: 8,
                        }}
                    >
                        Inflation
                    </div>


                    <div
                        style={{
                            fontSize: 24,
                            fontWeight: 700,
                            color: "#0f172a",
                        }}
                    >

                        {loadingData
                            ? "Loading..."
                            : latestInflation
                                ? `${latestInflation.value.toFixed(1)}%`
                                : "—"}

                    </div>


                    <div
                        style={{
                            marginTop: 6,
                            fontSize: 11,
                            color: "#94a3b8",
                        }}
                    >

                        {loadingData
                            ? "Loading..."
                            : latestInflation
                                ? latestInflation.date
                                    .substring(
                                        0,
                                        4
                                    )
                                : "No data"}

                    </div>

                </div>


                {/* UNEMPLOYMENT */}

                <div
                    style={{
                        background:
                            "#ffffff",
                        border:
                            "1px solid #e2e8f0",
                        borderRadius: 12,
                        padding: 20,
                    }}
                >

                    <div
                        style={{
                            fontSize: 12,
                            color: "#64748b",
                            marginBottom: 8,
                        }}
                    >
                        Unemployment
                    </div>


                    <div
                        style={{
                            fontSize: 24,
                            fontWeight: 700,
                            color: "#0f172a",
                        }}
                    >

                        {loadingData
                            ? "Loading..."
                            : latestUnemployment
                                ? `${latestUnemployment.value.toFixed(1)}%`
                                : "—"}

                    </div>


                    <div
                        style={{
                            marginTop: 6,
                            fontSize: 11,
                            color: "#94a3b8",
                        }}
                    >

                        {loadingData
                            ? "Loading..."
                            : latestUnemployment
                                ? latestUnemployment.date
                                    .substring(
                                        0,
                                        4
                                    )
                                : "No data"}

                    </div>

                </div>

            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "1fr",
                    gap: 20,
                    marginTop: 24,
                }}
            >
                <MacroLineChart
                    title="GDP"
                    observations={gdp}
                />

                <MacroLineChart
                    title="Inflation"
                    observations={inflation}
                    unit="%"
                />

                <MacroLineChart
                    title="Unemployment"
                    observations={unemployment}
                    unit="%"
                />
            </div>


            {/* RESPONSIVE */}

            <style>{`

                @media (max-width: 900px) {

                    .dashboard-indicators {
                        grid-template-columns:
                            1fr !important;
                    }

                }

                @media (max-width: 700px) {

                    select {
                        min-width: 150px;
                    }

                }

            `}</style>

        </div>

    );

}