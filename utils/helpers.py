"""
helpers.py
----------
General-purpose helper functions shared across the application, most
importantly the mapping from a qualitative water-usage label
(low/medium/high) — which is what both the AI extractor and the manual
input form produce — to the normalized 0-100 "usage intensity" score
that the fuzzy engine's Water Usage input universe expects.
"""

import os

# Representative midpoint scores for each qualitative usage label.
# These values were chosen to sit centrally within the corresponding
# fuzzy membership function region defined in fuzzy/membership.py,
# so a label of "high" reliably activates the High usage fuzzy set.
USAGE_LABEL_TO_SCORE = {
    "low": 15,
    "medium": 50,
    "high": 85,
}


def usage_label_to_score(label: str) -> float:
    """Converts a low/medium/high label into a 0-100 usage intensity score."""
    if not label:
        return USAGE_LABEL_TO_SCORE["medium"]
    label = label.strip().lower()
    return USAGE_LABEL_TO_SCORE.get(label, USAGE_LABEL_TO_SCORE["medium"])


def get_api_key() -> str:
    """
    Retrieves the OpenAI API key from Streamlit secrets (deployed) or
    environment variables (local development via .env), in that order.
    Never hardcoded. Returns an empty string if not found, letting
    calling code handle the "missing key" case gracefully.
    """
    try:
        import streamlit as st

        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass  # st.secrets not available (e.g. no secrets.toml locally) - fall through

    return os.environ.get("OPENAI_API_KEY", "")


def format_liters(value: float) -> str:
    """Formats a litre quantity for display, e.g. 1000 -> '1,000 L'."""
    try:
        return f"{value:,.0f} L"
    except (TypeError, ValueError):
        return "N/A"


def estimated_liters_remaining(tank_capacity_liters: float, tank_level_percent: float) -> float:
    """Computes the estimated litres currently remaining in the tank."""
    if tank_capacity_liters is None or tank_level_percent is None:
        return 0.0
    return round(tank_capacity_liters * (tank_level_percent / 100.0), 1)
