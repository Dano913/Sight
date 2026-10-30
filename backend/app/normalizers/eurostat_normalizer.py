from __future__ import annotations

from datetime import date
import math

from app.models.observation import Observation
from app.services.catalog.indicator_service import IndicatorService
from app.services.catalog.region_service import RegionService
from app.services.catalog.source_service import SourceService


class EurostatNormalizer:

    ANNUAL_INDICATORS = {
        "GDP",
        "INFLATION",
        "UNEMPLOYMENT",
        "EXPORTS_BY_COUNTRY",
        "IMPORTS_BY_COUNTRY",
        "TRADE_BALANCE_BY_COUNTRY",
    }

    QUARTERLY_INDICATORS = {
        "HOUSE_PRICE_INDEX",
    }

    QUARTER_MONTH = {
        "1": 1,
        "2": 4,
        "3": 7,
        "4": 10,
    }

    GEO_COLUMN_CANDIDATES = (
        "geo\\TIME_PERIOD",
        "geo\\time",
        "geo",
    )

    FILTERS = {
        "GDP": {
            "na_item": "B1G",
        },
        "INFLATION": {
            "coicop": "CP00",
            "unit": "RCH_A_AVG",
        },
        "CPI": {
            "coicop": "CP00",
            "unit": ["I05", "I15"],
        },
        "UNEMPLOYMENT": {
            "age": "Y15-74",
            "sex": "T",
        },
        "HOUSE_PRICE_INDEX": {
            "purchase": "TOTAL",
            "unit": "I15_Q",
        },
        "INDUSTRIAL_PRODUCTION": {
            "freq": "M",
            "indic_bt": "PRD",
            "nace_r2": "C",
            "s_adj": "SCA",
            "unit": "I21",
        },
        "RETAIL_SALES": {
            "unit": "I21",
        },
        "EXPORTS": {
            "freq": "M",
            "stk_flow": "EXP",
            "indic_et": "TRD_VAL",
            "partner": "EXT_EU27_2020",
            "sitc06": "TOTAL",
        },
        "IMPORTS": {
            "freq": "M",
            "stk_flow": "IMP",
            "indic_et": "TRD_VAL",
            "partner": "EXT_EU27_2020",
            "sitc06": "TOTAL",
        },
        "EXPORTS_BY_COUNTRY": {
            "partner": "WORLD",
            "indic_et": "MIO_EXP_VAL",
            "sitc06": "TOTAL",
        },
        "IMPORTS_BY_COUNTRY": {
            "partner": "WORLD",
            "indic_et": "MIO_IMP_VAL",
            "sitc06": "TOTAL",
        },
        "TRADE_BALANCE_BY_COUNTRY": {
            "partner": "WORLD",
            "indic_et": "MIO_BAL_VAL",
            "sitc06": "TOTAL",
        },
    }

    @staticmethod
    def _filter_dataframe(df, indicator_code: str):
        filters = EurostatNormalizer.FILTERS.get(indicator_code)

        if not filters:
            return df

        for column, expected_value in filters.items():
            if column not in df.columns:
                continue

            if isinstance(expected_value, list):
                df = df[df[column].isin(expected_value)]
            else:
                df = df[df[column] == expected_value]

        return df

    @staticmethod
    def _is_monthly_column(col_str: str) -> bool:
        if "-Q" in col_str:
            return False
        if "-" in col_str and len(col_str) == 7:
            year_str, month_str = col_str.split("-", 1)
            return (
                year_str.isdigit()
                and month_str.isdigit()
                and 1 <= int(month_str) <= 12
            )
        return False

    @staticmethod
    def _get_time_columns(df, indicator_code: str):
        if indicator_code in EurostatNormalizer.QUARTERLY_INDICATORS:
            return [
                column
                for column in df.columns
                if "-Q" in str(column)
            ]

        if indicator_code in EurostatNormalizer.ANNUAL_INDICATORS:
            return [
                column
                for column in df.columns
                if str(column).isdigit()
            ]

        return [
            column
            for column in df.columns
            if EurostatNormalizer._is_monthly_column(str(column))
            or str(column).isdigit()
        ]

    @staticmethod
    def _parse_date(
        period,
        indicator_code: str,
    ) -> date | None:
        period_str = str(period).strip()

        try:
            if "-Q" in period_str:
                year, quarter = period_str.split("-Q", 1)
                return date(
                    int(year),
                    EurostatNormalizer.QUARTER_MONTH[quarter],
                    1,
                )

            if "-" in period_str:
                year, month = period_str.split("-", 1)
                return date(
                    int(year),
                    int(month),
                    1,
                )

            if period_str.isdigit():
                return date(
                    int(period_str),
                    1,
                    1,
                )
        except (KeyError, TypeError, ValueError):
            return None

        return None

    @staticmethod
    def _get_regions():
        regions = RegionService.get_regions()

        return {
            region.code: region
            for region in regions
        }

    @staticmethod
    def _is_valid_value(value) -> bool:
        if value is None:
            return False

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return False

        return math.isfinite(numeric)

    @staticmethod
    def _resolve_geo_column(df) -> str | None:
        for candidate in EurostatNormalizer.GEO_COLUMN_CANDIDATES:
            if candidate in df.columns:
                return candidate
        return None

    @staticmethod
    def to_observations(
        df,
        indicator_code: str,
        source_code: str,
    ) -> list[Observation]:
        """
        Convierte un DataFrame de Eurostat en una lista de Observation.
        """
        if df is None or getattr(df, "empty", True):
            return []

        clean_indicator = indicator_code.strip().upper()

        df = EurostatNormalizer._filter_dataframe(
            df,
            clean_indicator,
        )

        if df.empty:
            return []

        geo_column = EurostatNormalizer._resolve_geo_column(df)
        if geo_column is None:
            return []

        time_columns = EurostatNormalizer._get_time_columns(
            df,
            clean_indicator,
        )

        region_map = EurostatNormalizer._get_regions()
        indicator = IndicatorService.get_indicator(clean_indicator)
        source = SourceService.get_by_code(source_code)

        observations: list[Observation] = []

        for _, row in df.iterrows():
            region_code = row.get(geo_column)
            region = region_map.get(region_code)

            if region is None:
                continue

            for period in time_columns:
                value = row[period]

                if not EurostatNormalizer._is_valid_value(value):
                    continue

                observation_date = EurostatNormalizer._parse_date(
                    period,
                    clean_indicator,
                )

                if observation_date is None:
                    continue

                observations.append(
                    Observation(
                        region=region,
                        indicator=indicator,
                        source=source,
                        date=observation_date,
                        value=float(value),
                    )
                )

        return observations
