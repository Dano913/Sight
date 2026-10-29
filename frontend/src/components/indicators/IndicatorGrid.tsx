import IndicatorCard from "./IndicatorCard";

interface IndicatorGridProps {
  search: string;
}

const indicators = [
  {
    code: "GDP",
    name: "Gross Domestic Product",
    category: "Economic Growth",
  },
  {
    code: "INFLATION",
    name: "Inflation",
    category: "Prices",
  },
  {
    code: "CPI",
    name: "Consumer Price Index",
    category: "Prices",
  },
  {
    code: "UNEMPLOYMENT",
    name: "Unemployment",
    category: "Labour Market",
  },
  {
    code: "INTEREST_RATE",
    name: "Interest Rate",
    category: "Monetary Policy",
  },
  {
    code: "HOUSE_PRICE_INDEX",
    name: "House Price Index",
    category: "Housing",
  },
  {
    code: "INDUSTRIAL_PRODUCTION",
    name: "Industrial Production",
    category: "Industry",
  },
  {
    code: "RETAIL_SALES",
    name: "Retail Sales",
    category: "Consumption",
  },
  {
    code: "EXPORTS",
    name: "Exports",
    category: "Trade",
  },
  {
    code: "IMPORTS",
    name: "Imports",
    category: "Trade",
  },
  { 
    code: "TRADE", 
    name: "Trade Balance", 
    category: "Trade", 
  },
];

export default function IndicatorGrid({ search }: IndicatorGridProps) {
  const filteredIndicators = indicators.filter((indicator) =>
    `${indicator.code} ${indicator.name}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
        gap: "1.5rem",
      }}
    >
      {filteredIndicators.map((indicator) => (
        <IndicatorCard
          key={indicator.code}
          indicator={indicator}
        />
      ))}
    </div>
  );
}