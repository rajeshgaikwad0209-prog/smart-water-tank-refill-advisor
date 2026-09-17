"""
inference.py
------------
The genuine Mamdani-style Fuzzy Inference System (FIS) for the
Smart Water Tank Refill Advisor.

Pipeline implemented here (all five classical FIS stages):

    1. FUZZIFICATION      -> compute membership degrees for each crisp input
                              against every linguistic set (membership.py)
    2. RULE EVALUATION     -> apply fuzzy AND (min) across antecedents for
                              every rule in the rule base (rules.py) to get
                              a firing strength
    3. IMPLICATION         -> clip each rule's output fuzzy set at its
                              firing strength (Mamdani min-implication)
    4. AGGREGATION         -> combine all clipped output sets using max
    5. DEFUZZIFICATION     -> centroid (center of area) method to obtain
                              a single crisp Refill Urgency score (0-100)

No branch of this module ever hardcodes the final score via if/else -
the score is always the numerical result of centroid defuzzification
over the aggregated fuzzy output surface.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import skfuzzy as fuzz

from fuzzy.membership import (
    TANK_LEVEL_UNIVERSE,
    WATER_USAGE_UNIVERSE,
    HOUSEHOLD_SIZE_UNIVERSE,
    URGENCY_UNIVERSE,
    tank_level_mfs,
    water_usage_mfs,
    household_size_mfs,
    urgency_mfs,
    interp_membership,
)
from fuzzy.rules import RULES


@dataclass
class RuleActivation:
    rule_id: int
    description: str
    firing_strength: float
    output_set: str


@dataclass
class FuzzyResult:
    urgency_score: float
    urgency_category: str
    tank_level_memberships: Dict[str, float]
    water_usage_memberships: Dict[str, float]
    household_size_memberships: Dict[str, float]
    activated_rules: List[RuleActivation]
    aggregated_output: np.ndarray = field(repr=False)
    urgency_universe: np.ndarray = field(repr=False)


def categorize_urgency(score: float) -> str:
    """
    Maps the crisp defuzzified score (0-100) onto a human-readable
    urgency category. These bands are documented consistently across
    the whole project (README, docs/fuzzy_rules.md, UI).
    """
    if score < 20:
        return "Very Low"
    elif score < 40:
        return "Low"
    elif score < 60:
        return "Medium"
    elif score < 80:
        return "High"
    else:
        return "Very High"


def run_fuzzy_inference(
    tank_level_percent: float,
    water_usage_score: float,
    household_size: int,
) -> FuzzyResult:
    """
    Executes the full Mamdani fuzzy inference pipeline.

    Parameters
    ----------
    tank_level_percent : float
        Current tank level as a percentage (0-100).
    water_usage_score : float
        Normalized water usage intensity (0-100), where higher = more
        water consumed relative to typical household usage.
    household_size : int
        Number of people in the household (0-12+, values above 12 are
        clipped to the universe boundary for membership purposes).

    Returns
    -------
    FuzzyResult
        Dataclass containing the crisp score, category, all membership
        degrees (for the "Fuzzy Analysis" UI section), and the list of
        activated rules with their firing strengths.
    """
    # ---------------- Stage 1: FUZZIFICATION ----------------
    tl_mfs = tank_level_mfs()
    wu_mfs = water_usage_mfs()
    hs_mfs = household_size_mfs()
    ur_mfs = urgency_mfs()

    tank_level_degrees = {
        name: interp_membership(TANK_LEVEL_UNIVERSE, mf, tank_level_percent)
        for name, mf in tl_mfs.items()
    }
    water_usage_degrees = {
        name: interp_membership(WATER_USAGE_UNIVERSE, mf, water_usage_score)
        for name, mf in wu_mfs.items()
    }
    household_size_degrees = {
        name: interp_membership(HOUSEHOLD_SIZE_UNIVERSE, mf, household_size)
        for name, mf in hs_mfs.items()
    }

    # ---------------- Stage 2 & 3: RULE EVALUATION + IMPLICATION ----------------
    aggregated_output = np.zeros_like(URGENCY_UNIVERSE, dtype=float)
    activated_rules: List[RuleActivation] = []

    for rule in RULES:
        antecedent_degrees = []

        if rule["tank_level"] is not None:
            antecedent_degrees.append(tank_level_degrees[rule["tank_level"]])
        if rule["water_usage"] is not None:
            antecedent_degrees.append(water_usage_degrees[rule["water_usage"]])
        if rule["household_size"] is not None:
            antecedent_degrees.append(household_size_degrees[rule["household_size"]])

        # Fuzzy AND = min of antecedent membership degrees
        firing_strength = min(antecedent_degrees) if antecedent_degrees else 0.0

        if firing_strength > 0.0:
            output_mf = ur_mfs[rule["urgency"]]
            # Mamdani min-implication: clip the output set at firing strength
            clipped = np.fmin(firing_strength, output_mf)
            # Aggregation: max across all activated rules
            aggregated_output = np.fmax(aggregated_output, clipped)

            activated_rules.append(
                RuleActivation(
                    rule_id=rule["id"],
                    description=rule["description"],
                    firing_strength=round(float(firing_strength), 4),
                    output_set=rule["urgency"],
                )
            )

    # Sort activated rules by firing strength, strongest first
    activated_rules.sort(key=lambda r: r.firing_strength, reverse=True)

    # ---------------- Stage 4: DEFUZZIFICATION (centroid) ----------------
    if np.sum(aggregated_output) == 0:
        # No rule fired at all (should not normally happen given full
        # coverage of the rule base, but guarded defensively).
        urgency_score = 0.0
    else:
        urgency_score = float(
            fuzz.defuzz(URGENCY_UNIVERSE, aggregated_output, "centroid")
        )

    urgency_score = round(float(np.clip(urgency_score, 0, 100)), 2)
    urgency_category = categorize_urgency(urgency_score)

    return FuzzyResult(
        urgency_score=urgency_score,
        urgency_category=urgency_category,
        tank_level_memberships={k: round(v, 4) for k, v in tank_level_degrees.items()},
        water_usage_memberships={k: round(v, 4) for k, v in water_usage_degrees.items()},
        household_size_memberships={k: round(v, 4) for k, v in household_size_degrees.items()},
        activated_rules=activated_rules,
        aggregated_output=aggregated_output,
        urgency_universe=URGENCY_UNIVERSE,
    )
