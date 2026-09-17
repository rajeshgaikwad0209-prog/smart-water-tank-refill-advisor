"""
charts.py
---------
Matplotlib visualizations of the fuzzy membership functions and the
aggregated output surface. These charts are important for the viva —
they visually prove that genuine overlapping fuzzy sets (not crisp
thresholds) are being used.
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from fuzzy.membership import (
    TANK_LEVEL_UNIVERSE,
    WATER_USAGE_UNIVERSE,
    HOUSEHOLD_SIZE_UNIVERSE,
    URGENCY_UNIVERSE,
    tank_level_mfs,
    water_usage_mfs,
    household_size_mfs,
    urgency_mfs,
)

PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def _plot_mfs(universe, mfs_dict, title, xlabel, current_value=None):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for i, (name, mf) in enumerate(mfs_dict.items()):
        ax.plot(universe, mf, label=name.replace("_", " ").title(), color=PALETTE[i % len(PALETTE)], linewidth=2)
        ax.fill_between(universe, mf, alpha=0.08, color=PALETTE[i % len(PALETTE)])
    if current_value is not None:
        ax.axvline(current_value, color="black", linestyle="--", linewidth=1.2, label=f"Input = {current_value}")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Membership Degree")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig


def tank_level_chart(current_value=None):
    return _plot_mfs(TANK_LEVEL_UNIVERSE, tank_level_mfs(), "Tank Level Membership Functions", "Tank Level (%)", current_value)


def water_usage_chart(current_value=None):
    return _plot_mfs(WATER_USAGE_UNIVERSE, water_usage_mfs(), "Water Usage Membership Functions", "Water Usage Intensity (0-100)", current_value)


def household_size_chart(current_value=None):
    return _plot_mfs(HOUSEHOLD_SIZE_UNIVERSE, household_size_mfs(), "Household Size Membership Functions", "Household Size (people)", current_value)


def urgency_output_chart(current_value=None):
    return _plot_mfs(URGENCY_UNIVERSE, urgency_mfs(), "Refill Urgency Membership Functions (Output)", "Refill Urgency Score (0-100)", current_value)


def aggregated_output_chart(urgency_universe, aggregated_output, defuzzified_score):
    """Shows the aggregated (clipped + combined) output fuzzy set with the
    defuzzified centroid score marked, for the Fuzzy Analysis section."""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.fill_between(urgency_universe, aggregated_output, color="#d62728", alpha=0.4, label="Aggregated Output")
    ax.plot(urgency_universe, aggregated_output, color="#d62728", linewidth=1.5)
    ax.axvline(defuzzified_score, color="black", linestyle="--", linewidth=1.5,
               label=f"Centroid = {defuzzified_score:.1f}")
    ax.set_title("Aggregated Fuzzy Output & Defuzzification", fontsize=12, fontweight="bold")
    ax.set_xlabel("Refill Urgency Score (0-100)")
    ax.set_ylabel("Membership Degree")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig
