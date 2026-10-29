import pandas as pd

from app.services.analysis.analysis_service import AnalysisService


def main():

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    features = AnalysisService.get_features(
        indicator_code="GDP",
        region_code="ES",
    )

    print("\n==============================")
    print("ANALYSIS SERVICE")
    print("==============================")

    print("Shape:", features.shape)

    print("\nColumns:")

    for column in features.columns:
        print(" -", column)

    print("\nNúmero de features:", len(features.columns))

    print("\nÚltimas observaciones:")

    print(features.tail())

    print("\n==============================")
    print("FEATURES POR FAMILIA")
    print("==============================")

    families = {
        "LEVEL": [
            "value",
            "rolling_mean",
            "rolling_median",
            "rolling_min",
            "rolling_max",
            "rolling_percentile",
            "rolling_zscore",
            "distance_from_rolling_mean",
        ],
        "GROWTH": [
            "log_difference",
            "percentage_change",
            "cumulative_growth",
            "momentum",
            "yoy_growth",
            "yoy_log_growth",
        ],
        "TREND": [
            "rolling_slope_short",
            "rolling_slope_medium",
            "rolling_slope_long",
            "acceleration",
            "slope_change",
            "trend_change",
        ],
        "VOLATILITY": [
            "rolling_std",
            "rolling_volatility",
            "rolling_range",
            "volatility_change",
            "volatility_zscore",
        ],
        "EXTREME": [
            "zscore",
            "percentile",
            "distance_from_max",
            "distance_from_min",
            "drawdown",
        ],
    }

    for family, expected_features in families.items():

        existing = [
            feature
            for feature in expected_features
            if feature in features.columns
        ]

        missing = [
            feature
            for feature in expected_features
            if feature not in features.columns
        ]

        print(f"\n{family}:")
        print(f"  Encontrados: {len(existing)}")

        for feature in existing:
            print(f"   ✓ {feature}")

        if missing:
            print(f"  FALTAN: {len(missing)}")

            for feature in missing:
                print(f"   ✗ {feature}")

    print("\n==============================")
    print("RESUMEN")
    print("==============================")

    expected_total = sum(
        len(feature_list)
        for feature_list in families.values()
    )

    print("Features esperados:", expected_total)
    print("Features obtenidos:", len(features.columns))

    if len(features.columns) == expected_total:
        print("✓ Todos los features están presentes.")
    else:
        print("⚠ El número de features no coincide.")


if __name__ == "__main__":
    main()