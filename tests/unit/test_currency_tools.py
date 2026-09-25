"""Unit tests for currency exchange rate tool."""

from unittest.mock import MagicMock, patch
from app.currency_tools import get_currency_exchange_rates


@patch("app.currency_tools.urllib.request.urlopen")
def test_get_currency_exchange_rates_success(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"base":"USD","date":"2026-09-24","rates":{"EUR":0.88,"JPY":158.5}}'
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = get_currency_exchange_rates(base_currency="USD", target_currencies="EUR,JPY")
    assert "Live Currency Exchange Rates" in res
    assert "1 USD = 0.88 EUR" in res
    assert "1 USD = 158.5 JPY" in res
