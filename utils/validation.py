"""
validation.py
--------------
Centralized validation rules for all user-provided or AI-extracted
values. Used by both the AI extraction pipeline (ai/extractor.py) and
the manual input form (app.py) so validation logic is never duplicated.
"""

from typing import Optional, Tuple

VALID_USAGE_LABELS = ("low", "medium", "high")


def is_valid_capacity(value: Optional[float]) -> bool:
    """Tank capacity must be a positive number."""
    return value is not None and isinstance(value, (int, float)) and value > 0


def is_valid_percent(value: Optional[float]) -> bool:
    """Tank level percentage must be between 0 and 100 inclusive."""
    return value is not None and isinstance(value, (int, float)) and 0 <= value <= 100


def is_valid_household_size(value: Optional[int]) -> bool:
    """Household size must be a positive integer."""
    return value is not None and isinstance(value, (int, float)) and value > 0


def is_valid_usage_label(value: Optional[str]) -> bool:
    return isinstance(value, str) and value.lower() in VALID_USAGE_LABELS


def validate_all_inputs(
    tank_capacity_liters,
    tank_level_percent,
    household_size,
    water_usage,
) -> Tuple[bool, list]:
    """
    Validates the full set of inputs required to run fuzzy inference.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []

    if not is_valid_capacity(tank_capacity_liters):
        errors.append("Tank capacity must be a number greater than 0 litres.")

    if not is_valid_percent(tank_level_percent):
        errors.append("Tank level must be a percentage between 0 and 100.")

    if not is_valid_household_size(household_size):
        errors.append("Household size must be a whole number greater than 0.")

    if not is_valid_usage_label(water_usage):
        errors.append("Water usage must be one of: low, medium, high.")

    return (len(errors) == 0, errors)
