import api from "../api/client";

import type { MacroRegimeData } from "../components/analysis/MacroRegime";

export async function getIndicator(
    indicator: string,
    signal?: AbortSignal
) {
    const response = await api.get(
        `/query/indicator/${indicator}`,
        { signal }
    );

    return response.data;
}

export async function getRegion(
    region: string,
    signal?: AbortSignal
) {
    const response = await api.get(
        `/query/region/${region}`,
        { signal }
    );

    return response.data;
}

export async function compareRegions(
    indicator: string,
    regions: string[],
    signal?: AbortSignal
) {
    const response = await api.get(
        "/query/compare",
        {
            params: {
                indicator,
                regions: regions.join(","),
            },
            signal,
        }
    );

    return response.data;
}

export async function getRegions(signal?: AbortSignal) {
    const response = await api.get("/regions/", { signal });

    return response.data;
}

export async function getMacroRegime(
    region: string,
    signal?: AbortSignal
): Promise<MacroRegimeData | null> {
    const response = await api.get<{ macro_regime?: MacroRegimeData | null }>(
        `/analysis/regime/${region}`,
        { signal }
    );

    return response.data.macro_regime ?? null;
}
