# Viva Preparation — Anticipated Questions & Answers

### Q1. What problem does this project solve?
Households (especially those relying on tanker/pump-fed tanks) often
don't know exactly when to schedule a refill. This project estimates a
0–100 "refill urgency" score from tank level, water usage, and household
size, using genuine fuzzy logic, and explains it in plain language via
an LLM.

### Q2. Why fuzzy logic instead of simple if-else rules?
Real-world quantities like "the tank is a bit low" don't have sharp
boundaries. A tank at 39% and one at 41% shouldn't be treated as
completely different categories the way a hard `if level < 40` would.
Fuzzy logic allows a value to *partially* belong to multiple categories
(e.g. 39% might be 0.6 Low and 0.3 Medium simultaneously), producing
smoother, more realistic urgency scores as inputs change.

### Q3. What type of fuzzy inference system did you use?
A **Mamdani-style** fuzzy inference system: fuzzy inputs, fuzzy IF-THEN
rules with fuzzy (not crisp) consequents, max-min composition for
aggregation, and centroid defuzzification to produce a crisp output.

### Q4. Walk through the 5 stages of your fuzzy system.
1. **Fuzzification** — convert crisp inputs into membership degrees
   using triangular/trapezoidal membership functions.
2. **Rule Evaluation** — compute each rule's firing strength as the
   minimum of its antecedent membership degrees (fuzzy AND).
3. **Implication** — clip each rule's output fuzzy set at its firing
   strength.
4. **Aggregation** — combine all clipped outputs using the maximum
   (fuzzy OR) to get one aggregated output surface.
5. **Defuzzification** — apply the centroid method to that surface to
   get a single number (0–100).

### Q5. Why triangular/trapezoidal membership functions specifically?
They are simple to define, computationally cheap, and easy to explain
and justify to non-technical stakeholders, while still producing smooth
overlapping membership — appropriate for a system whose inputs are
already fairly noisy estimates (e.g. self-reported tank percentage).

### Q6. Where exactly does LangChain get used, and why not just call the OpenAI API directly?
LangChain is used in two places:
1. **Extraction** (`ai/extractor.py`) — turning a free-text household
   description into a validated, schema-conformant structured object
   using `with_structured_output` bound to a Pydantic model.
2. **Explanation** (`ai/explainer.py`) — turning the fuzzy engine's
   numeric result into a natural-language recommendation.

LangChain provides `ChatPromptTemplate` for reusable prompt structuring,
a uniform `ChatOpenAI` interface, and — most importantly —
`with_structured_output`, which reliably constrains the model to emit
valid JSON matching our schema instead of us having to write fragile
regex/string parsing over raw text completions.

### Q7. Does the LLM ever decide the final urgency score?
No. The LLM never touches the numeric score. The fuzzy engine computes
`urgency_score` and `urgency_category` first; those are passed to the
explanation LLM call as fixed, authoritative values with an explicit
system-prompt instruction not to alter them. The LLM's only job is to
explain the *already-computed* result in natural language.

### Q8. What happens if the extraction is missing information?
The system never invents values. If the LLM cannot find tank capacity,
tank level, or household size in the text, those fields are returned as
`null`/missing, and the Streamlit UI presents input widgets so the user
can supply exactly the missing values — nothing else is re-asked.

### Q9. What if there's no API key configured?
The manual input tab (sliders and number inputs) works completely
independently of the LLM, feeding the same fuzzy engine. If the
explanation LLM call fails or no key is present, the app falls back to
a pre-written but result-accurate template explanation rather than
crashing.

### Q10. How does household size affect the outcome?
Household size is fuzzified into Small/Medium/Large sets and appears as
a third antecedent in several rules (e.g. rule 16: Low tank + High usage
+ Large household → Very High urgency), capturing that larger households
draw down the same tank level faster than smaller ones.

### Q11. How is water usage represented, given it's described qualitatively?
The AI extractor / manual dropdown produce a qualitative label
(low/medium/high). `utils/helpers.usage_label_to_score()` maps each
label to a representative point (15/50/85) on the fuzzy engine's 0–100
"usage intensity" universe, which is then fuzzified normally like any
other numeric input.

### Q12. Why centroid defuzzification and not, say, mean-of-maximum?
Centroid (center of area) is the most widely used and well-understood
Mamdani defuzzification method. It accounts for the *entire* shape of
the aggregated output surface (not just its peak), producing smoother,
more stable output as inputs change slightly — appropriate for a
recommendation system where jarring jumps between refills would be a
poor user experience.

### Q13. How would you extend this project?
- Integrate with real IoT tank-level sensors (ultrasonic sensor + ESP32)
  instead of self-reported percentages.
- Add a time-series forecast (e.g. using historical usage) to predict
  *when* the tank will hit critical level, not just current urgency.
- Support multiple tanks/multiple households with persistent storage.
- Add multi-turn conversational clarification instead of a static form
  for missing fields.

### Q14. What are the current limitations?
- Water usage is a coarse 3-level qualitative input rather than a
  precise litres/day figure (though the LLM does its best to infer it
  from context).
- No persistent history/database — each analysis is independent.
- Relies on an external LLM API for the AI mode (manual mode is fully
  offline-capable except for internet needed to load Streamlit itself).

### Q15. How did you validate the fuzzy engine gives sensible results?
Test cases (see `docs/project_report.md` Test Cases section) were run
covering extreme, mid-range, and boundary inputs, confirming the score
and category track intuitive expectations (e.g. very low tank + high
usage + large household → Very High; nearly full tank + low usage →
Very Low), while boundary inputs correctly show partial membership
across two neighboring categories rather than a sharp jump.
