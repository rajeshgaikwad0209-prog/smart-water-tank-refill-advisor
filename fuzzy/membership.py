"""
membership.py
--------------
Defines the fuzzy universes of discourse and membership functions for the
Smart Water Tank Refill Advisor.

All membership functions are built using scikit-fuzzy (skfuzzy) and are
either triangular (trimf) or trapezoidal (trapmf) shaped, as required by
the project specification. No crisp if-else thresholds are used to decide
urgency — degrees of membership are calculated mathematically.

Universes of discourse:
    Tank Level (%)      : 0  - 100
    Water Usage (score)  : 0  - 100   (Low/Medium/High usage intensity)
    Household Size (ppl) : 0  - 12    (12 = "very large household" cap)
    Refill Urgency (score): 0 - 100   (output variable)
"""

import numpy as np
import skfuzzy as fuzz

# ---------------------------------------------------------------------------
# Universes of discourse
# ---------------------------------------------------------------------------
TANK_LEVEL_UNIVERSE = np.arange(0, 101, 1)      # 0-100 %
WATER_USAGE_UNIVERSE = np.arange(0, 101, 1)     # 0-100 (normalized usage score)
HOUSEHOLD_SIZE_UNIVERSE = np.arange(0, 13, 1)   # 0-12 people
URGENCY_UNIVERSE = np.arange(0, 101, 1)         # 0-100 output score


# ---------------------------------------------------------------------------
# Tank Level membership functions (5 sets)
# ---------------------------------------------------------------------------
def tank_level_mfs(x=TANK_LEVEL_UNIVERSE):
    """
    Returns a dict of membership arrays for Tank Level.

    Design rationale:
    - Very Low and Very High use trapezoidal "shoulder" functions so that
      the extreme ends of the scale (0% and 100%) have full membership,
      rather than tapering to zero, which would be unrealistic.
    - Low, Medium, High are triangular with generous overlap so that a
      tank level such as 32% naturally has partial membership in two
      neighbouring sets (e.g. Low and Medium), which is the hallmark of
      genuine fuzzy logic as opposed to crisp thresholds.
    """
    very_low = fuzz.trapmf(x, [0, 0, 10, 25])
    low = fuzz.trimf(x, [10, 25, 40])
    medium = fuzz.trimf(x, [30, 50, 70])
    high = fuzz.trimf(x, [60, 75, 90])
    very_high = fuzz.trapmf(x, [80, 92, 100, 100])
    return {
        "very_low": very_low,
        "low": low,
        "medium": medium,
        "high": high,
        "very_high": very_high,
    }


# ---------------------------------------------------------------------------
# Water Usage membership functions (3 sets)
# ---------------------------------------------------------------------------
def water_usage_mfs(x=WATER_USAGE_UNIVERSE):
    """
    Water usage is represented on a normalized 0-100 "usage intensity"
    scale. The AI extraction / manual input layer maps qualitative labels
    (low/medium/high) or estimated litre/day figures onto this scale
    before it reaches the fuzzy engine (see utils/helpers.py).
    """
    low = fuzz.trapmf(x, [0, 0, 20, 45])
    medium = fuzz.trimf(x, [30, 50, 70])
    high = fuzz.trapmf(x, [55, 80, 100, 100])
    return {"low": low, "medium": medium, "high": high}


# ---------------------------------------------------------------------------
# Household Size membership functions (3 sets)
# ---------------------------------------------------------------------------
def household_size_mfs(x=HOUSEHOLD_SIZE_UNIVERSE):
    """
    Small: 1-3 members, Medium: 3-6 members, Large: 6+ members.
    Chosen to reflect typical household sizes; overlap around 3 and 6
    allows smooth transition rather than a hard cutoff.
    """
    small = fuzz.trapmf(x, [0, 0, 2, 4])
    medium = fuzz.trimf(x, [3, 5, 7])
    large = fuzz.trapmf(x, [6, 8, 12, 12])
    return {"small": small, "medium": medium, "large": large}


# ---------------------------------------------------------------------------
# Refill Urgency (OUTPUT) membership functions (5 sets)
# ---------------------------------------------------------------------------
def urgency_mfs(x=URGENCY_UNIVERSE):
    """
    Output fuzzy sets for Refill Urgency, mirroring the 5-level structure
    of Tank Level so the rule base reads naturally (low tank -> high
    urgency, etc.). Centroid defuzzification is applied over this
    aggregated output surface to produce the final 0-100 score.
    """
    very_low = fuzz.trapmf(x, [0, 0, 10, 25])
    low = fuzz.trimf(x, [15, 30, 45])
    medium = fuzz.trimf(x, [35, 50, 65])
    high = fuzz.trimf(x, [55, 70, 85])
    very_high = fuzz.trapmf(x, [75, 90, 100, 100])
    return {
        "very_low": very_low,
        "low": low,
        "medium": medium,
        "high": high,
        "very_high": very_high,
    }


def interp_membership(universe, mf_array, crisp_value):
    """
    Convenience wrapper around skfuzzy.interp_membership so calling code
    doesn't need to import skfuzzy directly.
    """
    crisp_value = float(np.clip(crisp_value, universe.min(), universe.max()))
    return float(fuzz.interp_membership(universe, mf_array, crisp_value))
