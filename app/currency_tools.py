"""Currency exchange rate tool for Globetrotter Travel Concierge using Frankfurter public API."""

import json
import os
import urllib.request


def get_currency_exchange_rates(
    base_currency: str = "USD", target_currencies: str = "EUR,JPY,GBP,IDR,ISK"
) -> str:
    """Fetches real-time live currency exchange rates for travel package calculations.

    Args:
        base_currency: The base currency code (e.g. 'USD', 'EUR'). Defaults to 'USD'.
        target_currencies: Comma-separated target currency codes (e.g. 'JPY,EUR,GBP,IDR,ISK').

    Returns:
        A string formatted list of current live exchange rates.
    """
    base = base_currency.strip().upper()
    targets = [t.strip().upper() for t in target_currencies.split(",") if t.strip()]

    # Read optional API key from env if configured
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")

    url = f"https://api.frankfurter.dev/v1/latest?base={base}"
    if targets:
        url += f"&symbols={','.join(targets)}"

    req = urllib.request.Request(
        url, headers={"User-Agent": "Globetrotter-Travel-Agent/1.0"}
    )
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return f"Error fetching exchange rates (HTTP status {response.status})."
            data = json.loads(response.read().decode("utf-8"))

        rates = data.get("rates", {})
        date_str = data.get("date", "latest")

        output_lines = [
            f"Live Currency Exchange Rates (Base: {base}, Date: {date_str}):"
        ]
        for curr, rate in rates.items():
            output_lines.append(f"- 1 {base} = {rate} {curr}")

        return "\n".join(output_lines)
    except Exception as e:
        return f"Failed to retrieve currency exchange rates: {str(e)}"
