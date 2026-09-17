# Fuzzy Rule Base — Smart Water Tank Refill Advisor

This document lists the complete Mamdani fuzzy rule base implemented in
`fuzzy/rules.py`, along with the reasoning behind the rule design.

## Fuzzy Variables

| Variable | Type | Fuzzy Sets |
|---|---|---|
| Tank Level (%) | Input | Very Low, Low, Medium, High, Very High |
| Water Usage (0–100 intensity) | Input | Low, Medium, High |
| Household Size (people) | Input | Small, Medium, Large |
| Refill Urgency (0–100) | Output | Very Low, Low, Medium, High, Very High |

## Design Principle

Two-antecedent rules (Tank Level × Water Usage) form the core 15-rule
backbone, covering every combination of the 5 Tank Level sets and 3
Water Usage sets. Three-antecedent rules (adding Household Size) refine
specific edge cases where household size meaningfully shifts urgency —
for example, a large household draws down a half-full tank much faster
than a small household, so urgency should be higher even at the same
tank level and usage reading.

## Complete Rule Table

| # | Tank Level | Water Usage | Household Size | → Urgency |
|---|---|---|---|---|
| 1 | Very Low | High | — | Very High |
| 2 | Very Low | Medium | — | Very High |
| 3 | Very Low | Low | — | High |
| 4 | Low | High | — | Very High |
| 5 | Low | Medium | — | High |
| 6 | Low | Low | — | Medium |
| 7 | Medium | High | — | High |
| 8 | Medium | Medium | — | Medium |
| 9 | Medium | Low | — | Low |
| 10 | High | High | — | Medium |
| 11 | High | Medium | — | Low |
| 12 | High | Low | — | Very Low |
| 13 | Very High | High | — | Low |
| 14 | Very High | Medium | — | Very Low |
| 15 | Very High | Low | — | Very Low |
| 16 | Low | High | Large | Very High |
| 17 | Medium | High | Large | High |
| 18 | Medium | Low | Small | Low |
| 19 | High | Medium | Large | Medium |
| 20 | Very Low | Low | Small | Medium |
| 21 | Low | Medium | Large | Very High |
| 22 | High | Low | Large | Low |

## Inference Method

1. **Fuzzification** — each crisp input (tank level %, usage score,
   household size) is converted into membership degrees against every
   relevant fuzzy set using `skfuzzy.interp_membership`.
2. **Rule Evaluation** — for each rule, the fuzzy AND (minimum) of its
   antecedent membership degrees gives the rule's *firing strength*.
3. **Implication** — each fired rule's output fuzzy set is clipped
   (min-implication) at its firing strength.
4. **Aggregation** — all clipped output sets are combined using the
   fuzzy OR (maximum) to form one aggregated output surface.
5. **Defuzzification** — the **centroid (center of area)** method is
   applied to the aggregated surface to produce the final crisp Refill
   Urgency score (0–100).

## Category Mapping (applied to the defuzzified score)

| Score Range | Category |
|---|---|
| 0 – 19.99 | Very Low |
| 20 – 39.99 | Low |
| 40 – 59.99 | Medium |
| 60 – 79.99 | High |
| 80 – 100 | Very High |
