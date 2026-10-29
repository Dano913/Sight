from app.clients.bls_client import BlsClient


def test_get_inflation_calculates_year_over_year_rate(monkeypatch):
    # IPC de enero: 100 el año anterior y 110 el actual.
    # IPC de febrero: 200 el año anterior y 210 el actual.
    cpi_data = [
        {"year": "2024", "period": "M01", "value": "100"},
        {"year": "2024", "period": "M02", "value": "200"},
        {"year": "2025", "period": "M01", "value": "110"},
        {"year": "2025", "period": "M02", "value": "210"},
    ]

    monkeypatch.setattr(
        BlsClient,
        "get_cpi",
        staticmethod(lambda: cpi_data),
    )

    result = BlsClient.get_inflation()

    assert result == [
        {"year": "2025", "period": "M01", "value": "10.000"},
        {"year": "2025", "period": "M02", "value": "5.000"},
    ]