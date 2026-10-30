from __future__ import annotations

from datetime import date
import pandas as pd
import pytest

from app.clients.bea_client import BeaClient
from app.clients.bls_client import BlsClient
from app.clients.eurostat_client import EurostatClient
from app.normalizers.bea_normalizer import BeaNormalizer
from app.normalizers.bls_normalizer import BlsNormalizer
from app.normalizers.eurostat_normalizer import EurostatNormalizer
from app.normalizers.nbs_normalizer import NbsNormalizer
from app.services.catalog.observation_service import ObservationService


class TestFetcherRegistryClientMethods:

    def test_all_registered_client_methods_exist(self):
        """
        Verifica que todos los métodos declarados en ObservationService._FETCHER_REGISTRY
        existan realmente en sus respectivas clases cliente y normalizadores.
        """
        for indicator_code, entries in ObservationService._FETCHER_REGISTRY.items():
            for source_code, client_cls, method_name, normalizer_cls in entries:
                assert hasattr(client_cls, method_name), (
                    f"{client_cls.__name__} no tiene el método {method_name} "
                    f"requerido por {indicator_code} ({source_code})"
                )
                assert hasattr(normalizer_cls, "to_observations"), (
                    f"{normalizer_cls.__name__} no tiene to_observations"
                )


class TestBeaClientAndNormalizer:

    def test_bea_client_supports_gdp_exports_and_imports(self, monkeypatch):
        monkeypatch.setenv("BEA_API_KEY", "fake_key")

        fake_payload = {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "SeriesCode": "A191RX",
                            "LineNumber": "1",
                            "CL_UNIT": "Level",
                            "TimePeriod": "2024Q1",
                            "DataValue": "22,500,000",
                        },
                        {
                            "SeriesCode": "A020RX",
                            "LineNumber": "16",
                            "CL_UNIT": "Level",
                            "TimePeriod": "2024Q1",
                            "DataValue": "2,500,000",
                        },
                        {
                            "SeriesCode": "A021RX",
                            "LineNumber": "19",
                            "CL_UNIT": "Level",
                            "TimePeriod": "2024Q1",
                            "DataValue": "3,400,000",
                        },
                    ]
                }
            }
        }

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return fake_payload

        monkeypatch.setattr(
            "app.clients.bea_client.requests.get",
            lambda *args, **kwargs: FakeResponse(),
        )

        gdp_rows = BeaClient.get_gdp()
        exp_rows = BeaClient.get_exports()
        imp_rows = BeaClient.get_imports()

        assert len(gdp_rows) == 1
        assert len(exp_rows) == 1
        assert len(imp_rows) == 1

        gdp_obs = BeaNormalizer.to_observations(gdp_rows, "GDP", "BEA")
        exp_obs = BeaNormalizer.to_observations(exp_rows, "EXPORTS", "BEA")
        imp_obs = BeaNormalizer.to_observations(imp_rows, "IMPORTS", "BEA")

        assert len(gdp_obs) == 1
        assert gdp_obs[0].value == 22500.0
        assert gdp_obs[0].date == date(2024, 1, 1)

        assert len(exp_obs) == 1
        assert exp_obs[0].value == 2500.0

        assert len(imp_obs) == 1
        assert imp_obs[0].value == 3400.0


class TestBlsNormalizerEdgeCases:

    def test_bls_normalizer_handles_missing_keys_and_special_markers(self):
        rows = [
            {"year": "2024", "period": "M01", "value": "3.5"},
            {"year": "2024", "period": "M00", "value": "3.5"},  # mes inválido 0
            {"year": "2024", "period": "M13", "value": "3.5"},  # media anual
            {"year": "2024", "period": "M02", "value": "-"},    # marcador BLS sin dato
            {"year": "2024", "period": "M03", "value": "nan"},  # NaN
            {"period": "M04", "value": "4.0"},                  # falta year
            {"year": "2024", "value": "4.0"},                   # falta period
        ]

        obs = BlsNormalizer.to_observations(rows, "UNEMPLOYMENT", "BLS")
        assert len(obs) == 1
        assert obs[0].date == date(2024, 1, 1)
        assert obs[0].value == 3.5


class TestEurostatNormalizerEdgeCases:

    def test_eurostat_normalizer_handles_string_flags_and_quarterly_columns_in_monthly(
        self,
    ):
        # En un indicador mensual (CPI), una columna '2024-Q1' (longitud 7 con '-')
        # o una columna anual '2024' no deben provocar ValueError, y banderas ':' deben ignorarse.
        df = pd.DataFrame(
            [
                {
                    "geo": "DE",
                    "coicop": "CP00",
                    "unit": "I15",
                    "2024-01": "115.2",
                    "2024-02": ":",
                    "2024-Q1": "115.0",
                    "2024": "115.0",
                }
            ]
        )

        obs = EurostatNormalizer.to_observations(df, "CPI", "EUROSTAT")
        dates = [o.date for o in obs]
        assert date(2024, 1, 1) in dates
        assert all(o.region.code == "DE" for o in obs)

    def test_eurostat_client_empty_dataframe_safety(self, monkeypatch):
        monkeypatch.setattr(
            "app.clients.eurostat_client.eurostat.get_data_df",
            lambda *args, **kwargs: None,
        )
        assert EurostatClient.get_exports().empty
        assert EurostatClient.get_imports().empty
        assert EurostatClient.get_exports_by_country().empty


class TestNbsNormalizer:

    def test_nbs_normalizer_parses_native_returndata_envelope(self):
        payload = {
            "returncode": 200,
            "returndata": {
                "datanodes": [
                    {
                        "data": {"hasdata": True, "data": 102.4, "strdata": "102.4"},
                        "wds": [
                            {"wdcode": "zb", "valuecode": "A0901"},
                            {"wdcode": "sj", "valuecode": "202403"},
                        ],
                    },
                    {
                        "data": {"hasdata": False, "data": 0.0},
                        "wds": [{"wdcode": "sj", "valuecode": "202404"}],
                    },
                ]
            },
        }

        obs = NbsNormalizer.to_observations(payload, "CPI", "NBS")
        assert len(obs) == 1
        assert obs[0].region.code == "CN"
        assert obs[0].date == date(2024, 3, 1)
        assert obs[0].value == 102.4

    def test_nbs_normalizer_parses_flat_list(self):
        flat = [
            {"year": "2023", "value": "5.2"},
            {"period": "2024B", "value": "5.0"},
        ]
        obs = NbsNormalizer.to_observations(flat, "GDP", "NBS")
        assert len(obs) == 2
        assert obs[0].date == date(2023, 1, 1)
        assert obs[1].date == date(2024, 4, 1)
