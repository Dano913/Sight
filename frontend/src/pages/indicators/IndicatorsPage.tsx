import { useState } from "react";

import PageHeader from "../../layout/PageHeader";
import IndicatorSearch from "../../components/indicators/IndicatorSearch.tsx";
import IndicatorGrid from "../../components/indicators/IndicatorGrid";

export default function IndicatorsPage() {

    const [search, setSearch] = useState("");

    return (
        <>
            <PageHeader
                title="Indicators"
                subtitle="Explore and discover available macroeconomic indicators."
            />

            <IndicatorSearch 
                value={search}
                onChange={setSearch}
            />

            <IndicatorGrid 
                search={search} 
            />
        </>
    );
}