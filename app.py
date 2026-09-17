"""
app.py
------
AI-Based Smart Water Tank Refill Advisor
Main Streamlit application entry point.

Architecture (see docs/project_report.md and README.md for full detail):

    Natural Language Input
            |
            v
      LangChain Extraction (ai/extractor.py)   -----.
            |                                        |
            v                                        |
    Structured & Validated Data                       |
            |                                         |  (Manual input mode
            v                                         |   feeds the same
      Fuzzy Inference Engine (fuzzy/inference.py) <---'   point)
            |
            v
    Refill Urgency Score + Category (authoritative, numeric)
            |
            v
      LangChain Explanation (ai/explainer.py)
            |
            v
          Streamlit UI
"""

import streamlit as st

from ai.extractor import extract_water_info, missing_fields_message
from ai.explainer import generate_explanation
from fuzzy.inference import run_fuzzy_inference
from utils.validation import validate_all_inputs
from utils.helpers import get_api_key, usage_label_to_score
from ui.components import (
    render_extracted_values,
    render_results_summary,
    render_recommendation,
    render_fuzzy_analysis,
    render_missing_fields_form,
)
from ui.charts import (
    tank_level_chart,
    water_usage_chart,
    household_size_chart,
    urgency_output_chart,
    aggregated_output_chart,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Based Smart Water Tank Refill Advisor",
    page_icon="💧",
    layout="wide",
)

API_KEY = get_api_key()
MODEL_NAME = "gpt-4o-mini"

if "final_inputs" not in st.session_state:
    st.session_state.final_inputs = None  # dict: capacity, level, household, usage
if "pending_extraction" not in st.session_state:
    st.session_state.pending_extraction = None  # holds AI result awaiting missing fields


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("💧 Project Info")
    st.markdown(
        "**AI-Based Smart Water Tank Refill Advisor**\n\n"
        "A college mini project combining LangChain-based natural language "
        "understanding with a genuine Mamdani fuzzy inference system to "
        "recommend household water tank refill urgency."
    )

    st.markdown("---")
    st.markdown("**System Status**")
    if API_KEY:
        st.success("🤖 AI / LangChain: Connected")
    else:
        st.error("🤖 AI / LangChain: No API key configured")
        st.caption("Manual input mode still works fully without an API key.")
    st.success("🧮 Fuzzy Logic Engine: Active (Mamdani, centroid defuzzification)")

    st.markdown("---")
    with st.expander("About this project"):
        st.markdown(
            "- **Fuzzy inputs:** Tank Level, Water Usage, Household Size\n"
            "- **Fuzzy output:** Refill Urgency (0-100)\n"
            "- **Method:** Mamdani inference, min-implication, max-aggregation, "
            "centroid defuzzification\n"
            "- **AI:** LangChain + OpenAI for extraction and explanation\n"
            "- **Rule base:** 22 hand-crafted fuzzy rules"
        )

    with st.expander("How It Works"):
        st.markdown(
            "```\n"
            "Natural Language\n"
            "      |\n"
            "  LangChain\n"
            "      |\n"
            "Information Extraction\n"
            "      |\n"
            " Fuzzy Inference\n"
            "      |\n"
            " Defuzzification\n"
            "      |\n"
            " Refill Urgency\n"
            "      |\n"
            "LangChain Explanation\n"
            "```"
        )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("💧 AI-Based Smart Water Tank Refill Advisor")
st.caption("Smart household water refill recommendations using LangChain and Fuzzy Logic")

tab_ai, tab_manual = st.tabs(["🗣️ Natural Language Input (AI)", "🎛️ Manual Input"])

# ---------------------------------------------------------------------------
# MODE A: Natural language / AI input
# ---------------------------------------------------------------------------
with tab_ai:
    st.subheader("Describe your household water situation")
    user_text = st.text_area(
        "Describe your household water situation...",
        placeholder=(
            "There are 5 people in my house. We have a 1000 litre tank which is "
            "currently 30% full. Our water usage is high because of daily bathing, "
            "washing clothes and cleaning."
        ),
        height=120,
    )

    if st.button("🤖 Analyze with AI", type="primary"):
        if not user_text.strip():
            st.error("Please enter a description of your household water situation.")
        else:
            with st.spinner("LangChain is extracting structured information..."):
                result = extract_water_info(user_text, api_key=API_KEY, model_name=MODEL_NAME)

            if not result.data and result.error_message:
                st.error(result.error_message)
                st.session_state.pending_extraction = None
            else:
                st.session_state.pending_extraction = result
                st.session_state.final_inputs = None  # reset downstream result

    pending = st.session_state.pending_extraction
    if pending is not None and pending.data is not None:
        render_extracted_values(pending.data)

        if pending.missing_fields:
            st.info(missing_fields_message(pending.missing_fields))
            filled = render_missing_fields_form(
                pending.missing_fields,
                defaults={
                    "tank_capacity_liters": pending.data.tank_capacity_liters,
                    "tank_level_percent": pending.data.tank_level_percent,
                    "household_size": pending.data.household_size,
                },
            )
            if st.button("✅ Confirm and Calculate Refill Urgency", key="confirm_ai"):
                capacity = filled.get("tank_capacity_liters", pending.data.tank_capacity_liters)
                level = filled.get("tank_level_percent", pending.data.tank_level_percent)
                household = filled.get("household_size", pending.data.household_size)
                usage = pending.data.water_usage

                valid, errors = validate_all_inputs(capacity, level, household, usage)
                if not valid:
                    for e in errors:
                        st.error(e)
                else:
                    st.session_state.final_inputs = {
                        "tank_capacity_liters": capacity,
                        "tank_level_percent": level,
                        "household_size": household,
                        "water_usage": usage,
                    }
        else:
            valid, errors = validate_all_inputs(
                pending.data.tank_capacity_liters,
                pending.data.tank_level_percent,
                pending.data.household_size,
                pending.data.water_usage,
            )
            if not valid:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.final_inputs = {
                    "tank_capacity_liters": pending.data.tank_capacity_liters,
                    "tank_level_percent": pending.data.tank_level_percent,
                    "household_size": pending.data.household_size,
                    "water_usage": pending.data.water_usage,
                }
                st.success("All information extracted successfully. See results below.")

# ---------------------------------------------------------------------------
# MODE B: Manual input
# ---------------------------------------------------------------------------
with tab_manual:
    st.subheader("Enter details manually")
    c1, c2 = st.columns(2)
    with c1:
        m_capacity = st.number_input("Tank Capacity (litres)", min_value=1.0, value=1000.0, step=50.0)
        m_level = st.slider("Current Tank Level (%)", min_value=0, max_value=100, value=50)
    with c2:
        m_household = st.number_input("Number of People", min_value=1, value=4, step=1)
        m_usage = st.selectbox("Water Usage Level", options=["low", "medium", "high"], index=1)

    if st.button("🧮 Calculate Refill Urgency", type="primary", key="manual_calc"):
        valid, errors = validate_all_inputs(m_capacity, m_level, m_household, m_usage)
        if not valid:
            for e in errors:
                st.error(e)
        else:
            st.session_state.final_inputs = {
                "tank_capacity_liters": m_capacity,
                "tank_level_percent": m_level,
                "household_size": m_household,
                "water_usage": m_usage,
            }

# ---------------------------------------------------------------------------
# SHARED RESULTS SECTION (fed by either mode)
# ---------------------------------------------------------------------------
inputs = st.session_state.final_inputs

if inputs:
    st.markdown("---")

    try:
        usage_score = usage_label_to_score(inputs["water_usage"])
        fuzzy_result = run_fuzzy_inference(
            tank_level_percent=inputs["tank_level_percent"],
            water_usage_score=usage_score,
            household_size=inputs["household_size"],
        )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Fuzzy inference failed: {exc}")
        fuzzy_result = None

    if fuzzy_result:
        render_results_summary(
            tank_capacity_liters=inputs["tank_capacity_liters"],
            tank_level_percent=inputs["tank_level_percent"],
            household_size=inputs["household_size"],
            water_usage=inputs["water_usage"],
            fuzzy_result=fuzzy_result,
        )

        with st.spinner("LangChain is generating your explanation..."):
            explanation = generate_explanation(
                tank_capacity_liters=inputs["tank_capacity_liters"],
                tank_level_percent=inputs["tank_level_percent"],
                household_size=inputs["household_size"],
                water_usage=inputs["water_usage"],
                urgency_score=fuzzy_result.urgency_score,
                urgency_category=fuzzy_result.urgency_category,
                api_key=API_KEY,
                model_name=MODEL_NAME,
            )
        render_recommendation(
            explanation.text, fuzzy_result.urgency_category, warning_note=explanation.error_message
        )

        render_fuzzy_analysis(fuzzy_result)

        st.subheader("Membership Function Visualizations")
        st.caption("These charts show the overlapping fuzzy sets used by the inference engine — the black dashed line marks your current input value.")
        v1, v2 = st.columns(2)
        with v1:
            st.pyplot(tank_level_chart(inputs["tank_level_percent"]), width='stretch')
            st.pyplot(household_size_chart(inputs["household_size"]), width='stretch')
        with v2:
            st.pyplot(water_usage_chart(usage_score), width='stretch')
            st.pyplot(urgency_output_chart(fuzzy_result.urgency_score), width='stretch')

        st.pyplot(
            aggregated_output_chart(
                fuzzy_result.urgency_universe, fuzzy_result.aggregated_output, fuzzy_result.urgency_score
            ),
            width='stretch',
        )
else:
    st.info("👆 Use the Natural Language or Manual input tab above, then view your results here.")

st.markdown("---")
st.caption(
    "AI-Based Smart Water Tank Refill Advisor · Built with Streamlit, LangChain, and scikit-fuzzy · College Mini Project"
)
