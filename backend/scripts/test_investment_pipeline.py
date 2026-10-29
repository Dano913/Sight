import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.catalog.observation_service import ObservationService
from app.services.analysis.analysis_service import AnalysisService


codes = [
    "GDP",
    "INFLATION",
    "UNEMPLOYMENT",
    "INDUSTRIAL_PRODUCTION",
    "RETAIL_SALES",
    "HOUSE_PRICE_INDEX",
]

observations = []

for code in codes:
    observations.extend(
        ObservationService.get_observations(
            indicator_code=code,
            region_code="ES",
        )
    )

result = AnalysisService.analyze_multiple(observations)

assert result["region"] == "ES"
assert result["macro_factor_scores"]
assert result["asset_scores"]

print("\n=== MACRO FACTORS ===")
for factor, score in result["macro_factor_scores"].items():
    print(f"{factor:<25} {score:>6.2f}")

print("\n=== ASSET RANKING ===")
for index, asset in enumerate(result["asset_scores"], start=1):
    print(
        f"{index:>2}. "
        f"{asset['asset']:<25} "
        f"{asset['score']:>7.2f}"
    )

print("\n=== TOP 3 ===")
for asset in result["asset_scores"][:3]:
    print(f"{asset['asset']}: {asset['score']:.2f}")

print("\nTEST OK")