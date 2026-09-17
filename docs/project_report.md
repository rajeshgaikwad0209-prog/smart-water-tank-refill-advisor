# AI-Based Smart Water Tank Refill Advisor Using LangChain and Fuzzy Logic
### College Mini Project Report

---

## Page 1

### 1.1 Title
**AI-Based Smart Water Tank Refill Advisor Using LangChain and Fuzzy Logic**

### 1.2 Introduction
Water scarcity and inefficient household water management are common
problems in many regions, particularly where households depend on
tanker-filled or pump-filled overhead/underground tanks rather than a
continuous municipal supply. Deciding *when* to schedule a refill is
often guesswork — residents either refill too early (wasting a trip and
sometimes money) or too late (running out of water). This project
builds an intelligent advisor that estimates refill urgency from a few
simple inputs and communicates that estimate in plain language.

### 1.3 Problem Statement
Households have no simple, data-driven way to determine how urgently
their water tank needs a refill based on multiple simultaneous factors —
current tank level, household size, and consumption pattern — all of
which interact in non-obvious ways. A tank at 40% may be perfectly fine
for a small, low-usage household but urgently need refilling for a
large, high-usage household. Simple rule-of-thumb thresholds ("refill
below 30%") fail to capture this nuance.

### 1.4 Motivation
This project was motivated by the observation that human reasoning
about "how urgent is this" is inherently fuzzy — we naturally think in
terms of degrees ("fairly low", "quite high") rather than hard
thresholds. Fuzzy logic mathematically formalizes exactly this kind of
reasoning, while a modern LLM (via LangChain) can bridge the gap between
how people *naturally describe* their situation in words and the
structured numeric input a fuzzy system needs.

### 1.5 Objectives
1. Build a genuine Mamdani fuzzy inference system that computes a
   0–100 Refill Urgency score from Tank Level, Water Usage, and
   Household Size.
2. Use LangChain to extract structured data from free-text household
   descriptions, with strict validation (no hallucinated values).
3. Use LangChain a second time to generate a natural-language
   explanation of the (already-computed) fuzzy result, without altering
   it.
4. Provide a simple, mobile-friendly Streamlit web UI supporting both
   natural-language and manual input, with visualizations of the fuzzy
   membership functions for transparency.
5. Deploy the application live on Streamlit Community Cloud with a
   public GitHub repository.

---

## Page 2

### 2.1 Existing Problem
Most existing "smart tank" consumer products either (a) simply display
the current percentage with no interpretation, or (b) use a fixed
threshold alarm (e.g. "alert below 20%") that ignores household size and
usage pattern entirely, and (c) provide no natural-language interface —
users must manually check a percentage reading and mentally judge
urgency themselves.

### 2.2 Proposed System
The proposed system accepts either a free-text description of the
household's water situation or manual structured input, extracts/uses
three key variables (tank level %, water usage level, household size),
feeds them into a rule-based fuzzy inference engine that mirrors human
reasoning about urgency, and returns both a numeric score and an
LLM-generated plain-language explanation — all through a single-page
Streamlit web application.

### 2.3 System Requirements

**Functional Requirements**
- Accept natural-language household descriptions and extract structured
  data via LangChain.
- Accept manual structured input as a fallback/alternative mode.
- Validate all inputs (capacity > 0, level 0–100%, household size > 0,
  usage in {low, medium, high}).
- Run a genuine 5-stage Mamdani fuzzy inference pipeline.
- Display membership degrees, activated rules, and the defuzzified
  score for transparency.
- Generate a natural-language recommendation via LangChain.
- Visualize membership functions using Matplotlib.

**Non-Functional Requirements**
- Must run entirely in Python, hostable on Streamlit Community Cloud.
- No hardcoded API keys; secrets managed via Streamlit Secrets / `.env`.
- Must gracefully degrade (manual mode + fallback template explanation)
  if no LLM API key is configured or the API call fails.

### 2.4 Technology Stack
| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web UI | Streamlit |
| AI / LLM orchestration | LangChain (`langchain`, `langchain-openai`, `langchain-core`) |
| LLM Provider | OpenAI (via LangChain's `ChatOpenAI`, model `gpt-4o-mini`) |
| Fuzzy Logic | scikit-fuzzy (`skfuzzy`) |
| Data validation | Pydantic |
| Visualization | Matplotlib |
| Data handling | Pandas, NumPy |
| Hosting | Streamlit Community Cloud |
| Version Control | GitHub |

---

## Page 3

### 3.1 AI / LangChain Component

**Why LangChain is used.** LangChain provides a standardized interface
(`ChatPromptTemplate`, `ChatOpenAI`) for constructing multi-message
prompts and, critically, the `with_structured_output()` method, which
binds a Pydantic model to the LLM call so the model's response is
constrained to a valid, parseable schema rather than free text that
would need fragile regex extraction.

**Natural-language input.** The user may describe their situation in a
sentence or paragraph, e.g.:

> "There are 5 people in my house. The tank capacity is 1000 litres and
> currently it is around 30% full. We use a lot of water because of
> daily bathing, washing clothes and cleaning."

**Extraction process.** `ai/extractor.py` builds a chain:
`ChatPromptTemplate | ChatOpenAI.with_structured_output(ExtractedWaterInfo)`.
The system prompt (in `ai/prompts.py`) instructs the model to extract
`tank_capacity_liters`, `tank_level_percent`, `household_size`, and
`water_usage`, explicitly forbidding it from inventing values that
aren't present or inferable in the text.

**Structured data.** The Pydantic schema `ExtractedWaterInfo` enforces
types at the parsing level; `utils/validation.py` then applies
domain-specific range checks (capacity > 0, 0 ≤ level ≤ 100, household
size > 0). Fields that are still missing after extraction are reported
back to the UI, which prompts the user for exactly those values — the
system never guesses.

### 3.2 Fuzzy Logic Component

**Inputs and fuzzy sets**

| Variable | Sets |
|---|---|
| Tank Level (%) | Very Low, Low, Medium, High, Very High |
| Water Usage (0–100 intensity) | Low, Medium, High |
| Household Size (people) | Small, Medium, Large |

**Output**

| Variable | Sets |
|---|---|
| Refill Urgency (0–100) | Very Low, Low, Medium, High, Very High |

**Membership function shapes.** Tank Level and Refill Urgency use
trapezoidal "shoulder" functions at the extremes (0% and 100%) so the
absolute ends of the scale have full, unambiguous membership, with
triangular functions for the three middle sets, deliberately overlapping
so a value like 32% has genuine partial membership in two neighboring
sets. Water Usage and Household Size follow the same trapezoidal-edges,
triangular-middle pattern with three sets each.

**Rule base.** 22 rules total — 15 covering every Tank Level × Water
Usage combination, plus 7 additional 3-antecedent rules that bring
Household Size into play for cases where a larger or smaller household
meaningfully shifts urgency (see `docs/fuzzy_rules.md` for the full
table and rationale).

**Inference pipeline (implemented in `fuzzy/inference.py`)**
1. Fuzzification — `skfuzzy.interp_membership` for every input against
   every relevant fuzzy set.
2. Rule evaluation — fuzzy AND (minimum) across a rule's antecedents
   gives its firing strength.
3. Implication — Mamdani min-implication clips each fired rule's output
   set at its firing strength.
4. Aggregation — `np.fmax` combines all clipped outputs into a single
   aggregated surface.
5. Defuzzification — `skfuzzy.defuzz(..., 'centroid')` computes the
   final crisp score.

### 3.3 LangChain Explanation Component
After the fuzzy engine returns `urgency_score` and `urgency_category`,
`ai/explainer.py` sends these — along with the original household data —
to a second LangChain chain whose system prompt explicitly instructs the
LLM that these values are authoritative and must not be changed,
recalculated, or contradicted. The LLM's sole task is to explain, in 2–4
plain sentences, why that score makes sense given the inputs. If the API
call fails or no key is configured, a pre-written fallback template
(indexed by category) is shown instead, so the application always
produces a coherent recommendation.

---

## Page 4

### 4.1 System Workflow

```
Natural Language Input  ──┐
                           ├──> LangChain Extraction ──> Validated Structured Data ──┐
Manual Input  ─────────────┘                                                         │
                                                                                       v
                                                                          Fuzzy Inference Engine
                                                                     (Fuzzification → Rules →
                                                                      Implication → Aggregation →
                                                                      Centroid Defuzzification)
                                                                                       │
                                                                                       v
                                                                    Refill Urgency Score + Category
                                                                                       │
                                                                                       v
                                                                      LangChain Explanation (LLM)
                                                                                       │
                                                                                       v
                                                                              Streamlit UI
```

### 4.2 Test Cases

All results below were generated by actually running the implemented
fuzzy engine (`fuzzy/inference.py`), not fabricated. "Usage" is the
qualitative label mapped internally to a 0–100 intensity score
(low=15, medium=50, high=85) before fuzzification.

| # | Tank Level | Usage | Household | Score | Category | Notes |
|---|---|---|---|---|---|---|
| TC1 | 10% | High | 5 | 90.45 | Very High | Classic urgent-refill case |
| TC2 | 90% | Low | 3 | 9.46 | Very Low | Comfortably full tank |
| TC3 | 50% | Medium | 4 | 50.0 | Medium | Balanced mid-range input |
| TC4 | 15% | High | 8 | 89.54 | Very High | Large household amplifies urgency |
| TC5 | 75% | Low | 3 | 9.02 | Very Low | High tank + low usage → very safe |
| TC6 | 35% | High | 6 | 79.72 | High | Large household pushes urgency up |
| TC7 | 60% | Medium | 2 | 50.0 | Medium | Small household moderates urgency |
| TC8 | 5% | Medium | 4 | 90.45 | Very High | Near-empty tank dominates the result |
| TC9 | 100% | High | 7 | 0.0 | Very Low | Full tank overrides high usage entirely |
| TC10 | 45% | Low | 1 | 30.0 | Low | Single person, low usage, moderate level |

**Natural-language example inputs** (processed through the same
pipeline via `ai/extractor.py` before reaching the fuzzy engine):

1. "Five people live in my house. Our tank holds 1000 litres and is
   currently 20% full. We use a lot of water every day." →
   extracts to (capacity=1000, level=20, household=5, usage=high).
2. "My family has 3 members, the tank is 75% full, and our water usage
   is low." → (capacity=missing, level=75, household=3, usage=low);
   UI prompts for capacity.
3. "There are 8 people at home, we have a 2000 litre tank and it is
   around 35 percent full. Usage is high." → (capacity=2000, level=35,
   household=8, usage=high).
4. "It's just me living alone, 500 litre tank, about 60% full, I don't
   use much water." → (capacity=500, level=60, household=1, usage=low).
5. "We're a family of 6, tank capacity 1500 litres, roughly half full,
   moderate usage — normal cooking, cleaning and bathing." →
   (capacity=1500, level=50, household=6, usage=medium).

### 4.3 Installation & Running Locally
```bash
git clone https://github.com/<your-username>/smart-water-tank-refill-advisor.git
cd smart-water-tank-refill-advisor
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then add your OPENAI_API_KEY
streamlit run app.py
```

### 4.4 Deployment (Streamlit Community Cloud)
1. Push the repository to GitHub.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click "New app", select the repository, branch `main`, and file
   `app.py`.
4. Under "Advanced settings" → "Secrets", add:
   ```
   OPENAI_API_KEY = "sk-..."
   ```
5. Click Deploy. The app builds from `requirements.txt` automatically.
6. Test the live URL provided by Streamlit Cloud.

---

## Page 5

### 5.1 Future Scope
- Integration with real IoT ultrasonic tank-level sensors for automatic
  (rather than self-reported) tank level input.
- Time-series usage forecasting to predict the exact day/time a refill
  will become necessary.
- Multi-tank and multi-user support with persistent storage (currently
  stateless per session).
- Support for additional LLM providers via LangChain's provider-agnostic
  interface (e.g. Anthropic, local models) as alternatives to OpenAI.
- SMS/push notification integration for automatic urgent-refill alerts.

### 5.2 Limitations
- Water usage is currently captured as a 3-level qualitative label
  rather than a precise litres/day measurement.
- The system is stateless — no historical tracking of tank level trends
  over time.
- Natural-language extraction quality depends on the underlying LLM's
  ability to correctly interpret the household description; ambiguous
  text may still require the manual fallback fields.
- Requires an active internet connection and a valid OpenAI API key for
  the AI input mode (manual mode works without either).

### 5.3 Viva Explanation Summary
This project demonstrates two distinct, complementary uses of AI: (1)
LangChain + an LLM for natural-language understanding — converting
unstructured household descriptions into validated structured data —
and (2) a genuine 5-stage Mamdani fuzzy inference system for the actual
decision-making, since "urgency" is inherently a matter of degree, not
a crisp yes/no threshold. The LLM is never allowed to override or
second-guess the fuzzy engine's numeric output; it only extracts inputs
beforehand and explains the result afterward. This separation of
concerns — LLM for language, fuzzy logic for reasoning under
uncertainty — is the central technical argument of the project and the
most important point to communicate clearly in the viva.

### 5.4 Author
**Project:** AI-Based Smart Water Tank Refill Advisor Using LangChain
and Fuzzy Logic
**Type:** College Mini Project
**Repository:** `smart-water-tank-refill-advisor` (GitHub)
