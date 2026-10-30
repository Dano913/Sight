from __future__ import annotations

import eurostat
import pandas as pd


class EurostatClient:

    EU_COUNTRIES = [
        "EU27_2020",
        "DE",
        "FR",
        "IT",
        "ES",
        "NL",
        "PL",
        "BE",
        "SE",
        "AT",
        "IE",
        "DK",
        "FI",
        "CZ",
        "PT",
    ]

    GDP_DATASET = "nama_10_gdp"
    INFLATION_DATASET = "prc_hicp_aind"
    CPI_DATASET = "prc_hicp_midx"
    UNEMPLOYMENT_DATASET = "une_rt_a"
    HOUSE_PRICE_INDEX_DATASET = "prc_hpi_q"
    INTEREST_RATE_DATASET = "ei_mfir_m"

    INDUSTRIAL_PRODUCTION_DATASET = "sts_inpr_m"
    RETAIL_SALES_DATASET = "sts_trtu_m"

    TRADE_BALANCE_DATASET = "ext_st_eu27_2020sitc"
    TRADE_BY_COUNTRY_DATASET = "ext_lt_intertrd"

    GOVERNMENT_DEBT_DATASET = "gov_10dd_edpt1"
    GOVERNMENT_DEFICIT_DATASET = "gov_10dd_edpt1"

    # ==========================================
    # GDP
    # ==========================================

    @staticmethod
    def get_gdp():
        df = eurostat.get_data_df(
            EurostatClient.GDP_DATASET,
            filter_pars={
                "geo": EurostatClient.EU_COUNTRIES,
                "na_item": "B1G",
                "unit": "CLV05_MEUR",
            },
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # INFLATION
    # ==========================================

    @staticmethod
    def get_inflation():
        df = eurostat.get_data_df(
            EurostatClient.INFLATION_DATASET,
            filter_pars={
                "geo": EurostatClient.EU_COUNTRIES,
                "coicop": "CP00",
                "unit": "RCH_A_AVG",
            },
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # CPI
    # ==========================================

    @staticmethod
    def get_cpi():
        df = eurostat.get_data_df(
            EurostatClient.CPI_DATASET
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # UNEMPLOYMENT
    # ==========================================

    @staticmethod
    def get_unemployment():
        df = eurostat.get_data_df(
            EurostatClient.UNEMPLOYMENT_DATASET,
            filter_pars={
                "geo": EurostatClient.EU_COUNTRIES,
                "unit": "PC_ACT",
                "age": "Y15-74",
                "sex": "T",
            },
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # HOUSE PRICE INDEX
    # ==========================================

    @staticmethod
    def get_house_price_index():
        df = eurostat.get_data_df(
            EurostatClient.HOUSE_PRICE_INDEX_DATASET
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # INTEREST RATE
    # ==========================================

    @staticmethod
    def get_interest_rate():
        df = eurostat.get_data_df(
            EurostatClient.INTEREST_RATE_DATASET
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # INDUSTRIAL PRODUCTION
    # ==========================================

    @staticmethod
    def get_industrial_production():
        df = eurostat.get_data_df(
            EurostatClient.INDUSTRIAL_PRODUCTION_DATASET,
            filter_pars={
                "geo": EurostatClient.EU_COUNTRIES,
                "freq": "M",
                "indic_bt": "PRD",
                "nace_r2": "C",
                "s_adj": "SCA",
                "unit": "I21",
            },
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # RETAIL SALES
    # ==========================================

    @staticmethod
    def get_retail_sales():
        df = eurostat.get_data_df(
            EurostatClient.RETAIL_SALES_DATASET,
            filter_pars={
                "freq": "M",
                "indic_bt": "VOL_SLS",
                "nace_r2": "G47",
                "s_adj": "SCA",
                "unit": "I21",
            },
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # TRADE DATASET
    # ==========================================

    @staticmethod
    def get_trade():
        df = eurostat.get_data_df(
            EurostatClient.TRADE_BALANCE_DATASET,
            filter_pars={
                "freq": "M",
                "stk_flow": ["EXP", "IMP"],
                "indic_et": "TRD_VAL",
                "partner": "EXT_EU27_2020",
                "sitc06": "TOTAL",
            },
        )
        return df if df is not None else pd.DataFrame()

    # ==========================================
    # EXPORTS
    # ==========================================

    @staticmethod
    def get_exports():
        df = EurostatClient.get_trade()
        if df.empty or "stk_flow" not in df.columns:
            return pd.DataFrame()
        return df[df["stk_flow"] == "EXP"].copy()

    # ==========================================
    # IMPORTS
    # ==========================================

    @staticmethod
    def get_imports():
        df = EurostatClient.get_trade()
        if df.empty or "stk_flow" not in df.columns:
            return pd.DataFrame()
        return df[df["stk_flow"] == "IMP"].copy()

    @staticmethod
    def get_trade_by_country(partner: str = "WORLD"):
        """
        Trade value/balance per EU member state (annual data).
        partner: 'WORLD' for total trade, or 'EXT_EU27_2020' for
        extra-EU trade only.
        """
        df = eurostat.get_data_df(
            EurostatClient.TRADE_BY_COUNTRY_DATASET,
            filter_pars={
                "geo": EurostatClient.EU_COUNTRIES,
                "partner": partner,
                "sitc06": "TOTAL",
                "indic_et": ["MIO_EXP_VAL", "MIO_IMP_VAL", "MIO_BAL_VAL"],
            },
        )
        return df if df is not None else pd.DataFrame()

    @staticmethod
    def get_exports_by_country(partner: str = "WORLD"):
        df = EurostatClient.get_trade_by_country(partner)
        if df.empty or "indic_et" not in df.columns:
            return pd.DataFrame()
        return df[df["indic_et"] == "MIO_EXP_VAL"].copy()

    @staticmethod
    def get_imports_by_country(partner: str = "WORLD"):
        df = EurostatClient.get_trade_by_country(partner)
        if df.empty or "indic_et" not in df.columns:
            return pd.DataFrame()
        return df[df["indic_et"] == "MIO_IMP_VAL"].copy()

    @staticmethod
    def get_trade_balance_by_country(partner: str = "WORLD"):
        df = EurostatClient.get_trade_by_country(partner)
        if df.empty or "indic_et" not in df.columns:
            return pd.DataFrame()
        return df[df["indic_et"] == "MIO_BAL_VAL"].copy()
