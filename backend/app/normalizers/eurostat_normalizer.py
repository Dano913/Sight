from datetime import date

from app.models.observation import Observation
from app.services.catalog.region_service import RegionService
from app.services.catalog.indicator_service import IndicatorService
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
        filters = EurostatNormalizer.FILTERS.get(
            indicator_code
        )

        if not filters:
            return df

        for column, expected_value in filters.items():
            if isinstance(expected_value, list):
                df = df[
                    df[column].isin(expected_value)
                ]
            else:
                df = df[
                    df[column] == expected_value
                ]

        return df

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
            if (
                (
                    "-" in str(column)
                    and len(str(column)) == 7
                )
                or str(column).isdigit()
            )
        ]

    @staticmethod
    def _parse_date(
        period,
        indicator_code: str,
    ) -> date:

        period = str(period)

        if indicator_code in EurostatNormalizer.ANNUAL_INDICATORS:
            return date(
                int(period),
                1,
                1,
            )

        if indicator_code in EurostatNormalizer.QUARTERLY_INDICATORS:
            year, quarter = period.split("-Q")

            quarter_month = {
                "1": 1,
                "2": 4,
                "3": 7,
                "4": 10,
            }

            return date(
                int(year),
                quarter_month[quarter],
                1,
            )

        year, month = period.split("-")

        return date(
            int(year),
            int(month),
            1,
        )

    @staticmethod
    def _get_regions():
        regions = RegionService.get_regions()

        return {
            region.code: region
            for region in regions
        }

    @staticmethod
    def _is_valid_value(value):
        if value is None:
            return False

        return value == value

    @staticmethod
    def to_observations(
        df,
        indicator_code: str,
        source_code: str,
    ):
        """
        Convierte un DataFrame de Eurostat
        en una lista de Observation.
        """

        df = EurostatNormalizer._filter_dataframe(
            df,
            indicator_code,
        )

        time_columns = EurostatNormalizer._get_time_columns(
            df,
            indicator_code,
        )

        region_map = EurostatNormalizer._get_regions()

        indicator = IndicatorService.get_indicator(
            indicator_code
        )

        source = SourceService.get_by_code(
            source_code
        )

        observations = []

        for _, row in df.iterrows():
            region_code = row["geo\\TIME_PERIOD"]

            region = region_map.get(region_code)

            if region is None:
                continue

            for period in time_columns:
                value = row[period]

                if not EurostatNormalizer._is_valid_value(
                    value
                ):
                    continue

                observation_date = (
                    EurostatNormalizer._parse_date(
                        period,
                        indicator_code,
                    )
                )

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