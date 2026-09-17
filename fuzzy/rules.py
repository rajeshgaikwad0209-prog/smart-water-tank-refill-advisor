"""
rules.py
--------
Defines the Mamdani fuzzy rule base for the Smart Water Tank Refill Advisor.

Each rule is expressed as a plain Python dict so it can be:
    1. Evaluated programmatically by fuzzy/inference.py
    2. Displayed to the user in the "Fuzzy Analysis" UI section
    3. Documented in docs/fuzzy_rules.md

Rule structure:
{
    "id": int,
    "tank_level": one of very_low/low/medium/high (or None to ignore),
    "water_usage": one of low/medium/high (or None to ignore),
    "household_size": one of small/medium/large (or None to ignore),
    "urgency": output fuzzy set name,
    "description": human-readable rule text
}

A rule with household_size = None means the rule fires purely on tank
level and water usage (2-antecedent rule). Rules with all three
antecedents are used to capture the extra nuance that a larger household
depletes a tank faster, and a smaller household can tolerate a lower
level slightly longer.
"""

RULES = [
    # ---- Core 2-antecedent rules: Tank Level x Water Usage -----------
    {"id": 1, "tank_level": "very_low", "water_usage": "high", "household_size": None,
     "urgency": "very_high",
     "description": "IF tank level is Very Low AND water usage is High THEN urgency is Very High"},
    {"id": 2, "tank_level": "very_low", "water_usage": "medium", "household_size": None,
     "urgency": "very_high",
     "description": "IF tank level is Very Low AND water usage is Medium THEN urgency is Very High"},
    {"id": 3, "tank_level": "very_low", "water_usage": "low", "household_size": None,
     "urgency": "high",
     "description": "IF tank level is Very Low AND water usage is Low THEN urgency is High"},
    {"id": 4, "tank_level": "low", "water_usage": "high", "household_size": None,
     "urgency": "very_high",
     "description": "IF tank level is Low AND water usage is High THEN urgency is Very High"},
    {"id": 5, "tank_level": "low", "water_usage": "medium", "household_size": None,
     "urgency": "high",
     "description": "IF tank level is Low AND water usage is Medium THEN urgency is High"},
    {"id": 6, "tank_level": "low", "water_usage": "low", "household_size": None,
     "urgency": "medium",
     "description": "IF tank level is Low AND water usage is Low THEN urgency is Medium"},
    {"id": 7, "tank_level": "medium", "water_usage": "high", "household_size": None,
     "urgency": "high",
     "description": "IF tank level is Medium AND water usage is High THEN urgency is High"},
    {"id": 8, "tank_level": "medium", "water_usage": "medium", "household_size": None,
     "urgency": "medium",
     "description": "IF tank level is Medium AND water usage is Medium THEN urgency is Medium"},
    {"id": 9, "tank_level": "medium", "water_usage": "low", "household_size": None,
     "urgency": "low",
     "description": "IF tank level is Medium AND water usage is Low THEN urgency is Low"},
    {"id": 10, "tank_level": "high", "water_usage": "high", "household_size": None,
     "urgency": "medium",
     "description": "IF tank level is High AND water usage is High THEN urgency is Medium"},
    {"id": 11, "tank_level": "high", "water_usage": "medium", "household_size": None,
     "urgency": "low",
     "description": "IF tank level is High AND water usage is Medium THEN urgency is Low"},
    {"id": 12, "tank_level": "high", "water_usage": "low", "household_size": None,
     "urgency": "very_low",
     "description": "IF tank level is High AND water usage is Low THEN urgency is Very Low"},
    {"id": 13, "tank_level": "very_high", "water_usage": "high", "household_size": None,
     "urgency": "low",
     "description": "IF tank level is Very High AND water usage is High THEN urgency is Low"},
    {"id": 14, "tank_level": "very_high", "water_usage": "medium", "household_size": None,
     "urgency": "very_low",
     "description": "IF tank level is Very High AND water usage is Medium THEN urgency is Very Low"},
    {"id": 15, "tank_level": "very_high", "water_usage": "low", "household_size": None,
     "urgency": "very_low",
     "description": "IF tank level is Very High AND water usage is Low THEN urgency is Very Low"},

    # ---- 3-antecedent rules: household size adds nuance ---------------
    {"id": 16, "tank_level": "low", "water_usage": "high", "household_size": "large",
     "urgency": "very_high",
     "description": "IF tank level is Low AND water usage is High AND household is Large THEN urgency is Very High"},
    {"id": 17, "tank_level": "medium", "water_usage": "high", "household_size": "large",
     "urgency": "high",
     "description": "IF tank level is Medium AND water usage is High AND household is Large THEN urgency is High"},
    {"id": 18, "tank_level": "medium", "water_usage": "low", "household_size": "small",
     "urgency": "low",
     "description": "IF tank level is Medium AND water usage is Low AND household is Small THEN urgency is Low"},
    {"id": 19, "tank_level": "high", "water_usage": "medium", "household_size": "large",
     "urgency": "medium",
     "description": "IF tank level is High AND water usage is Medium AND household is Large THEN urgency is Medium"},
    {"id": 20, "tank_level": "very_low", "water_usage": "low", "household_size": "small",
     "urgency": "medium",
     "description": "IF tank level is Very Low AND water usage is Low AND household is Small THEN urgency is Medium"},
    {"id": 21, "tank_level": "low", "water_usage": "medium", "household_size": "large",
     "urgency": "very_high",
     "description": "IF tank level is Low AND water usage is Medium AND household is Large THEN urgency is Very High"},
    {"id": 22, "tank_level": "high", "water_usage": "low", "household_size": "large",
     "urgency": "low",
     "description": "IF tank level is High AND water usage is Low AND household is Large THEN urgency is Low"},
]
