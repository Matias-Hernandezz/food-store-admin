from unittest.mock import MagicMock, patch

from app.core.geocoding import geocode_address


@patch("app.core.geocoding.httpx.Client")
def test_geocode_address_ok(mock_client_cls):
    mock_res = MagicMock()
    mock_res.json.return_value = [{"lat": "-34.60", "lon": "-58.38"}]
    mock_res.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.__enter__.return_value.get.return_value = mock_res
    mock_client_cls.return_value = mock_client

    coords = geocode_address(linea1="San Martín 123", ciudad="Rosario", provincia="Santa Fe")
    assert coords == (-34.60, -58.38)
