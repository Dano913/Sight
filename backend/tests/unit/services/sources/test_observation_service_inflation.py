import pandas as pd

from app.models.observation import Observation
from app.services.catalog.observation_service import ObservationService


def test_refresh_inflation_combines_eurostat_and_bls_without_database_writes(
    monkeypatch,
):
    eurostat_df = pd.DataFrame(
        [
            {
                "geo\\TIME_PERIOD": "ES",
                "coicop": "CP00",
                "unit": "RCH_A_AVG",
                "2024": 3.0,
                "2025": 2.5,
            },
            {
                "geo\\TIME_PERIOD": "ES",
                "coicop": "CP00",
                "unit": "OTHER",
                "2024": 99.0,
                "2025": 99.0,
            },
        ]
    )

    bls_data = [
        {"year": "2024", "period": "M01", "value": "3.1"},
        {"year": "2025", "period": "M01", "value": "2.8"},
    ]

    monkeypatch.setattr(
        "app.services.catalog.observation_service.EurostatClient.get_inflation",
        lambda: eurostat_df,
    )
    monkeypatch.setattr(
        "app.services.catalog.observation_service.BlsClient.get_inflation",
        lambda: bls_data,
    )

    writes = []

    def fake_replace(
        region_code,
        indicator_code,
        source_code,
        observations,
    ):
        writes.append(
            {
                "region_code": region_code,
                "indicator_code": indicator_code,
                "source_code": source_code,
                "observations": list(observations),
            }
        )

    monkeypatch.setattr(
        "app.services.catalog.observation_service.ObservationRepository.exists",
        lambda indicator_code: False,
    )
    monkeypatch.setattr(
        "app.services.catalog.observation_service.ObservationRepository.replace_by_region_indicator_source",
        fake_replace,
    )

    result = ObservationService.get_observations(
        indicator_code="INFLATION",
        refresh=True,
    )

    assert len(result) == 4
    assert all(isinstance(item, Observation) for item in result)

    sources = {item.source.code for item in result}
    assert sources == {"EUROSTAT", "BLS"}

    eurostat_result = [
        item for item in result if item.source.code == "EUROSTAT"
    ]
    bls_result = [
        item for item in result if item.source.code == "BLS"
    ]

    assert len(eurostat_result) == 2
    assert len(bls_result) == 2

    assert {item.region.code for item in eurostat_result} == {"ES"}
    assert {item.region.code for item in bls_result} == {"US"}

    assert {item.value for item in eurostat_result} == {3.0, 2.5}
    assert {item.value for item in bls_result} == {3.1, 2.8}

    assert len(writes) == 2
    assert {
        (write["region_code"], write["indicator_code"], write["source_code"])
        for write in writes
    } == {
        ("ES", "INFLATION", "EUROSTAT"),
        ("US", "INFLATION", "BLS"),
    }

    assert sum(len(write["observations"]) for write in writes) == 4