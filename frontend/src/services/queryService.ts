import api from "../api/client";

export async function getIndicator(indicator: string) {
    const url = `/query/indicator/${indicator}`;

    const response = await api.get(url);

    console.log(
        "GET",
        `${api.defaults.baseURL}${url}`
    );

    return response.data;
}

export async function getRegion(region: string) {
    const response = await api.get(
        `/query/region/${region}`
    );

    return response.data;
}

export async function compareRegions(
    indicator: string,
    regions: string[]
) {
    const response = await api.get(
        "/query/compare",
        {
            params: {
                indicator,
                regions: regions.join(","),
            },
        }
    );

    return response.data;
}

export async function getRegions() {
    const response = await api.get("/regions/");

    return response.data;
}