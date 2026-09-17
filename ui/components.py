"""
components.py
--------------
Reusable Streamlit UI rendering functions. Keeping these out of app.py
keeps the main application file readable and focused on flow control.
"""

import pandas as pd
import streamlit as st

from fuzzy.inference import FuzzyResult
from utils.helpers import format_liters, estimated_liters_remaining


CATEGORY_COLORS = {
    "Very Low": "#2E7D32",
    "Low": "#66BB6A",
    "Medium": "#FBC02D",
    "High": "#FB8C00",
    "Very High": "#E53935",
}

CATEGORY_ICON = {
    "Very Low": "🟢",
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🟠",
    "Very High": "🔴",
}


def render_extracted_values(data, editable_key_prefix="extracted"):
    """Displays the AI-extracted structured values in a compact info box."""
    st.markdown("**Extracted Information**")
    cols = st.columns(4)
    cols[0].metric("Tank Capacity", format_liters(data.tank_capacity_liters) if data.tank_capacity_liters else "Missing")
    cols[1].metric("Tank Level", f"{data.tank_level_percent:.0f}%" if data.tank_level_percent is not None else "Missing")
    cols[2].metric("Household Size", f"{data.household_size} people" if data.household_size else "Missing")
    cols[3].metric("Water Usage", (data.water_usage or "medium").capitalize())
    if data.notes:
        st.caption(f"Note: {data.notes}")


def render_results_summary(
    tank_capacity_liters: float,
    tank_level_percent: float,
    household_size: int,
    water_usage: str,
    fuzzy_result: FuzzyResult,
):
    """Renders the main results section with metric cards."""
    st.subheader("Results")

    row1 = st.columns(4)
    row1[0].metric("Tank Level", f"{tank_level_percent:.0f}%")
    row1[1].metric("Household Size", f"{household_size} people")
    row1[2].metric("Water Usage", water_usage.capitalize())
    row1[3].metric(
        "Remaining Water",
        format_liters(estimated_liters_remaining(tank_capacity_liters, tank_level_percent)),
    )

    st.markdown("---")

    row2 = st.columns(2)
    row2[0].metric("Refill Urgency Score", f"{fuzzy_result.urgency_score} / 100")

    category = fuzzy_result.urgency_category
    icon = CATEGORY_ICON.get(category, "⚪")
    color = CATEGORY_COLORS.get(category, "#607D8B")
    row2[1].markdown(
        f"""
        <div style="padding: 0.75rem 1rem; border-radius: 8px; background-color: {color}22;
                    border: 1px solid {color}; text-align:center;">
            <div style="font-size: 0.8rem; color: #555;">Urgency Category</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {color};">
                {icon} {category}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(min(int(fuzzy_result.urgency_score), 100) / 100)


def render_recommendation(explanation_text: str, category: str, warning_note: str = None):
    """Displays the LangChain-generated (or fallback) recommendation text."""
    st.subheader("Recommendation")
    if category in ("High", "Very High"):
        st.warning(explanation_text)
    elif category == "Medium":
        st.info(explanation_text)
    else:
        st.success(explanation_text)
    if warning_note:
        st.caption(f"ℹ️ {warning_note}")


def render_fuzzy_analysis(fuzzy_result: FuzzyResult):
    """Displays fuzzification degrees, activated rules, and defuzzification score."""
    st.subheader("Fuzzy Analysis")

    with st.expander("🔍 Membership Degrees (Fuzzification)", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Tank Level**")
            df = pd.DataFrame(
                {"Set": list(fuzzy_result.tank_level_memberships.keys()),
                 "Degree": list(fuzzy_result.tank_level_memberships.values())}
            )
            st.dataframe(df, hide_index=True, width='stretch')
        with c2:
            st.markdown("**Water Usage**")
            df = pd.DataFrame(
                {"Set": list(fuzzy_result.water_usage_memberships.keys()),
                 "Degree": list(fuzzy_result.water_usage_memberships.values())}
            )
            st.dataframe(df, hide_index=True, width='stretch')
        with c3:
            st.markdown("**Household Size**")
            df = pd.DataFrame(
                {"Set": list(fuzzy_result.household_size_memberships.keys()),
                 "Degree": list(fuzzy_result.household_size_memberships.values())}
            )
            st.dataframe(df, hide_index=True, width='stretch')

    with st.expander(f"⚙️ Activated Rules ({len(fuzzy_result.activated_rules)} fired)", expanded=False):
        if not fuzzy_result.activated_rules:
            st.info("No rules were activated for these inputs.")
        else:
            rule_rows = [
                {
                    "Rule #": r.rule_id,
                    "Firing Strength": r.firing_strength,
                    "Output Set": r.output_set.replace("_", " ").title(),
                    "Rule": r.description,
                }
                for r in fuzzy_result.activated_rules
            ]
            st.dataframe(pd.DataFrame(rule_rows), hide_index=True, width='stretch')

    with st.expander("📐 Defuzzification (Centroid Method)", expanded=False):
        st.write(
            f"The aggregated output fuzzy set was defuzzified using the **centroid "
            f"(center of area)** method, producing a crisp Refill Urgency Score of "
            f"**{fuzzy_result.urgency_score} / 100**, categorized as **{fuzzy_result.urgency_category}**."
        )


def render_missing_fields_form(missing_fields, defaults=None):
    """
    Renders input widgets for any fields the AI extraction could not find,
    returning a dict of user-filled values for those fields.
    """
    defaults = defaults or {}
    st.warning("Some information couldn't be found in your description. Please fill it in below:")
    filled = {}
    if "tank_capacity_liters" in missing_fields:
        filled["tank_capacity_liters"] = st.number_input(
            "Tank Capacity (litres)", min_value=1.0, value=float(defaults.get("tank_capacity_liters", 1000.0)), step=50.0
        )
    if "tank_level_percent" in missing_fields:
        filled["tank_level_percent"] = st.slider(
            "Current Tank Level (%)", min_value=0, max_value=100, value=int(defaults.get("tank_level_percent", 50))
        )
    if "household_size" in missing_fields:
        filled["household_size"] = st.number_input(
            "Household Size (people)", min_value=1, value=int(defaults.get("household_size", 4)), step=1
        )
    return filled
