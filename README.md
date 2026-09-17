# 💧 AI-Based Smart Water Tank Refill Advisor

**Smart household water refill recommendations using LangChain and Fuzzy Logic**

A college mini project combining genuine Mamdani fuzzy logic inference
with LangChain-powered natural-language understanding to help
households decide how urgently their water tank needs refilling.

---

## 1. Project Overview

Users describe their household water situation in plain English (or
fill in a short manual form), and the app:

1. Extracts structured data (tank capacity, tank level %, household
   size, water usage) using **LangChain + an LLM**.
2. Runs that data through a **genuine 5-stage Mamdani fuzzy inference
   system** (fuzzification → rule evaluation → implication →
   aggregation → centroid defuzzification) to compute a 0–100 **Refill
   Urgency Score** and category.
3. Uses **LangChain a second time** to generate a natural-language
   explanation of the result — without ever altering the fuzzy engine's
   numeric output.

## 2. Problem Statement

Households with tank-based water supply have no simple, data-driven way
to judge refill urgency that accounts for multiple interacting factors
(tank level, household size, consumption pattern) at once. Fixed
percentage thresholds ("refill below 30%") ignore this nuance — a 40%
tank might be fine for one household and urgent for another.

## 3. Objectives

- Build a genuine fuzzy inference system, not a disguised if-else chain.
- Use LangChain meaningfully: for structured extraction *and* for
  result explanation — never for the core numeric decision.
- Support both natural-language and manual input, feeding one shared
  fuzzy engine.
- Ship a simple, deployable, mobile-friendly Streamlit UI.

## 4. Features

- 🗣️ Natural-language input mode with LangChain structured extraction
- 🎛️ Manual input mode (sliders/number inputs) — works without an API key
- 🧮 Real Mamdani fuzzy inference (triangular/trapezoidal membership
  functions, 22-rule base, centroid defuzzification)
- 🔍 "Fuzzy Analysis" panel showing membership degrees and activated
  rules with real firing strengths
- 📊 Matplotlib visualizations of every membership function
- 🤖 LangChain-generated plain-language recommendation
- 🛡️ Full input validation and graceful error handling throughout

## 5. Technologies Used

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web UI | Streamlit |
| AI / LLM orchestration | LangChain (`langchain`, `langchain-openai`, `langchain-core`) |
| LLM Provider | OpenAI (`gpt-4o-mini` via `ChatOpenAI`) |
| Fuzzy Logic | scikit-fuzzy |
| Validation | Pydantic |
| Visualization | Matplotlib |
| Data handling | Pandas, NumPy |
| Hosting | Streamlit Community Cloud |

## 6. AI / LangChain Architecture

```
User's natural-language description
            │
            ▼
   ChatPromptTemplate (system + human prompt)
            │
            ▼
   ChatOpenAI.with_structured_output(ExtractedWaterInfo)
            │
            ▼
   Pydantic-validated structured data ──► utils/validation.py range checks
            │
            ▼
   Missing fields? ──yes──► UI prompts user for exactly those fields
            │no
            ▼
      Fuzzy Inference Engine
            │
            ▼
   urgency_score, urgency_category (authoritative)
            │
            ▼
   ChatPromptTemplate (explanation prompt, includes fixed score/category)
            │
            ▼
   ChatOpenAI ──► StrOutputParser ──► natural-language recommendation
```

The LLM is *never* allowed to change the numeric score — see
`ai/prompts.py` (`EXPLANATION_SYSTEM_PROMPT`) for the explicit
instruction, and `docs/viva_questions.md` (Q7) for the reasoning.

## 7. Fuzzy Logic Architecture

A genuine Mamdani-style fuzzy inference system implemented from first
principles on top of `scikit-fuzzy`'s membership/defuzzification
primitives (`fuzzy/membership.py`, `fuzzy/rules.py`, `fuzzy/inference.py`):

1. **Fuzzification** — crisp inputs → membership degrees via
   `skfuzzy.interp_membership`.
2. **Rule Evaluation** — fuzzy AND (min) of antecedent degrees = firing
   strength.
3. **Implication** — Mamdani min-implication clips each rule's output
   set.
4. **Aggregation** — max-combination of all clipped output sets.
5. **Defuzzification** — centroid (center of area) method → final 0–100
   score.

## 8. Fuzzy Membership Functions

| Variable | Sets | Shape |
|---|---|---|
| Tank Level (0–100%) | Very Low, Low, Medium, High, Very High | Trapezoidal shoulders + triangular middle |
| Water Usage (0–100 intensity) | Low, Medium, High | Trapezoidal shoulders + triangular middle |
| Household Size (0–12 people) | Small, Medium, Large | Trapezoidal shoulders + triangular middle |
| Refill Urgency (0–100, output) | Very Low, Low, Medium, High, Very High | Trapezoidal shoulders + triangular middle |

Full ranges and rationale are documented in `fuzzy/membership.py`
docstrings.

## 9. Fuzzy Rules

22 rules total (15 two-antecedent + 7 three-antecedent rules bringing in
household size). Full table with rationale: **`docs/fuzzy_rules.md`**.

## 10. System Workflow

```
Natural Language ──┐
                    ├─► LangChain Extraction ─► Fuzzy Inference ─► Defuzzification ─► Refill Urgency ─► LangChain Explanation ─► UI
Manual Input ───────┘
```

## 11. Installation

```bash
git clone https://github.com/<your-username>/smart-water-tank-refill-advisor.git
cd smart-water-tank-refill-advisor
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 12. API Key Setup

**Never commit a real API key.** Two supported methods:

**Local development (`.env`):**
```bash
cp .env.example .env
# then edit .env and set:
# OPENAI_API_KEY=sk-your-real-key-here
```

**Streamlit secrets (local testing):**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with your real key
```
`.env` and `.streamlit/secrets.toml` are both git-ignored.

## 13. Running Locally

```bash
streamlit run app.py
```
Then open the local URL Streamlit prints (typically `http://localhost:8501`).

> Manual input mode works fully even without an API key configured.

## 14. Deployment (Streamlit Community Cloud)

1. Push this repository to your own GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
   with GitHub.
3. Click **New app** → select your repo, branch `main`, file `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```
   OPENAI_API_KEY = "sk-your-real-key-here"
   ```
5. Click **Deploy**. Streamlit Cloud installs `requirements.txt`
   automatically.
6. Open and test the live URL provided after deployment.

## 15. Screenshots

_Add screenshots of your running app here after your first local or
deployed run (see `assets/README.md`)._

```
assets/screenshot-main.png
assets/screenshot-fuzzy-analysis.png
assets/screenshot-charts.png
```

## 16. Example Input / Output

**Input (natural language):**
> "There are 5 people in my house. The tank capacity is 1000 litres and
> currently it is around 30% full. We use a lot of water because of
> daily bathing, washing clothes and cleaning."

**Extracted:** capacity=1000L, level=30%, household=5, usage=high

**Fuzzy Result:** Refill Urgency Score ≈ 85 / 100 — Category: **Very High**

**Recommendation (LangChain-generated):**
> Your tank level is relatively low while your household's water usage
> is high, so demand is likely to outpace the remaining supply soon.
> Refilling the tank in the near future is recommended to avoid running
> out of water.

More worked examples with real engine output: `docs/project_report.md`
(Section 4.2, Test Cases).

## 17. Future Scope

- Real IoT ultrasonic tank-level sensor integration.
- Usage-trend forecasting to predict *when* a refill will be needed.
- Multi-tank / multi-household persistent tracking.
- Additional LLM provider support via LangChain's provider-agnostic
  interface.

## 18. Limitations

- Water usage is a 3-level qualitative input, not a precise litres/day
  measurement.
- Stateless — no historical trend tracking across sessions.
- AI input mode requires an internet connection and a valid API key
  (manual mode does not).

## 19. Viva Explanation

See **`docs/viva_questions.md`** for a full set of anticipated viva
questions and answers, and **`docs/project_report.md`** for the
complete written report. The core point to communicate: **LangChain
handles language (extraction and explanation); a genuine Mamdani fuzzy
inference system handles the actual reasoning under uncertainty. The
LLM never overrides the fuzzy engine's numeric result.**

## 20. Project Structure

```
smart-water-tank-refill-advisor/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── fuzzy/
│   ├── membership.py
│   ├── rules.py
│   └── inference.py
├── ai/
│   ├── extractor.py
│   ├── prompts.py
│   └── explainer.py
├── utils/
│   ├── validation.py
│   └── helpers.py
├── ui/
│   ├── components.py
│   └── charts.py
├── docs/
│   ├── project_report.md
│   ├── fuzzy_rules.md
│   └── viva_questions.md
└── assets/
```

## 21. Author

College Mini Project — AI-Based Smart Water Tank Refill Advisor Using
LangChain and Fuzzy Logic.
